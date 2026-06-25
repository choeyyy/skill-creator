# JSON Schemas — Skill Eval Data Structures

Schemas for all JSON files produced during the eval workflow. Each section shows a complete example followed by field descriptions.

---

## evals.json

Defines test cases for evaluating a skill. Created once, reused across iterations.

**Location:** `evals/evals.json`

```json
{
  "skill_name": "my-skill",
  "evals": [
    {
      "id": "basic-usage",
      "prompt": "help me set up a new React component for the sidebar",
      "expected_output": "A functional React component with TypeScript types",
      "files": ["src/App.tsx", "src/components/Header.tsx"],
      "expectations": [
        "Creates a new .tsx file in src/components/",
        "Uses functional component syntax",
        "Includes TypeScript interface for props"
      ]
    }
  ]
}
```

| Field | Type | Required | Description |
|:------|:-----|:---------|:------------|
| `skill_name` | string | yes | Matches the skill's frontmatter `name` |
| `evals[].id` | string | yes | Unique kebab-case identifier, used in directory names |
| `evals[].prompt` | string | yes | User message sent to the agent — casual, realistic phrasing |
| `evals[].expected_output` | string | yes | Human-readable correct output description (context for grader, not literal match) |
| `evals[].files` | string[] | no | Files to scaffold before running, paths relative to workspace |
| `evals[].expectations` | string[] | yes | Independently verifiable assertions the grader checks |

---

## grading.json

Produced by the grader subagent for each eval run.

**Location:** `evals/grading/{eval_id}-{config}.json`

```json
{
  "eval_id": "basic-usage",
  "config": "with_skill",
  "expectations": [
    {
      "text": "Creates a new .tsx file in src/components/",
      "passed": true,
      "evidence": "Agent created src/components/Sidebar.tsx (45 lines)"
    },
    {
      "text": "Includes TypeScript interface for props",
      "passed": false,
      "evidence": "No interface found; props typed inline as { items: string[] }"
    }
  ],
  "summary": {
    "passed": 3,
    "failed": 1,
    "total": 4,
    "pass_rate": 0.75
  },
  "execution_metrics": {
    "files_created": ["src/components/Sidebar.tsx"],
    "files_modified": ["src/App.tsx"],
    "commands_run": ["npx tsc --noEmit"],
    "errors_encountered": []
  },
  "timing": {
    "grading_duration_ms": 8500
  },
  "claims": [
    "Agent correctly identified component structure",
    "Missed the explicit interface requirement"
  ],
  "eval_feedback": "Skill should explicitly require a named interface for props"
}
```

| Field | Type | Required | Description |
|:------|:-----|:---------|:------------|
| `eval_id` | string | yes | Matches evals.json entry `id` |
| `config` | string | yes | `"with_skill"` or `"without_skill"` |
| `expectations[].text` | string | yes | Expectation text (copied from evals.json) |
| `expectations[].passed` | boolean | yes | Whether the output satisfies this expectation |
| `expectations[].evidence` | string | yes | Specific citation justifying the verdict |
| `summary.passed` | integer | yes | Expectations met |
| `summary.failed` | integer | yes | Expectations not met |
| `summary.total` | integer | yes | Total expectations |
| `summary.pass_rate` | float | yes | `passed / total`, range 0.0–1.0 |
| `execution_metrics` | object | no | What the agent did during the run |
| `claims` | string[] | no | High-level behavioral observations |
| `eval_feedback` | string | no | Suggested skill improvement (only when expectations fail) |

---

## benchmark.json

Aggregated results across all eval runs for one iteration.

**Location:** `benchmark.json` (workspace root)

```json
{
  "metadata": {
    "skill_name": "my-skill",
    "iteration": 2,
    "timestamp": "2026-06-18T11:45:00Z",
    "eval_count": 3
  },
  "runs": [
    {
      "eval_id": "basic-usage",
      "eval_name": "Basic component creation",
      "configuration": "with_skill",
      "run_number": 1,
      "result": {
        "pass_rate": 0.75,
        "passed": 3,
        "total": 4,
        "time_seconds": 34.2,
        "tokens": 12450
      }
    }
  ],
  "run_summary": {
    "with_skill": {
      "mean_pass_rate": 0.83,
      "mean_time_seconds": 36.5,
      "mean_tokens": 13200,
      "total_runs": 3
    },
    "without_skill": {
      "mean_pass_rate": 0.55,
      "mean_time_seconds": 27.8,
      "mean_tokens": 9100,
      "total_runs": 3
    },
    "delta": {
      "pass_rate": 0.28,
      "time_seconds": 8.7,
      "tokens": 4100
    }
  },
  "notes": [
    "Skill improves TypeScript type coverage significantly",
    "Time overhead acceptable given quality gains"
  ]
}
```

| Field | Type | Required | Description |
|:------|:-----|:---------|:------------|
| `metadata.skill_name` | string | yes | Skill under test |
| `metadata.iteration` | integer | yes | Iteration number (1-indexed) |
| `metadata.timestamp` | string | yes | ISO-8601 completion time |
| `metadata.eval_count` | integer | yes | Number of test cases evaluated |
| `runs[].eval_id` | string | yes | Matches evals.json `id` |
| `runs[].configuration` | string | yes | `"with_skill"` or `"without_skill"` |
| `runs[].run_number` | integer | yes | Run index (for repeated runs) |
| `runs[].result.pass_rate` | float | yes | 0.0–1.0 |
| `runs[].result.passed` | integer | yes | Expectations passed |
| `runs[].result.total` | integer | yes | Total expectations |
| `runs[].result.time_seconds` | float | yes | Wall-clock duration |
| `runs[].result.tokens` | integer | yes | Total tokens consumed |
| `run_summary.delta` | object | yes | `with_skill − without_skill` (positive = skill better) |
| `notes` | string[] | no | Human or agent observations |

---

## timing.json

Resource usage for a single eval run. Recorded when a Task subagent completes.

**Location:** `evals/timing/{eval_id}-{config}.json`

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

| Field | Type | Required | Description |
|:------|:-----|:---------|:------------|
| `eval_id` | string | yes | Matches evals.json `id` |
| `config` | string | yes | `"with_skill"` or `"without_skill"` |
| `total_tokens` | integer | yes | Tokens consumed (prompt + completion) |
| `duration_ms` | integer | yes | Wall-clock milliseconds |
| `total_duration_seconds` | float | yes | `duration_ms / 1000` — convenience field |
| `timestamp` | string | yes | ISO-8601 completion time |

---

## history.json

Tracks iteration history across the full eval lifecycle.

**Location:** `history.json` (workspace root)

```json
{
  "started_at": "2026-06-18T10:00:00Z",
  "skill_name": "my-skill",
  "current_best": 2,
  "iterations": [
    {
      "version": 1,
      "parent": 0,
      "expectation_pass_rate": 0.60,
      "grading_result": "evals/grading/iteration-1/",
      "changes": "Initial skill draft",
      "timestamp": "2026-06-18T10:30:00Z",
      "is_current_best": false
    },
    {
      "version": 2,
      "parent": 1,
      "expectation_pass_rate": 0.85,
      "grading_result": "evals/grading/iteration-2/",
      "changes": "Added output template, clarified TypeScript rules",
      "timestamp": "2026-06-18T11:15:00Z",
      "is_current_best": true
    }
  ]
}
```

| Field | Type | Required | Description |
|:------|:-----|:---------|:------------|
| `started_at` | string | yes | ISO-8601 timestamp of first iteration |
| `skill_name` | string | yes | Skill under development |
| `current_best` | integer | yes | Version number of highest-performing iteration |
| `iterations[].version` | integer | yes | 1-indexed version number |
| `iterations[].parent` | integer | yes | Parent version (`0` for initial draft) |
| `iterations[].expectation_pass_rate` | float | yes | Overall pass rate, 0.0–1.0 |
| `iterations[].grading_result` | string | yes | Path to grading output directory |
| `iterations[].changes` | string | no | What changed in this version |
| `iterations[].timestamp` | string | no | ISO-8601 completion time |
| `iterations[].is_current_best` | boolean | yes | `true` for exactly one entry — highest pass rate (ties: prefer later version) |
