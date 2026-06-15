#!/usr/bin/env python3
"""Bug triage decision logger.

Writes structured triage decisions to ~/.claude/data/bug_triage_log.jsonl.
One JSON object per line, append-only.

Usage:
    python3 triage_logger.py --bead-id BUG-001 --action auto-fix --confidence 0.92 --complexity trivial --project kicad-agent
    python3 triage_logger.py --bead-id BUG-002 --action escalate --confidence 0.35 --reason "multi-module crash, no pattern"
"""

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

LOG_PATH = Path.home() / ".claude" / "data" / "bug_triage_log.jsonl"


def log_decision(
    bead_id: str,
    action: str,
    confidence: float,
    complexity: str | None = None,
    project: str | None = None,
    reason: str | None = None,
    files_affected: list[str] | None = None,
    gsd_phase: str | None = None,
) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "bead_id": bead_id,
        "action": action,
        "confidence": confidence,
        "complexity": complexity,
        "project": project,
        "reason": reason,
        "files_affected": files_affected,
        "gsd_phase": gsd_phase,
    }

    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry, default=str) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Log a bug triage decision")
    parser.add_argument("--bead-id", required=True, help="Bead ID")
    parser.add_argument("--action", required=True, choices=["auto-fix", "attempt", "escalate", "defer-to-phase"], help="Action taken")
    parser.add_argument("--confidence", required=True, type=float, help="Confidence score 0-1")
    parser.add_argument("--complexity", default=None, help="trivial, medium, or complex")
    parser.add_argument("--project", default=None, help="Project name")
    parser.add_argument("--reason", default=None, help="Reason for escalation or deferral")
    parser.add_argument("--files", nargs="*", default=None, help="Files affected by the fix")
    parser.add_argument("--gsd-phase", default=None, help="GSD phase this was deferred to")

    args = parser.parse_args()
    log_decision(
        bead_id=args.bead_id,
        action=args.action,
        confidence=args.confidence,
        complexity=args.complexity,
        project=args.project,
        reason=args.reason,
        files_affected=args.files,
        gsd_phase=args.gsd_phase,
    )
    print(f"Logged: {args.bead_id} → {args.action} (confidence={args.confidence})")


if __name__ == "__main__":
    main()
