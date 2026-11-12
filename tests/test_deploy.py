from contextlib import redirect_stdout
import importlib.util
import io
from pathlib import Path
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
        self.destination = Path(self.temp.name).resolve() / "codex"
        self.outputs = deploy.render()
        quiet = redirect_stdout(io.StringIO())
        quiet.__enter__()
        self.addCleanup(quiet.__exit__, None, None, None)

    def test_profiles_and_agents_have_same_instructions_without_permission_overrides(self):
        self.assertEqual(len(self.outputs), 6)
        for role in deploy.ROLES:
            agent = tomllib.loads(self.outputs[f"agents/{role}.toml"])
            profile = tomllib.loads(self.outputs[f"agentic-{role}.config.toml"])
            self.assertEqual(agent["name"], role)
            self.assertEqual(agent["developer_instructions"], profile["developer_instructions"])
            self.assertIn(f"# {role.title()}", profile["developer_instructions"])
            self.assertEqual(set(profile), {"developer_instructions"})

    def test_dry_run_does_not_create_destination(self):
        deploy.deploy(self.destination, self.outputs, dry_run=True)
        self.assertFalse(self.destination.exists())

    def test_install_repeat_check_and_preserve_unrelated_files(self):
        self.destination.mkdir()
        config = self.destination / "config.toml"
        config.write_text('model = "existing-model"\n')
        hooks = self.destination / "hooks.json"
        hooks.write_text('{"hooks": {}}\n')
        self.assertEqual(deploy.deploy(self.destination, self.outputs, check=True), 1)
        deploy.deploy(self.destination, self.outputs)
        before = {path: path.stat().st_mtime_ns for path in self.destination.rglob("*.toml")}
        deploy.deploy(self.destination, self.outputs)
        self.assertEqual(before, {path: path.stat().st_mtime_ns for path in before})
        self.assertEqual(deploy.deploy(self.destination, self.outputs, check=True), 0)
        self.assertEqual(config.read_text(), 'model = "existing-model"\n')
        self.assertEqual(hooks.read_text(), '{"hooks": {}}\n')
        self.assertFalse(list(self.destination.rglob("*.bak-*")))

    def test_collision_preflight_then_explicit_replacement_with_backup(self):
        conflict = self.destination / "agents/reviewer.toml"
        conflict.parent.mkdir(parents=True)
        original = b'name = "reviewer"\r\n'
        conflict.write_bytes(original)
        with self.assertRaisesRegex(ValueError, "Unmanaged file"):
            deploy.deploy(self.destination, self.outputs)
        self.assertFalse((self.destination / "agents/lead.toml").exists())
        self.assertEqual(conflict.read_bytes(), original)
        deploy.deploy(self.destination, self.outputs, replace=True)
        backups = list(conflict.parent.glob("reviewer.toml.bak-*"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_bytes(), original)

    def test_changed_managed_file_is_detected_and_backed_up(self):
        deploy.deploy(self.destination, self.outputs)
        path = self.destination / "agentic-lead.config.toml"
        changed = path.read_text() + "# local edit\n"
        path.write_text(changed)
        self.assertEqual(deploy.deploy(self.destination, self.outputs, check=True), 1)
        deploy.deploy(self.destination, self.outputs)
        backups = list(self.destination.glob("agentic-lead.config.toml.bak-*"))
        self.assertEqual(backups[0].read_text(), changed)

    def test_symlink_is_refused_without_touching_target(self):
        target = Path(self.temp.name) / "outside"
        target.write_text("keep me")
        self.destination.mkdir()
        (self.destination / "agentic-reviewer.config.toml").symlink_to(target)
        with self.assertRaisesRegex(ValueError, "symlink"):
            deploy.deploy(self.destination, self.outputs, replace=True)
        self.assertEqual(target.read_text(), "keep me")
        self.assertFalse((self.destination / "agents").exists())


if __name__ == "__main__":
    unittest.main()
