from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
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
                raise HTTPException(401, "Missing auth token")
            return None

        token = credentials.credentials

        try:
            return self.client.verify_jwt(token, audience=self.audience)
        except TokenValidationError:
            # fallback to introspect
            try:
                info = await self.client.async_introspect(token)
                if not info.get("active"):
                    raise HTTPException(401, "Token inactive")
                return info
            except Exception:
                raise HTTPException(401, "Token verification failed")
