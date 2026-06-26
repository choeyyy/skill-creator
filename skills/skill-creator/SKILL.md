---
name: skill-creator
description: >-
  Create, test, iterate, and audit Cursor Agent Skills with eval-driven development.
  Use for /SKILL-creator, /SKILL-lint, /SKILL-fix, /SKILL-pythonGenerator,
  skill creation, skill testing, skill evaluation, skill iteration, skill audit,
  description optimization, or when systematically building agent skills.
  Even if the user just says "make a skill", "new skill", "check my skill",
  or "lint", use this to guide them through the full lifecycle.
disable-model-invocation: true
---

# Skill Creator — Orchestration

Create, test, iterate, and audit Cursor Agent Skills. This skill orchestrates the full lifecycle: intent capture → draft → test → iterate → optimize → lint → fix → extract.

## 1. Lifecycle Detection & Routing

Detect where the user is and route to the correct phase. Check these signals in order:

### Command routing (takes priority)

```
IF user invoked /SKILL-lint  → §7 Lint Audit
IF user invoked /SKILL-fix   → §8 Auto-Fix
IF user invoked /SKILL-pythonGenerator → §9 Script Extraction
OTHERWISE → continue to lifecycle detection below
```

### Detection logic

```
workspace = skill-creator-workspace/   (or user-specified path)

IF workspace does not exist:
  → Phase: NEW — go to §2 Intent Capture

IF workspace/SKILL.md exists AND workspace/evals/ does not exist:
  → Phase: DRAFT — offer choices (see below)

IF workspace/evals/ exists AND workspace/benchmark.json exists:
  → Phase: TESTED — offer choices (see below)

IF workspace/evals/ exists AND workspace/benchmark.json does not exist:
  → Phase: TESTING_INCOMPLETE — resume test execution (§4)
```

### Routing for DRAFT phase

Ask the user (via AskQuestion if available, conversationally otherwise):

> Your skill draft exists at `{path}`. What would you like to do?
>
> 1. **Run tests** — define test cases and evaluate the skill
> 2. **Continue editing** — refine the current draft
> 3. **Start fresh** — archive current work and begin a new skill

- Option 1 → §4 Test Execution
- Option 2 → §3 Skill Drafting (edit mode)
- Option 3 → archive `workspace/` to `workspace.bak-{timestamp}/`, then §2

### Routing for TESTED phase

Show a brief results summary from `benchmark.json`, then ask:

> Benchmark results: **{pass_rate}%** pass rate ({with_skill} vs {without_skill} baseline).
>
> 1. **Iterate** — improve the skill based on test results
> 2. **Optimize description** — tune trigger accuracy
> 3. **Run tests again** — re-run with current skill
> 4. **Export** — finalize and copy skill to target location

- Option 1 → §5 Iteration
- Option 2 → §6 Description Optimization
- Option 3 → §4 Test Execution
- Option 4 → run §7 Lint Audit first; if lint passes, copy `workspace/SKILL.md` (and references/) to user's chosen location; if lint fails, show findings and offer §8 Auto-Fix before completing export

---

## 2. Intent Capture

Gather structured requirements before writing any skill content. This prevents wasted iterations from vague starting points.

### Required information

Collect these six items. Use AskQuestion with structured options when available; fall back to conversational questions otherwise.

**Q1 — Purpose & scope**
> What specific task should this skill help with?
> _(free text)_

**Q2 — Trigger scenarios**
> When should the agent use this skill? Pick all that apply:
> - Explicit command (e.g., `/my-skill`)
> - Keyword detection (e.g., user says "review", "deploy")
> - File type detection (e.g., working with `.pdf` files)
> - Always active (ambient)

**Q3 — Output format**
> What should the skill produce?
> - Structured file (code, config, report)
> - Chat response (explanation, analysis)
> - Side effects (run commands, create files)
> - Mixed

**Q4 — Domain knowledge**
> What specialized knowledge does the agent need that it wouldn't already have?
> _(free text — APIs, conventions, internal tools, etc.)_

**Q5 — Existing patterns**
> Are there examples of correct output or existing workflows to follow?
> - Yes → ask user to share or point to files
> - No

**Q6 — Storage location**
> Where should this skill live?
> - Personal (`~/.cursor/skills/`)
> - Project (`.cursor/skills/`)
> - Plugin (within a cursor-plugin)

### Capture complete

After collecting answers, summarize the intent back to the user in a structured block:

```
Skill Intent Summary:
  Name:      {derived-name}
  Purpose:   {Q1 summary}
  Triggers:  {Q2 choices}
  Output:    {Q3 choice}
  Domain:    {Q4 summary}
  Patterns:  {Q5 summary}
  Location:  {Q6 choice}
```

Ask the user to confirm or adjust before proceeding to §3.

---

## 3. Skill Drafting

Generate the SKILL.md and supporting files. Follow the create-skill structure (frontmatter + body + references) and apply writing-guide principles.

### 3.1 Create workspace

```
skill-creator-workspace/
├── SKILL.md
├── references/          # only if needed
│   └── *.md
└── scripts/             # only if needed
    └── *.py / *.sh
```

### 3.2 Write frontmatter

```yaml
---
name: {skill-name}
description: >-
  {Pushy description — see writing-guide.md §Description Optimization}
disable-model-invocation: {true unless ambient trigger}
---
```

Apply the pushy description technique: include explicit trigger keywords, "even if user doesn't mention X" phrasing, and both WHAT and WHEN. See `references/writing-guide.md` for full guidance on description crafting.

### 3.3 Write body

Follow these principles (detailed in `references/writing-guide.md`):

- **Imperative form**: "Read the file", not "You should read the file"
- **Explain why**: each non-obvious rule gets a brief reason, not bare MUST/NEVER
- **Concise**: the agent is smart — only add context it doesn't already have
- **Progressive disclosure**: essential instructions in body, detailed content in references/
- **Few-shot examples**: include 1-2 concrete examples for output-sensitive tasks
- **Templates**: provide output format templates when structure matters

### 3.4 Extract references

If the body exceeds ~400 lines, extract detailed sections into `references/` files. Keep references one level deep (linked directly from SKILL.md, no chains).

### 3.5 Bundle scripts

If the skill involves repeatable code patterns, bundle them in `scripts/` rather than expecting the agent to generate code each time. Scripts save tokens and improve consistency.

### 3.6 Self-check before presenting

Verify the draft against the `references/writing-guide.md` quick-reference checklist and these structural rules:
- [ ] Description includes trigger keywords and WHAT + WHEN (writing-guide §5)
- [ ] Body is under 500 lines (writing-guide §3)
- [ ] Imperative form throughout (writing-guide §1)
- [ ] Non-obvious rules have "why" explanations (writing-guide §2)
- [ ] References are one level deep
- [ ] No time-sensitive information
- [ ] Consistent terminology
- [ ] Output templates provided where structure matters (writing-guide §6)

After the manual checklist, run a lint pass (§7 Lint Audit) against the draft. If lint reports errors or warnings, fix them before presenting to the user. This prevents exporting a skill that would fail the lint-on-export gate.

Present the draft to the user and ask for feedback before proceeding.

---

## 4. Test Execution

Run parallel evaluations to measure skill effectiveness. See `references/eval-workflow.md` for full protocol and `references/schemas.md` for JSON schemas.

### 4.1 Define test cases

If `evals/evals.json` doesn't exist, help the user create it:

1. Propose 3-5 realistic test prompts based on the skill's purpose
2. Make prompts concrete — include file paths, personal context, casual phrasing, abbreviations (realistic user messages, not polished requests)
3. For each prompt, define 2-4 verifiable expectations (assertions the grader checks)
4. Present to user for confirmation, then save to `evals/evals.json`

Format per `references/schemas.md` — each test case has: `id`, `prompt`, `expected_output`, `files` (optional), `expectations[]`.

### 4.2 Launch parallel runs

For each test case, spawn **two** Task subagents simultaneously — one with the skill loaded, one without:

```
For each test_case in evals.json:
  Launch Task(subagent_type: "generalPurpose", run_in_background: true):
    prompt: "{test_case.prompt}"
    description: "eval-with-{test_case.id}"
    # Include skill content in the prompt context

  Launch Task(subagent_type: "generalPurpose", run_in_background: true):
    prompt: "{test_case.prompt}"
    description: "eval-without-{test_case.id}"
    # No skill content — baseline run
```

Launch all 2×N subagents in a **single turn** to maximize parallelism. Save each output to `evals/outputs/{test_case.id}/{with_skill|without_skill}.md`.

### 4.3 Capture timing

When each Task subagent completes (via completion notification), record timing data to `evals/timing.json`:

```json
{
  "test_id": "...",
  "config": "with_skill | without_skill",
  "duration_ms": 0,
  "timestamp": "ISO-8601"
}
```

### 4.4 Grade results

After all runs complete, launch a grader subagent for each output pair. The grader evaluates each expectation against the output and produces `evals/grading/{test_id}.json`. See `agents/grader.md` for the grader prompt.

### 4.5 Aggregate benchmark

After all grading completes, aggregate into `benchmark.json`:

```json
{
  "with_skill":    { "pass_rate": 0.0, "mean_time_ms": 0, "stddev_time_ms": 0 },
  "without_skill": { "pass_rate": 0.0, "mean_time_ms": 0, "stddev_time_ms": 0 },
  "delta":         { "pass_rate": 0.0, "time_ms": 0 },
  "test_count": 0,
  "timestamp": "ISO-8601"
}
```

Run `scripts/aggregate_benchmark.py evals/` to compute this, or calculate inline if the script isn't available.

### 4.6 Present results

Show results via Canvas (preferred) or formatted markdown. Include:
- Pass rate comparison (with vs without skill)
- Per-test breakdown with pass/fail per expectation
- Timing comparison
- Qualitative output samples for failed tests

After presenting, route to §1 (lifecycle detection) so the user can choose next steps.

---

## 5. Iteration

Improve the skill based on test results and user feedback. Each iteration produces a versioned snapshot.

### 5.1 Read feedback

Gather improvement signals from multiple sources:
1. **Benchmark data**: which tests failed? What expectations weren't met?
2. **User feedback**: inline comments, chat feedback on specific outputs
3. **Grader evidence**: citations from grading.json showing why expectations failed
4. **Timing data**: is the skill making things slower without quality gains?

### 5.2 Identify patterns

Look for generalizable patterns, not test-specific fixes:
- Multiple tests fail the same expectation type → structural skill issue
- Skill outputs are correct but formatted differently → add output template
- Baseline outperforms skill on some tests → skill is over-constraining
- Timing significantly worse → skill is too verbose, trim unnecessary context

### 5.3 Improve the skill

Apply changes to `workspace/SKILL.md` (and references if needed). For each change:
- Explain what changed and why
- Ensure changes generalize beyond the failing test cases (no overfitting)

### 5.4 Version snapshot

Save iteration history to `workspace/history.json`:

```json
{
  "versions": [
    {
      "version": 1,
      "timestamp": "ISO-8601",
      "pass_rate": 0.85,
      "changes": "Added output template for...",
      "parent": 0
    }
  ],
  "current_best": 1
}
```

### 5.5 Re-run tests

After improving, go to §4 Test Execution to validate. Use the same test cases for fair comparison.

### 5.6 Optional: Blind A/B comparison

If the user wants rigorous comparison between versions, launch a comparator subagent (see `agents/comparator.md`):

1. For each test case, present Output A (old version) and Output B (new version) in randomized order
2. Comparator scores both without knowing which is which
3. After scoring, reveal labels and report which version won
4. Launch an analyzer subagent (`agents/analyzer.md`) to explain why the winner won

---

## 6. Description Optimization

Tune the skill's frontmatter description for accurate triggering. A good description ensures the agent loads the skill when relevant and ignores it otherwise.

### 6.1 Generate trigger eval queries

Create 20 realistic queries split into two groups:

**Should-trigger (10 queries):**
- Direct invocations ("help me create a skill")
- Indirect references ("I need to make my agent better at X")
- Edge cases (abbreviations, misspellings, related terms)
- Partial matches ("how do I test my prompt?")

**Should-NOT-trigger (10 queries):**
- Related but different domains ("write a Python script")
- Similar keywords, different intent ("I have a skill issue with my mouse")
- Completely unrelated ("deploy to production")

Focus on edge cases and near-misses — those reveal description weaknesses.

### 6.2 Train/test split

Split the 20 queries into:
- **Train set** (14 queries): used to identify description failures and guide improvements
- **Test set** (6 queries): held out to measure real accuracy, never used for tuning

### 6.3 Evaluate current description

For each train-set query, assess: would the agent select this skill based on the current description?
- True positive: should-trigger and would trigger → correct
- False negative: should-trigger but wouldn't → description missing keywords
- False positive: shouldn't-trigger but would → description too broad
- True negative: shouldn't-trigger and wouldn't → correct

### 6.4 Iterate (up to 5 rounds)

For each round:
1. Analyze failures from the train set
2. Propose a revised description addressing the failures
3. Re-evaluate the train set with the new description
4. If train accuracy reaches 100% or no improvement for 2 rounds, stop

### 6.5 Select best description

Evaluate all candidate descriptions against the **test set** (not train set). Select the description with the highest test accuracy. Present before/after comparison:

```
Before: "{old description}"
  Train: {X}/14  Test: {Y}/6

After:  "{new description}"
  Train: {X}/14  Test: {Y}/6
```

Apply the winning description to `workspace/SKILL.md` frontmatter.

---

## 7. Lint Audit

See `commands/SKILL-lint.md` for scope resolution, dispatch strategy, and reporting logic. Dispatches to `agents/linter.md` (Haiku sub-agent).

---

## 8. Auto-Fix

See `commands/SKILL-fix.md` for entry points, fix procedure, and confirmation gate. Dispatches to `agents/fixer.md` (Haiku sub-agent).

---

## 9. Script Extraction

See `commands/SKILL-pythonGenerator.md` for scan scope, detection, proposal, and generation logic. Dispatches to `agents/extractor.md` (Haiku sub-agent).

---

## Reference Files

These files contain detailed protocols referenced throughout this skill. Read them on demand, not upfront.

| Reference | Contents |
|:----------|:---------|
| `references/writing-guide.md` | Prompt engineering techniques for skill authoring: imperative form, explain-why, pushy descriptions, progressive disclosure, few-shot patterns |
| `references/eval-workflow.md` | Full eval protocol: test case format, execution details, grading rubric, benchmark computation |
| `references/schemas.md` | JSON schemas for `evals.json`, `grading.json`, `benchmark.json`, `history.json`, `timing.json` |
| `references/lint-rules.md` | 9-dimension criteria definitions, scoring rubric, language rules, report template |
| `references/fix-report-format.md` | Fix operation report format (Chinese): findings, fixes, validation, remaining issues |
| `references/extraction-patterns.md` | Common extractable patterns catalog with detection heuristics |

## Agent Files

| Agent | Purpose |
|:------|:--------|
| `agents/tester.md` | Execute a single eval test case (with or without skill), capture transcript and outputs for grading |
| `agents/grader.md` | Evaluate test outputs against expectations, produce structured grading |
| `agents/analyzer.md` | Surface patterns and regressions from benchmark data |
| `agents/comparator.md` | Blind A/B comparison between skill versions |
| `agents/linter.md` | Audit a single skill for language discipline + 9-dimension template compliance |
| `agents/fixer.md` | Auto-repair skill issues — logic first, then format enforcement |
| `agents/extractor.md` | Detect extractable deterministic logic patterns across skills |

## Script Files

| Script | Purpose |
|:-------|:--------|
| `scripts/aggregate_benchmark.py` | Compute benchmark.json from grading results |
| `scripts/generate_review.py` | Generate HTML review of eval results |
