# Claude Code adapter

Checked against local Claude Code `2.1.311` help and official documentation on 2026-10-27.
Recheck flags and capabilities after upgrades; model and effort choices belong to the caller.

## Native host

The installer writes skills to `.claude/skills` and generated Markdown agents to
`.claude/agents`, under the home or project root. Roles inherit the host model. Reviewer roles
have reading tools; the verifier also has Bash to run checks. Bash can write, so the verifier's
“no source edits” instruction is not an enforced read-only filesystem boundary.

Use the host's agent tool with a self-contained packet and explicit workspace. Request fresh
context for verification. Use foreground completion or the host's supported background result
notification; don't transfer Claude-specific background flags to another client's tools.
Keep the worker idle while verification reads the changed tree. If a native agent cannot select
the isolated worktree or enforce the required boundary, use a separate session instead.

## CLI from either orchestrator

Check `claude --version`, `claude --help`, and `claude auth status`. Use the existing approved
provider and permission setup. `-p` skips the workspace trust dialog, so inspect/trust the task
workspace's configuration before invoking it. Do not add blanket tool approvals or permission
bypass flags to make a blocked run finish.

This Bash example assumes absolute `task_workspace`, `task_packet`, and `task_artifacts` paths
set by the caller, with a new artifact directory for each attempt:

```bash
mkdir -p "$task_artifacts"
(
  cd "$task_workspace" || exit 1
  claude -p --output-format json < "$task_packet" \
    > "$task_artifacts/result.json" 2> "$task_artifacts/stderr.log"
)
```

Capture the exit status. Inspect the JSON result for errors, permission denials, and actual
completion; process termination alone does not establish that checks ran. Save the returned
session ID. Resume that ID, in the same workspace, using `claude -p --resume "$task_session_id"
--output-format json` with feedback on stdin and new output files. Avoid `--continue` when
other sessions may be active. Use the parsed final result rather than loading raw logs.

For a reading-only review, restrict the tool surface to `Read,Grep,Glob` using `--tools` if those
tools suffice. That reviewer cannot execute verification commands. For verification requiring
Bash, use an isolated workspace and the existing permission policy; an allowlist containing
Bash does not enforce read-only behavior. Report denied checks as UNVERIFIED.

Sources: [custom agents](https://code.claude.com/docs/en/sub-agents),
[programmatic execution](https://code.claude.com/docs/en/headless).
