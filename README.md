# Skill Creator

Create, lint, fix, and extract reusable Python scripts from Cursor Agent Skills. Eval-driven development with prompt engineering best practices.

## Codex installation

From this repository, run:

```text
python scripts/install_codex.py
```

This installs `$skill-lint` into `$CODEX_HOME/skills/skill-lint` (or `~/.codex/skills/skill-lint` when unset). It generates a self-contained copy of the canonical lint command, its five supporting documents and configuration, with Codex-compatible metadata and relative links. Start a new Codex task to discover it. Examples:

```text
$skill-lint <skill-path>
$skill-lint <skill-path> --session <transcript-path> --provider codex
```

To refresh the installed copy after pulling a newer version, run the same script. Identical files are left untouched; differing files require reviewing local edits and passing `--overwrite`. `--destination <directory>` supports a different installation directory. The optional session parser is not installed automatically. Cursor keeps its existing `/SKILL-lint` entry.

## Prerequisites

- [Cursor](https://cursor.sh/) IDE with Agent mode enabled
- Git
- Python 3.10+ (for benchmark scripts and Python extraction)

## Installation

### Windows (PowerShell)

```powershell
irm https://raw.githubusercontent.com/choeyyy/skill-creator/main/bootstrap.ps1 | iex
```

### macOS / Linux

```bash
curl -fsSL https://raw.githubusercontent.com/choeyyy/skill-creator/main/bootstrap.sh | bash
```

The bootstrap script clones the plugin into your Cursor plugins directory and runs initial setup.

### Manual installation

```bash
git clone https://github.com/choeyyy/skill-creator.git
```

Then run `/SKILL-setup` in Cursor to complete configuration.

## Commands

| Command | Description |
|:--------|:------------|
| `/SKILL-creator` | Create, test, and iterate on skills with eval-driven development |
| `/SKILL-lint` | Audit Skill quality, scope, and references; optionally review session evidence against a specified Skill/SOP and fix supported defects. |
| `/SKILL-fix` | Legacy disabled entry; use the integrated `/SKILL-lint` fix flow |
| `/SKILL-pythonGenerator` | Extract deterministic, repetitive logic into reusable Python CLI scripts |
| `/SKILL-setup` | Install, update, configure, or uninstall the plugin |

### SKILL-creator lifecycle

1. **Intent capture** — describe what the skill should do, target triggers, and expected behavior
2. **Draft** — generate SKILL.md with prompt engineering best practices
3. **Test** — define test cases and run parallel with/without-skill evaluations via Task subagents
4. **Grade** — grader agent scores each test against assertions
5. **Iterate** — improve the skill based on benchmark data, blind A/B comparison, and user feedback
6. **Description optimize** — tune the skill description for trigger accuracy

### SKILL-lint workflow

Run `/SKILL-lint <skill-path>` for nine applicability-aware quality checks. N/A is excluded from the score; language follows the target's actual rules (`--language-profile local-english` explicitly selects the local convention). Useful concise skills do not need persona/XML/example boilerplate merely to pass. Findings cite source lines and applicable rules.

Use `/SKILL-lint <skill-path> --session <transcript-path> --provider codex` for optional evidence review; the target is the baseline unless `--baseline <path>` adds another named Skill/SOP. These arguments are interpreted by the agent. The optional [upstream parser](https://github.com/patrickleehua/easily-skills/tree/78a5915750756c4851f6687ee50046348ace2810/cli-session-log-audit) supports Codex, Claude Code, Cursor agent transcripts and explicit generic exports; static lint has no parser dependency. Preserve original source references, human-input attribution and missing-history warnings. Report skill defects, execution deviations and unresolved evidence separately.

Repair is integrated: an audit-only request produces findings and concrete proposed diffs for approval; an explicit scoped fix request already authorizes ordinary edits. Re-lint the result and distinguish applied changes from runtime validation. See [lint rules](skills/skill-creator/references/lint-rules.md) and [session evidence](skills/skill-creator/references/session-audit.md).

### SKILL-pythonGenerator

Scans skills for deterministic, repetitive logic (aggregation, validation, formatting) and extracts it into standalone Python CLI scripts under `scripts/`.

## Configuration

Plugin defaults are stored in `config/defaults.json`. The `lint_rules` fields below are legacy authoring conventions, not universal audit failures; audit applicability and policy are defined in `skills/skill-creator/references/lint-rules.md`:

```json
{
  "agents": {
    "orchestrator": "sonnet",
    "linter": "haiku",
    "tester": "haiku",
    "extractor": "haiku"
  },
  "lint_rules": {
    "max_lines": 500,
    "require_english": true,
    "require_chinese_output": true,
    "require_examples": 1,
    "require_edge_cases": true
  },
  "fix": {
    "max_rounds": 2,
    "require_confirmation": true,
    "auto_run_validate": true
  },
  "extract": {
    "enabled": true,
    "min_duplicate_skills": 2,
    "min_duplicate_steps": 3
  }
}
```

Edit this file to customize agent model assignments, lint thresholds, and extraction behavior.

## Upgrading from v0.1.0

If you previously installed v0.1.0, re-running the install script (`install.ps1` / `install.sh`) will automatically detect the old single-pointer layout and create the 4 new skill pointers.

To preview what will change before writing:

```bash
python scripts/migrate-v1.py          # dry-run
python scripts/migrate-v1.py --apply  # write changes
```

## Upgrade

Re-run the bootstrap script to pull the latest version:

### Windows

```powershell
irm https://raw.githubusercontent.com/choeyyy/skill-creator/main/bootstrap.ps1 | iex
```

### macOS / Linux

```bash
curl -fsSL https://raw.githubusercontent.com/choeyyy/skill-creator/main/bootstrap.sh | bash
```

Or run `/SKILL-setup` and select the update option.

## Plugin structure

```
skill-creator/
├── .cursor-plugin/
│   └── plugin.json
├── bootstrap.ps1
├── bootstrap.sh
├── install.ps1
├── install.sh
├── CHANGELOG.md
├── README.md
├── config/
│   └── defaults.json
├── setup/
│   └── SKILL.md
├── commands/
│   ├── SKILL-creator.md
│   ├── SKILL-lint.md
│   ├── SKILL-fix.md
│   └── SKILL-pythonGenerator.md
├── skills/
│   └── skill-creator/
│       ├── SKILL.md
│       ├── agents/
│       │   ├── linter.md
│       │   ├── fixer.md
│       │   ├── extractor.md
│       │   ├── tester.md
│       │   ├── grader.md
│       │   ├── analyzer.md
│       │   └── comparator.md
│       └── references/
│           ├── writing-guide.md
│           ├── lint-rules.md
│           ├── fix-report-format.md
│           ├── extraction-patterns.md
│           ├── eval-workflow.md
│           ├── schemas.md
│           └── setup-checklist.md
├── scripts/
│   ├── migrate-v1.py
│   ├── aggregate_benchmark.py
│   └── generate_review.py
└── tests/
    ├── test-lint.md
    ├── test-fix.md
    ├── test-extract.md
    ├── test-setup.md
    ├── test-creator.md
    └── sample-skills/
        ├── good-skill.md
        ├── bad-language.md
        ├── bad-template.md
        └── extractable-pair/
            ├── skill-deploy-staging.md
            └── skill-deploy-production.md
```

## License

MIT
