# 🧩 GH Platform – Python Auth SDK (Multi‑Tenant)

Python SDK hỗ trợ xác thực cho hệ thống **GH Platform Authenticate**, bao gồm:

- Login (identifier + password + client_id + optional TOTP)  
- Refresh Token  
- Introspect  
- Middleware cho **FastAPI** & **Flask**  
- Hỗ trợ kiến trúc **đa‑tenant**: `/api/v1/{tenant}/auth/...`


---

## 📦 Cài đặt

SDK yêu cầu các package sau:

```bash
pip install requests httpx python-jose
```

---

## 🚀 Khởi tạo AuthClient (chuẩn multi‑tenant)

```python
from authsdk.client import AuthClient

client = AuthClient(
    tenant="demo",
    base_url="https://auth.example.com",
    jwks_url="https://auth.example.com/.well-known/jwks.json",
    public_key=None
)
```

--- 

## Client tự tạo:


```endpoint
    /api/v1/demo/auth/login
    /api/v1/demo/auth/refresh
    /api/v1/demo/auth/introspect
```


---

## 🔐 Login (sync)

```python
resp = client.login(
    identifier="alice@example.com",
    password="User@123",
    client_id="gh-platform-admin"
)

print(resp["access_token"])
```

---

## 🔐 Login (async)

```python
resp = await client.async_login(
    identifier="alice@example.com",
    password="User@123",
    client_id="gh-platform-admin"
)
```

---

## 🔄 Refresh

```python
new_tokens = client.refresh(refresh_token)
```

---

## 🔍 Introspect

```python
info = client.introspect(access_token)
```

---

# ⚙️ Middleware

## ✳️ FastAPI

```python
from fastapi import Depends, FastAPI
from authsdk.middleware_fastapi import FastAPIAuth

app = FastAPI()

auth_dep = FastAPIAuth(client, audience="my-service")

@app.get("/protected")
async def protected(user = Depends(auth_dep)):
    return {"user": user}
```

---

## ✳️ Flask

```python
from flask import Flask
from authsdk.middleware_flask import FlaskAuth, login_required

app = Flask(__name__)

FlaskAuth(app, client=client, audience="my-service")

@app.route("/protected")
@login_required
def protected():
    return {"user": "ok"}
```

---

## 📁 Cấu trúc SDK

```directory
py-authsdk/
├── client.py
├── exceptions.py
├── middleware_fastapi.py
├── middleware_flask.py
└── __init__.py
```

---
 
## 🧾 License  
MIT License © 2025 GH Platform
