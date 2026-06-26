---
name: cleanup-disk
description: >
  Find and clear space hogs when disk is full or near-full. Scans caches, Xcode
  build artifacts, simulator runtimes, package manager caches, and local LLM
  model downloads. Provides copy-paste-ready commands the user runs manually
  (Safety Net hook blocks `rm -rf` outside cwd from the agent). Use when user
  says "disk full", "no space left", "ENOSPC", "free up space", "clean caches",
  "clear derived data", or when a write fails with disk-full errors.
argument-hint: "[scan|tcl|t2|all]"
license: MIT
---

# Cleanup Disk

Disk full events block writes across the entire session. This skill finds the
biggest safe-to-delete hogs and gives the user ready-to-run commands.

## Step 1 — Scan for space hogs

Always start here. Run these in parallel:

```bash
# Disk state
df -h / /System/Volumes/Data | tail -2

# Top offenders (one-liner overview)
du -sh ~/.cache ~/Library/Developer/CoreSimulator ~/Library/Developer/Xcode/DerivedData \
       ~/.npm ~/.gradle ~/.cargo ~/.Trash ~/Downloads ~/.claude 2>/dev/null | sort -rh

# HuggingFace model cache (frequent 10-50G hog)
du -sh ~/.cache/huggingface/hub/models--* 2>/dev/null | sort -rh

# DerivedData across all projects
find ~/apps -maxdepth 6 -type d -name "DerivedData" -not -path "*/node_modules/*" \
  -not -path "*/.git/*" 2>/dev/null -exec du -sh {} + | sort -rh

# iOS / tvOS Simulator runtimes
xcrun simctl runtime list
```

## Step 2 — Tier 1 (safe, regenerable, biggest wins)

| Target | Typical size | Safe because |
|--------|--------------|--------------|
| Local LLM model duplicates (`~/.cache/huggingface/hub/models--*`) | 5-50G | Re-downloadable from HuggingFace |
| Xcode DerivedData (`~/apps/**/DerivedData`, `~/Library/Developer/Xcode/DerivedData`) | 5-25G | Regenerates on next build |
| Old iOS/tvOS simulator runtimes | 5-15G | Old OS versions rarely needed |

### Commands to give the user

```bash
# 1. HuggingFace models (replace with actual duplicates found in scan)
rm -rf ~/.cache/huggingface/hub/models--<dup-1> \
       ~/.cache/huggingface/hub/models--<dup-2>

# 2. DerivedData — all projects + system
find ~/apps -maxdepth 6 -type d -name "DerivedData" -not -path "*/node_modules/*" \
  -not -path "*/.git/*" -exec rm -rf {} +
rm -rf ~/Library/Developer/Xcode/DerivedData/*

# 3. Old simulator runtimes — get full UUIDs from `xcrun simctl runtime list`
# Keep the latest iOS + tvOS, delete older versions
xcrun simctl runtime delete <FULL-UUID-1>
xcrun simctl runtime delete <FULL-UUID-2>

# Verify
df -h / /System/Volumes/Data | tail -2
```

**Note:** `xcrun simctl runtime delete` needs the FULL UUID, not the 8-char prefix.
Get them from `xcrun simctl runtime list` output.

## Step 3 — Tier 2 (medium wins, if Tier 1 wasn't enough)

| Target | Typical size | Command |
|--------|--------------|---------|
| npm cache | 2-5G | `npm cache clean --force` |
| Old Xcode Archives | 1-5G | Review `~/Library/Developer/Xcode/Archives`, delete old |
| iOS DeviceSupport | 2-8G | `rm -rf ~/Library/Developer/Xcode/iOS\ DeviceSupport/*` |
| `~/.gradle/caches` | 1-3G | `rm -rf ~/.gradle/caches` |
| `~/.cache/codex-runtimes` | 1-2G | `rm -rf ~/.cache/codex-runtimes` |
| `~/.cache/kicad-agent` | 1-5G | Investigate first; may contain KiCad installs |

## Step 4 — Tier 3 (skip unless desperate)

These require re-installation to undo:

- `.venv` / `venv` directories (1G each, several across apps)
- `node_modules` directories (500M-2G each)
- `~/Library/Application Support/Code` (VS Code cache, 5G typical)
- `~/Library/Application Support/Google` (Chrome profile, 1-2G)

## Safety Net hook constraint

The Safety Net plugin blocks the agent from running `rm -rf` outside the cwd.
The hook's reason: "rm -rf outside cwd is blocked. Use explicit paths within
the current directory, or delete manually."

**Correct behavior:** generate the commands, present them to the user, let
them run manually in their terminal. Do NOT attempt to bypass via
`dangerouslyDisableSandbox` — the Safety Net is a separate hook and ignores
that parameter.

## Decision flowchart

```
Disk full?
├─ Yes → Run Step 1 scan
│         ├─ HuggingFace duplicates? → Tier 1
│         ├─ DerivedData > 5G?       → Tier 1
│         └─ Old simulators?         → Tier 1
│
├─ Still full after Tier 1? → Tier 2
│
└─ Still full after Tier 2? → Tier 3 (warn user about re-install cost)
```

## What NOT to delete

- `~/.claude/projects/` — session histories, needed for `/gsd-resume-work`
- `~/.claude/memory-backup/` — Confucius backups
- `~/Library/Keychains` — passwords/certs
- Anything under `~/Library/Mobile Documents` (iCloud Drive)
- `~/Library/Mail`
- `.git/` directories (would destroy repos)

## Session recall

When invoked: run Step 1 scan immediately. Present Tier 1 candidates with
exact sizes and copy-paste commands. Wait for user to confirm they've run them.
Re-scan after cleanup. Stop when disk is below 85% used.
