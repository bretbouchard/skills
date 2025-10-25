---
name: project-upgrade
description: Upgrade existing projects to unified structure and handle legacy formats

---

# Project Upgrade Workflow

## Purpose
Upgrades existing projects to match current unified structure while preserving legacy content and preventing duplicate upgrades.

## When to Use This Skill
Use when starting work on any existing project that:
- Was created before current unified system was established
- Has inconsistent documentation structure (docs vs specs vs plans)
- Contains .kiro files or legacy formats
- Missing unified directories (specs/, plans/)
- Unclear what version of project structure it's using

## Migration Checklist

### 1. Assessment Phase
- [ ] Check current project structure and identify legacy elements
- [ ] Look for .kiro files, old docs/, mixed documentation
- [ ] Check if CONSTITUTION.md exists and what version it references
- [ ] Identify what needs migration vs what's already correct

### 2. Legacy Detection
- [ ] **.kiro files**: Move to `legacy/.kiro/` (preserve, don't delete)
- [ ] **Old docs/ structure**: Check if contains project docs vs GitHub Pages content
- [ ] **Mixed documentation**: Separate specs from plans from existing content
- [ ] **Missing structure**: Create specs/, plans/ if needed

### 3. Migration Phase
- [ ] Create migration issue in bd to track the upgrade process
- [ ] Move legacy files to `legacy/` directory (never delete)
- [ ] Create unified docs structure (specs/, plans/)
- [ ] Update CONSTITUTION.md with upgrade notation
- [ ] Document what was changed and why

### 4. Version Tracking
- [ ] Add `.project-version` file to track structure version
- [ ] Note upgrade date and what was changed
- [ ] Mark in bd issue that project has been upgraded
- [ ] Create upgrade documentation for future reference

## Implementation Steps

### Step 1: Assessment
```bash
# Check current state
find . -name "*.md" -o -name ".kiro" -o -name "docs" -o -name "specs" -o -name "plans" | sort
bd ready --json
```

### Step 2: Legacy Handling
```bash
# Preserve legacy content
mkdir -p legacy/.kiro legacy/old-docs
# Move .kiro files (don't delete)
find . -name ".kiro" -exec mv {} legacy/.kiro/ \;
# Move old docs if they contain project content (not GitHub Pages)
if [ -d "docs" ] && ! grep -q "github.io\|pages" docs/*.md 2>/dev/null; then
    mv docs legacy/old-docs
fi
```

### Step 3: Structure Creation
```bash
# Create unified structure
mkdir -p specs plans
# Create version tracking
echo "project-structure-version: 2.0
upgraded: $(date +%Y-%m-%d)
previous-structure: mixed/legacy" > .project-version
```

### Step 4: Documentation
```bash
# Create upgrade note
cat > UPGRADE.md << 'EOF'
# Project Structure Upgrade

## Upgraded: $(date +%Y-%m-%d)
## Previous Structure: Mixed/Legacy
## New Structure: Unified (specs/, plans/, docs/ for GitHub Pages)

## Changes Made:
- Created unified documentation structure
- Preserved legacy files in \`legacy/\` directory
- Added version tracking for future upgrades
- Updated project constitution

## Legacy Content Preserved:
- .kiro files → \`legacy/.kiro/\`
- Old docs → \`legacy/old-docs/\` (if not GitHub Pages)

## New Workflow:
- Use \`specs/\` for specifications (from /speckit.specify)
- Use \`plans/\` for implementation plans (from /speckit.plan)
- Keep \`docs/\` for GitHub Pages content only
EOF
```

## Prevention of Duplicate Upgrades

The workflow prevents duplicate upgrades by:
1. **Version Tracking**: `.project-version` file shows current structure version
2. **Migration Issue**: bd issue tracks completion status
3. **Constitution Update**: Notes upgrade in project constitution
4. **Legacy Preservation**: Never deletes old content, moves to `legacy/`

## Commands to Remember
- `/skill:project-upgrade` - Run this full workflow
- `bd ready --json` - Check current project state
- `mkdir -p specs plans` - Create missing structure manually
- Check for `.project-version` file to detect if upgrade needed

## Integration with Other Workflows
This works alongside:
- `/speckit.specify` - After upgrade, creates specs in correct location
- `/superpowers:brainstorm` - Works with unified structure
- `~/.claude/project-startup.sh` - Detects upgraded structure correctly