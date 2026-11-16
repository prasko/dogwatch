# Roadmap

Update this page as items land or priorities change.

The workflow is defined in [the role instructions](../roles/), and model tiers in
[model selection](model-selection.md). This page tracks what is next.

## Current state

- Seven roles (Lead, Scoper, Architect, Developer, Tester, Validator, Reviewer) deploy
  to Codex and Claude Code from shared instructions plus per-tool notes.
- Model tiers (`fast`, `standard`, `deep`, `special`) give each role a default model and effort;
  Lead overrides per assignment. Codex subagent files leave the model to the spawning call.
- Reviews are flattened for background stage owners; scope review is optional and Lead's call for
  large tasks. Each tool reviews with its own Reviewer.
- Seven reusable skills cover scope, design, implement, test, validate, research
  and setup feedback. Setup feedback reaches an existing agent in this repository
  through Herdr; repo-local `AGENTS.md` defines receiver behavior.
  Lead chooses direct or delegated execution by task size. Research uses generic
  fast-tier workers; Reviewer always runs separately. Specialist roles embed the
  same maintained procedures with their own ownership boundaries.

## Priorities

### 1. Cross-provider review

Goal: the Reviewer runs on the other tool to bring a different model's view. Deferred from the first
Claude rollout to keep headless review simple.

Open questions:

- Headless (`claude -p`, `codex exec`) versus a Herdr pane. A pane is visible, while the work it
  reviews may be a background subagent, which is inconsistent. Headless runs inside the caller's
  sandbox and needs network access to the other provider and write access to its config home.
- Model and effort for the other tool's Reviewer; reuse the tier map.
- Optional input to implementation reviews: Claude `/code-review` or Codex `/review`. Both cover
  code only, and higher Claude levels start their own subagents.

### 2. Per-repository secretary

A plain session per repository that starts and keeps track of Leads. Not a role yet; try it by hand
first and record what it repeatedly does.

### Later

- Task-splitting skills and cross-worktree orchestration.
- Codex compaction settings and model context sizes.

## Context and compaction (Claude)

All current Claude models have a 1M context window. Claude Code compacts at `autoCompactWindow`
(settings, per model or top level, 100k to 1M or `"auto"`), overridden per session by
`CLAUDE_CODE_AUTO_COMPACT_WINDOW`. `"auto"` is chosen remotely per model.

- Decided: Lead always runs with a 1M window:
  `CLAUDE_CODE_AUTO_COMPACT_WINDOW=1000000 claude --agent agentic-lead`.
- On hold: a per-role window for interactive Scoper, Architect and Developer, applied with
  `herdr tab create --env CLAUDE_CODE_AUTO_COMPACT_WINDOW=<n>`. Revisit if they hit compaction.
- Open: whether the global default should be `"auto"` or an explicit window; check `/autocompact`.
