"""Exercise installation in temporary homes; never touch the real host setup."""

import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import tomllib
import unittest
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("kit_install", REPO / "scripts/install.py")
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="agentic-kit-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def run_install(self, *args, success=True):
        result = subprocess.run(
            [str(REPO / "install.sh"), "--root", str(self.root), *args],
            cwd=self.root, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0 if success else 1, result.stdout + result.stderr)
        return result

    def test_dry_run_creates_nothing(self):
        self.run_install("--host", "both", "--dry-run")
        self.assertEqual(list(self.root.iterdir()), [])

    def test_both_hosts_render_roles_and_bundle_references(self):
        self.run_install("--host", "both", "--scope", "project")
        for source in (REPO / "roles").glob("*.md"):
            fields, body = installer.role_parts(source)
            codex = tomllib.loads((self.root / ".codex/agents" / (source.stem + ".toml")).read_text())
            self.assertEqual(codex, dict(fields, developer_instructions=body))
            claude = (self.root / ".claude/agents" / source.name).read_text()
            self.assertTrue(claude.endswith(body))
            metadata = {key: json.loads(value) for key, value in (
                line.split(":", 1) for line in claude.split("---")[1].strip().splitlines())}
            self.assertEqual(metadata["name"], fields["name"])
            self.assertEqual(metadata["description"], fields["description"])
            self.assertNotIn("model", metadata)
        for host_dir in (".claude", ".codex"):
            self.assertEqual((self.root / host_dir / "agents/THIRD-PARTY-NOTICES.txt").read_bytes(),
                             (REPO / "THIRD-PARTY-NOTICES.md").read_bytes())
            self.assertEqual((self.root / host_dir / "agents/LICENSE").read_bytes(),
                             (REPO / "LICENSE").read_bytes())
        for host_dir in (".claude", ".agents"):
            skills = self.root / host_dir / "skills"
            self.assertEqual(len(list(skills.glob("*/SKILL.md"))), 9)
            for entry in skills.glob("*/SKILL.md"):
                self.assertEqual((entry.parent / "LICENSE").read_bytes(), (REPO / "LICENSE").read_bytes())
            for markdown in skills.rglob("*.md"):
                for link in re.findall(r"\]\(([^)]+)\)", markdown.read_text()):
                    if "://" not in link and not link.startswith("#"):
                        self.assertTrue((markdown.parent / link.split("#")[0]).is_file(), (markdown, link))

    def test_default_still_targets_claude(self):
        self.run_install()
        self.assertTrue((self.root / ".claude/skills/codex-implement/SKILL.md").is_file())
        self.assertFalse((self.root / ".codex").exists())

    def test_idempotence_and_settings_preserved(self):
        self.run_install("--host", "both")
        settings = self.root / ".claude/settings.json"
        config = self.root / ".codex/config.toml"
        settings.write_text('{"custom": true}\n')
        config.write_text('model = "user-choice"\n')
        before = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in self.root.rglob("*") if p.is_file()}
        self.run_install("--host", "both")
        after = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_collision_fails_before_any_writes(self):
        target = self.root / ".agents/skills/scout/SKILL.md"
        target.parent.mkdir(parents=True)
        target.write_text("my local workflow")
        self.run_install("--host", "both", success=False)
        self.assertEqual(target.read_text(), "my local workflow")
        self.assertFalse((self.root / ".claude").exists())
        self.assertFalse((self.root / ".codex").exists())

    def test_replace_backs_up_and_preserves_mode(self):
        target = self.root / ".codex/agents/qa-verifier.toml"
        target.parent.mkdir(parents=True)
        target.write_text("local role")
        target.chmod(0o600)
        self.run_install("--host", "codex", "--replace")
        backups = list((self.root / ".agentic-code-kit/backups").glob("*/codex/agents/qa-verifier.toml"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), "local role")
        self.assertEqual(target.stat().st_mode & 0o777, 0o600)
        self.assertEqual(tomllib.loads(target.read_text())["name"], "qa-verifier")

    def test_replace_dry_run_does_not_back_up_or_modify(self):
        target = self.root / ".claude/agents/qa-verifier.md"
        target.parent.mkdir(parents=True)
        target.write_text("local role")
        self.run_install("--replace", "--dry-run")
        self.assertEqual(target.read_text(), "local role")
        self.assertFalse((self.root / ".agentic-code-kit").exists())

    def test_legacy_nested_agents_are_backed_up_and_retired(self):
        old = self.root / ".claude/agents/grug-scout/AGENT.md"
        old.parent.mkdir(parents=True)
        old.write_text("custom legacy role")
        self.run_install(success=False)
        self.assertTrue(old.exists())
        self.run_install("--replace")
        self.assertFalse(old.exists())
        self.assertTrue((self.root / ".claude/agents/grug-scout.md").is_file())
        saved = list((self.root / ".agentic-code-kit/backups").glob("*/claude/agents/grug-scout/AGENT.md"))
        self.assertEqual(saved[0].read_text(), "custom legacy role")

    def test_symlink_destinations_are_refused(self):
        outside = self.root / "outside"
        outside.mkdir()
        (self.root / ".claude").symlink_to(outside, target_is_directory=True)
        self.run_install("--replace", success=False)
        self.assertEqual(list(outside.iterdir()), [])

    def test_broken_file_symlink_is_refused(self):
        target = self.root / ".claude/agents/qa-verifier.md"
        target.parent.mkdir(parents=True)
        target.symlink_to(self.root / "missing")
        self.run_install("--replace", success=False)
        self.assertFalse((self.root / "missing").exists())

    def test_non_directory_parent_is_refused_before_writes(self):
        (self.root / ".agents").write_text("file in the way")
        self.run_install("--host", "both", success=False)
        self.assertFalse((self.root / ".claude").exists())

    def test_backup_symlink_is_refused_before_replacement(self):
        target = self.root / ".claude/agents/qa-verifier.md"
        target.parent.mkdir(parents=True)
        target.write_text("original role")
        external = self.root / "external"
        external.mkdir()
        (self.root / ".agentic-code-kit").symlink_to(external, target_is_directory=True)
        self.run_install("--replace", success=False)
        self.assertEqual(target.read_text(), "original role")
        self.assertEqual(list(external.iterdir()), [])
        self.assertFalse((self.root / ".claude/skills").exists())

    def test_project_scope_defaults_to_callers_working_directory(self):
        result = subprocess.run([str(REPO / "install.sh"), "--host", "both", "--scope", "project"],
                                cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.root / ".claude/agents/qa-verifier.md").is_file())
        self.assertTrue((self.root / ".codex/agents/qa-verifier.toml").is_file())

    def test_codex_home_only_affects_user_roles(self):
        args = type("Args", (), dict(root=None, scope="user", host="codex"))()
        with patch.object(Path, "home", return_value=self.root), patch.dict(os.environ, {"CODEX_HOME": str(self.root / "custom-codex")}):
            _, plans = installer.destinations(args)
        paths = {p for p, _, _ in plans}
        self.assertIn(self.root / "custom-codex/agents/qa-verifier.toml", paths)
        self.assertIn(self.root / ".agents/skills/scout/SKILL.md", paths)
        args.scope = "project"
        with patch.object(Path, "cwd", return_value=self.root), patch.dict(os.environ, {"CODEX_HOME": str(self.root / "custom-codex")}):
            _, plans = installer.destinations(args)
        self.assertIn(self.root / ".codex/agents/qa-verifier.toml", {p for p, _, _ in plans})


if __name__ == "__main__":
    unittest.main()
