#!/usr/bin/env python3
"""Agentic COBOL-style skill routing test harness.

Sends real natural-language prompts to Claude Code via `claude -p`,
parses stream-json output for Skill tool invocations, and scores
whether the correct skill was selected.

Usage:
    python3 route-test.py --corpus default-corpus.json [--trials 3] [--output report.json] [--dry-run]
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ── Corpus loading ──────────────────────────────────────────────

def load_corpus(path: str) -> dict:
    with open(path) as f:
        corpus = json.load(f)
    if "test_cases" not in corpus:
        print("ERROR: corpus missing 'test_cases' array", file=sys.stderr)
        sys.exit(1)
    return corpus


# ── Stream-JSON parsing ─────────────────────────────────────────

def extract_skill_invocations(stream_json_lines: list[str]) -> list[str]:
    """Parse stream-json output for Skill tool invocations.

    Looks for tool_use events where the tool is 'Skill' and extracts
    the skill name from the input. Returns list of invoked skill names.
    """
    skills = []
    for line in stream_json_lines:
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue

        # Handle tool_use events
        if event.get("type") == "tool_use":
            tool_name = event.get("name", "")
            tool_input = event.get("input", {})

            # Direct Skill tool invocation
            if tool_name == "Skill":
                skill_name = tool_input.get("skill", "")
                if skill_name:
                    skills.append(skill_name)
            # Also check for skill name in nested structures
            if isinstance(tool_input, dict):
                for v in tool_input.values():
                    if isinstance(v, str) and v.startswith("gsd-") or (isinstance(v, str) and "bret" in v.lower()):
                        # Likely a skill reference in another tool's input
                        pass

        # Handle content blocks with tool_use type
        content = event.get("content", [])
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    if block.get("name") == "Skill":
                        inp = block.get("input", {})
                        skill_name = inp.get("skill", "")
                        if skill_name:
                            skills.append(skill_name)

        # Check message structure (nested content blocks)
        message = event.get("message", {})
        if isinstance(message, dict):
            msg_content = message.get("content", [])
            if isinstance(msg_content, list):
                for block in msg_content:
                    if isinstance(block, dict) and block.get("type") == "tool_use":
                        if block.get("name") == "Skill":
                            inp = block.get("input", {})
                            skill_name = inp.get("skill", "")
                            if skill_name:
                                skills.append(skill_name)

    return skills


# ── Single test execution ───────────────────────────────────────

def run_single_prompt(prompt: str, max_budget: float = 0.15) -> tuple[list[str], str]:
    """Run a single prompt through claude -p and return (skills_invoked, raw_output)."""
    cmd = [
        "claude", "-p", prompt,
        "--output-format", "stream-json",
        "--verbose",
        "--max-budget-usd", str(max_budget),
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )
        raw = result.stdout
        lines = raw.splitlines()
        skills = extract_skill_invocations(lines)
        return skills, raw
    except subprocess.TimeoutExpired:
        return [], "TIMEOUT"
    except Exception as e:
        return [], f"ERROR: {e}"


# ── Scoring ─────────────────────────────────────────────────────

def score_invocation(invoked: list[str], expected: str, alternates: list[str]) -> str:
    """Score a single invocation result.

    Returns: PASS, PARTIAL, MISS, or FAIL
    """
    if not invoked:
        return "MISS"

    for skill in invoked:
        # Normalize skill names (strip namespace prefixes)
        normalized = skill.split(":")[-1] if ":" in skill else skill
        expected_norm = expected.split(":")[-1] if ":" in expected else expected

        if normalized == expected_norm or skill == expected:
            return "PASS"

        for alt in alternates:
            alt_norm = alt.split(":")[-1] if ":" in alt else alt
            if normalized == alt_norm or skill == alt:
                return "PARTIAL"

    return "FAIL"


# ── Report generation ───────────────────────────────────────────

def format_report(results: list[dict], corpus: dict, trials: int) -> str:
    """Generate human-readable report."""
    lines = []
    lines.append("=" * 60)
    lines.append("SKILL ROUTE TEST REPORT")
    lines.append("=" * 60)

    total = len(results)
    pass_count = sum(1 for r in results if r["verdict"] == "PASS")
    partial_count = sum(1 for r in results if r["verdict"] == "PARTIAL")
    miss_count = sum(1 for r in results if r["verdict"] == "MISS")
    fail_count = sum(1 for r in results if r["verdict"] == "FAIL")

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines.append(f"Date: {ts}")
    lines.append(f"Corpus: {corpus.get('description', 'N/A')} ({total} test cases)")
    lines.append(f"Trials: {trials} per prompt")
    lines.append("")

    # Category breakdown
    categories = {}
    for r in results:
        cat = r["category"]
        if cat not in categories:
            categories[cat] = {"pass": 0, "partial": 0, "miss": 0, "fail": 0, "total": 0}
        categories[cat]["total"] += 1
        categories[cat][r["verdict"].lower()] += 1

    lines.append("RESULTS BY CATEGORY")
    lines.append("-" * 40)
    for cat, counts in sorted(categories.items()):
        good = counts["pass"] + counts["partial"]
        total_cat = counts["total"]
        pct = (good / total_cat * 100) if total_cat else 0
        flag = " <--" if counts["miss"] > 0 or counts["fail"] > 0 else ""
        lines.append(f"  {cat:20s} {good}/{total_cat} ({pct:5.1f}%){flag}")
    lines.append("")

    # Failures
    failures = [r for r in results if r["verdict"] in ("MISS", "FAIL")]
    if failures:
        lines.append("FAILURES")
        lines.append("-" * 40)
        for f in failures:
            lines.append(f"  {f['id']}: \"{f['prompt'][:50]}...\"")
            lines.append(f"    Expected: {f['expected_skill']}")
            lines.append(f"    Got: {f['invoked_skills'] or 'NONE'}")
            if f.get("hit_rate") is not None:
                lines.append(f"    Hit rate: {f['hit_rate']:.0%} across {trials} trials")
            lines.append("")
    else:
        lines.append("ALL TESTS PASSED")
        lines.append("")

    # Aggregate
    score = (pass_count + partial_count * 0.5) / total * 100 if total else 0
    lines.append(f"AGGREGATE: {pass_count}/{total} PASS + {partial_count} PARTIAL = {score:.1f}%")
    lines.append("=" * 60)

    return "\n".join(lines)


# ── Main ────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Skill routing test harness")
    parser.add_argument("--corpus", required=True, help="Path to test corpus JSON")
    parser.add_argument("--trials", type=int, default=3, help="Trials per prompt")
    parser.add_argument("--output", default=None, help="Path to save JSON report")
    parser.add_argument("--dry-run", action="store_true", help="Validate corpus without running")
    parser.add_argument("--budget", type=float, default=1.00, help="Max USD per prompt invocation")
    parser.add_argument("--save-transcripts", action="store_true", default=True, help="Save raw transcripts")
    args = parser.parse_args()

    # Load corpus
    corpus = load_corpus(args.corpus)
    test_cases = corpus["test_cases"]
    print(f"Loaded {len(test_cases)} test cases from {args.corpus}")

    if args.dry_run:
        print("\nDry run — corpus validation:")
        for tc in test_cases:
            print(f"  {tc['id']}: \"{tc['prompt'][:50]}\" -> {tc['expected_skill']}")
        print(f"\nWould run {len(test_cases)} x {args.trials} = {len(test_cases) * args.trials} invocations")
        print(f"Estimated cost: ~${len(test_cases) * args.trials * args.budget:.2f}")
        return

    # Prepare transcript directory
    transcript_dir = Path.home() / ".claude" / "plans" / "route-test-transcripts"
    transcript_dir.mkdir(parents=True, exist_ok=True)

    # Run tests
    results = []
    total_invocations = len(test_cases) * args.trials
    invocation_num = 0

    for tc in test_cases:
        prompt = tc["prompt"]
        expected = tc["expected_skill"]
        alternates = tc.get("acceptable_alternates", [])
        category = tc.get("category", "unknown")

        trial_results = []

        for trial in range(args.trials):
            invocation_num += 1
            print(f"  [{invocation_num}/{total_invocations}] {tc['id']} trial {trial+1}: \"{prompt[:40]}...\"", end=" ", flush=True)

            skills, raw = run_single_prompt(prompt, max_budget=args.budget)

            # Save transcript
            if args.save_transcripts and raw != "TIMEOUT" and not raw.startswith("ERROR"):
                ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
                transcript_path = transcript_dir / f"{ts}_{tc['id']}_t{trial+1}.jsonl"
                transcript_path.write_text(raw)

            verdict = score_invocation(skills, expected, alternates)
            trial_results.append({
                "trial": trial + 1,
                "invoked": skills,
                "verdict": verdict,
            })
            print(verdict)

            # Small delay between invocations to avoid rate limits
            if trial < args.trials - 1:
                time.sleep(1)

        # Aggregate across trials
        pass_trials = sum(1 for t in trial_results if t["verdict"] == "PASS")
        partial_trials = sum(1 for t in trial_results if t["verdict"] == "PARTIAL")
        hit_rate = (pass_trials + partial_trials * 0.5) / args.trials

        # Overall verdict: PASS if >50% of trials hit, else best trial result
        if hit_rate >= 0.5:
            overall = "PASS" if pass_trials == args.trials else "PARTIAL"
        else:
            overall = "MISS" if pass_trials == 0 and partial_trials == 0 else "FAIL"

        all_invoked = list(set(s for t in trial_results for s in t["invoked"]))

        results.append({
            "id": tc["id"],
            "prompt": prompt,
            "expected_skill": expected,
            "invoked_skills": all_invoked,
            "category": category,
            "priority": tc.get("priority", "medium"),
            "verdict": overall,
            "hit_rate": hit_rate,
            "trials": trial_results,
        })

    # Generate reports
    report_text = format_report(results, corpus, args.trials)
    print("\n" + report_text)

    # Save JSON report
    if args.output:
        report_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "corpus": args.corpus,
            "trials": args.trials,
            "results": results,
            "summary": {
                "total": len(results),
                "pass": sum(1 for r in results if r["verdict"] == "PASS"),
                "partial": sum(1 for r in results if r["verdict"] == "PARTIAL"),
                "miss": sum(1 for r in results if r["verdict"] == "MISS"),
                "fail": sum(1 for r in results if r["verdict"] == "FAIL"),
            },
        }
        with open(args.output, "w") as f:
            json.dump(report_data, f, indent=2)
        print(f"JSON report saved to {args.output}")
    else:
        # Auto-save to plans directory
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        auto_path = Path.home() / ".claude" / "plans" / f"route-test-report-{ts}.json"
        report_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "corpus": args.corpus,
            "trials": args.trials,
            "results": results,
            "summary": {
                "total": len(results),
                "pass": sum(1 for r in results if r["verdict"] == "PASS"),
                "partial": sum(1 for r in results if r["verdict"] == "PARTIAL"),
                "miss": sum(1 for r in results if r["verdict"] == "MISS"),
                "fail": sum(1 for r in results if r["verdict"] == "FAIL"),
            },
        }
        with open(auto_path, "w") as f:
            json.dump(report_data, f, indent=2)
        print(f"JSON report saved to {auto_path}")


if __name__ == "__main__":
    main()
