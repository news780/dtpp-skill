# Fluid-container validation

Use this reference for reservoirs, drip irrigators, bottles, nozzles, humidifiers, or any part that must intentionally retain and release liquid.

## Non-negotiable rule

`manifold=True` or `basic_pass=true` proves only a limited mesh condition. It does **not** prove that a part holds water. Do not call a fluid product functionally validated until its physical leak and flow tests pass.

## Target contract additions

Record these requirements before modeling:

| Item | Required decision | Evidence or test |
| --- | --- | --- |
| Reservoir | One continuous liquid chamber or an explicitly documented multi-chamber system | Section/cutaway and CAD inspection |
| Fill path | Fill port size, cap/plug type, user access | Fit and filling test |
| Drain path | Outlet/nozzle position and nominal diameter | Flow direction and drip test |
| Vent path | Vent location and whether it is intentional | Continuous flow without vacuum lock |
| Walls | Minimum nominal wall thickness and material | Wall-thickness inspection |
| Internal support | Whether support can be removed from every cavity | Orientation and removal plan |
| Capacity | Target usable volume | Fill-to-line measurement |

## CAD and mesh checks

1. Model the reservoir as a deliberately bounded volume; decorative segments must not cut it.
2. Check every connected component. A stray shell or tunnel is a design failure unless documented as an intentional separate part.
3. Use `validate_stl_blender.py -- --product-rules fluid-container body.stl`. Its `basic_pass` result is a mesh result only.
4. If intended fill/drain openings create boundary edges, document them in the rule config and check that they are the expected openings, not accidental leaks.
5. Inspect the actual internal passage, not only the exterior silhouette. Record minimum wall thickness, chamber volume, and every liquid/air path in `design_manifest.json`.

Example rules configuration:

```json
{
  "product_rules": {
    "fluid-container": {
      "expected_components": 1,
      "allow_boundary_edges": true
    }
  }
}
```

## Slicer check

Before printing, generate `3mf_manifest.json` and confirm the 3MF points to the intended STL filename and SHA-256. State the print orientation, support strategy, and whether supports can be removed from all wetted cavities.

## Physical test protocol

Advance evidence levels only with recorded observations:

1. `first_print_passed`: inspect the printed part, measure fit-critical dimensions, and assemble cap/plug/nozzle.
2. Leak test: fill to the specified line, seal it as intended, record start/end mass or volume, elapsed time, and every wet surface. Define the acceptance threshold in the target contract.
3. Drip-rate test: use the stated liquid, head height, hole diameter, and duration. Record volume or mass released over time and whether venting remains stable.
4. Repeat the leak/flow test after the intended assembly cycles or load condition when relevant.
5. Set `function_physically_validated` only when every acceptance criterion passes.

## Report rows

Add these rows to `check_report.md`:

| Feature | Method | Measured result | Evidence level | Pass |
| --- | --- | --- | --- | --- |
| Continuous chamber | CAD section inspection | | `cad_mesh_passed` | |
| Minimum wall thickness | Thickness measurement | | `cad_mesh_passed` | |
| 3MF current-STL match | SHA-256 manifest comparison | | `slicer_checked` | |
| Leak resistance | Timed fill test | | `function_physically_validated` | |
| Drip rate | Mass/volume over time | | `function_physically_validated` | |
