---
name: retro
description: Examine recent work for recurring friction and apply the smallest durable correction to instructions, skills, or project guidance. Use when the user requests a retrospective or setup improvement.
---

# Turn recurring friction into durable corrections

Use available conversation evidence and task artifacts: repeated corrections, failed handoffs,
verification gaps, misrouted skills, or recurring permission churn. Read other sessions only
within the user's authorized scope; transcript and memory locations depend on the host.
The [Claude](../../adapters/claude/README.md) and [Codex](../../adapters/codex/README.md)
adapters describe their configuration surfaces, not a universal transcript format.

A pattern earns a correction after recurrence, or one incident with clear generality. Do not
invent work to justify a retrospective. “No recurring friction found” is a complete result.

Choose the narrowest owner of each problem:

- A workflow trigger or missing decision rule belongs in that skill.
- A repository convention belongs in its existing project guidance (`AGENTS.md`, `CLAUDE.md`,
  or the host's equivalent), close to the affected code.
- A durable fact belongs in the established memory system, if one exists and is writable.
- A host configuration defect belongs in that host's supported settings mechanism. Repeated
  prompts alone do not justify broadening permissions or disabling approval checks.

Prefer correcting or removing stale instructions to adding rules. Preserve canonical kit
sources: installed copies are generated artifacts, so change the source and preview an update
when the kit owns the workflow. Avoid creating a new skill for something an existing one covers.
Do not post issues, send messages, or change external services without existing authorization.

Report each pattern with evidence, the correction and its location, and anything left unresolved.
