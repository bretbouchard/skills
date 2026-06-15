# Bug Report Schema v1 — Quick Reference

Full spec: `~/.claude/docs/BUG-REPORT-SPEC.md`

## Filing Bugs

Two paths for QA tools to file bugs — both produce identical output:

### CLI (standalone scripts)

```bash
file-bug --title "DRC export missing clearance" \
  --project kicad-agent --severity broken --area "DRC export" \
  --file lib/drc_exporter.py \
  --expected "Clearance values present" \
  --actual "Clearance values missing" \
  --repro-step "Open board with copper pour" \
  --repro-step "Run DRC export" \
  --evidence "lib/drc_exporter.py:142"
```

```bash
file-bug --type feature --title "Add batch export" \
  --project kicad-agent --area "export" \
  --description "Support batch DRC export for multiple boards" \
  --rationale "Users need to process boards in bulk"
```

### Python Library (agents, importable modules)

```python
from lib.file_bug import build_bug_description, build_feature_description, get_labels, get_priority

desc = build_bug_description(
    title="DRC export missing clearance",
    project="kicad-agent",
    severity="broken",
    area="DRC export",
    file="lib/drc_exporter.py",
    repro_steps=["Open board with copper pour", "Run DRC export"],
    expected="Clearance values present",
    actual="Clearance values missing",
    evidence=["lib/drc_exporter.py:142"],
)
labels = get_labels("bug", "broken", "kicad-agent")  # "bug,broken,kicad-agent"
priority = get_priority("broken")                     # "1"
```

### After Filing

```bash
/bug-triage --bead {id}   # immediate triage of just-filed bug
```

## Bead Labels Format

```
labels: "bug,{severity},{project}"
```

Severities: `crash`, `broken`, `degraded`, `cosmetic`

Priority auto-mapping: crash→0, broken→1, degraded→2, cosmetic→3

## Required Fields

| Field | Type | Purpose |
|-------|------|---------|
| `title` | string | What's broken |
| `project` | string | Catalog project ID |
| `severity` | enum | crash / broken / degraded / cosmetic |
| `area` | string | Subsystem |
| `repro_steps` | string[] | How to trigger |
| `expected` | string | What should happen |
| `actual` | string | What happens instead |
| `evidence` | string[] | File paths, logs, errors |
| `file` | string | Primary affected file (triage anchor) |

## Optional Fields

`regression` (bool), `related` (string[]), `environment` (string), `one_liner` (string)

## Triage Confidence Signals

| Signal | Impact |
|--------|--------|
| `file` field provided | +0.20 |
| Single file affected | +0.15 |
| Existing fix pattern | +0.20 |
| Clear expected vs actual | +0.10 |
| Well-tested module | +0.10 |
| Precise repro steps | +0.05 |
| Regression + git blame match | +0.10 |
| Regression + no blame match | -0.20 |
| No `file` field | -0.50 |
| Multi-module impact | -0.20 |
| Security-related area | -0.15 |

## Confidence Thresholds

| Range | Action |
|-------|--------|
| >= 0.85 | AUTO-FIX |
| 0.50-0.84 | ATTEMPT (1 retry) |
| < 0.50 | ESCALATE |

## Complexity Heuristics

| Signals | Complexity |
|---------|-----------|
| Single file + pattern + <50 line diff | trivial |
| 2-3 files + needs test + pattern | medium |
| Multi-module + no pattern + architectural | complex |
| Regression + no git blame match | complex |
