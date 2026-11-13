# Sandboxed agents in Herdr

Agents launch other agents through Herdr. They control Herdr through its Unix socket, so each
sandboxed agent needs access to that socket and nothing more. The launchers and installer live
outside this repository, in `~/.config/herdr/agent-launchers/`.

## Install

```sh
python3 ~/.config/herdr/agent-launchers/install.py          # preview
python3 ~/.config/herdr/agent-launchers/install.py --apply  # run from your own terminal
```

It backs up affected files under `~/.local/state/herdr-agent-setup/` (see `manifest.json` there for
rollback) and changes:

- `~/.codex/config.toml`: default permissions `:workspace`, approvals `on-request`.
- `~/.claude/settings.json`: shell sandbox on, with `failIfUnavailable`.
- `~/.zshrc`: inside Herdr only, puts the launcher directory first on `PATH`.

## How it works

Inside Herdr, plain `codex` and `claude` resolve to the launchers. Each launch allows only the current
pane's `HERDR_SOCKET_PATH`:

- Codex runs with `--no-daemon` and a permission profile extending `:workspace` that allows the socket.
- Claude gets an inline settings override that enables its sandbox and allows the socket.

Outside Herdr, the normal commands run with their usual defaults. Herdr starts new agents by typing
`codex` or `claude` into the new pane's shell, so they get the same launchers:

```sh
herdr agent start <name> --kind codex --pane <pane-id> -- <native args>
```

Do not use `--sandbox workspace-write` or Codex profiles with `sandbox_mode`/`sandbox_workspace_write`:
these older settings override permission profiles and drop the socket exception.

## Limits

- Claude's sandbox covers shell commands only, not file tools, MCP servers or hooks.
  `sandbox.allowUnsandboxedCommands` stays at its default (`true`).
- The launchers target Herdr TUI. Herdr desktop uses a different socket and is not covered.
- Socket access lets an agent run Herdr commands, which can reach beyond its own sandbox.

## Check

In a fresh Herdr pane, `command -v codex claude` points into the launcher `bin/`. Codex `/status` and
Claude `/sandbox` show the sandbox, and `herdr agent list` works without a sandbox escape.

## Sources

- [Codex permission profiles and Unix sockets](https://learn.chatgpt.com/docs/permissions)
- [Claude sandbox settings](https://code.claude.com/docs/en/settings-reference#sandbox)
- [Herdr v0.9.5 agent launch](https://github.com/herdrdev/herdr/blob/v0.9.5/src/app/agents.rs)
