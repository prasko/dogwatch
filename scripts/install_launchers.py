#!/usr/bin/env python3
"""Install or remove Herdr-only agent launchers; use --dry-run to preview. Never edits agent settings."""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shlex
import stat
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "launchers"
sys.path.insert(0, str(SOURCE))
from launcher import AGENTS, MARKER, find_binary

BEGIN = "# BEGIN Herdr sandboxed agent launchers"
END = "# END Herdr sandboxed agent launchers"


def shell_block(package):
    directory = shlex.quote(str(package / "bin"))
    return (
        BEGIN + "\n"
        'if [[ "${HERDR_ENV:-}" == "1" && "$PATH" != ' + directory + ':* ]]; then\n'
        '  export PATH=' + directory + ':"$PATH"\n'
        "fi\n" + END + "\n"
    )


def update_shell(text, block):
    pattern = re.compile(r"^" + re.escape(BEGIN) + r"\n.*?^" + re.escape(END) + r"(?:\n|$)",
                         re.MULTILINE | re.DOTALL)
    matches = list(pattern.finditer(text))
    if text.count(BEGIN) != len(matches) or text.count(END) != len(matches) or len(matches) > 1:
        raise ValueError("Malformed or duplicate Herdr launcher block in shell startup file; review it first.")
    if matches:
        return pattern.sub(lambda _: block, text)
    if not block:
        return text
    return text + ("\n" if text and not text.endswith("\n") else "") + ("\n" if text else "") + block


def snapshot(path):
    if not path.exists():
        return None, None
    return path.read_bytes(), stat.S_IMODE(path.stat().st_mode)


def plan(package, shell_rc, targets, *, uninstall=False, replace=False):
    """Preflight the whole operation before creating any directories or backups."""
    outputs = {}
    relative_paths = [Path("bin") / target for target in targets]
    remaining = [target for target in AGENTS
                 if target not in targets and (package / "bin" / target).exists()]
    if not uninstall or not remaining:
        relative_paths.append(Path("launcher.py"))
    for relative in relative_paths:
        path = package / relative
        if any(part.is_symlink() for part in (path, *path.parents)):
            raise ValueError(f"Refusing symlink in launcher destination: {path}")
        old, _ = snapshot(path)
        if old is not None and MARKER.encode() not in old[:256] and not replace:
            raise ValueError(f"Unmanaged file: {path}. Review it, then use --replace to back it up and replace/remove it.")
        outputs[path] = (None if uninstall else (SOURCE / relative).read_bytes(),
                         0o755 if relative.parent == Path("bin") else 0o644)

    # Shell dotfiles are often symlinks into a dotfiles checkout. Edit their target
    # atomically and keep the link, while generated launcher paths refuse links.
    shell_rc = shell_rc.resolve()
    if shell_rc == package or package in shell_rc.parents:
        raise ValueError("The shell startup file must be outside the launcher directory.")
    old, mode = snapshot(shell_rc)
    text = (old or b"").decode()
    block = shell_block(package) if not uninstall or remaining else ""
    updated = update_shell(text, block).encode()
    if updated != (old or b""):
        outputs[shell_rc] = updated, mode if mode is not None else 0o644
    return {path: value for path, value in outputs.items()
            if snapshot(path) != value and not (value[0] is None and not path.exists())}


def atomic_write(path, content, mode):
    if content is None:
        path.unlink(missing_ok=True)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".herdr-setup-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(content)
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def apply(changes, state_home):
    if not changes:
        return None
    previous = {path: snapshot(path) for path in changes}
    backup = state_home / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    backup.mkdir(parents=True, mode=0o700)
    manifest = {}
    for number, (path, (content, mode)) in enumerate(previous.items()):
        saved = None
        if content is not None:
            saved = backup / f"{number}-{path.name}"
            atomic_write(saved, content, 0o600)
        manifest[str(path)] = {"backup": str(saved) if saved else None, "mode": mode}
    atomic_write(backup / "manifest.json", (json.dumps(manifest, indent=2) + "\n").encode(), 0o600)

    applied = []
    try:
        for path, (content, mode) in changes.items():
            atomic_write(path, content, mode)
            applied.append(path)
    except OSError as error:
        failures = []
        for path in reversed(applied):
            try:
                atomic_write(path, *previous[path])
            except OSError:
                failures.append(str(path))
        detail = "Rollback incomplete for: " + ", ".join(failures) if failures else "Changed files restored."
        raise OSError(f"{error}. {detail} Backups: {backup}") from error
    return backup


def main():
    home = Path.home()
    config_home = Path(os.environ.get("XDG_CONFIG_HOME", str(home / ".config")))
    state_home = Path(os.environ.get("XDG_STATE_HOME", str(home / ".local/state")))
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", choices=(*AGENTS, "all"), default="all")
    parser.add_argument("--launcher-home", type=Path, default=config_home / "herdr/agent-launchers")
    parser.add_argument("--shell-rc", type=Path,
                        default=Path(os.environ.get("ZDOTDIR", str(home))) / ".zshrc")
    parser.add_argument("--state-home", type=Path, default=state_home / "herdr-agent-setup")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without writing")
    parser.add_argument("--uninstall", action="store_true", help="Remove selected launchers and their PATH block")
    parser.add_argument("--replace", action="store_true", help="Back up and replace/remove unmanaged launcher files")
    args = parser.parse_args()
    targets = AGENTS if args.target == "all" else (args.target,)
    package = args.launcher_home.expanduser().absolute()
    try:
        changes = plan(package, args.shell_rc.expanduser().absolute(), targets,
                       uninstall=args.uninstall, replace=args.replace)
        if not args.uninstall:
            for target in targets:
                print(f"{target}: {find_binary(target, os.environ, package / 'bin')}")
        for path, (content, _) in changes.items():
            print(f"{'Remove' if content is None else 'Write'} {path}")
        if not changes:
            print("Already up to date.")
        elif args.dry_run:
            print("Preview only. Run without --dry-run to write these changes.")
        else:
            backup = apply(changes, args.state_home.expanduser().absolute())
            print(f"Done. Backups and original modes: {backup}/manifest.json")
            print("Open a fresh Herdr pane. Existing shells and sessions keep their launch settings.")
    except (OSError, ValueError) as error:
        parser.exit(1, f"Launcher setup failed: {error}\n")


if __name__ == "__main__":
    main()
