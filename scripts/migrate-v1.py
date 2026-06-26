#!/usr/bin/env python3
"""Migrate skill-creator pointers from v0.1.0 to v0.2.0.

v0.1.0 installed a single pointer: ~/.cursor/skills/skill-creator/SKILL.md
v0.2.0 requires 5 pointers: SKILL-setup, skill-creator, SKILL-lint, SKILL-fix,
SKILL-pythonGenerator.

Usage:
    python scripts/migrate-v1.py              # dry-run (preview changes)
    python scripts/migrate-v1.py --apply      # actually write files
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional

SKILLS = [
    {
        "name": "SKILL-setup",
        "desc": (
            "Install, update, or configure the skill-creator plugin. "
            "Environment check, guided install, agent model selection."
        ),
        "path": "setup/SKILL.md",
    },
    {
        "name": "skill-creator",
        "desc": (
            "Create, test, and iterate on Cursor Agent Skills with "
            "eval-driven development. Full lifecycle: intent capture, "
            "drafting, testing, grading, iteration, description optimization."
        ),
        "path": "skills/skill-creator/SKILL.md",
    },
    {
        "name": "SKILL-lint",
        "desc": (
            "Audit Skill quality \u2014 language discipline (English body / "
            "Chinese output) + 9-dimension prompt-engineering template "
            "compliance. Parallel sub-agent dispatch for batch audit."
        ),
        "path": "skills/skill-creator/SKILL.md",
    },
    {
        "name": "SKILL-fix",
        "desc": (
            "Auto-repair Skill issues \u2014 fix logic first, then enforce "
            "format (English, Chinese summary, template, 500-line limit). "
            "Deterministic validation + diff confirmation."
        ),
        "path": "skills/skill-creator/SKILL.md",
    },
    {
        "name": "SKILL-pythonGenerator",
        "desc": (
            "Extract deterministic/repetitive logic from Skills into "
            "reusable Python CLI scripts. Single-skill or cross-skill scan."
        ),
        "path": "skills/skill-creator/SKILL.md",
    },
]


class Action(NamedTuple):
    kind: str  # "create", "update", "skip"
    name: str
    detail: str


def detect_skills_dir() -> Path:
    """Return ~/.cursor/skills, platform-aware."""
    if sys.platform == "win32":
        base = Path(os.environ.get("USERPROFILE", Path.home()))
    else:
        base = Path.home()
    return base / ".cursor" / "skills"


def detect_plugin_dir() -> Path:
    """Resolve the plugin root from this script's location."""
    return Path(__file__).resolve().parent.parent


def extract_plugin_path(content: str) -> Optional[str]:
    """Pull the plugin root path out of an existing pointer file."""
    m = re.search(r"instructions at `(.+?)/(?:setup|skills)/", content)
    if m:
        return m.group(1)
    m = re.search(r"path resolution .+? is `(.+?)/`", content)
    if m:
        return m.group(1)
    return None


def render_pointer(name: str, desc: str, rel_path: str, plugin_dir: str) -> str:
    return (
        f"---\n"
        f"name: {name}\n"
        f'description: "{desc}"\n'
        f"---\n"
        f"\n"
        f"Read and follow the complete orchestrator instructions at `{plugin_dir}/{rel_path}`.\n"
        f"\n"
        f"The plugin root for relative path resolution (agents/, references/) is `{plugin_dir}/`.\n"
    )


def plan_migration(skills_dir: Path, plugin_dir: Path) -> List[Action]:
    actions: List[Action] = []
    plugin_dir_str = str(plugin_dir).replace("\\", "/")

    for skill in SKILLS:
        name = skill["name"]
        skill_file = skills_dir / name / "SKILL.md"

        if not skill_file.exists():
            actions.append(Action("create", name, "new pointer file"))
            continue

        content = skill_file.read_text(encoding="utf-8", errors="replace")
        existing_path = extract_plugin_path(content)

        if existing_path and existing_path == plugin_dir_str:
            actions.append(Action("skip", name, "already points to current plugin"))
            continue

        if existing_path:
            actions.append(
                Action("update", name, f"old path: {existing_path}")
            )
        else:
            actions.append(
                Action("update", name, "pointer format unrecognized, will overwrite")
            )

    return actions


def execute_migration(
    actions: List[Action], skills_dir: Path, plugin_dir: Path, apply: bool
) -> None:
    plugin_dir_str = str(plugin_dir).replace("\\", "/")
    skill_map: Dict[str, dict] = {s["name"]: s for s in SKILLS}

    creates = [a for a in actions if a.kind == "create"]
    updates = [a for a in actions if a.kind == "update"]
    skips = [a for a in actions if a.kind == "skip"]

    if not creates and not updates:
        print("\nNothing to migrate — all pointers are up to date.")
        return

    print(f"\n{'=== DRY RUN ===' if not apply else '=== APPLYING ==='}")
    print(f"Plugin directory : {plugin_dir_str}")
    print(f"Skills directory : {skills_dir}\n")

    for action in actions:
        prefix = {"create": "[+]", "update": "[~]", "skip": "[ ]"}[action.kind]
        label = {"create": "CREATE", "update": "UPDATE", "skip": "skip"}[action.kind]
        print(f"  {prefix} {action.name:.<30s} {label}  ({action.detail})")

    print(f"\n  Summary: {len(creates)} create, {len(updates)} update, {len(skips)} skip")

    if not apply:
        print("\n  This was a dry run. Re-run with --apply to write changes.")
        return

    for action in actions:
        if action.kind == "skip":
            continue
        s = skill_map[action.name]
        skill_dir = skills_dir / action.name
        skill_dir.mkdir(parents=True, exist_ok=True)
        content = render_pointer(s["name"], s["desc"], s["path"], plugin_dir_str)
        (skill_dir / "SKILL.md").write_text(content, encoding="utf-8")

    print(f"\n  Done — {len(creates) + len(updates)} pointer(s) written.")
    print("  Restart Cursor (or open a new window) to activate.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Migrate skill-creator from v0.1.0 to v0.2.0"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually write changes (default is dry-run)",
    )
    parser.add_argument(
        "--skills-dir",
        type=Path,
        default=None,
        help="Override skills directory (default: ~/.cursor/skills)",
    )
    args = parser.parse_args()

    plugin_dir = detect_plugin_dir()
    skills_dir = args.skills_dir or detect_skills_dir()

    print("skill-creator migration: v0.1.0 → v0.2.0")
    print(f"  Plugin : {plugin_dir}")
    print(f"  Skills : {skills_dir}")

    if not skills_dir.exists():
        print(f"\nSkills directory not found: {skills_dir}")
        print("Nothing to migrate (no v0.1.0 install detected).")
        sys.exit(0)

    v1_pointer = skills_dir / "skill-creator" / "SKILL.md"
    if not v1_pointer.exists():
        print("\nNo existing skill-creator pointer found.")
        print("Run install.ps1 or install.sh for a fresh install instead.")
        sys.exit(0)

    actions = plan_migration(skills_dir, plugin_dir)
    execute_migration(actions, skills_dir, plugin_dir, apply=args.apply)


if __name__ == "__main__":
    main()
