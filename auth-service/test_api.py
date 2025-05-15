import pytest
from fastapi.testclient import TestClient
from api import app, hash_mac
from database import init_db
import sqlite3

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    init_db()
    with sqlite3.connect("authwifi.db") as conn:
        conn.execute(
            "INSERT INTO users (mac_hashed, phone) VALUES (?, ?)",
            (hash_mac("00:1A:2B:3C:4D:5E"), "+79001234567")
        )

def test_auth_valid():
    response = client.post(
        "/auth",
        json={"mac": "00:1A:2B:3C:4D:5E", "ip": "192.168.1.100", "token": "123456"},
        headers={"X-API-Key": "test-secret"}
    )
    assert response.status_code == 200
    assert "user_id" in response.json()

def test_auth_invalid_mac():
    response = client.post(
        "/auth",
        json={"mac": "invalid", "ip": "192.168.1.100", "token": "123456"},
        headers={"X-API-Key": "test-secret"}
    )
    assert response.status_code == 422  # Pydantic validation error
