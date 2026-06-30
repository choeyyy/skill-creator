---
name: SKILL-fix
description: "Auto-repair Cursor Agent Skill files — fix logic issues first, then format enforcement, with diff confirmation."
---

Resolve which skill to fix, run the linter, dispatch fixes, and confirm with the user before applying.

**Scope resolution** (run as orchestrator):

1. User specifies skill name(s) or path(s) → collect ALL of them into an ordered list, locate each skill's `SKILL.md`
2. No specification → if a `SKILL.md` is open in the editor, target that file; otherwise ask the user which skill(s) to fix

**Fix procedure**:

1. **Lint** — read `agents/linter.md` (relative to this plugin's `skills/skill-creator/` directory) and run a lint check on the target skill to get the lint results JSON
2. **Classify** — from the lint results, separate issues into logic (structural) vs format (mechanical). If no issues are found, report "无问题，无需修复" and stop
3. **Fix** — read `agents/fixer.md` (relative to this plugin's `skills/skill-creator/` directory) and pass it the skill path and lint results JSON. The fixer agent returns proposed fixes with before/after diffs
4. **Confirm** — present the proposed fixes to the user using the report format from `references/fix-report-format.md` (relative to this plugin's `skills/skill-creator/` directory). Wait for explicit user confirmation before proceeding. If the user rejects, stop without applying changes
5. **Apply** — on user confirmation, apply the approved fixes to the skill file
6. **Validate** — re-run the linter on the fixed file. If issues remain and the current round is below `max_rounds` (from `config/defaults.json`), repeat from step 3. Otherwise present the final validation result

**Configuration** (from `config/defaults.json` → `fix`):

| Setting | Value | Effect |
|---------|-------|--------|
| `max_rounds` | 2 | At most 2 fix iterations |
| `require_confirmation` | true | Always show diff and wait for user approval |
| `auto_run_validate` | true | Re-run linter after applying fixes |

**Dispatch strategy**:

- **Single skill**: run the fix procedure inline (read `agents/fixer.md` and execute in this conversation) — benefits from conversational context with the user for confirmation
- **Multiple skills**: run the fix procedure for each skill **one at a time, in order** — complete the full lint → classify → fix → confirm → apply → validate cycle for skill N before moving to skill N+1. **You MUST process every skill in the list. Do not stop after the first one.**

**Multi-skill enforcement**: After completing all skills, output a summary table listing each skill, the issues fixed, and the final validation result.

**Output**: present all findings and fix proposals in Chinese using the report format defined in `references/fix-report-format.md`.
