# Earned implementation and handoff lessons

These are conditional checks distilled from the original codex-implement incident notes
(July–September 2026). They describe failure modes observed in workers and orchestrators;
they do not establish a permanent ranking of models. Load the sections relevant to the task.

## Contracts and existing behavior

- Read code before asserting what it does. A mistaken statement in a packet can authorize the
  worker, in its own interpretation, to remove an intentional guard to satisfy the statement.
- Specify semantics before naming a helper or error variant. Existing helpers may drop small
  contributions before accumulation; an existing error variant may print the wrong diagnosis.
- Reuse the repository's predicate for a set or classification instead of enumerating its
  members from memory. Both packet prose and copied code can omit legitimate members.
- Require file/line evidence when a worker claims it followed an existing pattern.
- Inspect claimed deviations that dismiss an upstream constraint as “incorrect.” Check the
  actual specification before allowing an adapter to bypass validation.

## Validation and boundaries

- Specify absent, present-valid, and present-invalid separately. Optional fields must not
  become required by an ambiguous “reject everything other than X” instruction. Also consider
  empty strings, empty collections, and zero.
- Validate bounds across the real operating range, not just beyond the supplied examples.
  For numerical work, report worst errors by region and choose margins from measurements.
- Widening a gate exposes downstream clamps, validators, and helpers to new inputs. Exercise
  primitives directly as well as through high-level paths; the latter may dodge saturation.
- A guard on a data object must cover external consumers, not just its own methods. Enumerate
  entry points accepting the guarded type and exercise consumer-side paths.
- “Infallible” requires checking assertions, panics, unwraps, and exceptions as well as explicit
  error returns.

## Verification and ownership

- Independently owned reference data prevents a worker from changing the expected answer to
  match its implementation. Ordinary test authoring is still part of implementation; protect
  the oracle when the task's correctness depends on it.
- Place regression checks where CI actually runs them. A test in an excluded package is not
  an active regression gate.
- Label fix-demonstrating tests and compatibility tests separately. A compatibility check
  should not be required to fail on the old implementation.
- A worker that stashed, restored, or copied source may have overlapped a verification run.
  Wait for all writes, inspect the actual files, and verify a stable snapshot. Investigate cache
  effects before calling an inconsistent failure “flaky.”

## Scope and correction loops

- Scope stop conditions to their contract. Continue independent subtasks when one is blocked.
- Ask for all deviations, including ones the worker considers benign. Compare the report
  against the diff and new files rather than trusting “deviations: none.”
- If repeated correction rounds expose mistakes in the packet, revise the packet from the
  source of truth. More reasoning effort cannot repair a contradictory specification.
