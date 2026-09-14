from __future__ import annotations

from typing import Any

from fastapi import HTTPException

from .. import config, storage
from ..utils.http import get_json


def _instance(instance_id: int, kind: str) -> dict[str, Any]:
    instance = storage.get_instance(instance_id, kind)
    if not instance:
        raise HTTPException(status_code=404, detail=f"{kind.title()} instance not found or disabled")
    return instance


def _headers(instance: dict[str, Any]) -> dict[str, str]:
    return {"X-Api-Key": instance["api_key"]}


def search(instance_id: int, kind: str, query: str) -> list[dict]:
    instance = _instance(instance_id, kind)
    endpoint = "series" if kind == "sonarr" else "movie"
    items = get_json(
        f"{instance['url']}/api/v3/{endpoint}",
        headers=_headers(instance),
        timeout=config.REQUEST_TIMEOUT,
    )
    if not isinstance(items, list):
        raise HTTPException(status_code=502, detail=f"Unexpected response from {kind.title()}")

    q = query.casefold()
    result = []
    for item in items:
        title = item.get("title", "")
        if q in title.casefold():
            result.append({
                "id": item.get("id"),
                "title": title,
                "year": item.get("year"),
                "type": "tv" if kind == "sonarr" else "movie",
                "instanceId": instance_id,
                "instanceName": instance["name"],
            })
    result.sort(key=lambda x: (x["title"] or "").casefold())
    return result[:20]


def episode_files(instance_id: int, series_id: int) -> list[dict]:
    instance = _instance(instance_id, "sonarr")
    data = get_json(
        f"{instance['url']}/api/v3/episodefile",
        headers=_headers(instance),
        params={"seriesId": series_id},
        timeout=config.REQUEST_TIMEOUT,
    )
    if not isinstance(data, list):
        raise HTTPException(status_code=502, detail="Unexpected response from Sonarr")
    return data


def episodes(instance_id: int, series_id: int) -> list[dict]:
    instance = _instance(instance_id, "sonarr")
    data = get_json(
        f"{instance['url']}/api/v3/episode",
        headers=_headers(instance),
        params={"seriesId": series_id},
        timeout=config.REQUEST_TIMEOUT,
    )
    if not isinstance(data, list):
        raise HTTPException(status_code=502, detail="Unexpected response from Sonarr")
    return data


def movie_files(instance_id: int, movie_id: int) -> list[dict] | None:
    instance = _instance(instance_id, "radarr")
    headers = _headers(instance)
    movie = get_json(
        f"{instance['url']}/api/v3/movie/{movie_id}",
        headers=headers,
        timeout=config.REQUEST_TIMEOUT,
    )
    if not isinstance(movie, dict) or "id" not in movie:
        return None
    files = get_json(
        f"{instance['url']}/api/v3/moviefile",
        headers=headers,
        params={"movieId": movie_id},
        timeout=config.REQUEST_TIMEOUT,
    )
    if not isinstance(files, list):
        raise HTTPException(status_code=502, detail="Unexpected response from Radarr")
    return files
