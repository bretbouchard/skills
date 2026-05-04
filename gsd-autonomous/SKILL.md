---
name: gsd-autonomous
description: "INTERNAL — invoked by /gsd umbrella. Run phases autonomously with auto-loop — executes discuss→plan→execute per phase without user intervention. Use when user says 'run autonomously', 'auto-loop this', 'run all phases', or 'hands-off execution'. Always invoke this skill for autonomous execution rather than running phases one by one."
argument-hint: "[--from N] [--to N] [--only N] [--interactive]"
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
  - Task
  - Agent
---

<objective>
Execute all remaining milestone phases autonomously. For each phase: discuss → plan → execute. Pauses only for user decisions (grey area acceptance, blockers, validation requests).

Uses ROADMAP.md phase discovery and Skill() flat invocations for each phase command. After all phases complete: milestone audit → complete → cleanup.

**Creates/Updates:**
- `.planning/STATE.md` — updated after each phase
- `.planning/ROADMAP.md` — progress updated after each phase
- Phase artifacts — CONTEXT.md, PLANs, SUMMARYs per phase

**After:** Milestone is complete and cleaned up.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/autonomous.md
@$HOME/.claude/get-shit-done/references/ui-brand.md
</execution_context>

<context>
Optional flags:
- `--from N` — start from phase N instead of the first incomplete phase.
- `--to N` — stop after phase N completes (halt instead of advancing to next phase).
- `--only N` — execute only phase N (single-phase mode).
- `--interactive` — run discuss inline with questions (not auto-answered), then dispatch plan→execute as background agents. Keeps the main context lean while preserving user input on decisions.

Project context, phase list, and state are resolved inside the workflow using init commands (`gsd-sdk query init.milestone-op`, `gsd-sdk query roadmap.analyze`). No upfront context loading needed.
</context>

<process>
Execute the autonomous workflow from @$HOME/.claude/get-shit-done/workflows/autonomous.md end-to-end.
Preserve all workflow gates (phase discovery, per-phase execution, blocker handling, progress display).
</process>
