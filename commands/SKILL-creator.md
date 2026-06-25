---
name: SKILL-creator
description: "Create, test, and iterate on Cursor Agent Skills — detects lifecycle stage and guides next step."
---

Determine where the user is in the create/test/iterate lifecycle and guide them to the next step.

**Lifecycle detection**:
- No work-in-progress skill exists → start intent capture workflow
- A skill draft exists in workspace → ask whether to continue iterating, run tests, or start fresh
- Benchmark results exist → show results summary and offer to iterate or optimize description

Read and follow the complete instructions in `skills/skill-creator/SKILL.md` (relative to this plugin's root directory).
