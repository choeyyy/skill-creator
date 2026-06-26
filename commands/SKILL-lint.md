---
name: SKILL-lint
description: "Audit Cursor Agent Skill files for structural issues, best-practice violations, and spec drift."
---

Resolve which skills to audit, then route to the linter agent.

**Scope resolution** (run as orchestrator):

1. User specifies skill name(s) → locate each skill's `SKILL.md` and audit those
2. User says "all" / "所有" → ask scope: project skills only / personal skills only / both
3. No specification → if a `SKILL.md` is open in the editor, audit that file; otherwise ask the user which skills to audit

**Dispatch strategy**:

- **≤ 3 skills**: audit inline — read `agents/linter.md` (relative to this plugin's `skills/skill-creator/` directory) and run the checks sequentially in this conversation
- **> 3 skills**: dispatch one sub-agent per skill via the Task tool (subagent_type `generalPurpose`), each instructed to follow `agents/linter.md` against its assigned skill file; collect results and present a merged report

**Output**: present findings in Chinese using the report format defined in `agents/linter.md`.
