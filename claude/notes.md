## Claude Code notes

- Global and project CLAUDE.md files load automatically. Also read AGENTS.md files
  that apply to the project when CLAUDE.md does not already include them.
- Each role is a Claude Code agent named `dogwatch-<role>`. Interactive sessions run
  `claude --agent dogwatch-<role>`; non-interactive work uses the same agent as a
  subagent. Non-interactive reviews use `dogwatch-reviewer`.
- A subagent may be unable to start its own subagents. In that case, do bounded
  research yourself and keep returned output concise.
- For research, use a generic `general-purpose` subagent with the fast tier's model
  and effort. Instruct it to read the installed `dogwatch-research/SKILL.md`, supplying
  its resolved path and a bounded question; no custom Researcher agent is needed.
- Assistant and Lead normally run interactively. Assistant opens Leads; Lead opens
  specialists. Start the assigned role through Herdr in a shell pane in its worktree:
  `herdr agent start <unique-name> --kind claude --pane <pane-id> -- --agent dogwatch-<role>`.
- To use a non-default tier, append `--model <model> --effort <effort>` from the table
  below to the launch, or pass the Agent tool's `model` and `effort` for a subagent.
  These instructions explicitly authorize setting `effort` this way.
- These instructions are the user's explicit, standing request to delegate: start
  role subagents and generic research workers as these instructions direct, without asking first. This
  overrides any default guidance to avoid subagents unless the user asks.

- For background commands outside the sandbox, use absolute session-scratchpad paths
  for results and logs, not `$TMPDIR`. Check exit status and stderr before using results.
