---
name: "agentic-design"
description: "Turn software requirements into an implementable approach, from a concise plan for a small change to a reviewed design for substantial work."
---

# Design

Start from the scope, existing findings and approved decisions. Resolve choices
that affect the solution: interfaces, data flow, dependencies, failure behavior,
migration needs and meaningful tradeoffs. Include only those relevant to the task.

For a small change, propose a concise approach with affected components and checks.
For substantial work, write a dated design at the established location, usually
with objective/background, overview and detailed design. Place key models, methods
and affected files toward the end; avoid large code dumps and conversation history.

Discuss decisions through the current assignment's user channel. Distinguish
proposals from approved choices. Obtain the required approach approval before
building; preserve approval already covering the work. A design-only request ends
with the design and remaining decisions.

When the workflow calls for design review, give a separate Reviewer the scope,
design and relevant decisions. Resolve supported findings and obtain follow-up
review of affected sections. Resolve P0/P1 findings before calling the design ready;
disclose remaining concerns. Return the approach, approval state and review outcome.
