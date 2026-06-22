#!/usr/bin/env python3
"""Inspect a 3MF file as a zip/XML package.

Usage:
    python inspect_3mf.py path/to/file.3mf

This script reports package members and likely mesh/model references. It does not
validate geometry; use validate_stl_blender.py for STL validation.
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python inspect_3mf.py path/to/file.3mf")
        return 2

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"ERROR: not found: {path}")
        return 1

    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()
        print(f"3MF: {path}")
        print("\nMembers:")
        for name in names:
            print(f"- {name}")

        print("\nLikely model/config XML snippets:")
        for name in names:
            lower = name.lower()
            if lower.endswith((".model", ".config", ".xml", ".rels")):
                try:
                    data = zf.read(name).decode("utf-8", errors="replace")
                except Exception as exc:  # pragma: no cover
                    print(f"\n## {name}\nERROR reading: {exc}")
                    continue
                hits = []
                for line in data.splitlines():
                    if any(token in line.lower() for token in [".stl", "mesh", "model", "object", "support", "modifier"]):
                        hits.append(line.strip())
                if hits:
                    print(f"\n## {name}")
                    for line in hits[:80]:
                        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
