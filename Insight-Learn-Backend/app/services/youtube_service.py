import os
import requests
from datetime import datetime

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")

def youtube_enabled() -> bool:
    return bool(YOUTUBE_API_KEY)

def search_youtube(query: str, max_results: int = 6):
    if not youtube_enabled():
        raise RuntimeError("YouTube API key missing. Set YOUTUBE_API_KEY in environment.")

    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        "key": YOUTUBE_API_KEY,
        "safeSearch": "moderate",
    }
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()

    results = []
    for item in data.get("items", []):
        vid = (item.get("id") or {}).get("videoId")
        sn = item.get("snippet") or {}
        if not vid:
            continue
        results.append({
            "videoId": vid,
            "title": sn.get("title", ""),
            "channelTitle": sn.get("channelTitle", ""),
            "publishedAt": sn.get("publishedAt", ""),
            "url": f"https://www.youtube.com/watch?v={vid}",
            "thumbnail": (sn.get("thumbnails", {}).get("medium") or {}).get("url")
                      or (sn.get("thumbnails", {}).get("default") or {}).get("url"),
            "description": sn.get("description", "")
        })
    return results

def merge_dedup(lists):
    seen = set()
    merged = []
    for L in lists:
        for it in L:
            vid = it.get("videoId")
            if vid and vid not in seen:
                seen.add(vid)
                merged.append(it)
    return merged