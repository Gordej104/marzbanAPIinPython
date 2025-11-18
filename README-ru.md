# Минимальный Python-клиент MarzbanAPI

Простой синхронный клиент для API Marzban, реализованный в `marzbanAPI.py`. Он выполняет аутентификацию администратора, создаёт пользователей с преднастроенным VLESS и получает URL подписки пользователя. Конфигурация берётся из `config.py`.

## Файлы

- `marzbanAPI.py`: минимальный клиент с аутентификацией и операциями с пользователями
- `config.py`: конфигурация, читаемая из переменных окружения

## Требования

- Python 3.8+
- Библиотека `requests`

```bash
pip install requests
```

## Как работает

В `marzbanAPI.py` реализованы:

- `MarzbanAPI.authenticate()`  
  - Отправляет `POST` на `"{base_url}/api/admin/token"` с `username` и `password`
  - При успехе сохраняет `access_token` и возвращает `True`
  - Возвращает `False` при любой ошибке

- `MarzbanAPI.create_user(username, data_limit=0, expire_days=None)`  
  - Автоматически выполняет аутентификацию, если токена нет
  - Отправляет `POST` на `"/api/user"` с телом:
    - `username`: имя пользователя
    - `proxies`: `{"vless": {"flow": "xtls-rprx-vision"}}`
    - `inbounds`: `{"vless": ["VLESS TCP REALITY"]}`
    - `data_limit`: лимит данных (в байтах)
    - `status`: `"active"`
    - `expire` (опционально): UNIX-время (`сейчас + expire_days * 24ч`)
  - Заголовки включают `Authorization: Bearer {access_token}`
  - Возвращает JSON созданного пользователя при `200 OK`
  - Если `409 Conflict`, возвращает существующего пользователя через `get_user_info`
  - Возвращает `{}` при любой ошибке

- `MarzbanAPI.get_user_info(username)`  
  - Требует наличия `access_token`
  - Отправляет `GET` на `"/api/user/{username}"`
  - Возвращает JSON пользователя или `{}` при ошибке

- `MarzbanAPI.get_subscription_url(username)`  
  - Вызывает `get_user_info` и возвращает `subscription_url` или `""`, если отсутствует

- `create_vpn_subscription(period_days)`  
  - Генерирует случайный `username`
  - Создаёт `MarzbanAPI` с параметрами из `config.py`
  - Аутентифицируется и создаёт пользователя с `MARZBAN_DATA_LIMIT` и `expire_days=period_days`
  - Возвращает URL подписки или `""` при неуспехе

## Конфигурация (`config.py`)

`config.py` читает значения из окружения с безопасными значениями по умолчанию:

```python
MARZBAN_BASE_URL = os.getenv('MARZBAN_BASE_URL', 'https://example.com')
MARZBAN_USER = os.getenv('MARZBAN_USER', 'Login')
MARZBAN_PASS = os.getenv('MARZBAN_PASS', 'Password')
MARZBAN_DATA_LIMIT = int(os.getenv('MARZBAN_DATA_LIMIT', '100000000000'))
```

- `MARZBAN_BASE_URL`: адрес панели Marzban (например, `http://127.0.0.1:8000`)
- `MARZBAN_USER`: логин администратора
- `MARZBAN_PASS`: пароль администратора
- `MARZBAN_DATA_LIMIT`: лимит данных в байтах (по умолчанию `100000000000`)

Установка через окружение:

```bash
set MARZBAN_BASE_URL=http://127.0.0.1:8000
set MARZBAN_USER=admin
set MARZBAN_PASS=secret
set MARZBAN_DATA_LIMIT=0
```

## Примеры использования

- Аутентификация и создание пользователя:

```python
from marzbanAPI import MarzbanAPI
from config import MARZBAN_BASE_URL, MARZBAN_USER, MARZBAN_PASS

api = MarzbanAPI(MARZBAN_BASE_URL, MARZBAN_USER, MARZBAN_PASS)
if api.authenticate():
    user = api.create_user("test_user", data_limit=0, expire_days=30)
    print(user)
```

- Получение URL подписки:

```python
from marzbanAPI import MarzbanAPI
from config import MARZBAN_BASE_URL, MARZBAN_USER, MARZBAN_PASS

api = MarzbanAPI(MARZBAN_BASE_URL, MARZBAN_USER, MARZBAN_PASS)
api.authenticate()
print(api.get_subscription_url("test_user"))
```

- Создание подписки через хелпер:

```python
from marzbanAPI import create_vpn_subscription

url = create_vpn_subscription(period_days=30)
print(url)  # "" если не удалось
```

## Замечания и ограничения

- Клиент синхронный и использует `requests`.
- Обработка ошибок минимальная: методы возвращают `{}` или `""` при сбоях.
- Настройки прокси и inbound жёстко заданы для VLESS (`xtls-rprx-vision`, `VLESS TCP REALITY`).
- Управление проверкой SSL не вынесено в параметры; используется стандартное поведение `requests`.
- При необходимости скорректируйте payload и пути эндпоинтов под вашу установку Marzban.
