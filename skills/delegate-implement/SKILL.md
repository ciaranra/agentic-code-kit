---
name: delegate-implement
description: Delegate a bounded implementation to an agent, independently verify its result, and review corrections against a task contract. Use for decided work worth handing off; resolve open design questions first.
---

# Delegate implementation and verify the result

The orchestrator owns the task contract and final judgment. The implementer owns a bounded
change. A separate verifier supplies evidence. Assign these roles to available agents; no
vendor or model is inherently the planner, worker, or reviewer.

## Choose the execution path

Read the adapter for each host you will actually use:
[Claude](../../adapters/claude/README.md) or [Codex](../../adapters/codex/README.md).
Use native delegation when it satisfies the task; use a separate CLI session when you need a
different provider, a fresh session, or an enforceable permission boundary. With another host,
confirm its delegation, permissions, completion, and result capture before dispatch.

This workflow requests a bounded implementer and an independent verifier when the host permits
delegation. Honor explicit user limits on delegation, models, budget, and external actions.
Existing authorization carries forward; don't ask again solely because a different skill is
now active. If required capabilities or provider authorization are missing, complete unaffected
work and report the specific limitation. Never describe self-verification as independent.

## Prepare the contract

For a simple edit, doing it directly may cost less than handing it off. Otherwise give the
implementer a self-contained packet with:

- **Outcome and done criteria:** observable behavior, invariants, compatibility requirements,
  and non-goals. Cite the design/specification where there is one.
- **Verified context:** relevant architecture and real constraints. Check existing behavior
  before asserting it; label unresolved assumptions. Prescribe a contract rather than guessed
  edit locations or a helper whose semantics you have not checked.
- **Ownership:** workspace, starting revision, allowed scope, protected fixtures, and pre-existing
  changes. Set the task's commit/push policy from the user's actual authorization; dispatch alone
  adds no authority to publish, deploy, or change shared state.
- **Verification:** commands and expected outcomes. Distinguish tests that demonstrate the fix
  from tests that preserve existing behavior. Keep independent reference data under separate
  ownership when correctness depends on that oracle.
- **Stop conditions:** name the affected subtask. A blocked independent subtask should not stop
  the rest; a contradiction in the agreed design should be reported before changing that design.
- **Report:** changed files, commands and results, deviations (including seemingly benign ones),
  unresolved questions, and the exact revision/workspace examined.

Require the implementer to trace the affected behavior end to end, search for existing
primitives, fix the invariant at its owning layer, and inspect callers and newly reachable
paths. Tests provide evidence; they are not the full contract.

For validation, numerical boundaries, or complex changes, read only the relevant sections of
[earned lessons](references/lessons.md). For high-stakes work, independently check the packet
against the original specification before implementation; a faithful implementation of a wrong
packet is still wrong.

## Dispatch with attributable changes

Prefer a task-owned worktree for writes. A worktree starts from a revision, so explicitly carry
any required uncommitted inputs into it with their owner's agreement. Never stash or commit
someone else's work just to make the starting tree clean. If using a shared tree, establish
exclusive write ownership of the affected files and record pre-existing changes first.

Record the task's host, actual model if known, workspace, baseline revision, session identifier,
permission boundary, and artifact location. Give the worker only the context it needs.
Use the host's supported completion mechanism; wait for completion before reading results or
starting verification. A missing report, failed exit, or denied command is not success.

## Independently verify, then review

1. After the worker has stopped writing, inspect status, tracked diff, and new/untracked files
   against the baseline. Do not silently omit newly added files from review.
2. Give a fresh verifier the original packet, claimed outcome, stable changed workspace, and
   [verification role](../../roles/qa-verifier.md). Request the full specified checks and observed
   evidence. Keep the worker idle while verification runs. Builds may write artifacts; source,
   tests, and protected fixtures stay unchanged. An immutable snapshot or isolated verification
   copy is preferable when other sessions may write concurrently.
3. Check the verifier's evidence and scope. Routine work needs a scope and behavior review;
   correctness-sensitive work needs every hunk reviewed, including changed tests and fixtures.
   Use [cross-review](../cross-review/SKILL.md) or [deep-review](../deep-review/SKILL.md) when an
   independent adversarial review is warranted. Record whether independence came from fresh
   context, a different model/provider, or a specialized lens.
4. Send substantive findings to the same worker session, identifying the contract and evidence.
   Re-run checks affected by corrections. Repeated failed rounds are a reason to reassess the
   packet or take over, not to loop indefinitely; normally reassess after two correction rounds.
5. If work is rejected, remove only task-owned changes after confirming ownership still holds.
   Never use a blanket reset/checkout in a shared tree on the assumption that it started clean.

A verifier that could not run a required check returns UNVERIFIED for that claim. Do not turn
missing evidence into PASS, or quietly weaken the contract to close the task.

## Deliver

Report the resulting behavior, who implemented and verified it, actual verification results,
and remaining concerns. For substantial work, retain the packet, worker report, verification,
and resolved review findings with the project's existing artifacts. Integrate independent
worktrees sequentially and check the integrated result; evidence from a pre-integration tree
cannot prove the combined change. Publishing follows the user's existing authorization.
