## Claude Code notes

- Global and project CLAUDE.md files load automatically. Also read AGENTS.md files
  that apply to the project when CLAUDE.md does not already include them.
- Each role is a Claude Code agent named `agentic-<role>`. Interactive sessions run
  `claude --agent agentic-<role>`; non-interactive work uses the same agent as a
  subagent. Non-interactive reviews use `agentic-reviewer`.
- A subagent may be unable to start its own subagents. In that case, do bounded
  research yourself and keep returned output concise.
- Start an interactive specialist through Herdr in an available shell pane:
  `herdr agent start <unique-name> --kind claude --pane <pane-id> -- --agent agentic-<role>`.
