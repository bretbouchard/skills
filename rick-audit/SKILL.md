---
name: rick-audit
description: Audit domain specialist agents for currency and freshness. Use when checking if Ricks are up to date with cutting-edge developments, scheduling periodic freshness scans, or updating agent definitions. Scans agent definitions, researches latest versions/APIs/standards, assigns currency scores, and auto-fixes minor issues.
---

# Rick Currency Audit

Keep all domain specialists cutting-edge.

## When to Use

- User wants to check if agents are current: `/rick-audit`
- User wants to audit a single specialist: `/rick-audit kicad-rick`
- User wants to auto-fix minor staleness: `/rick-audit --auto-fix`
- User wants to schedule periodic audits: `/rick-audit --schedule "0 9 * * 1"`

## Modes

### Mode 1: Single Rick Audit

```
/rick-audit kicad-rick
```

1. Launch `rick-curator` agent targeting the named Rick
2. It researches the domain's cutting-edge
3. Scores the Rick's currency (0-100)
4. Reports findings with specific update items
5. If `--auto-fix`, applies minor updates

### Mode 2: Full Audit

```
/rick-audit
/rick-audit --auto-fix
```

1. Launch `rick-curator` agent for all 81+ agents
2. Batch research by domain (PCB, Audio, Apple, etc.)
3. Score each Rick
4. Generate audit report at `data/rick-audit-report.md`
5. If `--auto-fix`, apply minor updates; queue major changes

### Mode 3: Schedule Recurring Audit

```
/rick-audit --schedule "0 9 * * 1"
```

Creates a CronCreate job:
- Default: Monday 9am
- Custom: any cron expression
- The scheduled job runs the full audit automatically

## Agent Invocation

```
Agent(
  subagent_type="rick-curator",
  prompt="Run a <single/full> currency audit.

  Target: <rick-name or 'all'>
  Auto-fix: <true/false>

  Follow the full process:
  1. Scan agent definitions
  2. Research cutting-edge for each domain
  3. Diff current vs latest
  4. Score each Rick (0-100)
  5. Apply minor updates (if auto-fix)
  6. Generate report at data/rick-audit-report.md"
)
```

## Output

Audit report at `data/rick-audit-report.md` with:
- Currency scores per Rick
- Specific update items (version bumps, new APIs, deprecations)
- Auto-applied changes log
- Items queued for user review

## Examples

```
/rick-audit                        # Full audit of all Ricks
/rick-audit kicad-rick             # Single Rick audit
/rick-audit --auto-fix             # Full audit + auto-apply minor updates
/rick-audit --schedule weekly      # Schedule Monday 9am recurring audit
/rick-audit --schedule "0 9 * * 1" # Custom schedule
```
