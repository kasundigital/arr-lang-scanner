from typing import Literal, List

from fastapi import APIRouter, HTTPException, Query

from ..services import sonarr, radarr

router = APIRouter(tags=["search"])


@router.get("/search")
def search_items(
    q: str = Query(..., min_length=1),
    type: Literal["tv", "movie"] = Query(...),
) -> List[dict]:
    query = q.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    if type == "tv":
        return sonarr.search_series(query)
    elif type == "movie":
        return radarr.search_movies(query)
    else:
        raise HTTPException(status_code=400, detail="Invalid type")
