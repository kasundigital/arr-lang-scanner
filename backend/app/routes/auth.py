import hmac

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .. import storage

router = APIRouter(tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
def login(body: LoginRequest):
    if not storage.is_setup_complete():
        raise HTTPException(status_code=409, detail="Initial setup is required")

    username = storage.get_setting("username") or ""
    password_hash = storage.get_setting("password_hash") or ""
    username_ok = hmac.compare_digest(body.username, username)
    password_ok = storage.verify_password(body.password, password_hash)

    if username_ok and password_ok:
        return {"token": storage.get_setting("auth_token")}

    raise HTTPException(status_code=401, detail="Invalid credentials")
