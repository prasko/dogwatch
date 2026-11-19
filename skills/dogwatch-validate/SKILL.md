---
name: "dogwatch-validate"
description: "Validate software acceptance scenarios through an assembled system's real interfaces using fake data and throwaway resources, recording evidence and cleaning up afterward."
---

# Validate

Inspect acceptance criteria, the agreed approach, changes and existing evidence.
Choose complete scenarios with expected outcomes; startup or a health check alone
does not establish feature correctness. Reuse suitable existing acceptance evidence.

Follow repository setup instructions to run a throwaway instance. When validating in
a worktree, copy `.env` from the primary checkout if it exists and the worktree has
no `.env` yet. Use fake data and existing fixtures where suitable. Track resources
created for this run and avoid affecting unrelated resources. Stay within the
assigned execution authorization.

Exercise real interfaces. Record expected versus actual outcomes, useful evidence,
failures, untested paths and substituted dependencies. Do not claim substituted
integrations were tested against their real counterparts.

An implementation owner may fix failures within the agreed approach; a separately
assigned Validator reports production defects to that owner. Skill use does not
expand edit permissions. Rerun affected scenarios after fixes and request a new
decision for material scope/design changes.

Stop processes and remove disposable resources created for the run, including after
failure, unless the user asks to keep them. Report anything left running. Return
evidence and limitations for independent review against acceptance criteria. Save a
dated report when requested or needed for substantial evidence or a handoff; a small
run can be covered in the task report.
