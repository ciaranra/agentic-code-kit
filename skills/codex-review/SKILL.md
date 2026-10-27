---
name: codex-review
description: Compatibility entry point for explicitly using the Codex CLI for independent review. Uses the shared cross-review workflow.
---

# codex-review

Follow [cross-review](../cross-review/SKILL.md), selecting the Codex CLI as the execution backend.
Read its [adapter](../../adapters/codex/README.md) before dispatch. Preserve the user's
scope, provider authorization, and model choices. This alias does not make a Codex reviewer
independent of a Codex author; report the actual model and context independence.
