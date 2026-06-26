# Lint Rules — 9-Dimension Criteria & Scoring

Reference document for the Skill Linter agent. Load on demand; do not embed inline.

---

## 1. Nine-Dimension Criteria

Each dimension is evaluated independently. The detection column describes what the linter looks for.

| # | Dimension | Detection | Pass | Partial | Fail |
|---|-----------|-----------|------|---------|------|
| 1 | Role Assignment | `"You are a ..."` or equivalent persona statement within the first 10 lines of the skill body (after YAML front matter) | Persona statement present in first 10 lines | Persona exists but beyond line 10, or uses vague phrasing (e.g. "Act as") | No persona statement found |
| 2 | Context Provision | Background info block covering APIs, auth, defaults, or dependencies | Dedicated section with relevant context (APIs, auth, env, deps) | Some context mentioned but scattered or incomplete | No background / context section |
| 3 | Data-Instruction Separation | XML tags (`<tag>`) or template variables (`{{VAR}}`, `{var}`) used to separate data from instructions | XML tags or template vars clearly separate all dynamic data | Tags/vars used partially; some data is inline | No structural separation of data and instructions |
| 4 | Output Format Specification | At least one operation specifies the expected output structure (code block, table, template, schema) | Output structure explicitly defined for major operations | Output mentioned but format is vague or incomplete | No output format specified anywhere |
| 5 | Examples | `<example>` block(s) with `<input>` / `<output>` sub-tags per major operation | ≥1 example per major operation with input/output | Examples exist but missing input or output, or not covering all major operations | No example blocks |
| 6 | Step-by-Step Procedure | Numbered procedure steps for complex operations | Complex operations have numbered steps | Steps exist but unnumbered or missing for some operations | No procedural steps for complex operations |
| 7 | Constraints | Explicit "do NOT" rules + escape hatch ("say I don't know" or equivalent fallback) | Both "do NOT" constraints and escape hatch present | One of the two present (constraints without escape hatch or vice versa) | Neither present |
| 8 | Clarity | Instructions are unambiguous; no buried multi-sentence conditional logic | All instructions clear, scannable, well-structured | Mostly clear but some buried or ambiguous instructions | Ambiguous, dense, or contradictory instructions |
| 9 | Hallucination Guardrails | "do not fabricate" / "do not invent" / "verify before stating" or equivalent | Explicit anti-hallucination instruction present | Implicit guardrails only (e.g. "use only provided data") | No hallucination guardrails |

---

## 2. Language Discipline Rules

Skills must follow strict language discipline. The linter checks each element type.

### Must Be English

| Element | Example |
|---------|---------|
| YAML field names | `name:`, `description:` |
| Markdown headings | `## Step 1: Detect Environment` |
| Procedure step text | `1. Read the config file` |
| Code / commands | `git clone ...`, `python3 ...` |
| XML/HTML tag names | `<example>`, `<input>`, `<env_checks>` |
| Template variable names | `{{SKILL_NAME}}`, `{scope}` |
| Table column headers | `\| Check \| Command \| Required \|` |

### Chinese Allowed

| Element | Example |
|---------|---------|
| YAML `description` value | `description: "Skill 质量审计"` |
| Example tag content | `<example>用户输入 ...</example>` |
| Table cell content (user-visible) | `\| 已安装 \| 正常 \|` |
| Report output templates | `审计时间: ...` |
| User-facing messages | `"需要安装 git。"` |

### Scoring

| Verdict | Criteria |
|---------|----------|
| Pass | All elements follow the rules above |
| Partial | ≤3 violations, none in headings or YAML field names |
| Fail | >3 violations, or any heading / YAML field name in Chinese |

---

## 3. Scoring Rubric

### Per-Dimension Scoring

| Score | Label | Definition |
|-------|-------|------------|
| **Pass** | 通过 | Fully implemented — meets the detection criteria completely |
| **Partial** | 部分通过 | Present but incomplete — see dimension-specific partial criteria |
| **Fail** | 不合格 | Missing entirely or fundamentally inadequate |

### Aggregate Scoring

Calculate the overall skill verdict from individual dimension scores:

| Verdict | Condition |
|---------|-----------|
| **通过** (Pass) | All 9 dimensions Pass AND language discipline Pass |
| **需改进** (Needs Improvement) | ≤3 dimensions are Partial, 0 Fail AND language discipline ≥ Partial |
| **不合格** (Fail) | Any dimension is Fail OR >3 Partial OR language discipline Fail |

### Numeric Score (Optional)

For sorting and dashboards: Pass = 2, Partial = 1, Fail = 0. Max score: 18 + 2 (language) = 20.

---

## 4. Report Template

All audit reports MUST use this template. Field placeholders in `{braces}`.

````markdown
# Skill 质量审计报告

审计时间: {YYYY-MM-DD HH:MM}
审计范围: {scope}
审计数量: {N} 个 skill

---

## 总览

| Skill | 语言合规 | 模板合规 | 总分 | 判定 |
|-------|---------|---------|------|------|
| {skill-name} | {Pass/Partial/Fail} | {score}/18 | {score}/20 | {通过/需改进/不合格} |

---

## 详细发现

### {skill-name}

**文件路径**: `{relative-path-to-SKILL.md}`

#### 语言检查

**判定**: {Pass/Partial/Fail}

| 违规项 | 行号 | 内容 | 应为 |
|--------|------|------|------|
| {element-type} | {line} | `{actual}` | `{expected}` |

> 无违规时输出: "语言检查通过，未发现违规项。"

#### 模板检查（9 维度）

| # | 维度 | 判定 | 说明 |
|---|------|------|------|
| 1 | Role Assignment | {Pass/Partial/Fail} | {evidence or gap} |
| 2 | Context Provision | {Pass/Partial/Fail} | {evidence or gap} |
| 3 | Data-Instruction Separation | {Pass/Partial/Fail} | {evidence or gap} |
| 4 | Output Format Specification | {Pass/Partial/Fail} | {evidence or gap} |
| 5 | Examples | {Pass/Partial/Fail} | {evidence or gap} |
| 6 | Step-by-Step Procedure | {Pass/Partial/Fail} | {evidence or gap} |
| 7 | Constraints | {Pass/Partial/Fail} | {evidence or gap} |
| 8 | Clarity | {Pass/Partial/Fail} | {evidence or gap} |
| 9 | Hallucination Guardrails | {Pass/Partial/Fail} | {evidence or gap} |

#### 修复建议

1. {具体修复建议，引用维度编号}
2. {具体修复建议}
3. ...

> 全部通过时输出: "所有维度均已通过，无需修复。"

---

## 总结

| 判定 | 数量 |
|------|------|
| 通过 | {n} |
| 需改进 | {n} |
| 不合格 | {n} |

**最常见问题**: {top 1-3 most frequent failing dimensions across all audited skills}
````

---

## 5. Linter Detection Quick-Reference

Compact lookup table for the linter agent to pattern-match against.

| Dimension | Positive Signal (any match → candidate Pass) | Negative Signal (none found → Fail) |
|-----------|----------------------------------------------|-------------------------------------|
| Role Assignment | `/^You are /i` in first 10 body lines | No persona-like statement |
| Context Provision | Section header matching `context`, `background`, `prerequisites`, `dependencies`, `important rules` | No dedicated section |
| Data-Instruction Separation | `<tag>`, `{{VAR}}`, `{var}` patterns | Raw inline data without delimiters |
| Output Format | Code fence, table, or `template` / `format` / `schema` keyword near output description | No structured output spec |
| Examples | `<example>` tag with `<input>` and `<output>` children | No `<example>` blocks |
| Step-by-Step | Numbered list (`1.`, `2.`, ...) inside operational sections | Prose-only instructions for complex flows |
| Constraints | `do NOT` / `NEVER` / `MUST NOT` + `don't know` / `cannot` / `unsupported` / `stop` | No prohibition or fallback |
| Clarity | Short paragraphs, bullet lists, tables, clear conditionals | Wall-of-text paragraphs, nested conditionals |
| Hallucination Guardrails | `fabricate` / `invent` / `make up` / `hallucinate` / `verify before` | No anti-hallucination language |
