# Sandboxed Codex and Claude in Herdr TUI

Prepared November 12, 2026 for Codex 0.167.2, Claude Code 2.1.322, and Herdr TUI 0.9.5.

## Readiness and pending steps

Checked November 12, 2026: the installer has never been run. The requested work is to correct the script at `~/.config/herdr/agent-launchers/install.py`; updating that file does not apply any sandbox settings. The corrected script is prepared and tested, but copying it to its original location remains pending because that location is outside this session's writable folders.

The corrections fix multiline TOML handling, replacement of indented and quoted root keys, and preservation of symlinked configuration files. Three regression tests pass, covering ten TOML cases, idempotence, symlink chains and file modes, and rollback after a later write fails. Preview against the current user settings succeeds. Script and test artifacts belong outside this documentation directory; the temporary copies have been moved to `/private/tmp/`.

The commands below document a future installation after the script is updated; they have not been executed with `--apply`. The readiness checks establish installer behavior, not live agent connectivity. Verify fresh Herdr TUI sessions after installation. Desktop was researched only; no desktop-specific integration was added.

## Install and activate

The launcher files are prepared in `~/.config/herdr/agent-launchers/`. The settings changes remain pending until the installer runs: this Codex session cannot write the protected `~/.codex/config.toml` file.

Preview the changes without writing settings:

```sh
python3 ~/.config/herdr/agent-launchers/install.py
```

Apply them from your own terminal:

```sh
python3 ~/.config/herdr/agent-launchers/install.py --apply
```

The installer backs up each affected file under `~/.local/state/herdr-agent-setup/`, then updates:

- `~/.codex/config.toml`: default permissions `:workspace`, approvals `on-request`, reviewer `user`.
- `~/.claude/settings.json`: shell sandbox enabled, with `failIfUnavailable` enabled. Existing permission mode and cache/network exceptions are preserved.
- `~/.zshrc`: inside Herdr only, prepend the launcher directory to PATH.

The original Codex binary and updater-managed Claude symlink are preserved. The installer can be rerun; it avoids duplicate settings and shell blocks. It requires Python 3.11 or newer for TOML validation.

The installer parses complete TOML root assignments, including indented or quoted keys, and checks that only the intended Codex values change. Existing configuration-file symlinks are preserved: writes and automatic rollback update their resolved targets.

## Default commands

After installation, open a fresh Herdr terminal pane, or source `~/.zshrc` in an existing shell. Start from the project directory that should be writable.

Use the ordinary commands:

```sh
codex
claude
```

Inside Herdr, the launchers:

- Read the current pane's `HERDR_SOCKET_PATH` and allow that exact socket, including its canonical path when macOS exposes it through a symlink.
- Launch interactive Codex with `--no-daemon`, so its tools inherit the current pane environment.
- Use a Codex permission profile extending `:workspace`. Enable its network proxy and allow only the Herdr socket; no public network domains are added. Codex's own model/authentication traffic is separate.
- Give Claude an inline settings override enabling its sandbox and allowing the current Herdr socket. Its existing `auto` permission mode remains unchanged.

Socket permissions are set per launch, so they do not become stale when sessions change. They are not global access to every Unix socket or a filesystem write grant to the socket directory.

Outside Herdr, the normal installed commands are used with their sandbox defaults. Administrative Codex commands and remote connections are passed through without injecting `--no-daemon` or a local Herdr socket.

## Agents launching agents

Herdr TUI sends the canonical `codex` or `claude` command into the new pane's interactive shell. New panes therefore find the same launchers automatically:

```sh
herdr agent start worker --kind codex --pane <returned-pane-id>
herdr agent start worker --kind claude --pane <returned-pane-id>
```

Use unique names and the actual IDs returned by Herdr. Model and other native arguments can still be passed after `--`.

Do **not** add the old `--sandbox workspace-write` launch flag. Codex's older sandbox settings override permission profiles and would disable the socket exception. The launcher rejects common legacy flag forms with an explanation. A custom Codex profile containing `sandbox_mode` or `sandbox_workspace_write` is likewise incompatible with this setup; remove those older keys before using it here.

## Verify in fresh sessions

In a Herdr shell, `command -v codex` and `command -v claude` should point into `~/.config/herdr/agent-launchers/bin/`.

Start each agent and check:

1. Codex: `/status` shows the active filesystem/permission settings. Claude: `/sandbox` shows sandboxing enabled.
2. Ask each agent to run `herdr agent list` and inspect its own pane layout. These should work inside its sandbox without requesting a sandbox escape.
3. Repeat the reversed song experiment: Claude creates a sibling pane, launches Codex using the plain `agent start` command, and both exchange song lines.

Startup trust dialogs and actions outside the allowed scope can still require approval. Existing agent sessions keep their launch-time socket overrides; use fresh sessions for this verification. Settings files or explicit CLI flags from a project can override defaults.

The existing saved Codex `herdr agent prompt` approval rule is preserved. Socket access should let ordinary Herdr commands run without relying on that unsandboxed exception.

Claude's sandbox covers shell commands, not all file tools, MCP servers, or hooks. These settings do not make its isolation identical to Codex's.

`failIfUnavailable` makes Claude fail startup when the sandbox is unavailable; it does not disable unsandboxed retries after a command is blocked. The separate `sandbox.allowUnsandboxedCommands` setting defaults to `true` and is preserved by this installer. Approval of those retries depends on the active permission mode and rules. Strict sandboxing would require a separate decision to set it to `false` and review any `excludedCommands` entries; see the [Claude sandbox settings reference](https://code.claude.com/docs/en/settings-reference#sandboxallowunsandboxedcommands).

## Validation performed

The prepared launchers were checked for literal argument forwarding, exact socket policy construction, administrative passthrough, missing-socket failures, and errors for conflicting sandbox flags. Installer candidates were checked to preserve existing settings and to be idempotent. Both launchers successfully forwarded `--version` to the original binaries.

Live sandbox initialization and Herdr socket access must be verified from fresh agents inside Herdr. This setup session runs outside Herdr and cannot perform that check.

## Herdr desktop applicability

Researched November 12, 2026 against the current official desktop and core documentation; not tested in an installed desktop session. [Herdr's FAQ](https://herdr.dev/) describes desktop as a separate program built on `herdr-core`. TUI uses its own server, and the two do not share agents.

Desktop still runs agent CLIs in interactive shells, so the user-level Codex and Claude sandbox defaults can apply when those CLIs use the same home and configuration files. The [desktop agent guide](https://github.com/herdrdev/herdr-app/blob/master/defaults/AGENTS.md) says its built-in Codex launch already includes `--no-daemon` and supports custom executable/argument arrays through `programs.json`.

The TUI launcher activation and socket policy should not be assumed to work in desktop. Desktop reports agent status through terminal OSC 7501 output; ordinary status reporting therefore does not need the TUI socket exception. Agent-driven desktop control through `hc` uses core's separate Unix socket, with `HC_SOCKET` as an override, rather than `HERDR_SOCKET_PATH`. Such control would need a separately reviewed desktop integration; no desktop-specific script changes are included here.

Core itself supplies no agent sandbox. Its [security documentation](https://github.com/herdrdev/herdr-core/blob/master/docs/security.md) states that API clients can execute commands and access files with the core account's permissions. Granting an agent access to that socket therefore grants control beyond its own sandbox; it is not merely a status permission.

## Rollback

The installer prints its backup directory. Its `manifest.json` maps original paths to their backups. Restore those files from your own terminal, then open a fresh shell. The unused launcher directory can remain or be removed afterward.

## Sources

- [Codex permission profiles and Unix sockets](https://learn.chatgpt.com/docs/permissions)
- [Claude sandbox settings](https://code.claude.com/docs/en/settings-reference#sandbox)
- [Claude inline settings](https://code.claude.com/docs/en/cli-reference)
- [Herdr v0.9.5 agent launch implementation](https://github.com/herdrdev/herdr/blob/v0.9.5/src/app/agents.rs)
- [Herdr v0.9.5 canonical executable names](https://github.com/herdrdev/herdr/blob/v0.9.5/src/detect/mod.rs)
