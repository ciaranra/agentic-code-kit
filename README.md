# agentic-code-kit

Portable workflows and agent roles for Claude Code, Codex, and other coding-agent hosts.
Evolved from [claude-code-kit](https://github.com/ciaranra/claude-code-kit).

Delegate bounded work, keep ownership explicit, and verify claims against evidence. The same
workflow can be orchestrated by Claude or Codex, using native agents or an authorized external
CLI. Model choice belongs to the user and host configuration.

## Workflows

| Skill | Purpose |
| --- | --- |
| `delegate-implement` | Task contract → bounded implementation → independent verification → review and correction. |
| `scout` | Reconnaissance, inventories, and draft reports with checkable evidence. |
| `cross-review` | Independent review of a design, task packet, claim, or change. |
| `deep-review` | Multiple independent review perspectives, resolved by evidence. |
| `deep-research` | Independent source-grounded research for consequential questions. |
| `retro` | Recurring friction turned into the smallest durable correction. |

`codex-implement`, `codex-scout`, and `codex-review` remain compatibility entry points. They
select the Codex CLI and route to the shared workflows. A new Codex session can provide fresh
context; model diversity depends on which models actually authored and reviewed the work.

## Roles

| Role | Purpose |
| --- | --- |
| `qa-verifier` | Re-run the task's checks; return PASS, PASS-WITH-CONCERNS, or FAIL with per-claim evidence and explicit UNVERIFIED items. Never fixes source. |
| `tiger-grug` | Safety, correctness, performance, and simplicity review. |
| `grug-scout` | Review complexity, abstraction, and testing choices. |
| `ponytail` | Experimental reuse-first implementer for small, well-understood tasks. |

Canonical role instructions live in `roles/`. The installer renders Claude Markdown agents and
Codex TOML agents. Models and effort inherit from the host; host-specific tool settings live in
`adapters/<host>/roles.json`.

## Install or preview

Requires Python 3.11+ and Bash. No Python packages or model calls are needed to install.

```bash
git clone https://github.com/ciaranra/agentic-code-kit.git
cd agentic-code-kit

# Preview a project installation for both hosts.
./install.sh --host both --scope project --root /path/to/project --dry-run
./install.sh --host both --scope project --root /path/to/project

# Or install for your user.
./install.sh --host codex --dry-run
./install.sh --host codex
```

`--host` accepts `claude`, `codex`, or `both`. With no options, the original `./install.sh`
entry point still targets Claude's user directory. For project scope, `--root` defaults to the
current directory; for user scope it defaults to your home. An explicit `--root` is also useful
for staging an installation under `/tmp` without touching your setup.

| Host | User skills | User roles | Project paths |
| --- | --- | --- | --- |
| Claude | `~/.claude/skills` | `~/.claude/agents/*.md` | `.claude/skills`, `.claude/agents` |
| Codex | `~/.agents/skills` | `$CODEX_HOME/agents/*.toml`, default `~/.codex/agents` | `.agents/skills`, `.codex/agents` |

An explicit `--root` overrides the user destination, including `CODEX_HOME`. Project installs
always use project paths. Restart the host after installing. The installer does not edit
`CLAUDE.md`, `AGENTS.md`, settings, credentials, model choices, or permission policies.

Identical files are skipped. Differing files cause a failure **before any writes**. Review the
printed plan, then pass `--replace --dry-run` to preview or `--replace` to back up and replace.
Backups go under `<root>/.agentic-code-kit/backups/install-*/`, preserving host and relative paths.
All replacement backups finish before writes begin; individual writes are atomic, but the whole
installation is not a transaction. On an I/O failure, inspect the reported backup directory and
rerun or restore affected files. Run installation while no other process edits its destinations.
Symlink destinations and symlink parents are refused.

Upgrades also detect the old nested `grug-scout/AGENT.md` and `tiger-grug/AGENT.md` installations.
With `--replace`, those files are backed up and retired after their flat replacements are written.
Backups preserve local edits; merge any desired customization into the new role before use.
No other obsolete files are automatically removed.

## First workflow

Ask either host:

> Use delegate-implement for this bounded change. Give the implementer the agreed contract,
> then have a fresh qa-verifier check the resulting workspace. Review its evidence and report
> the behavior changed, checks actually run, and remaining concerns.

For an independent model review, identify the author and request another available model/provider.
If that provider is unavailable or not authorized, the workflow reports the limitation rather
than presenting a same-model pass as cross-model evidence.

The packet includes outcome, verified context, ownership, protected inputs, verification commands,
stop conditions, and expected report. The worker stops writing before verification. Review covers
tracked changes and new files. Corrections return to the worker; affected checks run again.
Independent worktrees are integrated sequentially and the integrated result is checked.

## Host boundaries

- [Claude adapter](adapters/claude/README.md): native agents, CLI execution, result capture, and permissions.
- [Codex adapter](adapters/codex/README.md): native roles, CLI execution/resume, and inherited permissions.

A role instruction is not a sandbox. In particular, Codex native roles inherit parent permissions;
a Claude verifier with Bash can also write. Use an appropriate separate session or isolated
workspace when enforced boundaries are needed. Verification may require build-artifact writes.

Skills, roles, and references are portable text. Another host can use them once its invocation,
permission, completion, and result semantics are established. This release ships installation
adapters for Claude and Codex only; it does not implement a scheduler or session transport.

## Maintain and validate

Edit canonical `skills/`, `roles/`, and `adapters/` files. Shared adapter and role references are
bundled into each installed skill that uses them, with links rewritten by the installer. Do not
maintain independent Claude and Codex copies of the workflow. Installing the complete kit keeps
sibling workflow references and compatibility wrappers available.

```bash
python3 -m unittest discover -s tests -v
bash -n install.sh
```

Tests run in temporary directories and cover both layouts, role rendering, packaged links,
collision handling, backups, migration, idempotence, destination boundaries, and scope selection.
CLI recipes were checked against local Codex 0.164.0 and Claude Code 2.1.311 help. Packaging tests
do not establish live model quality or guarantee compatibility with older hosts. Recheck adapters
when upgrading; use isolated task fixtures to evaluate behavior before relying on new workflows.

A native delegation trial on 2026-10-27 completed a parser fix with a separate implementer and
fresh verifier: six tests passed, additional input probes passed, and pre-existing untracked
files were preserved. This exercises the shared workflow; it does not establish external CLI
handoffs, automatic custom-role discovery, or cross-provider independence.

## Acknowledgements

This kit stands on other people's work, and two agents are largely theirs:

- **[grugbrain.dev](https://grugbrain.dev)** by Carson Gross — the complexity demon, the magic
  word "no", Chesterton's fence, FOLD. `grug-scout` is that philosophy turned into a reviewer,
  and `tiger-grug` takes its pragmatic half from the same place.
- **[DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail)** — the `ponytail`
  agent is that project's prompt, near-verbatim, with a house-rules paragraph swapped in for its
  closing line.
- **[TigerBeetle's Tiger Style](https://github.com/tigerbeetle/tigerbeetle/blob/main/docs/TIGER_STYLE.md)**
  — the safety half of `tiger-grug`: bounds on everything, assertions, naming discipline,
  performance considered at design time.

Upstream licenses and notices are reproduced in
[THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).

## License

MIT for original material; see [LICENSE](LICENSE). Derived role material retains upstream notices
in [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md), including in generated installations.
