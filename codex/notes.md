## Codex notes

- Read applicable global and project AGENTS.md instructions.
- Each role has a CLI profile `agentic-<role>` for interactive sessions and a custom
  subagent role `<role>` for non-interactive work: `agentic-scoper` corresponds to
  `scoper`, and non-interactive reviews use `reviewer`.
- Start an interactive specialist through Herdr in an available shell pane:
  `herdr agent start <unique-name> --kind codex --pane <pane-id> -- --profile agentic-<role>`.
- To use a non-default tier, append `-m <model> -c model_reasoning_effort=<effort>`
  from the table below to the launch. For a subagent, set the model and effort when
  spawning it if the spawn call supports that; otherwise use the role's default.
- Never use the `ultra` reasoning level; it delegates on its own.
