# Agentic setup

Personal agent roles, maintained here and deployed to local coding tools. Codex is
the first target; Claude support can reuse the role instructions later.

## Roles

| Role | Responsibility |
| --- | --- |
| Lead | Choose and adapt the workflow, scope and plan or delegate, retain decisions and approvals. |
| Scoper | Investigate scope in the background or discuss requirements with the user; return findings or a reviewed brief. |
| Architect | Develop a design interactively or in the background; return reviewed decisions and approval state. |
| Developer | Implement the agreed plan, include tests and validation as assigned, and report reviewed results and design drift. |
| Tester | Plan, author and run separately assigned unit and integration tests within the agreed authorization. |
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

Give Lead a task. It selects which steps run and which agents are interactive. Small
tasks can use a background Scoper, planning in Lead and an interactive Developer
handling implementation and tests. Medium tasks may add an interactive Architect
and separate background testing or validation. Large tasks can use interactive
specialists throughout. Reviews and documentation work run in the background.

For unclear work, Lead can first assign a bounded background Scoper investigation.
It brings findings and questions back to you, then continues in Lead or opens an
interactive Scoper. Clearly substantial work needing dedicated discussion can start
there immediately. Lead makes the same choice at later stages based on uncertainty,
risk and discussion needs, carrying findings and decisions across handoffs.

Interactive specialists use `agentic-<role>` profiles in separate Herdr tabs in the
same workspace and project directory. Their assignments include Lead's live pane ID
or unique agent name for replies. The same role instructions are available as custom
subagent roles for background work: `scoper` corresponds to `agentic-scoper`, for
example. Each assignment explicitly states its interaction mode and where to send
user questions; the role name does not determine that. Developer is normally interactive;
non-interactive development is reserved for tiny, well-defined changes. Use
`/subagents` to inspect background threads.
Custom Reviewer subagents use `reviewer`; separate CLI sessions use `agentic-reviewer`.
All profiles support standalone sessions with an explicit user handoff when needed.

One agreed plan may authorize implementation, tests and relevant validation. Extra
approval is needed for material scope or design changes or explicitly chosen
checkpoints. The fuller workflow can use separate Architect, Tester and Validator
contexts and code-before-tests approval when useful. A reviewed brief alone does
not authorize implementation, and a new agent does not require repeating approval.
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
do not prove model behavior: try small, medium and large task flows, including
background scoping that leads to an interactive handoff. Verify Developer normally
opens interactively, findings and questions reach Lead, approvals carry forward,
and implementation stays within the agreed plan and checkpoints.

To remove the setup, delete only the fourteen generated role/profile files after checking
their markers, and restore any desired backups. Nothing is added to shell startup
files or `config.toml`. The old `Code/agents` examples are not deployment inputs;
old project review hooks, if installed elsewhere, need separate removal.

## Sources

- [Codex custom agents](https://learn.chatgpt.com/docs/agent-configuration/subagents)
- [Codex profiles](https://learn.chatgpt.com/docs/config-file/config-advanced#profiles)
- [Configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)
