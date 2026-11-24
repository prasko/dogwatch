# Dogwatch

A coordinated coding workflow for Codex and Claude Code in **Herdr TUI**. Open
Assistant in your primary checkout to launch Leads in task worktrees. Each Lead
works directly or brings in specialists for scope, design, development, testing,
validation and independent review. This repository supplies the roles, workflow
skills and sandboxed launchers. Reviewr gives you a diff pane for feedback.

## Mac setup

Use either Codex or Claude Code, or both. You need a terminal with truecolor
(we recommend [Ghostty](https://ghostty.org)), zsh, Git, Python 3.11+ and Node/npm
(for `npx`). With [Homebrew](https://brew.sh):

```sh
brew install git python node herdr
```

[Herdr also has a direct installer](https://herdr.dev/tui/docs/install/).
Install and sign in to [Codex CLI](https://learn.chatgpt.com/docs/codex/cli) or
[Claude Code](https://code.claude.com/docs/en/setup), using your own supported
account or API credentials. Run each selected CLI once before installing its
integration. Download or clone this repository and run its Python commands from
the checkout directory.

The commands below install both providers. For one provider, omit its unused
integration command and skill agent name, and add `--target codex` or
`--target claude` to both Python scripts. The skill CLI calls Claude `claude-code`.

### 1. Install Reviewr, integrations and the Herdr skill

```sh
herdr plugin install persiyanov/herdr-reviewr
herdr integration install codex
herdr integration install claude
npx skills add herdrdev/herdr --skill herdr -g -a codex claude-code
```

The [integrations](https://herdr.dev/tui/docs/integrations/) report native session
identity to Herdr; the [skill](https://github.com/herdrdev/herdr) teaches agents
to control it. Review any hook trust prompt in your agent when starting a new session.

Add this binding to `~/.config/herdr/config.toml` to toggle
[Reviewr](https://github.com/persiyanov/herdr-reviewr) with prefix, then Ctrl+R.
Merge with existing sections rather than duplicating them. The `[keys]` prefix
change is optional; omit it to keep Herdr's default.

```toml
[keys]
prefix = "ctrl+s"

[[keys.command]]
key = "prefix+ctrl+r"
type = "plugin_action"
command = "persiyanov.reviewr.toggle"
```

Choose **Reload config** in Herdr's menu if it is already running.

### 2. Install the launchers

```sh
python3 scripts/install_launchers.py --dry-run
python3 scripts/install_launchers.py
```

This copies launchers to `~/.config/dogwatch/launchers/` and adds a marked block
to `~/.zshrc`. In a fresh Herdr pane, plain `codex` and `claude` use these launchers;
outside Herdr, your normal commands keep working. Real binaries are found on PATH,
so Homebrew, native and npm installations need no hardcoded paths. Shell aliases
or functions named `codex` or `claude` take precedence; remove those conflicts.

Each launch allows the current `HERDR_SOCKET_PATH`. Codex uses the `dogwatch` permission
profile extending `:workspace` and runs interactive sessions with `--no-daemon`;
Claude gets a shell-sandbox settings override. **Socket access lets agents control
other Herdr panes and run commands beyond their own sandbox.** Claude's sandbox
covers shell commands; its normal unsandboxed-retry policy remains in effect.
Keep Claude custom settings in `settings.json`: an extra `--settings` argument
is refused because it would replace the socket override.

The installer leaves agent configuration and approval preferences intact. It honors
`XDG_CONFIG_HOME`, `XDG_STATE_HOME` and `ZDOTDIR`; `--launcher-home`, `--state-home`
and `--shell-rc` override those destinations. Changed files have private backups and
a manifest under `~/.local/state/dogwatch/`. Unmanaged launcher files stop
installation: inspect them before using `--replace`. This also applies when migrating
an earlier hand-installed launcher: use its original `--launcher-home` with
`--replace` to adopt it in place. The installer migrates marked launchers from
the old `~/.config/herdr/agent-launchers/` directory as each provider is selected.
For a custom launcher directory, pass the original `--launcher-home` to update it
in place. Old backups stay at their original locations.

### 3. Deploy the roles

```sh
python3 scripts/deploy.py --dry-run
python3 scripts/deploy.py
python3 scripts/deploy.py --check
```

Deployment creates Codex agents in `~/.codex/agents/dogwatch-<role>.toml` and
interactive profiles in `~/.codex/dogwatch-<role>.config.toml`; Claude agents go in
`~/.claude/agents/dogwatch-<role>.md`. Both receive the `dogwatch-` workflow skills
in their tool home's `skills/` directory.
`CODEX_HOME` / `--codex-home PATH` and `CLAUDE_CONFIG_DIR` / `--claude-home PATH`
change these homes. Export custom homes in your shell so new Herdr panes use them too.

Existing files without this repository's generated marker stop deployment; inspect
the dry run before using `--replace`. Changed or removed files receive private backups
under `~/.local/state/dogwatch/`, with one timestamped directory and a `manifest.json`
recording original paths and modes per operation. `XDG_STATE_HOME` or `--state-home`
changes this location. Unrelated configuration and project agents are preserved;
generated paths refuse symlinks. Make role/skill edits here and redeploy, since updates replace
local edits. Deployment migrates marked `agentic-` files and Codex's old unprefixed
roles to the Dogwatch names, with backups. Retired Researcher files are also removed.
Unmarked files at old paths are preserved.

## Use

Start `herdr`, open your primary checkout, and start Assistant in a fresh pane:

```sh
codex --profile dogwatch-assistant -C /path/to/repo
# Or Claude:
cd /path/to/repo && claude --agent dogwatch-assistant
```

- Give Assistant an issue or task, such as “Open a Lead for issue #123.” It creates
  or reuses the task's worktree and opens Lead there.
- Discuss the task directly with Lead; Assistant tracks its status and worktree.
- For GitHub issue/PR input, install the [GitHub CLI](https://cli.github.com/)
  (`brew install gh`) and sign in with `gh auth login`.
- Lead manages its specialists; Assistant finishes removing the task workspace.

You can also start Lead directly in an existing project or worktree:

```sh
codex --profile dogwatch-lead -C /path/to/project
# Or Claude, with a 1M compaction window for Lead:
cd /path/to/project && CLAUDE_CODE_AUTO_COMPACT_WINDOW=1000000 claude --agent dogwatch-lead
```

- Give Lead a task, for example: “Scope why this test fails yourself, propose a fix,
  then implement it after we agree.” It follows the [default user checkpoints](#default-user-checkpoints)
  and delegates bounded work.
- Interactive specialists use separate Herdr tabs; background specialists run as
  subagents. Reviewer works independently.
- Your user/project `AGENTS.md` and `CLAUDE.md` also govern the agents. For Codex, ask
  for delegation in your task or applicable `AGENTS.md`/skill instructions; role
  instructions alone may not enable it. The roles contain the delegation details.
- Profiles and `--agent` apply to sessions started with them, including standalone
  specialists; they do not turn every conversation into Lead.

| Role | Responsibility |
| --- | --- |
| Assistant | Open and track Leads in task worktrees; coordinate cleanup after merge. |
| Lead | Choose the workflow, retain decisions and coordinate handoffs. |
| Scoper | Investigate the problem and clarify requirements. |
| Architect | Develop the approach, prepare an agreed design-stage sketch, and obtain design review. |
| Developer | Implement the agreed change and assigned checks. |
| Tester | Author and run separately assigned tests. |
| Validator | Exercise acceptance scenarios on a throwaway instance. |
| Reviewer | Independently assess the assigned artifact. |

Codex background roles, interactive profiles and Claude agents all use names such
as `dogwatch-reviewer`. See [Assistant](roles/assistant.md) and [Lead](roles/lead.md)
for their workflows.

### Project configuration and periodic checks

Project settings live in [dogwatch.toml](dogwatch.toml) at the repository root.
Every role uses the optional top-level `todo_file` when working with the backlog;
its path is relative to that root. This repository uses [docs/todo.md](docs/todo.md).
Other projects can provide their own `dogwatch.toml`; omit `todo_file` to keep their
existing conventions. The configuration is read from each checkout, so commit it
if task worktrees should inherit it.

The optional `[assistant.watch]` table enables periodic checks while an interactive
Assistant is open. `pull_requests`, `issues` and `scan_todo` each default to `false`;
`interval_minutes` defaults to 30 and must be a positive integer. `scan_todo` requires
`todo_file`. Without enabled sources, nothing is scheduled. GitHub checks require
an established GitHub remote and authenticated `gh`.

Assistant reports new actionable PR/issue information and asks a fast research
subagent for up to three small todo candidates. It skips unchanged scans and avoids
repeating findings. These are suggestions; selecting a task still goes through the
normal Lead workflow.

- **Codex:** reinstall the launchers after updating this checkout, then start with
  `--profile dogwatch-assistant` in Herdr. Start a fresh session in the intended
  checkout: `resume`, `fork` and `--worktree` launches do not start timers because
  Codex may choose a different checkout. A timer child of that CLI sends checks
  while Herdr reports it idle or done. It stops when the CLI exits, the session
  identity changes, or all sources are disabled. Busy ticks are skipped. Herdr's
  status check and prompt submission are separate operations, so a user turn can
  start between them; uncertain deliveries are not retried. Removing or invalidating
  the configuration stops the timer; restart Assistant after fixing or re-enabling it.
- **Claude:** on its first turn, Assistant uses native session-scoped scheduling
  tools and reconciles existing timers on resume. Checks wait for an idle session;
  nothing executes while it is closed. Pending timers may be restored on resume.
  `CLAUDE_CODE_DISABLE_CRON=1` makes scheduling unavailable. See the
  [scheduled-task lifecycle](https://code.claude.com/docs/en/scheduled-tasks#limitations).

Cadence is approximate. Assistant keeps its last-seen state in the session, including
compaction handoffs. A new session establishes a new baseline. Asking to pause skips
checks; on Codex, the launcher may still send timer prompts until all sources are
disabled or the session exits.

## Default user checkpoints

This example follows a typical medium-sized change delivered in one PR, such as
adding an endpoint that stores a new model. A code skeleton is a diff showing
the proposed models, key classes and functions, and how they fit together before
their behavior is filled in.

| Stage | Checkpoint | Your part |
| --- | --- | --- |
| Task kickoff | Choose who scopes the change | Choose Lead or a dedicated Scoper. |
| End of the design interview | Decide whether to prepare a skeleton and who will build it | Confirm the design owner's recommendation. In this example, Developer will prepare it. |
| When the design is ready | Approve the design | Review the requirements and proposed approach. |
| Start of implementation | Approve the skeleton | Review Developer's first diff before they fill in the behavior. |
| After independent review and fixes | Review the implementation | Review the finished change and any remaining findings. |

A quick skeleton can be part of the design review when seeing the code would
help you judge a single-PR change. Review a fuller skeleton at the start of
implementation, as in the example. For a multi-PR change, review each PR's
skeleton during implementation. Developer prepares it when work on that PR starts.

Once a task is complete and its PR merge is verified, Lead coordinates cleanup of
task-owned agents and worktrees by default, retaining anything still needed.
Lead or other agents may ask for additional decisions or permissions along the way
when something is unclear.

See [task sizes](roles/lead.md#task-sizes), the [Design](skills/dogwatch-design/SKILL.md),
[Prepare skeleton](skills/dogwatch-prepare-skeleton/SKILL.md)
and [Implement](skills/dogwatch-implement/SKILL.md) procedures, and the
[cleanup rules](roles/common.md#task-cleanup) for details.

## Preferences and compatibility

- **Approvals:** choose your own policy. In Codex's `config.toml`, root settings
  `approval_policy = "on-request"` and `approvals_reviewer = "auto_review"` enable
  “Approve for me”; use `"user"` for manual review. These
  [settings](https://learn.chatgpt.com/docs/config-file/config-reference) preserve
  the launcher's sandbox profile. Avoid the `--approve-for-me` shortcut, `--sandbox`
  and legacy `sandbox_mode` / `sandbox_workspace_write` settings in user, profile
  or project configuration: they override the socket exception. For Claude, choose
  `--permission-mode manual` or `--permission-mode auto`, or set
  `permissions.defaultMode` in [settings.json](https://code.claude.com/docs/en/settings-reference).
- **Models:** edit tiers in [codex/roles.toml](codex/roles.toml) or
  [claude/roles.toml](claude/roles.toml) and redeploy. Select models your account
  supports.
- **Codex context limits:** profiles compact at 250k tokens without overriding the
  context window. Adjust `model_auto_compact_token_limit` in
  [codex/roles.toml](codex/roles.toml) and redeploy, keeping the threshold below the
  [selected model's context window](https://learn.chatgpt.com/docs/models?surface=cli).
  Remove the compaction override to use each model's default compaction behavior.
- **Claude compaction:** the Claude Lead launch above requests 1M. For Sonnet
  sessions, `/autocompact 400000` saves a per-model preference
  under `modelSettings` in `settings.json`. See [Claude's settings reference](https://code.claude.com/docs/en/settings-reference#modelsettings).
- **Compatibility:** the launcher interfaces target Herdr TUI 0.9.5, Codex 0.169.0
  and Claude Code 2.1.326 on macOS. Project and managed settings can affect the
  result. Herdr desktop is outside this setup's scope.

In a fresh Herdr pane, `command -v codex` or `command -v claude` should point into
the launcher `bin/`. Check `herdr integration status`, Codex `/status` or Claude
`/sandbox`, then ask Lead to run `herdr agent list` and start a specialist that
replies through Herdr. This checks the installed workflow, including socket access.

## Update and remove

To move older adjacent role/skill backups into the central backup directory, preview
`python3 scripts/deploy.py --migrate-backups --dry-run`, then repeat without `--dry-run`.
This moves only marked backups at known package paths; it does not redeploy roles or
skills. Unmarked backups are left for manual review. The manifest also records each
backup's `restore_to` path; restore files manually if needed.

After updating this checkout, rerun launcher preview/apply and role deployment.
Update provider CLIs through their installation method. Use `brew upgrade herdr`
for Homebrew Herdr, or `herdr update` for a direct install. Re-run the integration
install commands and the `npx skills add` command to refresh them. Update Reviewr
by running `herdr plugin uninstall persiyanov.reviewr`, then its install command.

To remove launchers, preview `python3 scripts/install_launchers.py --uninstall --dry-run`,
then repeat without `--dry-run`. `--target` removes just one provider; the shared launcher
and PATH block remain until the last provider is removed. Open a fresh pane afterward.
Backups are retained; their `manifest.json` records original paths and modes for
manual restoration. Empty directories and unrelated files are left alone.

To remove roles and workflow skills, preview
`python3 scripts/deploy.py --uninstall --dry-run`, then repeat without `--dry-run`.
Both scripts accept `--target codex`, `--target claude` or `--target all` (the default).

`deploy.py` also accepts `--component roles`, `--component skills` or
`--component all` (the default) with `--uninstall`. For example,
preview removing Codex roles while keeping its skills:

```sh
python3 scripts/deploy.py --uninstall --target codex --component roles --dry-run
```

Roles include their interactive profiles. Skills can be used independently;
removing skills while keeping roles produces a dependency warning. Removal backs
up and deletes only marked files, including the old names, and keeps personal
agents, configuration and backups. Restore any desired backups manually. Installation
and updates keep roles and skills together so their names and references stay in sync.
If both providers share a home directory, changing shared skills requires `--target all`.

To remove the external pieces too, use
`herdr integration uninstall codex` / `claude`,
`npx skills remove herdr -g -a codex claude-code`, and
`herdr plugin uninstall persiyanov.reviewr`. Remove the Reviewr binding and any
prefix customization you added; uninstall Herdr through its original installation
method if no longer needed. Keep provider credentials and other configuration.

## Repository and checks

Shared role contracts live in `roles/`; reusable procedures live in `skills/`.
Lead loads skills as needed, while deployment embeds their bodies into specialist
roles. `roles/common.md` applies to every role; each tool's `notes.md` and
`roles.toml` add tool-specific behavior and model tiers. Each tool's `assistant.md`
adds timer instructions only to Assistant. There are no automatic
workflow review gates; agents commission reviews according to their roles.
`dogwatch-setup-feedback` can send feedback to a Herdr agent named `agentic-setup`;
receiver instructions live in [AGENTS.md](AGENTS.md).

```sh
python3 -m unittest discover -s tests -v
python3 scripts/deploy.py --dry-run
python3 scripts/deploy.py --check
```

Tests use temporary homes and stub CLIs to cover role generation, launcher execution,
provider/component selection, name migration, configuration preservation, backups,
repeat installation and removal. `deploy.py --check` compares installed roles and
skills with repository sources. A full signed-in workflow on a clean Mac account
still needs validation.
