---
name: bret:budget
description: "Manage agent budget allocation — view current agent usage, set parallel limits, and track token spend across active sessions. Use when user asks about agent budget, token costs, or resource limits."
user_invocable: true
allowed-tools:
  - Read
  - Bash
  - Write
  - Grep
  - Glob
---

<objective>
Display and manage agent budget — show current agent slot usage, token spend, and parallel limits for active sessions.
</objective>

<process>

## 1. Show current budget status

```bash
~/.claude/bin/auto-loopctl budget-status 2>/dev/null || echo "Budget: N/A (no auto-loop running)"
```

Also check settings for configured limits:
```bash
cat ~/.claude/settings.json 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print('Parallel limits:', d.get('maxConcurrentAgents', 'not set'))" 2>/dev/null || echo "No parallel limit configured"
```

## 2. Display budget dashboard

```
AGENT BUDGET
============
Active agents:    {active}/{max}
Token spend:      {spent} / {limit}
Auto-loop status: {running/paused/none}
```

## 3. If user wants to set limits

Guide them to update `~/.claude/settings.json` with the desired `maxConcurrentAgents` value, or use the `/bret-parallel-limits` skill for detailed configuration.

</process>
