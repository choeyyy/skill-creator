# Eval Workflow Protocol

Complete protocol for skill evaluation: test case design, parallel execution, grading, and benchmark computation.

## Overview

The eval workflow measures skill effectiveness by running identical prompts with and without the skill loaded, then grading the outputs against predefined expectations.

## Test Case Format

Each test case in `evals/evals.json`:

```json
{
  "id": "unique-test-id",
  "prompt": "Realistic user message",
  "files": ["optional/context/files.md"],
  "expectations": [
    {
      "id": "exp-1",
      "description": "What the output must contain or demonstrate",
      "type": "contains | format | behavior | absence"
    }
  ]
}
```

## Execution Protocol

1. For each test case, launch two parallel subagents (with-skill and without-skill)
2. Capture full output transcripts to `evals/outputs/{test_id}/`
3. Record timing data to `evals/timing.json`
4. After all runs complete, launch grader agents for each output pair

## Grading Rubric

- **PASS**: Expectation clearly met with evidence in output
- **FAIL**: Expectation not met or contradicted by output
- **PARTIAL**: Expectation partially met (counts as 0.5 in pass rate)

## Benchmark Computation

Aggregate all grading results into `benchmark.json` with pass rates, timing stats, and delta between with/without skill.

## TODO: Full implementation pending

Detailed execution error handling, retry logic, timeout configuration, and advanced grading criteria (weighted expectations, partial credit scales) to be added in a future iteration.
