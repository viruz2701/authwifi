import requests
from flask import current_app
from datetime import datetime, timedelta

class SMSService:
    @staticmethod
    def send_sms(phone, message):
        url = "https://sms.ru/sms/send"
        params = {
            'api_id': current_app.config['SMSRU_API_ID'],
            'to': phone,
            'msg': message,
            'json': 1,
            'from': current_app.config['SMSRU_FROM']
        }
        try:
            response = requests.get(url, params=params)
            data = response.json()
            return data.get('status') == "OK"
        except Exception as e:
            current_app.logger.error(f"SMS sending error: {str(e)}")
            return False

    @staticmethod
    def send_call_password(phone, code):
        url = "https://sms.ru/code/call"
        params = {
            'api_id': current_app.config['SMSRU_API_ID'],
            'phone': phone,
            'ip': '-1',
            'code': code
        }
        try:
            response = requests.get(url, params=params)
            data = response.json()
            return data.get('status') == "OK"
        except Exception as e:
            current_app.logger.error(f"Call password error: {str(e)}")
            return False