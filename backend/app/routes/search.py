from typing import Literal

from fastapi import APIRouter, HTTPException, Query

from ..services import arr

router = APIRouter(tags=["search"])


@router.get("/search")
def search_items(
    q: str = Query(..., min_length=1),
    type: Literal["tv", "movie"] = Query(...),
    instance_id: int = Query(..., ge=1),
) -> list[dict]:
    query = q.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    kind = "sonarr" if type == "tv" else "radarr"
    return arr.search(instance_id, kind, query)
