import requests
from flask import current_app
from urllib.parse import quote

class MikroTikService:
    @staticmethod
    def authorize_mac(mac_address, hotspot_ip, username, session_timeout):
        # Генерация URL для перенаправления MikroTik
        login_url = (
            f"{current_app.config['EXTERNAL_URL']}/auth/mikrotik?"
            f"mac={mac_address}&"
            f"hotspot={hotspot_ip}&"
            f"session_timeout={session_timeout}"
        )
        
        # URL для авторизации на MikroTik
        auth_url = (
            f"http://{hotspot_ip}/login?"
            f"username={quote(username)}&"
            f"password={current_app.config['MIKROTIK_SECRET']}&"
            f"dst={quote(login_url)}"
        )
        
        return auth_url

    @staticmethod
    def logout_mac(mac_address, hotspot_ip):
        try:
            logout_url = f"http://{hotspot_ip}/logout"
            data = {
                'mac': mac_address,
                'ajax': '1'
            }
            response = requests.post(logout_url, data=data)
            return response.status_code == 200
        except Exception as e:
            current_app.logger.error(f"MikroTik logout error: {str(e)}")
            return False