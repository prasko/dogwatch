---
name: "dogwatch-cleanup"
description: "Close task-owned agents and remove task worktrees once work is verified as merged, preserving local material and anything still needed. For parents that own task agents or worktrees."
---

# Task cleanup

- Each parent owns cleanup of agents and task resources it created or was explicitly
  assigned to manage. Track their names, paths and Herdr IDs; do not claim unrelated
  sessions or reused worktrees.
- Once the task is complete and code work is verified as merged, close its owned
  agents and remove its owned worktrees by default, without another confirmation.
  Honor requests to retain resources and keep anything still needed for follow-up.
- Collect results and preserve needed evidence before closing children.
- For work without code changes, a recorded completion is enough. For code changes,
  a completion report or closed issue is not proof of merge.
- Before cleanup of code work, verify that the worktree's current work was
  merged into its intended target. For squash/rebase merges, use the merged PR and
  matching head revision rather than ancestry alone. Additional commits or uncertain
  merge evidence mean keep the worktree and explain what remains unresolved.
- Check for tracked, untracked and ignored files, including local notes in `docs/tmp/`.
  Preserve useful local material outside the worktree or ask how to handle it;
  ordinary worktree removal can discard ignored files.
- Identify running processes that use the worktree and who owns them before cleanup.
- If ownership, merge evidence or preservation of local material is unclear, retain
  the affected resources, explain why and ask for a decision when needed.
- Carry cleanup instructions and retention decisions to child parents across handoffs.
- Cancellation or abandonment requires an explicit decision about any unmerged work.
- Before cleanup, recheck ownership, stop owned work/processes, collect
  final handoffs and close children before their parent.
- Immediately before removal, recheck the final HEAD and merge evidence plus tracked,
  untracked and ignored files. Final handoffs or process shutdown may have changed them.
- Worktree removal closes the linked Herdr workspace. Verify every affected tab/pane
  belongs to the completed task and is eligible for cleanup; otherwise retain the
  workspace.
- Use the Herdr skill's cleanup commands. Keep a linked worktree workspace available
  until its worktree-removal command completes; closing its last tab first can remove
  the target needed by that command.
- Remove worktrees without force. Delete a local branch only when covered by the
  user's instructions and merge evidence; never treat refusal as permission to force it.
- Keep the primary checkout open.
- Report completed cleanup and anything retained.
