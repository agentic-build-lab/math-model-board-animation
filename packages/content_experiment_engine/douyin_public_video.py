from __future__ import annotations

import asyncio
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit
from urllib.error import URLError
from urllib.request import Request, urlopen


AWEME_ID_RE = re.compile(r"(?:video/)?(\d{15,25})")
COMMENT_ENDPOINT_MARKER = "/aweme/v1/web/comment/list/"
DETAIL_ENDPOINT_MARKERS = (
    "/aweme/v1/web/aweme/detail/",
    "/aweme/v1/web/aweme/post/",
    "aweme/detail",
    "aweme/iteminfo",
)


def extract_aweme_id(value: str) -> str | None:
    """Extract a Douyin aweme id from a direct URL or raw id."""
    match = AWEME_ID_RE.search(value.strip())
    return match.group(1) if match else None


def resolve_douyin_url(value: str, timeout_s: int = 10) -> str:
    """Resolve a Douyin short URL when possible, otherwise return the input."""
    if "v.douyin.com" not in value:
        return value
    request = Request(
        value,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/126.0 Safari/537.36"
            )
        },
        method="GET",
    )
    try:
        with urlopen(request, timeout=timeout_s) as response:
            return response.geturl()
    except (URLError, TimeoutError, ValueError):
        return value


async def fetch_public_video_snapshot(
    url_or_id: str,
    output_dir: Path,
    *,
    max_scrolls: int = 8,
    headless: bool = True,
) -> dict[str, Any]:
    """Capture public Douyin video metadata and comments from the front page.

    This adapter intentionally avoids creator-center login state. It is useful
    for public video research, competitor review, and topic mining. Metrics that
    are only available in creator dashboards remain unavailable here.
    """

    try:
        from playwright.async_api import Response, async_playwright
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "playwright is required. Install it with `pip install playwright` "
            "and run `python -m playwright install chromium`."
        ) from exc

    output_dir.mkdir(parents=True, exist_ok=True)
    fetched_at = datetime.now(UTC).isoformat()
    resolved_url = resolve_douyin_url(url_or_id)
    aweme_id = extract_aweme_id(resolved_url) or extract_aweme_id(url_or_id)
    video_url = (
        f"https://www.douyin.com/video/{aweme_id}"
        if aweme_id and not resolved_url.startswith("http")
        else resolved_url
    )

    raw_response_path = output_dir / "raw_responses.jsonl"
    screenshot_path = output_dir / "public_video_page.png"
    captured_urls: list[str] = []
    raw_records: list[dict[str, Any]] = []
    comments: list[dict[str, Any]] = []
    detail_payloads: list[dict[str, Any]] = []
    page_error: str | None = None

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            headless=headless,
            args=["--disable-blink-features=AutomationControlled"],
        )
        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/126.0 Safari/537.36"
            ),
        )
        page = await context.new_page()

        async def on_response(response: Response) -> None:
            url = response.url
            if COMMENT_ENDPOINT_MARKER not in url and not any(
                marker in url for marker in DETAIL_ENDPOINT_MARKERS
            ):
                return
            safe_url = _sanitize_url(url)
            captured_urls.append(safe_url)
            try:
                data = await response.json()
            except Exception:
                return
            raw_records.append({"url": safe_url, "data": data})
            if COMMENT_ENDPOINT_MARKER in url:
                for item in data.get("comments") or []:
                    comments.append(_normalize_comment(item))
            else:
                detail_payloads.append(data)

        page.on("response", on_response)
        try:
            await page.goto(video_url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(5)
            await _open_comment_panel(page)
            await _scroll_comments(page, max_scrolls)
            await page.screenshot(path=str(screenshot_path), full_page=False)
        except Exception as exc:
            page_error = str(exc)
            try:
                await page.screenshot(path=str(screenshot_path), full_page=False)
            except Exception:
                pass
        finally:
            title = await _safe_title(page)
            meta_description = await _safe_meta_content(page, "description")
            og_title = await _safe_meta_property(page, "og:title")
            await context.close()
            await browser.close()

    deduped_comments = _dedupe_comments(comments)
    raw_response_path.write_text(
        "\n".join(json.dumps(record, ensure_ascii=False) for record in raw_records),
        encoding="utf-8",
    )

    detail = _extract_detail(detail_payloads)
    snapshot = {
        "schema_version": "1.0",
        "source": {
            "platform": "douyin",
            "adapter": "douyin_public_video",
            "url": video_url,
            "resolved_url": resolved_url,
            "platform_video_id": aweme_id,
            "aweme_id": aweme_id,
            "fetched_at": fetched_at,
        },
        "video": {
            "title": detail.get("title") or og_title or title,
            "description": detail.get("description") or meta_description,
            "author": detail.get("author"),
            "created_at": detail.get("created_at"),
            "duration_ms": detail.get("duration_ms"),
        },
        "metrics": {
            "play_count": detail.get("play_count"),
            "like_count": detail.get("like_count"),
            "comment_count": detail.get("comment_count"),
            "share_count": detail.get("share_count"),
            "collect_count": detail.get("collect_count"),
        },
        "comments": deduped_comments,
        "evidence": {
            "screenshot_path": str(screenshot_path),
            "raw_response_path": str(raw_response_path),
            "captured_api_urls": captured_urls,
        },
        "limitations": _limitations(page_error, detail, deduped_comments),
    }
    (output_dir / "snapshot.json").write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return snapshot


async def _open_comment_panel(page: Any) -> None:
    selectors = [
        '[data-e2e="video-comment-more"]',
        '[data-e2e="feed-comment-icon"]',
        '[aria-label*="评论"]',
        "text=评论",
    ]
    for selector in selectors:
        try:
            await page.locator(selector).first.click(force=True, timeout=2500)
            await asyncio.sleep(2)
            return
        except Exception:
            continue


async def _scroll_comments(page: Any, max_scrolls: int) -> None:
    stagnant_rounds = 0
    last_count = 0
    for _ in range(max_scrolls):
        count = await page.evaluate(
            """() => {
                const items = document.querySelectorAll(
                    '[data-e2e="comment-item"], [data-e2e^="comment-item"], .comment-item'
                );
                if (items.length > 0) {
                    items[items.length - 1].scrollIntoView({block: 'end', behavior: 'instant'});
                } else {
                    const scrollables = Array.from(document.querySelectorAll('div'))
                      .filter((el) => el.scrollHeight > el.clientHeight + 200);
                    const target = scrollables.sort((a, b) => b.scrollHeight - a.scrollHeight)[0];
                    if (target) {
                        target.scrollTop = target.scrollHeight;
                    } else {
                        window.scrollBy(0, 1800);
                    }
                }
                return items.length;
            }"""
        )
        await page.mouse.wheel(0, 1600)
        await asyncio.sleep(1.5)
        if count == last_count:
            stagnant_rounds += 1
            if stagnant_rounds >= 4:
                break
        else:
            stagnant_rounds = 0
            last_count = count


async def _safe_title(page: Any) -> str | None:
    try:
        value = await page.title()
        return value or None
    except Exception:
        return None


async def _safe_meta_content(page: Any, name: str) -> str | None:
    try:
        return await page.locator(f'meta[name="{name}"]').first.get_attribute("content")
    except Exception:
        return None


async def _safe_meta_property(page: Any, property_name: str) -> str | None:
    try:
        return await page.locator(f'meta[property="{property_name}"]').first.get_attribute("content")
    except Exception:
        return None


def _normalize_comment(comment: dict[str, Any]) -> dict[str, Any]:
    user = comment.get("user") or {}
    return {
        "id": str(comment.get("cid") or comment.get("id") or ""),
        "text": comment.get("text") or "",
        "like_count": comment.get("digg_count") or 0,
        "reply_count": comment.get("reply_comment_total") or 0,
        "created_at": _timestamp_to_iso(comment.get("create_time")),
        "user_name": user.get("nickname") or "",
        "ip_label": comment.get("ip_label") or "",
    }


def _dedupe_comments(comments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for comment in comments:
        key = comment["id"] or f"{comment['user_name']}:{comment['text']}"
        if key in seen:
            continue
        seen.add(key)
        result.append(comment)
    result.sort(key=lambda item: item.get("like_count") or 0, reverse=True)
    return result


def _extract_detail(payloads: list[dict[str, Any]]) -> dict[str, Any]:
    for payload in payloads:
        aweme = _find_aweme_object(payload)
        if not aweme:
            continue
        stats = aweme.get("statistics") or aweme.get("stats") or {}
        author = aweme.get("author") or {}
        video = aweme.get("video") or {}
        return {
            "title": aweme.get("desc") or aweme.get("title"),
            "description": aweme.get("desc"),
            "author": author.get("nickname") or author.get("unique_id"),
            "created_at": _timestamp_to_iso(aweme.get("create_time")),
            "duration_ms": video.get("duration") or aweme.get("duration"),
            "play_count": stats.get("play_count"),
            "like_count": stats.get("digg_count"),
            "comment_count": stats.get("comment_count"),
            "share_count": stats.get("share_count"),
            "collect_count": stats.get("collect_count"),
        }
    return {}


def _find_aweme_object(value: Any) -> dict[str, Any] | None:
    if isinstance(value, dict):
        if value.get("aweme_id") or value.get("item_id"):
            return value
        for key in ("aweme_detail", "item", "aweme", "data"):
            found = _find_aweme_object(value.get(key))
            if found:
                return found
        for child in value.values():
            found = _find_aweme_object(child)
            if found:
                return found
    elif isinstance(value, list):
        for child in value:
            found = _find_aweme_object(child)
            if found:
                return found
    return None


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


def _limitations(
    page_error: str | None,
    detail: dict[str, Any],
    comments: list[dict[str, Any]],
) -> list[str]:
    items = [
        "public_front_page_only",
        "creator_dashboard_metrics_unavailable",
    ]
    if not detail:
        items.append("video_detail_api_not_captured")
    if not comments:
        items.append("comments_not_captured_or_hidden")
    if page_error:
        items.append(f"page_error: {page_error[:240]}")
    return items
