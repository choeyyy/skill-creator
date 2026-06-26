# Test: /SKILL-lint

## Prerequisites

- skill-creator plugin installed (`/SKILL-setup` completed)
- Sample skills available at `tests/sample-skills/` in the plugin directory

## Test 1 — Lint a passing skill

1. Open `tests/sample-skills/good-skill.md` in the editor
2. Run `/SKILL-lint`
3. **Expected**: Agent detects the open file, runs audit, reports all 9 dimensions Pass + language Pass. Verdict: 通过
4. **Failure**: Any dimension scored Partial or Fail; language violations reported

## Test 2 — Lint a skill with language violations

1. Run `/SKILL-lint` and specify `tests/sample-skills/bad-language.md`
2. **Expected**: Language discipline scored Partial or Fail; report lists specific violations with line numbers and shows Chinese text found in English-required elements
3. **Failure**: Language check reported as Pass

## Test 3 — Lint a skill with template gaps

1. Run `/SKILL-lint` and specify `tests/sample-skills/bad-template.md`
2. **Expected**: Multiple dimensions scored Fail (at least Role Assignment, Examples, Constraints). Overall verdict: 不合格
3. **Failure**: Verdict is 通过 or 需改进

## Test 4 — Batch lint (>3 skills)

1. Run `/SKILL-lint` and say "all" targeting `tests/sample-skills/`
2. **Expected**: Agent dispatches sub-agents (one per skill), collects results, presents merged summary table covering all sample skills
3. **Failure**: Agent audits inline instead of dispatching sub-agents; results missing for any skill

## Test 5 — No skill specified, no file open

1. Close all editor tabs
2. Run `/SKILL-lint`
3. **Expected**: Agent asks which skills to audit
4. **Failure**: Agent errors out or picks a random file

## Checklist

- [ ] Report is in Chinese using the template from `references/lint-rules.md`
- [ ] Each finding includes line numbers
- [ ] Aggregate scoring matches the rubric (Pass=2, Partial=1, Fail=0)
- [ ] Agent suggests `/SKILL-fix` for skills scoring below Pass
