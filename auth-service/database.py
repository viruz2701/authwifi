import sqlite3
from contextlib import contextmanager
from config import settings
import logging
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def hash_mac(mac: str) -> str:
    """Хеширование MAC-адреса для безопасности."""
    return hashlib.sha256(mac.encode()).hexdigest()

def init_db():
    with sqlite3.connect(settings.DATABASE_URL.split("///")[-1]) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                mac_hashed TEXT UNIQUE NOT NULL,
                phone TEXT,
                is_active BOOLEAN DEFAULT TRUE
            );
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                ip TEXT NOT NULL,
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP,
                bytes_in INTEGER DEFAULT 0,
                bytes_out INTEGER DEFAULT 0
            );
            CREATE INDEX IF NOT EXISTS idx_mac ON users(mac_hashed);
            CREATE INDEX IF NOT EXISTS idx_ip ON sessions(ip);
        """)
        logger.info("Database initialized")

@contextmanager
def get_db():
    conn = sqlite3.connect(settings.DATABASE_URL.split("///")[-1])
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()
