# Skill Authoring — Prompt Engineering Guide

Six techniques that directly improve SKILL.md quality, distilled from Anthropic's prompt engineering research.

---

## 1. Imperative Form + Explain Why

**What:** Write instructions as direct commands. Pair each rule with a brief reason.

**Why it matters:** Imperative form is more token-efficient and less ambiguous for agent-read prose. Explaining "why" leverages the model's theory of mind — it generalizes the rule to edge cases you didn't enumerate.

### Before (weak)

```markdown
It would be nice if the agent checked for existing files before creating new ones.
You should probably avoid creating documentation unless asked.
```

### After (strong)

```markdown
Check for existing files before creating new ones — overwrites destroy user work silently.
NEVER create documentation files unless explicitly requested — users find unsolicited READMEs intrusive.
```

**Key insight:** Bare MUST/NEVER without reasons get ignored under pressure. "NEVER do X — because Y" sticks because the model understands the consequence.

---

## 2. Pushy Descriptions (Counter Under-Trigger)

**What:** Write the skill description to aggressively claim its trigger space. List keywords, synonyms, and say "Use even when…".

**Why it matters:** Claude tends to under-trigger skills — it won't activate a skill unless the match is obvious. Pushy descriptions lower the activation threshold.

### Before (under-triggers)

```markdown
Help with database migrations.
```

### After (reliably triggers)

```markdown
Database schema migrations and versioning. Use for /migrate, migration, schema change, alter table, 
add column, DB upgrade, even when user just says "update the database" without mentioning migrations.
```

### Pattern

```
<short summary>. Use for <keyword1>, <keyword2>, ... even when <non-obvious trigger scenario>.
```

**Key insight:** If users would benefit from the skill but might not phrase it perfectly, the description must meet them halfway.

---

## 3. Data/Instruction Separation

**What:** Clearly separate template content (data the agent fills in) from behavioral rules (instructions the agent follows). Use distinct formatting for each.

**Why it matters:** When templates and rules are mixed, the model confuses "output this literally" with "follow this guideline." Separation prevents the agent from treating template placeholders as instructions or vice versa.

### Before (mixed — confusing)

```markdown
Create a file with a title section. The title should be descriptive. Use ## for the heading.
Then add a description. Keep it under 100 words. Use plain language.
```

### After (separated)

```markdown
## Rules
- Title must be descriptive and specific to the task
- Description stays under 100 words in plain language

## Output Template
\```
## {{title}}

{{description}}
\```
```

### Techniques for separation

| Signal | Use for |
|--------|---------|
| `## Rules` / `## Template` headings | Top-level separation |
| Code fences for templates | Mark literal output structure |
| `{{placeholder}}` syntax | Show where dynamic content goes |
| Prose paragraphs for rules | Behavioral instructions |

---

## 4. Progressive Disclosure (500-Line Limit)

**What:** Keep SKILL.md under 500 lines. Move detailed references, examples, and lookup tables into `references/` files that the skill loads on demand.

**Why it matters:** Long skills waste context window on every invocation — even when 80% of the content isn't needed for the current task. Short skills load fast; reference files provide depth only when relevant.

### Structure

```
skills/my-skill/
├── SKILL.md              # ≤500 lines — core flow + rules
└── references/
    ├── api-patterns.md   # Loaded when skill needs API details
    ├── error-catalog.md  # Loaded when debugging
    └── examples.md       # Loaded for complex scenarios
```

### In SKILL.md — reference loading pattern

```markdown
## References
When implementing API calls, read `references/api-patterns.md` first.
For error handling, consult `references/error-catalog.md`.
```

### What stays in SKILL.md vs references

| In SKILL.md | In references/ |
|--------------|----------------|
| Trigger description | Detailed examples |
| Core workflow steps | Lookup tables |
| Critical rules (≤15) | Edge case catalogs |
| Output format | API documentation |

---

## 5. Few-Shot Examples Pattern

**What:** Include 1-3 concrete input→output examples showing the skill's expected behavior. Wrap in `<example>` tags with optional reasoning.

**Why it matters:** Examples anchor behavior more reliably than abstract rules. One good example eliminates paragraphs of explanation.

### Pattern

```markdown
<example>
User: "Add a login page"
Agent action:
1. Check for existing auth components
2. Create `src/pages/Login.tsx` with form
3. Add route in `src/App.tsx`
4. Run linter
</example>

<example>
User: "Fix the header"
Agent action:
1. Read the header component
2. Identify the issue from context/lints
3. Apply minimal fix
4. Verify no regressions
</example>
```

### Guidelines

- **1 example** for simple skills with predictable behavior
- **2-3 examples** for skills with branching logic or ambiguous inputs
- **Show the hard case** — easy cases don't need examples, tricky ones do
- **Include reasoning** when the decision isn't obvious from input alone

### Before (rules only — ambiguous)

```markdown
When the user asks to fix something, determine scope and apply minimal changes.
```

### After (example makes it concrete)

```markdown
<example>
User: "Fix the broken test"
Agent:
1. Run test suite to identify failure
2. Read failing test + source under test
3. Fix root cause (not the assertion)
4. Re-run to confirm green
<reasoning>
Fix targets root cause, not symptoms. "Minimal" means don't refactor adjacent code.
</reasoning>
</example>
```

---

## 6. Output Format Control

**What:** Define exact output structure using templates, headings, or tagged sections. Specify what to include AND what to omit.

**Why it matters:** Without format control, agents produce inconsistent outputs — sometimes verbose prose, sometimes bare lists. Templates guarantee parseable, predictable results.

### Template approach

```markdown
## Output Format
Report using exactly this structure:

**Status:** DONE | BLOCKED | NEEDS_INPUT
**Changed:** <file list>
**Summary:** <1-2 sentences>
```

### Exclusion control (equally important)

```markdown
Do NOT include:
- Line numbers or file paths in prose
- Tool call details
- Apologies or filler phrases
```

### Before (uncontrolled)

```markdown
Tell the user what you did.
```

### After (controlled)

```markdown
## Completion Report
End every task with:

\```
Status: DONE | DONE_WITH_CONCERNS | BLOCKED
Files: <changed file paths, one per line>
Notes: <only if DONE_WITH_CONCERNS or BLOCKED>
\```

Omit the Notes field entirely when Status is DONE.
```

### Techniques

| Technique | When to use |
|-----------|-------------|
| Literal template with placeholders | Structured reports, file generation |
| Enum values (`A | B | C`) | Constrain categorical fields |
| "Omit X entirely" | Prevent hallucinated/filler sections |
| "Exactly N sentences" | Control verbosity |

---

## Quick Reference

| # | Technique | One-liner |
|---|-----------|-----------|
| 1 | Imperative + Why | Command form, always explain the reason |
| 2 | Pushy Descriptions | Over-claim trigger space to counter under-trigger |
| 3 | Data/Instruction Split | Templates in fences, rules in prose |
| 4 | Progressive Disclosure | SKILL.md ≤500 lines, detail in references/ |
| 5 | Few-Shot Examples | 1-3 concrete input→output pairs |
| 6 | Output Format Control | Template the exact output structure |
