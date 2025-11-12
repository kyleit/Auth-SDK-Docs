# middleware_fastapi.py
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Callable
from .client import AuthClient
from .exceptions import TokenValidationError

security = HTTPBearer(auto_error=False)

class FastAPIAuth:
    def __init__(self, client: AuthClient, audience: Optional[str] = None, raise_on_no_token: bool = True):
        self.client = client
        self.audience = audience
        self.raise_on_no_token = raise_on_no_token

    async def __call__(self, credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
        if not credentials or credentials.scheme.lower() != "bearer":
            if self.raise_on_no_token:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing auth token")
            return None

        token = credentials.credentials
        # 1) Try local verification if possible
        try:
            payload = self.client.verify_jwt(token, audience=self.audience)
            return payload
        except TokenValidationError:
            # fallback to introspect endpoint
            try:
                info = await self.client.async_introspect(token)
                if not info.get("active"):
                    raise HTTPException(status_code=401, detail="Token inactive")
                return info
            except Exception:
                raise HTTPException(status_code=401, detail="Token verification failed")
