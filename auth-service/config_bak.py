import os
from datetime import timedelta

class Config:
    # Основные настройки
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-very-secret-key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/auth_service')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Настройки SMS.RU
    SMSRU_API_ID = os.getenv('SMSRU_API_ID')
    SMSRU_FROM = os.getenv('SMSRU_FROM', 'HotSpotAuth')
    
    # Настройки сессии
    PERMANENT_SESSION_LIFETIME = timedelta(days=365)
    SESSION_COOKIE_SECURE = True
    
    # Настройки администратора
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'securepassword')
    
    # Настройки MikroTik
    MIKROTIK_SECRET = os.getenv('MIKROTIK_SECRET', 'shared-secret-for-hotspot')
    SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', '86400'))  # 24 часа
    
    # Настройки VPS
    EXTERNAL_URL = os.getenv('EXTERNAL_URL', 'https://your-vps-domain.com')