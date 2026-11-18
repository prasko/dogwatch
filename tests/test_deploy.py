from contextlib import redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest

SPEC = importlib.util.spec_from_file_location(
    "deploy", Path(__file__).resolve().parents[1] / "scripts/deploy.py")
deploy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(deploy)


class DeploymentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        # macOS /var is a symlink; use its real path for the test destination.
        self.home = Path(self.temp.name).resolve()
        self.destination = self.home / "codex"
        self.homes = {"codex": self.destination, "claude": self.home / "claude"}
        self.rendered = deploy.render()
        self.outputs = deploy.resolve(self.rendered, self.homes)
        quiet = redirect_stdout(io.StringIO())
        quiet.__enter__()
        self.addCleanup(quiet.__exit__, None, None, None)

    def test_profiles_and_agents_have_same_instructions_without_permission_overrides(self):
        roles = deploy.ROLES
        codex = self.rendered["codex"]
        self.assertEqual(set(codex), {
            path for role in roles
            for path in (f"agents/dogwatch-{role}.toml", f"dogwatch-{role}.config.toml")
        } | {f"skills/dogwatch-{skill}/SKILL.md" for skill in deploy.SKILLS})
        for role in roles:
            agent = tomllib.loads(codex[f"agents/dogwatch-{role}.toml"])
            profile = tomllib.loads(codex[f"dogwatch-{role}.config.toml"])
            self.assertEqual(agent["name"], f"dogwatch-{role}")
            self.assertEqual(agent["developer_instructions"], profile["developer_instructions"])
            self.assertIn(f"# {role.title()}", profile["developer_instructions"])
            self.assertEqual(set(profile),
                             {"developer_instructions", "model", "model_reasoning_effort",
                              "model_context_window", "model_auto_compact_token_limit"})
            self.assertEqual(profile["model_context_window"], 872000)
            self.assertEqual(profile["model_auto_compact_token_limit"], 400000)
            self.assertEqual(set(agent), {"name", "description", "developer_instructions"})
            self.assertIn("| `fast` | gpt-6-luna | medium |", agent["developer_instructions"])
            self.assertIn("## Codex notes", profile["developer_instructions"])
            self.assertNotIn("Claude", profile["developer_instructions"])

    def test_claude_agents_have_frontmatter_and_shared_instructions(self):
        roles = deploy.ROLES
        claude = self.rendered["claude"]
        self.assertEqual(set(claude), {f"agents/dogwatch-{role}.md" for role in roles}
                         | {f"skills/dogwatch-{skill}/SKILL.md" for skill in deploy.SKILLS})
        for role in roles:
            content = claude[f"agents/dogwatch-{role}.md"]
            self.assertTrue(content.startswith(deploy.CLAUDE_MARKER))
            frontmatter, body = content.removeprefix("---\n").split("\n---\n\n", 1)
            fields = dict(line.split(": ", 1) for line in frontmatter.splitlines()[1:])
            expected = {"name", "description", "model", "effort"}
            self.assertEqual(set(fields), expected)
            self.assertEqual(fields["name"], f'"dogwatch-{role}"')
            self.assertIn("explicitly", fields["description"])
            codex = tomllib.loads(self.rendered["codex"][f"dogwatch-{role}.config.toml"])
            shared = codex["developer_instructions"].split("## Codex notes")[0]
            self.assertTrue(body.startswith(shared))
            self.assertIn("### Model tiers", body)
            self.assertIn("## Claude Code notes", body)
            self.assertNotIn("Codex", body)

    def test_lead_receives_the_same_contracts_as_agent_descriptions(self):
        lead = tomllib.loads(self.rendered["codex"]["dogwatch-lead.config.toml"])
        claude_lead = self.rendered["claude"]["agents/dogwatch-lead.md"]
        for role in deploy.ROLES:
            agent = tomllib.loads(self.rendered["codex"][f"agents/dogwatch-{role}.toml"])
            if role != "lead":
                contract = f"- **{role.title()}:** {agent['description']}"
                self.assertIn(contract, lead["developer_instructions"])
                self.assertIn(contract, claude_lead)
                self.assertNotIn("## Delegated role contracts", agent["developer_instructions"])

    def test_tiers_resolve_to_models_and_role_overrides_win(self):
        def settings(target, role):
            if target == "codex":
                return tomllib.loads(self.rendered["codex"][f"dogwatch-{role}.config.toml"])
            frontmatter = self.rendered["claude"][f"agents/dogwatch-{role}.md"].split("\n---\n")[0]
            return {key: value.strip('"') for key, value in
                    (line.split(": ", 1) for line in frontmatter.splitlines()[2:])}
        self.assertEqual(settings("claude", "lead")["model"], "opus")
        self.assertEqual(settings("claude", "developer")["model"], "sonnet")
        self.assertEqual(settings("claude", "developer")["effort"], "high")
        self.assertEqual(deploy._load_runtime(deploy.ROOT, "claude")[1]["fast"]["model"], "haiku")
        self.assertEqual(settings("codex", "reviewer")["model"], "gpt-6.1-sol")
        self.assertEqual(settings("codex", "architect")["model"], "gpt-6-astra")

        root = self.home / "src"
        for path in ("roles", "codex", "claude", "skills"):
            shutil.copytree(deploy.ROOT / path, root / path)
        config = root / "claude/roles.toml"
        config.write_text(config.read_text().replace(
            "[roles.lead]\n", '[roles.lead]\nmodel = "fable"\n'))
        lead = deploy.render(root, ("claude",))["claude"]["agents/dogwatch-lead.md"]
        self.assertIn('model: "fable"', lead)
        self.assertIn("| lead | `deep` | fable | medium |", lead)
        self.assertIn('effort: "medium"', lead)

        config.write_text(config.read_text().replace('effort = "low"', 'effort = "ultra"'))
        with self.assertRaisesRegex(ValueError, "effort"):
            deploy.render(root, ("claude",))
        shared = root / "roles/roles.toml"
        shared.write_text(shared.read_text().replace('tier = "deep"', 'tier = "quick"'))
        with self.assertRaisesRegex(ValueError, "tier"):
            deploy.render(root, ("codex",))

    def test_context_settings_validate_and_role_overrides_win(self):
        root = self.home / "src"
        for path in ("roles", "codex", "claude", "skills"):
            shutil.copytree(deploy.ROOT / path, root / path)
        config = root / "codex/roles.toml"
        original = config.read_text()
        config.write_text(original.replace(
            "[roles.lead]\n", "[roles.lead]\nmodel_auto_compact_token_limit = 350000\n"))
        output = deploy.render(root, ("codex",))["codex"]
        lead = tomllib.loads(output["dogwatch-lead.config.toml"])
        self.assertEqual(lead["model_context_window"], 872000)
        self.assertEqual(lead["model_auto_compact_token_limit"], 350000)

        for value in ('"400000"', "true", "0", "-1", "400000.5"):
            with self.subTest(value=value):
                config.write_text(original.replace(
                    "model_auto_compact_token_limit = 400000",
                    f"model_auto_compact_token_limit = {value}"))
                with self.assertRaisesRegex(ValueError, "positive integer"):
                    deploy.render(root, ("codex",))
        config.write_text(original.replace(
            "[roles.lead]\n", "[roles.lead]\nmodel_context_window = 300000\n"))
        with self.assertRaisesRegex(ValueError, "Compaction threshold"):
            deploy.render(root, ("codex",))

        claude = root / "claude/roles.toml"
        claude.write_text(claude.read_text().replace(
            "[roles.lead]\n", "[roles.lead]\nmodel_context_window = 872000\n"))
        with self.assertRaisesRegex(ValueError, "Unsupported settings"):
            deploy.render(root, ("claude",))

    def test_target_selection_and_claude_markers_are_managed(self):
        only = deploy.render(targets=("claude",))
        self.assertEqual(set(only), {"claude"})
        outputs = deploy.resolve(only, self.homes)
        deploy.deploy(outputs)
        self.assertFalse(self.destination.exists())
        path = self.homes["claude"] / "agents/dogwatch-lead.md"
        path.write_text(path.read_text() + "local edit\n")
        deploy.deploy(outputs)
        self.assertEqual(len(list(path.parent.glob("dogwatch-lead.md.bak-*"))), 1)
        self.assertEqual(deploy.deploy(outputs, check=True), 0)

    def test_dry_run_does_not_create_destination(self):
        deploy.deploy(self.outputs, dry_run=True)
        self.assertFalse(self.destination.exists())

    def test_install_repeat_check_and_preserve_unrelated_files(self):
        self.destination.mkdir()
        config = self.destination / "config.toml"
        config.write_text('model = "existing-model"\n')
        hooks = self.destination / "hooks.json"
        hooks.write_text('{"hooks": {}}\n')
        self.assertEqual(deploy.deploy(self.outputs, check=True), 1)
        deploy.deploy(self.outputs)
        before = {path: path.stat().st_mtime_ns for path in self.home.rglob("*")
                  if path.is_file()}
        deploy.deploy(self.outputs)
        self.assertEqual(before, {path: path.stat().st_mtime_ns for path in before})
        self.assertEqual(deploy.deploy(self.outputs, check=True), 0)
        self.assertEqual(config.read_text(), 'model = "existing-model"\n')
        self.assertEqual(hooks.read_text(), '{"hooks": {}}\n')
        self.assertFalse(list(self.home.rglob("*.bak-*")))

    def test_collision_preflight_then_explicit_replacement_with_backup(self):
        conflict = self.destination / "agents/dogwatch-reviewer.toml"
        conflict.parent.mkdir(parents=True)
        original = b'name = "reviewer"\r\n'
        conflict.write_bytes(original)
        with self.assertRaisesRegex(ValueError, "Unmanaged file"):
            deploy.deploy(self.outputs)
        self.assertFalse((self.destination / "agents/dogwatch-lead.toml").exists())
        self.assertEqual(conflict.read_bytes(), original)
        deploy.deploy(self.outputs, replace=True)
        backups = list(conflict.parent.glob("dogwatch-reviewer.toml.bak-*"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_bytes(), original)

    def test_changed_managed_file_is_detected_and_backed_up(self):
        deploy.deploy(self.outputs)
        path = self.destination / "dogwatch-lead.config.toml"
        changed = path.read_text() + "# local edit\n"
        path.write_text(changed)
        self.assertEqual(deploy.deploy(self.outputs, check=True), 1)
        deploy.deploy(self.outputs)
        backups = list(self.destination.glob("dogwatch-lead.config.toml.bak-*"))
        self.assertEqual(backups[0].read_text(), changed)

    def test_symlink_is_refused_without_touching_target(self):
        target = Path(self.temp.name) / "outside"
        target.write_text("keep me")
        self.destination.mkdir()
        (self.destination / "dogwatch-reviewer.config.toml").symlink_to(target)
        with self.assertRaisesRegex(ValueError, "symlink"):
            deploy.deploy(self.outputs, replace=True)
        self.assertEqual(target.read_text(), "keep me")
        self.assertFalse((self.destination / "agents").exists())

    def test_skills_are_portable_and_roles_embed_the_canonical_procedure(self):
        for skill in deploy.SKILLS:
            relative = f"skills/dogwatch-{skill}/SKILL.md"
            source = (deploy.ROOT / relative).read_text()
            rendered = self.rendered["codex"][relative]
            self.assertEqual(rendered, self.rendered["claude"][relative])
            self.assertEqual(rendered.replace(deploy.MARKER, "", 1), source)
            frontmatter, body = rendered[4:].split("\n---\n", 1)
            fields = dict(line.split(":", 1) for line in frontmatter.splitlines()
                          if not line.startswith("#"))
            self.assertEqual(json.loads(fields["name"]), f"dogwatch-{skill}")
            self.assertTrue(json.loads(fields["description"]))
            self.assertEqual(set(fields), {"name", "description"})
            self.assertNotIn("### Model tiers", body)
            for role, skills in deploy.ROLE_SKILLS.items():
                if skill in skills:
                    profile = tomllib.loads(self.rendered["codex"][f"dogwatch-{role}.config.toml"])
                    self.assertIn(body.strip(), profile["developer_instructions"])
            lead = tomllib.loads(self.rendered["codex"]["dogwatch-lead.config.toml"])
            self.assertNotIn(body.strip(), lead["developer_instructions"])

    def test_skill_collision_preflights_roles_and_skill_backup_preserves_bytes(self):
        path = self.destination / "skills/dogwatch-test/SKILL.md"
        path.parent.mkdir(parents=True)
        original = b"---\r\nname: mine\r\n---\r\n"
        path.write_bytes(original)
        with self.assertRaisesRegex(ValueError, "Unmanaged file"):
            deploy.deploy(self.outputs)
        self.assertFalse((self.destination / "agents").exists())
        deploy.deploy(self.outputs, replace=True)
        self.assertEqual(next(path.parent.glob("SKILL.md.bak-*")).read_bytes(), original)
        self.assertEqual(deploy.deploy(self.outputs, check=True), 0)

    def test_retirement_is_scoped_backed_up_and_idempotent(self):
        retired = deploy.retired_paths(self.homes)
        for path in retired:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((deploy.LEGACY_MARKER + "old role\r\n").encode())
        original = retired[0].read_bytes()
        deploy.deploy(self.outputs, retired=retired, dry_run=True)
        self.assertTrue(all(path.exists() for path in retired))
        self.assertEqual(deploy.deploy(self.outputs, retired=retired, check=True), 1)
        deploy.deploy(self.outputs, retired=retired)
        self.assertTrue(all(not path.exists() for path in retired))
        self.assertEqual(next(retired[0].parent.glob("researcher.toml.bak-*")).read_bytes(), original)
        self.assertEqual(deploy.deploy(self.outputs, retired=retired, check=True), 0)
        backups = set(self.home.rglob("*.bak-*"))
        deploy.deploy(self.outputs, retired=retired)
        self.assertEqual(set(self.home.rglob("*.bak-*")), backups)
        self.assertTrue(all(path.is_relative_to(self.homes["claude"])
                            for path in deploy.retired_paths(self.homes, ("claude",))))

    def test_unmanaged_retired_file_is_preserved_even_with_replace(self):
        path = deploy.retired_paths(self.homes, ("claude",))[0]
        path.parent.mkdir(parents=True)
        path.write_text("user agent\n")
        deploy.deploy(self.outputs, retired=(path,), replace=True)
        self.assertEqual(path.read_text(), "user agent\n")
        self.assertFalse(list(path.parent.glob("agentic-researcher.md.bak-*")))

    def test_retired_symlink_aborts_before_any_writes(self):
        path = deploy.retired_paths(self.homes)[0]
        path.parent.mkdir(parents=True)
        target = self.home / "unrelated"
        target.write_text(deploy.LEGACY_MARKER + "keep me")
        path.symlink_to(target)
        with self.assertRaisesRegex(ValueError, "symlink"):
            deploy.deploy(self.outputs, retired=(path,))
        self.assertFalse((self.destination / "agents/dogwatch-lead.toml").exists())
        self.assertTrue(target.read_text().endswith("keep me"))

    def test_cli_custom_home_keeps_skills_and_retirement_in_selected_target(self):
        retired = deploy.retired_paths(self.homes)[0]
        retired.parent.mkdir(parents=True)
        retired.write_text(deploy.LEGACY_MARKER + "old")
        command = [sys.executable, str(deploy.ROOT / "scripts/deploy.py"),
                   "--target", "codex", "--codex-home", str(self.destination),
                   "--claude-home", str(self.homes["claude"])]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(retired.exists())
        self.assertTrue((self.destination / "skills/dogwatch-research/SKILL.md").exists())
        self.assertFalse(self.homes["claude"].exists())
        result = subprocess.run(command + ["--check"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def cli(self, *args):
        return subprocess.run([sys.executable, str(deploy.ROOT / "scripts/deploy.py"),
                               "--codex-home", str(self.destination),
                               "--claude-home", str(self.homes["claude"]), *args],
                              capture_output=True, text=True)

    def test_dogwatch_migration_is_scoped_and_preserves_personal_bare_roles(self):
        for target in deploy.TARGETS:
            for relative in deploy.component_paths(target, legacy=True):
                path = self.homes[target] / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes((deploy.PREVIOUS_MARKER + "old content\r\n").encode())
        personal = self.destination / "agents/reviewer.toml"
        personal.write_text('name = "reviewer"\n')
        before = {path: path.read_bytes() for path in self.home.rglob("*") if path.is_file()}
        result = self.cli("--target", "codex", "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(before, {path: path.read_bytes() for path in before})
        self.assertFalse(list(self.home.rglob("*.bak-*")))

        result = self.cli("--target", "codex")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.destination / "agents/dogwatch-reviewer.toml").exists())
        self.assertEqual(personal.read_text(), 'name = "reviewer"\n')
        for old, content in before.items():
            if old == personal or old.is_relative_to(self.homes["claude"]):
                self.assertEqual(old.read_bytes(), content)
            else:
                self.assertFalse(old.exists())
                self.assertEqual(next(old.parent.glob(old.name + ".bak-*")).read_bytes(), content)
        self.assertEqual(self.cli("--target", "codex", "--check").returncode, 0)

    def test_uninstall_roles_keeps_skills_other_provider_and_configuration(self):
        deploy.deploy(self.outputs)
        config = self.destination / "config.toml"
        config.write_text('approvals_reviewer = "auto_review"\n')
        personal = self.destination / "agents/mine.toml"
        personal.write_text("my role")
        before = {path: (path.read_bytes(), path.stat().st_mtime_ns)
                  for path in self.home.rglob("*") if path.is_file()}
        args = ("--uninstall", "--target", "codex", "--component", "roles")
        result = self.cli(*args, "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Would remove", result.stdout)
        self.assertEqual(before, {path: (path.read_bytes(), path.stat().st_mtime_ns) for path in before})
        self.assertFalse(list(self.home.rglob("*.bak-*")))
        result = self.cli(*args)
        self.assertEqual(result.returncode, 0, result.stderr)
        removed = {self.destination / relative for relative in deploy.component_paths("codex", "roles")}
        for path, (content, modified) in before.items():
            if path in removed:
                self.assertFalse(path.exists())
                self.assertEqual(next(path.parent.glob(path.name + ".bak-*")).read_bytes(), content)
            else:
                self.assertEqual((path.read_bytes(), path.stat().st_mtime_ns), (content, modified))
        backups = set(self.home.rglob("*.bak-*"))
        self.assertEqual(self.cli(*args).returncode, 0)
        self.assertEqual(backups, set(self.home.rglob("*.bak-*")))

    def test_uninstall_skills_warns_about_remaining_roles_and_preserves_unmarked_files(self):
        deploy.deploy(self.outputs)
        personal = self.destination / "skills/dogwatch-test/SKILL.md"
        personal.write_text("my replacement skill")
        result = self.cli("--uninstall", "--target", "codex", "--component", "skills")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("roles still use these skills", result.stderr)
        self.assertIn("Preserving unmanaged file", result.stdout)
        self.assertEqual(personal.read_text(), "my replacement skill")
        self.assertTrue((self.destination / "agents/dogwatch-lead.toml").exists())
        self.assertFalse((self.destination / "skills/dogwatch-design/SKILL.md").exists())
        self.assertTrue((self.homes["claude"] / "skills/dogwatch-design/SKILL.md").exists())

    def test_uninstall_includes_legacy_files_and_rejects_symlinks_before_removal(self):
        deploy.deploy(self.outputs)
        legacy = self.destination / "agentic-lead.config.toml"
        legacy.write_bytes((deploy.PREVIOUS_MARKER + "legacy\r\n").encode())
        unrelated = self.home / "unrelated"
        unrelated.write_text(deploy.MARKER + "keep me")
        link = self.homes["claude"] / "agents/agentic-lead.md"
        link.symlink_to(unrelated)
        result = self.cli("--uninstall")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("symlink", result.stderr)
        self.assertTrue(all(path.exists() for path in self.outputs))
        self.assertTrue(legacy.exists())
        self.assertFalse(list(self.home.rglob("*.bak-*")))
        link.unlink()
        result = self.cli("--uninstall")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(any(path.exists() for path in self.outputs))
        self.assertFalse(legacy.exists())
        self.assertEqual(unrelated.read_text(), deploy.MARKER + "keep me")
        self.assertEqual(next(self.destination.glob(legacy.name + ".bak-*")).read_bytes(),
                         (deploy.PREVIOUS_MARKER + "legacy\r\n").encode())

    def test_components_only_apply_to_removal_to_avoid_incomplete_migrations(self):
        for component in ("roles", "skills"):
            for mode in ((), ("--check",), ("--dry-run",)):
                result = self.cli("--target", "claude", "--component", component, *mode)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("deploy roles and skills together", result.stderr)
        self.assertFalse(self.destination.exists())
        self.assertFalse(self.homes["claude"].exists())

    def test_uninstall_on_empty_homes_is_noop_and_invalid_modes_do_not_write(self):
        result = self.cli("--uninstall")
        self.assertEqual(result.returncode, 0, result.stderr)
        for option in ("--check", "--replace"):
            result = self.cli("--uninstall", option)
            self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.destination.exists())
        self.assertFalse(self.homes["claude"].exists())

    def test_shared_provider_home_migrates_and_uninstalls_each_file_once(self):
        self.homes["claude"] = self.destination
        for path in set(deploy.retired_paths(self.homes)):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(deploy.PREVIOUS_MARKER + "old file")
        result = self.cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(any(path.exists() for path in deploy.retired_paths(self.homes)))
        self.assertEqual(self.cli("--check").returncode, 0)
        files = deploy.resolve(self.rendered, self.homes)
        self.assertTrue(all(path.exists() for path in files))
        before = {path: path.read_bytes() for path in files}
        for args in (("--target", "codex"),
                     ("--target", "codex", "--uninstall", "--component", "skills")):
            result = self.cli(*args)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Provider homes share skill files", result.stderr)
            self.assertEqual(before, {path: path.read_bytes() for path in files})
        self.assertEqual(self.cli("--target", "codex", "--check").returncode, 0)
        result = self.cli("--uninstall")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(any(path.exists() for path in files))
        for path in files:
            self.assertEqual(len(list(path.parent.glob(path.name + ".bak-*"))), 1)
        self.assertEqual(self.cli("--uninstall").returncode, 0)

    def test_shared_home_aliases_are_normalized_without_bypassing_symlink_checks(self):
        self.homes["claude"] = self.destination / ".." / "codex"
        result = self.cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.cli("--target", "claude", "--uninstall")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Provider homes share skill files", result.stderr)
        self.assertEqual(self.cli("--uninstall").returncode, 0)

        linked = self.home / "linked"
        linked.symlink_to(self.destination, target_is_directory=True)
        self.homes["claude"] = linked / ".." / "codex"
        result = self.cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("symlink", result.stderr)
        self.assertFalse((self.destination / "agents/dogwatch-lead.toml").exists())


if __name__ == "__main__":
    unittest.main()
