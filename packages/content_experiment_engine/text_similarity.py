from __future__ import annotations

import re
from difflib import SequenceMatcher
from typing import Any


MARKDOWN_HEADER_RE = re.compile(r"^#+\s+.*$", re.MULTILINE)
MARKDOWN_HR_RE = re.compile(r"^[-=*]{3,}\s*$", re.MULTILINE)
MARKDOWN_BLOCKQUOTE_RE = re.compile(r"^>+\s*", re.MULTILINE)
MARKDOWN_LIST_RE = re.compile(r"^[-*+]\s+|^\d+\.\s+", re.MULTILINE)
FORMATTING_PUNCT_RE = re.compile(r"[「」『』“”\"`*_~]")
ALL_WHITESPACE_RE = re.compile(r"\s+")


def normalize_for_similarity(text: str) -> str:
    """Strip markdown and spacing noise before transcript/script comparison."""

    value = MARKDOWN_HEADER_RE.sub("", text)
    value = MARKDOWN_HR_RE.sub("", value)
    value = MARKDOWN_BLOCKQUOTE_RE.sub("", value)
    value = MARKDOWN_LIST_RE.sub("", value)
    value = FORMATTING_PUNCT_RE.sub("", value)
    value = ALL_WHITESPACE_RE.sub("", value)
    return value


def text_diff_percent(original: str, revised: str) -> dict[str, Any]:
    """Return a 0-100 normalized text distance with backend diagnostics."""

    original_normalized = normalize_for_similarity(original)
    revised_normalized = normalize_for_similarity(revised)
    max_len = max(len(original_normalized), len(revised_normalized))
    if max_len == 0:
        return {
            "diff_percent": 0,
            "backend": "trivial",
            "original_normalized_length": 0,
            "revised_normalized_length": 0,
        }

    try:
        from rapidfuzz.distance import Levenshtein

        distance = Levenshtein.distance(original_normalized, revised_normalized)
        diff_percent = int((distance * 100) // max_len)
        backend = "rapidfuzz"
    except ImportError:
        matcher = SequenceMatcher(
            a=original_normalized,
            b=revised_normalized,
            autojunk=False,
        )
        diff_percent = int(round((1 - matcher.ratio()) * 100))
        backend = "difflib"

    return {
        "diff_percent": diff_percent,
        "backend": backend,
        "original_normalized_length": len(original_normalized),
        "revised_normalized_length": len(revised_normalized),
    }
