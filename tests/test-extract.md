# Test: /SKILL-pythonGenerator

## Prerequisites

- skill-creator plugin installed (`/SKILL-setup` completed)
- Sample skills at `tests/sample-skills/extractable-pair/`
- Python installed (for running generated scripts)

## Test 1 — Detect shared patterns

1. Run `/SKILL-pythonGenerator` and specify both skills in `tests/sample-skills/extractable-pair/`
2. **Expected**:
   - Extractor agent identifies ≥1 candidate pattern shared across both skills
   - Pattern has ≥3 deterministic steps (matching `min_duplicate_steps: 3`)
   - Candidate presented with: pattern type, steps, source skills with line refs, proposed script name, CLI args, viability rating
3. **Failure**: No candidates detected despite shared logic

## Test 2 — Approve and generate script

1. Continue from Test 1 — approve a candidate for extraction
2. **Expected**:
   - Python script created in the first skill's `scripts/` directory
   - Script uses `argparse`, type hints, docstrings, `if __name__ == "__main__":`
   - Error handling writes to stderr
   - `requirements.txt` created if external deps needed
   - Affected skills updated with reference to the generated script
3. **Failure**: Script missing argparse or type hints; no skill update

## Test 3 — Decline extraction

1. Run `/SKILL-pythonGenerator` on the extractable pair
2. When candidates are shown, decline all
3. **Expected**: Agent reports no scripts generated and stops
4. **Failure**: Scripts generated despite declining

## Test 4 — No patterns found

1. Run `/SKILL-pythonGenerator` on `tests/sample-skills/good-skill.md` alone (single skill)
2. **Expected**: "No extractable patterns detected" — needs ≥2 skills
3. **Failure**: Agent fabricates patterns from a single skill

## Test 5 — Scope resolution

1. Close all editor tabs, run `/SKILL-pythonGenerator` with no args
2. **Expected**: Agent asks which skills to scan
3. **Failure**: Agent errors or scans random files

## Checklist

- [ ] `min_duplicate_skills` (2) and `min_duplicate_steps` (3) from config respected
- [ ] Generated script is standalone and runnable
- [ ] Skills updated to reference the generated script
- [ ] No extraction without user approval
