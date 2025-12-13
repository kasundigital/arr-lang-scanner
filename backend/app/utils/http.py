from typing import Optional, Dict, Any

import requests
from fastapi import HTTPException


def get_json(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    timeout: int = 10,
):
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=timeout)
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Error contacting upstream: {e}")

    if resp.status_code >= 400:
        raise HTTPException(
            status_code=resp.status_code,
            detail=f"Upstream error {resp.status_code}: {resp.text[:200]}",
        )

    try:
        return resp.json()
    except ValueError:
        raise HTTPException(status_code=500, detail="Invalid JSON from upstream")
