# Workflow skills scope

Status: scoping record. The user subsequently authorized implementation; see the
skills, role instructions and README for the resulting behavior. Deployment uses
each tool home’s `skills/` directory so custom-home installs stay isolated.

## Objective

Let Lead complete small tasks in its own conversation using reusable scope, design,
implement, test and validate skills. Keep dedicated roles available when separate
ownership, a fresh context, specialist discussion or parallel work is useful.
Lead selects the execution pattern according to task size, uncertainty and risk;
the ability to execute stages directly does not establish a universal default.

Research becomes a sixth skill, usable by a role or a generic agent. Remove the
dedicated Researcher role. Lead continues delegating bounded research to fast/Haiku
agents even when it owns all five delivery stages. Reviewer always remains separate.

The user has established that most stage procedures should be reusable, but role
restrictions should not automatically become skill restrictions. In particular, a
separate Tester routes production fixes back to the implementation owner; Lead
using the test skill can make those fixes within the agreed plan.

## Current behavior and gaps

- `roles/lead.md` forbids Lead inspecting code and requires delegation of research,
  file inspection and documentation. Its small-task workflow still launches specialists.
- `roles/common.md` mixes shared working rules with assignment channels, handoffs
  and review commissioning. Those mechanics assume separate agents.
- Stage files mix useful procedures with role ownership, interaction modes, review
  requirements and reporting to Lead. Developer repeats some testing and validation guidance.
- `scripts/deploy.py` composes common instructions, a role and tool notes. It emits
  agents and profiles, with no skill outputs. Model tiers belong to role execution.
- `docs/roadmap.md` already identifies skills as the first priority, with reuse,
  routing and deployment unresolved.

Adding skill files alone would leave contradictory Lead instructions and two
copies of the procedures to maintain.

## Recommended separation

**Skills describe how to perform an activity.** They include the important questions,
decision criteria, useful evidence and completion conditions. They do not confer
new permissions, replace the current role or require another agent to be launched.

**Roles define responsibility and boundaries.** They retain interaction modes,
delegation mechanics, allowed edits, reporting channels and responsibility for
commissioning reviews. A Tester stays a Tester even when using a shared procedure.

**Lead chooses the workflow.** It selects stages, decides which to perform itself,
preserves decisions and authorization, and decides where independent review belongs.
Loading a skill neither starts the next stage nor authorizes it. Existing approval
continues to apply when switching stages or contexts.

Avoid permanent stage restrictions in skill wording. “This scoping step produces
findings or a brief” lets Lead subsequently implement an agreed approach; “never
edit code” would incorrectly constrain the rest of the conversation. Likewise, the
test skill must not universally grant production editing: that depends on its caller.

## Initial skill set

Proposed names use the existing `agentic-` prefix. Each skill should work on its own,
with the task context already available; using one should not load all six.

| Skill | Reusable procedure | Completion evidence | Kept in the dedicated role |
| --- | --- | --- | --- |
| `agentic-scope` | Inspect current behavior; establish the problem, outcome, constraints, exclusions and observable acceptance criteria; separate requirements from candidate solutions; identify assumptions and decisions. Support a bounded investigation or a complete brief. | Findings or a brief, supporting evidence, proposed direction and unresolved decisions. | Scoper's no-code/no-test-edit boundary, user-question channel and handoff to Lead. |
| `agentic-design` | Turn scope into an implementable approach; cover relevant tradeoffs, interfaces, affected components and failure modes. Scale from a short plan to a design document. | Proposed approach, important decisions, checks and approval state. | Architect's design-only assignment, dedicated discussion and review/reporting obligations. |
| `agentic-implement` | Follow the agreed approach; make coherent changes; include testing and validation when in scope; run relevant README checks; identify material drift and address findings. | Changes, check results, deviations, limitations and material ready for review. | Developer's interactive-session default, assigned boundaries and handoff mechanics. |
| `agentic-test` | Choose and author unit/integration tests from requirements and risks; cover meaningful behavior and failures; run relevant checks and rerun after fixes. Avoid tests that only mirror implementation or other libraries. | Coverage, results, failures, unrun checks and remaining gaps. | Tester's separate testing ownership and routing of production-code failures. |
| `agentic-validate` | Exercise complete acceptance scenarios through real system interfaces using fake data and disposable resources; record expected/actual behavior, substitutions and limitations; clean up resources created for the run. | Acceptance evidence, failed or untested paths, and cleanup status. Startup alone is insufficient. | Validator's assignment boundaries, failure routing and reporting to Lead. |
| `agentic-research` | Answer a bounded factual question from code, docs or other relevant sources; return evidence, pointers, uncertainties and conflicting information. Keep the research activity read-only and distinguish findings from recommendations. | Concise factual findings with sources and unanswered questions for the caller to interpret. | No dedicated role; remove Researcher. The caller supplies the assignment and return channel. |

Research supports any stage rather than adding a sixth delivery stage. Any role or
generic agent can use the skill. Its read-only boundary applies to the research
activity and does not permanently prevent the caller implementing later. Keep the
existing narrow factual remit; scope/design decisions remain with the stage owner.

Implementation can include testing throughout; these skills are not a mandatory
waterfall. Test concerns repeatable unit/integration coverage; validate concerns
acceptance evidence from the assembled system. Reuse evidence when a check serves
both purposes instead of running it twice for the stage labels.

For small tasks, use concise discussion and a final report where sufficient. Save
docs when requested, needed for a handoff or justified by substantial design or
validation evidence. Use the established location and dated filenames for saved docs.

## Lead workflow and routing

Choose the workflow by task size before assigning stage ownership. Small, understood
tasks can stay with Lead; medium tasks can mix direct execution and specialist
assignments; large tasks generally use dedicated specialists with Lead coordinating.
These are starting points, adjusted for uncertainty, risk and user preference.
Reassess the choice when investigation changes the apparent size of the task.

When direct execution is selected for a small task:

1. Establish the scope using the available context and targeted investigation.
2. Propose a concise approach and agree it with the user before building. If valid
   approval already covers the approach, preserve it.
3. Implement with relevant tests in the same conversation. Validate through runtime
   scenarios when the acceptance criteria warrant it.
4. Collect the agreed review evidence, resolve findings and report the result.

Lead can fix a production failure found while testing or validating when the fix
fits the approved approach. It must rerun affected checks. A fix that materially
changes scope or design needs a new decision before dependent work continues.

Use a dedicated role when fresh context, independent ownership, sustained specialist
discussion, parallel work or the volume of investigation justifies the handoff.
Risk and uncertainty matter more than a file-count threshold. Mixed workflows are
valid: Lead may scope and implement while delegating a bounded investigation or
validation run. If the task grows, carry the findings, approved decisions, current
changes and remaining work into the handoff without restarting completed stages.

Adjust Lead's restrictions enough to allow direct execution of the five delivery
stages. Preserve research delegation as the default: Lead sends a bounded question
to a generic fast-tier agent instructed to use `agentic-research`, then interprets
its findings. Apply the same reusable research path from other roles where delegation
is available. A dedicated Researcher agent definition is unnecessary.

Lead needs a short routing guide, with full procedures loaded as needed. A skill
runs in the caller's existing model/context. Fast/Haiku selection belongs to the
delegating caller's launch decision, not to the research skill; loading that skill
directly does not switch the current model or inherently spawn another agent.

## Review policy: confirmed

Reviewer always runs in a separate context. Lead can own scope through validation;
self-checks never replace independent review. For small tasks, the proposal remains
one combined review of implementation,
tests and relevant validation evidence. Keep scope review optional and avoid five
separate review gates just because there are five skills.

Do not introduce a review skill in this scope. Keep Reviewer separate;
its criteria can guide ordinary self-checks without changing the independence rule.
An orchestration skill is outside this initial set.

## Shared source and deployment direction

Recommendation: maintain each reusable stage procedure once, in its skill source.
Generate standalone skills for Lead and compose that same procedure into the
corresponding dedicated role alongside its role-specific instructions. Generated
copies are acceptable; manually maintaining two versions is not.

This preserves self-contained specialist instructions without requiring every
specialist to discover and load its skill. Lead loads only the procedures needed.
Developer's combined-work guidance should refer to the shared testing/validation
procedures rather than maintain another full copy. Resolve the precise composition
and reference mechanism during design; every deployed reference must be available
in the target environment, without relying on this repository being checked out.

Preserve the seven remaining roles and their existing entry points. Replace the
Researcher role with its standalone skill and update callers to use generic agents.
Keep role-launch syntax,
Herdr coordination and model tables out of stage skills. Use ordinary discoverable
skills with concise descriptions; do not force forked execution or change permissions.

Deployment should cover both Codex and Claude with the existing dry-run, check,
collision preflight, backups, repeatability and symlink protections. The roadmap
proposes `~/.agents/skills/` for Codex and `~/.claude/skills/` for Claude. Confirm
supported discovery paths and target-specific metadata during design, including
explicit destination overrides so temporary-home tests never touch live installs.
The Codex skill destination needs an explicit design because current output paths
are resolved under the selected Codex home. Do not silently couple a custom home
to writes into the real user's global skills directory.

Account for retirement of installed Researcher artifacts: Codex's agent and profile,
and Claude's agent. Design a narrow migration for those generated files, preserving
unmanaged files and backups. Removing the source role alone would leave stale installed
entry points, since the current deployer only manages its current output set.

## Implementation scope after agreement

Expected affected areas: new skill sources; the five stage roles; `roles/lead.md`
and `roles/common.md`; deployment and its tests; README, roadmap and any model-selection
wording that assumes every stage runs in another role. Update tool notes only where
needed for discovery or accurate routing. Remove Researcher from shared and per-tool
role configuration and generation, update research delegation references and model
guidance, and cover retirement of its installed artifacts. Preserve Reviewer behavior
and the research procedure's factual remit. Keep the fast tier for generic research
assignments even though it no longer has a dedicated role default.

Acceptance criteria for that future work:

- Lead selects direct, mixed or delegated execution according to task size,
  uncertainty and risk, rather than treating direct execution as the universal default.
- Lead can complete an agreed small change using the five procedures as needed,
  without mandatory specialist launches for each stage.
- A separate Tester reports a production defect; Lead using the test skill can fix
  that same defect within authorization and rerun tests.
- Scope-only and design-only requests stop before implementation. Existing approval
  survives skill transitions; material changes and explicit checkpoints still matter.
- Validation exercises behavior, reports substitutions/gaps and cleans up its own
  resources, including after failure. Fixes receive affected-scenario reruns.
- Reviewer always runs separately; self-checks do not replace it. Changing context
  does not erase decisions or repeat approval.
- Research works in both a role context and a generic agent. Lead's default research
  delegation selects the fast tier without requiring a Researcher role. Skill use
  alone neither switches models nor forces delegation.
- Researcher is removed from generated roles, caller references and role defaults;
  the migration handles its old managed outputs without touching unrelated files.
- One maintained procedure feeds both skills and roles. Outputs have valid metadata,
  working references and no accidental role-launch/model instructions in skills.
- Temporary-destination tests cover new outputs and existing deployment guarantees.
  Small behavioral exercises check the ownership/authorization distinctions; passing
  syntax checks alone does not establish that the instructions work.

Implementation was subsequently authorized. Live deployment remains a separate action.

## Confirmed direction and remaining decisions

Confirmed: task size informs whether Lead executes stages or delegates them;
five delivery skills are usable by Lead; role-specific restrictions remain
with their roles; Reviewer always separate; research delegation remains the default;
research becomes a reusable skill and the dedicated Researcher role is dropped.

Remaining proposal: one maintained procedure composed into both standalone skills
and applicable roles, with exact packaging and migration settled in design. Research
needs no corresponding role. This proposal was subsequently implemented for review.
