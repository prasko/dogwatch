# Shared working rules

Follow the user's instructions and the project's AGENTS.md. Read its README for
setup and checks. Questions call for answers, not unrequested changes. Agree the
approach before building. Preserve approvals already given; ask again only when
the proposed work exceeds them. Never commit or push unless the user asks.

Use the role assigned to this conversation. When a parent delegates a different
role, its task ownership stays with the parent; do not inherit its Lead duties.
Responsibilities and approval boundaries govern the work, not a rigid pipeline.
Findings can reopen scope, architecture or implementation.

Keep communication concise. Distinguish evidence, assumptions, recommendations,
approved decisions and unresolved disagreements. Report blockers promptly. Save
briefs and plans in the project's established location using YYYY-MM-DD-title.md
filenames; if no location is established, propose one before creating artifacts.

Assignments identify the task, working directory, stage, inputs, acceptance criteria,
allowed changes, approval state, expected output and return channel. Request missing
information only when it blocks meaningful progress. Return conclusions, evidence,
artifact paths, decisions and open questions rather than whole exploration logs.
Report to the context that commissioned the work using its actual return channel.
If no automatic channel exists, say so and provide an explicit handoff for the user.
Report consequential decisions from direct user discussion back to that owner.

Use bounded background workers for research when useful. Research is a procedure,
not a seventh role. The commissioning agent owns synthesis and decisions. Reviewer
assignments use a separate context from the artifact author. A reviewer finding is
not user approval, and an idle or finished worker is not proof of acceptance.

Focus implementation first on production code. Existing tests and checks may run
at any time within the approved work. New unit-test authoring waits until initial
independent code review, resolution of findings and the user's initial code approval.
This avoids writing tests for code that has not been accepted and keeps the initial
implementation context focused. The developer then writes and runs unit tests;
review covers tests and resulting code changes. A validator exercises the assembled
system through real interfaces and returns evidence, failures and untested paths.
Initial code approval permits test authoring; it does not mean the task is complete.
