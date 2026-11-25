---
name: "dogwatch-design"
description: "Turn software requirements into an implementable approach, from a concise plan for a small change to a reviewed design for substantial work."
---

# Design

Start from the scope, existing findings and approved decisions. Settle the big
picture first: the overall approach, component boundaries and the few decisions
that shape the PR plan. Then ask whether the user wants to go into details such
as failure behavior or migration now; otherwise record them as open or leave
them to the PR skeletons.

Settle these choices with the user using `dogwatch-interview`. For substantial work,
keep dated decision notes at the established location, in the order decisions are
made, and track open choices there.

## Write the plan or design

For a small change, keep the written plan to the affected components and checks.
For substantial work, draft the design as a whole after the interview. Keep it high
level: components, responsibilities, data flow and key decisions. Leave classes,
signatures, fields and file-level changes to each PR's skeleton. Put a one-line
link to the decision notes directly below the title, before these sections:

- **Objective** states the goal in one or two sentences.
- **Requirements** describes the current state, the intended behavior and any
  constraints the implementation must preserve.
- **Design** explains how the components work together, with subsections for the
  concerns that matter, such as recovery after a partial failure.
- **PR plan** lists the PRs in order, each independently reviewable and mergeable,
  with dependencies and what each provides to later PRs. It may propose sequential
  or parallel work; Lead orchestrates it. A single-PR change says so in one line.
- **Other considerations** covers relevant limitations, deferred work or follow-ups
  when they exist.

The linked notes provide the history behind those choices. Follow `dogwatch-write-doc`
and honor the user's requested depth or drafting process.

## Review and handoff

When design review is requested, use the two passes in `dogwatch-write-doc`.
Supply the design and intended audience first, then the scope and decision notes.
Address supported findings and obtain follow-up review of affected sections.
Resolve P0/P1 findings before calling the design ready and disclose remaining concerns.

Obtain user approval for the plan or design before implementation, carrying
forward any existing approval. Hand off the approved plan or design, linked
decision notes and review outcome. A design-only assignment ends here.
