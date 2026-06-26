# Test: /SKILL-fix

## Prerequisites

- skill-creator plugin installed (`/SKILL-setup` completed)
- Sample skills available at `tests/sample-skills/`

## Test 1 — Fix a skill with known issues

1. Copy `tests/sample-skills/bad-template.md` to a temp location (avoid modifying the original)
2. Run `/SKILL-fix` targeting the copy
3. **Expected**:
   - Agent runs lint first, identifies failing dimensions
   - Classifies issues as logic vs format
   - Presents before/after diffs for proposed fixes
   - Waits for user confirmation before applying
4. **Failure**: Agent applies changes without showing diffs; skips confirmation

## Test 2 — Confirm and apply fixes

1. Continue from Test 1 — approve all proposed fixes
2. **Expected**:
   - Fixes applied to the file
   - Re-lint runs automatically (`auto_run_validate: true`)
   - Validation result shown (improved score)
3. **Failure**: No re-lint after apply; file unchanged despite approval

## Test 3 — Reject fixes

1. Copy `tests/sample-skills/bad-language.md` to a temp location
2. Run `/SKILL-fix` targeting the copy
3. When diffs are shown, reject all fixes
4. **Expected**: Agent stops without modifying the file. Reports "用户拒绝修复"
5. **Failure**: File is modified despite rejection

## Test 4 — Fix a passing skill

1. Run `/SKILL-fix` targeting `tests/sample-skills/good-skill.md`
2. **Expected**: Agent runs lint, finds no issues, reports "无问题，无需修复" and stops
3. **Failure**: Agent proposes unnecessary changes

## Test 5 — Multi-round fix

1. Copy `tests/sample-skills/bad-template.md` to a temp location
2. Run `/SKILL-fix`, approve fixes
3. **Expected**: If issues remain after round 1, agent iterates (up to `max_rounds: 2`). After round 2, stops regardless of remaining issues
4. **Failure**: Agent attempts more than 2 rounds

## Checklist

- [ ] Fix report uses Chinese format from `references/fix-report-format.md`
- [ ] Diffs are clear (before/after with context)
- [ ] Logic issues fixed before format issues
- [ ] `max_rounds` (2) respected
- [ ] `require_confirmation` (true) enforced — no silent changes
