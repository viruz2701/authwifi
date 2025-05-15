from flask import Blueprint, request, jsonify, session
from app import db, limiter
from app.models import User, AuthCode, UserSession
from datetime import datetime, timedelta
from app.sms_service import SMSService
from app.mikrotik import MikroTikService
from werkzeug.exceptions import BadRequest
import secrets

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/init', methods=['POST'])
@limiter.limit("5 per minute")
def auth_init():
    data = request.get_json()
    if not data or 'phone' not in data:
        raise BadRequest('Phone number is required')
    
    phone = validate_phone(data['phone'])
    method = data.get('method', 'sms')
    mac_address = data.get('mac', '')
    
    user = get_or_create_user(phone)
    code = generate_code()
    expires_at = datetime.utcnow() + timedelta(minutes=5)
    
    auth_code = AuthCode(
        user_id=user.id,
        code=code,
        method=method,
        expires_at=expires_at
    )
    db.session.add(auth_code)
    db.session.commit()
    
    if method == 'sms':
        SMSService.send_sms(phone, f"Your code: {code}")
    elif method == 'call':
        SMSService.send_call(phone, code)
    
    return jsonify(
        status='success',
        method=method,
        expires_in=300
    )

def validate_phone(phone):
    # Реализация валидации телефона
    return phone

def get_or_create_user(phone):
    user = User.query.filter_by(phone=phone).first()
    if not user:
        user = User(phone=phone)
        db.session.add(user)
        db.session.commit()
    return user

def generate_code():
    return ''.join([str(secrets.randbelow(10)) for _ in range(6)])