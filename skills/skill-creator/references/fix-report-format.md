# Fix Report Format

Used by the integrated `/SKILL-lint` fix workflow. Scale detail to the change; report in Chinese.

## Proposed Changes

Identify the target, applicable baseline/language policy, issue IDs and current round (`fix.max_rounds`, default 2). Show only actionable defects; list evidence gaps and execution deviations separately.

| 目标 | 静态判定 | 通过数/适用数 | 会话判定 | 可修复缺陷 |
|---|---|---|---|---|
| {absolute path} | {static_verdict} | {score} | {session_verdict} | {count} |

For each proposal show:

- Finding ID, source path and original lines, applicable rule and concrete impact.
- Exact before/after diff; logic changes before format changes.
- Intended behavior and the observable verification check.
- Any skipped item and the specific reason.

Use “拟修改” for proposals. If the task already authorizes the edits, proceed within scope. Otherwise request approval once after presenting the concrete diff; never treat a proposal as an applied fix.

## Applied Changes and Validation

After writing, report absolute modified paths and verified write results. Derive applied counts from successful edits, not from the fixer's proposal count. Re-run relevant lint/validators; execute new or changed scripts. Report actual results and limits.

| 检查 | 修改前 | 修改后 | 验证依据 |
|---|---|---|---|
| 静态质量 | {before score/verdict} | {after score/verdict} | {source / validator result} |
| 会话行为 | {historical observation} | {new outcome or 未重跑} | {fresh evidence or limitation} |

`template_check.score` already includes the applicable denominator; do not append `/9`. Exclude N/A from scored dimensions. No historical session failure becomes a runtime pass because its skill text was edited.

Finish with per-target found/proposed/applied/skipped counts, rounds used and remaining issues. If a write or validator fails, retain that failure. If no warranted changes remain, say so without inventing repairs. Stop at the configured round limit.
