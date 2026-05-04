---
name: gsd-help
description: "Show all available GSD commands and usage guide — lists every skill with description and arguments. Use when user says 'what does GSD do', 'show me commands', 'help', 'what commands are available', or 'GSD help'. Always invoke this skill when user asks about GSD capabilities."
allowed-tools:
  - Read
---

<objective>
Display the complete GSD command reference.

Output ONLY the reference content below. Do NOT add:
- Project-specific analysis
- Git status or file context
- Next-step suggestions
- Any commentary beyond the reference
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/help.md
</execution_context>

<process>
Output the complete GSD command reference from @$HOME/.claude/get-shit-done/workflows/help.md.
Display the reference content directly — no additions or modifications.
</process>
