#!/usr/bin/env python3
# Managed by dogwatch: Herdr agent launcher.
"""Send optional watch prompts while the owning Codex Assistant process is alive."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import time
import tomllib


PROMPT = (
    "Dogwatch periodic check: follow the Assistant role's periodic-check procedure "
    "using this repository's dogwatch.toml. Check only enabled sources, "
    "skip work already in progress, and report only new actionable findings."
)
SWITCHES = ("pull_requests", "issues", "scan_todo")


def watch_prompt(root):
    return (f"{PROMPT} Repository: {json.dumps(str(root))}. "
            "If this session now serves another repository, skip this check.")


def read_watch(root):
    """Return an enabled watch table, or None when this repository opts out."""
    path = root / "dogwatch.toml"
    if not path.exists():
        return None
    config = tomllib.loads(path.read_text())
    todo = config.get("todo_file")
    if todo is not None and (not isinstance(todo, str) or not todo.strip()
                             or Path(todo).is_absolute()):
        raise ValueError("todo_file must be a nonempty repository-relative path")
    assistant = config.get("assistant", {})
    if not isinstance(assistant, dict):
        raise ValueError("assistant must be a TOML table")
    watch = assistant.get("watch", {})
    if not isinstance(watch, dict) or set(watch) - {*SWITCHES, "interval_minutes"}:
        raise ValueError("Unsupported assistant.watch settings")
    interval = watch.get("interval_minutes", 30)
    if type(interval) is not int or interval <= 0:
        raise ValueError("assistant.watch.interval_minutes must be a positive integer")
    for key in SWITCHES:
        if type(watch.get(key, False)) is not bool:
            raise ValueError(f"assistant.watch.{key} must be true or false")
    if watch.get("scan_todo") and todo is None:
        raise ValueError("assistant.watch.scan_todo requires todo_file")
    if not any(watch.get(key, False) for key in SWITCHES):
        return None
    return {"interval_minutes": interval, **watch}


def project_root(directory):
    result = subprocess.run(["git", "-C", str(directory), "rev-parse", "--show-toplevel"],
                            capture_output=True, text=True, timeout=5)
    return Path(result.stdout.strip()) if result.returncode == 0 else None


def agent_info(herdr, pane):
    result = subprocess.run([herdr, "agent", "get", pane], capture_output=True,
                            text=True, timeout=5)
    if result.returncode:
        return None
    payload = json.loads(result.stdout).get("result", {})
    return payload.get("agent") if payload.get("type") == "agent_info" else None


def owner_foreground(owner_pid):
    """Do not paste into a shell or another program while the CLI is suspended."""
    result = subprocess.run(["ps", "-o", "pgid=", "-o", "tpgid=", "-p", str(owner_pid)],
                            capture_output=True, text=True, timeout=5)
    groups = result.stdout.split()
    return (result.returncode == 0 and len(groups) == 2 and groups[0].isdigit()
            and groups[0] == groups[1])


def run_watch(root, pane, herdr, owner_pid, settings):
    """Skip busy ticks; never retry an uncertain delivery or catch up missed ticks."""
    deadline = time.monotonic() + settings["interval_minutes"] * 60
    next_owner_check = time.monotonic()
    identity = None
    while os.getppid() == owner_pid:
        time.sleep(1)
        if os.getppid() != owner_pid:
            return
        current = read_watch(root)
        if current is None:
            return
        if current["interval_minutes"] != settings["interval_minutes"]:
            deadline = time.monotonic() + current["interval_minutes"] * 60
        settings = current
        now = time.monotonic()
        due = now >= deadline
        if due:
            deadline = now + settings["interval_minutes"] * 60
        if not due and now < next_owner_check:
            continue
        next_owner_check = now + 5
        if not owner_foreground(owner_pid):
            continue
        agent = agent_info(herdr, pane)
        if not agent or agent.get("agent") != "codex":
            if identity is not None:
                return
            continue  # The integration may not have registered the new CLI yet.
        session = agent.get("agent_session")
        if not session or not session.get("value"):
            continue
        if identity is not None and session != identity:
            return
        identity = session
        if not due or agent.get("agent_status") not in {"idle", "done"}:
            continue
        if os.getppid() != owner_pid or not owner_foreground(owner_pid):
            return
        # Herdr has no atomic idle-only submission. A user turn may start between
        # this check and submission; do not retry even if delivery times out.
        try:
            subprocess.run([herdr, "agent", "prompt", pane, watch_prompt(root)],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
        except subprocess.TimeoutExpired:
            pass


def start_watch(root, pane, settings, environ):
    """Fork once before exec; getppid changes when the owning CLI exits."""
    herdr = shutil.which("herdr", path=environ.get("PATH"))
    if not herdr:
        raise ValueError("herdr is required for Assistant periodic checks")
    owner_pid = os.getpid()
    child = os.fork()
    if child:
        return child
    try:
        os.setsid()
        with open(os.devnull, "r+b", buffering=0) as null:
            for fd in (0, 1, 2):
                os.dup2(null.fileno(), fd)
        run_watch(root, pane, herdr, owner_pid, settings)
    except (OSError, ValueError, subprocess.SubprocessError):
        # Losing configuration, ownership or the Herdr connection stops the timer.
        pass
    finally:
        os._exit(0)
