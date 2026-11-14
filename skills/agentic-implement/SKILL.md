---
name: "agentic-implement"
description: "Implement an agreed software change, coordinate its tests and validation, handle design drift and prepare the resulting changes for independent review."
---

# Implement

Build from the agreed plan or approved design within the caller's role and assigned
edit boundaries. Skill use does not grant approval to build. Preserve authorization
already covering implementation, tests and validation.

Include relevant tests as the change develops, using `agentic-test` when needed.
Defer test authoring only when assigned separately or blocked by an explicit
code-before-tests checkpoint. Read the project's README and run applicable existing
checks. Use `agentic-validate` for runtime acceptance scenarios included in the work.
Do not force testing and validation into separate passes when evidence overlaps.

Raise material changes to scope or design through the current user-question channel
before dependent work continues. Explain the reason and affected decisions. Routine
fixes within the agreed approach do not require renewed approval.

Prepare the plan, code/test changes, check results and relevant validation evidence
for independent review, identifying tests explicitly deferred. Resolve findings and
rerun affected checks; obtain follow-up review through the workflow's review owner.

Report what changed, drift from the approach, checks and results, unrun checks,
limitations, approval state and review outcome. Identify the reviewed working-tree
state or revision so later changes are not implicitly represented as reviewed.
