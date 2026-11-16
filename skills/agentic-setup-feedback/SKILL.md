---
name: "agentic-setup-feedback"
description: "Send user feedback or concrete observations about agentic-setup roles, skills and workflow to its repository's maintainer through Herdr. Use when asked to relay setup feedback or request a setup improvement based on current work."
---

# Setup feedback

Send actionable feedback to an existing agent in the agentic-setup repository.
The receiver owns checking coverage and making authorized source changes.

## Recipient

Use the Herdr skill for discovery and messaging, including its `HERDR_ENV=1`
requirement. If unavailable or outside Herdr, return the prepared feedback to the
caller and explain that it has not been sent.

Use an explicitly supplied live agent name or pane ID; otherwise target the agent
named `agentic-setup`. Inspect it with `herdr agent get <target>` and confirm its
working directory is the intended agentic-setup checkout. A matching name alone
does not establish the repository. If the target is missing or ambiguous, report
that and ask for a recipient; do not start an agent or broadcast to other agents.
Selecting among all agents in the repository is optional follow-up work, not
required for sending to a known recipient.

If this session is the recipient, read the local `AGENTS.md` and handle the feedback
here instead of sending a message to yourself.

## Handoff

Send a concise, self-contained message containing:

- The source project and task, concrete observed behavior, and desired behavior.
- The user's feedback, distinguished from the sender's interpretation or suggestion.
  Include relevant examples or file pointers, not a full conversation dump.
- The scope and approach already approved by the user, or that this is a suggestion
  only. Relaying feedback does not itself authorize implementation or deployment.
- Related requests already sent and unresolved conflicts.

Tell the recipient to read its repository's `AGENTS.md` before handling the request.
The receiver handles feedback and reports directly to Matija in its own conversation;
do not request a reply or acknowledgement. Related observations can travel together,
but preserve their distinct authorization and context.

Submit through `herdr agent prompt <target> <message>` without `--wait`, using safe
shell quoting that preserves the message literally. Do not interpret user text as
shell code. Follow the Herdr skill if the recipient is blocked or delivery fails;
do not answer its approval prompts or blindly retry an uncertain submission.

Report successful submission as sent, not applied. Continue the original task when
it does not depend on the feedback outcome; do not wait for a receiver response.
