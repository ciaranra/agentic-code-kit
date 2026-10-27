# Codex adapter

Checked against local `codex-cli 0.164.0` help and official documentation on 2026-10-27.
Recheck CLI flags and host capabilities after upgrades; no model ID or price is assumed.

## Native host

The installer writes skills to `~/.agents/skills` (or project `.agents/skills`) and generated
roles to `$CODEX_HOME/agents` (default `~/.codex/agents`) or project `.codex/agents`.
Custom roles are TOML with `name`, `description`, and `developer_instructions`. Model and effort
inherit unless the user or host configuration selects them. Use the host's available spawn,
follow-up, and completion tools; their names differ between clients. Request fresh context for
verification instead of forking the author's reasoning into the verifier.

Native subagents inherit parent permissions. A verifier role's “no edits” instruction does not
create a separate read-only sandbox. For enforced filesystem separation, use a separate CLI
session under the appropriate policy or an externally isolated workspace. A build may need
writes for artifacts: isolate verification rather than quietly elevating its permissions.

## CLI from either orchestrator

Check `codex --version`, `codex exec --help`, and authentication with `codex login status`.
Confirm that the configured provider is authorized for the task's data; Codex need not use
OpenAI as its provider. Preserve approved model, reasoning, and service-tier choices.

Prepare a UTF-8 packet and a unique artifact directory outside the source tree. The following
Bash example assumes `task_workspace`, `task_packet`, and `task_artifacts` are absolute paths
set by the caller. Choose `task_sandbox=read-only` for a scout/reviewer, or `workspace-write`
for an authorized implementer. Worktree isolation and sandbox policy are distinct controls.

```bash
mkdir -p "$task_artifacts"
codex exec -C "$task_workspace" --sandbox "$task_sandbox" --json \
  -o "$task_artifacts/final.md" - \
  < "$task_packet" > "$task_artifacts/events.jsonl" 2> "$task_artifacts/stderr.log"
```

Capture the command's exit status without a pipeline masking it. Only accept success after the
process completes, the exit status is zero, and a nonempty final report exists. Use a fresh
artifact directory for each attempt so a previous report cannot masquerade as a new one.
Save the session ID from the `thread.started` JSON event for resumable runs. If the installed
version uses a different event shape, inspect its schema; don't guess or use `--last` while
other tasks may be running. Read the final report, using logs only for diagnosis.

Resume a known session with the same working directory, authentication home, and permissions:

```bash
codex exec -C "$task_workspace" --sandbox "$task_sandbox" --json \
  -o "$task_artifacts/correction-final.md" resume "$task_session_id" - \
  < "$task_feedback" > "$task_artifacts/correction-events.jsonl" \
  2> "$task_artifacts/correction-stderr.log"
```

Options owned by `exec`, including `-C` and `--sandbox`, precede `resume`. Record the original
home without exposing credentials and preserve it on resume. Do not duplicate credentials or
create additional identities as a generic concurrency workaround. Use supported native
concurrency or serialize runs when the installed CLI/account cannot safely fan out.

Keep failures visible. Missing dependencies or denied network access are blockers for the
specific check, not reasons to disable the sandbox. A filesystem sandbox does not constrain
every external connector action; inspect the available tool surface when isolation matters.

For a code review, `codex review --help` documents the installed scope flags. `exec` with an
explicit baseline and target remains suitable for custom review instructions and design claims.

Sources: [skills](https://learn.chatgpt.com/docs/build-skills),
[custom agents and permissions](https://learn.chatgpt.com/docs/agent-configuration/subagents),
[non-interactive execution](https://developers.openai.com/codex/noninteractive).
