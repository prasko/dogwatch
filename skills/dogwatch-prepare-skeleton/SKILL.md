---
name: "dogwatch-prepare-skeleton"
description: "Show a proposed code structure as a reviewable diff, at the level of detail requested."
---

# Prepare a code skeleton

Prepare a diff in the intended source files for the scope and level of detail
requested. Show the proposed models and their defining fields, key classes and
functions, and the signatures or calls that explain how they fit together.

Include supporting interfaces, schema changes or additional call sites where
they help the reader trace the proposed flow. Leave behavior unfinished. Use a
short comment where a signature alone would leave the flow unclear.

If the structure outgrows the requested scope, show the partial diff before
expanding it. Run relevant structural checks, such as compilation or type
checking, and present the diff. Behavioral tests can wait for implementation.
