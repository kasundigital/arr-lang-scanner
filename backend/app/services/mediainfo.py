from typing import Dict, List

from ..utils.parse import parse_audio_languages


def aggregate_languages(files: List[dict]) -> List[Dict]:
    lang_counts: Dict[str, int] = {}

    for f in files:
        media_info = f.get("mediaInfo") or f.get("mediaInfoJson") or {}
        langs = parse_audio_languages(media_info)
        for lang in langs:
            lang_counts[lang] = lang_counts.get(lang, 0) + 1

    result = [
        {"code": code, "count": count}
        for code, count in lang_counts.items()
    ]
    result.sort(key=lambda x: x["code"])
    return result
