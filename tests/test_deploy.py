from contextlib import redirect_stdout
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import tomllib
import unittest
from unittest import mock

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
        self.state_home = self.home / "state/dogwatch"
        environment = mock.patch.dict(os.environ, {"XDG_STATE_HOME": str(self.home / "state")})
        environment.start()
        self.addCleanup(environment.stop)
        self.destination = self.home / "codex"
        self.homes = {"codex": self.destination, "claude": self.home / "claude"}
        self.rendered = deploy.render()
        self.outputs = deploy.resolve(self.rendered, self.homes)
        quiet = redirect_stdout(io.StringIO())
        quiet.__enter__()
        self.addCleanup(quiet.__exit__, None, None, None)

    def backups(self, path):
        return [Path(entry["backup"])
                for manifest in sorted(self.state_home.glob("*/manifest.json"))
                if (entry := json.loads(manifest.read_text()).get(str(path)))]

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
                              "model_auto_compact_token_limit"})
            self.assertEqual(profile["model_auto_compact_token_limit"], 250000)
            self.assertEqual(set(agent), {"name", "description", "developer_instructions"})
            self.assertIn("| `fast` | gpt-6-luna | medium |", agent["developer_instructions"])
            self.assertIn("## Codex notes", profile["developer_instructions"])
            self.assertNotIn("## Claude Code notes", profile["developer_instructions"])

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
            self.assertNotIn("## Codex notes", body)

    def test_provider_assistant_notes_are_scoped_to_assistant(self):
        for target in deploy.TARGETS:
            shared_notes = (deploy.ROOT / f"{target}/notes.md").read_text().strip()
            assistant_notes = (deploy.ROOT / f"{target}/assistant.md").read_text().strip()
            other = next(provider for provider in deploy.TARGETS if provider != target)
            other_notes = (deploy.ROOT / f"{other}/assistant.md").read_text().strip()
            for role in deploy.ROLES:
                if target == "codex":
                    contents = [tomllib.loads(self.rendered[target][path])["developer_instructions"]
                                for path in (f"agents/dogwatch-{role}.toml",
                                             f"dogwatch-{role}.config.toml")]
                else:
                    contents = [self.rendered[target][f"agents/dogwatch-{role}.md"]]
                for content in contents:
                    with self.subTest(target=target, role=role):
                        self.assertIn(shared_notes, content)
                        self.assertEqual(content.count(assistant_notes), int(role == "assistant"))
                        self.assertNotIn(other_notes, content)

    def test_coordinators_receive_only_their_child_role_contracts(self):
        children = {"assistant": ("lead",),
                    "lead": ("scoper", "architect", "developer", "tester", "validator", "reviewer")}
        for role in deploy.ROLES:
            agent = tomllib.loads(self.rendered["codex"][f"agents/dogwatch-{role}.toml"])
            for content in (agent["developer_instructions"],
                            self.rendered["claude"][f"agents/dogwatch-{role}.md"]):
                if role not in children:
                    self.assertNotIn("## Delegated role contracts", content)
                    continue
                contracts = content.split("## Delegated role contracts\n\n", 1)[1].split("\n\n", 1)[0]
                expected = []
                for child in children[role]:
                    description = tomllib.loads(
                        self.rendered["codex"][f"agents/dogwatch-{child}.toml"])["description"]
                    expected.append(f"- **{child.title()}:** {description}")
                self.assertEqual(contracts.splitlines(), expected)

    def test_tiers_resolve_to_models_and_role_overrides_win(self):
        def settings(target, role):
            if target == "codex":
                return tomllib.loads(self.rendered["codex"][f"dogwatch-{role}.config.toml"])
            frontmatter = self.rendered["claude"][f"agents/dogwatch-{role}.md"].split("\n---\n")[0]
            return {key: value.strip('"') for key, value in
                    (line.split(": ", 1) for line in frontmatter.splitlines()[2:])}
        self.assertEqual(settings("claude", "lead")["model"], "opus")
        self.assertEqual(settings("claude", "assistant")["model"], "sonnet")
        self.assertEqual(settings("claude", "assistant")["effort"], "high")
        self.assertEqual(settings("claude", "developer")["model"], "sonnet")
        self.assertEqual(settings("claude", "developer")["effort"], "high")
        self.assertEqual(deploy._load_runtime(deploy.ROOT, "claude")[1]["fast"]["model"], "haiku")
        self.assertEqual(settings("codex", "reviewer")["model"], "gpt-6.2-sol")
        self.assertEqual(settings("codex", "assistant")["model"], "gpt-6.2-sol")
        self.assertEqual(settings("codex", "assistant")["model_reasoning_effort"], "high")
        self.assertEqual(settings("codex", "architect")["model"], "gpt-6.2-astra")

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
            "[roles.lead]\n", "[roles.lead]\nmodel_context_window = 300000\n"
            "model_auto_compact_token_limit = 200000\n"))
        output = deploy.render(root, ("codex",))["codex"]
        lead = tomllib.loads(output["dogwatch-lead.config.toml"])
        self.assertEqual(lead["model_context_window"], 300000)
        self.assertEqual(lead["model_auto_compact_token_limit"], 200000)

        for value in ('"250000"', "true", "0", "-1", "250000.5"):
            with self.subTest(value=value):
                config.write_text(original.replace(
                    "model_auto_compact_token_limit = 250000",
                    f"model_auto_compact_token_limit = {value}"))
                with self.assertRaisesRegex(ValueError, "positive integer"):
                    deploy.render(root, ("codex",))
        config.write_text(original.replace(
            "[roles.lead]\n", "[roles.lead]\nmodel_context_window = 200000\n"))
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
        self.assertEqual(len(self.backups(path)), 1)
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
        backups = self.backups(conflict)
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_bytes(), original)

    def test_changed_managed_file_is_detected_and_backed_up(self):
        deploy.deploy(self.outputs)
        path = self.destination / "dogwatch-lead.config.toml"
        changed = path.read_text() + "# local edit\n"
        path.write_text(changed)
        self.assertEqual(deploy.deploy(self.outputs, check=True), 1)
        deploy.deploy(self.outputs)
        backups = self.backups(path)
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
        self.assertEqual(self.backups(path)[0].read_bytes(), original)
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
        self.assertEqual(self.backups(retired[0])[0].read_bytes(), original)
        self.assertEqual(deploy.deploy(self.outputs, retired=retired, check=True), 0)
        backups = set(self.state_home.rglob("*"))
        deploy.deploy(self.outputs, retired=retired)
        self.assertEqual(set(self.state_home.rglob("*")), backups)
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
                self.assertEqual(self.backups(old)[0].read_bytes(), content)
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
                self.assertEqual(self.backups(path)[0].read_bytes(), content)
            else:
                self.assertEqual((path.read_bytes(), path.stat().st_mtime_ns), (content, modified))
        backups = set(self.state_home.rglob("*"))
        self.assertEqual(self.cli(*args).returncode, 0)
        self.assertEqual(backups, set(self.state_home.rglob("*")))

    def test_assistant_install_and_removal_preserve_unrelated_legacy_names(self):
        unrelated = self.home / "personal-assistant"
        original = deploy.PREVIOUS_MARKER + "personal assistant\n"
        unrelated.write_text(original)
        bare = self.destination / "agents/assistant.toml"
        bare.parent.mkdir(parents=True)
        bare.symlink_to(unrelated)
        aliases = (self.destination / "agentic-assistant.config.toml",
                   self.homes["claude"] / "agents/agentic-assistant.md")
        for path in aliases:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(original)

        result = self.cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        agent = self.destination / "agents/dogwatch-assistant.toml"
        profile = self.destination / "dogwatch-assistant.config.toml"
        claude = self.homes["claude"] / "agents/dogwatch-assistant.md"
        self.assertTrue(all(path.is_file() for path in (agent, profile, claude)))
        self.assertEqual(self.cli("--check").returncode, 0)
        expected = {path: path.read_bytes() for path in (agent, profile, claude)}

        result = self.cli("--uninstall", "--target", "codex", "--component", "roles")
        self.assertEqual(result.returncode, 0, result.stderr)
        for path in (agent, profile):
            self.assertFalse(path.exists())
            self.assertEqual(self.backups(path)[0].read_bytes(), expected[path])
        self.assertEqual(claude.read_bytes(), expected[claude])
        self.assertTrue((self.destination / "skills/dogwatch-scope/SKILL.md").exists())

        result = self.cli("--uninstall")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(claude.exists())
        self.assertTrue(bare.is_symlink())
        self.assertEqual(unrelated.read_text(), original)
        for path in aliases:
            self.assertEqual(path.read_text(), original)
            self.assertFalse(list(path.parent.glob(path.name + ".bak-*")))

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
        self.assertEqual(self.backups(legacy)[0].read_bytes(),
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
            self.assertEqual(len(self.backups(path)), 1)
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

    def test_backup_batch_preserves_bytes_modes_and_is_private(self):
        changed = self.destination / "dogwatch-lead.config.toml"
        retired = self.homes["claude"] / "agents/agentic-lead.md"
        originals = {changed: b"my config\r\n", retired: (deploy.PREVIOUS_MARKER + "old\r\n").encode()}
        for path, content in originals.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
            path.chmod(0o640)
        deploy.deploy(self.outputs, retired=(retired,), replace=True)
        manifests = list(self.state_home.glob("*/manifest.json"))
        self.assertEqual(len(manifests), 1)
        manifest = json.loads(manifests[0].read_text())
        self.assertEqual(set(manifest), {str(path) for path in originals})
        for path, content in originals.items():
            saved = Path(manifest[str(path)]["backup"])
            self.assertEqual(saved.read_bytes(), content)
            self.assertEqual(manifest[str(path)]["mode"], 0o640)
            self.assertEqual(stat.S_IMODE(saved.stat().st_mode), 0o600)
        self.assertEqual(stat.S_IMODE(manifests[0].stat().st_mode), 0o600)
        self.assertEqual(stat.S_IMODE(manifests[0].parent.stat().st_mode), 0o700)
        self.assertFalse(list(self.destination.rglob("*.bak-*")))
        self.assertFalse(list(self.homes["claude"].rglob("*.bak-*")))

    def test_preview_check_and_noop_do_not_create_backup_state(self):
        path = self.destination / "agents/dogwatch-lead.toml"
        path.parent.mkdir(parents=True)
        path.write_text(deploy.MARKER + "old")
        deploy.deploy(self.outputs, dry_run=True)
        deploy.deploy(self.outputs, check=True)
        self.assertFalse(self.state_home.exists())
        deploy.deploy({path: path.read_text()})
        self.assertFalse(self.state_home.exists())

    def test_backup_failure_precedes_all_deployment_mutations(self):
        changed = self.destination / "old"
        removed = self.destination / "retired"
        new = self.destination / "new"
        self.destination.mkdir()
        for path in (changed, removed):
            path.write_text(deploy.MARKER + "original")
        before = {path: path.read_bytes() for path in (changed, removed)}
        # Fail while syncing a backup, its manifest or its directory.
        for results in ([None, OSError("disk full")], [None, None, OSError("disk full")],
                        [None, None, None, OSError("disk full")]):
            with mock.patch.object(deploy.os, "fsync", side_effect=results):
                with self.assertRaisesRegex(OSError, "disk full"):
                    deploy.deploy({new: "new", changed: deploy.MARKER + "changed"}, retired=(removed,))
            self.assertEqual(before, {path: path.read_bytes() for path in before})
            self.assertFalse(new.exists())

    def test_state_override_and_symlink_destination(self):
        with mock.patch.dict(os.environ, {"XDG_STATE_HOME": ""}):
            self.assertEqual(deploy.default_state_home(), Path.home() / ".local/state/dogwatch")
        deploy.deploy(self.outputs)
        path = self.destination / "dogwatch-lead.config.toml"
        path.write_text(deploy.MARKER + "old")
        custom = self.home / "custom-state"
        result = self.cli("--state-home", str(custom))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(list(custom.glob("*/manifest.json"))), 1)
        self.assertFalse(self.state_home.exists())
        link = self.home / "state-link"
        link.symlink_to(custom, target_is_directory=True)
        path.write_text(deploy.MARKER + "another edit")
        for destination in (link, link / ".." / "custom-state"):
            result = self.cli("--state-home", str(destination))
            self.assertEqual(result.returncode, 2)
            self.assertIn("symlink backup destination", result.stderr)
            self.assertEqual(path.read_text(), deploy.MARKER + "another edit")

    def adjacent_backup(self, original, *, suffix="20261118T123456123456Z", content=None):
        path = original.with_name(original.name + ".bak-" + suffix)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content if content is not None else (deploy.MARKER + "old\r\n").encode())
        path.chmod(0o640)
        return path

    def test_backup_migration_is_scoped_repeatable_and_does_not_deploy(self):
        current = self.destination / "agents/dogwatch-lead.toml"
        legacy = self.destination / "agentic-lead.config.toml"
        retired = self.destination / "agents/researcher.toml"
        skill = self.destination / "skills/dogwatch-scope/SKILL.md"
        originals = (current, current, legacy, retired, skill)
        candidates = {
            self.adjacent_backup(path, suffix=f"20261118T12345612345{n}Z",
                                 content=("---\n" + deploy.PREVIOUS_MARKER + str(n)).replace("\n", "\r\n").encode()): path
            for n, path in enumerate(originals)
        }
        current.write_text("active local edits")
        untouched = [current,
                     self.adjacent_backup(self.destination / "agents/mine.toml"),
                     self.adjacent_backup(legacy, suffix="manual"),
                     self.adjacent_backup(retired, suffix="20261118T123457Z", content=b"personal original"),
                     self.adjacent_backup(self.homes["claude"] / "agents/dogwatch-lead.md")]
        before = {path: (path.read_bytes(), path.stat().st_mtime_ns) for path in (*candidates, *untouched)}
        args = ("--migrate-backups", "--target", "codex")
        result = self.cli(*args, "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Would migrate 5", result.stdout)
        self.assertEqual(before, {path: (path.read_bytes(), path.stat().st_mtime_ns) for path in before})
        self.assertFalse(self.state_home.exists())
        result = self.cli(*args)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Preserving unmarked backup", result.stdout)
        manifest = json.loads(next(self.state_home.glob("*/manifest.json")).read_text())
        for path, original in candidates.items():
            self.assertFalse(path.exists())
            entry = manifest[str(path)]
            self.assertEqual(Path(entry["backup"]).read_bytes(), before[path][0])
            self.assertEqual(entry["restore_to"], str(original))
            self.assertEqual(entry["mode"], 0o640)
        self.assertEqual({path: before[path] for path in untouched},
                         {path: (path.read_bytes(), path.stat().st_mtime_ns) for path in untouched})
        self.assertFalse((self.destination / "dogwatch-assistant.config.toml").exists())
        state = {path: path.stat().st_mtime_ns for path in self.state_home.rglob("*")}
        result = self.cli(*args)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(state, {path: path.stat().st_mtime_ns for path in self.state_home.rglob("*")})

    def test_migration_failures_keep_sources(self):
        originals = [self.destination / "agents/dogwatch-lead.toml",
                     self.destination / "dogwatch-lead.config.toml"]
        sources = [self.adjacent_backup(path) for path in originals]
        before = {path: path.read_bytes() for path in sources}
        with mock.patch.object(deploy.os, "fsync", side_effect=[None, None, OSError("disk full")]):
            with self.assertRaisesRegex(OSError, "disk full"):
                deploy.migrate_backups(self.homes)
        self.assertEqual(before, {path: path.read_bytes() for path in sources})
        save = deploy.backup_files

        def change_after_backup(*args, **kwargs):
            result = save(*args, **kwargs)
            sources[-1].write_text(deploy.MARKER + "concurrent edit")
            return result

        with mock.patch.object(deploy, "backup_files", side_effect=change_after_backup):
            with self.assertRaisesRegex(ValueError, "source changed"):
                deploy.migrate_backups(self.homes)
        self.assertTrue(all(path.exists() for path in sources))

        def chmod_after_backup(*args, **kwargs):
            result = save(*args, **kwargs)
            sources[-1].chmod(0o600)
            return result

        with mock.patch.object(deploy, "backup_files", side_effect=chmod_after_backup):
            with self.assertRaisesRegex(ValueError, "source changed"):
                deploy.migrate_backups(self.homes)
        self.assertTrue(all(path.exists() for path in sources))

    def test_migration_rechecks_each_source_immediately_before_removal(self):
        first = self.adjacent_backup(self.destination / "dogwatch-lead.config.toml")
        second = self.adjacent_backup(self.destination / "dogwatch-scoper.config.toml")
        original_read = Path.read_bytes
        reads = 0

        def read_and_replace(path):
            nonlocal reads
            content = original_read(path)
            if path == second:
                reads += 1
                if reads == 1:
                    replacement = first.with_name("replacement")
                    replacement.write_bytes(original_read(first))
                    replacement.replace(first)
            return content

        with mock.patch.object(Path, "read_bytes", read_and_replace):
            with self.assertRaisesRegex(ValueError, "source changed"):
                deploy.migrate_backups(self.homes)
        self.assertTrue(first.exists())
        self.assertTrue(second.exists())

    def test_migration_refuses_symlinks_before_moving_anything(self):
        source = self.adjacent_backup(self.destination / "dogwatch-lead.config.toml")
        linked = self.destination / "dogwatch-scoper.config.toml.bak-20261118T123456Z"
        linked.symlink_to(source)
        result = self.cli("--migrate-backups")
        self.assertEqual(result.returncode, 2)
        self.assertIn("symlink backup source", result.stderr)
        self.assertTrue(source.exists())
        self.assertFalse(self.state_home.exists())
        linked.unlink()
        (self.destination / "agents").symlink_to(self.home)
        result = self.cli("--migrate-backups")
        self.assertEqual(result.returncode, 2)
        self.assertIn("symlink backup directory", result.stderr)
        self.assertTrue(source.exists())
        self.assertFalse(self.state_home.exists())

    def test_migration_deduplicates_shared_homes_and_rejects_conflicting_modes(self):
        self.homes["claude"] = self.destination
        path = self.adjacent_backup(self.destination / "skills/dogwatch-scope/SKILL.md")
        for option in ("--uninstall", "--check", "--replace"):
            result = self.cli("--migrate-backups", option)
            self.assertNotEqual(result.returncode, 0)
            self.assertTrue(path.exists())
            self.assertFalse(self.state_home.exists())
        result = self.cli("--migrate-backups")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(self.backups(path)), 1)
        self.assertFalse(path.exists())


if __name__ == "__main__":
    unittest.main()
