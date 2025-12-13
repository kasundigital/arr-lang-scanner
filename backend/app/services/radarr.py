from typing import List, Dict, Optional

from fastapi import HTTPException

from .. import config
from ..utils.http import get_json


def _get_headers() -> dict:
    if not config.RADARR_API_KEY:
        raise HTTPException(status_code=500, detail="RADARR_API_KEY is not configured")
    return {"X-Api-Key": config.RADARR_API_KEY}


def search_movies(query: str) -> List[Dict]:
    url = f"{config.RADARR_URL}/api/v3/movie"
    movies = get_json(url, headers=_get_headers(), timeout=config.REQUEST_TIMEOUT)

    q_lower = query.lower()
    matches: List[Dict] = []

    for m in movies:
        title = m.get("title", "")
        if q_lower in title.lower():
            matches.append(
                {
                    "id": m["id"],
                    "title": title,
                    "year": m.get("year"),
                    "type": "movie",
                }
            )

    matches.sort(key=lambda x: (x["title"] or ""))
    return matches[:20]


def get_movie_files(movie_id: int) -> Optional[List[Dict]]:
    movie_url = f"{config.RADARR_URL}/api/v3/movie/{movie_id}"
    movie = get_json(movie_url, headers=_get_headers(), timeout=config.REQUEST_TIMEOUT)

    if not movie or "id" not in movie:
        return None

    files_url = f"{config.RADARR_URL}/api/v3/moviefile"
    params = {"movieId": movie_id}
    files = get_json(files_url, headers=_get_headers(), params=params, timeout=config.REQUEST_TIMEOUT)

    if not isinstance(files, list):
        raise HTTPException(status_code=500, detail="Unexpected response from Radarr")

    return files
