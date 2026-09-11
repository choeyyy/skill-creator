#!/usr/bin/env python3
"""Install a self-contained Codex skill-lint bundle from the canonical plugin files."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
RESOURCES = (
    "agents/linter.md",
    "agents/fixer.md",
    "references/lint-rules.md",
    "references/session-audit.md",
    "references/fix-report-format.md",
)


def default_destination() -> Path:
    configured = os.environ.get("CODEX_HOME")
    codex_dir = Path(configured).expanduser() if configured else Path.home() / ".codex"
    return codex_dir / "skills" / "skill-lint"


def build_bundle(plugin_root: Path = PLUGIN_ROOT) -> dict[str, str]:
    command = (plugin_root / "commands/SKILL-lint.md").read_text(encoding="utf-8-sig")
    if command.count("\nname: SKILL-lint\n") != 1:
        raise ValueError("Expected the canonical SKILL-lint command frontmatter")
    command = command.replace("\nname: SKILL-lint\n", "\nname: skill-lint\n", 1)
    command = command.replace("(../skills/skill-creator/", "(")
    command = command.replace("plugin-root `config/defaults.json`", "skill-root `config/defaults.json`")
    command = command.replace("/SKILL-lint", "$skill-lint")
    command = command.replace("(../references/host-compatibility.md)", "(references/host-compatibility.md)")
    bundle = {"SKILL.md": command, "references/host-compatibility.md": (plugin_root / "references/host-compatibility.md").read_text(encoding="utf-8")}
    for relative in RESOURCES:
        bundle[relative] = (plugin_root / "skills/skill-creator" / relative).read_text(encoding="utf-8-sig")
    bundle["config/defaults.json"] = (plugin_root / "config/defaults.json").read_text(encoding="utf-8-sig")
    return bundle


def install(destination: Path, *, overwrite: bool = False, plugin_root: Path = PLUGIN_ROOT) -> list[Path]:
    bundle = build_bundle(plugin_root)
    destination = destination.expanduser().resolve()
    conflicts = []
    for relative, content in bundle.items():
        target = destination / relative
        if target.exists() and (not target.is_file() or target.read_text(encoding="utf-8") != content):
            conflicts.append(target)
    if conflicts and not overwrite:
        raise FileExistsError("Existing files differ; review them before using --overwrite: " + ", ".join(map(str, conflicts)))
    # All input files and conflicts are checked before the first output write.
    written = []
    for relative, content in bundle.items():
        target = destination / relative
        if target.is_file() and target.read_text(encoding="utf-8") == content:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8", newline="\n")
        written.append(target)
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, default=default_destination(), help="Skill directory (default: CODEX_HOME/skills/skill-lint or ~/.codex/skills/skill-lint)")
    parser.add_argument("--overwrite", action="store_true", help="Replace differing generated files after reviewing local edits; leave other files intact")
    args = parser.parse_args()
    try:
        written = install(args.destination, overwrite=args.overwrite)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Installation failed: {error}\n")
    print(f"Installed skill-lint: {args.destination.expanduser().resolve()}")
    print(f"Files written: {len(written)}; invoke $skill-lint in a new Codex task.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
