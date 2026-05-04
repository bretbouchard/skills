---
name: gsd
description: "Universal GSD project workflow — route ANY project management action to the right sub-command. Handles: new projects, milestones, phases, planning, execution, code review, debugging, verification, backlog, health checks, shipping, cleanup, notes, todos, workspaces, docs, and more. ALWAYS invoke this skill for any GSD-related request instead of routing to individual gsd-* skills. Use when user mentions ANY project workflow, phase, milestone, planning, execution, review, debugging, shipping, or GSD action."
argument-hint: "<what you want to do or sub-command>"
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
Universal GSD dispatcher — analyze user intent and invoke the correct gsd-* sub-skill.

This skill NEVER does project work itself. It reads intent from $ARGUMENTS,
matches it against the routing table below, and dispatches via the Skill tool.

All 70+ gsd-* skills are marked INTERNAL — this is the ONLY routing surface
for GSD-related natural language requests.
</objective>

<process>

<step name="validate">
**Check for input.**

If `$ARGUMENTS` is empty, ask via AskUserQuestion:

```
What would you like to do? Describe the task, bug, or idea and I'll route it to the right GSD command.
```

Wait for response before continuing.
</step>

<step name="check_project">
**Check if project exists.**

```bash
INIT=$(gsd-sdk query state.load 2>/dev/null)
```

Track whether `.planning/` exists — routes marked [requires project] need it.
</step>

<step name="route">
**Match intent to command.**

Evaluate `$ARGUMENTS` against these routing rules. Apply the **first matching** rule.
Phase numbers in square brackets are extracted from arguments if present.

## Project Lifecycle

| If the text describes... | Route to | Notes |
|--------------------------|----------|-------|
| Starting a new project, "set up", "initialize" | `/gsd-new-project` | No project needed |
| Starting a new milestone, "next version", "new cycle" | `/gsd-new-milestone` [requires project] | Brownfield milestone |
| Completing a milestone, "archive milestone", "wrap up version" | `/gsd-complete-milestone` [requires project] | Archive + prepare next |
| Summary of milestone, "milestone summary", "project recap" | `/gsd-milestone-summary` [requires project] | |

## Phase Lifecycle

| If the text describes... | Route to | Notes |
|--------------------------|----------|-------|
| Adding a phase, "add phase", "new phase" | `/gsd-add-phase` [requires project] | Adds to end of milestone |
| Inserting a phase urgently, "insert phase", "urgent phase" | `/gsd-insert-phase` [requires project] | Decimal numbering |
| Removing a phase, "remove phase", "delete phase" | `/gsd-remove-phase` [requires project] | Future phases only |
| Discussing a phase, "gather context", "clarify approach", "how should" | `/gsd-discuss-phase` [requires project] | Adaptive questioning |
| Planning a phase, "plan phase N", "create plan" | `/gsd-plan-phase` [requires project] | PLAN.md generation |
| Researching before planning, "research phase", "how does X work", "investigate" | `/gsd-research-phase` [requires project] | Domain research |
| Spec refinement, "spec phase", "refine requirements", "ambiguity" | `/gsd-spec-phase` [requires project] | Socratic refinement |
| Executing a phase, "build phase N", "run phase N", "execute" | `/gsd-execute-phase` [requires project] | Wave-based execution |
| Verifying work, "UAT", "test features", "validate features" | `/gsd-verify-work` [requires project] | Conversational UAT |
| Listing assumptions, "what assumptions", "assumptions about phase" | `/gsd-list-phase-assumptions` [requires project] | |
| Analyzing dependencies, "phase dependencies", "depends on" | `/gsd-analyze-dependencies` [requires project] | |

## Workflow Navigation

| If the text describes... | Route to | Notes |
|--------------------------|----------|-------|
| What's next, continue, advance, "what should I work on" | `/gsd-next` [requires project] | State-based routing |
| Progress check, "where am I", "project status", "how's it going" | `/gsd-progress` [requires project] | Status + routing |
| Do something (vague), "I want to...", not sure which command | `/gsd-do` fallback | Intent parsing |
| Run phases automatically, "autonomous", "auto-loop all phases" | `/gsd-autonomous` [requires project] | Sequential auto-exec |
| Manage multiple phases, "command center", "manage phases" | `/gsd-manager` [requires project] | Interactive dashboard |
| Managing parallel work, "workstreams", "parallel tracks" | `/gsd-workstreams` [requires project] | |

## Quick Actions

| If the text describes... | Route to | Notes |
|--------------------------|----------|-------|
| Quick trivial fix, "just fix this", "one-liner", "small thing" | `/gsd-fast` | No subagents, no planning |
| Quick task with options, "quick task", "small feature", "simple change" | `/gsd-quick` | Optional agents |
| Add to backlog, "save for later", "park this idea", "backlog" | `/gsd-add-backlog` [requires project] | 999.x numbering |
| Review backlog, "promote backlog", "backlog review" | `/gsd-review-backlog` [requires project] | |
| Capture a note, "note this", "remember to", "jot down" | `/gsd-note` [requires project] | Zero-friction capture |
| Add a todo, "add task", "track this", "todo" | `/gsd-add-todo` [requires project] | Structured todos |
| Check todos, "pending todos", "what's on my list" | `/gsd-check-todos` [requires project] | |

## Code Quality & Review

| If the text describes... | Route to | Notes |
|--------------------------|----------|-------|
| Code review, "review the code", "check code quality" | `/gsd-code-review` [requires project] | |
| Fix review issues, "fix code review", "address review" | `/gsd-code-review-fix` [requires project] | |
| External AI review, "cross-AI review", "get external review" | `/gsd-review` [requires project] | External CLI review |
| UI review, "visual audit", "UI check" | `/gsd-ui-review` [requires project] | 6-pillar audit |
| Security audit, "security check", "threat verification" | `/gsd-secure-phase` [requires project] | Threat mitigation check |
| Add tests, "write tests", "test coverage", "generate tests" | `/gsd-add-tests` [requires project] | Based on UAT |
| Validate phase, "validation gaps", "Nyquist check" | `/gsd-validate-phase` [requires project] | |
| AI eval review, "audit evaluation", "eval coverage" | `/gsd-eval-review` [requires project] | |

## Debugging & Investigation

| If the text describes... | Route to | Notes |
|--------------------------|----------|-------|
| Debug, bug, broken, crash, failure, "something's wrong" | `/gsd-debug` | Systematic debugging |
| Forensics, "post-mortem", "investigate failure", "what went wrong" | `/gsd-forensics` | Post-mortem analysis |
| Audit and fix, "auto-fix audit", "pipeline fix" | `/gsd-audit-fix` [requires project] | Autonomous pipeline |

## Innovation & Exploration

| If the text describes... | Route to | Notes |
|--------------------------|----------|-------|
| Spike, "test if", "will this work", "experiment", "prove this" | `/gsd-spike` | Throwaway experiment |
| Spike wrap-up, "package spikes", "consolidate findings" | `/gsd-spike-wrap-up` | |
| Sketch, "mockup", "what would this look like", "prototype UI" | `/gsd-sketch` | HTML mockups |
| Sketch wrap-up, "package designs", "consolidate sketches" | `/gsd-sketch-wrap-up` | |
| Explore ideas, "ideation", "Socratic", "brainstorm direction" | `/gsd-explore` | Socratic ideation |
| Plant a seed, "future idea", "trigger condition", "capture for later" | `/gsd-plant-seed` [requires project] | Forward-looking idea |
| AI integration phase, "AI design contract", "AI-SPEC" | `/gsd-ai-integration-phase` [requires project] | |
| UI design phase, "UI design contract", "UI-SPEC" | `/gsd-ui-phase` [requires project] | |

## Project Management

| If the text describes... | Route to | Notes |
|--------------------------|----------|-------|
| Audit milestone, "milestone audit", "pre-archive check" | `/gsd-audit-milestone` [requires project] | |
| Audit UAT, "cross-phase audit", "UAT audit" | `/gsd-audit-uat` [requires project] | |
| Plan milestone gaps, "fill gaps", "close audit gaps" | `/gsd-plan-milestone-gaps` [requires project] | |
| Cleanup, "archive phases", "clean up old phases" | `/gsd-cleanup` [requires project] | |
| Stats, "project statistics", "how many phases" | `/gsd-stats` [requires project] | |
| Health check, "diagnose planning", "is my project healthy" | `/gsd-health` | |
| Settings, "configure GSD", "workflow toggles" | `/gsd-settings` | |
| Set profile, "switch model", "change model profile" | `/gsd-set-profile` | |

## Documentation & Intelligence

| If the text describes... | Route to | Notes |
|--------------------------|----------|-------|
| Update docs, "generate docs", "documentation" | `/gsd-docs-update` [requires project] | |
| Map codebase, "analyze codebase", "codebase mapping" | `/gsd-map-codebase` | Parallel mapper agents |
| Scan codebase, "quick scan", "rapid assessment" | `/gsd-scan` | Lightweight |
| Intel, "codebase intelligence", "query intel" | `/gsd-intel` [requires project] | |
| Graphify, "knowledge graph", "graph query" | `/gsd-graphify` | |
| Extract learnings, "lessons learned", "what did we learn" | `/gsd-extract_learnings` [requires project] | |
| Session report, "session summary", "token usage" | `/gsd-session-report` | |
| Profile user, "developer profile", "behavioral analysis" | `/gsd-profile-user` | |

## Session Management

| If the text describes... | Route to | Notes |
|--------------------------|----------|-------|
| Pause work, "I need to stop", "handoff context" | `/gsd-pause-work` [requires project] | Context handoff |
| Resume work, "pick up where I left off", "restore session" | `/gsd-resume-work` [requires project] | Full context restore |
| Thread management, "persistent thread", "cross-session context" | `/gsd-thread` [requires project] | |
| Ship, "create PR", "release phase", "prepare merge" | `/gsd-ship` [requires project] | PR + review + merge |

## Workspace Operations

| If the text describes... | Route to | Notes |
|--------------------------|----------|-------|
| List workspaces, "show workspaces" | `/gsd-list-workspaces` | |
| New workspace, "create workspace", "isolated workspace" | `/gsd-new-workspace` | |
| Remove workspace, "delete workspace" | `/gsd-remove-workspace` | |

## Git & Integration

| If the text describes... | Route to | Notes |
|--------------------------|----------|-------|
| Undo, "revert phase", "rollback", "undo last commit" | `/gsd-undo` [requires project] | Safe git revert |
| PR branch, "clean PR branch", "filter .planning commits" | `/gsd-pr-branch` [requires project] | |
| Import plans, "ingest plans", "import external" | `/gsd-import` [requires project] | Conflict detection |
| Inbox triage, "triage GitHub issues", "process issues" | `/gsd-inbox` [requires project] | |
| GSD update, "update GSD", "latest version" | `/gsd-update` | |
| Reapply patches, "reapply local changes", "post-update fix" | `/gsd-reapply-patches` | |
| From GSD2, "import GSD-2", "migrate old project" | `/gsd-from-gsd2` | |
| Join Discord, "GSD community", "Discord" | `/gsd-join-discord` | No project needed |
| Help, "what does GSD do", "show commands" | `/gsd-help` | No project needed |

**Requires `.planning/` directory:** All routes marked [requires project]. If the project doesn't exist and the route requires it, suggest `/gsd-new-project` first.

**Ambiguity handling:** If the text could reasonably match multiple routes, ask the user via AskUserQuestion with the top 2-3 options.
</step>

<step name="display">
**Show the routing decision.**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 GSD ► ROUTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Input:** {first 80 chars of $ARGUMENTS}
**Routing to:** {chosen command}
**Reason:** {one-line explanation}
```
</step>

<step name="dispatch">
**Invoke the chosen command.**

Use the Skill tool to invoke the selected gsd-* command, passing `$ARGUMENTS` as args.

If the chosen command expects a phase number and one wasn't provided, extract it from context or ask via AskUserQuestion.

After invoking the command, stop. The dispatched command handles everything from here.
</step>

</process>
