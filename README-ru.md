# MarzbanAPI Python Клиент

Универсальная синхронная Python-библиотека для работы с API панели Marzban. Поддерживает аутентификацию по `access_token` или паре `username/password` и организует операции в секции: `user`, `system`, `core`, `node`.

## Возможности
- Единый HTTP-слой с автоматическим управлением токеном
- Аутентификация через `username/password` или `access_token`
- Модульные секции: `user`, `system`, `core`, `node`
- Простое синхронное API на базе `requests`
- Управление верификацией SSL

## Требования
- Python 3.8+
- Библиотека `requests`

```bash
pip install requests
```

## Обзор файлов
- `marzbanAPI.py`: основная библиотека с `MarzbanAPI` и вспомогательными функциями.
- `config.py` (необязателен): ваш файл конфигурации с константами; библиотека его не требует, но можно использовать для удобства.

## Как работает (`marzbanAPI.py`)
- `MarzbanAPI` инициализируется `base_url` и либо `username/password`, либо `access_token`.
- Приватный метод `_request` оборачивает `requests.request` и добавляет заголовок `Authorization`.
- Секции доступны как свойства:
  - `api.user`: управление пользователями
  - `api.system`: системная статистика и конфигурация
  - `api.core`: управление ядром Xray
  - `api.node`: управление узлами
- Хелпер: `create_vpn_subscription(...)` создаёт пользователя и возвращает его `subscription_url`.

### Инициализация

```python
from marzbanAPI import MarzbanAPI

# Аутентификация по логину/паролю
api = MarzbanAPI(base_url="http://127.0.0.1:8000", username="admin", password="password")

# Или по токену
api = MarzbanAPI(base_url="http://127.0.0.1:8000", access_token="ваш_jwt_токен")
```

### Использование секций

```python
# Пользователи
api.user.create({"username": "test_user", "proxies": {"vless": {}}, "status": "active"})
user = api.user.get("test_user")
api.user.modify("test_user", {"data_limit": 0})
api.user.reset_data_usage("test_user")
api.user.revoke_subscription("test_user")
usage = api.user.get_usage("test_user")
subs_url = api.user.get_subscription_url("test_user")
api.user.delete("test_user")

# Система
stats = api.system.get_stats()
inbounds = api.system.get_inbounds()
hosts = api.system.get_hosts()
api.system.modify_hosts({"example.com": "127.0.0.1"})

# Ядро
core_stats = api.core.get_stats()
api.core.restart()
core_cfg = api.core.get_config()
api.core.modify_config({"loglevel": "info"})

# Узлы
nodes = api.node.get_all()
node = api.node.create({"name": "Node1", "address": "192.168.1.10"})
node_info = api.node.get(node["id"])
api.node.modify(node["id"], {"name": "Node1-Updated"})
api.node.reconnect(node["id"])
api.node.delete(node["id"])
node_usage = api.node.get_usage()
```

### Хелпер: Создание подписки

```python
from marzbanAPI import create_vpn_subscription

url = create_vpn_subscription(
    base_url="http://127.0.0.1:8000",
    admin_username="admin",
    admin_password="password",
    data_limit=0,          # без лимита
    expire_days=30         # опционально
)
print(url)
```

## Необязательная конфигурация (`config.py`)
Библиотека больше не требует `config.py`. Если удобнее хранить настройки централизованно, создайте свой `config.py` и импортируйте значения в скрипт:

```python
# config.py
MARZBAN_BASE_URL = "http://127.0.0.1:8000"
MARZBAN_USER = "admin"
MARZBAN_PASS = "password"
MARZBAN_DATA_LIMIT = 0
```

Использование:

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

## Обработка ошибок и SSL
- Аутентификация выбрасывает `ValueError`, если не переданы учётные данные или не удалось получить токен.
- Все HTTP-вызовы используют `response.raise_for_status()`.
- Управление верификацией SSL через `verify_ssl`:
  - `True` (по умолчанию), `False`, либо путь к сертификату.

```python
api = MarzbanAPI(
  base_url="https://your-host",
  username="admin",
  password="password",
  verify_ssl=False  # или "/path/to/cert.pem"
)
```

## Примечания
- Эндпоинты соответствуют общей структуре API Marzban. Если в вашей установке пути отличаются, скорректируйте методы соответствующей секции.
- Клиент синхронный. Для асинхронной работы можно обернуть вызовы в потоки или мигрировать на `httpx.AsyncClient`.