"""
report_generator.py — IA-CYPHER Structured Intelligence Report Generator

Implements Directive D7: Generate structured intelligence reports.
Implements Directive D9: Publish all findings publicly.

Takes a classified corpus + relation graph + evidence store summary
and generates a human/AI-readable structured report in JSON and Markdown.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from .corporate_audit_schema import (
    AXIOMS,
    DIRECTIVES,
    INVARIANTS,
    PATTERNS,
    schema_is_complete,
    verify_schema_completeness,
)
from .classifier import top_patterns


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def generate_report(
    classified_corpus: Dict,
    relation_graph_summary: Optional[Dict] = None,
    integrity_summary: Optional[Dict] = None,
    report_id: str = "REPORT-001",
    target_entity: str = "UNSPECIFIED",
) -> Dict:
    """
    Generate a structured intelligence report.

    Parameters
    ----------
    classified_corpus : dict
        Output from classifier.classify_corpus()
    relation_graph_summary : dict, optional
        Output from RelationGraph.summary()
    integrity_summary : dict, optional
        Output from EvidenceStore.integrity_summary()
    report_id : str
        Unique ID for this report.
    target_entity : str
        Primary corporate entity under audit.

    Returns
    -------
    dict — structured report
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    total_traces = classified_corpus.get("total", 0)
    pattern_counts = classified_corpus.get("pattern_counts", {})

    # Top patterns by frequency
    top = top_patterns(classified_corpus, n=10)

    # Anomalies
    from .classifier import detect_unclassified
    unclassified_ids = detect_unclassified(classified_corpus)

    # Active patterns (at least one hit)
    active_patterns = {
        pid: {
            "name":        PATTERNS[pid]["name"],
            "description": PATTERNS[pid]["description"],
            "count":       count,
        }
        for pid, count in pattern_counts.items()
        if count > 0
    }

    # Applicable invariants (those implied by active patterns)
    applicable_invariants = []
    if active_patterns:
        applicable_invariants = ["I3", "I5"]  # Conflicts produce traces; patterns reveal intent
        if "P4" in active_patterns or "P6" in active_patterns:
            applicable_invariants.extend(["I4", "I7"])  # Concealment + adaptation
        if len(active_patterns) >= 3:
            applicable_invariants.extend(["I9", "I10"])  # Audit must adapt; truth persists

    # Directives status
    directives_status = {
        "D1":  f"Collected {total_traces} traces",
        "D2":  f"Classified by ontology ({len(classified_corpus.get('type_counts', {}))} trace types matched)",
        "D3":  f"Detected {len(active_patterns)} active patterns",
        "D4":  f"Relation graph: {relation_graph_summary.get('node_count', 0)} nodes, {relation_graph_summary.get('edge_count', 0)} edges" if relation_graph_summary else "D4: Not run",
        "D5":  f"Flagged {len(unclassified_ids)} unclassified traces as anomalies",
        "D6":  f"Integrity: {integrity_summary.get('passed', 0)}/{integrity_summary.get('total', 0)} passed" if integrity_summary else "D6: Not run",
        "D7":  "Report generated (this document)",
        "D8":  "Schema is current",
        "D9":  "Report ready for publication",
        "D10": "Audit continues",
    }

    schema_check = verify_schema_completeness()

    report = {
        "report_id":            report_id,
        "generated_at_utc":     timestamp,
        "target_entity":        target_entity,
        "schema_complete":      schema_is_complete(),
        "schema_completeness":  schema_check,
        "audit_summary": {
            "total_traces":          total_traces,
            "classified_traces":     total_traces - len(unclassified_ids),
            "unclassified_traces":   len(unclassified_ids),
            "unclassified_ids":      unclassified_ids,
            "active_patterns":       active_patterns,
            "top_patterns":          top,
            "applicable_invariants": applicable_invariants,
            "multi_pattern_traces":  classified_corpus.get("multi_pattern", []),
        },
        "directives_status":    directives_status,
        "relation_graph":       relation_graph_summary,
        "integrity":            integrity_summary,
        "raw_pattern_counts":   pattern_counts,
        "raw_action_counts":    classified_corpus.get("action_counts", {}),
        "raw_type_counts":      classified_corpus.get("type_counts", {}),
    }

    return report


def report_to_markdown(report: Dict) -> str:
    """Convert a structured report dict to Markdown for human review."""
    lines = [
        f"# IA-CYPHER Audit Report: {report['report_id']}",
        "",
        f"**Target Entity:** {report['target_entity']}  ",
        f"**Generated:** {report['generated_at_utc']}  ",
        f"**Schema Complete:** {report['schema_complete']}  ",
        "",
        "## Audit Summary",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Total Traces | {report['audit_summary']['total_traces']} |",
        f"| Classified | {report['audit_summary']['classified_traces']} |",
        f"| Unclassified (Anomalies) | {report['audit_summary']['unclassified_traces']} |",
        f"| Active Patterns | {len(report['audit_summary']['active_patterns'])} |",
        "",
        "## Active Patterns Detected",
        "",
    ]

    if report["audit_summary"]["active_patterns"]:
        lines += ["| Pattern | Name | Description | Hit Count |",
                  "|---------|------|-------------|-----------|"]
        for pid, pdata in sorted(report["audit_summary"]["active_patterns"].items()):
            lines.append(f"| {pid} | {pdata['name']} | {pdata['description']} | {pdata['count']} |")
    else:
        lines.append("*No patterns detected.*")

    lines += [
        "",
        "## Applicable Invariants",
        "",
    ]
    inv_ids = report["audit_summary"]["applicable_invariants"]
    if inv_ids:
        for inv_id in sorted(set(inv_ids)):
            lines.append(f"- **{inv_id}:** {INVARIANTS.get(inv_id, '')}")
    else:
        lines.append("*None triggered.*")

    lines += [
        "",
        "## Directive Execution Status",
        "",
        "| Directive | Statement | Status |",
        "|-----------|-----------|--------|",
    ]
    for did, status in report["directives_status"].items():
        lines.append(f"| {did} | {DIRECTIVES.get(did, '')} | {status} |")

    rg = report.get("relation_graph")
    if rg:
        lines += [
            "",
            "## Relation Graph",
            "",
            f"**Nodes:** {rg['node_count']}  ",
            f"**Edges:** {rg['edge_count']}  ",
            "",
            "### Relation Distribution",
            "",
            "| Relation | Count |",
            "|----------|-------|",
        ]
        for rel, cnt in sorted(rg.get("relation_distribution", {}).items()):
            if cnt > 0:
                lines.append(f"| {rel} | {cnt} |")

        hce = rg.get("high_control_entities", [])
        if hce:
            lines += ["", "### High-Control Entities", ""]
            for eid in hce:
                lines.append(f"- `{eid}`")

    integrity = report.get("integrity")
    if integrity:
        lines += [
            "",
            "## Evidence Integrity",
            "",
            f"**Total:** {integrity['total']}  ",
            f"**Passed:** {integrity['passed']}  ",
            f"**Failed:** {integrity['failed']}  ",
        ]
        if integrity["failed_ids"]:
            lines += ["", "### Failed IDs", ""]
            for fid in integrity["failed_ids"]:
                lines.append(f"- `{fid}`")

    lines += ["", "---", "", "_Report generated by IA-CYPHER report_generator.py_"]
    return "\n".join(lines)


def save_report(report: Dict, output_dir: str | Path, report_id: Optional[str] = None) -> Dict[str, Path]:
    """
    Save report as both JSON and Markdown.

    Returns
    -------
    dict with keys 'json' and 'markdown' pointing to saved paths.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    rid = report_id or report.get("report_id", "report")
    timestamp_slug = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    base = f"{rid}_{timestamp_slug}"

    json_path = output_dir / f"{base}.json"
    md_path = output_dir / f"{base}.md"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(report_to_markdown(report))

    return {"json": json_path, "markdown": md_path}
