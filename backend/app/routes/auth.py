import hmac

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .. import config

router = APIRouter(tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
def login(body: LoginRequest):
    username_ok = hmac.compare_digest(body.username, config.AUTH_USERNAME)
    password_ok = hmac.compare_digest(body.password, config.AUTH_PASSWORD)

    if username_ok and password_ok:
        return {"token": config.AUTH_TOKEN}

    raise HTTPException(status_code=401, detail="Invalid credentials")
