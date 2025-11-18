import os

MARZBAN_BASE_URL = os.getenv('MARZBAN_BASE_URL', 'https://example.com')
MARZBAN_USER = os.getenv('MARZBAN_USER', 'Login')
MARZBAN_PASS = os.getenv('MARZBAN_PASS', 'Password')
MARZBAN_DATA_LIMIT = int(os.getenv('MARZBAN_DATA_LIMIT', '100000000000'))