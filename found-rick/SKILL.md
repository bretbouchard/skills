---
name: found-rick
description: Create a new domain specialist Rick agent. Use when encountering a domain with no existing specialist, when the user says "create a rick for X", "we need a specialist for X", or "make a rick". Auto-researches the domain, generates the agent definition, self-expands capabilities, and registers in the Council of Ricks.
---

# Found a Rick

Create a new domain specialist agent from scratch.

## When to Use

- User encounters a domain with no existing Rick
- User says "create a rick for X", "make a rick", "we need a specialist"
- Council review identifies a domain gap (no specialist for the work being reviewed)
- User mentions a technology/framework with no dedicated agent

## Process

### Step 1: Confirm the Domain

Ask the user to confirm or refine:
- What domain/technology needs a specialist?
- What's the primary use case? (Review, creation, analysis, automation?)
- Any existing Ricks that partially cover this?

### Step 2: Launch Rick Founder

Use the `rick-founder` agent to:

```
Agent(
  subagent_type="rick-founder",
  prompt="Create a new domain specialist Rick for: <domain>

  Context: <what the user described>
  Use case: <review/creation/analysis/automation>
  Related existing Ricks: <any partial coverage>

  Follow the full 5-phase process:
  1. Research the domain (WebSearch, Context Hub, codebase scan)
  2. Draft the agent definition
  3. Self-expand capabilities (identify 3-5 additional capabilities)
  4. Register in Council roster (agents/council-of-ricks.md)
  5. Validate the result

  Write the agent file to: agents/<domain>-rick.md"
)
```

### Step 3: Review with User

Present the created Rick to the user:
- Show the agent file path
- Summarize key capabilities
- Show where it was registered in the Council
- Ask if any capabilities should be added or removed

### Step 4: Iterate if Needed

If the user wants changes, use `rick-founder` again with refinement instructions.

## Examples

```
/found-rick quantum-computing
/found-rick rust-embedded
/found-rick devops
/found-rick cybersecurity
```
