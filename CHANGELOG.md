# Changelog

## [0.2.0] - 2025-06-26

### Migration from v0.1.0

If you installed v0.1.0 (single `/SKILL-creator` command only), upgrade as follows:

1. **Automatic** — re-run `install.ps1` or `install.sh`. The scripts detect outdated
   pointers and overwrite them, then create the 4 new pointer files.
2. **Preview first** — run the migration script in dry-run mode, then apply:
   ```
   python scripts/migrate-v1.py          # preview changes
   python scripts/migrate-v1.py --apply  # write changes
   ```
3. Restart Cursor after migration to activate the new commands.

### Added
- `/SKILL-lint` command — audit skill files for structural issues, best-practice violations, and spec drift
- `/SKILL-fix` command — auto-repair skill files with logic-first fixing and diff confirmation
- `/SKILL-pythonGenerator` command — extract deterministic logic from skills into reusable Python CLI scripts
- `/SKILL-setup` command — install, update, configure, or uninstall the plugin from GitHub
- `config/defaults.json` — centralized configuration for agent models, lint rules, fix behavior, and extraction settings
- Linter agent (`agents/linter.md`) for rule-based skill auditing
- Lint rules reference (`references/lint-rules.md`)
- Bootstrap scripts for Windows (`bootstrap.ps1`) and macOS/Linux (`bootstrap.sh`)
- Install scripts (`install.ps1`, `install.sh`)

### Changed
- `/SKILL-creator` enhanced with improved orchestration and eval-driven workflow
- `plugin.json` updated to v0.2.0 with explicit registration of all 5 commands
- `README.md` rewritten with comprehensive documentation, installation instructions, and configuration guide

## [0.1.0] - 2025-05-01

### Added
- Initial release with `/SKILL-creator` command
- Eval-driven skill development lifecycle: intent capture, draft, test, grade, iterate, description optimize
- Grader, analyzer, and comparator agents
- Writing guide, eval workflow, and schemas references
- Benchmark aggregation and review generation scripts
