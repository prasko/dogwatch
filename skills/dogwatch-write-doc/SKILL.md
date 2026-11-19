---
name: "dogwatch-write-doc"
description: "Write, revise or review substantive technical documents with clear priorities, separated concerns and concise, visible structure. Use for plans, designs, implementation notes and reports, not routine chat replies."
---

# Write a document

Follow the user's chosen structure, repository conventions and the task skill's
required content. Do not impose a universal template or page limit. Writing guidance
does not authorize creating an unrequested document or change your role's boundaries.

## Read before gathering context

When revising or reviewing an existing document, assess standalone readability first.
An agent already immersed in the task cannot simulate a fresh reader by rereading;
use a fresh Reviewer without inherited conversation history for that pass. Supply
the document, its purpose and intended audience, with supporting material for later.

1. Read the document before consulting conversation history or repository material.
   Can the reader identify what changes before encountering its rationale and steps?
   Record missing explanations, unexplained terms and steps whose purpose is unclear.
2. Then consult requirements, recorded decisions, code and evidence to assess
   correctness and completeness. Context that explains an unclear passage does not
   fix the document; retain the readability finding until the text stands on its own.

## Choose what matters

- **Start small:** make the first draft brief while covering the agreed structure
  and depth. Select the key explanations instead of compressing every available detail.
- **State the change first:** plainly say what is changing before explaining why
  or how. For a rename, give the old-to-new mapping before migration steps.
- **Expand on request:** let the user request more detail; honor depth already
  explicitly requested and the task's drafting, discussion and approval flow.
- **Explain decisions:** capture non-obvious reasoning and consequences. Link to
  code and evidence instead of narrating or repeating them.
- **Trim:** remove repetition, conversation history and speculative additions.
  Keep detail that helps the reader decide, implement or verify. The document should
  reduce their work, not add another implementation to read.

## Separate concerns

Give each concern one clear home; reference it elsewhere instead of restating it.
Distinguish the problem, proposed approach, agreed decisions and unresolved questions.
Keep the overview understandable without implementation detail; place supporting
detail in later sections. Preserve necessary evidence and uncertainty when trimming.

## Make structure visible

Use descriptive headings, bullets for parallel points, numbered steps for flows,
and tables where they clarify comparisons or outcomes. Use short prose to explain
reasoning and connections; do not turn everything into a checklist.
Keep code excerpts focused. Before returning, trim anything that does not help the
reader find the main point, understand a decision or act on the document.
