# Shared working rules

- Follow your assigned role; the commissioning agent retains oversight of delegated work.
- Each delegated assignment states the role, interaction mode (`interactive` or
  `non-interactive`), user-question channel and return channel. Follow that mode;
  do not infer it from the role or session name. Clarify missing details with the
  caller when needed, while continuing work that does not depend on them.
- Read applicable global and project agent instructions; the tool notes below say where.
- Read the repository-root `dogwatch.toml` when present. Its optional top-level
  `todo_file` is shared by every role and is relative to that root. Use it when the
  task calls for consulting or updating the backlog; the setting alone does not
  authorize changes. If absent, follow the repository's existing conventions.
- Skills supply procedures without changing your role, edit boundaries or existing
  authorization. Use included procedures directly; load other skills only as needed.
- Create worktrees at `~/Code/dogwatch/worktrees/{base_repo}/{worktree_name}`.
  Derive `{base_repo}` from the primary checkout's directory name, even when
  working from another worktree. Create parent directories as needed.
- Save any docs in a suitable location using YYYY-MM-DD-title.md format.
- Use `dogwatch-write-doc` when creating or substantially revising a document.
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
- For a requested cross-provider review, use the normal Herdr launcher defaults;
  do not add sandbox or approval overrides. Request review-only behavior in a
  self-contained prompt and return findings under the existing review rules.

## Delegation and reporting

- Delegate bounded research to a generic fast-tier subagent using `dogwatch-research`
  when your tool allows delegation. Supply the skill's resolved path, a narrow
  question, source locations and return channel. Split broad questions into smaller
  assignments and interpret the findings yourself. If delegation is unavailable,
  use the skill in your current context. There is no dedicated Researcher role.
- Assistant opens interactive Leads in task worktrees; it is a repository entry point.
- Lead owns interactive specialist launches for its task. Other roles send requests
  for an interactive conversation to Lead.
- Notify Lead or the commissioning agent only when a substantial checkpoint is
  complete: an agreed deliverable is ready for review, a review or validation pass
  is complete, or the assignment is finished. Short assignments normally need only
  a completion report.
- Do not send acknowledgements or progress messages after every turn, tool call or
  edit. Batch routine findings and working notes into the next checkpoint report.
  User-facing progress requirements do not imply notifications to Lead.
- Send peers and child agents only what they need to act, such as a decision that
  changes their work, contract or dependencies. Keep other updates in your own plan.
- Escalate blockers requiring the parent's action, decisions needed and material
  scope/design changes promptly; honor explicitly requested status updates.
- Include conclusions, evidence, artifact paths, decisions and open questions in
  checkpoint reports.
  - When given a Herdr return address, send the reply with
    `herdr agent prompt <caller> "<summary>"` without `--wait`.
  - Without a return channel, give the user an explicit handoff.

## Cleanup

- Close agents and remove disposable resources you started once their results are
  collected; report anything you keep.
- Parents that own task worktrees or interactive agents, such as Assistant and Lead,
  follow `dogwatch-cleanup` before closing children or removing worktrees, including
  on cancellation.
