# authsdk

Python SDK nhỏ cho login / middleware (FastAPI + Flask).

## Cài đặt
```
pip install requests httpx python-jose
```

## Khởi tạo client
```
from authsdk.client import AuthClient 

client = AuthClient(
    base_url="https://auth.example.com",
    jwks_url="https://auth.example.com/.well-known/jwks.json",
    public_key=None
)
```
## Login sync 
```
resp = client.login("alice", "secret")
```
## Login async 
```
 await client.async_login(...)
```
## FastAPI
```
from authsdk.middleware_fastapi import FastAPIAuth

auth_dep = FastAPIAuth(client, audience="my-audience")

@app.get("/protected")
async def p(user=Depends(auth_dep)): ...
```

## Flask

```
from authsdk.middleware_flask import FlaskAuth, login_required

FlaskAuth(app, client=client, audience="my-audience")

@app.route("/p")
@login_required
def p(): ...
```