"""
classifier.py — IA-CYPHER Trace Classifier

Classifies raw trace text into:
  - Action type (FORMATION, FINANCING, CONTROL, etc.)
  - Trace type (LEGAL, FINANCIAL, DIGITAL, AI_OUTPUT, etc.)
  - Detected patterns (P1-P10)

Classification is keyword-based — no ML dependency, deterministic, testable.
Multiple categories/patterns can match a single trace (multi-label).

Keyword matching uses word-boundary regex for short/ambiguous tokens to avoid
false positives (e.g. "AI" inside "financial" or "PR" inside "approach").
"""

from __future__ import annotations

import hashlib
import re
from typing import Dict, List, Optional, Set

from .corporate_audit_schema import (
    ACTIONS,
    PATTERNS,
    TRACE_TYPES,
)

# Threshold: keywords shorter than this use word-boundary matching (\b).
# Longer keywords are matched as plain substrings (lower false-positive risk).
_WORD_BOUNDARY_MAX_LEN = 4


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _text_lower(text: str) -> str:
    return text.lower()


def _keyword_match(text_lower: str, keyword: str) -> bool:
    """
    Return True if `keyword` matches in `text_lower`.

    Short keywords (≤ _WORD_BOUNDARY_MAX_LEN chars, e.g. "AI", "PR") use
    word-boundary regex to avoid false positives ("ai" inside "financial").
    Longer keywords use plain substring matching.
    """
    kl = keyword.lower()
    if len(kl) <= _WORD_BOUNDARY_MAX_LEN:
        return bool(re.search(r"\b" + re.escape(kl) + r"\b", text_lower))
    return kl in text_lower


def _keyword_hits(text_lower: str, keywords: List[str]) -> List[str]:
    """Return which keywords from `keywords` appear in `text_lower`."""
    return [kw for kw in keywords if _keyword_match(text_lower, kw)]


# ---------------------------------------------------------------------------
# Classify a single trace text
# ---------------------------------------------------------------------------

def classify_trace(text: str) -> Dict:
    """
    Classify a raw trace text string.

    Parameters
    ----------
    text : str
        Raw text of the trace (news article snippet, filing text, etc.)

    Returns
    -------
    dict with keys:
        actions         : list of action ids that matched
        trace_types     : list of trace type ids that matched
        patterns        : list of pattern ids (P1-P10) that matched
        keyword_hits    : dict of section -> list of matched keywords
        sha256          : SHA-256 of the input text (for integrity tracking)
    """
    tl = _text_lower(text)
    sha = hashlib.sha256(text.encode("utf-8")).hexdigest()

    # Action classification
    matched_actions: List[str] = []
    action_hits: Dict[str, List[str]] = {}
    for action_id, action_def in ACTIONS.items():
        hits = _keyword_hits(tl, action_def["keywords"])
        if hits:
            matched_actions.append(action_id)
            action_hits[action_id] = hits

    # Trace type classification
    matched_types: List[str] = []
    type_hits: Dict[str, List[str]] = {}
    for type_id, type_def in TRACE_TYPES.items():
        hits = _keyword_hits(tl, type_def["keywords"])
        if hits:
            matched_types.append(type_id)
            type_hits[type_id] = hits

    # Pattern detection
    matched_patterns: List[str] = []
    pattern_hits: Dict[str, List[str]] = {}
    for pat_id, pat_def in PATTERNS.items():
        hits = _keyword_hits(tl, pat_def["keywords"])
        if hits:
            matched_patterns.append(pat_id)
            pattern_hits[pat_id] = hits

    return {
        "actions":      matched_actions,
        "trace_types":  matched_types,
        "patterns":     matched_patterns,
        "keyword_hits": {
            "actions":  action_hits,
            "types":    type_hits,
            "patterns": pattern_hits,
        },
        "sha256": sha,
    }


# ---------------------------------------------------------------------------
# Classify a batch of traces and aggregate pattern statistics
# ---------------------------------------------------------------------------

def classify_corpus(traces: List[Dict]) -> Dict:
    """
    Classify a list of trace dicts, each with at least a 'text' key.
    Optional keys: 'id', 'source', 'date', 'entity'.

    Parameters
    ----------
    traces : list of dict
        Each dict must have 'text'. Optional: 'id', 'source', 'entity'.

    Returns
    -------
    dict with:
        classified      : list of per-trace classification results (merged with input)
        pattern_counts  : dict P1..P10 -> int (how many traces matched each pattern)
        action_counts   : dict ACTION_ID -> int
        type_counts     : dict TYPE_ID -> int
        total           : int
        multi_pattern   : list of trace ids with 2+ patterns detected
    """
    classified = []
    pattern_counts: Dict[str, int] = {p: 0 for p in PATTERNS}
    action_counts: Dict[str, int] = {a: 0 for a in ACTIONS}
    type_counts: Dict[str, int] = {t: 0 for t in TRACE_TYPES}
    multi_pattern: List[str] = []

    for i, trace in enumerate(traces):
        text = trace.get("text", "")
        result = classify_trace(text)

        # Merge input trace metadata with classification
        merged = {**trace, **result}
        classified.append(merged)

        # Aggregate
        for pat in result["patterns"]:
            pattern_counts[pat] += 1
        for act in result["actions"]:
            action_counts[act] += 1
        for tt in result["trace_types"]:
            type_counts[tt] += 1

        trace_id = trace.get("id", f"trace_{i}")
        if len(result["patterns"]) >= 2:
            multi_pattern.append(trace_id)

    return {
        "classified":     classified,
        "pattern_counts": pattern_counts,
        "action_counts":  action_counts,
        "type_counts":    type_counts,
        "total":          len(traces),
        "multi_pattern":  multi_pattern,
    }


# ---------------------------------------------------------------------------
# Anomaly detection: traces with zero classification hits
# ---------------------------------------------------------------------------

def detect_unclassified(classified_corpus: Dict) -> List[str]:
    """
    Return trace ids that had no action, type, or pattern matches.
    These are anomalies — either novel patterns or bad input.
    """
    unclassified = []
    for item in classified_corpus["classified"]:
        if not item["actions"] and not item["trace_types"] and not item["patterns"]:
            unclassified.append(item.get("id", "unknown"))
    return unclassified


# ---------------------------------------------------------------------------
# Top patterns by frequency
# ---------------------------------------------------------------------------

def top_patterns(classified_corpus: Dict, n: int = 5) -> List[Dict]:
    """Return top-n patterns by hit count."""
    counts = classified_corpus["pattern_counts"]
    sorted_patterns = sorted(counts.items(), key=lambda x: -x[1])
    result = []
    for pat_id, count in sorted_patterns[:n]:
        if count > 0:
            from .corporate_audit_schema import PATTERNS as _PAT
            result.append({
                "pattern_id":   pat_id,
                "name":         _PAT[pat_id]["name"],
                "description":  _PAT[pat_id]["description"],
                "count":        count,
            })
    return result
