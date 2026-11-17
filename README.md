# Agentic setup

Personal agent roles and workflow skills, maintained here and deployed to Codex
and Claude Code from the same instructions.

## Roles

| Role | Responsibility |
| --- | --- |
| Lead | Choose and adapt the workflow, scope and plan or delegate, retain decisions and approvals. |
| Scoper | Investigate scope in the background or discuss requirements with the user; return findings or a brief. |
| Architect | Develop a design interactively or in the background; return reviewed decisions and approval state. |
| Developer | Implement the agreed plan, include tests and validation as assigned, and report reviewed results and design drift. |
| Tester | Plan, author and run separately assigned unit and integration tests within the agreed authorization. |
| Validator | Exercise acceptance scenarios on a throwaway instance and return reviewed evidence. |
| Reviewer | Independently review the assigned artifact against its requirements and stage. |

Role boundaries live in `roles/`; reusable procedures live in `skills/`:

| Skill | Procedure |
| --- | --- |
| `agentic-scope` | Investigate the problem and define requirements and acceptance criteria. |
| `agentic-design` | Develop a concise approach or a substantial design. |
| `agentic-implement` | Implement an agreed change and prepare it for review. |
| `agentic-test` | Author and run meaningful unit and integration tests. |
| `agentic-validate` | Exercise acceptance scenarios and record runtime evidence. |
| `agentic-research` | Answer a bounded factual question with sources and uncertainties. |
| `agentic-setup-feedback` | Relay setup feedback to an agent in this repository through Herdr. |
| `agentic-write-doc` | Write concise, structured documents while preserving task-specific content. |

Lead loads skills as needed. Deployment embeds the same procedure bodies into the
corresponding specialist roles; Developer includes implement, test and validate.
Skills preserve the caller's ownership: Lead can fix production code while testing,
whereas a separate Tester reports the defect to the implementation owner. Research
can run in any role or a generic agent; it has no dedicated role.

`roles/common.md` is included in every role, and
`roles/roles.toml` holds the shared descriptions, including ownership, edit boundaries
and expected output. Deployment also includes these contracts in Lead's instructions.
Each tool directory (`codex/`,
`claude/`) adds `notes.md`, appended to every role for that tool, and `roles.toml`
mapping model tiers (`fast`, `standard`, `deep`, `special`) to concrete models, with
optional per-role overrides. `roles/roles.toml` gives each role a default tier, and Lead
can change the tier per assignment; see
[the model selection doc](docs/model-selection.md). Next steps are in
[the roadmap](docs/roadmap.md). There are no hooks or automatic review gates;
each tool reviews with its own Reviewer.

Interactive stage owners commission their own reviews. Background stage owners return
work ready for review, and Lead commissions the review and routes findings back.

## Install and update

Requires Python 3.11+. Targets Codex 0.167.2 and Claude Code 2.1.322.
Run from this repository:

```sh
python3 scripts/deploy.py --dry-run
python3 scripts/deploy.py
python3 scripts/deploy.py --check
```

Deployment covers both tools by default; `--target codex` or `--target claude`
selects one. For each role above it generates:

- Codex: a named agent in `~/.codex/agents/<role>.toml` and a profile
  `~/.codex/agentic-<role>.config.toml`. `CODEX_HOME` or `--codex-home PATH` changes
  the destination.
- Claude Code: an agent in `~/.claude/agents/agentic-<role>.md`, usable as a subagent
  and with `claude --agent`. `CLAUDE_CONFIG_DIR` or `--claude-home PATH` changes the
  destination. Descriptions tell Claude to use them only when assigned.
- Both: eight skills in `<tool-home>/skills/agentic-<skill>/SKILL.md`. The existing
  home overrides also relocate skills, keeping custom and temporary installs isolated.
  For Codex this uses its supported Codex-home skills directory.

Lead launches interactive agents with the Herdr skill, inside sandboxed agents set up as in
[the Herdr sandbox doc](docs/herdr-sandbox.md). Codex reads it from
`~/.agents/skills/herdr`; link it for Claude with
`ln -s ~/.agents/skills/herdr ~/.claude/skills/herdr`. Edit the source files here and
redeploy.

Existing files without this repository's generated marker cause deployment to
stop before writing anything. Use `--replace` to replace those exact files after
reviewing the dry run. Every changed existing file is backed up next to itself
with a timestamp. Symlink targets are refused. Unrelated configuration, hooks,
credentials, and project-local agents are untouched. Updates to generated files
belong in this repository; redeployment replaces local edits after backing them up.
Updates also retire the old generated Researcher agent/profile files with backups.
Unmanaged files at those retired paths are preserved, including with `--replace`.

## Use

From a Herdr pane, start a Lead conversation in the project you want to work on:

```sh
codex --profile agentic-lead -C /path/to/project
# or, with a 1M compaction window for Lead
cd /path/to/project && CLAUDE_CODE_AUTO_COMPACT_WINDOW=1000000 claude --agent agentic-lead
```

Codex only delegates to subagents when the user or applicable AGENTS.md or skill
instructions ask for it; role instructions alone may not count. Make sure your global
or project AGENTS.md asks for delegation, as the roles describe.

Give Lead a task. It chooses steps and ownership by size, uncertainty and risk.
Small tasks can use the five delivery skills directly in Lead; medium tasks can mix
direct work with specialists; large tasks generally use dedicated specialists.
Direct execution is not the universal default. Lead still delegates bounded research
to generic fast-tier agents using `agentic-research`. Reviewer always runs separately;
small tasks normally get one combined implementation/tests/evidence review.

For unclear work, Lead can first assign a bounded background Scoper investigation.
It brings findings and questions back to you, then continues in Lead or opens an
interactive Scoper. Clearly substantial work needing dedicated discussion can start
there immediately. Lead makes the same choice at later stages based on uncertainty,
risk and discussion needs, carrying findings and decisions across handoffs.

Interactive specialists run as `agentic-<role>` (a Codex profile or Claude agent) in
separate Herdr tabs in the same workspace and project directory, using the same tool
as Lead. Their assignments include Lead's live pane ID
or unique agent name for replies. The same role instructions are available as subagents for
background work: Codex `scoper` corresponds to `agentic-scoper`; Claude uses
`agentic-scoper` for both. Each assignment explicitly states its interaction mode and where to send
user questions; the role name does not determine that. Developer is normally interactive;
non-interactive development is reserved for tiny, well-defined changes. In Codex, use
`/subagents` to inspect background threads.
Codex Reviewer subagents use `reviewer`; separate CLI sessions and Claude use `agentic-reviewer`.
All profiles support standalone sessions with an explicit user handoff when needed.

One agreed plan may authorize implementation, tests and relevant validation. Extra
approval is needed for material scope or design changes or explicitly chosen
checkpoints. The fuller workflow can use separate Architect, Tester and Validator
contexts and code-before-tests approval when useful. A brief alone does
not authorize implementation, and a new agent does not require repeating approval.
See [the Lead role](roles/lead.md) for the workflow.

Profiles and `--agent` apply only to sessions started with them; they do not
automatically turn every app conversation into Lead. Project configuration can override profile
settings.

Codex profiles request an 872k context window and automatic compaction at 400k tokens,
configured per tier in `codex/roles.toml`. The larger ceiling leaves headroom between
compactions; it does not guarantee account/model support for that full window.

Use `agentic-setup-feedback` to message the Herdr agent named `agentic-setup`; receiver guidance lives in [AGENTS.md](AGENTS.md).

## Maintain and verify

```sh
python3 -m unittest discover -s tests -v
python3 scripts/deploy.py --dry-run
python3 scripts/deploy.py --check
```

Tests use temporary destinations and cover generated roles and skills, shared procedure
composition, target selection, conflicts, backups, repeat deployment, Researcher
retirement and preservation of unrelated configuration. `--check`
reports whether the installed files exactly match the current sources.

To remove the setup, delete only the generated files (twenty-two for Codex, fifteen for
Claude, including eight skills each) after checking their markers, and restore any desired backups. Nothing is
added to shell startup files, `config.toml` or `settings.json`.

## Sources

- [Codex custom agents](https://learn.chatgpt.com/docs/agent-configuration/subagents)
- [Codex profiles](https://learn.chatgpt.com/docs/config-file/config-advanced#profiles)
- [Configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)
- [Claude Code subagents](https://code.claude.com/docs/en/sub-agents)
- [Codex skill authoring and home-directory installation](https://developers.openai.com/cookbook/examples/codex/iterating-development-workflows-with-codex)
- [Claude Code skills](https://code.claude.com/docs/en/skills)
