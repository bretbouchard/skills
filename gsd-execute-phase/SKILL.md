# gsd:execute-phase

Execute all plans in a GSD phase with automatic metrics tracking.

## Purpose

Execute phase plans sequentially, tracking execution metrics for continuous improvement.

Collect metrics during execution:
- Execution time per task
- Success/failure outcomes
- Verification results
- Context usage
- Rework indicators

Post-execution:
- **AUTO-PROMPT: Offer to analyze metrics with phase-suggest**
- Suggest refinements if patterns detected
- Human approval required for all changes

## Usage

```
/gsd:execute-phase {N}
/gsd:execute-phase {N} --autonomous
```

## Post-Execution Auto-Prompt (MANDATORY)

After phase completes successfully, ALWAYS offer:

```markdown
## Phase {N} Complete ✅

Metrics saved to `.planning/phase-metrics/{N}/`

**Run refinement analysis?**
- `phase-suggest analyze {N}` - Detect patterns and suggest improvements

<options>
<option>Run analysis now</option>
<option>Skip for now</option>
</options>
```

This prompt ensures continuous improvement is integrated into the workflow.

## Metrics Integration

### Before Execution
1. Record start time for the phase
2. Initialize metrics collection
3. Load any previous metrics for this phase

### During Execution
For each task:
1. Use `ExecutionTimer` context manager or manual timing
2. Track task start time
3. Record task completion:
   - Execution time
   - Outcome (success/failure/partial)
   - Verification result
   - Context tokens used
   - Any errors

### After Execution
1. Calculate phase aggregate metrics
2. Offer to analyze patterns
3. Suggest refinements if applicable
4. **HUMAN APPRO REQUIRED** for any changes

5. Save metrics to `.planning/phase-metrics/{phase}/`

## Code Integration

```python
from lib.phase_metrics import (
    record_execution,
    start_task_timer,
    ExecutionTimer
)
from lib.phase_refiner import (
    analyze_phase,
    suggest_improvements
)

```

## Example: Task Timing

```python
# Using context manager
with start_task_timer("06", "01", "Create library") as timer:
    # Do work...
    # Timer automatically records on exit

# Manual recording
metric = record_execution(
    phase="06",
    plan="01",
    task="Create library",
    execution_time_seconds=342.5,
    outcome="success",
    verification_passed=True,
    context_tokens_used=45000
)
```

## Post-Execution Analysis
After phase completion, the agent should:

1. Analyze metrics:
```bash
./scripts/phase-suggest analyze 06
```

2. Review suggestions (if any):
```bash
./scripts/phase-suggest show 06
```

3. Approve suggestions if desired:
```bash
./scripts/phase-suggest approve ref-06-xxx
```

4. Apply approved changes
```bash
./scripts/phase-suggest apply ref-06-xxx
```

**CRITICAL: All changes require human approval. The system will NOT automatically modify plans.**

## Success Criteria
- [ ] Metrics tracked for all tasks
- [ ] Phase aggregate metrics calculated
- [ ] **Auto-prompt for phase-suggest analysis shown**
- [ ] Pattern analysis available
- [ ] Refinement suggestions generated
- [ ] Human approval gate enforced
- [ ] Version history maintained
- [ ] Rollback capability verified

## Files
- `.planning/phase-metrics/{phase}/{plan}-metrics.json` - Task metrics
- `.planning/phase-metrics/{phase}/refinements.json` - Refinement history
- `.planning/phase-metrics/aggregate.json` - Cross-phase patterns

## Dependencies
- `lib/phase_metrics.py` - Metrics tracking library
- `lib/phase_refiner.py` - Refinement suggestion engine
- `lib/phase_versioning.py` - Version control for rollback
- `scripts/phase-suggest` - CLI for refinement workflow
