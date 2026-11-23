---
name: "dogwatch-design"
description: "Turn software requirements into an implementable approach, from a concise plan for a small change to a reviewed design for substantial work."
---

# Design

Start from the scope, existing findings and approved decisions. Resolve choices
that affect the solution: interfaces, data flow, dependencies, failure behavior,
migration needs and meaningful tradeoffs. Include only those relevant to the task.

Discuss the direction with the user. Ask one decision question at a time, explain
the tradeoff and your recommendation, and wait for the answer before the next
dependent decision. In a background assignment, route decisions through Lead.
For substantial work, keep dated working notes at the established location.
Record decisions and their rationale in order as they happen, including revisions.
Save each decision before the next question and track open choices.

For a small change, keep the written plan to the affected components and checks.
For substantial work, put a one-line link to the decision notes directly below the
design title, before the first section. Use this structure:

- **Objective** states the goal in one or two sentences.
- **Requirements** describes the current state, the intended behavior and any
  constraints the implementation must preserve.
- **Design** explains how the pieces work together. Use subsections named for the
  concerns that matter to this change. Point to the skeleton for code structure
  and explain behavior such as recovery after a partial failure.
- **Other considerations** covers relevant limitations, deferred work or follow-ups
  when they exist.

Keep the requirements and design sufficient to implement the change. The linked
notes provide the history behind those choices. Follow `dogwatch-write-doc` and
honor the user's requested depth or drafting process.

Include a code skeleton by default for development work. Even a small change
needs one if it introduces a model, class or module, adds or changes an interface
or schema, or introduces or reroutes calls or data flow across files. Skip it for
work that preserves the existing structure and flow, such as a fix inside one
function, a copy edit or a mechanical configuration update.

Agree on the direction with the user before editing source. Lead or Architect,
whoever owns design, drafts the plan or design and its skeleton together in the
task worktree. Show declarations and signatures in their intended files. For a
cross-file flow, show the entry point and each changed handoff, using a short
comment in an unfinished body where needed. Leave behavior and tests to
implementation and run checks appropriate to the unfinished diff.

When the workflow calls for design review, use a fresh Reviewer from the other
provider: Codex reviews a Claude-authored design, and Claude reviews a Codex-authored
design. Follow the shared review ownership and launch rules. Supply the design,
any skeleton diff and intended audience for the first pass, then scope and decision
notes for the second. Have Reviewer assess whether the proposed structure fits
the codebase and supports the behavior described in the design.
Use `dogwatch-write-doc`'s two-pass review: assess standalone clarity, brevity and
section boundaries before checking correctness against the supporting material.
Ask for concrete cuts or moves where content is repetitive or unnecessary. Resolve
supported findings and obtain follow-up review of affected sections. Resolve P0/P1
findings before calling the design ready; disclose remaining concerns.

Present the plan or design and any skeleton together for user approval. Carry
forward decisions already approved. After approval, if the user has authorized a
commit, commit only the reviewed skeleton before implementing behavior. Give the
implementation owner the approved plan or design with its linked decision notes
and any skeleton's commit hash or worktree diff. A design-only assignment ends here.
