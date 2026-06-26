# Writing Guide — Skill Authoring Best Practices

Practical principles for writing effective SKILL.md files. Derived from prompt engineering fundamentals, adapted for Cursor Agent Skills.

---

## 1. Imperative Form

Write instructions as direct commands, not suggestions.

```
# Good
Read the config file. Extract the API key. Validate the format.

# Bad
You should read the config file. Then you would extract the API key.
```

Why: imperative form is shorter, unambiguous, and matches how agents process instructions.

---

## 2. Explain-Why Pattern

Non-obvious rules need a brief reason. Bare MUST/NEVER without context invites the agent to misapply or ignore them.

```
# Good
Keep references one level deep — chained references cause context loss
  when the agent navigates multiple hops.

# Bad
References MUST be one level deep.
```

Obvious rules (e.g., "write valid JSON") don't need justification. Reserve explanations for constraints the agent can't infer from general knowledge.

---

## 3. Progressive Disclosure

Structure information in layers:

| Layer | Contains | Guideline |
|:------|:---------|:----------|
| **Description** (frontmatter) | Trigger keywords + WHAT + WHEN | ≤ 3 lines |
| **Body** (SKILL.md) | Essential workflow, decision logic, constraints | ≤ 500 lines |
| **References** (`references/`) | Detailed schemas, examples, lookup tables | Read on demand |

Body should be self-sufficient for the common case. References handle edge cases, detailed formats, and domain data the agent shouldn't memorize.

---

## 4. Few-Shot Examples

Include 1-2 concrete input/output examples for tasks where output format matters.

```
### Example

Input: "help me make a skill for code review"

Expected intent capture:
  Name:      code-review
  Purpose:   Automated code review with project-specific rules
  Triggers:  Keyword detection ("review", "check code")
  Output:    Chat response (analysis + suggestions)
```

When to add examples:
- Output has a specific structure (JSON, tables, reports)
- The task involves classification or judgment calls
- Users report format inconsistencies

When to skip:
- Output is freeform text
- The task is straightforward (read file, run command)

---

## 5. Pushy Descriptions

The frontmatter `description` controls when the agent loads the skill. Make it aggressive about triggering.

**Formula**: trigger keywords + WHAT it does + WHEN to use it + inclusive phrasing

```yaml
description: >-
  Create, test, and iterate Cursor Agent Skills. Use for skill creation,
  skill testing, evaluation, or when user says "make a skill", "new skill",
  "check my skill". Even if user just says "prompt" or "lint", use this.
```

Techniques:
- List synonyms and abbreviations the user might use
- Add "even if user doesn't mention X" for non-obvious triggers
- Include both English and Chinese trigger words if bilingual users expected
- Err on the side of over-triggering — false positives are cheaper than missed activations

---

## 6. Output Templates

When structure matters, provide the exact format. Don't describe it — show it.

```
### Output format

```json
{
  "name": "...",
  "status": "PASS | FAIL",
  "findings": [
    { "rule": "...", "severity": "error | warning", "detail": "..." }
  ]
}
```
```

Why: agents reproduce templates more faithfully than they follow prose descriptions of structure.

---

## 7. Conciseness

The agent already knows how to code, reason, and use tools. Only add information it wouldn't already have:

- Domain-specific conventions
- Project-specific file paths and patterns
- Non-obvious decision criteria
- Constraints that override default behavior

**Cut ruthlessly**: if removing a sentence doesn't change the agent's behavior, remove it.

---

## 8. Constraint Clarity

State explicit do/don't rules. Provide escape hatches so the agent isn't stuck.

```
# Good
Do not modify files outside the workspace/ directory.
If the user explicitly requests changes elsewhere, confirm the path before proceeding.

# Bad
Be careful about file modifications.
```

Pattern:
1. State the constraint
2. State the escape condition (if any)
3. Brief reason (if non-obvious)

---

## 9. Data-Instruction Separation

Use XML tags or clear delimiters to separate variable data from fixed instructions.

```
Analyze the skill at the path below and report issues.

<skill_path>
{{SKILL_PATH}}
</skill_path>

<lint_config>
{{CONFIG_JSON}}
</lint_config>
```

Why: prevents the agent from confusing user data with instructions. Especially important when skill content is injected as context for another agent (grader, linter, etc.).

---

## Quick Reference Checklist

Before finalizing any skill file, verify:

- [ ] All instructions use imperative form
- [ ] Non-obvious rules include a brief "why"
- [ ] Body ≤ 500 lines; detail in references/
- [ ] 1-2 examples for output-sensitive tasks
- [ ] Description includes trigger keywords + WHAT + WHEN
- [ ] Output templates provided where structure matters
- [ ] No redundant instructions the agent already knows
- [ ] Do/don't constraints have escape hatches
- [ ] Variable data separated from instructions with tags
