import hmac

from fastapi import Header, HTTPException

from .. import config


def require_auth(authorization: str | None = Header(default=None)):
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    token = authorization.split(" ", 1)[1].strip()
    if not token or not hmac.compare_digest(token, config.AUTH_TOKEN):
        raise HTTPException(status_code=401, detail="Invalid token")
