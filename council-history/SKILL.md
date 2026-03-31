# Council Review History Skill

Track and learn from past Council of Ricks reviews with performance scoring integration.

## Purpose
Maintain searchable history of all Council of Ricks reviews to learn from past findings, track patterns, and identify top-performing specialists.

## Instructions

**Step 1: Initialize History and Scoring**
```bash
# Ensure directories exist
mkdir -p ~/.claude/telemetry/council-history
mkdir -p ~/.claude/.planning/council-performance/history

```

**Step 2: Load Context**
- Read `.planning/council-performance/scores.json` for specialist rankings
- Check review history in `~/.claude/telemetry/council-history/`
- Load current project context if available

**Step 3: Search and Filter History**
Support filters:
- `--last N` - Show last N reviews (default: 10)
- `--by-project NAME` - Filter by project
- `--by-severity LEVEL` - Filter by severity (SLC, Critical, High, Medium, Low)
- `--by-specialist NAME` - Filter by specialist agent
- `--mode TYPE` - Filter by mode (standard, all-hands)
- `--decision TYPE` - Filter by decision (approve, reject)
- `--since DATE` - Reviews since date (YYYY-MM-DD)
- `--with-scores` - Include performance scores in output

- `--export` - Export to markdown file

**Step 4: Generate History Report with Scores**
```
================================================================================
 Council of Ricks - Review History with Performance Scores
================================================================================

## Summary Statistics

| Metric            | Count  |
|-------------------|--------|
| Total Reviews     | {total}|
| Standard Mode     | {std}  |
| All Hands Mode    | {ah}   |
| Approved          | {appr} |
| Rejected          | {rej}  |
| Approval Rate     | {rate}%|

---

## Specialist Performance Scores

| Specialist        | Reviews | Score  | Issues Found | FP Rate |
|-------------------|--------|--------|--------------|--------|
| security-rick     | {n}     | {0.92} | {n}          | 5%     |
| performance-rick  | {n}     | {0.88} | {n}          | 8%     |
| dsp-rick          | {n}     | {0.85} | {n}          | 3%     |
| ...               | ...    | ...    | ...          | ...    |

---

## Recent Reviews

{for each review:}

### [{date}] {project} - {mode}
**Decision**: {APPROVED / REJECTED}
**Specialists**: {list of specialists with scores}
**Issues Found**: {total} ({critical} critical, {high} high, {med} medium)

**Specialist Scores**:
- security-rick: [0.92] (ranked #1 for security)
- performance-rick: [0.88] (ranked #2 for performance)

**Key Findings**:
- {issue_1}
- {issue_2}
- {issue_3}

**File**: `{review_file}`

---

## Top Issues by Frequency

| Issue Type       | Count | Trend    |
|------------------|-------|----------|
| SLC Violations   | {n}   | {up/down/flat}  |
| Security Issues  | {n}   | {up/down/flat}  |
| Performance      | {n}   | {up/down/flat}  |
| Code Quality     | {n}   | {up/down/flat}  |

---

## Insights from Review History

{Based on patterns detected:}

1. **Recurring Issues**: {issue} appears in {n}% of reviews
   -> Consider adding to project lint rules

2. **Specialist Expertise**: {specialist} (score: {score}) consistently finds {category} issues
   -> Prioritize this specialist for {category}-related changes

3. **Improvement Trend**: Approval rate {increased/decreased} by {n}%
   -> Code quality is {improving/declining}

---

## Advisory Score Recommendations

Based on historical performance, consider these specialists for your next review:
{domain}: {top specialists with scores}

NOTE: Scores are ADVISORY only. Human judgment always overrides.
Selection should still consider task context first.
```

**Step 5: Record Review Outcome**
After each Council review:
1. Load the scoring library: `from lib.council_scorer import CouncilScorer`
2. For each specialist that participated:
   - Record their review outcome
   - Update their score based on issues found
3. Save updated scores to `.planning/council-performance/scores.json`

Example:
```python
from lib.council_scorer import CouncilScorer
from lib.review_tracker import ReviewTracker

# After review completes
scorer = CouncilScorer()
tracker = ReviewTracker()

# Record the review
review_id = tracker.create_review(
    specialists=["security-rick", "performance-rick"],
    issues=[
        {"id": 1, "severity": "high", "specialist": "security-rick", "description": "SQL injection risk"},
        {"id": 2, "severity": "medium", "specialist": "performance-rick", "description": "Slow query"}
    ]
)

# After issues are addressed, record outcomes
tracker.record_outcome(review_id, 1, "valid")  # SQL injection was real
tracker.record_outcome(review_id, 2, "false_positive")  # Slow query was acceptable

# Update specialist scores
for issue in review["issues"]:
    scorer.score_review(
        issue["specialist"],
        review,
        issue["outcome"]
    )
```
**Step 6: Get Specialist Recommendations**
When planning a Council review:
```bash
# For a given domain, get ranked specialists
scripts/council-score rank security

# Output:
1. security-rick [0.92] (top ranked)
2. red-team-rick [0.87]
3. build-rick [0.75]
```
**IMPORTANT**: These are recommendations only. You should still:
- Consider task context
- Consider specialist availability
- Use human judgment to final selection
```

## Performance Scoring Integration
The scoring system is integrated via:
- `lib/council_scorer.py` - Main scoring engine
- `lib/review_tracker.py` - Review outcome tracking
- `.planning/council-performance/` - Score storage

### Scoring Factors
| Factor | Weight | Impact |
|--------|--------|--------|
| Issue Detection | +0.3 max | High detection = higher score |
| False Positives | -0.15 max | High FP = lower score |
| Actionability | +0.15 max | Actionable feedback = higher score |

**Score Range**: 0.1 to 1.0 (neutral = 0.5)

### Recording Outcomes
When recording review outcomes:
1. `valid` - Issue was real and addressed (+0.1 to score)
2. `false_positive` - Issue was not real (-0.05 to score)
3. `actionable` - Feedback led to improvement (+0.05 to score)
4. `ignored` - Feedback not acted upon (no change)

```

## Examples
Show history with scores:
```bash
/council-history --last 5 --with-scores
```

Get top specialists for security domain:
```bash
/council-history --by-specialist security-rick --with-scores
```

Export history for analysis:
```bash
/council-history --export > review-history.md
```
