# Modeling Playbook

## Phase 0: target mode

Target mode means the agent owns the closed loop from product image to printable candidate. It does not mean the agent may skip validation or user constraints.

Produce a target contract and a short execution plan before editing geometry. If the user explicitly says to proceed without questions, proceed with marked assumptions.

## Phase 1: functional skeleton

Create a low-detail model that proves the function:

- fit interface first,
- internal volume or load path second,
- removable parts third,
- visual envelope last.

For Blender scripts, keep all critical values as named constants. Avoid magic numbers inside mesh construction.

Common constants:

- `WALL_THICKNESS_MM`
- `CLEARANCE_FDM_MM`
- `NOZZLE_MM`
- `LAYER_HEIGHT_MM`
- `FIT_SLOT_WIDTH_MM`
- `PART_VERSION`
- `EXPORT_DIR`

## Phase 2: visual shell

Build the shell as an intentionally designed object, not a side effect of the functional skeleton.

Preferred approaches:

- Combine primitive masses with boolean union, bevel, and weighted normals.
- Use bevelled boxes for product-like hard goods.
- Use overlapping ellipsoids for toy-like organic shapes.
- Use shallow grooves or surface embossing for segmentation.
- Use separate detail objects for eyes, buttons, icons, knobs, and caps.

Avoid:

- deep decorative cuts through functional bodies,
- scanline/tube methods that create pipe-like results when the target is a character or consumer product,
- putting all variants in one visual preview,
- using infill as a functional wall or reservoir boundary.

## Phase 3: variant generation

Generate variants only along controlled axes:

- size,
- hole diameter,
- slot width,
- plug clearance,
- left/right orientation,
- material-specific tolerance.

Every variant must have a reason and a file name reflecting the reason.

## Phase 4: preview and comparison

Render at least:

- front,
- side,
- top,
- three-quarter,
- functional detail view,
- assembled scene if multipart.

The preview check is not beauty rendering. It answers: does the object read correctly, does the part count match, are functional features visible where expected, and are there unintended repeated faces/holes/caps/limbs?

## Phase 5: iteration loop

Use the smallest loop that addresses the failed gate:

- target unclear -> update target contract,
- fit problem -> adjust functional skeleton,
- topology problem -> rebuild geometry around the failing feature,
- print problem -> adjust orientation, chamfers, supports, wall thickness,
- visual problem -> change modeling paradigm or silhouette masses,
- user taste problem -> ask for reference direction or produce 2-3 controlled alternatives.

Do not hide failed attempts. Summarize them in the report.

## File naming

Recommended folder:

`generated_vN/`

Recommended files:

- `target_contract.md`
- `generate_product_vN.py`
- `product_vN_partname_variant.stl`
- `product_vN_preview.blend`
- `product_vN_preview_front.png`
- `product_vN_preview_side.png`
- `product_vN_preview_top.png`
- `product_vN_preview_three_quarter.png`
- `check_report.md`
- `summary.json`

## Blender implementation notes

- Use millimeters and apply transforms before export.
- Prefer manifold boolean operations followed by cleanup.
- Recalculate normals outside.
- Use bevel modifiers for user-touch edges.
- Apply modifiers before final export when validation scripts require real mesh data.
- Re-import exported STL files into a clean scene for validation.
- For 3MF debug, inspect XML references before analyzing meshes.
