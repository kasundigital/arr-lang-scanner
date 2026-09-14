import hmac

from fastapi import Header, HTTPException

from .. import storage


def require_auth(authorization: str | None = Header(default=None)):
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    token = authorization.split(" ", 1)[1].strip()
    expected = storage.get_setting("auth_token") or ""
    if not token or not expected or not hmac.compare_digest(token, expected):
        raise HTTPException(status_code=401, detail="Invalid token")
