# Skills Repository Branch Strategy

## Repository Structure
- **Main Repository**: `anthropics/skills` (upstream)
- **Your Fork**: `bretbouchard/skills` (origin/fork)

## Branches

### `bretbouchard-custom` (Public)
- **Purpose**: Public-facing custom skills
- **Contents**: Safe to share with the community
- **Examples**: `project-upgrade.md`, generic utility skills
- **Visibility**: Public (can be shared openly)

### `bretbouchard-custom-private` (Private)
- **Purpose**: Internal/private custom skills
- **Contents**: Company-specific, sensitive, or proprietary skills
- **Examples**: Internal workflows, proprietary algorithms, sensitive data processing
- **Visibility**: Private (internal use only)

## Workflow

### Adding Public Skills
```bash
cd skills
git checkout bretbouchard-custom
# Add your public skill
git add .
git commit -m "feat: Add new public skill"
git push fork bretbouchard-custom
```

### Adding Private Skills
```bash
cd skills
git checkout bretbouchard-custom-private
# Add your private skill
git add .
git commit -m "feat: Add private internal skill"
git push fork bretbouchard-custom-private
```

### Syncing Updates from Upstream
```bash
cd skills
git checkout main
git pull origin main

# Update public branch
git checkout bretbouchard-custom
git merge main

# Update private branch
git checkout bretbouchard-custom-private
git merge main

# Push updates
git push fork bretbouchard-custom
git push fork bretbouchard-custom-private
```

### Copying Skills Between Branches
```bash
# From private to public (if skill becomes safe to share)
git checkout bretbouchard-custom-private
git checkout bretbouchard-custom -- path/to/skill

# From public to private (if skill needs private modifications)
git checkout bretbouchard-custom
git checkout bretbouchard-custom-private -- path/to/skill
```

## Guidelines

### Public Skills (bretbouchard-custom)
- ✅ Generic and reusable
- ✅ No proprietary information
- ✅ Well-documented
- ✅ Safe for open source sharing

### Private Skills (bretbouchard-custom-private)
- 🔒 Company-specific workflows
- 🔒 Proprietary algorithms
- 🔒 Sensitive data handling
- 🔒 Internal business logic

## Integration with .claude

Your .claude repository uses the skills submodule. To switch which branch you're using:

```bash
cd ~/.claude/skills
git checkout bretbouchard-custom        # Use public skills
# OR
git checkout bretbouchard-custom-private # Use private skills
```

This allows you to easily switch between public and private skill sets depending on your current project context.
