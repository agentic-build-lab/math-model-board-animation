from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .candidates import Candidate


@dataclass(slots=True)
class VideoBrief:
    candidate_id: str
    title: str
    source_url: str | None
    target_workflow: str
    hook: str
    video_angle: str
    evidence_needed: list[str]
    suggested_assets: list[str]
    audience_questions: list[str]
    risk_notes: list[str]
    workflow_inputs: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def generate_video_brief(
    candidate: Candidate,
    *,
    target_workflow: str = "evidence_driven_ai_video",
    comments: list[dict[str, Any]] | None = None,
) -> VideoBrief:
    """Convert a topic candidate into a workflow-neutral video brief."""
    audience_questions = _questions_from_comments(comments or [])
    evidence_needed = _evidence_needed(candidate, target_workflow)
    suggested_assets = _assets_for_workflow(target_workflow)
    risk_notes = list(candidate.risk_flags)
    if candidate.source.startswith("trend:"):
        risk_notes.append("trend_source_needs_freshness_check")
    if target_workflow == "quant_signal_research":
        risk_notes.append("not_a_trading_signal_without_market_data_validation")

    return VideoBrief(
        candidate_id=candidate.id,
        title=candidate.title,
        source_url=candidate.url,
        target_workflow=target_workflow,
        hook=_hook(candidate, audience_questions),
        video_angle=_angle(candidate, target_workflow),
        evidence_needed=evidence_needed,
        suggested_assets=suggested_assets,
        audience_questions=audience_questions,
        risk_notes=risk_notes,
        workflow_inputs=_workflow_inputs(candidate, target_workflow),
    )


def _hook(candidate: Candidate, audience_questions: list[str]) -> str:
    if audience_questions:
        return f"Start from the audience question: {audience_questions[0]}"
    if candidate.composite_score and candidate.composite_score >= 8:
        return f"Why this is suddenly becoming important: {candidate.title}"
    return f"What is really behind: {candidate.title}"


def _angle(candidate: Candidate, target_workflow: str) -> str:
    if target_workflow == "math_model_board_animation":
        return "Turn the topic into a visible model: define variables, show the mechanism, then animate the key relationship."
    if target_workflow == "quant_signal_research":
        return "Treat the topic as a hypothesis for sector attention, then validate it against price, volume, and event timing."
    if target_workflow == "ai_editing_workflow":
        return "Use public clips, screenshots, captions, and generated images to build a fast evidence-led explainer."
    return "Build a claim-first explainer: public evidence first, interpretation second, review gate before publish."


def _evidence_needed(candidate: Candidate, target_workflow: str) -> list[str]:
    items = ["original_source_snapshot", "publish_time", "public_engagement_metrics"]
    if target_workflow == "evidence_driven_ai_video":
        items.extend(["official_webpage_or_pdf", "source_manifest", "privacy_review"])
    if target_workflow == "math_model_board_animation":
        items.extend(["model_definition", "formula_or_variable_list", "visual_analogy"])
    if target_workflow == "quant_signal_research":
        items.extend(["related_stocks_or_sectors", "event_timestamp", "market_reaction_window"])
    return items


def _assets_for_workflow(target_workflow: str) -> list[str]:
    if target_workflow == "math_model_board_animation":
        return ["formula_scene_config", "chart_scene", "contact_sheet"]
    if target_workflow == "ai_editing_workflow":
        return ["public_clip_reference", "caption_events", "b_roll_or_generated_images"]
    if target_workflow == "quant_signal_research":
        return ["event_timeline", "sector_watchlist", "price_volume_panel"]
    return ["source_screenshot", "highlight_boxes", "sync_timeline", "render_manifest"]


def _questions_from_comments(comments: list[dict[str, Any]]) -> list[str]:
    questions: list[str] = []
    for comment in comments:
        text = (comment.get("text") or "").strip()
        if not text:
            continue
        if "?" in text or "？" in text or any(token in text for token in ("怎么", "为什么", "如何", "哪里", "是什么")):
            questions.append(text[:160])
        if len(questions) >= 5:
            break
    return questions


def _workflow_inputs(candidate: Candidate, target_workflow: str) -> dict[str, Any]:
    common = {
        "topic": candidate.title,
        "candidate_id": candidate.id,
        "source": candidate.source,
        "source_url": candidate.url,
        "composite_score": candidate.composite_score,
    }
    if target_workflow == "math_model_board_animation":
        common["scene_style"] = "modern_tech"
        common["animation_goal"] = "make the mechanism feel advanced and visible"
    if target_workflow == "evidence_driven_ai_video":
        common["review_gate_required"] = True
        common["evidence_first"] = True
    return common
