import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(32))
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 3600,
        'pool_size': 10,
        'max_overflow': 20
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(days=365)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    CACHE_TYPE = 'RedisCache' if os.getenv('REDIS_URL') else 'SimpleCache'
    CACHE_REDIS_URL = os.getenv('REDIS_URL')
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL')
    SMSRU_API_ID = os.getenv('SMSRU_API_ID')
    MIKROTIK_SECRET = os.getenv('MIKROTIK_SECRET')
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_DOMAIN = os.getenv('DOMAIN')

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///dev.db')