# Eval Workflow — Cursor Task Subagent Protocol

Step-by-step procedure for running skill evaluations using Cursor's Task tool. Each iteration compares skill-assisted runs against a baseline.

---

## Step 1: Create Test Cases

If `evals/evals.json` doesn't exist, create it with 2–5 realistic test prompts. Each test case needs a concrete user prompt (casual phrasing — how real users talk), 2–4 verifiable expectations, and optional `files` for workspace scaffolding.

```json
{
  "skill_name": "my-skill",
  "evals": [
    {
      "id": "basic-usage",
      "prompt": "help me set up a new React component for the sidebar",
      "expected_output": "A React component file with proper structure",
      "files": ["src/App.tsx"],
      "expectations": [
        "Creates a new .tsx file in src/components/",
        "Uses functional component syntax",
        "Includes TypeScript interface for props"
      ]
    }
  ]
}
```

Save to `evals/evals.json`. See `references/schemas.md` for full schema.

---

## Step 2: Launch Parallel Eval Runs

For **each** test case, spawn exactly **two** Task subagents in the same turn:

### With-skill run

```
Task(
  subagent_type: "generalPurpose",
  run_in_background: true,
  description: "eval-with-{eval_id}",
  prompt: "Read and follow the skill at {path_to_SKILL.md}\n\n
           Then complete this task:\n{eval_prompt}\n\n
           Working directory: {workspace}/iteration-{N}/eval-{eval_id}/with_skill/
           Save all outputs to that directory."
)
```

### Without-skill run (baseline)

```
Task(
  subagent_type: "generalPurpose",
  run_in_background: true,
  description: "eval-without-{eval_id}",
  prompt: "Complete this task:\n{eval_prompt}\n\n
           Working directory: {workspace}/iteration-{N}/eval-{eval_id}/without_skill/
           Save all outputs to that directory."
)
```

### Parallelism rules

- Launch **all** 2×N subagents in a **single message** — maximizes parallel execution
- For 3 test cases = 6 Task calls in one turn
- Never wait for one eval before starting the next

### Output directory structure

```
iteration-1/
├── eval-basic-usage/
│   ├── with_skill/outputs/
│   └── without_skill/outputs/
├── eval-edge-case/
│   ├── with_skill/outputs/
│   └── without_skill/outputs/
```

---

## Step 3: Capture Timing

When each Task completes (via completion notification), record timing to `evals/timing/{eval_id}-{config}.json`:

```json
{
  "eval_id": "basic-usage",
  "config": "with_skill",
  "total_tokens": 12450,
  "duration_ms": 34200,
  "total_duration_seconds": 34.2,
  "timestamp": "2026-06-18T10:30:00Z"
}
```

Extract `total_tokens` and `duration_ms` from subagent completion metadata. Capture each run as it completes — don't wait for all.

---

## Step 4: Grade Results

After **all** eval runs complete, launch a grader subagent for each run:

```
Task(
  subagent_type: "generalPurpose",
  run_in_background: true,
  description: "grade-{eval_id}-{config}",
  prompt: "Read grader instructions at {workspace}/agents/grader.md\n\n
           Grade this eval run:\n
           - Eval definition: {eval entry with expectations}\n
           - Agent output: {path to outputs/}\n
           - Config: {with_skill | without_skill}\n\n
           Write results to: evals/grading/{eval_id}-{config}.json
           Use the grading.json schema from references/schemas.md."
)
```

Launch graders in parallel — one per run (2×N graders for N test cases). Each grader produces per-expectation pass/fail with evidence citations.

---

## Step 5: Aggregate Benchmark

After all grading completes, compute the benchmark summary.

**Option A — Script:** `python scripts/aggregate_benchmark.py evals/ --output benchmark.json`

**Option B — Inline:** Read all `evals/grading/*.json`, group by config, compute:
- `pass_rate` = total passed / total expectations
- `mean_time_ms` = average duration
- `delta` = with_skill − without_skill for each metric

Write to `benchmark.json` (schema in `references/schemas.md`).

### Interpreting results

| Delta pass_rate | Interpretation |
|:----------------|:---------------|
| > +0.15 | Skill provides clear value |
| +0.05 to +0.15 | Marginal — investigate which tests benefit |
| −0.05 to +0.05 | No significant effect — skill needs rework |
| < −0.05 | Skill is hurting — over-constraining the agent |

---

## Step 6: Present Results

Use Canvas (preferred) or formatted markdown. Include:
- Side-by-side pass rate comparison
- Per-test breakdown with expectation-level pass/fail
- Timing comparison (with_skill vs without_skill)
- Output samples for failed tests

### Markdown fallback

```markdown
## Benchmark — Iteration {N}
| Metric | With Skill | Without Skill | Delta |
|:-------|:-----------|:--------------|:------|
| Pass Rate | 85% | 60% | +25% |
| Avg Time | 34.2s | 28.1s | +6.1s |
```

---

## Step 7: Iterate

1. **Read feedback** — user comments on results
2. **Identify patterns** — systemic failures, not test-specific fixes
3. **Improve skill** — edit SKILL.md and references
4. **Bump iteration** — create `iteration-{N+1}/`
5. **Re-run** — return to Step 2 with the same test cases
6. **Update** `history.json` — track pass rates across versions

### Stopping criteria

- Pass rate > 90% AND delta over baseline > 15%
- Two consecutive iterations with < 2% improvement
- User is satisfied
- Five iterations completed (diminishing returns)
