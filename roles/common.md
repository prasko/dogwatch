# Shared working rules

- Follow your assigned role; task ownership stays with the commissioning agent.
- Each delegated assignment states the role, interaction mode (`interactive` or
  `non-interactive`), user-question channel and return channel. Follow that mode;
  do not infer it from the role or session name. Clarify missing details with the
  caller when needed, while continuing work that does not depend on them.
- Read applicable global and project agent instructions; the tool notes below say where.
- Save any docs in a suitable location using YYYY-MM-DD-title.md format.
- Follow the assignment's workflow and approval boundaries. An agreed plan may cover
  implementation, tests and relevant validation. Preserve valid approvals; request
  a new decision for material scope or design changes or an explicit checkpoint.
- In background assignments, return questions requiring user judgment to the caller.
  State assumptions and unresolved decisions; do not invent the user's answers or
  wait for direct user discussion in a non-interactive worker.

## Reviews

- Interactive assignment: commission a separate non-interactive Reviewer yourself at
  the review tier stated in the assignment (default `standard`), address its findings
  and obtain follow-up review of affected work.
- Non-interactive assignment: do not commission a Reviewer. Return your result marked
  ready for review, with the review material your role lists. Lead commissions the
  review and routes findings back to you or to a follow-up worker.
- Report unresolved disagreement with review findings instead of silently discarding it.

## Delegation and reporting

- Delegate research to the Researcher subagent to save your context, when your tool
  allows you to start subagents. Give each one a simple, narrow question and split
  broader research into several; draw conclusions yourself from what it returns.
- Lead owns interactive launches. Other roles send findings and requests for an
  interactive conversation to Lead.
- Return conclusions, evidence, artifact paths, decisions and open questions to the
  caller.
  - When given a Herdr return address, send the reply with
    `herdr agent prompt <caller> "<summary>"` without `--wait`.
  - Without a return channel, give the user an explicit handoff.
