---
name: skill-route-test
description: "Test skill routing accuracy — send natural-language prompts to Claude, detect which skill fires, score against expected matches. Use when auditing skill descriptions, debugging wrong-skill invocations, or measuring routing precision after description changes."
argument-hint: "[--corpus path/to/corpus.json] [--trials N] [--output path/to/report.json] [--dry-run]"
user_invocable: true
allowed-tools:
  - Read
  - Bash
  - Write
  - Glob
---

<objective>
Run the Agentic COBOL-style routing test harness against the skill catalog.
</objective>

<process>

## 1. Parse arguments

Extract from the user's invocation:
- `--corpus <path>`: Path to test corpus JSON. Default: `scripts/default-corpus.json` (relative to this skill's directory)
- `--trials <N>`: Number of trials per prompt. Default: 3
- `--output <path>`: Path to save JSON report. Default: `~/.claude/plans/route-test-report-{timestamp}.json`
- `--dry-run`: Validate corpus and show what would run, without making API calls

## 2. Resolve corpus path

If `--corpus` not provided, use the default corpus at this skill's `scripts/default-corpus.json`.
Read and validate the corpus structure.

## 3. Run the harness

```bash
python3 ~/.claude/skills/skill-route-test/scripts/route-test.py \
  --corpus <corpus_path> \
  --trials <N> \
  --output <output_path>
```

If `--dry-run`, add the `--dry-run` flag.

## 4. Present results

Read the output report and present:
- Aggregate score (PASS/PARTIAL/MISS/FAIL counts)
- Per-category breakdown
- Any failures with the prompt, expected skill, and actual result
- If failures found, suggest description improvements for the affected skills

## 5. Save raw transcripts

The harness saves raw stream-json transcripts to `~/.claude/plans/route-test-transcripts/`.
Mention this location so the user can inspect raw artifacts for scorer debugging.

</process>
