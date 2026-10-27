---
name: cross-review
description: Independently challenge a design, task packet, claim, or code change and resolve actionable findings against evidence. Use at consequential design decisions or when a second opinion is requested.
---

# Cross-review

Select a reviewer relative to the author. Prefer a different model/provider when that is
available and authorized; otherwise use fresh context and describe the actual independence.
A different CLI is not proof of a different underlying model. Do not silently cross a new data
boundary; carry forward existing provider authorization.

Use the relevant [Claude](../../adapters/claude/README.md) or
[Codex](../../adapters/codex/README.md) adapter. Give the reviewer the target revision/diff or
design, original specification, runtime constraints it cannot infer, and the claim to test.
Include untracked/new files and keep the reviewed tree stable. Avoid the author's rationale
or conclusions when they would prime the review; frame disputed claims as hypotheses.

Ask for actionable findings with severity, confidence, file/line evidence or reproduction,
assumptions, and an overall verdict. Cover correctness, missing cases, and scope; skip stylistic
nits unless they affect the contract. The reviewer reports findings and does not implement fixes.

Cross-check each finding against the actual source. Keep valid findings, explain rejected ones,
and send substantive corrections back to the implementer. Re-review affected behavior after
fixes; don't restart an entire panel for unrelated nits. If a reviewer cannot inspect or execute
a required check, report that limitation instead of manufacturing a verdict.

Retain useful review evidence in the project's normal artifacts for substantial changes.
