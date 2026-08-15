#!/usr/bin/env python3
"""Non-LLM validator for the markdown INDEX + subjects memory adapter.

Exit 0 if no errors. Warnings print to stderr but do not fail the run unless
--strict is set.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

EPISODE_REQUIRED = ("id", "time", "what", "source_type", "confidence")
SECRET_PATTERNS = [
    re.compile(r"BEGIN (RSA |OPENSSH |EC )?PRIVATE KEY"),
    re.compile(r"\bsk-[A-Za-z0-9]{16,}\b"),
    re.compile(r"\bghp_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bxox[baprs]-", re.I),
    re.compile(r"(?i)\b(api[_-]?key|secret_access_key|password)\s*[:=]\s*\S+"),
]
STATUS_HINTS = re.compile(
    r"(?i)\b(currently|right now|this session|this machine|wip\b|todo today|clone is)\b"
)
INDEX_ENTRY = re.compile(r"^(memory/[\w./-]+\.md)(?:\s+[—–\-]+\s*(.*))?$")
FENCE_YAML = re.compile(r"```(?:yaml|yml)\s*\n(.*?)```", re.S | re.I)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", default=".", help="Project root")
    p.add_argument("--memory-dir", default="memory", help="Memory directory relative to root")
    p.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    return p.parse_args()


def section(text: str, heading: str) -> str:
    pattern = re.compile(
        rf"^## {re.escape(heading)}\s*\n(.*?)(?=^## |\Z)",
        re.S | re.M,
    )
    m = pattern.search(text)
    return m.group(1) if m else ""


def yaml_fields(block: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for raw in block.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, val = line.split(":", 1)
        fields[key.strip()] = val.strip().strip('"').strip("'")
    return fields


def looks_like_episode(fields: dict[str, str]) -> bool:
    ident = fields.get("id", "")
    return ident.startswith("ep_") or ("what" in fields and "source_type" in fields)


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    mem = root / args.memory_dir
    errors: list[str] = []
    warnings: list[str] = []

    index_path = mem / "INDEX.md"
    if not index_path.is_file():
        errors.append(f"missing catalog: {index_path}")
        _print(errors, warnings, args.strict)
        return 1

    listed: list[Path] = []
    for i, line in enumerate(index_path.read_text(encoding="utf-8").splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("<!--"):
            continue
        if not stripped.startswith("memory/"):
            continue
        m = INDEX_ENTRY.match(stripped)
        if not m:
            warnings.append(
                f"{index_path}:{i} catalog line is not 'memory/<file>.md — description'"
            )
            continue
        if not (m.group(2) or "").strip():
            warnings.append(f"{index_path}:{i} catalog line is missing a one-line description")
        rel = m.group(1)
        target = root / rel
        listed.append(target)
        if not target.is_file():
            errors.append(f"{index_path}:{i} points at missing file {rel}")

    skip_names = {"INDEX.md", "situation.md", ".state.json"}
    on_disk = [p for p in mem.glob("*.md") if p.name not in skip_names]
    listed_set = {p.resolve() for p in listed}
    for p in on_disk:
        if p.resolve() not in listed_set:
            warnings.append(f"{p.relative_to(root)} exists but is not in INDEX.md")

    subjects = {p.resolve(): p for p in listed if p.is_file()}
    for p in on_disk:
        subjects.setdefault(p.resolve(), p)

    for path in subjects.values():
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(root)
        if "## Must never miss" not in text:
            warnings.append(f"{rel}: no '## Must never miss' heading")
        policy = section(text, "Must never miss")
        for j, line in enumerate(policy.splitlines(), 1):
            if line.strip().startswith("-") and STATUS_HINTS.search(line):
                errors.append(
                    f"{rel} Must never miss:{j} looks like status, not a rule/pointer"
                )
            if line.strip().startswith("```") and "yaml" in line.lower():
                warnings.append(f"{rel} Must never miss: fenced block — pointers should not paste bodies")
        for m in FENCE_YAML.finditer(text):
            fields = yaml_fields(m.group(1))
            if not looks_like_episode(fields):
                continue
            missing = [k for k in EPISODE_REQUIRED if not fields.get(k)]
            if missing:
                errors.append(f"{rel}: episode {fields.get('id', '(no id)')} missing {missing}")
            if fields.get("cause") and fields.get("tags") and fields["cause"] == fields["tags"]:
                errors.append(f"{rel}: episode {fields.get('id')} cause equals tags")
        for pat in SECRET_PATTERNS:
            if pat.search(text):
                errors.append(f"{rel}: possible secret/credential pattern ({pat.pattern})")
                break

    situation = mem / "situation.md"
    if situation.is_file():
        sit = situation.read_text(encoding="utf-8")
        for pat in SECRET_PATTERNS:
            if pat.search(sit):
                errors.append(f"{situation.relative_to(root)}: possible secret/credential pattern")
                break

    _print(errors, warnings, args.strict)
    failed = bool(errors) or (args.strict and bool(warnings))
    return 1 if failed else 0


def _print(errors: list[str], warnings: list[str], strict: bool) -> None:
    for w in warnings:
        print(f"warning: {w}", file=sys.stderr)
    for e in errors:
        print(f"error: {e}", file=sys.stderr)
    if not errors and not warnings:
        print("ok")
    elif not errors and warnings and not strict:
        print(f"ok ({len(warnings)} warning(s))")


if __name__ == "__main__":
    sys.exit(main())
