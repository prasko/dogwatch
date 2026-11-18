---
name: "dogwatch-test"
description: "Select, author and run meaningful unit and integration tests for a software change, diagnose failures and report coverage and remaining gaps."
---

# Test

Start from requirements, acceptance examples, the agreed approach and changed code.
Choose a concise set of tests covering meaningful behavior, edge cases and failure
paths. Avoid assertions that merely mirror implementation or retest dependencies.
Do not add tests solely to accompany a reversible, low-impact edit.

Respect existing authorization and explicit code-approval or test-plan checkpoints.
Author the relevant tests and run applicable README checks. Reuse passing evidence
unless changes, failures or unresolved concerns justify rerunning it.

Handle failures according to the caller's ownership: an implementation owner such
as Lead or Developer may fix production code within the agreed scope; a separately
assigned Tester reports production defects to the implementation owner. This skill
does not expand edit permissions. Material scope/design changes need a new decision.
Rerun affected tests after fixes and include resulting production changes in review.

Return coverage, results, failures, unrun checks and remaining gaps. Supply the
requirements, tests, results and resulting code changes to the workflow's separate
Reviewer, together with implementation when appropriate.
