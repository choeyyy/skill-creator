# Test: /SKILL-creator (enhanced)

## Prerequisites

- skill-creator plugin installed (`/SKILL-setup` completed)
- No existing `skill-creator-workspace/` in the current project (for Test 1)

## Test 1 — New skill (intent capture → draft)

1. Delete `skill-creator-workspace/` if it exists
2. Run `/SKILL-creator`
3. **Expected**: Detects NEW phase, begins intent capture asking Q1-Q6 (Purpose, Triggers, Output, Domain, Patterns, Location). After all answers collected, shows "Skill Intent Summary" and asks confirmation
4. After confirming, **Expected**: Generates `skill-creator-workspace/SKILL.md` with frontmatter + body following writing-guide principles. Runs self-check (§3.6) and lint before presenting
5. **Failure**: Skips any Q1-Q6 question; no summary shown; draft not lint-checked

## Test 2 — Existing draft (DRAFT phase routing)

1. Ensure `skill-creator-workspace/SKILL.md` exists but `evals/` does not
2. Run `/SKILL-creator`
3. **Expected**: Detects DRAFT phase, offers 3 options: Run tests / Continue editing / Start fresh
4. **Failure**: Starts intent capture again instead of detecting existing draft

## Test 3 — Test results exist (TESTED phase routing)

1. Ensure `skill-creator-workspace/benchmark.json` exists
2. Run `/SKILL-creator`
3. **Expected**: Detects TESTED phase, shows pass rate summary from benchmark.json, offers 4 options: Iterate / Optimize description / Re-run tests / Export
4. **Failure**: Ignores benchmark data; doesn't show results summary

## Test 4 — Export with lint gate

1. From TESTED phase, choose "Export"
2. **Expected**: Runs lint audit first. If lint passes, copies skill to user's chosen location. If lint fails, shows findings and offers `/SKILL-fix` before completing export
3. **Failure**: Exports without running lint; exports despite lint failure

## Test 5 — Start fresh (archive)

1. From DRAFT phase, choose "Start fresh"
2. **Expected**: Archives current `skill-creator-workspace/` to `skill-creator-workspace.bak-{timestamp}/`, then restarts intent capture
3. **Failure**: Deletes workspace without archiving; archive has wrong naming

## Checklist

- [ ] All lifecycle phases detected correctly (NEW → DRAFT → TESTED)
- [ ] Intent capture collects all 6 required items
- [ ] Draft follows writing-guide principles (imperative, pushy description, etc.)
- [ ] Lint-on-export gate enforced — never exports without passing lint
- [ ] Archive uses `.bak-{timestamp}` naming
