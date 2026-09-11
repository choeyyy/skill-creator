---
name: SKILL-creator
description: "Create, test, iterate, and lint Cursor Agent Skills — detects lifecycle stage, guides next step, and enforces quality on export."
---

## Host compatibility

Read [host capability mapping](../references/host-compatibility.md) before using tools. It governs host-specific tool names, model arguments, installation paths and unavailable capabilities throughout this workflow. Keep all task approval and evidence requirements.


Determine where the user is in the create/test/iterate lifecycle and guide them to the next step.

**Lifecycle detection**:
- No work-in-progress skill exists → start intent capture workflow
- A skill draft exists in workspace → ask whether to continue iterating, run tests, or start fresh
- Benchmark results exist → show results summary and offer to iterate or optimize description

**Lint-on-export**: When the user chooses "Export" (copy skill to target location), run §7 Lint Audit automatically before finalizing. If lint fails, show findings and offer §8 Auto-Fix before completing export. Never export a skill that hasn't passed lint.

Read and follow the complete instructions in `skills/skill-creator/SKILL.md` (relative to this plugin's root directory).
