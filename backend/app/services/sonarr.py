from typing import List, Dict

from fastapi import HTTPException

from .. import config
from ..utils.http import get_json


def _get_headers() -> dict:
    if not config.SONARR_API_KEY:
        raise HTTPException(status_code=500, detail="SONARR_API_KEY is not configured")
    return {"X-Api-Key": config.SONARR_API_KEY}


def search_series(query: str) -> List[Dict]:
    url = f"{config.SONARR_URL}/api/v3/series"
    series = get_json(url, headers=_get_headers(), timeout=config.REQUEST_TIMEOUT)

    q_lower = query.lower()
    matches: List[Dict] = []

    for s in series:
        title = s.get("title", "")
        if q_lower in title.lower():
            matches.append(
                {
                    "id": s["id"],
                    "title": title,
                    "year": s.get("year"),
                    "type": "tv",
                }
            )

    matches.sort(key=lambda x: (x["title"] or ""))
    return matches[:20]


def get_episode_files(series_id: int) -> List[Dict]:
    url = f"{config.SONARR_URL}/api/v3/episodefile"
    params = {"seriesId": series_id}
    files = get_json(url, headers=_get_headers(), params=params, timeout=config.REQUEST_TIMEOUT)

    if not isinstance(files, list):
        raise HTTPException(status_code=500, detail="Unexpected response from Sonarr (episodefile)")

    return files


def get_episodes(series_id: int) -> List[Dict]:
    url = f"{config.SONARR_URL}/api/v3/episode"
    params = {"seriesId": series_id}
    episodes = get_json(url, headers=_get_headers(), params=params, timeout=config.REQUEST_TIMEOUT)

    if not isinstance(episodes, list):
        raise HTTPException(status_code=500, detail="Unexpected response from Sonarr (episode)")

    return episodes
