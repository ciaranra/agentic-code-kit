---
name: deep-research
description: Independently research a consequential or rapidly changing question, verify primary sources, and synthesize evidence across perspectives. Use when a single search is insufficient for the decision.
---

# Independent research panel

Define the question, decision criteria, relevant date, and required evidence. For questions
where stale or incorrect information is costly, request independent research perspectives
when delegation and resources permit. A quick settled fact does not need a panel.

Use the [Claude](../../adapters/claude/README.md) or [Codex](../../adapters/codex/README.md)
adapter as applicable. Confirm live source access before dispatch; model recollection is not
live research. Honor provider authorization and existing limits. Another model may use the
same search service, so do not assume a different index or independent evidence.

Give each researcher the question and constraints, without your preferred conclusion or the
other researcher's output. Useful diversity includes current primary sources, a counter-position,
a specialist facet, and another model. They may run sequentially in separate contexts.
Require source URLs, dates, supported claims, uncertainty, and conflicting evidence.

Open the cited sources and check consequential claims. Two researchers citing the same source
are not two independent confirmations. Resolve conflicts against the source material; distinguish
observation, inference, and unsupported hypotheses. Evaluate solo findings on their evidence.

Return the recommendation or answer, its key supporting sources, uncertainty, and material
coverage gaps. Keep research artifacts for substantial decisions in the project's usual location.
If live access is unavailable, state which questions remain unverified rather than presenting
training knowledge as a current finding.
