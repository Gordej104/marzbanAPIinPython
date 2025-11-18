# MarzbanAPI Minimal Python Client

A simple synchronous Python client for Marzban API implemented in `marzbanAPI.py`. It authenticates an admin, creates users with predefined VLESS proxy settings, and retrieves a user’s subscription URL. Configuration values are read from `config.py`.

## Files

- `marzbanAPI.py`: Minimal client with admin authentication and user operations
- `config.py`: Configuration defaults loaded from environment variables

## Requirements

- Python 3.8+
- `requests` library

```bash
pip install requests
```

## How It Works

`marzbanAPI.py` implements:

- `MarzbanAPI.authenticate()`  
  - Sends `POST` to `"{base_url}/api/admin/token"` with `username` and `password`
  - On success, stores `access_token` and returns `True`
  - Returns `False` if any error occurs

- `MarzbanAPI.create_user(username, data_limit=0, expire_days=None)`  
  - Automatically authenticates if `access_token` is not set
  - Sends `POST` to `"/api/user"` with payload:
    - `username`: provided name
    - `proxies`: `{"vless": {"flow": "xtls-rprx-vision"}}`
    - `inbounds`: `{"vless": ["VLESS TCP REALITY"]}`
    - `data_limit`: provided limit (bytes)
    - `status`: `"active"`
    - `expire` (optional): UNIX timestamp (`now + expire_days * 24h`)
  - Headers include `Authorization: Bearer {access_token}`
  - Returns created user JSON on `200 OK`
  - If `409 Conflict`, returns existing user via `get_user_info`
  - Returns `{}` on any error

- `MarzbanAPI.get_user_info(username)`  
  - Requires `access_token` to be present
  - Sends `GET` to `"/api/user/{username}"`
  - Returns user JSON or `{}` on error

- `MarzbanAPI.get_subscription_url(username)`  
  - Calls `get_user_info` and returns `subscription_url` or `""` if missing

- `create_vpn_subscription(period_days)`  
  - Generates random username
  - Creates `MarzbanAPI` with values from `config.py`
  - Authenticates and creates user with `MARZBAN_DATA_LIMIT` and `expire_days=period_days`
  - Returns subscription URL or `""` on failure

## Configuration (`config.py`)

`config.py` reads values from environment variables with safe defaults:

```python
MARZBAN_BASE_URL = os.getenv('MARZBAN_BASE_URL', 'https://example.com')
MARZBAN_USER = os.getenv('MARZBAN_USER', 'Login')
MARZBAN_PASS = os.getenv('MARZBAN_PASS', 'Password')
MARZBAN_DATA_LIMIT = int(os.getenv('MARZBAN_DATA_LIMIT', '100000000000'))
```

- `MARZBAN_BASE_URL`: Base URL of your Marzban panel (e.g., `http://127.0.0.1:8000`)
- `MARZBAN_USER`: Admin username
- `MARZBAN_PASS`: Admin password
- `MARZBAN_DATA_LIMIT`: Data limit in bytes (default `100000000000`)

You can set them via environment:

```bash
set MARZBAN_BASE_URL=http://127.0.0.1:8000
set MARZBAN_USER=admin
set MARZBAN_PASS=secret
set MARZBAN_DATA_LIMIT=0
```

## Usage Examples

- Authenticate and create user:

```python
from marzbanAPI import MarzbanAPI
from config import MARZBAN_BASE_URL, MARZBAN_USER, MARZBAN_PASS

api = MarzbanAPI(MARZBAN_BASE_URL, MARZBAN_USER, MARZBAN_PASS)
if api.authenticate():
    user = api.create_user("test_user", data_limit=0, expire_days=30)
    print(user)
```

- Get subscription URL:

```python
from marzbanAPI import MarzbanAPI
from config import MARZBAN_BASE_URL, MARZBAN_USER, MARZBAN_PASS

api = MarzbanAPI(MARZBAN_BASE_URL, MARZBAN_USER, MARZBAN_PASS)
api.authenticate()
print(api.get_subscription_url("test_user"))
```

- Create subscription via helper:

```python
from marzbanAPI import create_vpn_subscription

url = create_vpn_subscription(period_days=30)
print(url)  # "" if failed
```

## Notes & Limitations

- Client is synchronous and uses `requests`.
- Error handling is minimal: methods return `{}` or `""` on failure.
- Proxy and inbound settings are hardcoded for VLESS (`xtls-rprx-vision`, `VLESS TCP REALITY`).
- SSL verification control is not exposed; requests use default `requests` behavior.
- Adjust payloads and endpoints to match your Marzban deployment if necessary.
