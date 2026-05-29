---
name: bootstrap-project
description: Bootstrap a project with CLAUDE.md context, tool inventory, and workflow automation. Scans for CLI tools, scripts, and automation, then writes project-scoped instructions so agents know what's available without hand-holding. Use when setting up a new project, fixing agents that ask humans to run things manually, or updating stale project context.
---

# Bootstrap Project

Give agents the context they need to work autonomously.

## When to Use

- New project needs agent context
- Agents ask humans to run things that should be automated
- Project tools have changed and context is stale
- User says "bootstrap this project" or "set up the agents"

## Process

### Step 1: Detect Project Type

Scan the project root for:
- `.kicad_pro`, `.kicad_sch`, `.kicad_pcb` → KiCad project
- `*.xcodeproj`, `*.xcworkspace`, `Package.swift` → Apple/Swift project
- `*.juce`, `*.jucer`, `CMakeLists.txt` with JUCE → Audio/JUCE project
- `.pyproject.toml`, `setup.py`, `requirements.txt` → Python project
- `Cargo.toml` → Rust project
- `package.json` → Node.js project
- `*.blend`, `*.blender` → Blender project
- `.ue4`, `.uproject` → Unreal Engine project

### Step 2: Scan for Available Tools

Run these detections:

```bash
# Check for CLI tools
which kicad-cli && kicad-cli --version
which swift && swift --version
which cargo && cargo --version
which npm && npm --version
which blender && blender --version

# Check for project scripts
ls scripts/ 2>/dev/null
ls tools/ 2>/dev/null
ls Makefile Justfile Rakefile 2>/dev/null

# Check for Python packages
ls requirements.txt pyproject.toml setup.py 2>/dev/null

# Check for CI/CD
ls .github/workflows/ .gitlab-ci.yml Jenkinsfile 2>/dev/null

# Check for existing Claude config
ls .claude/CLAUDE.md CLAUDE.md .claude/settings.local.json 2>/dev/null
```

### Step 3: Generate CLAUDE.md

Write to `.claude/CLAUDE.md` in the project root. The file should contain:

1. **Tool Inventory** — Every CLI command, script, and automation available, with exact invocation syntax
2. **Workflow Stages** — The domain-specific pipeline (what happens in what order)
3. **Agent Rules** — "Never ask a human to do what a CLI can do" plus domain-specific rules
4. **Beads/GSD Integration** — How to track work and create issues
5. **Project Structure** — Key directories and what they contain

Template:

```markdown
# {Project Name} — Agent Context

## Tool Inventory

{Auto-generated from scan. Every CLI command with exact syntax.}

## Workflow Stages

{Domain-specific pipeline stages.}

## Agent Rules

- **Automate first.** Before asking a human to run something manually, check the tool inventory above. If a CLI command exists, use it.
- **Track in Beads.** Use `mcp__beads__beads_create` for every issue found or task started. Use `mcp__beads__beads_update` to track progress.
- **Never skip validation.** {Domain-specific: e.g., always run ERC before DRC, always run DRC before gerber export}
- **Out-of-scope findings must be tracked.** If you find an issue but it's not in the current task, create a Bead with labels "out-of-scope" before continuing.

## Project Structure

{Key directories and their purpose.}

## Key Commands

| I want to... | Command |
|-------------|---------|
| {action} | `{exact command}` |
```

### Step 4: Create .claude Directory

```bash
mkdir -p .claude
```

### Step 5: Verify

1. Read back the generated CLAUDE.md
2. Confirm every tool referenced actually exists (`which` / `ls`)
3. Confirm workflow stages match the domain
4. Present summary to user

## Important Rules

- **Verify every tool.** Don't list a CLI that isn't installed. Run `which` or `--version` first.
- **Exact syntax only.** Every command must be copy-pasteable. Include all required flags.
- **Domain-aware.** The workflow stages must match the actual domain (KiCad != Audio != Swift).
- **Don't overwrite without reading.** If CLAUDE.md exists, read it first and merge/update rather than replace.
- **Keep it actionable.** This is a reference for agents, not documentation for humans. Every line should help an agent do something.
