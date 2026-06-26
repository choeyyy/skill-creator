# Setup Environment Checklist

Pre-installation verification for skill-creator plugin.

---

## Required

| # | Requirement | Verify (Windows) | Verify (macOS/Linux) | Fix |
|---|-------------|-------------------|---------------------|-----|
| 1 | Cursor IDE installed | `Test-Path "$env:USERPROFILE\.cursor"` | `test -d "$HOME/.cursor"` | Download from cursor.com |
| 2 | Git in PATH | `git --version` → 2.x+ | `git --version` → 2.x+ | Install from git-scm.com |
| 3 | Shell available | PowerShell runs (default on Win) | `bash --version` or `zsh --version` | Pre-installed on modern OS |
| 4 | Internet access | `git ls-remote https://github.com/choeyyy/skill-creator.git` | same | Check proxy/firewall |
| 5 | Skills dir writable | `New-Item -ItemType File "$env:USERPROFILE\.cursor\skills\.write-test" -Force` then remove | `touch "$HOME/.cursor/skills/.write-test" && rm ...` | Fix permissions: `chmod 755 ~/.cursor/skills` |

## Optional

| # | Requirement | Verify | Purpose |
|---|-------------|--------|---------|
| 6 | Python 3.8+ | `python --version` / `python3 --version` | For validate-skill.py and extraction scripts |
| 7 | Node.js 18+ | `node --version` | For future plugin extensions |

---

## Conflict Checks

Before install, verify no conflicting skill pointers exist:

1. Check `~/.cursor/skills/SKILL-lint/SKILL.md` — if it exists but its description does NOT mention "skill-creator" or "Audit Skill", it belongs to a standalone old install and needs migration.
2. Check `~/.cursor/skills/skill-creator/SKILL.md` — if it exists but points to a different repo/path, user must choose which to keep.
3. No two plugins should write to the same pointer directory.

---

## Post-Install Verification

After `/SKILL-setup` completes, confirm:

| # | Check | Expected |
|---|-------|----------|
| 1 | Pointer files exist | 5 directories under `~/.cursor/skills/`: SKILL-setup, skill-creator, SKILL-lint, SKILL-fix, SKILL-pythonGenerator |
| 2 | Pointers readable | Each contains valid YAML frontmatter and path to plugin source |
| 3 | Config loaded | `<PLUGIN_DIR>/config/defaults.json` exists and is valid JSON |
| 4 | Git repo intact | `git -C <PLUGIN_DIR> status` returns clean |
| 5 | Commands respond | Restart Cursor → type `/skill-creator` → agent activates |

---

## Upgrade Verification

When updating an existing install:

1. `git -C <PLUGIN_DIR> log HEAD..origin/main --oneline` shows commits pulled
2. Pointer files still resolve correctly (paths unchanged)
3. `config/defaults.json` preserved (git pull doesn't overwrite local changes unless conflicted)
