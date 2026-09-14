from __future__ import annotations

import secrets

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from .. import config, storage
from ..utils.auth import require_auth
from ..utils.http import get_json

router = APIRouter(tags=["settings"])


class SetupRequest(BaseModel):
    username: str
    password: str


class CredentialsRequest(BaseModel):
    username: str
    password: str


class InstanceRequest(BaseModel):
    kind: str
    name: str
    url: str
    api_key: str
    enabled: bool = True


@router.get("/setup-status")
def setup_status():
    return {"setupComplete": storage.is_setup_complete()}


@router.post("/setup")
def initial_setup(body: SetupRequest):
    if storage.is_setup_complete():
        raise HTTPException(status_code=409, detail="Setup is already complete")
    try:
        storage.set_credentials(body.username, body.password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"ok": True, "token": storage.get_setting("auth_token")}


@router.get("/instances", dependencies=[Depends(require_auth)])
def instances():
    return storage.list_instances()


@router.post("/instances", dependencies=[Depends(require_auth)])
def create_instance(body: InstanceRequest):
    try:
        instance_id = storage.save_instance(body.kind, body.name, body.url, body.api_key, body.enabled)
    except Exception as exc:
        detail = str(exc)
        if "UNIQUE constraint" in detail:
            detail = "An instance with that name already exists"
        raise HTTPException(status_code=400, detail=detail) from exc
    return {"ok": True, "id": instance_id}


@router.put("/instances/{instance_id}", dependencies=[Depends(require_auth)])
def update_instance(instance_id: int, body: InstanceRequest):
    try:
        storage.save_instance(body.kind, body.name, body.url, body.api_key, body.enabled, instance_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"ok": True}


@router.delete("/instances/{instance_id}", dependencies=[Depends(require_auth)])
def remove_instance(instance_id: int):
    storage.delete_instance(instance_id)
    return {"ok": True}


@router.post("/instances/{instance_id}/test", dependencies=[Depends(require_auth)])
def test_instance(instance_id: int):
    instance = storage.get_instance(instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    data = get_json(
        f"{instance['url']}/api/v3/system/status",
        headers={"X-Api-Key": instance["api_key"]},
        timeout=config.REQUEST_TIMEOUT,
    )
    return {
        "ok": True,
        "name": data.get("appName") if isinstance(data, dict) else None,
        "version": data.get("version") if isinstance(data, dict) else None,
    }


@router.put("/credentials", dependencies=[Depends(require_auth)])
def update_credentials(body: CredentialsRequest):
    try:
        storage.set_credentials(body.username, body.password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    storage.set_setting("auth_token", secrets.token_urlsafe(48))
    return {"ok": True}
