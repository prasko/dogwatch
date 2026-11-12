# Shared working rules

- Follow your assigned role; task ownership stays with the commissioning agent.
- Read applicable global and project AGENTS.md instructions.
- Save any docs in a suitable location using YYYY-MM-DD-title.md format.

## Spawning agents

- Use non-interactive bounded background workers (sub-agents) for research to save your context.
- Use the Herdr skill to spawn interactive agents with dedicated roles.
  - Pass your live tab/pane ID and unique agent name.
  - Require replies via `herdr agent prompt <caller> "<summary>"` without `--wait`.
  - Start them in a separate named tab in the assigned workspace and project directory.
  - Track tab/pane IDs returned by Herdr.
- Use the native `reviewer` role for non-interactive reviews. `agentic-reviewer` is
  the CLI profile for standalone review sessions.
- Return conclusions, evidence, artifact paths, decisions and open questions to the
  caller.
  - Without a return channel, give the user an explicit handoff.
