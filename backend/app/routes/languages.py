from typing import Literal

from fastapi import APIRouter, HTTPException, Query

from ..services import sonarr, radarr, mediainfo
from ..utils.parse import parse_audio_languages

router = APIRouter(tags=["languages"])


@router.get("/languages")
def get_languages(
    id: int = Query(..., description="Sonarr seriesId or Radarr movieId"),
    type: Literal["tv", "movie"] = Query(...),
):
    if type == "tv":
        files = sonarr.get_episode_files(series_id=id)
        lang_counts = mediainfo.aggregate_languages(files)
        return {
            "type": "tv",
            "id": id,
            "totalFiles": len(files),
            "audioLanguages": lang_counts,
        }

    elif type == "movie":
        files = radarr.get_movie_files(movie_id=id)
        if files is None:
            raise HTTPException(status_code=404, detail="Movie not found")
        lang_counts = mediainfo.aggregate_languages(files)
        return {
            "type": "movie",
            "id": id,
            "totalFiles": len(files),
            "audioLanguages": lang_counts,
        }

    else:
        raise HTTPException(status_code=400, detail="Invalid type")


@router.get("/tv/{series_id}/episodes")
def get_tv_episodes_languages(series_id: int):
    episodes = sonarr.get_episodes(series_id=series_id)
    files = sonarr.get_episode_files(series_id=series_id)

    file_by_id = {f["id"]: f for f in files if "id" in f}

    seasons_map: dict[int, list[dict]] = {}

    for ep in episodes:
        season_no = ep.get("seasonNumber")
        episode_no = ep.get("episodeNumber")
        file_id = ep.get("episodeFileId")
        file_obj = file_by_id.get(file_id) if file_id else None

        media_info = file_obj.get("mediaInfo") if file_obj else None
        langs = parse_audio_languages(media_info) if media_info else []

        ep_entry = {
            "id": ep.get("id"),
            "title": ep.get("title"),
            "seasonNumber": season_no,
            "episodeNumber": episode_no,
            "episodeFileId": file_id,
            "hasFile": bool(file_obj),
            "audioLanguages": langs,
        }

        seasons_map.setdefault(season_no, []).append(ep_entry)

    seasons = []
    for s_num in sorted(seasons_map.keys()):
        eps_sorted = sorted(
            seasons_map[s_num],
            key=lambda e: (e.get("episodeNumber") or 0),
        )
        seasons.append(
            {
                "seasonNumber": s_num,
                "episodes": eps_sorted,
            }
        )

    return {
        "seriesId": series_id,
        "seasonCount": len(seasons),
        "seasons": seasons,
    }
