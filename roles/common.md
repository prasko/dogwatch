# Shared working rules

- Follow your assigned role; task ownership stays with the commissioning agent.
- Each delegated assignment states the role, interaction mode (`interactive` or
  `non-interactive`), user-question channel and return channel. Follow that mode;
  do not infer it from the role or session name. Clarify missing details with the
  caller when needed, while continuing work that does not depend on them.
- Read applicable global and project agent instructions; the tool notes below say where.
- Skills supply procedures without changing your role, edit boundaries or existing
  authorization. Use included procedures directly; load other skills only as needed.
- Save any docs in a suitable location using YYYY-MM-DD-title.md format.
- Use `agentic-write-doc` when creating or substantially revising a document.
- Follow the assignment's workflow and approval boundaries. An agreed plan may cover
  implementation, tests and relevant validation. Preserve valid approvals; request
  a new decision for material scope or design changes or an explicit checkpoint.
- In background assignments, return questions requiring user judgment to the caller.
  State assumptions and unresolved decisions; do not invent the user's answers or
  wait for direct user discussion in a non-interactive worker.

## Reviews

- Reviewer always runs in a separate context. Self-checks do not replace it. Lead
  executing stages directly commissions review itself, normally one combined review
  for a small task. Scope review remains optional; each skill is not a review gate.
- Interactive assignment: commission a separate non-interactive Reviewer yourself at
  the review tier stated in the assignment (default `standard`), address its findings
  and obtain follow-up review of affected work.
- Non-interactive assignment: do not commission a Reviewer. Return your result marked
  ready for review, with the review material your role lists. Lead commissions the
  review and routes findings back to you or to a follow-up worker.
- Report unresolved disagreement with review findings instead of silently discarding it.

## Delegation and reporting

- Delegate bounded research to a generic fast-tier subagent using `agentic-research`
  when your tool allows delegation. Supply the skill's resolved path, a narrow
  question, source locations and return channel. Split broad questions into smaller
  assignments and interpret the findings yourself. If delegation is unavailable,
  use the skill in your current context. There is no dedicated Researcher role.
- Lead owns interactive launches. Other roles send findings and requests for an
  interactive conversation to Lead.
- Report to Lead or the commissioning agent at meaningful checkpoints: work ready
  for review, review completed with findings addressed or outstanding, or assignment
  complete. Batch routine edits and document updates into these summaries rather
  than sending a message after each change. Escalate blockers, decisions needed and
  material scope/design changes promptly; honor explicitly requested status updates.
- Include conclusions, evidence, artifact paths, decisions and open questions in
  checkpoint reports.
  - When given a Herdr return address, send the reply with
    `herdr agent prompt <caller> "<summary>"` without `--wait`.
  - Without a return channel, give the user an explicit handoff.
