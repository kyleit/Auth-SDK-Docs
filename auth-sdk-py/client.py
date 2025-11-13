import time
from typing import Optional, Dict, Any
import requests
import httpx
from jose import jwt, JWTError

from .exceptions import LoginError, RefreshError, TokenValidationError

DEFAULT_TIMEOUT = 10


class AuthClient:
    """
    GH Platform Multi-Tenant Auth Client
    
    Supports:
    - login(identifier, password, client_id, totp?)
    - refresh(refresh_token)
    - introspect(token)
    - optional local JWT verification via jwks_url or public_key
    """

    def __init__(
        self,
        tenant: str,
        base_url: str,
        jwks_url: Optional[str] = None,
        public_key: Optional[str] = None,
        algo: str = "RS256",
        timeout: int = DEFAULT_TIMEOUT,
    ):
        self.tenant = tenant
        self.base_url = base_url.rstrip("/")

        prefix = f"/api/v1/{tenant}/auth"

        self.login_url = f"{self.base_url}{prefix}/login"
        self.refresh_url = f"{self.base_url}{prefix}/refresh"
        self.introspect_url = f"{self.base_url}{prefix}/introspect"

        self.jwks_url = jwks_url
        self.public_key = public_key
        self.algo = algo
        self.timeout = timeout

        self._jwks = None
        if jwks_url:
            self._fetch_jwks()

    # -------------------------------------
    # JWKS
    # -------------------------------------
    def _fetch_jwks(self):
        try:
            r = requests.get(self.jwks_url, timeout=self.timeout)
            r.raise_for_status()
            self._jwks = r.json()
        except Exception:
            self._jwks = None

    # -------------------------------------
    # LOGIN (sync)
    # -------------------------------------
    def login(
        self,
        identifier: str,
        password: str,
        client_id: str,
        totp: Optional[str] = None,
    ) -> Dict[str, Any]:

        payload = {
            "identifier": identifier,
            "password": password,
            "client_id": client_id,
        }
        if totp:
            payload["totp"] = totp

        try:
            r = requests.post(self.login_url, json=payload, timeout=self.timeout)
            r.raise_for_status()
            return r.json()

        except requests.HTTPError as e:
            raise LoginError(f"Login failed: {e}; body={getattr(e.response, 'text', None)}")

        except Exception as e:
            raise LoginError(f"Login request error: {e}")

    # -------------------------------------
    # REFRESH (sync)
    # -------------------------------------
    def refresh(self, refresh_token: str) -> Dict[str, Any]:
        try:
            r = requests.post(
                self.refresh_url,
                json={"refresh_token": refresh_token},
                timeout=self.timeout,
            )
            r.raise_for_status()
            return r.json()
        except requests.HTTPError as e:
            raise RefreshError(f"Refresh failed: {e}; body={e.response.text}")
        except Exception as e:
            raise RefreshError(f"Refresh request error: {e}")

    # -------------------------------------
    # INTROSPECT (sync)
    # -------------------------------------
    def introspect(self, token: str) -> Dict[str, Any]:
        try:
            r = requests.post(
                self.introspect_url,
                json={"token": token},
                timeout=self.timeout,
            )
            r.raise_for_status()
            return r.json()
        except Exception as e:
            raise TokenValidationError(f"Introspect failed: {e}")

    # -------------------------------------
    # ASYNC: login
    # -------------------------------------
    async def async_login(
        self,
        identifier: str,
        password: str,
        client_id: str,
        totp: Optional[str] = None,
    ) -> Dict[str, Any]:

        payload = {
            "identifier": identifier,
            "password": password,
            "client_id": client_id,
        }
        if totp:
            payload["totp"] = totp

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                r = await client.post(self.login_url, json=payload)
                r.raise_for_status()
                return r.json()
            except httpx.HTTPStatusError as e:
                raise LoginError(f"Login failed: {e}; body={e.response.text}")
            except Exception as e:
                raise LoginError(f"Login request error: {e}")

    # -------------------------------------
    # ASYNC: refresh
    # -------------------------------------
    async def async_refresh(self, refresh_token: str) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                r = await client.post(
                    self.refresh_url,
                    json={"refresh_token": refresh_token},
                )
                r.raise_for_status()
                return r.json()
            except Exception as e:
                raise RefreshError(f"Refresh failed: {e}")

    # -------------------------------------
    # ASYNC: introspect
    # -------------------------------------
    async def async_introspect(self, token: str) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                r = await client.post(
                    self.introspect_url,
                    json={"token": token},
                )
                r.raise_for_status()
                return r.json()
            except Exception as e:
                raise TokenValidationError(f"Introspect failed: {e}")

    # -------------------------------------
    # JWT LOCAL VERIFY (optional)
    # -------------------------------------
    def _get_signing_key_from_jwks(self, kid: str):
        if not self._jwks:
            self._fetch_jwks()
            if not self._jwks:
                raise TokenValidationError("JWKS not available")

        for key in self._jwks.get("keys", []):
            if key.get("kid") == kid:
                return key
        raise TokenValidationError("Signing key not found")

    def verify_jwt(self, token: str, audience: Optional[str] = None) -> Dict[str, Any]:
        try:
            headers = jwt.get_unverified_header(token)
        except JWTError as e:
            raise TokenValidationError(f"Invalid token header: {e}")

        # Prefer static public key
        if self.public_key:
            try:
                return jwt.decode(
                    token,
                    self.public_key,
                    algorithms=[self.algo],
                    audience=audience,
                )
            except JWTError as e:
                raise TokenValidationError(f"JWT verification failed: {e}")

        # Else use JWKS
        if self.jwks_url:
            key = self._get_signing_key_from_jwks(headers.get("kid"))
            try:
                return jwt.decode(
                    token,
                    key,
                    algorithms=[self.algo],
                    audience=audience,
                )
            except JWTError as e:
                raise TokenValidationError(f"JWT verification failed: {e}")

        raise TokenValidationError("No public_key or jwks_url available.")
