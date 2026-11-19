# Shared working rules

- Follow your assigned role; the commissioning agent retains oversight of delegated work.
- Each delegated assignment states the role, interaction mode (`interactive` or
  `non-interactive`), user-question channel and return channel. Follow that mode;
  do not infer it from the role or session name. Clarify missing details with the
  caller when needed, while continuing work that does not depend on them.
- Read applicable global and project agent instructions; the tool notes below say where.
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

## Task cleanup

- Each parent owns cleanup of agents and task resources it created or was explicitly
  assigned to manage. Track their names, paths and Herdr IDs; do not claim unrelated
  sessions or reused worktrees.
- Collect results and preserve needed evidence before closing children.
- For work without code changes, a recorded completion is enough. For code changes,
  a completion report or closed issue is not proof of merge.
- Before offering cleanup of code work, verify that the worktree's current work was
  merged into its intended target. For squash/rebase merges, use the merged PR and
  matching head revision rather than ancestry alone. Additional commits or uncertain
  merge evidence mean keep the worktree and explain what remains unresolved.
- Check for tracked, untracked and ignored files, including local notes in `docs/tmp/`.
  Preserve useful local material outside the worktree or ask how to handle it;
  ordinary worktree removal can discard ignored files.
- Identify running processes that use the worktree and who owns them before cleanup.
- Offer one short confirmation for the task, naming the agents, worktree and any local
  branch to remove: “#123 is merged. Close its agents and remove its worktree and local
  branch?”
- An explicit cleanup request or existing task-level approval covers the named targets.
  Pass it to child parents without repeating the question.
- Cancellation or abandonment requires an explicit decision about any unmerged work.
- After approval, recheck ownership, stop owned work/processes, collect
  final handoffs and close children before their parent.
- Immediately before removal, recheck the final HEAD and merge evidence plus tracked,
  untracked and ignored files. Final handoffs or process shutdown may have changed them.
- Worktree removal closes the linked Herdr workspace. Verify every affected tab/pane
  belongs to the task and is covered by the approval; otherwise retain the workspace.
- Use the Herdr skill's cleanup commands. Keep a linked worktree workspace available
  until its worktree-removal command completes; closing its last tab first can remove
  the target needed by that command.
- Remove worktrees without force. Delete a local branch only when covered by the
  confirmation and merge evidence; never treat refusal as permission to force it.
- Keep the primary checkout open.
- Report completed cleanup and anything retained.
