---
name: gsd-health
description: "Diagnose GSD planning directory health and optionally repair issues — checks STATE.md, ROADMAP.md, phase directories for consistency. Use when user says 'check project health', 'health check', 'diagnose planning', 'is my project healthy', or 'repair planning'. Always invoke this skill for project health diagnostics."
argument-hint: "[--repair]"
allowed-tools:
  - Read
  - Bash
  - Write
  - AskUserQuestion
---

<objective>
Validate `.planning/` directory integrity and report actionable issues. Checks for missing files, invalid configurations, inconsistent state, and orphaned plans.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/health.md
</execution_context>

<process>
Execute the health workflow from @$HOME/.claude/get-shit-done/workflows/health.md end-to-end.
Parse --repair flag from arguments and pass to workflow.
</process>
