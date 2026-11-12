# Agentic setup

Personal agent roles, maintained here and deployed to local coding tools. Codex is
the first target; Claude support can reuse the role instructions later.

## Roles

| Role | Responsibility |
| --- | --- |
| Lead | Own the task, delegate work, retain decisions and approvals, route findings. |
| Scoper | Work with the user on the problem and acceptance criteria; return a reviewed brief. |
| Architect | Develop the design with the user; return an independently reviewed, approved design. |
| Developer | Implement the approved design, run existing checks, and report reviewed changes and design drift. |
| Tester | Propose unit and integration tests; author, run and review them after plan approval. |
| Validator | Exercise acceptance scenarios on a throwaway instance and return reviewed evidence. |
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

Deployment generates seven named agents in `~/.codex/agents/` and seven profiles
named `agentic-<role>.config.toml`, one for each role above. `CODEX_HOME` is respected;
`--codex-home PATH` selects an explicit destination. Edit the source files here and
redeploy.

Existing files without this repository's generated marker cause deployment to
stop before writing anything. Use `--replace` to replace those exact files after
reviewing the dry run. Every changed existing file is backed up next to itself
with a timestamp. Symlink targets are refused. Unrelated configuration, hooks,
credentials, and project-local agents are untouched. Updates to generated files
belong in this repository; redeployment replaces local edits after backing them up.

## Use

From a Herdr pane, start a Lead conversation in the project you want to work on:

```sh
codex --profile agentic-lead -C /path/to/project
```

Give it a task and ask it to start with scoping. Lead opens Scoper in a separate
Herdr tab using the Scoper profile, in the same workspace and project directory.
Discuss scope directly there. The assignment includes Lead's live pane ID or unique
agent name so Scoper can message its reviewed brief and decisions back to Lead.
A reviewed brief does not authorize implementation; existing scoped work can skip
repeated scoping.

Lead opens interactive stage owners in separate Herdr tabs using their
`agentic-<role>` profiles. Research, reviews and documentation updates use native
non-interactive subagents. Use `/subagents` to inspect those threads; use Herdr tabs
for direct user conversations. Native reviews use the `reviewer` role; standalone
review sessions use the `agentic-reviewer` profile. All role profiles also support
standalone sessions, with an explicit user handoff when no caller address is available.

The Lead follows scoping, architecting, developing, unit and integration testing,
validating and documenting. It tracks approvals and keeps docs current. Developer
may run existing checks; Tester authors new unit and integration tests after
initial code approval and user approval of the proposed test plan.
See [the Lead role](roles/lead.md) for the workflow.

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
do not prove model behavior: try direct scoping in its Herdr tab, verify the return
message reaches Lead, and confirm no implementation starts without approval.

To remove the setup, delete only the fourteen generated role/profile files after checking
their markers, and restore any desired backups. Nothing is added to shell startup
files or `config.toml`. The old `Code/agents` examples are not deployment inputs;
old project review hooks, if installed elsewhere, need separate removal.

## Sources

- [Codex custom agents](https://learn.chatgpt.com/docs/agent-configuration/subagents)
- [Codex profiles](https://learn.chatgpt.com/docs/config-file/config-advanced#profiles)
- [Configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)
