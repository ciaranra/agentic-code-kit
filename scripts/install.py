#!/usr/bin/env python3
"""Render shared skills/roles and install them without changing host settings."""

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import tomllib

REPO = Path(__file__).resolve().parents[1]
HOSTS = ("claude", "codex")


def role_parts(path):
    """Canonical role metadata uses single-line strings, not arbitrary YAML."""
    _, front, body = path.read_text().split("---", 2)
    fields = {}
    for line in front.strip().splitlines():
        key, value = line.split(":", 1)
        value = value.strip()
        fields[key] = json.loads(value) if value.startswith('"') else value
    if set(fields) != {"name", "description"}:
        raise ValueError(f"Unsupported role metadata in {path}")
    if fields["name"] != path.stem:
        raise ValueError(f"Role name must match filename: {path}")
    return fields, body.lstrip()


def render_role(path, host, overrides):
    fields, body = role_parts(path)
    if host == "claude":
        fields.update(overrides)
        front = "\n".join(f"{key}: {json.dumps(value, ensure_ascii=False)}"
                          for key, value in fields.items())
        return f"---\n{front}\n---\n\n{body}".encode()
    fields.update(developer_instructions=body, **overrides)
    # JSON string escaping is compatible with TOML basic strings for this text.
    result = "\n".join(f"{key} = {json.dumps(value, ensure_ascii=False)}"
                       for key, value in fields.items()) + "\n"
    tomllib.loads(result)
    return result.encode()


def payload(host):
    files = {
        Path("agents/LICENSE"): (REPO / "LICENSE").read_bytes(),
        Path("agents/THIRD-PARTY-NOTICES.txt"): (REPO / "THIRD-PARTY-NOTICES.md").read_bytes(),
    }
    overrides = json.loads((REPO / "adapters" / host / "roles.json").read_text())
    for role in sorted((REPO / "roles").glob("*.md")):
        suffix = ".md" if host == "claude" else ".toml"
        files[Path("agents", role.stem + suffix)] = render_role(
            role, host, overrides[role.stem])
    for source in sorted((REPO / "skills").rglob("*")):
        if not source.is_file():
            continue
        relative = source.relative_to(REPO)
        if source.name == "SKILL.md":
            files[relative.parent / "LICENSE"] = (REPO / "LICENSE").read_bytes()
        if source.suffix != ".md":
            files[relative] = source.read_bytes()
            continue
        content = source.read_text()
        # Bundle linked shared resources so installed skills are self-contained.
        for resource in set(re.findall(r"\.\./\.\./((?:adapters|roles)/[\w./-]+\.md)", content)):
            target = Path("skills", relative.parts[1], "references", resource)
            files[target] = (REPO / resource).read_bytes()
            content = content.replace("../../" + resource, "references/" + resource)
        files[relative] = content.encode()
    return files


def check_path(path):
    """Refuse symlinks and non-directory ancestors before writing anything."""
    for ancestor in (path, *path.parents):
        if ancestor.is_symlink():
            raise ValueError(f"Refusing symlink destination: {ancestor}")
        if ancestor.exists() and ancestor != path and not ancestor.is_dir():
            raise ValueError(f"Destination parent is not a directory: {ancestor}")
    if path.exists() and not path.is_file():
        raise ValueError(f"Destination is not a regular file: {path}")


def destinations(args):
    root = Path(args.root).expanduser().absolute() if args.root else (
        Path.cwd() if args.scope == "project" else Path.home())
    hosts = HOSTS if args.host == "both" else (args.host,)
    plans = []
    for host in hosts:
        host_root = root / (".claude" if host == "claude" else ".codex")
        if host == "codex" and args.scope == "user" and not args.root:
            host_root = Path(os.environ.get("CODEX_HOME", str(host_root))).expanduser().absolute()
        skills_root = root / ".agents" if host == "codex" else host_root
        for relative, data in payload(host).items():
            base = skills_root if relative.parts[0] == "skills" else host_root
            plans.append((base / relative, data, Path(host) / relative))
    return root, plans


def install(args):
    root, plans = destinations(args)
    changes = []
    conflicts = []
    for destination, data, backup_relative in plans:
        check_path(destination)
        if destination.exists():
            if destination.read_bytes() == data:
                continue
            conflicts.append(destination)
        changes.append((destination, data, backup_relative))

    # Old releases copied nested AGENT.md files verbatim. Don't leave duplicate
    # role definitions behind, or discard local edits during migration.
    obsolete = []
    if args.host in ("claude", "both"):
        for name in ("grug-scout", "tiger-grug"):
            old = root / ".claude" / "agents" / name / "AGENT.md"
            check_path(old)
            if old.exists():
                conflicts.append(old)
                obsolete.append((old, Path("claude/agents") / name / "AGENT.md"))

    for destination, _, _ in changes:
        print(f"{'replace' if destination.exists() else 'create'} {destination}")
    for old, _ in obsolete:
        print(f"retire duplicate {old}")
    if conflicts and not args.replace:
        print("Existing files differ. Inspect the plan, then use --replace to back them up and replace them.", file=sys.stderr)
        return 1
    if args.dry_run:
        print(f"Dry run: {len(changes)} writes, {len(obsolete)} retirements; no files changed.")
        return 0

    backup = None
    if conflicts:
        backup_parent = root / ".agentic-code-kit" / "backups"
        check_path(backup_parent / "probe")
        backup_parent.mkdir(parents=True, exist_ok=True)
        backup = Path(tempfile.mkdtemp(prefix="install-", dir=backup_parent))
        # All backups complete before the first replacement or retirement.
        for destination, _, relative in changes:
            if destination.exists():
                saved = backup / relative
                saved.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(destination, saved)
        for old, relative in obsolete:
            saved = backup / relative
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(old, saved)
        print(f"Backups: {backup}")

    for destination, data, _ in changes:
        destination.parent.mkdir(parents=True, exist_ok=True)
        # Atomic per file. Preserve existing access mode on replacement.
        mode = destination.stat().st_mode & 0o777 if destination.exists() else 0o644
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as stream:
                temporary = Path(stream.name)
                stream.write(data)
            temporary.chmod(mode)
            temporary.replace(destination)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
    for old, _ in obsolete:
        old.unlink()
    print(f"Installed {len(changes)} files; retired {len(obsolete)} duplicate definitions. Restart the host to reload.")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", choices=(*HOSTS, "both"), default="claude")
    parser.add_argument("--scope", choices=("user", "project"), default="user")
    parser.add_argument("--root", help="Destination home/project directory (also useful for staging)")
    parser.add_argument("--dry-run", action="store_true", help="Show the plan without writing")
    parser.add_argument("--replace", action="store_true", help="Back up and replace differing files")
    args = parser.parse_args()
    try:
        return install(args)
    except (OSError, ValueError, KeyError) as error:
        print(f"Install failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
