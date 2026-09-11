---
name: SKILL-lint
description: "Audit Skill quality, scope, and references; optionally review session evidence against a specified Skill/SOP and fix supported defects."
---

## Host compatibility

Read [host capability mapping](../references/host-compatibility.md) before using tools. It governs host-specific tool names, model arguments, installation paths and unavailable capabilities throughout this workflow. Keep all task approval and evidence requirements.


# Skill Lint

You are the SKILL-lint orchestrator. Audit the requested skills, distinguish document defects from observed execution failures, and report in Chinese. A static pass does not prove runtime success.

## Scope and Mode

- Collect every user-specified name or path in order. Accept a skill directory, `SKILL.md`, or an explicit command/reference file. Resolve pointers to their real source and record both paths; detect cycles and unreadable targets. Do not audit a pointer as though it were the full skill.
- For “all”, use an already specified directory or scope. Ask once only if project/personal/both is unresolved. For an unspecified target, use an available active skill file; otherwise ask which skill to audit.
- **Static (default):** read the skill and reachable resources relevant to its behavior. Do not scan personal session stores.
- **Session evidence (optional):** when the user supplies transcripts or requests a session/SOP audit, read [session-audit.md](../skills/skill-creator/references/session-audit.md). `--session <path>` (repeatable), `--provider <auto|codex|claude|cursor|generic>`, `--baseline <path>` and `--output-dir <path>` are conversational arguments interpreted by this orchestrator, not an installed CLI. The target skill is the default baseline; additional baselines must be named by the user. Resolve missing session scope before reading logs; continue static checks while waiting.
- Read [lint-rules.md](../skills/skill-creator/references/lint-rules.md) for applicability and language policy. User instructions and applicable target rules take precedence over plugin conventions. `--language-profile local-english` explicitly selects this plugin's English-instructions/Chinese-output convention.

## Audit Workflow

1. Read [agents/linter.md](../skills/skill-creator/agents/linter.md) and audit all targets. For 1–3 targets, work inline; for larger batches, use bounded parallel subagents only when the host permits delegation. Otherwise audit sequentially. Use available host tools, not a required tool name or unavailable model. Give each worker only its target, relevant rules and scoped evidence.
2. If session mode applies, extract one scoped fact bundle and reuse it across relevant targets. Evaluate only applicable baseline clauses; do not assign unrelated session events to every skill.
3. Collect one result per requested target, including errors, skipped inputs and duplicate-pointer aliases. Missing/unreadable targets prevent a blanket pass; complete the others.
4. Present a Chinese overview and supported findings using the report contract in `lint-rules.md`. Show static and session verdicts separately, plus warnings and evidence limits. Do not turn `N/A`, `Not assessed`, or `Unknown` into a failure or a pass.

## Fix Workflow

- Audit-only requests are read-only. If actionable defects exist and fixing is not already authorized, prepare concrete proposed diffs using [agents/fixer.md](../skills/skill-creator/agents/fixer.md), then ask once whether to apply them. Do not ask “fix?” and then ask the same approval again.
- An explicit request to fix/update the named skills authorizes ordinary edits within that scope. Honor prior approval; ask only for a material scope change or an action still requiring permission. Rejection means stop editing.
- Fix only supported skill defects in the named targets and their necessary supporting resources. Do not rewrite a skill to compensate for a clear instruction that the runtime ignored, invent missing transcript content, or change unrelated settings, invocation policies, or external systems.
- Apply minimal changes, then re-audit the changed resources with the same baseline and language profile. Run relevant validators and any new/changed scripts. Historical logs remain historical evidence: re-linting the text does not establish that a runtime defect is resolved.
- Use `fix.max_rounds` from the plugin-root `config/defaults.json` (default 2). Count each apply-and-validate cycle; stop at the limit or when no justified change remains. Report unresolved items honestly.
- Use [fix-report-format.md](../skills/skill-creator/references/fix-report-format.md) to distinguish proposals, applied fixes and verified outcomes. Output the absolute modified paths and a per-target summary after completing all targets.

## Examples

<example>
<input>/SKILL-lint ./skills/rename-file</input>
<output>
Audit the source and referenced helper. A clear, short workflow needs no persona phrase or XML example solely to earn a score. Session status is Not assessed; no log store is scanned.
</output>
</example>

<example>
<input>/SKILL-lint ./skills/deploy --session ./exports/run.jsonl --provider codex</input>
<output>
Read the deploy skill as baseline, then the explicit transcript. Link an observed repeated approval request to the earlier human authorization and applicable clause. If the transcript starts mid-task, report the missing context instead of concluding that no authorization existed. Separate a defective rule from failure to follow a correct rule.
</output>
</example>

<example>
<input>/SKILL-lint 修复 skill-a skill-b skill-c skill-d</input>
<output>
Audit all four targets, apply supported fixes within the existing authorization, and validate. Each target appears in the final table, including any unreadable file. Use sequential execution if delegation is unavailable.
</output>
</example>
