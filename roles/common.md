# Shared working rules

- Follow your assigned role; task ownership stays with the commissioning agent.
- Each delegated assignment states the role, interaction mode (`interactive` or
  `non-interactive`), user-question channel and return channel. Follow that mode;
  do not infer it from the role or profile name. Clarify missing details with the
  caller when needed, while continuing work that does not depend on them.
- Read applicable global and project AGENTS.md instructions.
- Save any docs in a suitable location using YYYY-MM-DD-title.md format.
- Follow the assignment's workflow and approval boundaries. An agreed plan may cover
  implementation, tests and relevant validation. Preserve valid approvals; request
  a new decision for material scope or design changes or an explicit checkpoint.
- In background assignments, return questions requiring user judgment to the caller.
  State assumptions and unresolved decisions; do not invent the user's answers or
  wait for direct user discussion in a non-interactive worker.

## Delegation and reporting

- Use non-interactive bounded background workers (sub-agents) for research to save your context.
- Use the custom `reviewer` subagent role for non-interactive reviews.
- Lead owns interactive launches. Other roles send findings and requests for an
  interactive conversation to Lead.
- Return conclusions, evidence, artifact paths, decisions and open questions to the
  caller.
  - When given a Herdr return address, send the reply with
    `herdr agent prompt <caller> "<summary>"` without `--wait`.
  - Without a return channel, give the user an explicit handoff.
