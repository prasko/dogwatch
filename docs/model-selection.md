# Model and reasoning-level selection

## Objective

Run each role, and each kind of delegated work, on a model and reasoning level suited to it.
Judgment-heavy roles get the strongest models; routine execution gets a capable workhorse; search
and summarizing gets a fast model. Defaults come from configuration, so normal work needs no per-task
choice, but Lead can raise or lower the tier for a specific assignment.

## What the tools support

Checked against Claude Code 2.1.322 and Codex 0.167.2.

| | Claude Code | Codex |
| --- | --- | --- |
| Role default | Agent frontmatter `model` (alias such as `opus`, `sonnet`, `haiku`, `fable`, or a full ID) and `effort` | Custom agent and profile `model`, `model_reasoning_effort` |
| Interactive session override | `claude --agent agentic-<role> --model <m> --effort <level>` | `codex --profile agentic-<role> -m <m> -c model_reasoning_effort=<level>` |
| Per-subagent override | Agent tool `model` and `effort` parameters; `effort` only when instructions explicitly ask | Spawn `model` and `reasoning_effort`, only with `fork_turns="none"`; custom-agent settings take precedence over them |
| Effort levels | low, medium, high, xhigh, max | low, medium, high, xhigh, max, ultra (ultra adds automatic delegation) |

Available models of interest:

- Claude: Opus 5.5, Sonnet 5.5, Haiku 5.5, Fable 5.2.
- Codex: `gpt-6-astra` (frontier), `gpt-6.1-sol` (workhorse), `gpt-6.1-terra`, `gpt-6-luna` (fast,
  for easier tasks).

## Overview

Introduce four **tiers** that describe the kind of thinking needed, independent of the tool:

| Tier | Use | Claude Code | Codex |
| --- | --- | --- | --- |
| `fast` | Locate and summarize; no conclusions | Haiku 5.5, low | `gpt-6-luna`, medium |
| `standard` | Execute an agreed plan; routine judgment | Sonnet 5.5, high | `gpt-6.1-sol`, high |
| `deep` | Coordination, requirements, design, review | Opus 5.5, medium | `gpt-6-astra`, high |
| `special` | Exceptional difficulty; user-approved | Fable 5.2, medium | `gpt-6-astra`, xhigh |

Each role gets a default tier in shared configuration. Each tool maps tiers to a concrete model and
effort. The generated tool notes list that mapping, so Lead can override an assignment by tier
without knowing model names. A model change then means editing one table per tool.

## Detailed design

### Role defaults

| Role | Tier | Reasoning |
| --- | --- | --- |
| Lead | `deep` | Chooses the workflow, keeps decisions and approvals, reconciles results. Mistakes here spread. |
| Scoper | `deep` | Separates requirements from solutions and finds what is missing. |
| Architect | `deep` | Tradeoffs, interfaces and failure modes. |
| Developer | `standard` | Works from an agreed plan; review catches what it misses. |
| Tester | `standard` | Test design from given requirements and risks. |
| Validator | `standard` | Runs scenarios and records evidence. |
| Reviewer | `standard` | Lead chooses `standard` or `deep` per review; see below. |
| Generic research worker | `fast` | Use the research skill for bounded factual questions. |

The interactive and background versions of a role share a default. An interactive Developer still
starts on `standard`; the user can override it at launch or ask Lead to.

### Review tier and frequency

Lead decides the review tier and how much review a task gets, and states the tier in each assignment
that commissions or requires a review:

- Large tasks with substantial design: `deep` review, starting early with the architecture or
  design rather than the scope. Scope review stays optional, as described in the Lead role.
- Smaller tasks: fewer reviews overall, typically one `standard` review of the combined
  implementation and tests; `deep` only where the risk justifies it.

The configured default is `standard`, so an assignment without a tier gets the cheaper review.

### Research skill and generic workers

`agentic-research` supplies the factual research procedure without a dedicated role.
Lead and specialists normally delegate bounded questions to generic fast-tier agents,
including when Lead performs all delivery stages itself. The caller supplies the
question, source locations, skill path and return channel, and interprets the findings.

Use Codex's `default` agent or Claude's `general-purpose` agent with the configured
fast model and effort. Research stays read-only and returns pointers, evidence,
uncertainties and a concise factual summary. A caller can use the same skill directly
when delegation is unavailable. Loading a skill does not change the current model.

### Per-assignment overrides

Lead states the tier in each assignment when it differs from the default, and uses the tool-specific
override when launching. Guidance for Lead:

- **Raise to `deep`**: debugging with an unclear cause, security-sensitive or concurrency-heavy
  changes, work that failed review twice, or a cross-cutting change in an unfamiliar area.
- **Lower to `standard` or `fast`**: documentation updates, mechanical edits, running checks and
  collecting results. Doc-update subagents default to `standard`.
- **`special`** only when the user asks, or when Lead proposes it with a reason and the user agrees.
- Never use Codex `ultra`; it delegates on its own and bypasses the workflow's delegation rules.
- Record a non-default tier and the reason in the assignment, so drift stays visible.

Other roles do not override tiers, except for choosing `fast` for their own generic
research workers.

### Configuration and generation

- `roles/roles.toml` defines the seven roles and their default tiers. The fast tier
  remains available for generic research workers without a Researcher role entry.
- `codex/roles.toml` and `claude/roles.toml` gain a `[tiers.<name>]` table with `model` and
  `model_reasoning_effort` (Codex) or `effort` (Claude). Per-role tables stay, for exceptions that
  bypass the tier.
- The deploy script resolves each role's tier into concrete settings: the Claude frontmatter
  `model`/`effort` and the Codex profile `model`/`model_reasoning_effort`. Codex custom-agent
  files set no model, because their settings would override spawn-time values; callers always pass
  the role's default (or the assignment's tier) model and effort when spawning. A subagent spawned
  without them gets the configured default subagent model, if any, otherwise the caller's model.
- The generated tool notes include the tier table, each role's resolved defaults (including per-role
  overrides) and override syntax.
- Validation: unknown tiers, unknown roles and unsupported effort values fail generation.

Codex tiers also set `model_context_window = 872000` and
`model_auto_compact_token_limit = 400000`, with optional per-role overrides.
These are emitted into interactive profiles, not custom-agent files. Context-setting
inheritance to spawned subagents has not been verified. The 872k ceiling comes from
the local model catalog; acceptance at that size still depends on the service.

Example `claude/roles.toml`:

```toml
[tiers.fast]
model = "haiku"
effort = "low"

[tiers.standard]
model = "sonnet"
effort = "high"

[tiers.deep]
model = "opus"
effort = "medium"

[tiers.special]
model = "fable"
effort = "medium"
```

Aliases follow the latest model of each family automatically; full IDs pin a version. Prefer aliases
for Claude. Codex has no aliases, so model updates there are explicit edits.

## Decisions and open questions

1. `standard` uses Sonnet 5.5 at high effort.
2. Haiku 5.5 is tried for `fast`, with simple, narrow research questions only. Fallback is
   Sonnet 5.5 at low.
3. Lead chooses the review tier and frequency per task, as described above.
4. Codex subagent override: the spawn call accepts model and
   effort with `fork_turns="none"`, but pinned custom-agent settings win. Codex subagent files
   therefore leave the model to the caller.

## Sources

- [Claude Code subagents](https://code.claude.com/docs/en/sub-agents)
- [Claude Code CLI reference](https://code.claude.com/docs/en/cli-reference)
- [Codex custom agents](https://learn.chatgpt.com/docs/agent-configuration/subagents)
- [Codex configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)
