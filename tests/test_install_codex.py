"""Behavioral checks for the Codex bundle installer; no real user directory is used."""
import importlib.util
import os
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("install_codex", Path(__file__).resolve().parents[1] / "scripts/install_codex.py")
installer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(installer)


class InstallCodexTests(unittest.TestCase):
    def test_installed_bundle_resolves_all_relative_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / "skill-lint"
            self.assertEqual(len(installer.install(destination)), 7)
            for path in destination.rglob("*.md"):
                for relative in re.findall(r"\[[^\]]+\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
                    if not re.match(r"\w+://", relative):
                        resolved = (path.parent / relative).resolve()
                        self.assertTrue(resolved.is_relative_to(destination.resolve()))
                        self.assertTrue(resolved.is_file(), (path, relative))
            self.assertIn("\nname: skill-lint\n", (destination / "SKILL.md").read_text(encoding="utf-8"))

    def test_repeat_install_is_noop_and_preserves_extra_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / "skill-lint"
            installer.install(destination)
            extra = destination / "notes.txt"
            extra.write_text("local notes", encoding="utf-8")
            self.assertEqual(installer.install(destination), [])
            self.assertEqual(extra.read_text(encoding="utf-8"), "local notes")

    def test_conflict_aborts_before_any_write_then_explicit_overwrite_works(self):
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / "skill-lint"
            target = destination / "references/lint-rules.md"
            target.parent.mkdir(parents=True)
            target.write_text("local changes", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                installer.install(destination)
            self.assertEqual(target.read_text(encoding="utf-8"), "local changes")
            self.assertFalse((destination / "SKILL.md").exists())
            installer.install(destination, overwrite=True)
            self.assertTrue((destination / "SKILL.md").is_file())
            self.assertNotEqual(target.read_text(encoding="utf-8"), "local changes")

    def test_codex_home_controls_default_location(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {"CODEX_HOME": tmp}):
            self.assertEqual(installer.default_destination(), Path(tmp) / "skills/skill-lint")


if __name__ == "__main__":
    unittest.main()
