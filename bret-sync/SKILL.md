---
name: bret:sync
description: Sync GSD projects with beads tracking - creates/updates beads for requirements, phases, and plans
user_invocable: true
allowed-tools:
  - Read
  - Bash
  - Write
  - Grep
  - Glob
---

<objective>
Sync GSD project structure with Beads tracking — create and update beads for requirements, phases, plans, and milestones to maintain universal visibility.
</objective>

<process>

## 1. Discover GSD projects

Scan for directories with `.planning/`:
```bash
find ~ -maxdepth 4 -name ".planning" -type d 2>/dev/null | head -20
```

## 2. For each project, read structure

Read `.planning/PROJECT.md`, `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, and `.planning/STATE.md`.

## 3. Create or update beads

Using `mcp__beads__beads_create` and `mcp__beads__beads_update`:

- **Meta-bead** (EPIC): One per project, tracks project-level status
- **Feature beads** (FEAT): One per requirement (AUTH-01, CONT-02, etc.)
- **Phase epics** (EPIC): One per roadmap phase
- **Task beads** (TASK): One per plan in each phase

Set dependencies using `mcp__beads__beads_dep_add`:
- Features depend on the meta-bead
- Phases depend on their features
- Tasks depend on their phase epic

## 4. Report sync results

```
BRETSYNC COMPLETE
=================
Project:    {name}
Meta-bead:  META-{id} ({created/updated})
Features:   {N} created, {M} updated
Phases:     {N} epics
Tasks:      {N} task beads
Dependencies: {N} links created
```

</process>
