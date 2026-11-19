---
name: "dogwatch-design"
description: "Turn software requirements into an implementable approach, from a concise plan for a small change to a reviewed design for substantial work."
---

# Design

Start from the scope, existing findings and approved decisions. Resolve choices
that affect the solution: interfaces, data flow, dependencies, failure behavior,
migration needs and meaningful tradeoffs. Include only those relevant to the task.

For a small change, propose a concise approach with affected components and checks.
For substantial work, keep dated working notes separate from the design document
at the established location:

1. **Decision notes:** during the interview, save each resolved decision and its
   brief rationale to the notes before asking the next question. Keep open
   questions in those notes and update decisions when the user revises them. Persist
   these notes on disk from the first decision; do not wait for a design draft.
2. **Complete first draft:** after the interview, write the whole design in one pass,
   keeping it deliberately brief. Use **Objective**, **Background**, **Overview** and
   **Detailed design** in that order. Use descriptive, unnumbered subsections under
   Detailed design. End with **Other considerations** when there are relevant deferred
   decisions, TODOs or follow-ups to record.
3. **Whole-document review:** review and revise the draft as a whole, expanding where
   the user needs more explanation. Honor explicitly requested depth or staged drafting.

The design should stand alone: explain what changes, why and how the important pieces
fit together. Select what the reader needs to understand the proposal; brevity means
choosing what matters, not squeezing every detail into dense prose. Keep decision
history and supporting rationale in the notes. In Other considerations, distinguish
deferred work from unresolved choices needed for implementation. Propose additional
major sections before adding them; otherwise use the agreed structure.

Use `dogwatch-write-doc` for concise writing and visible structure.
Name key services, models or affected files in Detailed design when they help explain
the approach and responsibilities; avoid an exhaustive inventory or method-by-method
walkthrough.

Work conversationally: ask one decision question at a time, explain the relevant
tradeoff and your recommendation, then wait for the answer before moving to the next
dependent decision. In a background assignment, return the saved decision notes or
current draft and next decision to Lead for user discussion.

Discuss decisions through the current assignment's user channel. Distinguish
proposals from approved choices. Obtain the required approach approval before
building; preserve approval already covering the work. A design-only request ends
with the design and remaining decisions.

When the workflow calls for design review, use a fresh Reviewer from the other
provider: Codex reviews a Claude-authored design, and Claude reviews a Codex-authored
design. Follow the shared review ownership and launch rules. Supply the design and
intended audience for the first pass, then scope and decision notes for the second.
Use `dogwatch-write-doc`'s two-pass review: assess standalone clarity, brevity and
section boundaries before checking correctness against the supporting material.
Ask for concrete cuts or moves where content is repetitive or unnecessary. Resolve
supported findings and obtain follow-up review of affected sections. Resolve P0/P1
findings before calling the design ready; disclose remaining concerns. Return the
approach, approval state and review outcome.
