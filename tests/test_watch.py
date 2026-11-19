import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "launchers"))
import launcher
import watch


class WatchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.config = self.root / "dogwatch.toml"
        self.config.write_text('[assistant.watch]\nissues = true\ninterval_minutes = 1\n')
        self.settings = watch.read_watch(self.root)

    def test_optional_config_and_shared_todo(self):
        for content in ('', 'todo_file = "docs/backlog.md"\n', '[assistant.watch]\n'):
            self.config.write_text(content)
            self.assertIsNone(watch.read_watch(self.root))
        self.config.unlink()
        self.assertIsNone(watch.read_watch(self.root))
        self.config.write_text((ROOT / "dogwatch.toml").read_text())
        self.assertEqual(watch.read_watch(self.root), {
            "interval_minutes": 30, "pull_requests": True, "issues": True, "scan_todo": True,
        })
        self.config.write_text('[assistant.watch]\nissues = true\n')
        self.assertEqual(watch.read_watch(self.root)["interval_minutes"], 30)

    def test_invalid_settings_are_not_silently_enabled(self):
        cases = (
            'todo_file = ""', 'todo_file = "/tmp/todo.md"', 'todo_file = true',
            'assistant = true', '[assistant]\nwatch = true',
            '[assistant.watch]\nscan_todo = true', '[assistant.watch]\nissue = true',
            '[assistant.watch]\nissues = "true"', '[assistant.watch]\nissues = 1',
            '[assistant.watch]\ninterval_minutes = true',
            '[assistant.watch]\ninterval_minutes = 0',
            '[assistant.watch]\ninterval_minutes = -1',
            '[assistant.watch]\ninterval_minutes = 1.5', 'invalid toml',
        )
        for content in cases:
            with self.subTest(content=content):
                self.config.write_text(content)
                with self.assertRaises(ValueError):
                    watch.read_watch(self.root)

    def run_cycles(self, agents, *, foreground=True, error=None, on_sleep=None, step_seconds=60):
        clock = [0]
        owner = [123]
        answers = iter(agents)

        def sleep(_):
            clock[0] += step_seconds
            if on_sleep:
                on_sleep(clock[0])

        def info(*_):
            try:
                return next(answers)
            except StopIteration:
                owner[0] = 1
                return None

        with (mock.patch.object(watch.time, "monotonic", side_effect=lambda: clock[0]),
              mock.patch.object(watch.time, "sleep", side_effect=sleep),
              mock.patch.object(watch.os, "getppid", side_effect=lambda: owner[0]),
              mock.patch.object(watch, "owner_foreground", return_value=foreground),
              mock.patch.object(watch, "agent_info", side_effect=info),
              mock.patch.object(watch.subprocess, "run", side_effect=error) as submit):
            watch.run_watch(self.root, "pane:1", "/bin/herdr", 123, self.settings)
        return submit

    def agent(self, status="idle", session="one"):
        return {"agent": "codex", "agent_status": status,
                "agent_session": {"source": "herdr:codex", "kind": "id", "value": session}}

    def test_busy_blocked_and_unidentified_sessions_are_skipped(self):
        unidentified = self.agent()
        del unidentified["agent_session"]
        submit = self.run_cycles([
            self.agent("working"), self.agent("blocked"), self.agent("unknown"),
            unidentified, self.agent(), self.agent("done"),
        ])
        self.assertEqual(submit.call_count, 2)
        self.assertEqual(submit.call_args.args[0],
                         ["/bin/herdr", "agent", "prompt", "pane:1", watch.watch_prompt(self.root)])

    def test_session_replacement_stops_timer(self):
        submit = self.run_cycles([self.agent(), self.agent(session="replacement"), self.agent()])
        self.assertEqual(submit.call_count, 1)

    def test_session_replacement_before_first_tick_stops_without_prompt(self):
        submit = self.run_cycles([self.agent(), self.agent(session="replacement")], step_seconds=10)
        submit.assert_not_called()

    def test_other_provider_stops_timer(self):
        submit = self.run_cycles([self.agent() | {"agent": "claude"}])
        submit.assert_not_called()

    def test_disabling_config_stops_without_prompt(self):
        submit = self.run_cycles([self.agent()], on_sleep=lambda _: self.config.unlink())
        submit.assert_not_called()

    def test_suspended_owner_does_not_receive_prompts(self):
        def disable_later(now):
            if now == 120:
                self.config.unlink()
        submit = self.run_cycles([self.agent()], foreground=False, on_sleep=disable_later)
        submit.assert_not_called()

    def test_uncertain_delivery_is_not_retried(self):
        submit = self.run_cycles([self.agent()], error=subprocess.TimeoutExpired("herdr", 5))
        self.assertEqual(submit.call_count, 1)

    def test_interval_change_resets_deadline(self):
        def change_interval(now):
            if now == 60:
                self.config.write_text('[assistant.watch]\nissues = true\ninterval_minutes = 2\n')
            if now == 240:
                self.config.unlink()
        submit = self.run_cycles([self.agent(), self.agent(), self.agent()], on_sleep=change_interval)
        self.assertEqual(submit.call_count, 1)

    def test_parent_exit_during_wait_stops_immediately(self):
        with (mock.patch.object(watch.os, "getppid", side_effect=[123, 1]),
              mock.patch.object(watch.time, "sleep"),
              mock.patch.object(watch, "agent_info") as info):
            watch.run_watch(self.root, "pane:1", "/bin/herdr", 123, self.settings)
        info.assert_not_called()

    def test_foreground_group_requires_positive_matching_ids(self):
        for output, expected in (("123 123\n", True), ("123 124\n", False),
                                 ("-1 -1\n", False), ("", False)):
            with self.subTest(output=output), mock.patch.object(
                    watch.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, output)):
                self.assertEqual(watch.owner_foreground(123), expected)

    def test_herdr_response_and_read_failure(self):
        response = {"result": {"type": "agent_info", "agent": self.agent()}}
        with mock.patch.object(watch.subprocess, "run", return_value=
                               subprocess.CompletedProcess([], 0, json.dumps(response))):
            self.assertEqual(watch.agent_info("herdr", "pane:1"), self.agent())
        with mock.patch.object(watch.subprocess, "run", return_value=
                               subprocess.CompletedProcess([], 1, "unavailable")):
            self.assertIsNone(watch.agent_info("herdr", "pane:1"))

    def test_launcher_limits_timer_to_explicit_interactive_assistant(self):
        env = {"HERDR_ENV": "1", "HERDR_PANE_ID": "pane:1"}
        cases = (
            ("codex", ["--profile", "dogwatch-assistant"], env, True),
            ("codex", ["-pdogwatch-assistant", "-C", str(self.root)], env, True),
            ("codex", ["--profile=dogwatch-assistant"], env, True),
            ("codex", ["--profile", "dogwatch-assistant", "exec", "hi"], env, False),
            ("codex", ["--profile", "dogwatch-assistant", "--help"], env, False),
            ("codex", ["--profile", "dogwatch-assistant", "--remote", "host"], env, False),
            ("codex", ["--profile", "dogwatch-assistant", "-p", "dogwatch-lead"], env, False),
            ("codex", [], env, False),
            ("codex", ["--profile", "dogwatch-assistant"], {}, False),
            ("claude", ["--agent", "dogwatch-assistant"], env, False),
        )
        for agent, args, environment, expected in cases:
            with (self.subTest(agent=agent, args=args, env=environment),
                  mock.patch.object(watch, "project_root", return_value=self.root),
                  mock.patch.object(watch, "start_watch", return_value=456) as start):
                launcher.assistant_watch(agent, args, environment)
                self.assertEqual(start.called, expected)
                if expected:
                    self.assertEqual(environment["DOGWATCH_WATCH_PID"], "456")
                    self.assertEqual(environment["DOGWATCH_WATCH_OWNER_PID"], str(os.getpid()))
                else:
                    self.assertNotIn("DOGWATCH_WATCH_PID", environment)
                if "-C" in args:
                    watch.project_root.assert_called_once_with(self.root)

    def test_ambiguous_checkout_launches_warn_and_skip_timer(self):
        for args in (["resume"], ["fork"], ["--worktree"]):
            with (self.subTest(args=args),
                  mock.patch.object(watch, "project_root", return_value=self.root),
                  mock.patch.object(watch, "start_watch") as start,
                  mock.patch("sys.stderr") as stderr):
                launcher.assistant_watch("codex", ["-p", "dogwatch-assistant", *args],
                                         {"HERDR_ENV": "1", "HERDR_PANE_ID": "pane:1"})
                start.assert_not_called()
                self.assertIn("can change the checkout", "".join(c.args[0] for c in stderr.write.call_args_list))

    def test_launcher_reports_invalid_config_without_blocking_cli(self):
        self.config.write_text('[assistant.watch]\ninterval_minutes = 0\n')
        with (mock.patch.object(watch, "project_root", return_value=self.root),
              mock.patch.object(watch, "start_watch") as start,
              mock.patch("sys.stderr") as stderr):
            launcher.assistant_watch("codex", ["-p", "dogwatch-assistant"], {"HERDR_ENV": "1"})
        start.assert_not_called()
        self.assertIn("periodic checks disabled", "".join(c.args[0] for c in stderr.write.call_args_list))

    @unittest.skipUnless(hasattr(os, "fork"), "launcher timers require fork")
    def test_timer_survives_exec_and_exits_with_its_cli(self):
        """Exercise real fork/exec and fake CLI/Herdr, with an accelerated tick clock."""
        binary = self.root / "bin"
        binary.mkdir()
        for name, body in {
            "codex": "(root / 'ready').touch()\ninput()\n",
            "herdr": (
                "if sys.argv[1:3] == ['agent', 'get']:\n"
                "    agent = {'agent': 'codex', 'agent_status': (root / 'status').read_text(),\n"
                "             'agent_session': {'kind': 'id', 'value': 'test-session'}}\n"
                "    print(json.dumps({'result': {'type': 'agent_info', 'agent': agent}}))\n"
                "elif sys.argv[1:3] == ['agent', 'prompt']:\n"
                "    (root / 'prompted').write_text(sys.argv[4])\n"
            ),
        }.items():
            executable = binary / name
            executable.write_text(f"#!{sys.executable}\nimport json, sys\nfrom pathlib import Path\n"
                                  f"root = Path({str(self.root)!r})\n" + body)
            executable.chmod(0o755)
        driver = self.root / "driver.py"
        driver.write_text(
            "import sys\nfrom pathlib import Path\n"
            f"sys.path.insert(0, {str(ROOT / 'launchers')!r})\n"
            "import launcher, watch\n"
            f"root = Path({str(self.root)!r})\n"
            "watch.project_root = lambda _: root\n"
            "watch.owner_foreground = lambda _: True\n"
            "real_now = watch.time.monotonic\n"
            "watch.time.monotonic = lambda: real_now() * 60\n"
            "run = watch.run_watch\n"
            "def tracked_run(*args):\n"
            "    try:\n"
            "        run(*args)\n"
            "    finally:\n"
            "        (root / 'timer-exited').touch()\n"
            "watch.run_watch = tracked_run\n"
            "launcher.main()\n"
        )
        env = os.environ | {
            "PATH": str(binary) + os.pathsep + os.defpath,
            "CODEX_HOME": str(self.root / "codex-home"),
            "HERDR_ENV": "1", "HERDR_PANE_ID": "test-pane",
            "HERDR_SOCKET_PATH": str(self.root / "fake.sock"),
        }
        (self.root / "status").write_text("working")
        process = subprocess.Popen(
            [sys.executable, str(driver), "codex", "-p", "dogwatch-assistant"],
            env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )

        def wait_file(name):
            deadline = time.monotonic() + 5
            while time.monotonic() < deadline and not (self.root / name).exists():
                time.sleep(0.05)
            self.assertTrue((self.root / name).exists(), name)

        try:
            wait_file("ready")
            time.sleep(1.2)
            self.assertFalse((self.root / "prompted").exists())
            (self.root / "status").write_text("idle")
            wait_file("prompted")
            self.assertEqual((self.root / "prompted").read_text(), watch.watch_prompt(self.root))
            _, errors = process.communicate(b"\n", timeout=5)
            self.assertEqual(process.returncode, 0, errors)
        finally:
            if process.poll() is None:
                process.kill()
            process.communicate(timeout=5)
            wait_file("timer-exited")


if __name__ == "__main__":
    unittest.main()
