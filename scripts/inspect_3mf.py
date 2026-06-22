#!/usr/bin/env python3
"""Inspect a 3MF ZIP/XML package and write a reproducible manifest.

The manifest exposes STL references and hashes so a slicer project that still
references an older STL can be detected before print testing.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path
from typing import Any


STL_PATTERN = re.compile(r"(?i)[A-Za-z0-9_./\\ -]+\.stl")
VERSION_PATTERN = re.compile(r"(?i)(?:^|[_-])(v\d+(?:\.\d+)*)?(?:[_-]|$)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect a 3MF file as ZIP/XML and write 3mf_manifest.json.")
    parser.add_argument("path", type=Path, help="3MF package to inspect")
    parser.add_argument("--output", type=Path, help="Manifest destination; defaults beside the 3MF")
    return parser.parse_args()


def extract_stl_names(text: str) -> list[str]:
    names = []
    for match in STL_PATTERN.findall(text):
        name = match.strip().strip('"\'')
        if name not in names:
            names.append(name)
    return names


def version_from_name(name: str) -> str | None:
    for segment in re.split(r"[_-]", Path(name).stem):
        if re.fullmatch(r"(?i)v\d+(?:\.\d+)*", segment):
            return segment.lower()
    return None


def version_key(version: str | None) -> tuple[int, ...]:
    if not version:
        return ()
    return tuple(int(number) for number in version[1:].split("."))


def logical_name(name: str) -> str:
    return re.sub(r"(?i)(?:^|[_-])v\d+(?:\.\d+)*(?=[_-]|$)", "", Path(name).stem).strip("_-")


def sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def available_versions(directory: Path, stem: str) -> list[str]:
    return [version for file in directory.glob("*.stl") if logical_name(file.name) == stem if (version := version_from_name(file.name))]


def build_manifest(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"3MF not found: {path}")
    archive_references: dict[str, list[str]] = {}
    model_members: list[str] = []
    config_members: list[str] = []
    with zipfile.ZipFile(path) as zf:
        members = zf.namelist()
        for member in members:
            lower = member.lower()
            if not lower.endswith((".model", ".config", ".xml", ".rels")):
                continue
            text = zf.read(member).decode("utf-8", errors="replace")
            references = extract_stl_names(text)
            if references:
                archive_references[member] = references
            if lower.endswith(".model"):
                model_members.append(member)
            if lower.endswith((".config", ".xml", ".rels")):
                config_members.append(member)

    referenced_names = list(dict.fromkeys(name for names in archive_references.values() for name in names))
    stl_files: list[dict[str, Any]] = []
    warnings: list[str] = []
    for name in referenced_names:
        local = path.parent / Path(name).name
        version = version_from_name(name)
        candidates = available_versions(path.parent, logical_name(name))
        newest = max(candidates, key=version_key, default=None)
        stale = bool(version and newest and version_key(version) < version_key(newest))
        if not local.exists():
            warnings.append(f"Referenced STL is not beside the 3MF: {name}")
        if stale:
            warnings.append(f"Possible stale reference: {name} is older than available {newest}")
        stl_files.append(
            {
                "file_name": Path(name).name,
                "archive_reference": name,
                "version": version,
                "exists_beside_3mf": local.is_file(),
                "sha256": sha256(local),
                "newest_available_version": newest,
                "possible_stale_reference": stale,
                "referenced_by": [member for member, names in archive_references.items() if name in names],
            }
        )
    return {
        "schema_version": "1.1",
        "three_mf": {"file_name": path.name, "sha256": sha256(path)},
        "package_members": members,
        "model_references": {member: archive_references.get(member, []) for member in model_members},
        "config_references": config_members,
        "archive_references": archive_references,
        "stl_files": stl_files,
        "warnings": warnings,
    }


def main() -> int:
    args = parse_args()
    output = args.output or args.path.with_name("3mf_manifest.json")
    try:
        manifest = build_manifest(args.path)
        output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"Wrote 3MF manifest: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
