from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .. import config

router = APIRouter(tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
def login(body: LoginRequest):
    if (
        body.username == config.AUTH_USERNAME
        and body.password == config.AUTH_PASSWORD
    ):
        return {"token": config.AUTH_TOKEN}

    raise HTTPException(status_code=401, detail="Invalid credentials")
