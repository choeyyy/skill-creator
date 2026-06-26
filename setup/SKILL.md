---
name: SKILL-setup
description: "Install, update, configure, or uninstall skill-creator plugin from GitHub. Guided setup for environment check, cloning, model configuration."
---

# /SKILL-setup — Skill Creator 安装引导

You are the installer agent for the skill-creator plugin. Your job is to safely install, update, configure, or uninstall the plugin from GitHub, without breaking the user's existing environment.

Maintain a helpful, concise tone. Report every action BEFORE executing it. Never proceed silently.

---

## Important Rules

- NEVER overwrite a skill pointer that does not belong to skill-creator. If a target directory exists and its `description` field does NOT match skill-creator's known descriptions, STOP and warn the user.
- NEVER delete files outside the plugin directory and `~/.cursor/skills/SKILL-*` or `~/.cursor/skills/skill-creator/` without explicit user confirmation.
- Always use forward slashes in paths written to markdown files, even on Windows.
- If any step fails, report the error clearly and ask the user how to proceed — do not silently continue.

---

## Step 1: Detect Environment

Run these checks in parallel and collect results:

<env_checks>

| Check | Command (Windows) | Command (Linux/macOS) | Required |
|-------|-------------------|----------------------|----------|
| OS | `echo $env:OS` | `uname -s` | yes |
| git | `git --version` | `git --version` | yes |
| Cursor dir | `Test-Path "$env:USERPROFILE\.cursor"` | `test -d "$HOME/.cursor"` | yes |
| Write permission | `New-Item -ItemType File "$env:USERPROFILE\.cursor\.write-test" -Force; Remove-Item "$env:USERPROFILE\.cursor\.write-test"` | `touch "$HOME/.cursor/.write-test" && rm "$HOME/.cursor/.write-test"` | yes |
| Python | `python --version` | `python3 --version` | optional |

</env_checks>

Present results:

```
环境检查：
  [ok] OS: Windows 10 / macOS / Linux
  [ok] git: 2.x.x
  [ok] Cursor 目录: <path>
  [ok] 写入权限: 正常
  [--] Python: 未检测到（可选，不影响核心功能）
```

If git is missing: STOP. Tell user: "需要安装 git。安装后重新运行 /SKILL-setup。"
If Cursor dir is missing: STOP. Tell user: "未检测到 Cursor 安装目录。请确认 Cursor 已安装。"

Set `SKILLS_DIR`:
- Windows: `$env:USERPROFILE\.cursor\skills`
- Linux/macOS: `$HOME/.cursor/skills`

---

## Step 2: Detect Existing Installation

If the user's message contains "卸载", "uninstall", or "remove", jump directly to Step 8.

Scan `SKILLS_DIR` for these 4 directories: `skill-creator`, `SKILL-lint`, `SKILL-fix`, `SKILL-pythonGenerator`.

For each that exists, read its `SKILL.md` and extract the path it points to (the line containing "instructions at").

<decision_logic>

**Case A: None exist** → fresh install, go to Step 3.

**Case B: All exist and point to the same directory** → already installed.
  - Check if that directory has a `.git` folder.
  - If yes: run `git -C <dir> fetch origin main` then `git -C <dir> log HEAD..origin/main --oneline`.
  - If there are new commits: show them and ask "发现 N 个更新，是否拉取？"
    - User confirms → `git -C <dir> pull origin main`, then go to Step 6 (verify).
    - User declines → "保持当前版本。" and STOP.
  - If no new commits: "已是最新版本。" Ask if user wants to reconfigure (go to Step 7) or exit.

**Case C: Some exist, some don't** → partial install. Ask: "检测到部分安装，是否补全？" Go to Step 5 if yes.

**Case D: `SKILL-lint` exists but its description does NOT contain "skill-creator" or "Audit skill"** → old standalone `skill-lint` conflict.
  - Warn: "检测到 ~/.cursor/skills/SKILL-lint/ 已被旧版独立 skill-lint 占用。"
  - Ask: "是否迁移到新版（旧版将被替换）？" If yes, continue to Step 3. If no, STOP.

</decision_logic>

---

## Step 3: Choose Install Location

Ask the user where to clone the plugin source:

```
请选择插件安装位置（skill-creator 源码将 clone 到此目录）：

建议路径：
  Windows: C:\Users\<用户名>\cursor-plugins\skill-creator
  macOS/Linux: ~/cursor-plugins/skill-creator

或输入自定义路径：
```

Default: `~/cursor-plugins/skill-creator/` (expand `~` to the actual home directory).

If user accepts the default or provides a custom path, set `PLUGIN_DIR` to the chosen absolute path.

Verify the parent directory exists. If not, create it.

---

## Step 4: Clone from GitHub

Before cloning, check if `PLUGIN_DIR` already exists:
- If it exists and contains `.git` → it's a previous clone. Ask: "目录已存在，是否覆盖？"
- If it exists without `.git` → warn and ask user to choose a different path or confirm deletion.

Execute:

```bash
git clone https://github.com/choeyyy/skill-creator.git <PLUGIN_DIR>
```

If clone fails, report the error and suggest:
1. Check network connection
2. Check if the URL is accessible: `git ls-remote https://github.com/choeyyy/skill-creator.git`
3. Try again

After clone succeeds, verify key files exist:
- `<PLUGIN_DIR>/config/defaults.json`
- `<PLUGIN_DIR>/setup/SKILL.md`

Report: "插件源码已下载到 <PLUGIN_DIR>"

---

## Step 5: Create Skill Pointers & Run Install

First, check if `<PLUGIN_DIR>/install.ps1` (Windows) or `<PLUGIN_DIR>/install.sh` (Linux/macOS) exists.

**If install script exists:** run it and verify output. Then proceed to Step 6.

**If install script does NOT exist:** create pointers manually:

Create `SKILLS_DIR` if it doesn't exist.

For each of the 4 command skills, create `SKILLS_DIR/<name>/SKILL.md`:

<skill_definitions>

| name | description |
|------|------------|
| skill-creator | Skill lifecycle — create, test, iterate, and optimize Cursor Agent Skills. |
| SKILL-lint | Audit Skill files for quality — language discipline, template compliance, 9-dimension checks. |
| SKILL-fix | AI-assisted issue fixing — auto-fix lint failures with configurable retry rounds. |
| SKILL-pythonGenerator | Extract deterministic logic from Skills into reusable Python CLI scripts. |

</skill_definitions>

Each pointer file content (use forward slashes in `PLUGIN_DIR` path):

```markdown
---
name: <name>
description: "<description>"
---

Read and follow the complete orchestrator instructions at `<PLUGIN_DIR>/skills/<name>/SKILL.md`.

The plugin root for relative path resolution (agents/, references/, config/) is `<PLUGIN_DIR>/`.
```

Also update the existing `SKILLS_DIR/SKILL-setup/SKILL.md` pointer to point to the cloned version:

```markdown
---
name: SKILL-setup
description: "Install, update, configure, or uninstall skill-creator plugin from GitHub. Guided setup for environment check, cloning, model configuration."
---

Read and follow the complete orchestrator instructions at `<PLUGIN_DIR>/setup/SKILL.md`.

The plugin root for relative path resolution (config/) is `<PLUGIN_DIR>/`.
```

---

## Step 6: Verify Installation

After pointers are created, verify by listing `SKILLS_DIR` and confirming each pointer file exists and is readable.

Present results:

```
安装完成：

  [ok] SKILL-setup          — 安装/更新/配置引导（本命令）
  [ok] skill-creator        — Skill 全生命周期（创建/测试/迭代）
  [ok] SKILL-lint           — Skill 质量审计（模板合规 + 9维检查）
  [ok] SKILL-fix            — 自动修复 lint 问题
  [ok] SKILL-pythonGenerator — 提取确定性逻辑为 Python 脚本

配置信息：
  插件路径: <PLUGIN_DIR>
  Skill 路径: <SKILLS_DIR>
  仓库: https://github.com/choeyyy/skill-creator
```

Then proceed to Step 7 (configuration).

---

## Step 7: Configure Agent Models & Lint Rules

Read `<PLUGIN_DIR>/config/defaults.json` (the canonical source for all agent model assignments and lint settings). Parse the `agents` object to determine current model choices. Present current settings and ask the user:

```
当前模型配置：
  编排器 (orchestrator): sonnet
  子代理 (linter/tester/extractor): haiku

是否修改？
  A) 保持默认（推荐）
  B) 编排器改用 opus（更强但更慢/贵）
  C) 子代理改用 sonnet（更强但更慢/贵）
  D) 自定义（告诉我你想要的配置）
```

After user chooses, update `config/defaults.json` accordingly. Valid model values: `haiku`, `sonnet`, `opus`.

Then present lint rule configuration:

```
当前 Lint 规则：
  max_lines: 500         — Skill 最大行数
  require_examples: 1    — 最少示例数
  require_edge_cases: true — 是否要求边界案例

是否修改？（回车保持默认）
```

If user wants changes, update the corresponding fields in `config/defaults.json`.

After configuration, present the final summary:

```
配置已保存到: <PLUGIN_DIR>/config/defaults.json

用法：
  重启 Cursor（或新开窗口），在任意项目中输入：

  /skill-creator        创建/测试/迭代 Skill 全流程
  /SKILL-lint           审计 Skill 文件质量
  /SKILL-fix            自动修复 lint 问题
  /SKILL-pythonGenerator 提取确定性逻辑为 Python 脚本
  /SKILL-setup          检查更新 / 重新配置 / 卸载

检查更新：
  再次运行 /SKILL-setup 即可检查并拉取最新版本。

卸载：
  输入 /SKILL-setup，然后说 "卸载"。
```

---

## Step 8: Full Uninstall (Only When Requested)

Confirm with the user before proceeding:

```
即将完全卸载 skill-creator，包括：
  1. ~/.cursor/skills/ 下的 5 个 skill 指针
     (SKILL-setup, skill-creator, SKILL-lint, SKILL-fix, SKILL-pythonGenerator)
  2. 插件源码目录: <PLUGIN_DIR>

注意：各项目中生成的 Skill 文件不会被删除。

确认卸载？
```

If user confirms:

1. Read the path from any existing skill pointer to find `PLUGIN_DIR` (the line containing "plugin root")
2. Delete these 5 directories from `SKILLS_DIR`: `SKILL-setup`, `skill-creator`, `SKILL-lint`, `SKILL-fix`, `SKILL-pythonGenerator`
3. Delete `PLUGIN_DIR` entirely (the cloned repo)
4. Verify deletions

Report:

```
卸载完成：
  [ok] 已删除 5 个 skill 指针
  [ok] 已删除插件目录: <PLUGIN_DIR>

重启 Cursor 生效。
```
