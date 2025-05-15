from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = (
        db.Index('ix_users_phone', 'phone'),
        db.Index('ix_users_created_at', 'created_at'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    sessions = db.relationship('UserSession', back_populates='user', lazy='dynamic')
    auth_codes = db.relationship('AuthCode', back_populates='user', lazy='dynamic')

class AuthCode(db.Model):
    __tablename__ = 'auth_codes'
    __table_args__ = (
        db.Index('ix_auth_codes_user_id', 'user_id'),
        db.Index('ix_auth_codes_expires_at', 'expires_at'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    code = db.Column(db.String(6), nullable=False)
    method = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    
    user = db.relationship('User', back_populates='auth_codes')

class UserSession(db.Model):
    __tablename__ = 'user_sessions'
    __table_args__ = (
        db.Index('ix_user_sessions_user_id', 'user_id'),
        db.Index('ix_user_sessions_mac_address', 'mac_address'),
        db.Index('ix_user_sessions_is_active', 'is_active'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ip_address = db.Column(db.String(45))
    mac_address = db.Column(db.String(17))
    hotspot_id = db.Column(db.String(50))
    session_start = db.Column(db.DateTime, default=datetime.utcnow)
    session_end = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    user = db.relationship('User', back_populates='sessions')

class AdminUser(db.Model):
    __tablename__ = 'admin_users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)