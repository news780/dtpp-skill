# Validation Checklist

## 1. Mesh validity

For every exported STL:

- correct unit scale in millimeters,
- dimensions match target contract,
- transforms applied,
- no unintended duplicate objects,
- connected components count is expected,
- no non-manifold edges,
- no boundary edges unless deliberately open and not used as a container,
- no degenerate faces,
- normals outward,
- no self-intersections around booleans if detectable,
- no tiny loose shells.

## 2. Functional validity

Select the relevant rows.

### Container or fluid part

- internal volume is continuous,
- fill path exists,
- drain/flow path exists,
- wall thickness is sufficient,
- no decorative cut breaks the chamber,
- support material would not be trapped inside,
- flow holes are exported in test sizes if uncertain,
- cap/plug has clearance and grip features.

### Clip, hook, or mounting part

- opening matches must-fit dimension plus clearance,
- root has fillet/radius,
- minimum wall thickness is acceptable,
- insertion direction is physically possible,
- removal is possible,
- layer orientation does not put peak stress on weak layers.

### Lid, plug, socket, or assembly

- separate parts exported separately,
- clearance defined by printer/material,
- lead-in chamfers present,
- grip/removal feature present,
- assembled preview confirms no collision,
- variant dimensions are documented.

### Load-bearing part

- load path is visible,
- edges are rounded at stress concentration zones,
- wall/rib thickness is adequate,
- infill is not the only strength mechanism,
- test print orientation is stated.

### Decorative/character product

- one clear main character or product body,
- no unintended repeated faces/features,
- silhouette matches the reference,
- styling details do not create unprintable slivers,
- visible seams and holes are intentional.

## 3. Printability

- printable orientation proposed,
- overhangs over about 45 degrees identified,
- support material can be removed,
- bridges are short enough or reinforced,
- bottom contact area is stable or brim recommended,
- minimum feature diameter meets nozzle/material limits,
- sharp internal corners are avoided when strength matters,
- small vertical pins are thick enough,
- thin walls are not below the slicer wall threshold.

## 4. 3MF and slicer file validation

If a 3MF is provided or generated:

- inspect it as zip/XML,
- list the referenced mesh assets,
- identify support blockers/modifiers separately from model geometry,
- confirm the printed body is the newly generated STL, not an old referenced STL,
- record printer/material/profile assumptions.

## 5. Final report template

```markdown
# Check Report

## Summary

- Version:
- Generated files:
- User target:
- Main assumptions:

## Dimensions

| Feature | Target | Actual | Pass |
| --- | ---: | ---: | --- |

## Mesh validation

| File | Manifold | Components | Degenerate | Normals | Pass |
| --- | --- | ---: | ---: | --- | --- |

## Functional validation

| Feature | Method | Result | Pass |
| --- | --- | --- | --- |

## Print recommendation

- Printer:
- Material:
- Nozzle:
- Layer height:
- Orientation:
- Supports:
- First test variant:

## Remaining physical tests

1.
```
