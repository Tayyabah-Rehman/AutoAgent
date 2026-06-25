"""
AutoAgent Export — CSV, JSON, TXT export of query history
"""
import csv
import json
import io
from typing import List, Dict
from datetime import datetime


def export_to_csv(history: List[Dict]) -> bytes:
    """Export query history to CSV bytes."""
    output = io.StringIO()
    fieldnames = ["id", "query", "answer", "tool_count", "duration", "created_at"]
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for row in history:
        writer.writerow({k: row.get(k, "") for k in fieldnames})
    return output.getvalue().encode("utf-8")


def export_to_json(history: List[Dict]) -> bytes:
    """Export query history to JSON bytes."""
    clean = []
    for row in history:
        clean.append({
            "id": row.get("id"),
            "query": row.get("query"),
            "answer": row.get("answer"),
            "tool_count": row.get("tool_count", 0),
            "duration_seconds": row.get("duration", 0),
            "timestamp": row.get("created_at"),
        })
    return json.dumps(clean, indent=2, ensure_ascii=False).encode("utf-8")


def export_to_txt(history: List[Dict]) -> bytes:
    """Export query history to readable plain text."""
    lines = []
    lines.append("=" * 60)
    lines.append("AutoAgent — Query History Export")
    lines.append(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 60)

    for i, row in enumerate(history, 1):
        lines.append(f"\n[{i}] {row.get('created_at', '')}")
        lines.append(f"Q: {row.get('query', '')}")
        lines.append(f"A: {row.get('answer', '')}")
        lines.append(f"   Tools used: {row.get('tool_count', 0)} | Duration: {row.get('duration', 0)}s")
        lines.append("-" * 40)

    return "\n".join(lines).encode("utf-8")


def get_export_filename(fmt: str, username: str = "user") -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"autoagent_{username}_{ts}.{fmt}"
