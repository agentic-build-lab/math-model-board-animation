from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from .content_state import DEFAULT_STATE_FILE_NAME, create_initial_state, write_state


def render_audience_template(
    *,
    project_name: str = "content experiment",
    created_at: str | None = None,
) -> str:
    stamp = _date(created_at)
    return "\n".join(
        [
            "# Audience Profile",
            "",
            f"**Project**: {project_name}",
            "**Persona Version**: v0",
            f"**Last Rebuilt**: {stamp}",
            "**Data Basis**: 0 retros / 0 comments",
            "**Confidence**: no data",
            "",
            "> This file is derived from retrospective comments and therefore may contain performance signals.",
            "> Do not use it for blind scoring or immutable predictions.",
            "",
            "## Core Persona",
            "",
            "Pending data. Rebuild after retros contain enough real comments.",
            "",
            "## Verified Traits",
            "",
            "| Trait | Evidence | Strength |",
            "|---|---|---|",
            "| pending | pending | pending |",
            "",
            "## Hypotheses To Validate",
            "",
            "- Add user-asserted or benchmark-seeded traits here until comments verify them.",
            "",
            "## Anti-Persona",
            "",
            "- Add audiences that data shows are not actually engaging.",
            "",
            "## Audience Language",
            "",
            "- Add phrases, memes, objections, and repeated wording from comments.",
            "",
            "## Topic Appetite",
            "",
            "| Topic Type | Reaction | Evidence |",
            "|---|---|---|",
            "| pending | pending | pending |",
            "",
            "## Persona X Rubric Cross-Check",
            "",
            "- Record conflicts between what comments seem to want and what calibrated outcomes support.",
            "",
            "## Version History",
            "",
            f"- v0 - created on {stamp}.",
            "",
        ]
    )


def render_benchmark_template(
    *,
    benchmark_name: str = "[benchmark-name]",
    platform: str = "[platform]",
    created_at: str | None = None,
) -> str:
    stamp = _date(created_at)
    return "\n".join(
        [
            f"# Benchmark Account: {benchmark_name}",
            "",
            "> Use this as a cold-start reference frame, not as ground truth.",
            "> Imported patterns are untested on the current channel until retros validate them.",
            "",
            "## Account",
            "",
            f"- **Name**: {benchmark_name}",
            f"- **Platform**: {platform}",
            "- **URL**: ",
            "- **Follower Scale**: ",
            "- **Style**: ",
            f"- **Imported At**: {stamp}",
            "- **Sample Count**: 0",
            "",
            "## Imported Samples",
            "",
            "| # | Title | Plays | Likes | Comments | Shares | Impression | Transcript |",
            "|---|---|---:|---:|---:|---:|---|---|",
            "| 1 | pending |  |  |  |  | high / medium / low | samples/.../transcript.md |",
            "",
            "## Qualitative Rubric Signals",
            "",
            "- Important dimensions: pending.",
            "- Weak or non-significant dimensions: pending.",
            "- Initial suggestion: pending. Do not convert this into numeric weights without calibration.",
            "",
            "## Script Patterns Imported From Benchmark",
            "",
            "- Pending. Mark every imported pattern as `imported_untested` until the local channel validates it.",
            "",
            "## Topic Direction",
            "",
            "- Pending.",
            "",
            "## Maintenance History",
            "",
            f"- {stamp} - template created.",
            "",
        ]
    )


def render_script_patterns_template(
    *,
    project_name: str = "content experiment",
    created_at: str | None = None,
) -> str:
    stamp = _date(created_at)
    return "\n".join(
        [
            "# Script Pattern Library",
            "",
            f"**Project**: {project_name}",
            f"**Created At**: {stamp}",
            "",
            "> This file teaches drafting structure. It is not a scoring rubric.",
            "> Because it can contain benchmark or retrospective signals, do not use it for blind scoring.",
            "",
            "## Structure Selection",
            "",
            "| Content Attribute | Candidate Structure | Local Evidence |",
            "|---|---|---|",
            "| strong metaphor | metaphor-first explanation | pending |",
            "| strong time sequence | timeline arc | pending |",
            "| strong data contrast | data reversal opening | pending |",
            "| multiple cases | case-driven narrative | pending |",
            "| parallel concepts | three-part compression | pending |",
            "| strong scene | second-person scene into reversal | pending |",
            "",
            "## Hook Patterns",
            "",
            "- Scene + reversal: pending.",
            "- Direct data contrast: pending.",
            "- Identity challenge: pending.",
            "",
            "## Body Patterns",
            "",
            "- Prefer the smallest number of named parts that preserves the argument.",
            "- Mark every unvalidated structure as `pending_validation`.",
            "",
            "## Language Library",
            "",
            "| Category | Usage | Local Vocabulary |",
            "|---|---|---|",
            "| plain translation | converts abstract concepts into daily language | pending |",
            "| reversal marker | signals the turn | pending |",
            "| emotional marker | tells viewers where to feel the point | pending |",
            "| rhythm words | controls spoken pacing | pending |",
            "",
            "## User Edit Observations",
            "",
            "| Sample | Removed | Added | Outcome Signal |",
            "|---|---|---|---|",
            "| pending | pending | pending | pending |",
            "",
            "## Benchmark Imports",
            "",
            "- Pending. Keep these below local validated patterns.",
            "",
            "## Maintenance Rules",
            "",
            "- Keep the file short enough to read before drafting.",
            "- Remove patterns that are disproven or absorbed into a stronger rule.",
            "- Keep evidence and actual performance out of blind scoring prompts.",
            "",
        ]
    )


def initialize_learning_artifacts(
    root: Path,
    *,
    project_name: str = "content_experiment",
    benchmark_name: str = "[benchmark-name]",
    platform: str = "[platform]",
    overwrite: bool = False,
) -> list[Path]:
    root.mkdir(parents=True, exist_ok=True)
    created_at = datetime.now(UTC).isoformat()
    targets = {
        "audience.md": render_audience_template(project_name=project_name, created_at=created_at),
        "benchmark.md": render_benchmark_template(
            benchmark_name=benchmark_name,
            platform=platform,
            created_at=created_at,
        ),
        "script_patterns.md": render_script_patterns_template(
            project_name=project_name,
            created_at=created_at,
        ),
    }
    written: list[Path] = []
    for filename, content in targets.items():
        path = root / filename
        if path.exists() and not overwrite:
            continue
        path.write_text(content, encoding="utf-8")
        written.append(path)

    state_path = root / DEFAULT_STATE_FILE_NAME
    if overwrite or not state_path.exists():
        write_state(
            state_path,
            create_initial_state(
                project_name=project_name,
                content_form="mixed",
                initialized_at=created_at,
            ),
        )
        written.append(state_path)
    return written


def _date(value: str | None) -> str:
    if not value:
        return datetime.now(UTC).date().isoformat()
    return value.split("T", 1)[0]
