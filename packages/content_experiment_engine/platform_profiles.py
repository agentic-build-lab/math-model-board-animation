from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


READINESS_LEVELS = {
    "official_api_ready",
    "authorized_only",
    "best_effort_public_observation",
    "research_or_experimental",
}


@dataclass(frozen=True, slots=True)
class PlatformDimension:
    code: str
    name: str
    weight: float
    description: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class PlatformProfile:
    key: str
    platform: str
    content_format: str
    readiness: str
    dimensions: tuple[PlatformDimension, ...]
    metric_aliases: dict[str, tuple[str, ...]]
    unavailable_metrics: tuple[str, ...]
    compliance_notes: tuple[str, ...]
    product_notes: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["normalized_weights"] = normalized_weights(self)
        return data


DEFAULT_PLATFORM_PROFILES: tuple[PlatformProfile, ...] = (
    PlatformProfile(
        key="youtube_long",
        platform="youtube",
        content_format="long_video",
        readiness="official_api_ready",
        dimensions=(
            PlatformDimension("wi", "watch_intent", 1.35, "Reason to keep watching beyond the opening."),
            PlatformDimension("si", "search_intent", 1.2, "Long-tail search value and clear topic demand."),
            PlatformDimension("hd", "hook_density", 1.15, "Strength of the title, opening claim, and first 30 seconds."),
            PlatformDimension("cev", "comment_engagement_value", 1.0, "Audience questions and discussion depth."),
            PlatformDimension("ef", "evidence_fit", 1.0, "Whether the topic can be supported by sources or examples."),
            PlatformDimension("cf", "creator_fit", 0.9, "Fit with the channel promise and viewer expectations."),
            PlatformDimension("lt", "long_tail_value", 1.25, "Whether the video can keep attracting views after the trend fades."),
        ),
        metric_aliases={
            "play_count": ("viewCount", "views"),
            "like_count": ("likeCount", "likes"),
            "comment_count": ("commentCount", "comments"),
            "published_at": ("publishedAt",),
        },
        unavailable_metrics=("average_view_duration", "impressions", "click_through_rate"),
        compliance_notes=("Use official YouTube Data API for product-facing workflows.",),
        product_notes=("Best first platform for a paid creator-growth product.",),
    ),
    PlatformProfile(
        key="youtube_shorts",
        platform="youtube",
        content_format="short_video",
        readiness="official_api_ready",
        dimensions=(
            PlatformDimension("hd", "hook_density", 1.5, "Immediate first-second attention strength."),
            PlatformDimension("lp", "loop_potential", 1.25, "Whether the ending encourages replay or repeat viewing."),
            PlatformDimension("sh", "shareability", 1.25, "Meme, surprise, utility, or identity-driven sharing."),
            PlatformDimension("wi", "watch_intent", 1.1, "Reason to finish the short clip."),
            PlatformDimension("pnf", "platform_native_fit", 1.1, "Fit with vertical rhythm and Shorts consumption."),
            PlatformDimension("ef", "evidence_fit", 0.7, "Whether claims can be checked without slowing the clip."),
        ),
        metric_aliases={
            "play_count": ("viewCount", "views"),
            "like_count": ("likeCount", "likes"),
            "comment_count": ("commentCount", "comments"),
        },
        unavailable_metrics=("swipe_away_rate", "retention_curve", "viewed_vs_swiped"),
        compliance_notes=("Use official YouTube Data API; creator analytics needs OAuth later.",),
        product_notes=("Separate scoring from long-form YouTube because retention mechanics differ.",),
    ),
    PlatformProfile(
        key="bilibili",
        platform="bilibili",
        content_format="video",
        readiness="official_api_ready",
        dimensions=(
            PlatformDimension("cd", "community_depth", 1.25, "Fit with Bilibili community language and expectations."),
            PlatformDimension("lt", "long_tail_value", 1.2, "Educational or archival value that supports later discovery."),
            PlatformDimension("si", "save_intent", 1.15, "Likelihood of favorites, coins, and later rewatching."),
            PlatformDimension("cev", "comment_engagement_value", 1.0, "Comment and danmaku discussion potential."),
            PlatformDimension("ef", "evidence_fit", 1.0, "Source quality and explainability."),
            PlatformDimension("hd", "hook_density", 0.9, "Title and opening pull."),
        ),
        metric_aliases={
            "play_count": ("view", "views"),
            "like_count": ("like", "likes"),
            "comment_count": ("reply", "comments"),
            "collect_count": ("favorite", "favorites"),
            "coin_count": ("coin", "coins"),
            "danmaku_count": ("danmaku",),
        },
        unavailable_metrics=("completion_rate", "traffic_source"),
        compliance_notes=("Keep public adapter best-effort and store raw response paths for debugging.",),
        product_notes=("Strong fit for educational and model-explainer content.",),
    ),
    PlatformProfile(
        key="douyin",
        platform="douyin",
        content_format="short_video",
        readiness="best_effort_public_observation",
        dimensions=(
            PlatformDimension("hd", "hook_density", 1.5, "First seconds must be immediately legible and surprising."),
            PlatformDimension("er", "emotional_resonance", 1.35, "Emotion, conflict, identity, or urgency."),
            PlatformDimension("sh", "shareability", 1.2, "Whether viewers would forward or comment quickly."),
            PlatformDimension("pnf", "platform_native_fit", 1.2, "Fit with fast vertical short-video pacing."),
            PlatformDimension("si", "save_intent", 0.95, "Utility or tutorial value worth saving."),
            PlatformDimension("ef", "evidence_fit", 0.7, "Evidence must be fast to show and understand."),
        ),
        metric_aliases={
            "play_count": ("play_count",),
            "like_count": ("digg_count", "like_count"),
            "comment_count": ("comment_count",),
            "share_count": ("share_count",),
            "collect_count": ("collect_count",),
        },
        unavailable_metrics=("completion_rate", "traffic_source", "follower_conversion"),
        compliance_notes=("Official Open Platform permissions are required for product-facing comment workflows.",),
        product_notes=("Use public-page capture for internal research only unless authorized APIs are added.",),
    ),
    PlatformProfile(
        key="tiktok",
        platform="tiktok",
        content_format="short_video",
        readiness="authorized_only",
        dimensions=(
            PlatformDimension("hd", "hook_density", 1.45, "Opening pattern and immediate curiosity."),
            PlatformDimension("sh", "shareability", 1.3, "Cross-audience share or remix potential."),
            PlatformDimension("pnf", "platform_native_fit", 1.25, "Fit with TikTok pacing, sound, and trend mechanics."),
            PlatformDimension("er", "emotional_resonance", 1.1, "Emotion or identity resonance."),
            PlatformDimension("lp", "loop_potential", 1.0, "Replay or loopability."),
            PlatformDimension("ci", "commercial_intent", 0.75, "Product or creator monetization relevance."),
        ),
        metric_aliases={
            "play_count": ("view_count", "views"),
            "like_count": ("like_count", "likes"),
            "comment_count": ("comment_count", "comments"),
            "share_count": ("share_count", "shares"),
        },
        unavailable_metrics=("retention_curve", "for_you_distribution"),
        compliance_notes=("Display API needs user authorization; Research API requires approved research access.",),
        product_notes=("Good migration target after YouTube because short-video mechanics are similar to Douyin.",),
    ),
    PlatformProfile(
        key="x",
        platform="x",
        content_format="post_or_thread",
        readiness="official_api_ready",
        dimensions=(
            PlatformDimension("nr", "narrative_relevance", 1.35, "Fit with active public conversation and event timing."),
            PlatformDimension("sh", "shareability", 1.25, "Quote, reply, repost, or controversy potential."),
            PlatformDimension("ef", "evidence_fit", 1.15, "Verifiable source trail and low rumor risk."),
            PlatformDimension("td", "timeliness_delta", 1.25, "How early the signal appears relative to mainstream attention."),
            PlatformDimension("el", "entity_linkability", 1.0, "Can the topic be mapped to people, companies, sectors, or events."),
            PlatformDimension("qr", "quant_research_value", 0.8, "Useful as a hypothesis seed, not a direct trading signal."),
        ),
        metric_aliases={
            "like_count": ("like_count",),
            "reply_count": ("reply_count",),
            "repost_count": ("retweet_count", "repost_count"),
            "quote_count": ("quote_count",),
            "impression_count": ("impression_count",),
            "bookmark_count": ("bookmark_count",),
        },
        unavailable_metrics=("private_clicks", "organic_metrics", "promoted_metrics"),
        compliance_notes=("API is pay-per-use; add explicit cost limits before bulk collection.",),
        product_notes=("Strong for topic heat and quant-event hypotheses, but requires validation.",),
    ),
    PlatformProfile(
        key="xiaohongshu",
        platform="xiaohongshu",
        content_format="note_or_ecommerce",
        readiness="best_effort_public_observation",
        dimensions=(
            PlatformDimension("si", "search_intent", 1.3, "Likelihood that users search this problem or product category."),
            PlatformDimension("sv", "save_intent", 1.35, "Collection intent for tutorials, lists, or purchase research."),
            PlatformDimension("ci", "commercial_intent", 1.2, "Product, category, store, or conversion relevance."),
            PlatformDimension("co", "cover_strength", 1.1, "Cover and title clarity for feed stopping power."),
            PlatformDimension("oq", "objection_questions", 1.0, "Comment objections and unresolved buying questions."),
            PlatformDimension("ef", "evidence_fit", 0.85, "Whether claims can be supported by screenshots, receipts, or sources."),
        ),
        metric_aliases={
            "like_count": ("liked_count", "likes"),
            "comment_count": ("comments_count", "comments"),
            "collect_count": ("collected_count", "collects", "saves"),
            "share_count": ("share_count", "shares"),
        },
        unavailable_metrics=("search_impressions", "conversion_rate", "store_sales"),
        compliance_notes=(
            "Separate best-effort public observation from authorized ecommerce or marketing data.",
            "Do not promise stable public scraping as a paid product core.",
        ),
        product_notes=("Best product angle is demand, search, and ecommerce intent analysis.",),
    ),
)


def list_platform_profiles() -> tuple[PlatformProfile, ...]:
    return DEFAULT_PLATFORM_PROFILES


def get_platform_profile(key: str) -> PlatformProfile:
    normalized_key = _normalize_key(key)
    for profile in DEFAULT_PLATFORM_PROFILES:
        if profile.key == normalized_key:
            return profile
    available = ", ".join(profile.key for profile in DEFAULT_PLATFORM_PROFILES)
    raise KeyError(f"Unknown platform profile: {key}. Available: {available}")


def normalized_weights(profile: PlatformProfile) -> dict[str, float]:
    total = sum(dimension.weight for dimension in profile.dimensions)
    if total <= 0:
        raise ValueError(f"Profile {profile.key} has no positive dimension weights.")
    return {
        dimension.code: round(dimension.weight / total, 6)
        for dimension in profile.dimensions
    }


def platform_weighted_score(
    profile_key: str,
    dimension_scores: dict[str, int],
) -> dict[str, Any]:
    profile = get_platform_profile(profile_key)
    normalized_scores = {
        key.lower(): _validate_score(value, key) for key, value in dimension_scores.items()
    }
    weighted_sum = 0.0
    weight_total = 0.0
    for dimension in profile.dimensions:
        score = normalized_scores.get(dimension.code)
        if score is None:
            continue
        weighted_sum += score * dimension.weight
        weight_total += dimension.weight
    composite = round((weighted_sum / weight_total) * 2.0, 2) if weight_total else None
    return {
        "profile_key": profile.key,
        "platform": profile.platform,
        "content_format": profile.content_format,
        "readiness": profile.readiness,
        "composite_score": composite,
        "dimension_scores": normalized_scores,
        "top_dimensions": _top_dimensions(profile, normalized_scores),
    }


def profiles_as_dict() -> list[dict[str, Any]]:
    return [profile.to_dict() for profile in DEFAULT_PLATFORM_PROFILES]


def _top_dimensions(
    profile: PlatformProfile,
    dimension_scores: dict[str, int],
) -> list[dict[str, Any]]:
    rows = []
    for dimension in profile.dimensions:
        score = dimension_scores.get(dimension.code)
        if score is None:
            continue
        rows.append({
            "code": dimension.code,
            "name": dimension.name,
            "score": score,
            "weight": dimension.weight,
            "weighted_score": round(score * dimension.weight, 4),
        })
    rows.sort(key=lambda item: item["weighted_score"], reverse=True)
    return rows[:3]


def _normalize_key(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def _validate_score(value: int, key: str) -> int:
    if not isinstance(value, int) or value < 0 or value > 5:
        raise ValueError(f"dimension score {key} must be an integer from 0 to 5")
    return value
