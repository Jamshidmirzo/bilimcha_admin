from yt_dlp import YoutubeDL
from typing import Dict

YDL_OPTS_META = {"quiet": True, "skip_download": True}
YDL_OPTS_URL = {"quiet": True, "skip_download": True, "format": "best[ext=mp4]/best"}

def fetch_meta(youtube_id: str) -> Dict:
    """
    Возвращает словарь: title, description, duration, thumbnail
    youtube_id — просто id (dQw4... или полный url — но мы передаём id)
    """
    url = f"https://www.youtube.com/watch?v={youtube_id}"
    with YoutubeDL(YDL_OPTS_META) as ydl:
        info = ydl.extract_info(url, download=False)
    return {
        "title": info.get("title"),
        "description": info.get("description"),
        "duration": info.get("duration"),
        "thumbnail": info.get("thumbnail"),
    }

def get_fresh_video_url(youtube_id: str) -> str:
    """
    Возвращает прямой URL на видео (streamable). Может меняться со временем.
    """
    url = f"https://www.youtube.com/watch?v={youtube_id}"
    with YoutubeDL(YDL_OPTS_URL) as ydl:
        info = ydl.extract_info(url, download=False)
    # info may have "url" directly or via formats; try both
    if info.get("url"):
        return info["url"]
    # fallback: choose first format url
    formats = info.get("formats") or []
    for f in reversed(formats):
        if f.get("url"):
            return f["url"]
    raise RuntimeError("No streamable URL found")
