from typing import List


def parse_audio_languages(media_info: dict) -> List[str]:
    if not media_info:
        return []

    raw = (
        media_info.get("audioLanguages")
        or media_info.get("AudioLanguages")
        or ""
    )

    if not raw:
        return []

    raw = raw.replace(",", "+")
    parts = [p.strip() for p in raw.split("+") if p.strip()]

    if not parts:
        return []

    unique = sorted(set(p.upper() for p in parts))
    return unique
