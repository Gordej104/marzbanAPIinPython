# MarzbanAPI Python Client

A universal, synchronous Python client for the Marzban VPN panel API. It supports authentication with either an access token or a username/password pair and organizes operations into clear sections: `user`, `system`, `core`, and `node`.

## Features
- Unified HTTP layer with automatic token management
- Authentication via `username/password` or `access_token`
- Modular sections: `user`, `system`, `core`, `node`
- Simple, synchronous API using `requests`
- Optional SSL verification control

## Requirements
- Python 3.8+
- `requests` library

```bash
pip install requests
```

## File Overview
- `marzbanAPI.py`: Core library containing `MarzbanAPI` and helper functions.
- `config.py` (optional): Your configuration file for constants; not required by the library but can be used to centralize settings.

## How It Works (`marzbanAPI.py`)
- `MarzbanAPI` is initialized with `base_url` and either `username/password` or `access_token`.
- A unified private method `_request` wraps `requests.request` and adds `Authorization` headers.
- Sections are exposed as properties:
  - `api.user`: user management
  - `api.system`: system statistics and configuration
  - `api.core`: Xray core management
  - `api.node`: multi-node management
- Helper: `create_vpn_subscription(...)` creates a user and returns its `subscription_url`.

### Initialization

```python
from marzbanAPI import MarzbanAPI

# Username/Password auth
api = MarzbanAPI(base_url="http://127.0.0.1:8000", username="admin", password="password")

# Or Access Token auth
api = MarzbanAPI(base_url="http://127.0.0.1:8000", access_token="your_jwt_token")
```

### Using Sections

```python
# User operations
api.user.create({"username": "test_user", "proxies": {"vless": {}}, "status": "active"})
user = api.user.get("test_user")
api.user.modify("test_user", {"data_limit": 0})
api.user.reset_data_usage("test_user")
api.user.revoke_subscription("test_user")
usage = api.user.get_usage("test_user")
subs_url = api.user.get_subscription_url("test_user")
api.user.delete("test_user")

# System operations
stats = api.system.get_stats()
inbounds = api.system.get_inbounds()
hosts = api.system.get_hosts()
api.system.modify_hosts({"example.com": "127.0.0.1"})

# Core operations
core_stats = api.core.get_stats()
api.core.restart()
core_cfg = api.core.get_config()
api.core.modify_config({"loglevel": "info"})

# Node operations
nodes = api.node.get_all()
node = api.node.create({"name": "Node1", "address": "192.168.1.10"})
node_info = api.node.get(node["id"])
api.node.modify(node["id"], {"name": "Node1-Updated"})
api.node.reconnect(node["id"])
api.node.delete(node["id"])
node_usage = api.node.get_usage()
```

### Helper: Create Subscription

```python
from marzbanAPI import create_vpn_subscription

url = create_vpn_subscription(
    base_url="http://127.0.0.1:8000",
    admin_username="admin",
    admin_password="password",
    data_limit=0,          # unlimited
    expire_days=30         # optional
)
print(url)
```

## Optional Configuration (`config.py`)
The library no longer requires `config.py`. If you prefer centralizing settings, you can create your own `config.py` and import values into your scripts:

```python
# config.py
MARZBAN_BASE_URL = "http://127.0.0.1:8000"
MARZBAN_USER = "admin"
MARZBAN_PASS = "password"
MARZBAN_DATA_LIMIT = 0
```

Then use:

```python
from config import MARZBAN_BASE_URL, MARZBAN_USER, MARZBAN_PASS, MARZBAN_DATA_LIMIT
from marzbanAPI import MarzbanAPI, create_vpn_subscription

api = MarzbanAPI(MARZBAN_BASE_URL, username=MARZBAN_USER, password=MARZBAN_PASS)
url = create_vpn_subscription(
    base_url=MARZBAN_BASE_URL,
    admin_username=MARZBAN_USER,
    admin_password=MARZBAN_PASS,
    data_limit=MARZBAN_DATA_LIMIT,
    expire_days=30,
)
print(url)
```

## Error Handling and SSL
- Authentication raises `ValueError` if credentials are missing or login fails.
- All HTTP calls use `response.raise_for_status()`.
- Control SSL verification via `verify_ssl`:
  - `True` (default), `False`, or path to a certificate bundle.

```python
api = MarzbanAPI(
  base_url="https://your-host",
  username="admin",
  password="password",
  verify_ssl=False  # or "/path/to/cert.pem"
)
```

## Notes
- Endpoints are aligned with common Marzban API routes. If your deployment differs, adjust the paths in section methods.
- The client is synchronous. If you need async, consider wrapping with threads or migrating to `httpx.AsyncClient`.
