# Skill应用

原因：cursor原生插件生成skill时不够细致、缺少审查环节。
做法：根据claude的插件源码以及提示词优化工程，设计skill生成插件并内置到cursor。

项目地址：[choeyyy/skill-creator](https://github.com/choeyyy/skill-creator)

这个例子也用作写skill规范的说明。

### 一、参考例子

#### 1.1 cursor的skill插件create-skill 工作流

Cursor 内置的 `create-skill` 是一个纯编写指南，没有测试和迭代能力，分四个阶段。

1. **需求采集**

   确定命令目的、skill存储位置、适用场景、输出格式要求、是否有示例参考、是否有上下文可供推断。

   阶段产出：明确的需求。

2. **设计**

   根据第一阶段产生的明确需求，确定：skill名称、描述、规划主要章节结构（做什么、什么时候用、判断是否需要附带参考文件/脚本）

   阶段产出：skill的名称、描述、结构大纲

3. **实现**

   创建目录结构，写skill（以及可能的配置yaml文件、参考文档路径、脚本等）。

   按照原则编写：500行内、精简、渐进式披露、按任务脆弱度选择自由度。

   阶段产出：完整的skill目录

4. **验证**

   用一组checklist静态检查skill是否符合要求（主要检查编写是否符合规范、术语是否一致、描述是否具体、文件引用是否一致）

   阶段产出：检查过的完整的skill目录

#### 1.2 claude的skill插件skill-creator 工作流

Claude 官方的 `skill-creator` 是一个完整的评测驱动（eval-driven）开发框架，覆盖从创建到优化的全过程。分九步骤完成：

1. **意图捕获**

   问用户四个问题弄清意图

   做什么、什么场景应该触发、希望输出什么格式、要不要设置测试用例来验证效果。

   提取上下文信息、当前目录信息。

   产出：结构化的需求描述

2. **访谈调研**

   围绕边界情况、输入输出格式、示例文件、成功标准和依赖项进行追问。

   （如果有mcp工具，比如搜索文档、查找类似skill，就并行调研）

   一边调研一边问用户问题，减少用户负担，弄清楚边界、以来、成功标准。

   产出：完整的需求规格

3. **编写skill**

   根据访谈结果写SKILL.md

   格式：根据上下文写约100词的浓缩元数据

   ​           主要任务，500行内，触发skill时加载

   ​           其他资源按需加载（比如重复的部分打包成scripts/下的脚本，而不是让agent重新生成）

   风格：描述字段强势（即使用户没有明确提到 X 也应该用这个 skill）

   ​           使用祈使句，直接说做什么而不是建议或者禁止。

   产出：SKILL.md初稿以及配套文件

4. **测试执行**

   写好初稿之后拟定2-3个真实的提示词（含文件路径、背景、口语化表达、缩写）。在同一轮中对每个测试用例同时启动两个子agent：一个加载skill、一个不加载作为对照组。同时跑测，同时写量化标准，跑测预期。跑测完成后记录各自的耗时、token用量。

   产出：每个测试用例的有skill没skill的两组输出、时间数据、量化以及预期结果。

5. **评分**

   所有run跑完之后，根据输出、数据、标准来评估。

   这一步优先用脚本检查，不主观判断。

   产出：每个测试用例的评分结果（pass/fail + 证据引用）

6. **整合**

   将所有评分汇总为 数据集合文档`benchmark.json`，包含 with_skill 和 without_skill 两组的通过率、平均耗时、token 用量，各自带均值和标准差，以及两者的差值（delta）。

   然后用 `generate_review.py` 生成一个交互式 HTML 查看器，展示输出、指标给用户看以及反馈。用户提交反馈之后生成反馈文档`feedback.json`

   产出： benchmark 数据、交互式查看器、用户反馈

7. **改进迭代**

   读取用户反馈，改进。

   改进时追求泛化而非过拟合：如果多个测试都在同一类断言上失败，说明 skill 有结构性问题；如果 baseline 在某些测试上反而更好，说明 skill 限制过多需要放松。

   改完后进入下一轮迭代：重新跑所有测试（到新的 `iteration-N+1/` 目录）、重新评分、重新生成查看器（带 `--previous-workspace` 显示上一轮对比），直到用户满意或不再有改进。

   产出：改进后的 skill 版本 + 新一轮 benchmark。

   

8. **盲比（Blind A/B Comparison）**

   （可选步骤）严格对比skill版本

   对每个测试用例，把两个版本的输出随机标记为 A 和 B，交给一个独立的 comparator agent 在不知道版本标签的情况下打分。

   打完分后揭晓标签，报告哪个版本赢了。再由 analyzer agent 分析赢的版本为什么赢。

   产出：盲评分数、版本胜负、原因分析。

   

9. **描述优化**

   最后一步，优化 SKILL.md frontmatter 中的 description 字段以提升触发准确率。生成 20 条测试查询（10 条应触发 + 10 条不应触发），按 70/30 分为训练集和测试集（14 条训练 / 6 条测试）。在训练集上迭代改进 description（最多 5 轮），用测试集评估最终效果避免过拟合。

   产出：优化后的 description 、准确率报告。

   

#### 1.3 claude的提示词工程中关于提示词的优化

官方文档：[提示最佳实践 - Claude API Docs](https://platform.claude.com/docs/zh-CN/build-with-claude/prompt-engineering/claude-prompting-best-practices)

提示词教程交互版：[anthropics/prompt-eng-interactive-tutorial: Anthropic's Interactive Prompt Engineering Tutorial](https://github.com/anthropics/prompt-eng-interactive-tutorial)

ps：针对fable5、opus4.8，官方给出专门的提示词模板。在此只列举其他版本通用的提示词模板。

##### 1.3.1 技巧启示

​      用祈使句写指令、用 XML 标签隔离数据和指令、给出具体示例覆盖边界、在末尾重申任务并要求先思考再回答、用 prefill 控制输出格式、给模型留一个"不知道"的出口减少幻觉、先跑通再精简。

> 不知道的出口：不直接让 Claude 回答问题，而是先让它从文档中提取相关引用到 `<scratchpad>` 里，再基于引用回答。如果找不到引用，Claude 自然不会编造。教程给了一个例子：问 Claude "Who is the heaviest hippo of all time?"，Claude 会编造几只大河马的名字和体重来"帮忙"。加一句 "Only answer if you know the answer with certainty" 之后，Claude 就会承认自己不确定。



> 先跑通再精简：意思是先把下面模板的所有元素都填上，让输出先达到预期效果，然后逐个去掉元素看哪些去掉不影响效果——最终留下的就是最精简的版本。不是一开始就追求短，而是先写全再删。



##### 1.3.2 模板

**使用方法**：不是每个元素都要填。根据任务需要选填，用 `if` 判断跳过空元素。教程的做法是先全填，跑出满意结果后，逐个清空元素看去掉哪个不影响输出质量，最后留下最小集合。

教程还特别强调了几个**元素的位置敏感性**：任务背景放最前面，示例和输入数据在中间，即时任务重申、思维链、输出格式放末尾，预填充放 assistant 消息。但示例和输入数据之间的顺序可以灵活调换——教程的法律文档案例就把输入数据放到了示例前面，因为那个场景里先看到文档再看引用格式示例更自然。

模板：

```markdown
# ===== 输入变量 =====
HISTORY = "..."      # 对话历史、文档、数据等（根据场景替换）
QUESTION = "..."     # 用户的具体问题

# ===== 10 个提示词元素 =====

# 元素 1: user 角色（API 层面自动处理，不需要手写）

# 元素 2: 任务背景 — 告诉模型它是谁、要做什么
# 放在最前面，越早给背景越好
TASK_CONTEXT = "You will be acting as an AI career coach named Joe created by the company AdAstra Careers. Your goal is to give career advice to users."

# 元素 3: 语气要求 — 不是所有任务都需要
TONE_CONTEXT = "You should maintain a friendly customer service tone."

# 元素 4: 详细任务描述和规则 — 具体规则、边界约束、"不知道"出口
TASK_DESCRIPTION = """Here are some important rules for the interaction:
- Always stay in character, as Joe
- If you are unsure how to respond, say "Sorry, I didn't understand that. Could you rephrase your question?"
- If someone asks something irrelevant, say "Sorry, I am Joe and I give career advice. Do you have a career question today I can help you with?"
"""

# 元素 5: 示例 — 教程称这是"让模型按预期行为最有效的单一工具"
# 用 <example> 标签包裹，多个示例各自独立标签，覆盖边界情况
EXAMPLES = """Here is an example of how to respond:
<example>
Customer: Hi, how were you created?
Joe: Hello! My name is Joe, and I was created by AdAstra Careers. What can I help you with today?
</example>"""

# 元素 6: 输入数据 — 用 XML 标签隔离，防止数据被当成指令
INPUT_DATA = f"""Here is the conversational history:
<history>
{HISTORY}
</history>

Here is the user's question:
<question>
{QUESTION}
</question>"""

# 元素 7: 即时任务重申 — 在长提示词末尾再说一次"现在请做什么"
# 放末尾比放开头效果好，用户问题也放在靠近末尾的位置
IMMEDIATE_TASK = "How do you respond to the user's question?"

# 元素 8: 思维链 — 让模型先想再答
# 放在末尾、紧跟即时任务之后
PRECOGNITION = "Think about your answer first before you respond."

# 元素 9: 输出格式 — 放末尾，明确告诉模型怎么格式化
OUTPUT_FORMATTING = "Put your response in <response></response> tags."

# 元素 10: 预填充 — 写在 assistant 角色里，强制引导输出开头
PREFILL = "[Joe] <response>"


# ===== 组装 =====
PROMPT = ""
if TASK_CONTEXT:     PROMPT += f"{TASK_CONTEXT}"
if TONE_CONTEXT:     PROMPT += f"\n\n{TONE_CONTEXT}"
if TASK_DESCRIPTION: PROMPT += f"\n\n{TASK_DESCRIPTION}"
if EXAMPLES:         PROMPT += f"\n\n{EXAMPLES}"
if INPUT_DATA:       PROMPT += f"\n\n{INPUT_DATA}"
if IMMEDIATE_TASK:   PROMPT += f"\n\n{IMMEDIATE_TASK}"
if PRECOGNITION:     PROMPT += f"\n\n{PRECOGNITION}"
if OUTPUT_FORMATTING:PROMPT += f"\n\n{OUTPUT_FORMATTING}"

# 调用 API 时 PREFILL 放在 assistant 消息里
```

##### 1.3.3 使用提示词优化模板的时机

**用模板的场景**：在构建一个要反复执行的任务——system prompt、SKILL.md、API 调用中的固定 prompt、自动化工作流中的提示词。这些场景下输入数据每次不同但指令结构固定，模板让你把"骨架"和"变量"分离，每次只替换变量部分。教程 Chapter 4 专门讲了这个——用 f-string 的 `{VARIABLE}` 做占位符，用 XML 标签隔离数据和指令。典型例子：代码审查 prompt（固定规则+变量是 diff）、文档问答 prompt（固定流程+变量是文档和问题）、分类 prompt（固定类别定义+变量是待分类内容）。

**直接对话的场景**：一次性的、探索性的、上下文在对话中逐步建立的任务。比如在 Cursor 里和 agent 聊天调试一个 bug、讨论架构方案、问一个具体技术问题。这些场景下不需要提前设计模板，对话本身就是迭代过程。

如果同一个提示词需要反复使用，或需要程序化调用（脚本、API、hook），可以做成提示词模板/skill。skill本质上是一个持久的提示词模板。

---

（根据官方的提示词工程，产出了3个skill，为通用模板、fable5、opus4.8的提示词生成skill，放在文末。）



### 二、融合开发新cursor skill

#### 2.1 准备：根据参考例子，整合需要的部分

需要：cursor skill插件的格式、claude生成skill的9步方法、提示词工程中提到的提示词规范。

预计和claude的流程差不多，在此基础上改动了：1.要求生成的skill强制按照提示词规范格式；2.加入生命周期检测，让用户可以随时中断skill生成，下次输入请求会自动回到正确位置；3.关于评估反馈这一步，主要改为在 IDE 内展示结果（Canvas 或 markdown），HTML 报告（generate_review.py）保留为可选备选方案。4.在呈现初版skill给用户之前，加上了cursor的检查步骤（格式、规范、一致性）。



#### 2.2 融合：自定义插件SKILL creator v0.2.0

项目地址：[choeyyy/skill-creator](https://github.com/choeyyy/skill-creator)

v0.2.0 在原有 `/SKILL-creator` 基础上扩展为统一的 `/SKILL-xxx` 命令族：

| 命令 | 功能 | 入口文件 |
|:-----|:-----|:---------|
| `/SKILL-creator` | 创建 → 测试 → 评分 → 迭代 → 描述优化 | skills/skill-creator/SKILL.md |
| `/SKILL-lint` | 9 维度审计（语言纪律 + 模板合规 + 质量评分） | commands/SKILL-lint.md |
| `/SKILL-fix` | 逻辑优先修复 → 格式强制 → diff 确认 | commands/SKILL-fix.md |
| `/SKILL-pythonGenerator` | 跨 skill 重复逻辑提取为 Python CLI 脚本 | commands/SKILL-pythonGenerator.md |
| `/SKILL-setup` | 环境检测 → 安装 → agent 模型配置 | setup/SKILL.md |

##### 安装方式

两阶段安装：bootstrap（一行命令）→ `/SKILL-setup`（IDE 内引导）

```powershell
# Windows
irm https://raw.githubusercontent.com/choeyyy/skill-creator/main/bootstrap.ps1 | iex

# macOS/Linux
curl -fsSL https://raw.githubusercontent.com/choeyyy/skill-creator/main/bootstrap.sh | bash
```

##### 配置

`config/defaults.json` 控制 agent 选型和规则：

```json
{
  "agents": {
    "orchestrator": "sonnet",
    "linter": "haiku",
    "tester": "haiku",
    "extractor": "haiku"
  },
  "lint": {
    "max_lines": 500,
    "language": { "body": "english", "output": "chinese" }
  },
  "fix": { "max_rounds": 2, "require_confirmation": true },
  "extract": { "min_duplicate_skills": 2, "min_duplicate_steps": 3 }
}
```

##### Lint 9 维度

| # | 维度 | 检查内容 |
|:--|:-----|:---------|
| 1 | 语言纪律 | body 全英文，user-facing output 中文 |
| 2 | 模板结构 | 必须有 role、output format、constraints |
| 3 | 示例覆盖 | 至少 1 个 example（含边界） |
| 4 | 边界处理 | edge cases 明确 |
| 5 | 行数限制 | ≤500 行 |
| 6 | 引用一致性 | references/ 和 scripts/ 路径存在 |
| 7 | 描述强度 | description 够"pushy" |
| 8 | 幻觉防护 | 有 escape hatch |
| 9 | 格式规范 | XML 标签隔离、祈使句 |

##### Fix 工作流

```
/SKILL-fix [file]
    │
    ▼
读取 lint 报告（或现场 lint）
    │
    ▼
分类: logic issue → 优先修复
      format issue → 后续强制
    │
    ▼
生成 diff → 用户确认 → 应用
    │
    ▼
自动重新 lint 验证（最多 2 轮）
```

##### PythonGenerator 工作流

```
/SKILL-pythonGenerator [scope]
    │
    ▼
扫描 skill 文件，检测重复模式：
  • 数据聚合（多源 → 统一结构）
  • 格式转换（JSON/YAML/CSV 互转）
  • 验证逻辑（schema check）
  • 报告生成（模板填充）
    │
    ▼
满足阈值（≥2 skill × ≥3 步骤重复）
    │
    ▼
生成 Python CLI 脚本 → scripts/
带 argparse + docstring + type hints
```

SKILL-creator 的代码架构、完整工作流见附件。



## 其他：skill工程方法

skill设计类别 各自适应的场景

在这根据市面上有关skill编写优化提炼的方式大致分4类：

1. ##### **人工编写**

> 人类基于经验，主动编写skill。
>
> （包括从0写、从已有skill出发改写）



2. ##### 经验提炼

> 从已发生的agent交互记录、语料中（上下文、并行轨迹、产出内容、文档手册代码库等）提取生成skill
>
> 知识来源是执行过程，不是人的预设知识。

包括：从语料编写，从agent执行过程中获取、从大量轨迹池中蒸馏。



3. ##### 评测迭代

> 已有一个skill，不断通过运行、分析，改进skill
>
> 约定评估标准，通过测试用例/执行轨迹之后改进skill（包含版本历史、对比）
>
> 知识来源是运行的反馈。是改进迭代skill的思路。（注意经验提炼是0~1生成skill）

包括人评测以及自动化评测（脚本/agent实时监听，同步语料尝试迭代已有skill）



4. ##### 组合编排

> 不创造新skill，而是定义已有agent、skill之间的调度逻辑（mcp、多agent）。



**上述四类可以按照场景叠加混用。**

## 附件

##### SKILLS\claude-fable-5-prompting.md

~~~markdown
---
name: claude-fable-5-prompting
description: >-
  Model-specific prompting for Claude Fable 5 and Mythos 5. Use when writing
  prompts targeting Fable 5 / Mythos 5 specifically, or when adapting existing
  prompts for these models. Covers effort levels, subagent behavior, instruction
  following, long-running autonomy, memory systems, and scaffolding changes.
---

# Claude Fable 5 Prompting Guide

## Key Behavioral Differences from Prior Models

- Longer default turns at high effort — single requests may run for minutes; autonomous runs can last hours.
- Stronger instruction following — short directives steer behavior without enumerating every case.
- More aggressive parallel subagent spawning.
- Occasional early stops (states intent without issuing tool call) in deep sessions.
- Occasional context-budget anxiety in very long sessions.

---

## Effort Levels

The `effort` parameter is the primary control for intelligence/latency/cost tradeoff on Fable 5.

| Level | When to Use |
|-------|-------------|
| `xhigh` | Capability-sensitive workloads; complex multi-step reasoning |
| `high` | Default for most tasks; already exceeds prior model `xhigh` |
| `medium` | Routine work where speed matters more than depth |
| `low` | Simple lookups, short-form generation |

Fable 5 performs well even at lower effort — often surpassing prior models at `xhigh`.

**Prevent over-planning at high effort:**

```text
When you have enough information to act, act. Do not re-derive facts already established
in the conversation, re-litigate a decision the user has already made, or narrate
options you will not pursue in user-facing messages. If you are weighing a choice, give
a recommendation, not an exhaustive survey. This does not apply to thinking blocks.
```

**Prevent unsolicited refactoring at high effort:**

```text
Don't add features, refactor, or introduce abstractions beyond what the task requires. A
bug fix doesn't need surrounding cleanup and a one-shot operation usually doesn't need a
helper. Don't design for hypothetical future requirements: do the simplest thing that
works well. Avoid premature abstraction and half-finished implementations. Don't add
error handling, fallbacks, or validation for scenarios that cannot happen. Trust
internal code and framework guarantees. Only validate at system boundaries (user input,
external APIs). Don't use feature flags or backwards-compatibility shims when you can
just change the code.
```

---

## Instruction Following

Fable 5 responds well to concise directives. No need to enumerate every behavior.

**Conciseness directive:**

```text
Lead with the outcome. Your first sentence after finishing should answer "what happened"
or "what did you find": the thing the user would ask for if they said "just give me the
TLDR." Supporting detail and reasoning come after. Being readable and being concise are
different things, and readability matters more.

The way to keep output short is to be selective about what you include (drop details
that don't change what the reader would do next), not to compress the writing into
fragments, abbreviations, arrow chains like A → B → fails, or jargon.
```

**Checkpoint behavior (pause only when genuinely needed):**

```text
Pause for the user only when the work genuinely requires them: a destructive or
irreversible action, a real scope change, or input that only they can provide. If you
hit one of these, ask and end the turn, rather than ending on a promise.
```

---

## Long-Running Autonomy

### Verify progress claims against tool results

```text
Before reporting progress, audit each claim against a tool result from this session.
Only report work you can point to evidence for; if something is not yet verified, say so
explicitly. Report outcomes faithfully: if tests fail, say so with the output; if a step
was skipped, say that; when something is done and verified, state it plainly without
hedging.
```

### Declare boundaries to prevent unsolicited actions

```text
When the user is describing a problem, asking a question, or thinking out loud rather
than requesting a change, the deliverable is your assessment. Report your findings and
stop. Don't apply a fix until they ask for one. Before running a command that changes
system state (restarts, deletes, config edits), check that the evidence actually
supports that specific action. A signal that pattern-matches to a known failure may have
a different cause.
```

### Autonomous pipeline reminder (prevent premature stops)

```text
You are operating autonomously. The user is not watching in real time and cannot answer
questions mid-task, so asking "Want me to…?" or "Shall I…?" will block the work. For
reversible actions that follow from the original request, proceed without asking.
Offering follow-ups after the task is done is fine; asking permission after already
discussing with the user before doing the work is not. Before ending your turn, check
your last paragraph. If it is a plan, an analysis, a question, a list of next steps, or
a promise about work you have not done ("I'll…", "let me know when…"), do that work now
with tool calls. End your turn only when the task is complete or you are blocked on
input only the user can provide.
```

---

## Parallel Subagents

Fable 5 spawns subagents more aggressively than prior models. Guide delegation:

```text
Delegate independent subtasks to subagents and keep working while they run. Intervene
if a subagent goes off track or is missing relevant context.
```

Prefer async communication over blocking waits. Long-lived subagents that maintain context save time via cache reads.

---

## Memory Systems

Fable 5 excels when it can record and reference lessons from previous runs.

**Recording lessons:**

```text
Store one lesson per file with a one-line summary at the top. Record corrections and
confirmed approaches alike, including why they mattered. Don't save what the repo or
chat history already records; update an existing note rather than creating a duplicate;
delete notes that turn out to be wrong.
```

**Bootstrapping memory from history:**

```text
Reflect on the previous sessions we've had together. Use subagents to identify core
themes and lessons, and store them in [X]. Make sure you know to reference [X] for
future use.
```

---

## Context Budget Anxiety

In very long sessions, Fable 5 may suggest starting a new session or summarizing. Avoid showing explicit token counts. If your framework must show them:

```text
You have ample context remaining. Do not stop, summarize, or suggest a new session on
account of context limits. Continue the work.
```

---

## Readability in User-Facing Output

In extended agentic conversations, Fable 5 may produce dense shorthand. Add a communication style appendix:

```text
Terse shorthand is fine between tool calls (that's you thinking out loud, and brevity
there is good). Your final summary is different: it's for a reader who didn't see any of
that.

When you write the summary at the end, drop the working shorthand. Write complete
sentences. Spell out terms. Don't use arrow chains, hyphen-stacked compounds, or labels
you made up earlier. Open with the outcome: one sentence on what happened or what you
found. Then the supporting detail.
```

---

## Scaffolding Migration Recommendations

- **Start at the top of your difficulty range.** Give Fable 5 harder tasks than you'd assign prior models.
- **Explicit self-validation in long runs.** Independent validator subagents outperform self-critique.
- **Refactor existing skills.** Skills built for prior models are often over-prescriptive for Fable 5 — audit and simplify.
- **Do NOT instruct reasoning echo.** Prompts asking the model to repeat/explain its internal reasoning may trigger `reasoning_extraction` refusals. Use `thinking` blocks via adaptive thinking instead.
- **Create a send-to-user tool** for long async agents that need to deliver content mid-run without ending the turn.

---

## Provide Reasons, Not Just Requests

Fable 5 performs better when it understands intent behind requests:

```text
I'm working on [the larger task] for [who it's for]. They need [what the output
enables]. With that in mind: [request].
```

---

## Safety Classifiers

Fable 5 runs classifiers for offensive cybersecurity, biology/life-science content, and reasoning extraction. Benign work in these areas may trigger refusals (`stop_reason: "refusal"`). Configure server-side or client-side fallback to Opus 4.8 for auto-rerouting.

~~~

##### SKILLS\claude-opus-4-8-prompting.md

~~~markdown
---
name: claude-opus-4-8-prompting
description: >-
  Model-specific prompting for Claude Opus 4.8. Use when writing prompts
  targeting Opus 4.8 specifically, or when adapting existing prompts for this
  model. Covers effort calibration, verbosity control, tool use triggers,
  literal instruction following, subagent control, frontend defaults, and
  code review frameworks.
---

# Claude Opus 4.8 Prompting Guide

## Key Behavioral Differences from Prior Models

- Calibrates response length by perceived task complexity (shorter for simple queries, longer for open analysis).
- Strictly follows effort levels, especially at the low end — may under-think at `low` on moderately complex tasks.
- Prefers reasoning over tool calls by default — explicit guidance needed for tool-heavy workflows.
- More literal instruction interpretation — won't silently generalize rules across contexts.
- Fewer subagents by default — needs explicit delegation guidance.
- Persistent design aesthetic defaults (warm cream, serif fonts, terracotta accents) in frontend generation.
- Thinking is OFF by default unless `thinking: {type: "adaptive"}` is set explicitly.

---

## Effort Level Calibration

Effort is the most important parameter on Opus 4.8 — experiment aggressively.

| Level | When to Use |
|-------|-------------|
| `max` | Peak intelligence; may over-think; test for diminishing returns |
| `xhigh` | Best for coding and agentic use cases |
| `high` | Balanced; minimum for intelligence-sensitive tasks |
| `medium` | Cost-sensitive; trades intelligence for tokens |
| `low` | Short, well-scoped tasks; latency-sensitive but not intelligence-dependent |

**At `low`/`medium`, Opus 4.8 scopes work strictly to what was asked.** Risk of under-thinking on medium-complexity tasks. If you see shallow reasoning, raise effort rather than adding prompt workarounds.

**If forced to stay at `low` effort on a complex task:**

```text
This task involves multi-step reasoning. Think carefully through the problem before responding.
```

**Guide adaptive thinking trigger frequency (if it fires too often):**

```text
Thinking adds latency and should only be used when it will meaningfully improve answer
quality — typically for problems that require multi-step reasoning. When in doubt,
respond directly.
```

**Token budget at high effort:** Set max output tokens to at least 64k for `max`/`xhigh` to give room for thinking and tool calls.

---

## Response Length and Verbosity

Opus 4.8 auto-calibrates length. Adjust only if your product needs specific verbosity:

**Reduce verbosity:**

```text
Provide concise, focused responses. Skip non-essential context, and keep examples minimal.
```

**Positive examples work better than negative instructions** — show Claude how to communicate at the right length rather than listing what not to do.

---

## Tool Use Triggers

Opus 4.8 prefers reasoning over tool calls. Higher effort increases tool use. For tool-heavy workflows:

- Use `high` or `xhigh` effort — shows significantly more tool use in agentic search and coding.
- Describe clearly **why and how** to use each tool in the tool description.
- If a specific tool is under-used, add explicit instructions about when it should be called.

---

## Literal Instruction Following

Opus 4.8 interprets prompts literally, especially at lower effort. It won't generalize rules from one context to another without explicit scope.

**If you need broad application:**

```text
Apply this format to every section, not just the first.
```

**Benefits:** Precision, fewer iterations, predictable pipeline behavior.

---

## Controlling Subagent Spawning

Opus 4.8 spawns fewer subagents by default. Provide explicit guidance:

```text
Do not spawn a subagent for work you can complete directly in a single response (e.g.
refactoring a function you can already see).

Spawn multiple subagents in the same turn when fanning out across items or reading multiple files.
```

---

## User-Facing Progress Updates

Opus 4.8 provides more frequent, higher-quality progress updates during long agentic traces. If you previously added scaffolding to force intermediate summaries ("every 3 tool calls, summarize progress"), try removing it. If updates still don't match your needs, describe what they should look like with examples.

---

## Tone and Writing Style

Opus 4.8 defaults to direct, opinionated prose with minimal hedging. For warmer voice:

```text
Use a warm, collaborative tone. Acknowledge the user's framing before answering.
```

---

## Frontend Design Defaults

Opus 4.8 has a persistent default aesthetic: warm cream/off-white backgrounds (~`#F4F1EA`), serif display fonts (Georgia, Fraunces, Playfair), italic emphasis, terracotta/amber accents. This fits editorial/portfolio work but not dashboards, fintech, healthcare, or enterprise.

**Two reliable approaches to override:**

### 1. Specify concrete alternatives

Provide explicit color palettes, font choices, border radii, and spacing. The model follows precise specs exactly.

### 2. Ask the model to propose options first

```text
Before building, propose 4 distinct visual directions tailored to this brief (each as:
bg hex / accent hex / typeface — one-line rationale). Ask the user to pick one, then
implement only that direction.
```

**Anti-generic-AI aesthetic prompt (pairs well with the above):**

```text
<frontend_aesthetics>
NEVER use generic AI-generated aesthetics like overused font families (Inter, Roboto,
Arial, system fonts), cliched color schemes (particularly purple gradients on white or
dark backgrounds), predictable layouts and component patterns, and cookie-cutter design
that lacks context-specific character. Use unique fonts, cohesive colors and themes, and
animations for effects and micro-interactions.
</frontend_aesthetics>
```

---

## Code Review Framework

Opus 4.8 has higher bug-finding recall and precision than prior models. However, if your review prompts say things like "only report high-severity issues" or "be conservative," Opus 4.8 may follow that more faithfully — identifying bugs but not reporting them because they fall below the stated threshold.

**For maximum recall (recommended for discovery phase):**

```text
Report every issue you find, including ones you are uncertain about or consider
low-severity. Do not filter for importance or confidence at this stage - a separate
verification step will do that. Your goal here is coverage: it is better to surface a
finding that later gets filtered out than to silently drop a real bug. For each finding,
include your confidence level and an estimated severity so a downstream filter can rank
them.
```

**For single-pass self-filtering, be specific about the threshold:**

Instead of "report only important issues," use: "Report any bug that could cause incorrect behavior, test failures, or misleading results; only ignore purely stylistic or naming preferences."

---

## Interactive vs Autonomous Coding

Opus 4.8 uses more tokens in interactive (multi-turn) sessions because it reasons more after each user turn. To maximize performance and token efficiency:

- Use `xhigh` or `high` effort.
- Add autonomous features (auto-mode) to reduce required human interactions.
- Front-load clear, complete task specifications in the first human turn.

Vague or under-specified prompts delivered over multiple turns tend to reduce both token efficiency and performance.

---

## Computer Use

Supports resolutions up to 2576px / 3.75MP. Internal testing shows 1080p offers good performance/cost balance. For cost-sensitive workloads, 720p or 1366x768 are strong lower-cost options. Experiment with effort levels to tune behavior.

~~~

##### SKILLS\prompt-engineering.md

~~~markdown
---
name: prompt-engineering
description: >-
  Guide prompt engineering work. Use when writing, reviewing, or improving
  prompts for LLMs — including system prompts, user messages, tool descriptions,
  or any structured instructions sent to an AI model.
---

# Prompt Engineering

## Prompt Construction Checklist

Before finalizing any prompt, walk through these steps:

1. **Define the goal** — What exact output do you need? (format, length, style)
2. **Assign a role** — Would a persona improve quality? Set it in the system prompt.
3. **Provide context** — Include all necessary background. Omit nothing the model needs.
4. **Separate data from instructions** — Wrap user-supplied data in XML tags.
5. **Specify the format** — State the desired output structure explicitly.
6. **Add examples** — Include 2-3 input/output pairs for non-trivial formats.
7. **Enable thinking** — For complex reasoning, ask the model to think step-by-step.
8. **Add constraints** — State what NOT to do. Give escape hatches ("say I don't know").
9. **Colleague test** — If a colleague couldn't follow your prompt, rewrite it.

---

## Core Techniques

### 1. Basic Prompt Structure (API Format)

Messages API requires: `model`, `max_tokens`, `messages` array.

```json
{
  "model": "claude-sonnet-4-20250514",
  "max_tokens": 1024,
  "system": "System-level instructions here.",
  "messages": [
    {"role": "user", "content": "User message"},
    {"role": "assistant", "content": "Assistant response"}
  ]
}
```

Rules:
- User/assistant turns **must alternate** — never two user or two assistant messages in a row.
- **System prompt** is separate from messages; use it for persistent context, role, and constraints.
- First message must be `user`; use system prompt instead of a leading assistant message.

### 2. Be Clear and Direct

**Golden Rule**: Show your prompt to a colleague. If they'd be confused, the model will be too.

- Be explicit: "Respond with ONLY a JSON object" not "give me JSON".
- Remove ambiguity: "List exactly 3 bullet points" not "list some points".
- Suppress preamble: "Skip the preamble. Start directly with the answer."
- One ask per sentence. Don't bury instructions in long paragraphs.

### 3. Role Prompting

Roles change tone, depth, accuracy, and style.

Set roles in the system prompt:

```
You are a senior security engineer reviewing code for vulnerabilities.
Focus on OWASP Top 10 issues. Be thorough and cite specific line numbers.
```

Effective role patterns:
- **Expert**: "You are a world-class data scientist..."
- **Audience-aware**: "Explain to a 5-year-old..."
- **Logic enforcer**: "You are a logic bot. Only draw conclusions supported by the premises."
- **Persona**: "You are a terse unix sysadmin. Answer in short commands."

### 4. Separating Data from Instructions

Use XML tags to delineate user data from instructions. This prevents the model from confusing data with commands.

```
Summarize the following article in 2 sentences.

<article>
{{ARTICLE_TEXT}}
</article>
```

Guidelines:
- Use descriptive tag names: `<document>`, `<email>`, `<code>`, `<query>`.
- Use template variables (`{{VAR}}`) for dynamic content.
- **Small details matter** — typos, inconsistent formatting, and sloppy structure degrade output quality.

### 5. Formatting Output

**Request structured output** by naming the format explicitly:

```
Extract the name, date, and amount. Return as JSON:
{"name": "...", "date": "...", "amount": "..."}
```

**Use XML tags in output** for parseable multi-part responses:

```
Respond in this format:
<summary>one-paragraph summary</summary>
<key_points>bullet list of key points</key_points>
<action_items>numbered action items</action_items>
```

**Prefill the assistant turn** to force format compliance:

```json
{"role": "assistant", "content": "{"}
```

This forces JSON output by starting with `{`.

**Use `stop_sequences`** to cut output at a closing tag:

```json
{"stop_sequences": ["</answer>"]}
```

### 6. Thinking Step-by-Step (Precognition)

Let the model reason before answering — dramatically improves accuracy on complex tasks.

```
<brainstorm>
Think through possible approaches before answering.
</brainstorm>

Now provide your final answer.
```

Key rules:
- Thinking only works when it's "out loud" — the model must write reasoning in the output.
- Wrap thinking in tags (`<thinking>`, `<brainstorm>`, `<analysis>`) so you can strip it later.
- **Ordering bias**: when comparing two options, the model may favor the second. Mitigate by asking it to consider both before deciding.
- Use structured thinking tags: `<pros>`, `<cons>`, `<evidence>`, `<conclusion>`.

### 7. Few-Shot Examples

Provide input/output pairs to demonstrate desired behavior. More effective than lengthy descriptions for tone, format, and edge cases.

```
Classify the sentiment of each review.

<example>
<input>The food was terrible and the service was slow.</input>
<output>Negative</output>
</example>

<example>
<input>Absolutely loved the ambiance and the pasta was divine!</input>
<output>Positive</output>
</example>

Now classify:
<input>It was okay, nothing special but not bad either.</input>
```

Tips:
- 2-3 examples is usually enough; add more for subtle distinctions.
- Include edge cases in examples.
- Examples set format, tone, and length simultaneously.

### 8. Avoiding Hallucinations

- **Grant permission to abstain**: "If you don't know, say 'I don't have enough information.'"
- **Quote-first pattern**: "Find a direct quote from the document that supports your answer. If no quote exists, say so."
- **Ground in evidence**: Pass source documents in context and instruct the model to only use provided information.
- **Cite sources**: "After each claim, cite the source in [brackets]."

```
Answer the question based ONLY on the provided documents.
If the documents don't contain the answer, say "Not found in provided documents."

<documents>
{{DOCS}}
</documents>

Question: {{QUESTION}}
```

### 9. Complex Prompt Assembly

Combine techniques in this order:

```
[SYSTEM PROMPT]
  1. Role assignment
  2. Context / background
  3. Global constraints

[USER MESSAGE]
  4. Task description
  5. Input data (in XML tags)
  6. Output format specification
  7. Examples (few-shot)
  8. Edge case instructions
  9. Thinking instructions (if needed)
```

Build iteratively: start with a simple prompt, test, then layer in techniques to fix failure modes.

---

## Reusable Prompt Patterns

### Pattern 1: Structured Extraction

```
You are a data extraction specialist.

Extract the following fields from the provided text. Return as JSON.
If a field is not found, use null.

Fields: {{FIELD_LIST}}

<source>
{{INPUT_TEXT}}
</source>

Respond with ONLY the JSON object, no commentary.
```

### Pattern 2: Grounded Q&A (Anti-Hallucination)

```
Answer the question using ONLY the provided context.
First, find a direct quote that supports your answer.
If no supporting evidence exists, respond: "Not found in provided context."

<context>
{{DOCUMENTS}}
</context>

<question>{{QUESTION}}</question>

<evidence>relevant quote from context</evidence>
<answer>your answer based on the evidence</answer>
```

### Pattern 3: Step-by-Step Analysis

```
Analyze the following {{SUBJECT}}.

<input>
{{DATA}}
</input>

<thinking>
Walk through your reasoning step by step.
Consider edge cases and potential issues.
</thinking>

<answer>
Provide your final analysis with:
1. Summary of findings
2. Key issues identified
3. Recommended actions
</answer>
```

### Pattern 4: Classification with Examples

```
Classify the input into one of these categories: {{CATEGORIES}}.

<example>
<input>{{EXAMPLE_1_INPUT}}</input>
<category>{{EXAMPLE_1_CATEGORY}}</category>
<reasoning>{{BRIEF_REASON}}</reasoning>
</example>

<example>
<input>{{EXAMPLE_2_INPUT}}</input>
<category>{{EXAMPLE_2_CATEGORY}}</category>
<reasoning>{{BRIEF_REASON}}</reasoning>
</example>

Now classify:
<input>{{NEW_INPUT}}</input>
```

### Pattern 5: Iterative Refinement

```
Review the following {{ARTIFACT_TYPE}} and suggest improvements.

<artifact>
{{CONTENT}}
</artifact>

<criteria>
{{QUALITY_CRITERIA}}
</criteria>

Respond in this format:
<assessment>Overall quality rating (1-5) and brief justification</assessment>
<issues>List of specific issues found</issues>
<revised>The improved version incorporating all fixes</revised>
```

### Pattern 6: Tool Description Template

```json
{
  "name": "tool_name",
  "description": "One clear sentence: what it does and when to use it. Include edge cases.",
  "input_schema": {
    "type": "object",
    "properties": {
      "param_name": {
        "type": "string",
        "description": "What this parameter controls. Include valid values or constraints."
      }
    },
    "required": ["param_name"]
  }
}
```

Write tool descriptions as if for a colleague who has never seen the tool.

---

## Advanced Techniques

### Prompt Chaining

Break complex tasks into subtasks. Pass output of one call as input to the next.

```
Step 1: Extract key facts    → facts
Step 2: Analyze facts         → analysis (receives facts)
Step 3: Generate report       → report (receives analysis)
```

Each step gets the model's full attention on a narrower task. Chaining beats a single mega-prompt when:
- The task has distinct phases (extract → transform → generate).
- Intermediate results need validation.
- Different steps need different system prompts or temperatures.

### Tool Use (Function Calling)

Define tools with `name`, `description`, and `input_schema`. The model decides when to call a tool based on the user's request.

Flow:
1. Send user message + tool definitions.
2. Model returns `tool_use` content block with tool name and arguments.
3. Your code executes the tool, returns result as `tool_result`.
4. Model incorporates the result and continues.

Write tool descriptions as precisely as prompts — vague descriptions lead to wrong tool selection.

### Retrieval-Augmented Generation (RAG)

Combine retrieval with generation:

1. **Retrieve** relevant documents from a vector store or search index.
2. **Inject** retrieved content into the prompt context using XML tags.
3. **Instruct** the model to answer only from provided evidence.
4. **Require citations** — "cite the document name after each claim."

```
<retrieved_documents>
<doc source="annual_report_2024.pdf" page="12">{{CHUNK}}</doc>
<doc source="policy_v3.md" section="4.2">{{CHUNK}}</doc>
</retrieved_documents>

Using ONLY the documents above, answer: {{QUESTION}}
Cite sources after each statement as [source, page/section].
If the answer is not in the documents, say "Not found."
```

### Prompt Review Checklist

When reviewing an existing prompt, check for:

- [ ] **Ambiguity** — Could any instruction be interpreted two ways?
- [ ] **Missing context** — Does the model have all info it needs?
- [ ] **Conflicting instructions** — Do any rules contradict each other?
- [ ] **Format specification** — Is the expected output format clear?
- [ ] **Edge cases** — What happens with empty input, long input, or adversarial input?
- [ ] **Hallucination guardrails** — Can the model say "I don't know"?
- [ ] **Example coverage** — Do examples cover the main cases and at least one edge case?
- [ ] **Token efficiency** — Can you say the same thing in fewer words without losing clarity?

~~~

##### 自研/SKILL-creator v0.2.0 的代码架构、工作流

代码结构（34 文件）：

```
skill-creator/
├── .cursor-plugin/
│   └── plugin.json                    # 插件元数据 v0.2.0（5 commands 注册）
├── bootstrap.ps1                      # 一行命令安装入口（Windows）
├── bootstrap.sh                       # 一行命令安装入口（macOS/Linux）
├── install.ps1                        # 全局指针注册（PowerShell）
├── install.sh                         # 全局指针注册（Bash 3.2+ 兼容）
├── CHANGELOG.md                       # 版本变更记录
├── README.md                          # 插件文档
├── config/
│   └── defaults.json                  # agent 模型 + lint 规则 + fix/extract 配置
├── setup/
│   └── SKILL.md                       # /SKILL-setup 引导式安装
├── commands/
│   ├── SKILL-creator.md               # /SKILL-creator 入口
│   ├── SKILL-lint.md                  # /SKILL-lint 入口
│   ├── SKILL-fix.md                   # /SKILL-fix 入口
│   └── SKILL-pythonGenerator.md       # /SKILL-pythonGenerator 入口
├── skills/
│   └── skill-creator/
│       ├── SKILL.md                   # 主编排（320 行）— 生命周期 + 6 阶段 + 命令路由
│       ├── agents/
│       │   ├── linter.md              # lint 子 agent — 9 维度审计
│       │   ├── fixer.md               # fix 子 agent — 分类修复 + diff
│       │   ├── extractor.md           # extract 子 agent — 模式检测
│       │   ├── tester.md              # test 子 agent — 并行执行
│       │   ├── grader.md              # 评分 agent — 逐条断言 PASS/FAIL
│       │   ├── comparator.md          # 盲比 agent — A/B 随机标签 + 5 维评分
│       │   └── analyzer.md            # 分析 agent — 隐藏模式发现
│       └── references/
│           ├── writing-guide.md       # 6 条提示词工程写作技巧
│           ├── lint-rules.md          # 9 维度评分标准 + 报告格式
│           ├── fix-report-format.md   # fix 操作报告格式
│           ├── extraction-patterns.md # 可提取模式目录
│           ├── eval-workflow.md       # 评测协议（7 步 + 停止条件）
│           ├── schemas.md             # JSON schema 定义
│           └── setup-checklist.md     # 安装检查清单
├── scripts/
│   ├── migrate-v1.py                  # v0.1→v0.2 迁移脚本
│   ├── aggregate_benchmark.py         # 聚合评分为 benchmark.json
│   └── generate_review.py            # 生成 HTML 结果查看器
└── tests/
    ├── test-lint.md                   # lint 集成测试步骤
    ├── test-fix.md                    # fix 集成测试步骤
    ├── test-extract.md                # extract 集成测试步骤
    ├── test-setup.md                  # setup 集成测试步骤
    ├── test-creator.md                # creator 集成测试步骤
    └── sample-skills/
        ├── good-skill.md              # 合规样本
        ├── bad-language.md            # 语言违规样本
        ├── bad-template.md            # 模板违规样本
        └── extractable-pair/          # 可提取重复模式样本
            ├── skill-deploy-staging.md
            └── skill-deploy-production.md
```

---

工作流：

**整体命令路由：**

```
用户输入 /SKILL-xxx
        │
        ├── /SKILL-creator  → 主编排（§1-§6 生命周期）
        ├── /SKILL-lint     → lint 子 agent（9 维度审计）
        ├── /SKILL-fix      → fixer 子 agent（逻辑→格式，2 轮）
        ├── /SKILL-pythonGenerator → extractor 子 agent（模式提取）
        └── /SKILL-setup    → 环境检测 → 安装/升级/配置
```

**SKILL-creator 主工作流（eval-driven 全生命周期）：**

```
用户输入 /SKILL-creator
        │
        ▼
┌─ §1 生命周期检测 + 命令路由 ───────────────────┐
│  优先检测命令关键词（lint/fix/extract/setup）    │
│  → 匹配则路由到对应命令文件                      │
│                                                  │
│  否则检查 workspace 目录状态：                    │
│  • 目录不存在        → NEW     → §2             │
│  • 有 SKILL.md 无 evals/ → DRAFT  → 问用户选择  │
│  • 有 evals/ 无 benchmark → TESTING_INCOMPLETE   │
│  • 有 benchmark.json  → TESTED → 问用户选择      │
└─────────────────────────────────────────────────┘
        │
        ▼ (NEW)
┌─ §2 意图采集 ──────────────────────────────────┐
│  6 个结构化问题（AskQuestion 或对话）：           │
│  Q1 用途  Q2 触发场景  Q3 输出格式               │
│  Q4 领域知识  Q5 现有模式  Q6 存放位置           │
│  → 输出 Intent Summary → 用户确认               │
└─────────────────────────────────────────────────┘
        │
        ▼
┌─ §3 起草 SKILL.md ─────────────────────────────┐
│  3.1 创建 workspace 目录                        │
│  3.2 写 frontmatter（pushy description）        │
│  3.3 写正文（遵循 writing-guide 6 条原则）       │
│  3.4 超 400 行则抽取 references/                │
│  3.5 重复代码模式打包为 scripts/                 │
│  3.6 自检 7 项 checklist → 呈现给用户           │
│  3.7 自动触发 lint → 确保出厂质量               │
└─────────────────────────────────────────────────┘
        │
        ▼
┌─ §4 测试执行 ──────────────────────────────────┐
│  4.1 定义 3-5 个测试用例 → evals/evals.json     │
│  4.2 同一轮启动 2×N 个 Task subagent（并行）     │
│      每个用例：with_skill + without_skill        │
│  4.3 subagent 完成时记录 timing.json             │
│  4.4 全部完成后启动 grader subagent（也是并行）   │
│  4.5 聚合 → benchmark.json                      │
│  4.6 Canvas 或 markdown 展示结果                 │
│  → 回到 §1 让用户选择下一步                      │
└─────────────────────────────────────────────────┘
        │
        ▼ (用户选 Iterate)
┌─ §5 迭代改进 ──────────────────────────────────┐
│  5.1 读取反馈（benchmark 数据 + 用户评语）       │
│  5.2 识别可泛化模式（不过拟合）                   │
│  5.3 改进 SKILL.md                              │
│  5.4 版本快照 → history.json                    │
│  5.5 重新跑 §4 测试                             │
│  5.6 可选：盲 A/B 对比（comparator + analyzer）  │
│                                                  │
│  停止条件：                                      │
│  • pass_rate > 90% 且 delta > 15%               │
│  • 连续两轮 < 2% 提升                           │
│  • 用户满意                                      │
│  • 已达 5 轮迭代                                 │
└─────────────────────────────────────────────────┘
        │
        ▼ (用户选 Optimize description)
┌─ §6 描述优化 ──────────────────────────────────┐
│  6.1 生成 20 条查询（10 应触发 + 10 不应触发）   │
│  6.2 70/30 分为训练集 / 测试集                   │
│  6.3 在训练集上评估当前描述（TP/FP/TN/FN）       │
│  6.4 最多 5 轮迭代改进描述                       │
│  6.5 用测试集选出最佳描述 → 更新 frontmatter     │
└─────────────────────────────────────────────────┘
```

**SKILL-lint 工作流：**

```
/SKILL-lint [path|--all]
        │
        ▼
确定范围（单文件 / 目录 / 全部 skill）
        │
        ▼
对每个 skill 启动 linter 子 agent（Haiku, 并行）
        │
        ▼
9 维度逐项评分（0-10）→ 加权总分
        │
        ▼
输出报告：
  • 总分 + 等级（A/B/C/D/F）
  • 逐维度得分 + 扣分原因
  • 修复建议（附行号）
```

**SKILL-fix 工作流：**

```
/SKILL-fix [file]
        │
        ▼
读取已有 lint 报告（无则现场 lint）
        │
        ▼
fixer 子 agent 分类 issues：
  • logic（逻辑/缺失/矛盾）→ 优先修复
  • format（语言/行数/模板）→ 后续强制
        │
        ▼
生成 diff 预览 → 用户确认
        │
        ▼
应用修改 → 自动重新 lint
        │
        ▼
仍有 issues? → 第 2 轮（最多 2 轮）
        │
        ▼
输出 fix 报告（已修/未修/需人工）
```

**SKILL-pythonGenerator 工作流：**

```
/SKILL-pythonGenerator [scope]
        │
        ▼
扫描指定 skill 或全部 skill
        │
        ▼
extractor 子 agent 检测模式：
  • 数据聚合（多源 → 结构化）
  • 格式转换（JSON/YAML/CSV）
  • 验证逻辑（schema check）
  • 报告生成（模板填充）
  • API 调用编排
        │
        ▼
满足阈值（≥2 skill × ≥3 步骤）?
        │  是                    │ 否
        ▼                       ▼
生成 Python CLI 脚本      报告"无可提取模式"
（argparse + docstring
 + type hints）
        │
        ▼
写入 scripts/ → 更新引用 skill
```

