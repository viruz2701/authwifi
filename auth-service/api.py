from fastapi import FastAPI, Depends, HTTPException, status, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field, validator
from database import get_db, hash_mac
from config import settings
import sqlite3
import logging
import re

app = FastAPI()
logger = logging.getLogger(__name__)
api_key_header = APIKeyHeader(name="X-API-Key")

class AuthRequest(BaseModel):
    mac: str = Field(..., example="00:1A:2B:3C:4D:5E")
    ip: str = Field(..., example="192.168.1.100")
    token: str = Field(..., min_length=6, max_length=6)

    @validator("mac")
    def validate_mac(cls, v):
        if not re.match(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$", v):
            raise ValueError("Invalid MAC format")
        return v

    @validator("ip")
    def validate_ip(cls, v):
        if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", v):
            raise ValueError("Invalid IP format")
        return v

def validate_api_key(api_key: str = Security(api_key_header)):
    if api_key != settings.HOTSPOT_SECRET.get_secret_value():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key"
        )

@app.post("/auth", dependencies=[Security(validate_api_key)])
async def auth_user(
    request: AuthRequest,
    db: sqlite3.Connection = Depends(get_db)
):
    try:
        mac_hashed = hash_mac(request.mac)
        cursor = db.execute(
            "SELECT id FROM users WHERE mac_hashed = ?",
            (mac_hashed,)
        )
        user = cursor.fetchone()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return {"status": "OK", "user_id": user["id"]}
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
