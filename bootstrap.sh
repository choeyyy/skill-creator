#!/usr/bin/env bash
# skill-creator bootstrap (Linux / macOS)
# Downloads only the setup skill so user can run /SKILL-setup in Cursor.
# Usage: curl -sL https://raw.githubusercontent.com/choeyyy/skill-creator/main/bootstrap.sh | bash

set -euo pipefail

SKILL_DIR="${HOME}/.cursor/skills/SKILL-setup"
SKILL_FILE="${SKILL_DIR}/SKILL.md"
RAW_URL="https://raw.githubusercontent.com/choeyyy/skill-creator/main/setup/SKILL.md"

if [ ! -d "${HOME}/.cursor" ]; then
    echo "[ERROR] Cursor directory not found. Please install Cursor first."
    exit 1
fi

if ! command -v git &>/dev/null; then
    echo "[ERROR] git is required. Please install git first."
    exit 1
fi

if ! command -v curl &>/dev/null; then
    echo "[ERROR] curl is required. Please install curl first."
    exit 1
fi

mkdir -p "${SKILL_DIR}"

if curl -sfL -o "${SKILL_FILE}" "${RAW_URL}"; then
    echo ""
    echo "[ok] SKILL-setup skill installed."
    echo ""
    echo "Next: open Cursor, type /SKILL-setup to install the full plugin."
    echo ""
else
    echo "[ERROR] Failed to download setup skill."
    exit 1
fi
