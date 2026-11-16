---
name: "agentic-design"
description: "Turn software requirements into an implementable approach, from a concise plan for a small change to a reviewed design for substantial work."
---

# Design

Start from the scope, existing findings and approved decisions. Resolve choices
that affect the solution: interfaces, data flow, dependencies, failure behavior,
migration needs and meaningful tradeoffs. Include only those relevant to the task.

For a small change, propose a concise approach with affected components and checks.
For substantial work, build the dated design document in phases at the established
location. Start with objective/background, an overview and the big open questions.
Let the user review that first and settle the main direction before adding details.
Expand the detailed design incrementally as decisions are made, keeping each phase
small enough to review. Place key models, methods and affected files toward the end;
avoid large code dumps and conversation history.

Work conversationally: ask one decision question at a time, explain the relevant
tradeoff and your recommendation, then wait for the answer before moving to the next
dependent decision. Update the document as the conversation progresses. In a background
assignment, return the current draft and next decision to Lead for user discussion.

Discuss decisions through the current assignment's user channel. Distinguish
proposals from approved choices. Obtain the required approach approval before
building; preserve approval already covering the work. A design-only request ends
with the design and remaining decisions.

When the workflow calls for design review, give a separate Reviewer the scope,
design and relevant decisions. Resolve supported findings and obtain follow-up
review of affected sections. Resolve P0/P1 findings before calling the design ready;
disclose remaining concerns. Return the approach, approval state and review outcome.
