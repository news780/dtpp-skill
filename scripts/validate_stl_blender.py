# Run with Blender, for example:
# blender -b --python validate_stl_blender.py -- file1.stl file2.stl
# or on this user's Windows machine when available:
# D:\blender.exe -b --python validate_stl_blender.py -- file1.stl file2.stl

from __future__ import annotations

import json
import sys
from pathlib import Path

import bpy
import bmesh


def import_stl(path: Path):
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    if hasattr(bpy.ops.wm, "stl_import"):
        bpy.ops.wm.stl_import(filepath=str(path))
    else:
        bpy.ops.import_mesh.stl(filepath=str(path))
    objs = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    if not objs:
        raise RuntimeError(f"No mesh imported from {path}")
    return objs[0]


def component_count(mesh) -> int:
    verts = list(mesh.vertices)
    if not verts:
        return 0
    adjacency = [[] for _ in verts]
    for edge in mesh.edges:
        a, b = edge.vertices
        adjacency[a].append(b)
        adjacency[b].append(a)
    seen = set()
    count = 0
    for idx in range(len(verts)):
        if idx in seen:
            continue
        count += 1
        stack = [idx]
        seen.add(idx)
        while stack:
            cur = stack.pop()
            for nxt in adjacency[cur]:
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
    return count


def validate(path: Path) -> dict:
    obj = import_stl(path)
    mesh = obj.data
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    non_manifold_edges = sum(1 for e in bm.edges if not e.is_manifold)
    boundary_edges = sum(1 for e in bm.edges if e.is_boundary)
    degenerate_faces = sum(1 for f in bm.faces if f.calc_area() <= 1e-9)
    verts = len(bm.verts)
    edges = len(bm.edges)
    faces = len(bm.faces)
    chi = verts - edges + faces
    genus_if_closed_orientable = None
    if non_manifold_edges == 0 and boundary_edges == 0:
        genus_if_closed_orientable = (2 - chi) / 2

    dims = [round(v, 4) for v in obj.dimensions]
    comps = component_count(mesh)
    bm.free()

    return {
        "file": str(path),
        "dimensions_mm": dims,
        "vertices": verts,
        "edges": edges,
        "faces": faces,
        "components": comps,
        "non_manifold_edges": non_manifold_edges,
        "boundary_edges": boundary_edges,
        "degenerate_faces": degenerate_faces,
        "euler_chi": chi,
        "genus_if_closed_orientable": genus_if_closed_orientable,
        "basic_pass": non_manifold_edges == 0 and boundary_edges == 0 and degenerate_faces == 0,
    }


def main() -> int:
    args = sys.argv
    if "--" in args:
        files = args[args.index("--") + 1 :]
    else:
        files = args[1:]
    if not files:
        print("Usage: blender -b --python validate_stl_blender.py -- file1.stl [file2.stl]")
        return 2
    results = []
    for file in files:
        try:
            results.append(validate(Path(file)))
        except Exception as exc:
            results.append({"file": file, "error": str(exc), "basic_pass": False})
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0 if all(r.get("basic_pass") for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
