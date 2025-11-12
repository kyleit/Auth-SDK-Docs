# middleware_flask.py
from flask import request, g
from functools import wraps
from .client import AuthClient
from .exceptions import TokenValidationError
from werkzeug.exceptions import Unauthorized

class FlaskAuth:
    def __init__(self, app=None, client: AuthClient = None, audience: str = None, raise_on_no_token: bool = True):
        self.client = client
        self.audience = audience
        self.raise_on_no_token = raise_on_no_token
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        @app.before_request
        def _check_token():
            # skip if route is public maybe you want decorator for that
            auth = request.headers.get("Authorization", "")
            if not auth:
                if self.raise_on_no_token:
                    raise Unauthorized("Missing Authorization header")
                g.current_user = None
                return
            parts = auth.split()
            if len(parts) != 2 or parts[0].lower() != "bearer":
                raise Unauthorized("Invalid Authorization header")
            token = parts[1]
            # try local verification
            try:
                payload = self.client.verify_jwt(token, audience=self.audience)
                g.current_user = payload
            except TokenValidationError:
                # fallback to introspect
                try:
                    info = self.client.introspect(token)
                    if not info.get("active"):
                        raise Unauthorized("Token inactive")
                    g.current_user = info
                except Exception:
                    raise Unauthorized("Token verification failed")

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        from flask import g
        if getattr(g, "current_user", None) is None:
            raise Unauthorized("Authentication required")
        return f(*args, **kwargs)
    return decorated
