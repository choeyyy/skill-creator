#!/usr/bin/env bash
# skill-creator install script (Linux / macOS)
# Usage: cd to skill-creator directory, then: bash install.sh
#        Uninstall: bash install.sh --uninstall

set -euo pipefail

PLUGIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="${HOME}/.cursor/skills"

if [ ! -f "${PLUGIN_DIR}/.cursor-plugin/plugin.json" ]; then
    echo "[ERROR] .cursor-plugin/plugin.json not found."
    echo "Please run this script from the skill-creator plugin directory."
    exit 1
fi

SKILL_NAMES=(SKILL-setup skill-creator SKILL-lint SKILL-fix SKILL-pythonGenerator)

SKILL_DESCS=(
    "Install, update, or configure the skill-creator plugin. Environment check, guided install, agent model selection."
    "Create, test, and iterate on Cursor Agent Skills with eval-driven development. Full lifecycle: intent capture, drafting, testing, grading, iteration, description optimization."
    "Audit Skill quality — language discipline (English body / Chinese output) + 9-dimension prompt-engineering template compliance. Parallel sub-agent dispatch for batch audit."
    "Auto-repair Skill issues — fix logic first, then enforce format (English, Chinese summary, template, 500-line limit). Deterministic validation + diff confirmation."
    "Extract deterministic/repetitive logic from Skills into reusable Python CLI scripts. Single-skill or cross-skill scan."
)

SKILL_PATHS=(
    "setup/SKILL.md"
    "skills/skill-creator/SKILL.md"
    "commands/SKILL-lint.md"
    "commands/SKILL-fix.md"
    "commands/SKILL-pythonGenerator.md"
)

if [ "${1:-}" = "--uninstall" ]; then
    echo ""
    echo "=== Uninstalling skill-creator ==="
    for name in "${SKILL_NAMES[@]}"; do
        dir="${SKILLS_DIR}/${name}"
        if [ -d "$dir" ]; then
            rm -rf "$dir"
            echo "  Removed: $dir"
        fi
    done
    echo ""
    echo "Uninstall complete. Restart Cursor to take effect."
    exit 0
fi

echo ""
echo "=== Installing skill-creator ==="
echo "Plugin directory: ${PLUGIN_DIR}"
echo "Skills directory: ${SKILLS_DIR}"

mkdir -p "${SKILLS_DIR}"

created=0
skipped=0

for i in "${!SKILL_NAMES[@]}"; do
    name="${SKILL_NAMES[$i]}"
    skill_dir="${SKILLS_DIR}/${name}"
    skill_file="${skill_dir}/SKILL.md"
    mkdir -p "$skill_dir"

    if [ -f "$skill_file" ] && grep -qF "${PLUGIN_DIR}" "$skill_file" 2>/dev/null; then
        echo "  [skip] ${name} -- already installed with current path"
        ((skipped++)) || true
        continue
    fi

    # v0.1.0 upgrade: pointer exists but points to a different (old) path — overwrite
    if [ -f "$skill_file" ]; then
        echo "  [upgrade] ${name} -- updating pointer to current path"
    fi

    cat > "$skill_file" << SKILLEOF
---
name: ${name}
description: "${SKILL_DESCS[$i]}"
---

Read and follow the complete orchestrator instructions at \`${PLUGIN_DIR}/${SKILL_PATHS[$i]}\`.

The plugin root for relative path resolution (agents/, references/) is \`${PLUGIN_DIR}/\`.
SKILLEOF

    echo "  [ok] ${name}"
    ((created++)) || true
done

echo ""
echo "=== Done ==="
echo "  Created: ${created} skill(s)"
echo "  Skipped: ${skipped} skill(s) (already installed)"
echo ""
echo "Restart Cursor (or open a new window) to activate."
echo "Then type /skill-creator in any project to start creating skills."
echo ""
