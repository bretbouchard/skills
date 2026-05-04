---
name: bret:parallel-limits
description: "INTERNAL — invoked by /bret umbrella. Configure concurrent agent limits — set max parallel agents, view current contention, and adjust resource allocation for auto-loops. Use when user says 'set parallel limits', 'how many agents can run', 'agent concurrency', 'throttle agents', or 'parallel agent'. Always invoke this skill for agent limit configuration."
user_invocable: true
allowed-tools:
  - Read
  - Bash
  - Write
  - Grep
  - Glob
---

<objective>
Configure and display concurrent agent limits — control how many parallel agents can run simultaneously to manage resource contention.
</objective>

<process>

## 1. Show current limits

Read current configuration:
```bash
python3 -c "
import json
with open('$HOME/.claude/settings.json') as f:
    d = json.load(f)
print(f\"Max concurrent agents: {d.get('maxConcurrentAgents', 'not set (unlimited)')}\")
" 2>/dev/null || echo "Could not read settings"
```

Check active agent count:
```bash
~/.claude/bin/auto-loopctl budget-status 2>/dev/null || echo "No auto-loop running"
```

## 2. If user wants to set limits

Read the current `~/.claude/settings.json`, update `maxConcurrentAgents` to the desired value, and write it back.

Common values:
- **2**: Conservative — for resource-constrained environments
- **4**: Default — good balance of throughput and safety
- **5**: Recommended max for most workflows (per rules/agents.md)

## 3. Verify the change

After updating, confirm the new value is set:
```bash
python3 -c "import json; d=json.load(open('$HOME/.claude/settings.json')); print('Updated limit:', d.get('maxConcurrentAgents', 'not set'))"
```

## 4. Present summary

```
PARALLEL AGENT LIMITS
=====================
Current limit:   {N} concurrent agents
Active agents:   {count}
Recommended:     4 (default), max 5 per agents.md
```

</process>
