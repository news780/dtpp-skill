---
name: design-to-printable-product-modeling
description: Use when a user uploads a product design image or concept and wants an agent to iteratively create a functional 3D-printable Blender/STL/3MF model, or when the user invokes the dtpp alias in any capitalization such as dtpp, DTPP, Dtpp, or dTpP. Converts visual intent into measurable structure, generates versioned CAD-like geometry, renders previews, validates printability and functional constraints, and iterates until the model is ready for slicing or asks for missing critical constraints.
metadata:
  short-description: DTPP: turn product images into printable functional models
  aliases:
    - dtpp
    - DTPP
    - Dtpp
    - dTpP
---

# Design to Printable Product Modeling

Short alias: `dtpp`. Treat the alias as case-insensitive; `dtpp`, `DTPP`, `Dtpp`, `dTpP`, and any other capitalization all refer to this skill.

## Trigger

Use this skill when the user provides a product image, design board, sketch, rendering, reference product, or short product idea and wants a printable functional model, not just a visual 3D mockup. Also use it when the user invokes `dtpp` in any capitalization.

Typical phrasing:

- `dtpp`、`DTPP`、`Dtpp`、`dTpP`
- “根据我上传的产品图建模，并导出可打印的 STL。”
- “进入目标模式，按这张图从产品设计迭代到可切片测试的模型。”
- “做一个能装水、挂盆、卡扣、旋盖、滴灌、灯罩、支架或宠物用品等功能件。”

Do not use this skill for pure image generation, decorative-only renderings, or slicer parameter tuning unless the model geometry has already passed functional validation.

## Operating contract

The agent must act like a product-development loop:

1. Convert the uploaded image into a measurable target contract.
2. Separate visual styling from functional geometry.
3. Build a parametric or scripted Blender model with versioned outputs.
4. Render preview images from multiple views.
5. Validate STL/mesh/3MF with explicit checks.
6. Compare output against the target contract.
7. Iterate only on failed criteria.
8. Stop with a clear pass/fail report and next physical-print tests.

Never claim a model is “功能已验证” / “functionally validated” only because it looks correct or passes a mesh check. A functional print requires geometry validation, printability validation, feature-specific validation, and physical evidence.

## Evidence levels

Use exactly one current evidence level in `design_manifest.json` and `check_report.md`:

1. `cad_mesh_passed`: exported meshes pass the stated CAD/mesh checks. This is not proof of fit, slicing, or function.
2. `slicer_checked`: the correct STL hashes are confirmed in the 3MF/slicer project and orientation, supports, and printable features are reviewed.
3. `first_print_passed`: a first physical print completed and its dimensions/assembly observations are recorded.
4. `function_physically_validated`: the product-specific real-world test passed, such as leak, drip-rate, load, clip retention, or repeated assembly.

Only level 4 permits the statement “功能已验证” / “functionally validated.” Levels 1–3 are candidates for the next gate, not proof of final use.

## First response behavior

If the user has already uploaded a usable product image and asks for target-mode modeling, do not ask broad design questions first. Start by extracting a target contract.

Ask questions only when a missing constraint blocks safe or useful modeling:

- target dimensions or scaling basis,
- print technology/material/nozzle when tolerances matter,
- load/water/heat/food-contact/safety requirements,
- which side is visible versus functional,
- must-fit measurements such as pot rim thickness, screw diameter, phone width, candle diameter.

When uncertain, produce a default assumption table and mark each assumption as `needs confirmation` rather than silently inventing it.

## Target contract from image

For every uploaded product image, create `target_contract.md` before modeling. Extract these sections:

1. Product role: what the object does physically.
2. User scenario: where it is used, what it touches, how the user operates it.
3. Visual identity: silhouette, character, style, surface finish, color, proportion, visible seams.
4. Functional features: holes, chambers, hooks, clips, nozzles, caps, hinges, threaded parts, magnets, drainage, airflow.
5. Fit dimensions: known dimensions from image text, user text, or inferred constraints.
6. Hidden structures: cavities, walls, clearances, support-free regions, internal passages.
7. Print constraints: orientation, wall thickness, overhangs, bridges, tolerances, support removal access.
8. Variant matrix: sizes, hole diameters, clip widths, colorways, left/right variants.
9. Acceptance criteria: measurable pass/fail checks.
10. Visual red lines: things the output must not look like.

Read `references/intake-schema.md` when the image contains multiple panels, exploded views, instruction steps, dimension callouts, or internal cutaways.

## Modeling strategy

Use Blender scripting or CAD-like procedural geometry where possible. Keep the model reconstructable from code rather than hand-editing an opaque scene.

Recommended sequence:

1. Create a clean version folder: `generated_vN/`.
2. Define global units in millimeters and copy `references/design-manifest-template.json` to `design_manifest.json`.
3. Build a low-detail functional skeleton first.
4. Add fit-critical features: hooks, sockets, threads, holes, caps, channels, interfaces.
5. Add internal functional volume or moving clearance.
6. Add visual shell and styling details.
7. Apply bevels, weighted normals, smoothing, and cleanup.
8. Export STL/3MF and preview `.blend`.
9. Re-import exported meshes and validate independently.
10. Render previews and compare against the target contract.

For fragile functional geometry, use low freedom: explicit dimensions, fixed clearance rules, deterministic validation scripts. For purely decorative styling, allow more freedom but never let decoration break the functional skeleton.

Read `references/modeling-playbook.md` for detailed build phases and iteration rules.

## Functional-first rules

- A decorative shape must never cut through a required chamber, wall, clip, bearing surface, or load path.
- Internal voids must be intentionally modeled, reachable when needed, and printable without impossible support removal.
- For containers or fluid parts, `manifold=True` is only a minimum check; also inspect connected components, internal tunnels, Euler/genus or equivalent topology, wall thickness, and real fill/drain path.
- For clips/hooks, validate opening width, insertion clearance, wall thickness at the root, stress concentration, and print orientation.
- For caps/plugs/screws, validate clearance, bevels, lead-in chamfers, and whether the user can actually grip/remove the part.
- For small nozzles/holes, export multiple test diameters when clogging or flow rate is uncertain.
- For load-bearing parts, prefer fillets, ribs, larger root radii, and orientation-aware layer direction.

Read `references/fluid-container.md` before modeling or diagnosing any fluid part. Read `references/validation-checklist.md` before calling any output final.

## Visual interpretation rules

When the image is a polished design board, do not copy surface appearance only. Parse it like a product spec:

- Dimension callouts become target dimensions.
- Exploded views define parts and assembly relationships.
- Cutaways define internal volumes and wall routes.
- Use-step icons define required affordances.
- Feature highlight panels define selling-point geometry.
- Color option panels usually do not require multiple geometry exports unless color affects material or visibility.

If the image conflicts with physical manufacturability, preserve the product intent and adjust geometry. Record the adjustment in `target_contract.md` and `check_report.md`.

## Required outputs

Minimum deliverables for a complete modeling run:

- `target_contract.md`
- `design_manifest.json`, the single source of truth for parameters, materials, versions, STL hashes, and evidence level
- versioned Blender generation script, for example `generate_product_vN.py`
- one or more STL files for printable parts
- preview `.blend`
- preview images: front, side, top, three-quarter, and one function-focused view
- `check_report.md`
- `summary.json` with dimensions, variants, validation results, and assumptions

If the product is multipart, export each printable part as a separate STL and include an assembled preview scene.

## Validation gates

The agent must pass these gates in order:

1. Target gate: target contract exists and all critical assumptions are listed.
2. Feature gate: every functional feature in the target contract appears in the model.
3. Mesh gate: exported STLs are re-imported and checked for manifold issues, degenerate faces, scale, and every connected component. `basic_pass` means this gate only.
4. Product-rule gate: apply the relevant `--product-rules` checks and record what still requires measurement or a physical test.
5. Print gate: confirm STL hashes in 3MF, then review orientation, overhangs, support-removal access, wall thickness, and small-feature limits.
6. First-print gate: record the first printed part, actual dimensions, and assembly result.
7. Functional gate: run the product-specific physical test. Only a pass raises the evidence level to `function_physically_validated`.
8. Visual gate: complete `references/visual-acceptance.md` against the reference image and render set.
9. Report gate: failures and remaining physical tests are explicitly listed.

If any gate fails, iterate from the smallest responsible layer. Do not randomly tune all dimensions.

## Iteration policy

Use bounded iteration:

- v0: target contract and risk analysis.
- v1: functional skeleton.
- v2: visual shell over functional skeleton.
- v3+: correction loops driven by validation failures or user feedback.

Each iteration must state what changed and what did not change. Do not overwrite previous successful versions unless the user explicitly requests it.

When a user rejects the look, do not keep patching the same failed modeling paradigm. Identify the paradigm that caused the look and replace it. Example: if a caterpillar body generated by sinusoidal tube scanning looks like a corrugated pipe, switch to overlapping ellipsoid character sculpture plus shallow segmentation.

## Diagnostic rules for existing files

If the user uploads `.blend`, `.stl`, `.3mf`, or slicer screenshots:

1. Confirm the current Blender scene contains the target object; if not, inspect files directly.
2. For `.3mf`, inspect it as zip/XML first and write `3mf_manifest.json` to identify referenced STLs, hashes, versions, and slicer modifiers.
3. Re-import the referenced STL files and validate them, not only the currently open scene.
4. Distinguish geometry defects from slicer/support defects.
5. If the printed part fails functionally, do not start with support blockers or print settings unless the geometry already passes the relevant functional gate.

Use `scripts/validate_stl_blender.py -- --product-rules fluid-container file.stl` and `scripts/inspect_3mf.py file.3mf` as starting points when available.

## Completion definition

A modeling task is complete at its stated evidence level only when the output package contains its reports and tells the user:

- what was built,
- what assumptions were used,
- exact dimensions and variants,
- which validations passed,
- which physical tests remain,
- how to slice/print the first test piece,
- what to change if the first print fails.

Do not present concept renders as finished printable models, and do not present a mesh pass as functional validation.

## References

- For detailed intake: read `references/intake-schema.md`.
- For build workflow: read `references/modeling-playbook.md`.
- For validation: read `references/validation-checklist.md`.
- For fluid products: read `references/fluid-container.md`.
- For the single source of truth: copy `references/design-manifest-template.json` into the version folder.
- For visual sign-off: read `references/visual-acceptance.md`.
- For reusable prompts: read `references/prompt-templates.md`.
- For a worked example based on the caterpillar planter dripper: read `references/case-caterpillar-dripper.md`.
