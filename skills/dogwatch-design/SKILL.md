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
   these notes on disk from the first decision; do not wait for an overview draft.
2. **Design overview:** build the design document with three major sections in order:
   **Objective**, **Background**, **Overview**. State what will be built and why,
   synthesizing the agreed direction rather than recounting decisions. Let the user
   review this before adding details.
3. **Detailed design:** in the next phase, add **Detailed design** with numbered,
   descriptive subsections. Expand incrementally as requested, keeping each phase
   small enough to review.

The design is a standalone statement of what will be built and why, not a conversation
record. Keep decision logs, open questions and other transient tracking in the notes.
Propose any additional major section (such as alternatives, future plans, privacy or
security) before adding it; include relevant detail within the agreed structure.

Use `dogwatch-write-doc` for concise writing and visible structure.
Include a short list of key services, models and affected files in detailed design,
with their responsibilities; avoid an exhaustive inventory or method-by-method walkthrough.

Work conversationally: ask one decision question at a time, explain the relevant
tradeoff and your recommendation, then wait for the answer before moving to the next
dependent decision. In a background assignment, return the saved decision notes or
current draft and next decision to Lead for user discussion.

Discuss decisions through the current assignment's user channel. Distinguish
proposals from approved choices. Obtain the required approach approval before
building; preserve approval already covering the work. A design-only request ends
with the design and remaining decisions.

When the workflow calls for design review, give a separate Reviewer the scope,
design and relevant decisions. Resolve supported findings and obtain follow-up
review of affected sections. Resolve P0/P1 findings before calling the design ready;
disclose remaining concerns. Return the approach, approval state and review outcome.
