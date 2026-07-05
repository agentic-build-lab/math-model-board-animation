from __future__ import annotations

import json
import re
from html import unescape
from typing import Any
from urllib.error import URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from .candidates import Candidate, normalize_candidate


DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)


def fetch_zhihu_hot(limit: int = 50, timeout_s: int = 15) -> list[Candidate]:
    url = f"https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit={limit}&desktop=true"
    try:
        payload = _fetch_text(url, timeout_s=timeout_s)
        data = json.loads(payload)
    except (URLError, TimeoutError, ValueError, json.JSONDecodeError):
        return []

    candidates: list[Candidate] = []
    for item in data.get("data") or []:
        target = item.get("target") or {}
        title_area = target.get("title_area") or {}
        title = title_area.get("text") or target.get("title")
        if not title:
            continue
        target_url = target.get("url") or target.get("link", {}).get("url")
        snapshot_text = title
        excerpt = _first_text(target, ("excerpt_area", "excerpt", "summary", "description"))
        if excerpt:
            snapshot_text = f"{title}\n\n{excerpt}"
        candidates.append(
            normalize_candidate(
                title=title,
                source="trend:zhihu_hot",
                snapshot_text=snapshot_text,
                url=target_url,
                category="public_discussion",
                tags=["zhihu", "hot"],
                raw=_safe_raw(item),
            )
        )
    return candidates[:limit]


def fetch_weibo_hot(limit: int = 50, timeout_s: int = 15) -> list[Candidate]:
    url = "https://s.weibo.com/top/summary?cate=realtimehot"
    try:
        html = _fetch_text(url, timeout_s=timeout_s)
    except (URLError, TimeoutError, ValueError):
        return []

    candidates: list[Candidate] = []
    seen: set[str] = set()
    for match in re.finditer(r'<a[^>]+href="(?P<href>/weibo\?q=[^"]+)"[^>]*>(?P<title>.*?)</a>', html):
        title = _strip_html(match.group("title"))
        if not title or title in seen or title in {"更多", "实时热点"}:
            continue
        seen.add(title)
        item_url = f"https://s.weibo.com{unescape(match.group('href'))}"
        candidates.append(
            normalize_candidate(
                title=title,
                source="trend:weibo_hot",
                snapshot_text=f"{title}\n\nWeibo realtime hot-search item.",
                url=item_url,
                category="public_discussion",
                tags=["weibo", "hot"],
            )
        )
        if len(candidates) >= limit:
            break
    return candidates


def fetch_manual_topics(topics: list[str], *, source: str = "manual:user") -> list[Candidate]:
    return [
        normalize_candidate(
            title=topic,
            source=source,
            snapshot_text=topic,
            url=f"manual://topic/{quote(topic)}",
            category="manual",
            tags=["manual"],
        )
        for topic in topics
        if topic.strip()
    ]


def _fetch_text(url: str, *, timeout_s: int) -> str:
    request = Request(url, headers={"User-Agent": DEFAULT_USER_AGENT})
    with urlopen(request, timeout=timeout_s) as response:
        return response.read().decode("utf-8", errors="replace")


def _first_text(value: dict[str, Any], keys: tuple[str, ...]) -> str | None:
    for key in keys:
        current = value.get(key)
        if isinstance(current, dict):
            text = current.get("text")
            if text:
                return str(text)
        elif isinstance(current, str) and current:
            return current
    return None


def _strip_html(value: str) -> str:
    text = re.sub(r"<[^>]+>", "", value)
    text = unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def _safe_raw(value: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": value.get("type"),
        "detail_text": value.get("detail_text"),
        "attached_info": value.get("attached_info"),
    }
