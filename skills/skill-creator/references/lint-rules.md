# Skill Quality Rules

Use this reference for static audit and aggregate scoring. Session-only procedures live in [session-audit.md](session-audit.md); load them only for session mode.

## Authority and Applicability

Use the user's task and applicable target instructions as the baseline. Distinguish host requirements, local conventions and optional design advice. Review the target's actual workflow and relevant resources before proposing a change.

The nine dimensions are questions about behavior, not a mandatory document template. Missing a persona phrase, XML tags, numbered headings, examples, a `<summary>` block, or a fixed section is not automatically a defect. Honor an explicit local formatting requirement, but label its source and do not present it as a universal platform requirement.

A supported optional metadata field is not invalid merely because a validator has an older allowlist. Preserve existing invocation policy and dependency metadata. Flag compatibility against the actual target host, not an assumed platform.

## Nine Dimensions

| ID | Dimension | Assess | Applicability and evidence |
|---|---|---|---|
| 1 | Purpose and Discovery | Does the name/description identify the capability and discriminate when it applies? Does the body preserve that purpose? | Always applicable. Reject catchall triggers that attract unrelated work; no required “You are” wording. |
| 2 | Context and Dependencies | Are necessary defaults, domain facts, inputs and tool requirements available? Do referenced resources exist and resolve? | Always applicable; a self-contained task can pass without a context section. A required unavailable tool without a feasible fallback is a defect. |
| 3 | Data and Instruction Boundaries | Can task instructions be distinguished from untrusted logs, documents, examples or generated data? | Applicable when the workflow consumes external content. XML is one option, not proof of safety or a required syntax. |
| 4 | Observable Outcome | Does the reader know what artifact, action or answer completes the task and how to recognize it? | Always applicable. Natural language is sufficient when a fixed schema is unnecessary. Distinguish proposed, applied, tested and published states where relevant. |
| 5 | Examples and Validation | Are non-obvious decisions illustrated or meaningfully validated where that changes reliability? Are added/changed scripts exercised? | `N/A` for a simple, self-contained operation that needs neither examples nor dedicated tests. Examples need not use XML. Test observable behavior, not matching headings or keywords. |
| 6 | Workflow and Proportionality | Are dependencies and failure/stopping conditions clear enough for the risk? Is process overhead justified? | Always applicable. Free-form work need not be forced into fixed steps, mandatory delegation or unnecessary approval loops. |
| 7 | Scope and Authorization | Does the workflow preserve the user's chosen product, target files, prior authorization and invocation settings? | Always applicable. Extra publishing, installation, config changes or unrelated audits need an actual basis. Retry limits should match the operation's risk. |
| 8 | Clarity and Progressive Disclosure | Is guidance concise, consistent and actionable? Are conditional references discoverable and loaded only when needed? | Always applicable. Preserve domain invariants; remove duplication and generic advice before adding more sections. A large line count is a review signal, not itself a failure. |
| 9 | Grounding and Uncertainty | Are evidence, claims and limits distinguished where factual accuracy matters? | Applicable to retrieval, audits, external state or verification claims. Allow `N/A` for purely creative work without such claims. Do not require a canned anti-hallucination phrase. |

## Language Policy

Resolve the target's explicit user preference and applicable rules first. The plugin's `config/defaults.json` contains legacy authoring defaults (`require_english`, example counts, line budget); these do not impose a policy on arbitrary third-party skills.

- `auto` (default): apply an actual language policy found for the target and cite it. If none applies, language is `N/A`; Chinese instructions alone are not a defect.
- `local-english` (explicitly requested, or required by target rules): English instruction prose, headings and structural identifiers; Chinese user-facing output, descriptions and example/output templates are allowed. Report violations only where this convention applies.
- Never translate a real filename, path, command argument, API value, quoted source or user-visible string simply because it contains Chinese. Preserve the user's intended output language.
- Under an applicable policy: `Pass` for zero violations, `Partial` for 1–3 non-structural violations, `Fail` for more than 3 or a violating instruction heading/field name. `Unknown` when the selected policy/source cannot be read. Use these thresholds everywhere; do not maintain a second scoring table in the agent.

## Scoring

For every dimension record `Pass`, `Partial`, `Fail`, `N/A`, or `Unknown` and a reason. `N/A` means irrelevant; `Unknown` means needed evidence is missing. Inspect references before declaring a criterion absent.

- `pass_count`: dimensions marked Pass. `applicable_count`: all dimensions except N/A, including Unknown. `total`: always 9.
- `score`: `pass_count/applicable_count`; if none apply use `N/A`. Never count N/A as Pass or Fail, or compare unlike denominators without stating scope.
- Static verdict: `Fail` if any applicable dimension or language check fails; otherwise `Unknown` if a required check is unknown; otherwise `Needs Improvement` if any is Partial; otherwise `Pass`. Language N/A is neutral. Any known failure remains visible even when other checks are unknown.
- Session verdict is independent: `Not assessed`, `Pass`, `Needs Improvement`, or `Unknown`, as defined in the session reference. Never fold it into a static numeric score.
- A blanket success message requires complete target coverage, static Pass for every target, and no unknown/violating requested session check. Without session mode say “静态检查通过；未评估运行效果”.

## Chinese Report Contract

Scale the report to the findings; use one overview row per target:

| Skill / 源路径 | 语言策略与判定 | 静态通过数/适用数 | 静态判定 | 会话判定 |
|---|---|---|---|---|
| {target} | {profile + verdict} | {score} | {static_verdict} | {session_verdict} |

For actionable findings include: check ID, source path/lines, observed text or behavior, applicable rule and its source, concrete impact, and smallest justified recommendation. List N/A reasons and unresolved evidence separately from defects. Label local convention findings as such.

For session mode add scope/provider/session IDs, fact-bundle path, historical baseline/version, coverage/warnings, and a fact-to-rule table from `session-audit.md`. Report raw facts separately from interpretation. Exclude the audit's own turns from the reviewed task and disclose that exclusion.

For multiple targets report missing/unreadable inputs explicitly. For fixes use [fix-report-format.md](fix-report-format.md); do not imply that a proposed diff or a historical trace proves successful repair.

## Design Basis

Adapted on 2026-09-11 from the user-selected Codex `skill-creator` at `~/.codex/skills/.system/skill-creator/SKILL.md`: scoped instructions, proportional workflows, precise discovery, progressive disclosure and behavioral validation. This reference contains the needed criteria; that machine-specific path is provenance, not a runtime dependency.
