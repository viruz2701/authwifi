from flask import Blueprint, request, jsonify, session, redirect, url_for
from app.models import User, AuthCode, UserSession, UserDevice
from app import db
from datetime import datetime, timedelta
from .sms_service import SMSService
from .mikrotik import MikroTikService
import secrets
from functools import wraps

auth_bp = Blueprint('auth', __name__)

def generate_code(length=6):
    return ''.join([str(secrets.randbelow(10)) for _ in range(length)])

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/auth/mikrotik', methods=['GET'])
def mikrotik_auth_redirect():
    mac_address = request.args.get('mac')
    hotspot_ip = request.args.get('hotspot')
    session_timeout = request.args.get('session_timeout', 86400)
    
    if not mac_address or not hotspot_ip:
        return "Invalid request parameters", 400
    
    # Сохраняем данные в сессии для формы авторизации
    session['hotspot_mac'] = mac_address
    session['hotspot_ip'] = hotspot_ip
    session['session_timeout'] = session_timeout
    
    return redirect(url_for('auth.show_auth_form'))

@auth_bp.route('/auth/form', methods=['GET'])
def show_auth_form():
    return """
    <html>
    <body>
        <h2>Авторизация в HotSpot</h2>
        <form action="/auth/init" method="post">
            <input type="text" name="phone" placeholder="Номер телефона" required>
            <select name="method">
                <option value="sms">SMS</option>
                <option value="call">Call Password</option>
            </select>
            <input type="hidden" name="mac" value="{mac}">
            <input type="hidden" name="hotspot_ip" value="{hotspot_ip}">
            <button type="submit">Получить код</button>
        </form>
    </body>
    </html>
    """.format(
        mac=session.get('hotspot_mac', ''),
        hotspot_ip=session.get('hotspot_ip', '')
    )

@auth_bp.route('/auth/init', methods=['POST'])
def auth_init():
    phone = request.form.get('phone')
    method = request.form.get('method', 'sms')
    mac_address = request.form.get('mac') or session.get('hotspot_mac')
    hotspot_ip = request.form.get('hotspot_ip') or session.get('hotspot_ip')
    
    if not all([phone, mac_address, hotspot_ip]):
        return "Missing required parameters", 400
    
    # Находим или создаем пользователя
    user = User.query.filter_by(phone=phone).first()
    if not user:
        user = User(phone=phone)
        db.session.add(user)
        db.session.commit()
    
    # Генерируем код
    code = generate_code()
    expires_at = datetime.utcnow() + timedelta(minutes=5)
    
    # Сохраняем код в базу
    auth_code = AuthCode(
        user_id=user.id,
        code=code,
        method=method,
        expires_at=expires_at
    )
    db.session.add(auth_code)
    
    # Обновляем информацию об устройстве
    device = UserDevice.query.filter_by(
        user_id=user.id,
        mac_address=mac_address
    ).first()
    
    if not device:
        device = UserDevice(
            user_id=user.id,
            mac_address=mac_address,
            device_name=f"Device {mac_address[-6:]}"
        )
        db.session.add(device)
    else:
        device.last_seen = datetime.utcnow()
    
    db.session.commit()
    
    # Отправляем код
    if method == 'sms':
        message = f"Ваш код авторизации: {code}"
        sent = SMSService.send_sms(phone, message)
    elif method == 'call':
        sent = SMSService.send_call_password(phone, code)
    else:
        return "Invalid method", 400
    
    if not sent:
        return "Failed to send code", 500
    
    # Сохраняем данные для верификации
    session['temp_user_id'] = user.id
    session['temp_user_phone'] = phone
    session['temp_mac_address'] = mac_address
    session['temp_hotspot_ip'] = hotspot_ip
    
    return """
    <html>
    <body>
        <h2>Введите код подтверждения</h2>
        <form action="/auth/verify" method="post">
            <input type="text" name="code" placeholder="Код из SMS/звонка" required>
            <button type="submit">Подтвердить</button>
        </form>
    </body>
    </html>
    """

@auth_bp.route('/auth/verify', methods=['POST'])
def auth_verify():
    code = request.form.get('code')
    
    if 'temp_user_id' not in session:
        return "Session expired", 400
    
    user_id = session['temp_user_id']
    phone = session['temp_user_phone']
    mac_address = session['temp_mac_address']
    hotspot_ip = session['temp_hotspot_ip']
    
    # Проверяем код
    auth_code = AuthCode.query.filter(
        AuthCode.user_id == user_id,
        AuthCode.code == code,
        AuthCode.used == False,
        AuthCode.expires_at > datetime.utcnow()
    ).order_by(AuthCode.created_at.desc()).first()
    
    if not auth_code:
        return "Invalid or expired code", 400
    
    # Помечаем код как использованный
    auth_code.used = True
    
    # Создаем сессию
    user_session = UserSession(
        user_id=user_id,
        ip_address=request.remote_addr,
        mac_address=mac_address,
        hotspot_id=hotspot_ip,
        session_start=datetime.utcnow()
    )
    db.session.add(user_session)
    db.session.commit()
    
    # Авторизуем на MikroTik
    auth_url = MikroTikService.authorize_mac(
        mac_address=mac_address,
        hotspot_ip=hotspot_ip,
        username=f"user_{user_id}",
        session_timeout=session.get('session_timeout', 86400)
    )
    
    # Очищаем временные данные
    session.pop('temp_user_id', None)
    session.pop('temp_user_phone', None)
    session.pop('temp_mac_address', None)
    session.pop('temp_hotspot_ip', None)
    
    return redirect(auth_url)

@auth_bp.route('/auth/logout', methods=['POST'])
@login_required
def logout():
    session_id = session.get('session_id')
    if session_id:
        user_session = UserSession.query.get(session_id)
        if user_session:
            user_session.session_end = datetime.utcnow()
            user_session.is_active = False
            db.session.commit()
            
            # Отправляем команду logout на MikroTik
            MikroTikService.logout_mac(
                user_session.mac_address,
                user_session.hotspot_id
            )
    
    session.clear()
    return jsonify({'success': True})

@auth_bp.route('/api/sessions', methods=['GET'])
@login_required
def get_user_sessions():
    user_id = session['user_id']
    sessions = UserSession.query.filter_by(user_id=user_id).order_by(
        UserSession.session_start.desc()
    ).all()
    
    return jsonify({
        'sessions': [{
            'id': s.id,
            'session_start': s.session_start.isoformat(),
            'session_end': s.session_end.isoformat() if s.session_end else None,
            'ip_address': s.ip_address,
            'mac_address': s.mac_address,
            'hotspot_id': s.hotspot_id,
            'is_active': s.is_active
        } for s in sessions]
    })