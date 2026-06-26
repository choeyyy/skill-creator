# Test: /SKILL-setup

## Prerequisites

- Cursor IDE installed
- git installed
- Internet access (for GitHub clone)

## Test 1 — Fresh install

1. Ensure no skill-creator pointers exist in `~/.cursor/skills/`
2. Run `/SKILL-setup`
3. **Expected**:
   - Environment checks run (OS, git, Cursor dir, write permission, Python)
   - Results presented in the `环境检查` format
   - Agent asks for install location (shows default path)
   - After confirming, clones from GitHub
   - Creates 5 skill pointers in `~/.cursor/skills/`
   - Verification table shows all `[ok]`
   - Proceeds to model/lint configuration
4. **Failure**: Skips env check; clones without asking location; missing pointers

## Test 2 — Already installed (check for updates)

1. With skill-creator already installed, run `/SKILL-setup`
2. **Expected**: Detects existing install (Case B), runs `git fetch`, reports whether updates are available
3. **Failure**: Treats as fresh install and overwrites

## Test 3 — Partial install

1. Delete 2 of the 5 skill pointers from `~/.cursor/skills/`
2. Run `/SKILL-setup`
3. **Expected**: Detects partial install (Case C), asks "检测到部分安装，是否补全？", recreates missing pointers only
4. **Failure**: Reinstalls everything or misses the partial state

## Test 4 — Uninstall

1. Run `/SKILL-setup` and say "卸载"
2. **Expected**: Jumps to Step 8, shows confirmation prompt listing what will be deleted, waits for confirmation. On confirm: deletes 5 pointers + plugin dir, shows completion report
3. **Failure**: Deletes without confirmation; leaves orphaned files

## Test 5 — Missing git

1. Temporarily rename git executable (or use a machine without git)
2. Run `/SKILL-setup`
3. **Expected**: Environment check fails on git, agent STOPs with "需要安装 git" message
4. **Failure**: Agent continues despite missing git

## Checklist

- [ ] Environment check runs all 5 probes
- [ ] All 4 detection cases (A/B/C/D) handled correctly
- [ ] Pointer files use forward slashes in paths
- [ ] Uninstall requires explicit confirmation
- [ ] Configuration step offers model and lint-rule customization
