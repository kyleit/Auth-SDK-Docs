# client.py
import time
from typing import Optional, Dict, Any
import requests
import httpx
from jose import jwt, JWTError
from jose.utils import base64url_decode

from .exceptions import LoginError, RefreshError, TokenValidationError

DEFAULT_TIMEOUT = 10

class AuthClient:
    """
    Simple auth client supporting:
    - login (username+password + optional totp)
    - refresh
    - token introspect
    - optional local JWT verification via JWKS or public_key
    """
    def __init__(
        self,
        base_url: str,
        login_path: str = "/api/v1/auth/login",
        refresh_path: str = "/api/v1/auth/refresh",
        introspect_path: str = "/api/v1/auth/introspect",
        jwks_url: Optional[str] = None,
        public_key: Optional[str] = None,
        algo: str = "RS256",
        timeout: int = DEFAULT_TIMEOUT,
    ):
        self.base_url = base_url.rstrip("/")
        self.login_url = f"{self.base_url}{login_path}"
        self.refresh_url = f"{self.base_url}{refresh_path}"
        self.introspect_url = f"{self.base_url}{introspect_path}"
        self.jwks_url = jwks_url
        self.public_key = public_key
        self.algo = algo
        self.timeout = timeout
        self._jwks = None
        if jwks_url:
            self._fetch_jwks()

    def _fetch_jwks(self):
        try:
            r = requests.get(self.jwks_url, timeout=self.timeout)
            r.raise_for_status()
            self._jwks = r.json()
        except Exception:
            self._jwks = None

    # ---------- Sync methods ----------
    def login(self, username: str, password: str, totp: Optional[str] = None, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = {"username": username, "password": password}
        if totp:
            payload["totp"] = totp
        if extra:
            payload.update(extra)
        try:
            r = requests.post(self.login_url, json=payload, timeout=self.timeout)
            r.raise_for_status()
            return r.json()
        except requests.HTTPError as e:
            raise LoginError(f"Login failed: {e}; body={getattr(e.response, 'text', None)}")
        except Exception as e:
            raise LoginError(f"Login request error: {e}")

    def refresh(self, refresh_token: str) -> Dict[str, Any]:
        try:
            r = requests.post(self.refresh_url, json={"refresh_token": refresh_token}, timeout=self.timeout)
            r.raise_for_status()
            return r.json()
        except requests.HTTPError as e:
            raise RefreshError(f"Refresh failed: {e}; body={getattr(e.response, 'text', None)}")
        except Exception as e:
            raise RefreshError(f"Refresh request error: {e}")

    def introspect(self, access_token: str) -> Dict[str, Any]:
        try:
            r = requests.post(self.introspect_url, json={"token": access_token}, timeout=self.timeout)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            raise TokenValidationError(f"Introspect failed: {e}")

    # ---------- Async methods ----------
    async def async_login(self, username: str, password: str, totp: Optional[str] = None, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = {"username": username, "password": password}
        if totp:
            payload["totp"] = totp
        if extra:
            payload.update(extra)
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                r = await client.post(self.login_url, json=payload)
                r.raise_for_status()
                return r.json()
            except httpx.HTTPStatusError as e:
                raise LoginError(f"Login failed: {e}; body={e.response.text}")
            except Exception as e:
                raise LoginError(f"Login request error: {e}")

    async def async_refresh(self, refresh_token: str) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                r = await client.post(self.refresh_url, json={"refresh_token": refresh_token})
                r.raise_for_status()
                return r.json()
            except Exception as e:
                raise RefreshError(f"Refresh failed: {e}")

    async def async_introspect(self, access_token: str) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                r = await client.post(self.introspect_url, json={"token": access_token})
                r.raise_for_status()
                return r.json()
            except Exception as e:
                raise TokenValidationError(f"Introspect failed: {e}")

    # ---------- JWT local verification ----------
    def _get_signing_key_from_jwks(self, kid: str):
        if not self._jwks:
            self._fetch_jwks()
            if not self._jwks:
                raise TokenValidationError("JWKS not available")
        for key in self._jwks.get("keys", []):
            if key.get("kid") == kid:
                return key
        raise TokenValidationError("Signing key not found in JWKS")

    def verify_jwt(self, token: str, audience: Optional[str] = None) -> Dict[str, Any]:
        """
        Verify JWT locally:
        - If public_key is set -> use it
        - Else if jwks_url is set -> fetch jwks and find key by kid
        - Else raise TokenValidationError
        Returns payload dict on success.
        """
        try:
            headers = jwt.get_unverified_header(token)
        except JWTError as e:
            raise TokenValidationError(f"Invalid token header: {e}")

        if self.public_key:
            try:
                payload = jwt.decode(token, self.public_key, algorithms=[self.algo], audience=audience)
                return payload
            except JWTError as e:
                raise TokenValidationError(f"JWT verification failed: {e}")

        if self.jwks_url:
            key = self._get_signing_key_from_jwks(headers.get("kid"))
            # build a public key PEM from key info if needed (python-jose can accept jwk dict)
            try:
                payload = jwt.decode(token, key, algorithms=[self.algo], audience=audience)
                return payload
            except JWTError as e:
                raise TokenValidationError(f"JWT verification failed: {e}")

        raise TokenValidationError("No public_key or jwks_url configured for local verification.")
