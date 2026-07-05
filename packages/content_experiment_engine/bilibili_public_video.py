from __future__ import annotations

import json
import re
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.parse import urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen


BVID_RE = re.compile(r"(BV[0-9A-Za-z]{10})")
VIEW_API = "https://api.bilibili.com/x/web-interface/view"
REPLY_API = "https://api.bilibili.com/x/v2/reply"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)


def extract_bvid(value: str) -> str | None:
    match = BVID_RE.search(value.strip())
    return match.group(1) if match else None


def fetch_public_bilibili_snapshot(
    url_or_bvid: str,
    output_dir: Path,
    *,
    max_comments: int = 30,
    timeout_s: int = 20,
) -> dict[str, Any]:
    """Capture public Bilibili metadata and hot comments without login."""
    bvid = extract_bvid(url_or_bvid)
    if not bvid:
        raise ValueError("Bilibili URL or BV id is required.")

    output_dir.mkdir(parents=True, exist_ok=True)
    fetched_at = datetime.now(UTC).isoformat()
    video_url = f"https://www.bilibili.com/video/{bvid}"
    raw_response_path = output_dir / "raw_responses.jsonl"
    raw_records: list[dict[str, Any]] = []
    captured_api_urls: list[str] = []
    limitations = ["public_front_page_only", "creator_dashboard_metrics_unavailable"]

    video_payload = _get_json(VIEW_API, {"bvid": bvid}, timeout_s=timeout_s)
    raw_records.append({"url": VIEW_API, "data": video_payload})
    captured_api_urls.append(VIEW_API)
    video = _parse_video(video_payload, bvid)

    comments: list[dict[str, Any]] = []
    if video.get("aid"):
        try:
            comments, comment_records = _fetch_comments(
                int(video["aid"]),
                max_comments=max_comments,
                timeout_s=timeout_s,
            )
            raw_records.extend(comment_records)
            captured_api_urls.append(REPLY_API)
        except (URLError, TimeoutError, ValueError, RuntimeError) as exc:
            limitations.append(f"comments_error: {str(exc)[:240]}")
    else:
        limitations.append("aid_missing_comments_unavailable")

    raw_response_path.write_text(
        "\n".join(json.dumps(record, ensure_ascii=False) for record in raw_records),
        encoding="utf-8",
    )

    snapshot = {
        "schema_version": "1.0",
        "source": {
            "platform": "bilibili",
            "adapter": "bilibili_public_video",
            "url": video_url,
            "resolved_url": _sanitize_url(video_url),
            "platform_video_id": bvid,
            "bvid": bvid,
            "aweme_id": None,
            "fetched_at": fetched_at,
        },
        "video": {
            "title": video.get("title"),
            "description": video.get("description"),
            "author": video.get("author"),
            "created_at": video.get("created_at"),
            "duration_ms": video.get("duration_ms"),
        },
        "metrics": {
            "play_count": video.get("play_count"),
            "like_count": video.get("like_count"),
            "comment_count": video.get("comment_count"),
            "share_count": video.get("share_count"),
            "collect_count": video.get("collect_count"),
            "coin_count": video.get("coin_count"),
            "danmaku_count": video.get("danmaku_count"),
        },
        "comments": comments,
        "evidence": {
            "screenshot_path": None,
            "raw_response_path": str(raw_response_path),
            "captured_api_urls": captured_api_urls,
        },
        "limitations": limitations,
    }
    (output_dir / "snapshot.json").write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return snapshot


def _get_json(url: str, params: dict[str, Any], *, timeout_s: int) -> dict[str, Any]:
    full_url = f"{url}?{urlencode(params)}" if params else url
    request = Request(
        full_url,
        headers={
            "User-Agent": USER_AGENT,
            "Referer": "https://www.bilibili.com",
        },
    )
    with urlopen(request, timeout=timeout_s) as response:
        payload = response.read().decode("utf-8", errors="replace")
    data = json.loads(payload)
    if data.get("code") != 0:
        raise RuntimeError(f"Bilibili API failed: code={data.get('code')} message={data.get('message')}")
    return data


def _parse_video(payload: dict[str, Any], bvid: str) -> dict[str, Any]:
    data = payload.get("data") or {}
    stat = data.get("stat") or {}
    owner = data.get("owner") or {}
    return {
        "bvid": data.get("bvid") or bvid,
        "aid": data.get("aid"),
        "title": data.get("title") or "",
        "description": data.get("desc") or "",
        "author": owner.get("name") or "",
        "created_at": _timestamp_to_iso(data.get("pubdate")),
        "duration_ms": (data.get("duration") or 0) * 1000,
        "play_count": stat.get("view"),
        "like_count": stat.get("like"),
        "coin_count": stat.get("coin"),
        "collect_count": stat.get("favorite"),
        "share_count": stat.get("share"),
        "comment_count": stat.get("reply"),
        "danmaku_count": stat.get("danmaku"),
    }


def _fetch_comments(
    aid: int,
    *,
    max_comments: int,
    timeout_s: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    comments: list[dict[str, Any]] = []
    raw_records: list[dict[str, Any]] = []
    seen: set[str] = set()
    page = 1
    while len(comments) < max_comments and page <= 10:
        payload = _get_json(
            REPLY_API,
            {"type": 1, "oid": aid, "sort": 2, "pn": page, "ps": 20},
            timeout_s=timeout_s,
        )
        raw_records.append({"url": REPLY_API, "page": page, "data": payload})
        replies = (payload.get("data") or {}).get("replies") or []
        if not replies:
            break
        for item in replies:
            comment = _normalize_comment(item)
            key = comment["id"] or f"{comment['user_name']}:{comment['text']}"
            if key in seen:
                continue
            seen.add(key)
            comments.append(comment)
            if len(comments) >= max_comments:
                break
        page += 1
        time.sleep(0.25)
    comments.sort(key=lambda item: item.get("like_count") or 0, reverse=True)
    return comments[:max_comments], raw_records


def _normalize_comment(value: dict[str, Any]) -> dict[str, Any]:
    member = value.get("member") or {}
    content = value.get("content") or {}
    location = (value.get("reply_control") or {}).get("location") or ""
    return {
        "id": str(value.get("rpid") or ""),
        "text": content.get("message") or "",
        "like_count": value.get("like") or 0,
        "reply_count": value.get("rcount") or 0,
        "created_at": _timestamp_to_iso(value.get("ctime")),
        "user_name": member.get("uname") or "",
        "ip_label": location.replace("IP属地：", "").replace("IP属地:", "").strip(),
    }


def _timestamp_to_iso(value: Any) -> str | None:
    try:
        timestamp = int(value)
    except (TypeError, ValueError):
        return None
    if timestamp <= 0:
        return None
    return datetime.fromtimestamp(timestamp, UTC).isoformat()


def _sanitize_url(url: str) -> str:
    parsed = urlsplit(url)
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "", ""))
