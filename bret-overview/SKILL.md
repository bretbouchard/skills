---
name: bret:overview
description: "Show unified dashboard of all work — GSD projects, beads tasks, auto-loop status, agent budget, blockers, progress. Triggers: show me everything, overview, dashboard, what's the status, what's going on"
user_invocable: true
allowed-tools:
  - Read
  - Bash
  - Grep
  - Glob
---

<objective>
Universal dashboard — show EVERYTHING at a glance. All GSD projects, beads tracking, progress, blockers, active auto-loops, and agent budget.
</objective>

<process>

## 1. Active Auto-Loop Status

```bash
~/.claude/bin/auto-loopctl awareness 2>/dev/null || echo "No auto-loop running"
~/.claude/bin/auto-loopctl budget-status 2>/dev/null || echo "Budget: N/A"
```

Display prominently at the top if any auto-loop is running. Include:
- Run ID, objective, iteration progress
- Agent budget usage (claimed/total)
- Whether the current session should throttle its own agent usage

## 2. Beads Overview

```bash
bd list --tree 2>/dev/null || echo "Beads unavailable"
bd ready --json 2>/dev/null || echo "No ready work"
bd blocked 2>/dev/null || echo "No blockers"
```

## 3. GSD Projects

For each directory with `.planning/`:
```bash
cat .planning/PROJECT.md 2>/dev/null | head -20
cat .planning/STATE.md 2>/dev/null | head -30
```

## 4. Summary

Present a unified dashboard:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 OVERVIEW — {date}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

 AUTO-LOOP: {status or "None active"}
 AGENTS:   {budget_used}/{budget_total} slots in use

 PROJECTS:
 {project summaries}

 BEADS:
 {bead tree summary}

 READY WORK:
 {ready items}

 BLOCKERS:
 {blocked items}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

</process>
