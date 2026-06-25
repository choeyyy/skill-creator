# Skill Creator

Systematically create, test, and iterate on Cursor Agent Skills with eval-driven development and prompt engineering best practices.

## Installation

```bash
/add-plugin skill-creator
```

## Usage

Run `/SKILL-creator` in any Cursor chat. The command detects your current progress and guides you to the next step.

### Lifecycle stages

1. **Intent capture** — describe what the skill should do, target triggers, and expected behavior
2. **Draft** — generate SKILL.md with prompt engineering best practices (clear imperatives, role assignment, structured output, chain-of-thought)
3. **Test** — define test cases and run parallel with/without-skill evaluations via Task subagents
4. **Grade** — grader agent scores each test against assertions, producing structured results
5. **Iterate** — improve the skill based on benchmark data, blind A/B comparison, and user feedback
6. **Description optimize** — tune the skill description for trigger accuracy using train/test splits

### First run (no existing skill)

```
/SKILL-creator
→ starts intent capture
```

### Continuing work (draft exists)

```
/SKILL-creator
→ offers: continue iterating, run tests, or start fresh
```

### After tests (benchmark results exist)

```
/SKILL-creator
→ shows results summary, offers to iterate or optimize description
```

## Components

### Skills

| Skill | Description |
|:------|:------------|
| `skill-creator` | Main orchestrator — guides the full create/test/iterate lifecycle |

### Commands

| Command | Description |
|:--------|:------------|
| `SKILL-creator` | Single entry point for skill creation, testing, and iteration |

### Agents

| Agent | Description |
|:------|:------------|
| `grader` | Evaluate test outputs against assertions, produce structured `grading.json` |
| `analyzer` | Surface patterns and regressions from aggregated benchmark data |
| `comparator` | Blind A/B judging between skill versions |

### References

| Reference | Description |
|:----------|:------------|
| `writing-guide` | Prompt engineering techniques distilled for skill authoring |
| `eval-workflow` | Eval loop details: test case format, execution, grading, benchmark |
| `schemas` | JSON schemas for test cases, grading results, and benchmarks |

### Scripts

| Script | Description |
|:-------|:------------|
| `aggregate_benchmark.py` | Aggregate grading results into benchmark summary |
| `generate_review.py` | Generate HTML review of eval results |

## Plugin structure

```
cursor-plugins/skill-creator/
├── .cursor-plugin/
│   └── plugin.json
├── skills/
│   └── skill-creator/
│       ├── SKILL.md
│       ├── agents/
│       │   ├── grader.md
│       │   ├── analyzer.md
│       │   └── comparator.md
│       ├── references/
│       │   ├── writing-guide.md
│       │   ├── eval-workflow.md
│       │   └── schemas.md
│       └── scripts/
│           ├── aggregate_benchmark.py
│           └── generate_review.py
├── commands/
│   └── SKILL-creator.md
└── README.md
```

## License

MIT
