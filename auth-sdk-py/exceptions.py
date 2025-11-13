# exceptions.py
class AuthSDKError(Exception):
    """Base SDK error."""

class LoginError(AuthSDKError):
    """Raised when login fails."""

class TokenValidationError(AuthSDKError):
    """Raised when token validation fails."""

class RefreshError(AuthSDKError):
    """Refresh token failed."""
