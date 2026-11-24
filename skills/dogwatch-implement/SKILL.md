---
name: "dogwatch-implement"
description: "Implement an agreed software change, coordinate its tests and validation, handle design drift and prepare the resulting changes for independent review."
---

# Implement

Build from the agreed plan or approved design within the caller's role and assigned
edit boundaries. Skill use does not grant approval to build. Preserve authorization
already covering implementation, tests and validation.

Follow the agreed plan and build from the approved skeleton diff or commit when
available. If skeleton approval is pending, obtain it before filling in behavior.

Include relevant tests as implementation develops, using `dogwatch-test` when needed.
Defer test authoring only when assigned separately or blocked by an explicit
code-before-tests checkpoint. Read the project's README and run applicable existing
checks. Use `dogwatch-validate` for runtime acceptance scenarios included in the work.
Do not force testing and validation into separate passes when evidence overlaps.

Raise material changes to scope or design through the current user-question channel
before dependent work continues. Explain the reason and affected decisions. Routine
fixes within the agreed approach do not require renewed approval.

Prepare the plan, approved skeleton baseline when applicable, code/test changes,
check results and relevant validation evidence for independent review, identifying
tests explicitly deferred.
Address findings, rerun affected checks and obtain follow-up review. Resolve P0/P1
findings before presenting the implementation as ready for final user review; keep
remaining findings and disagreements visible.

Present the finished implementation for the user's final review after the reviewer
and fix cycle.
Report final user review as pending until it occurs.

Keep implementation reports to a few bullets: changed behavior, any design drift,
checks/results and material gaps, approval/review state and the reviewed revision
or working-tree state. Link to evidence and code instead of narrating edits.
Reporting does not require a separate document.

For requested implementation documents, use `dogwatch-write-doc`. Include a short
list of key models, services or files and their role in the change when useful;
avoid an exhaustive inventory or repeating what the code already explains.
