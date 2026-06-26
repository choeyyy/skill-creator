---
name: SKILL-pythonGenerator
description: "Identify deterministic, repetitive logic across skills and extract into reusable Python CLI scripts."
---

Resolve which skills to scan, identify extractable patterns, and orchestrate script generation upon user approval.

**Scope resolution** (run as orchestrator):

1. User specifies skill name(s) or path(s) → scan those skills
2. User says "all" / "所有" → ask scope: project skills only / personal skills only / both
3. No specification → if a `SKILL.md` is open in the editor, scan that file and its sibling skills; otherwise ask the user which skills to scan

**Detection phase**:

1. Collect absolute paths for all in-scope SKILL.md files
2. Read `agents/extractor.md` (relative to this plugin's `skills/skill-creator/` directory)
3. Dispatch the extractor agent via the Task tool (subagent_type `generalPurpose`, model `claude-4.5-haiku-thinking`) with the collected skill paths and detection parameters:
   - `min_duplicate_skills`: 2 (or user-specified)
   - `min_duplicate_steps`: 3 (or user-specified)
4. Receive the candidate JSON from the extractor agent

**Presentation phase**:

1. If no candidates found → report "No extractable patterns detected" and stop
2. Present each candidate to the user in a readable format:
   - Pattern type and description
   - Steps involved
   - Skills where it appears (with line references)
   - Proposed script name, CLI args, and dependencies
   - Viability rating
3. Ask the user which candidates to extract (all / specific IDs / none)

**Generation phase** (only if user approves ≥1 candidate):

For each approved candidate, generate a Python CLI script:

1. Create the script in the first listed skill's `scripts/` directory (create directory if needed)
2. Script requirements:
   - Standalone CLI using `argparse`
   - Type hints on all function signatures
   - Docstrings for all public functions
   - Error handling with clear messages to stderr
   - `if __name__ == "__main__":` entry point
3. If external dependencies are needed, create or update `requirements.txt` in the same `scripts/` directory
4. Update the affected skills: add a note referencing the generated script as a replacement for the inline logic

**Output**: Present a summary report listing:
- Scripts generated (path, purpose, CLI usage)
- Skills updated (path, what was changed)
- Dependencies added (if any)
