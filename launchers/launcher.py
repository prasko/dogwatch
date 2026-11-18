#!/usr/bin/env python3
# Managed by agentic-setup: Herdr agent launcher.
"""Launch Codex or Claude with access to the current Herdr TUI socket."""

import json
import os
from pathlib import Path
import sys
import tomllib


MARKER = "# Managed by agentic-setup: Herdr agent launcher."
AGENTS = ("codex", "claude")
CODEX_ADMIN_COMMANDS = {
    "agents", "login", "logout", "mcp", "plugin", "app-server",
    "remote-control", "app", "completion", "update", "doctor", "sandbox",
    "debug", "apply", "a", "queue", "archive", "delete", "migrate-rollouts",
    "migrate-nfs-db", "unarchive", "cloud", "exec-server", "features", "help",
}
CODEX_VALUE_OPTIONS = {
    "-c", "--config", "-i", "--image", "-m", "--model", "-p", "--profile",
    "-C", "--cd", "--add-dir", "--remote", "--remote-auth-token-env",
    "--local-provider", "--enable", "--disable", "-a", "--ask-for-approval",
    "-s", "--sandbox",
}
LEGACY_FLAGS = {
    "--sandbox", "-s", "--approve-for-me", "--not-so-yolo",
    "--dangerously-bypass-approvals-and-sandbox", "--yolo",
}


def find_binary(agent, environ, wrapper_dir=None):
    """Search PATH past our wrappers, including symlinks and copied wrappers."""
    wrapper = (wrapper_dir or Path(__file__).resolve().parent / "bin") / agent
    for directory in environ.get("PATH", os.defpath).split(os.pathsep):
        # An empty or relative PATH entry must not select a repository executable.
        if not os.path.isabs(directory):
            continue
        candidate = Path(directory) / agent
        if not candidate.is_file() or not os.access(candidate, os.X_OK):
            continue
        if candidate.resolve() == wrapper.resolve():
            continue
        with candidate.open("rb") as stream:
            if MARKER.encode() in stream.read(256):
                continue
        return str(candidate)
    raise ValueError(f"No installed {agent} executable found on PATH beyond the Herdr launchers.")


def codex_arguments(args):
    """Inspect options without treating their values or a literal prompt as flags."""
    command = None
    options = []
    index = 0
    while index < len(args):
        arg = args[index]
        if arg == "--":
            break
        key, separator, value = arg.partition("=")
        if arg.startswith("-") and not arg.startswith("--") and arg[:2] in CODEX_VALUE_OPTIONS:
            key = arg[:2]
            value = arg[2:]
            separator = bool(value)
        if key in CODEX_VALUE_OPTIONS and not separator:
            index += 1
            if index == len(args):
                raise ValueError(f"Missing value for {key}.")
            value = args[index]
        if arg.startswith("-"):
            options.append((key, value))
        elif command is None:
            command = arg
        index += 1
    return command, options


def has_legacy_settings(settings):
    return "sandbox_mode" in settings or "sandbox_workspace_write" in settings


def check_codex_settings(options, environ):
    """Catch legacy settings that would defeat the socket permission profile."""
    for key, value in options:
        if key in LEGACY_FLAGS:
            raise ValueError(
                "The Herdr launcher needs Codex permission profiles; omit --sandbox, "
                "--approve-for-me and bypass flags. To use automatic approval review, "
                'set approvals_reviewer="auto_review" in config.toml instead.'
            )
        if key in {"-c", "--config"}:
            setting = value.partition("=")[0].strip().strip('"')
            if setting.split(".")[0] in {"sandbox_mode", "sandbox_workspace_write"}:
                raise ValueError("Legacy Codex sandbox overrides disable the Herdr socket exception.")

    home = Path(environ.get("CODEX_HOME", str(Path.home() / ".codex"))).expanduser()
    paths = [] if any(key == "--ignore-user-config" for key, _ in options) else [home / "config.toml"]
    profiles = [value for key, value in options if key in {"-p", "--profile"}]
    if profiles:
        paths.append(home / f"{profiles[-1]}.config.toml")
    for path in paths:
        if path.is_file() and has_legacy_settings(tomllib.loads(path.read_text())):
            raise ValueError(f"Legacy sandbox settings in {path}; migrate them to permission profiles first.")


def launch_argv(agent, args, environ):
    real = find_binary(agent, environ)
    if environ.get("HERDR_ENV") != "1":
        return [real, *args]
    before_separator = args[:args.index("--")] if "--" in args else args
    if agent == "codex":
        command, options = codex_arguments(args)
        keys = {key for key, _ in options}
        if keys & {"--help", "-h", "--version", "-V", "--remote"} or command in CODEX_ADMIN_COMMANDS:
            return [real, *args]
    elif any(arg in {"--help", "-h", "--version", "-v"} for arg in before_separator):
        return [real, *args]

    socket = environ.get("HERDR_SOCKET_PATH", "")
    if not socket or not os.path.isabs(socket) or "\x00" in socket:
        raise ValueError(
            "HERDR_ENV=1 but HERDR_SOCKET_PATH is not an absolute socket path. "
            "Open a fresh Herdr terminal pane and try again."
        )
    # /tmp and /var may be symlinks to /private on macOS. Both spellings identify
    # the same socket; neither grants access to the containing directory.
    sockets = list(dict.fromkeys([socket, os.path.realpath(socket)]))
    if agent == "claude":
        if any(arg == "--settings" or arg.startswith("--settings=") for arg in before_separator):
            raise ValueError(
                "Claude --settings would replace the Herdr socket override. "
                "Keep custom settings in settings.json, or use flags such as --permission-mode."
            )
        settings = {"sandbox": {
            "enabled": True,
            "failIfUnavailable": True,
            "network": {"allowUnixSockets": sockets},
        }}
        return [real, "--settings", json.dumps(settings), *args]

    check_codex_settings(options, environ)
    extra = []
    if command not in {"exec", "e", "review"} and "--no-daemon" not in keys:
        extra.append("--no-daemon")
    overrides = [
        'default_permissions="herdr"',
        'permissions.herdr.extends=":workspace"',
        'permissions.herdr.network.enabled=true',
        'features.network_proxy=true',
    ]
    socket_table = "{" + ", ".join(json.dumps(path) + '="allow"' for path in sockets) + "}"
    overrides.append("permissions.herdr.network.unix_sockets=" + socket_table)
    for value in overrides:
        extra.extend(["-c", value])
    return [real, *extra, *args]


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in AGENTS:
        sys.exit("Usage: launcher.py codex|claude [arguments...]")
    try:
        argv = launch_argv(sys.argv[1], sys.argv[2:], os.environ)
        os.execv(argv[0], argv)
    except (ValueError, OSError) as error:
        sys.exit("Herdr agent launcher: " + str(error))


if __name__ == "__main__":
    main()
