# Fix Report Format

Reference document for the SKILL-fix command. The orchestrator uses this template to present fix results to the user.

---

## Report Template

All fix reports MUST use this template. Field placeholders in `{braces}`.

````markdown
# Skill 修复报告

修复时间: {YYYY-MM-DD HH:MM}
目标文件: `{skill_path}`
修复轮次: {round}/{max_rounds}

---

## 1. 检查结果（引用 lint 结果）

| 检查类型 | 判定 | 问题数 |
|----------|------|--------|
| 语言合规 | {Pass/Partial/Fail} | {violation_count} |
| 模板合规 | {score}/9 | {fail_count + partial_count} 项待改进 |

**问题分类**:

| 类别 | 数量 | 说明 |
|------|------|------|
| 逻辑问题 | {logic_count} | 结构性缺陷（角色、示例、约束等） |
| 格式问题 | {format_count} | 规范性问题（语言、行数、模板合规） |

---

## 2. 修复操作

### 逻辑修复（优先处理）

> 无逻辑问题时输出: "未发现逻辑问题，跳过。"

#### 修复 {id}: {dimension} — {description}

**修改前** (行 {start_line}-{end_line}):

```
{before_content}
```

**修改后**:

```
{after_content}
```

---

### 格式修复

> 无格式问题时输出: "未发现格式问题，跳过。"

#### 修复 {id}: {dimension} — {description}

**修改前** (行 {start_line}-{end_line}):

```
{before_content}
```

**修改后**:

```
{after_content}
```

---

### 跳过的问题

> 无跳过项时输出: "所有问题均已修复。"

| # | 维度 | 原因 |
|---|------|------|
| {id} | {dimension} | {reason} |

---

## 3. 修复后验证

> 仅在 auto_run_validate 为 true 时展示本节。

| 检查类型 | 修复前 | 修复后 |
|----------|--------|--------|
| 语言合规 | {before_verdict} | {after_verdict} |
| 模板合规 | {before_score}/9 | {after_score}/9 |

**验证判定**: {通过 / 仍需改进 / 不合格}

---

## 4. 遗留问题

> 全部通过时输出: "所有问题已修复，验证通过。"

| # | 维度 | 说明 | 建议 |
|---|------|------|------|
| {n} | {dimension} | {finding} | {manual_fix_suggestion} |

---

## 总结

| 指标 | 数值 |
|------|------|
| 发现问题 | {issue_count} |
| 已修复 | {fix_count} |
| 已跳过 | {skip_count} |
| 修复轮次 | {round}/{max_rounds} |
| 最终判定 | {通过 / 仍需改进 / 不合格} |
````

---

## Field Definitions

| Field | Source | Description |
|-------|--------|-------------|
| `skill_path` | Input | Absolute path to the SKILL.md file |
| `round` / `max_rounds` | Config `fix.max_rounds` | Current round / maximum allowed rounds |
| `violation_count` | Linter `language_check.violation_count` | Number of language violations |
| `score` | Linter `template_check.pass_count` | Template compliance pass count |
| `logic_count` / `format_count` | Fixer `categories` | Issue counts by category |
| `before_content` / `after_content` | Fixer `fixes[].before.content` / `fixes[].after.content` | Original and proposed text |
| `before_verdict` / `after_verdict` | Pre/post-fix linter runs | Language discipline verdicts |
| `before_score` / `after_score` | Pre/post-fix linter runs | Template compliance scores |

## Rendering Rules

- Show logic fixes before format fixes (matches fix priority order).
- For each fix, always show both before and after code blocks so the user can compare.
- Skipped issues must include a reason explaining why the fixer could not address them.
- Section 3 (validation) only appears when `auto_run_validate` is `true` in config.
- Section 4 (remaining issues) only appears when post-fix validation still finds issues.
