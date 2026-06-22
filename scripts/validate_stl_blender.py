# Run with Blender, for example:
# blender -b --python validate_stl_blender.py -- file1.stl file2.stl
# Windows example:
# D:\blender.exe -b --python validate_stl_blender.py -- --product-rules fluid-container file1.stl
"""Validate exported STL meshes without confusing mesh health with product proof.

Exit status reflects only basic mesh validity. Product-rule failures are reported
in JSON but do not turn a CAD/mesh pass into a functional-product claim.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import bmesh
import bpy


STRAY_SHELL_AREA_RATIO = 0.05


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate one or more STL files in Blender.")
    parser.add_argument("files", nargs="+", help="STL files to inspect")
    parser.add_argument(
        "--product-rules",
        action="append",
        default=[],
        choices=("fluid-container", "hook", "clip"),
        help="Apply a named product-level rule set. Repeat for multiple rule sets.",
    )
    parser.add_argument(
        "--rules-config",
        type=Path,
        help="Optional JSON configuration for product rules, such as allowed boundary edges.",
    )
    return parser.parse_args(blender_args())


def blender_args() -> list[str]:
    """Return only arguments supplied after Blender's `--` separator."""
    import sys

    return sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]


def load_rules_config(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot read rules config {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("Rules config must contain a JSON object.")
    return data


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def import_stl(path: Path) -> list[Any]:
    clear_scene()
    if hasattr(bpy.ops.wm, "stl_import"):
        bpy.ops.wm.stl_import(filepath=str(path))
    else:
        bpy.ops.import_mesh.stl(filepath=str(path))
    objects = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    if not objects:
        raise RuntimeError(f"No mesh imported from {path}")
    for obj in objects:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        obj.select_set(False)
    return objects


def vertex_components(bm: bmesh.types.BMesh) -> list[set[int]]:
    adjacency = {vertex.index: set() for vertex in bm.verts}
    for edge in bm.edges:
        first, second = (vertex.index for vertex in edge.verts)
        adjacency[first].add(second)
        adjacency[second].add(first)

    seen: set[int] = set()
    components: list[set[int]] = []
    for vertex_id in adjacency:
        if vertex_id in seen:
            continue
        component = {vertex_id}
        stack = [vertex_id]
        seen.add(vertex_id)
        while stack:
            current = stack.pop()
            for neighbour in adjacency[current]:
                if neighbour not in seen:
                    seen.add(neighbour)
                    component.add(neighbour)
                    stack.append(neighbour)
        components.append(component)
    return components


def analyse_component(bm: bmesh.types.BMesh, vertex_ids: set[int], source_object: str) -> dict[str, Any]:
    component_edges = [edge for edge in bm.edges if all(vertex.index in vertex_ids for vertex in edge.verts)]
    component_faces = [face for face in bm.faces if all(vertex.index in vertex_ids for vertex in face.verts)]
    edge_count = len(component_edges)
    face_count = len(component_faces)
    euler_chi = len(vertex_ids) - edge_count + face_count
    non_manifold_edges = sum(1 for edge in component_edges if not edge.is_manifold)
    boundary_edges = sum(1 for edge in component_edges if edge.is_boundary)
    degenerate_faces = sum(1 for face in component_faces if face.calc_area() <= 1e-9)
    is_closed_orientable = non_manifold_edges == 0 and boundary_edges == 0
    return {
        "source_object": source_object,
        "vertices": len(vertex_ids),
        "edges": edge_count,
        "faces": face_count,
        "surface_area_mm2": round(sum(face.calc_area() for face in component_faces), 6),
        "non_manifold_edges": non_manifold_edges,
        "boundary_edges": boundary_edges,
        "degenerate_faces": degenerate_faces,
        "euler_chi": euler_chi,
        "genus_if_closed_orientable": (2 - euler_chi) / 2 if is_closed_orientable else None,
        "basic_pass": non_manifold_edges == 0 and boundary_edges == 0 and degenerate_faces == 0,
    }


def analyse_object(obj: Any) -> list[dict[str, Any]]:
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    reports = [analyse_component(bm, component, obj.name) for component in vertex_components(bm)]
    bm.free()
    return reports


def label_components(components: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ordered = sorted(components, key=lambda component: component["surface_area_mm2"], reverse=True)
    if not ordered:
        return ordered
    main_area = ordered[0]["surface_area_mm2"]
    for index, component in enumerate(ordered):
        component["index"] = index + 1
        if index == 0:
            component["role"] = "main"
        elif component["surface_area_mm2"] <= main_area * STRAY_SHELL_AREA_RATIO:
            component["role"] = "stray_shell"
        else:
            component["role"] = "secondary_shell"
    return ordered


def product_rule_results(
    requested: list[str], components: list[dict[str, Any]], config: dict[str, Any]
) -> dict[str, Any]:
    violations: list[str] = []
    manual_checks: list[str] = []
    per_rule = config.get("product_rules", {}) if isinstance(config.get("product_rules", {}), dict) else {}
    for rule in requested:
        options = per_rule.get(rule, {}) if isinstance(per_rule.get(rule, {}), dict) else {}
        if rule == "fluid-container":
            expected_components = int(options.get("expected_components", 1))
            if len(components) != expected_components:
                violations.append(
                    f"fluid-container requires {expected_components} connected shell(s); found {len(components)}"
                )
            if any(component["non_manifold_edges"] or component["degenerate_faces"] for component in components):
                violations.append("fluid-container contains non-manifold edges or degenerate faces")
            if not options.get("allow_boundary_edges", False) and any(
                component["boundary_edges"] for component in components
            ):
                violations.append("fluid-container has boundary edges; declare intentional ports in rules config")
            manual_checks.extend(
                [
                    "Verify one continuous liquid chamber, not only one exterior shell.",
                    "Verify fill, drain, and vent paths plus minimum wall thickness.",
                    "Run physical leak and drip-rate tests before claiming functional validation.",
                ]
            )
        elif rule in {"hook", "clip"}:
            manual_checks.append(
                f"{rule}: measure the target interface, clearance, root thickness, and print orientation."
            )
    return {
        "requested": requested,
        "passes": not violations,
        "violations": violations,
        "manual_checks": manual_checks,
    }


def validate(path: Path, requested_rules: list[str], rules_config: dict[str, Any]) -> dict[str, Any]:
    objects = import_stl(path)
    components = label_components([report for obj in objects for report in analyse_object(obj)])
    basic_pass = bool(components) and all(component["basic_pass"] for component in components)
    dimensions = [
        {
            "object": obj.name,
            "dimensions_mm": [round(value, 4) for value in obj.dimensions],
        }
        for obj in objects
    ]
    return {
        "file": str(path),
        "mesh_object_count": len(objects),
        "component_count": len(components),
        "components": components,
        "object_dimensions_mm": dimensions,
        "basic_pass": basic_pass,
        "basic_pass_meaning": "Mesh topology only; it is not evidence that the product function works.",
        "product_rule_results": product_rule_results(requested_rules, components, rules_config),
    }


def main() -> int:
    args = parse_args()
    try:
        rules_config = load_rules_config(args.rules_config)
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False, indent=2))
        return 2

    results: list[dict[str, Any]] = []
    for value in args.files:
        path = Path(value)
        try:
            results.append(validate(path, args.product_rules, rules_config))
        except Exception as exc:  # Keep the remaining files inspectable.
            results.append({"file": str(path), "error": str(exc), "basic_pass": False})

    report = {
        "schema_version": "1.1",
        "evidence_level": "cad_mesh_passed" if all(result.get("basic_pass") for result in results) else "cad_mesh_failed",
        "evidence_note": "Product-rule and physical-test outcomes are intentionally separate from basic mesh validity.",
        "product_rules": args.product_rules,
        "files": results,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if all(result.get("basic_pass") for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
