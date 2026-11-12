# Agentic setup

Personal agent roles, maintained here and deployed to local coding tools. Codex is
the first target; Claude support can reuse the role instructions later.

## Roles

| Role | Responsibility |
| --- | --- |
| Lead | Own the task, delegate work, retain decisions and approvals, route findings. |
| Scoper | Work with the user on the problem and acceptance criteria; return a reviewed brief. |
| Reviewer | Independently review the assigned artifact against its requirements and stage. |

Role instructions live in `roles/`. `common.md` is included in every role.
Codex-specific descriptions and optional model choices live in `codex/roles.toml`.
No models are pinned by default. Research and task-splitting skills are deferred.
There are no hooks, automatic review gates, or cross-provider CLI calls.

## Install and update

Requires Python 3.11+ and a current Codex CLI. The initial target is Codex 0.167.2.
Run from this repository:

```sh
python3 scripts/deploy.py --dry-run
python3 scripts/deploy.py
python3 scripts/deploy.py --check
```

Deployment generates three named agents in `~/.codex/agents/` and three profiles:
`agentic-lead.config.toml`, `agentic-scoper.config.toml`, and
`agentic-reviewer.config.toml`. `CODEX_HOME` is respected; `--codex-home PATH`
selects an explicit destination. Edit the source files here and redeploy.

Existing files without this repository's generated marker cause deployment to
stop before writing anything. Use `--replace` to replace those exact files after
reviewing the dry run. Every changed existing file is backed up next to itself
with a timestamp. Symlink targets are refused. Unrelated configuration, hooks,
credentials, and project-local agents are untouched. Updates to generated files
belong in this repository; redeployment replaces local edits after backing them up.

## Use

Start a Lead conversation in the project you want to work on:

```sh
codex --profile agentic-lead -C /path/to/project
```

Give it a task and ask it to start with scoping. The first trial is Lead → Scoper
→ Reviewer → Scoper → Lead. It stops at a reviewed brief and unresolved questions;
it does not infer permission to implement. Existing scoped work can skip repeated
scoping. Use `/subagents` in the CLI to inspect and switch agent threads.

Direct conversation inside a spawned Scoper thread still needs a live client
trial. If the client cannot support it, the Lead relays questions explicitly.
For a separate interactive conversation, start
`codex --profile agentic-scoper -C /path/to/project` and supply the assignment and
brief path. That separate session has no automatic return channel: give its saved
brief back to Lead. The Reviewer profile is also available for standalone review.

The Lead can later brief ordinary workers for architecture, development and runtime
validation. Those responsibilities remain separate even without custom definitions.
Implementation requires an approved design. The developer may run existing tests
while focusing on production code; new unit-test authoring starts after independent
code review and initial user approval. Runtime validation exercises real acceptance
scenarios. Initial code approval does not mean the task is finished.

Profiles apply to CLI sessions selected with `--profile`; they do not automatically
turn every app conversation into Lead. Project configuration can override profile
settings. Existing project-local role definitions may affect role discovery; verify
which instructions load when adopting a project with old reviewer configuration.

## Maintain and verify

```sh
python3 -m unittest discover -s tests -v
python3 scripts/deploy.py --dry-run
python3 scripts/deploy.py --check
```

Tests use temporary destinations and cover generated TOML, deployment conflicts,
backups, repeat deployment, and preservation of unrelated configuration. `--check`
reports whether the installed files exactly match the current sources. These checks
do not prove model behavior: try the scoping/review loop on a real brief, inspect the
findings and handoff, and confirm no implementation starts without approval.

To remove the setup, delete only the six generated role/profile files after checking
their markers, and restore any desired backups. Nothing is added to shell startup
files or `config.toml`. The old `Code/agents` examples are not deployment inputs;
old project review hooks, if installed elsewhere, need separate removal.

## Sources

- [Codex custom agents](https://learn.chatgpt.com/docs/agent-configuration/subagents)
- [Codex profiles](https://learn.chatgpt.com/docs/config-file/config-advanced#profiles)
- [Configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)
