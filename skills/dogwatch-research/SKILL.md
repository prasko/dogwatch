---
name: "dogwatch-research"
description: "Answer a bounded factual question from code, documentation, configuration or web sources with concise evidence and pointers. Usable by any role or generic agent."
---

# Research

Answer one simple, narrowly scoped factual question. If it is broad or requires a
design decision, identify the missing scope or useful smaller questions rather than
guessing. Find relevant code, docs, configuration or primary web sources.

Return pointers (`path:line`, URLs and commands run), short supporting excerpts,
a factual summary, what you could not find and conflicting or uncertain evidence.
Keep it concise; omit raw logs. Interpretation and recommendations belong to the
caller or its subsequent scope/design activity.

Keep this research activity read-only: do not edit files or run mutating commands.
A bounded research worker returns its findings without delegating again. These
activity boundaries do not prevent an owning role performing other authorized work
after research is complete.

Use the current context and model. This skill neither launches a worker nor changes
models. Callers can delegate it to a generic fast-tier agent, supplying the question,
source locations, this skill's path and return channel; no Researcher role is needed.
