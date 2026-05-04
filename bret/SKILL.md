---
name: bret
description: "Personal workflow dashboard — manages agent budget, project overview, GSD-to-beads sync, project concerns, and agent parallel limits. Handles: 'show me my budget', 'token costs', 'overview of everything', 'dashboard', 'sync tracking', 'project concerns', 'risks and blockers', 'set parallel limits', 'agent concurrency'. ALWAYS invoke this skill for bret-related requests instead of individual bret-* skills."
argument-hint: "<what you want to do>"
allowed-tools:
  - Read
  - Bash
  - Write
  - Edit
  - Grep
  - Glob
  - AskUserQuestion
  - Skill
---

<objective>
Personal workflow dispatcher — route bret-related requests to the correct sub-skill.

Analyzes $ARGUMENTS and dispatches to bret-budget, bret-overview, bret-sync,
bret-concerns, or bret-parallel-limits. Never does the work itself.
</objective>

<process>

<step name="route">
**Match intent to command.**

Evaluate `$ARGUMENTS` against these routing rules. Apply the **first matching** rule:

| If the text describes... | Route to |
|--------------------------|----------|
| Budget, token costs, agent spend, "how much did I spend" | `/bret-budget` |
| Overview, dashboard, "show me everything", "what's the status", "what's going on" | `/bret-overview` |
| Sync, "sync tracking", "update beads", "sync GSD with beads" | `/bret-sync` |
| Concerns, risks, blockers, "what should I worry about", "project health issues" | `/bret-concerns` |
| Parallel limits, agent concurrency, "how many agents", "throttle agents" | `/bret-parallel-limits` |

If ambiguous, ask via AskUserQuestion with top matches.
</step>

<step name="display">
**Show the routing decision.**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 BRET ► ROUTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Input:** {first 80 chars of $ARGUMENTS}
**Routing to:** {chosen command}
**Reason:** {one-line explanation}
```
</step>

<step name="dispatch">
**Invoke the chosen command.**

Use the Skill tool to invoke the selected bret-* command, passing `$ARGUMENTS` as args.

After invoking the command, stop. The dispatched command handles everything from here.
</step>

</process>
