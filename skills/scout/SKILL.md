---
name: scout
description: Delegate codebase reconnaissance, usage inventories, or first drafts to a fresh agent and return a compact, checkable report. Use when bulk reading would crowd the main task context.
---

# Scout

Delegate a bounded reading or drafting task using the available host:
[Claude](../../adapters/claude/README.md) or [Codex](../../adapters/codex/README.md).
Honor the user's provider and delegation choices. Keep design decisions with the orchestrator.

Give the scout the question, workspace, useful starting points, scope, and report format.
Request file/line evidence for code claims and explicit unknowns. Drafts belong in its report;
source edits require a separate implementation task. Prefer an enforced read-only session when
needed; a “do not edit” instruction alone is not a sandbox.

Use a fresh context to keep bulk exploration out of the main conversation. Select model and
effort from the task and available configuration, not assumptions about which provider is cheap.
Wait for completion using the host's supported mechanism. Read the final report; inspect raw
logs only to diagnose a failure.

Spot-check cited claims before relying on the inventory. If a sampled claim is wrong, treat the
report as leads and verify consequential claims directly. Ambiguous architecture or subtle
correctness questions need deeper investigation, not an unverified scout verdict.
