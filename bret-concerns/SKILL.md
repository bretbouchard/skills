---
name: bret:concerns
description: "INTERNAL — invoked by /bret umbrella. Surface project concerns, risks, and blockers — scan GSD projects and beads for issues needing attention before they escalate. Use when user asks about risks, concerns, blockers, or what might go wrong."
user_invocable: true
allowed-tools:
  - Read
  - Bash
  - Write
  - Grep
  - Glob
---

<objective>
Surface project concerns, risks, and blockers across all active GSD projects and beads tasks.
</objective>

<process>

## 1. Check beads blockers

```bash
# Use MCP tools if available, otherwise CLI
```

Call `mcp__beads__beads_blocked` to get issues with unresolved dependencies.

## 2. Scan GSD project state files

For each directory with `.planning/`:
```bash
cat .planning/STATE.md 2>/dev/null | grep -i "blocked\|concern\|risk\|issue\|warning" || true
```

## 3. Check drift events

```bash
cat ~/.claude/data/drift_events.json 2>/dev/null | python3 -c "
import json, sys
try:
    events = json.load(sys.stdin)
    recent = events[-5:] if len(events) > 5 else events
    for e in recent:
        print(f\"  {e.get('timestamp', 'N/A')}: {e.get('file', 'N/A')} — {e.get('type', 'N/A')}\")
except: print('No drift events')
" || echo "No drift events file"
```

## 4. Check escalation state

```bash
python3 ~/.claude/hooks/rick-escalation.py status 2>/dev/null || echo "No escalation state"
```

## 5. Present concerns report

```
CONCERNS & RISKS
================
Blockers:       {count} beads blocked
Drift events:   {count} recent scope deviations
Escalations:    {current tier or "None"}
Project risks:  {from STATE.md scan}

Top concerns:
1. {most urgent}
2. {second}
3. {third}

Action needed: {yes/no — what to address first}
```

</process>
