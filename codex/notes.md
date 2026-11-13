## Codex notes

- Read applicable global and project AGENTS.md instructions.
- Each role has a CLI profile `agentic-<role>` for interactive sessions and a custom
  subagent role `<role>` for non-interactive work: `agentic-scoper` corresponds to
  `scoper`, and non-interactive reviews use `reviewer`.
- Start an interactive specialist through Herdr in an available shell pane:
  `herdr agent start <unique-name> --kind codex --pane <pane-id> -- --profile agentic-<role>`.
