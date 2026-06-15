---
name: bug-triage
description: >
  Autonomous bug triage and auto-fix pipeline. Polls Beads for open bug reports filed
  by QA tools (analog, future verification agents), assesses fix confidence using
  structured triage signals, and either auto-fixes trivial bugs or escalates complex
  ones to the developer. Trigger this skill when: processing bug reports from QA
  tools, running scheduled bug triage, checking for open bugs to fix, or setting up
  autonomous bug resolution via /schedule. Works across all catalog projects
  (kicad-agent, white-room, ai-stack, analog, etc.).
---

# Bug Triage — Autonomous Bug Resolution Pipeline

## Overview

Hybrid triage system that processes bug reports filed as Beads. QA tools and verification agents file structured bug reports; the triage agent assesses confidence, auto-fixes trivial bugs, and escalates complex ones.

**Invocations:**
- `/bug-triage` — scan and triage all open bugs (interactive mode)
- `/bug-triage --bead {id}` — triage a single bug just filed (used by QA tools after filing)
- `/bug-triage --project {name}` — scan only a specific project
- `/bug-triage --scheduled` — scheduled/cron mode (minimal output, designed for automation)

## Resources

- `references/BUG-REPORT-SPEC.md` — Quick reference for the bug report schema, confidence signals, and thresholds. Load this before triaging.
- `scripts/triage_logger.py` — Append-only logger for triage decisions to `~/.claude/data/bug_triage_log.jsonl`. Run after every triage decision.

## Workflow

### Step 1: Parse Arguments

Parse `$ARGUMENTS` for flags:

| Flag | Effect |
|------|--------|
| (none) | Interactive mode — full output, confirm before fixing |
| `--bead {id}` | Triage a single bug by ID (skips polling, goes straight to Step 4) |
| `--project {name}` | Filter bugs to a single project |
| `--scheduled` | Autonomous mode — minimal output, no confirmation needed |

Set `$MODE` to `interactive` or `scheduled` based on flags.

If `--bead {id}` is provided, skip Step 3 (Poll Bugs) and proceed directly to Step 4 with only that bead. This is the automated path — QA tools invoke `/bug-triage --bead {id}` immediately after filing, so triage runs the moment a bug is reported.

### Step 2: Load Reference

Read `references/BUG-REPORT-SPEC.md` to load the schema, confidence signals, and thresholds into context before triaging any bugs.

### Step 3: Poll Bugs

Query Beads for open bug reports:

```
mcp__beads__beads_list(
  label="bug",
  status="open",
  limit=50
)
```

If `--project {name}` was specified, filter results to matching project by checking bead descriptions for `project: {name}`.

If no open bugs found, report "No open bugs to triage" and stop.

Sort bugs by priority (crash first, then broken, degraded, cosmetic).

### Step 4: Triage Each Bug

For each bug bead (in priority order):

#### 4a. Parse the Bug Report

Read the bead description and extract YAML frontmatter fields:
- `title`, `project`, `severity`, `area`, `file`
- `repro_steps`, `expected`, `actual`, `evidence`
- `regression`, `environment`, `one_liner` (if present)

If the description does not contain valid YAML frontmatter with required fields, log the bead as malformed and skip it.

#### 4b. Check for Active GSD Phase

Check if the bug's project has an active GSD phase that covers the affected area:

1. Navigate to the project directory (or check `.planning/STATE.md` if in current project)
2. Check `.planning/ROADMAP.md` for active phases covering the bug's `area`
3. If a matching phase exists:
   - Add the bug bead as a dependency on the phase bead: `mcp__beads__beads_dep_add(from=bug_id, to=phase_id)`
   - Log triage decision as `defer-to-phase`
   - Skip to next bug

#### 4c. Assess Confidence

Read the bug's primary file (`file` field) from the project codebase. Assess confidence using these signals:

**Positive signals (add to base 0.5):**
| Signal | + |
|--------|---|
| `file` field provided and file exists | +0.20 |
| Only 1 file needs modification | +0.15 |
| Similar fix pattern exists in codebase (git log, Confucius) | +0.20 |
| Expected vs actual are clear and specific | +0.10 |
| Affected module has tests | +0.10 |
| Repro steps are precise (specific inputs/commands) | +0.05 |
| Regression with clear git blame match | +0.10 |

**Negative signals (subtract):**
| Signal | - |
|--------|---|
| `file` is `unknown` or missing | -0.50 |
| Multiple files/modules affected | -0.20 |
| Security-related area (auth, crypto, input validation) | -0.15 |
| Regression without git blame match | -0.20 |

**Determine complexity:**
- `trivial` — single file, existing pattern, estimated <50 line diff
- `medium` — 2-3 files, needs new test, pattern exists
- `complex` — multi-module, no clear pattern, or architectural change

Clamp confidence to 0.0-1.0.

#### 4d. Route Based on Confidence

```
confidence >= 0.85 AND complexity == trivial  →  AUTO-FIX
confidence >= 0.50                            →  ATTEMPT (1 retry)
confidence < 0.50                             →  ESCALATE
```

#### 4e. Execute Action

**AUTO-FIX** (confidence >= 0.85, trivial):
1. In `scheduled` mode: proceed directly. In `interactive` mode: display the plan and fix.
2. Read the affected file
3. Apply the fix (single focused edit)
4. Run the deterministic verifier
5. If verifier passes: commit and close the bead
6. Log via `scripts/triage_logger.py`:
   ```bash
   python3 skills/bug-triage/scripts/triage_logger.py \
     --bead-id {id} --action auto-fix --confidence {score} \
     --complexity trivial --project {project} --files {file}
   ```

**ATTEMPT** (confidence 0.50-0.84):
1. Try the fix as above
2. If it succeeds on first attempt: treat as auto-fix
3. If it fails: log as escalation, add what was tried to bead comments
4. Log via triage_logger.py

**ESCALATE** (confidence < 0.50):
1. Send push notification so Bret knows immediately:
   ```bash
   happy notify "ESCALATED [{severity}] {title} — confidence {score} — {project}"
   ```
2. Update the bead with `needs-human` label: `mcp__beads__beads_update(id=bead_id, labels="bug,needs-human")`
3. Add triage findings as a bead comment:
   ```
   mcp__beads__beads_comment(
     id=bead_id,
     body="[TRIAGE] Confidence: {score}, Complexity: {complexity}\n
           Reason: {reason}\n
           Files examined: {files}\n
           Suggested investigation: {direction}"
   )
   ```
4. Log via triage_logger.py:
   ```bash
   python3 skills/bug-triage/scripts/triage_logger.py \
     --bead-id {id} --action escalate --confidence {score} \
     --complexity {complexity} --project {project} --reason "{reason}"
   ```

### Step 5: Report

Display summary:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 BUG TRIAGE COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

 Scanned:  {total} bugs
 Auto-fixed: {fixed} ({list IDs})
 Attempted: {attempted} ({list IDs})
 Escalated: {escalated} ({list IDs})
 Deferred to phase: {deferred} ({list IDs})

 Log: ~/.claude/data/bug_triage_log.jsonl
```

In `scheduled` mode, output only the summary (no per-bug details).

## Scheduled Execution

To run bug triage on a recurring schedule:

```
/schedule
```

Create a trigger with:
- **Cron:** `*/30 * * * *` (every 30 minutes, adjust as needed)
- **Prompt:** `/bug-triage --scheduled`
- **Description:** "Autonomous bug triage — poll and auto-fix trivial bugs"

The `--scheduled` flag ensures minimal output suitable for background execution.

## Constraints

- **Never fix bugs outside the project directory.** The `project` field in the bug report determines the working directory.
- **Max 5 bugs per session.** If more than 5 bugs exist, triage the top 5 by priority and stop. Remaining bugs will be picked up in the next run.
- **Security bugs always escalate.** If `area` contains "auth", "crypto", "security", "credential", or "permission", set confidence to 0.0 regardless of other signals.
- **Never close a bug without a commit.** Auto-fixed bugs must have a corresponding git commit before the bead is closed.
- **No silent deferral.** Every bug must result in one of: auto-fix, attempt, escalate, or defer-to-phase. Unhandled bugs are logged as errors.
