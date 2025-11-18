import requests
import time
import random
import string
from typing import Optional
from config import MARZBAN_BASE_URL, MARZBAN_USER, MARZBAN_PASS, MARZBAN_DATA_LIMIT

def generate_random_string(length=8):
    characters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

class MarzbanAPI:
    def __init__(self, base_url: str, admin_username: str, admin_password: str):
        self.base_url = base_url.rstrip('/')
        self.admin_username = admin_username
        self.admin_password = admin_password
        self.access_token = None
        
    def authenticate(self) -> bool:
        try:
            url = f"{self.base_url}/api/admin/token"
            data = {"username": self.admin_username, "password": self.admin_password}
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            response = requests.post(url, data=data, headers=headers, timeout=10)
            response.raise_for_status()
            token_data = response.json()
            self.access_token = token_data.get("access_token")
            return bool(self.access_token)
        except Exception:
            return False
    
    def create_user(self, username: str, data_limit: int = 0, expire_days: Optional[int] = None) -> dict:
        if not self.access_token and not self.authenticate():
            return {}
        try:
            url = f"{self.base_url}/api/user"
            user_data = {
                "username": username,
                "proxies": {"vless": {"flow": "xtls-rprx-vision"}},
                "inbounds": {"vless": ["VLESS TCP REALITY"]},
                "data_limit": data_limit,
                "status": "active"
            }
            if expire_days:
                expire_timestamp = int(time.time()) + (expire_days * 24 * 60 * 60)
                user_data["expire"] = expire_timestamp
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.access_token}"
            }
            response = requests.post(url, json=user_data, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 409:
                return self.get_user_info(username)
            else:
                return {}
        except Exception:
            return {}
    
    def get_user_info(self, username: str) -> dict:
        if not self.access_token:
            return {}
        try:
            url = f"{self.base_url}/api/user/{username}"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception:
            return {}
    
    def get_subscription_url(self, username: str) -> str:
        user_info = self.get_user_info(username)
        return user_info.get('subscription_url', '')

def create_vpn_subscription(period_days: int) -> str:
    username = generate_random_string(10)
    marzban = MarzbanAPI(MARZBAN_BASE_URL, MARZBAN_USER, MARZBAN_PASS)
    if marzban.authenticate():
        user_info = marzban.create_user(
            username=username,
            data_limit=MARZBAN_DATA_LIMIT,
            expire_days=period_days
        )
        if user_info:
            return marzban.get_subscription_url(username)
    return ""