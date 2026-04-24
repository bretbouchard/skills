---
name: auto-loop
description: "Autonomous agent loop — give an objective, it works for hours/days using all tools"
argument-hint: "<objective> [--iterations N] [--duration HOURS] [--resume ID] [--schedule \"cron\"] [--dry-run] [--driver]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
  - Agent
  - CronCreate
  - CronDelete
  - CronList
  - TodoWrite
  - RemoteTrigger
  - WebSearch
  - mcp__beads__beads_create
  - mcp__beads__beads_update
  - mcp__beads__beads_list
  - mcp__confucius__memory_store
  - mcp__confucius__memory_retrieve
  - mcp__confucius__memory_retrodict
  - mcp__confucius__memory_record_trajectory
  - mcp__cognee-local__search
  - mcp__cognee-local__cognify
  - mcp__serena__find_symbol
  - mcp__serena__get_symbols_overview
  - mcp__serena__replace_symbol_body
  - mcp__serena__safe_delete_symbol
  - mcp__serena__write_memory
  - mcp__chub__chub_get
  - mcp__chub__chub_search
---

<objective>
Run a fully autonomous agent loop on a freeform objective. Not tied to GSD milestones — works on any codebase, any goal.

Architecture: deterministic control plane (`auto-loopctl`) + stateless LLM workers. Each iteration is a fresh session with clean context. State managed via STATE.json (source of truth).

Designed for extended runs (hours/days): "Optimize the build pipeline", "Audit all security surfaces", "Refactor the auth module", "Find and fix all performance bottlenecks".

**Two execution modes:**
1. **Interactive** (default) — runs in current session, one iteration at a time
2. **Driver** (`--driver`) — chains sessions via `auto-loop-driver` for unattended multi-day runs

**Creates/Updates:**
- `.auto-loop/{ID}/` — Run directory with STATE.json, LOG.jsonl, episodes, strategy
- Beads tasks for tracking visibility
- Confucius memory entries for cross-session learning
- Git commits on dedicated branch `auto-loop/{ID}`

**After:** Objective complete (all criteria met) or paused for review.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/auto-loop.md
@$HOME/.claude/get-shit-done/references/auto-loop-strategies.md
</execution_context>

<context>
$ARGUMENTS — The objective to autonomously pursue.

Flags:
- `--iterations N` — Maximum iterations before pause (default: 10)
- `--duration HOURS` — Time limit in hours (default: none, runs until done)
- `--resume ID` — Resume a previous run by ID
- `--schedule "cron"` — Schedule as recurring remote agent (e.g., "*/30 * * * *" for every 30min)
- `--dry-run` — Plan strategy without executing, then exit
- `--driver` — Use external driver script for unattended multi-day runs
- `--confirm-criteria` — Pause after strategy generation for user to review success criteria
- `--review-every N` — Pause every N iterations for user steering
- `--ship` — On success, push branch and create PR
</context>

<process>
Execute the auto-loop workflow from @$HOME/.claude/get-shit-done/workflows/auto-loop.md end-to-end.
Uses auto-loopctl for deterministic state management (iteration counting, timing, git tracking, failure counting).
</process>
