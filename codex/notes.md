## Codex notes

- Read applicable global and project AGENTS.md instructions.
- Each role has a CLI profile `dogwatch-<role>` for interactive sessions and a custom
  subagent role with the same name for non-interactive work. For example, use
  `dogwatch-scoper` for scoping and `dogwatch-reviewer` for independent reviews.
- Assistant and Lead normally run interactively. Assistant opens Leads; Lead opens
  specialists. Start the assigned role through Herdr in a shell pane in its worktree:
  `herdr agent start <unique-name> --kind codex --pane <pane-id> -- --profile dogwatch-<role>`.
- Interactive profiles start on their role's default tier. To use another tier,
  append `-m <model> -c model_reasoning_effort=<effort>` from the table below.
- Subagent role files set no model, so always pass `model` and `reasoning_effort`
  when spawning one, with `fork_turns="none"`: the role's defaults from the role table
  below, or the tier stated in the assignment. Overrides require a fresh context, so
  make the assignment self-contained. A subagent spawned without them gets the
  configured default subagent model, if any, otherwise your model.
- Never use the `ultra` reasoning level; it delegates on its own.
- For research, use a generic `default` subagent with the fast tier's model and
  effort and `fork_turns="none"`. Instruct it to read the installed
  `dogwatch-research/SKILL.md`, supplying its resolved path and a bounded question.
