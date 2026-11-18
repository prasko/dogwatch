import importlib.util
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
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("install_launchers", ROOT / "scripts/install_launchers.py")
installer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(installer)
launcher = sys.modules["launcher"]


class LauncherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name).resolve()
        self.bin = self.home / "real bin"
        self.bin.mkdir()
        self.package = self.home / "config space ' quote" / "herdr/agent-launchers"
        self.shell_rc = self.home / "shell/.zshrc"
        self.state = self.home / "state/herdr-agent-setup"
        self.env = {
            "HOME": str(self.home),
            "PATH": os.pathsep.join([str(self.bin), str(Path(sys.executable).parent), "/usr/bin", "/bin"]),
            "XDG_CONFIG_HOME": str(self.package.parents[1]),
            "XDG_STATE_HOME": str(self.state.parent),
            "ZDOTDIR": str(self.shell_rc.parent),
            "CODEX_HOME": str(self.home / "custom codex"),
            "CLAUDE_CONFIG_DIR": str(self.home / "custom claude"),
            "HERDR_ENV": "1",
            "HERDR_SOCKET_PATH": str(self.home / "socket.sock"),
            "PYTHONDONTWRITEBYTECODE": "1",
        }
        for agent in launcher.AGENTS:
            path = self.bin / agent
            path.write_text(f"#!{sys.executable}\nimport json, os, sys\n"
                            "print(json.dumps({'args': sys.argv[1:], "
                            "'codex_home': os.getenv('CODEX_HOME'), "
                            "'claude_home': os.getenv('CLAUDE_CONFIG_DIR')}))\n")
            path.chmod(0o755)

    def cli(self, *args, env=None):
        return subprocess.run([sys.executable, str(ROOT / "scripts/install_launchers.py"), *args],
                              env=env or self.env, capture_output=True, text=True)

    def install(self, *args):
        result = self.cli(*args)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def run_wrapper(self, agent, *args, env=None):
        environment = (env or self.env).copy()
        environment["PATH"] = str(self.package / "bin") + os.pathsep + environment["PATH"]
        return subprocess.run([str(self.package / "bin" / agent), *args], env=environment,
                              capture_output=True, text=True)

    def overrides(self, argv):
        return tomllib.loads("\n".join(argv[i + 1] for i, arg in enumerate(argv) if arg == "-c"))

    def test_preview_does_not_create_destinations(self):
        result = self.cli("--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Preview only", result.stdout)
        self.assertFalse(self.package.exists())
        self.assertFalse(self.shell_rc.exists())
        self.assertFalse(self.state.exists())

    def test_uninstall_preview_preserves_files_and_backups(self):
        self.install()
        paths = [self.shell_rc, self.package / "launcher.py", *self.package.glob("bin/*")]
        before = {path: (path.read_bytes(), path.stat().st_mtime_ns) for path in paths}
        backups = list(self.state.iterdir())
        result = self.cli("--uninstall", "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Preview only", result.stdout)
        self.assertEqual(before, {path: (path.read_bytes(), path.stat().st_mtime_ns) for path in paths})
        self.assertEqual(backups, list(self.state.iterdir()))

    def test_each_provider_installs_without_other_provider_or_settings(self):
        for agent in launcher.AGENTS:
            with self.subTest(agent=agent):
                other = next(name for name in launcher.AGENTS if name != agent)
                hidden = self.bin / (other + ".hidden")
                (self.bin / other).rename(hidden)
                self.install("--target", agent)
                self.assertTrue((self.package / "bin" / agent).exists())
                self.assertFalse((self.package / "bin" / other).exists())
                self.assertFalse(Path(self.env["CODEX_HOME"]).exists())
                self.assertFalse(Path(self.env["CLAUDE_CONFIG_DIR"]).exists())
                self.install("--uninstall", "--target", agent)
                hidden.rename(self.bin / other)

    def test_preserves_preferences_hooks_and_shell_with_repeat_install(self):
        files = {
            Path(self.env["CODEX_HOME"]) / "config.toml":
                b'approval_policy = "on-request"\napprovals_reviewer = "auto_review"\n',
            Path(self.env["CLAUDE_CONFIG_DIR"]) / "settings.json":
                b'{"permissions":{"defaultMode":"manual"},"hooks":{"SessionStart":[]}}\n',
        }
        for path, content in files.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        self.shell_rc.parent.mkdir()
        self.shell_rc.write_text("# user setup\nexport EDITOR=vi\n")
        self.shell_rc.chmod(0o640)
        self.install()
        paths = [self.shell_rc, self.package / "launcher.py", *self.package.glob("bin/*")]
        before = {path: (path.read_bytes(), path.stat().st_mtime_ns) for path in paths}
        backups = list(self.state.iterdir())
        self.install()
        self.assertEqual(before, {path: (path.read_bytes(), path.stat().st_mtime_ns) for path in paths})
        self.assertEqual(backups, list(self.state.iterdir()))
        self.assertEqual(stat.S_IMODE(self.shell_rc.stat().st_mode), 0o640)
        for path, content in files.items():
            self.assertEqual(path.read_bytes(), content)

    def test_installed_wrapper_executes_real_cli_and_passes_custom_homes(self):
        self.install()
        for agent in launcher.AGENTS:
            result = self.run_wrapper(agent, "--version")
            self.assertEqual(result.returncode, 0, result.stderr)
            output = json.loads(result.stdout)
            self.assertEqual(output["args"], ["--version"])
            self.assertEqual(output["codex_home"], self.env["CODEX_HOME"])
            self.assertEqual(output["claude_home"], self.env["CLAUDE_CONFIG_DIR"])

    @unittest.skipUnless(shutil.which("zsh"), "zsh is required for shell activation")
    def test_shell_activates_only_inside_herdr_with_quoted_paths(self):
        self.install("--target", "codex")
        script = 'source "$1"; source "$1"; command -v codex; print -r -- "$PATH"'
        for inside in ("0", "1"):
            result = subprocess.run([shutil.which("zsh"), "-f", "-c", script, "zsh", str(self.shell_rc)],
                                    env=self.env | {"HERDR_ENV": inside}, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            binary, path = result.stdout.splitlines()
            expected = self.package / "bin/codex" if inside == "1" else self.bin / "codex"
            self.assertEqual(binary, str(expected))
            self.assertEqual(path.split(":").count(str(self.package / "bin")), int(inside))

    def test_discovery_skips_wrappers_and_symlinks_and_tracks_binary_updates(self):
        self.install()
        aliases = self.home / "aliases"
        aliases.mkdir()
        (aliases / "codex").symlink_to(self.package / "bin/codex")
        env = self.env | {"PATH": os.pathsep.join([str(aliases), str(self.package / "bin"), str(self.bin)])}
        self.assertEqual(launcher.find_binary("codex", env), str(self.bin / "codex"))
        (self.bin / "codex").unlink()
        with self.assertRaisesRegex(ValueError, "No installed codex"):
            launcher.find_binary("codex", env)
        (self.bin / "codex-new").write_text("#!/bin/sh\nexit 0\n")
        (self.bin / "codex-new").chmod(0o755)
        (self.bin / "codex").symlink_to(self.bin / "codex-new")
        self.assertEqual(launcher.find_binary("codex", env), str(self.bin / "codex"))

    def test_unmanaged_collision_preflights_then_backs_up_on_replace(self):
        path = self.package / "launcher.py"
        path.parent.mkdir(parents=True)
        original = b"# prior local launcher\r\n"
        path.write_bytes(original)
        result = self.cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unmanaged file", result.stderr)
        self.assertFalse(self.shell_rc.exists())
        self.assertFalse((self.package / "bin").exists())
        self.install("--replace")
        manifest_path = next(self.state.glob("*/manifest.json"))
        manifest = json.loads(manifest_path.read_text())
        saved = Path(manifest[str(path)]["backup"])
        self.assertEqual(saved.read_bytes(), original)
        self.assertEqual(stat.S_IMODE(saved.stat().st_mode), 0o600)
        self.assertEqual(stat.S_IMODE(manifest_path.parent.stat().st_mode), 0o700)

    def test_partial_then_complete_uninstall_preserves_unrelated_files(self):
        self.install()
        unrelated = self.package / "personal.txt"
        unrelated.write_text("keep")
        self.install("--uninstall", "--target", "codex")
        self.assertFalse((self.package / "bin/codex").exists())
        self.assertTrue((self.package / "bin/claude").exists())
        self.assertIn(installer.BEGIN, self.shell_rc.read_text())
        result = self.run_wrapper("claude", "--version")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.install("--uninstall", "--target", "claude")
        self.assertFalse((self.package / "launcher.py").exists())
        self.assertNotIn(installer.BEGIN, self.shell_rc.read_text())
        self.assertEqual(unrelated.read_text(), "keep")
        before = list(self.state.iterdir())
        self.install("--uninstall")
        self.assertEqual(before, list(self.state.iterdir()))

    def test_missing_binary_aborts_before_writes(self):
        (self.bin / "claude").unlink()
        result = self.cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.package.exists())
        self.assertFalse(self.shell_rc.exists())

    def test_shell_symlink_preserved_but_generated_symlink_refused(self):
        dotfile = self.home / "actual.zshrc"
        dotfile.write_text("# shared shell\n")
        self.shell_rc.parent.mkdir()
        self.shell_rc.symlink_to(dotfile)
        self.install()
        self.assertTrue(self.shell_rc.is_symlink())
        self.assertIn(installer.BEGIN, dotfile.read_text())
        wrapper = self.package / "bin/codex"
        wrapper.unlink()
        wrapper.symlink_to(self.bin / "codex")
        result = self.cli("--replace")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("symlink", result.stderr)
        self.assertTrue(wrapper.is_symlink())

    def test_malformed_shell_block_aborts_before_writes(self):
        self.shell_rc.parent.mkdir()
        self.shell_rc.write_text(installer.BEGIN + "\nunfinished\n")
        result = self.cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Malformed", result.stderr)
        self.assertFalse(self.package.exists())

    def test_failed_write_restores_changed_files(self):
        self.install()
        wrapper = self.package / "bin/codex"
        original = installer.snapshot(wrapper)
        absent = self.package / "new-file"
        changes = {wrapper: (original[0] + b"# update\n", 0o755), absent: (b"new", 0o644),
                   self.shell_rc: (b"changed shell", 0o644)}
        real_write = installer.atomic_write

        def fail_shell(path, content, mode):
            if path == self.shell_rc:
                raise OSError("simulated write failure")
            return real_write(path, content, mode)

        with patch.object(installer, "atomic_write", side_effect=fail_shell):
            with self.assertRaisesRegex(OSError, "Changed files restored"):
                installer.apply(changes, self.state)
        self.assertEqual(installer.snapshot(wrapper), original)
        self.assertFalse(absent.exists())

    def test_codex_socket_profile_and_prompt_arguments(self):
        self.install("--target", "codex")
        args = ["--profile", "agentic-lead", "-C", str(self.home / "project space"),
                "-c", 'approvals_reviewer="auto_review"', "--", "--sandbox is just prompt text"]
        result = self.run_wrapper("codex", *args)
        self.assertEqual(result.returncode, 0, result.stderr)
        argv = json.loads(result.stdout)["args"]
        self.assertEqual(argv[-len(args):], args)
        self.assertIn("--no-daemon", argv)
        config = self.overrides(argv)
        self.assertEqual(config["default_permissions"], "herdr")
        self.assertEqual(config["permissions"]["herdr"]["extends"], ":workspace")
        self.assertEqual(config["permissions"]["herdr"]["network"]["unix_sockets"],
                         {self.env["HERDR_SOCKET_PATH"]: "allow"})
        self.assertEqual(config["approvals_reviewer"], "auto_review")
        self.assertNotIn("approval_policy", config)

    def test_codex_exec_review_and_admin_commands(self):
        for command in ("exec", "e", "review"):
            argv = launcher.launch_argv("codex", [command], self.env)
            self.assertNotIn("--no-daemon", argv)
            self.assertIn('default_permissions="herdr"', argv)
        for args in (["login"], ["-m", "help", "exec", "--help"], ["--remote=unix:///server"]):
            self.assertEqual(launcher.launch_argv("codex", args, self.env | {"HERDR_SOCKET_PATH": ""}),
                             [str(self.bin / "codex"), *args])
        argv = launcher.launch_argv("codex", ["-m", "help", "exec"], self.env)
        self.assertIn('default_permissions="herdr"', argv)

    def test_outside_herdr_and_help_pass_through_without_socket(self):
        for agent in launcher.AGENTS:
            env = self.env | {"HERDR_ENV": "0", "HERDR_SOCKET_PATH": ""}
            self.assertEqual(launcher.launch_argv(agent, ["a prompt"], env), [str(self.bin / agent), "a prompt"])
            env["HERDR_ENV"] = "1"
            self.assertEqual(launcher.launch_argv(agent, ["--help"], env), [str(self.bin / agent), "--help"])
            for socket in ("", "relative.sock", "/invalid\x00.sock"):
                with self.assertRaisesRegex(ValueError, "absolute socket path"):
                    launcher.launch_argv(agent, [], env | {"HERDR_SOCKET_PATH": socket})

    def test_codex_legacy_flags_and_root_or_profile_settings_fail_clearly(self):
        for args in (["-sworkspace-write"], ["--sandbox=workspace-write"], ["--approve-for-me"],
                     ["--yolo"], ["-csandbox_mode='workspace-write'"],
                     ["--config", "sandbox_workspace_write.network_access=true"]):
            with self.subTest(args=args), self.assertRaises(ValueError):
                launcher.launch_argv("codex", args, self.env)
        home = Path(self.env["CODEX_HOME"])
        home.mkdir()
        for filename, args in (("config.toml", []), ("agentic-lead.config.toml", ["-pagentic-lead"])):
            path = home / filename
            path.write_text('sandbox_mode="workspace-write"\n')
            with self.assertRaisesRegex(ValueError, "Legacy sandbox settings"):
                launcher.launch_argv("codex", args, self.env)
            path.unlink()

    def test_claude_socket_settings_preserve_arguments_and_canonicalize_socket(self):
        linked = self.home / "linked"
        linked.symlink_to(self.home, target_is_directory=True)
        socket = str(linked / "socket.sock")
        argv = launcher.launch_argv("claude", ["--agent", "agentic-lead", "--permission-mode", "auto"],
                                    self.env | {"HERDR_SOCKET_PATH": socket})
        self.assertEqual(argv[1], "--settings")
        settings = json.loads(argv[2])
        self.assertEqual(settings, {"sandbox": {"enabled": True, "failIfUnavailable": True,
                         "network": {"allowUnixSockets": [socket, str(self.home / "socket.sock")]}}})
        self.assertEqual(argv[3:], ["--agent", "agentic-lead", "--permission-mode", "auto"])

    def test_claude_explicit_settings_cannot_silently_drop_socket_override(self):
        for args in (["--settings", '{"permissions":{"defaultMode":"auto"}}'],
                     ["--settings=custom-settings.json"]):
            with self.subTest(args=args), self.assertRaisesRegex(ValueError, "replace the Herdr socket"):
                launcher.launch_argv("claude", args, self.env)
        # Literal prompt text after -- remains unmodified.
        argv = launcher.launch_argv("claude", ["--", "--settings"], self.env)
        self.assertEqual(argv[-2:], ["--", "--settings"])

    def test_codex_ignore_user_config_skips_only_base_config(self):
        home = Path(self.env["CODEX_HOME"])
        home.mkdir()
        (home / "config.toml").write_text('sandbox_mode="workspace-write"\n')
        args = ["exec", "--ignore-user-config"]
        argv = launcher.launch_argv("codex", args, self.env)
        self.assertIn('default_permissions="herdr"', argv)
        (home / "custom.config.toml").write_text('sandbox_mode="workspace-write"\n')
        with self.assertRaisesRegex(ValueError, "Legacy sandbox settings"):
            launcher.launch_argv("codex", [*args, "--profile", "custom"], self.env)


if __name__ == "__main__":
    unittest.main()
