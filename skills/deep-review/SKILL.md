---
name: deep-review
description: Run independent reviewers for a consequential code change or design, then resolve their findings by evidence. Use when correctness risk warrants more than a single review.
---

# Independent review panel

Use [cross-review](../cross-review/SKILL.md) for the review contract and evidence handling.
For a high-stakes change, request two independent reviewers when available: fresh context plus
another model/provider relative to the author. Add a specialized lens only when the risk calls
for it. Honor the user's delegation and resource limits.

Select execution through the [Claude](../../adapters/claude/README.md) or
[Codex](../../adapters/codex/README.md) adapter. Record author/reviewer models when known;
a different host name does not establish model diversity. If only one model is available,
use fresh sessions or different lenses and describe the remaining correlated blind spots.

Give each reviewer the same stable target, original specification, and relevant runtime facts.
Do not give it the author's conclusions or the other reviewer's findings. Include new files.
Parallel execution is optional: blindness requires separate context, not simultaneous execution.
No reviewer writes fixes. Wait for all requested reviews before synthesizing a verdict.

Cross-check findings against source and reproductions:

- Corroborated findings increase confidence only when the evidence supports them.
- Solo findings are valuable non-overlapping coverage; judge them on merit.
- Conflicts need investigation, not a majority vote.

Deduplicate issues, explain rejected findings, and produce a severity-ranked list with one
verdict. State missing evidence and what all reviewers might have missed. Return corrections
to the implementer, then review the affected behavior again. Retain raw reviews and resolved
findings in the project's normal artifact location for substantial work.
