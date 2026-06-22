# Intake Schema

Use this when a product image or design board is the primary input.

## Image parsing checklist

Record the following as a table with columns: item, evidence, modeling implication, confidence, needs user confirmation.

### Visual product identity

- Main object type
- Front/back/top/side orientation
- Overall silhouette
- Character or styling language
- Surface finish: matte, glossy, textured, translucent, fabric-like
- Color/material assumptions
- Proportional hierarchy: largest mass, secondary masses, small details
- Symmetry or asymmetry
- Visual red lines: what the object must not resemble

### Functional anatomy

- User grip/touch areas
- Mounting interface: hook, slot, clip, magnet, screw, strap, weight, stand
- Storage or containment: water, oil, fragrance, soil, electronics, candle, incense, tools
- Flow path: air, water, cable, light, heat, smoke, liquid
- Moving or removable parts: cap, plug, lid, drawer, hinge, clip, insert
- Replaceable consumables
- Safety-critical surfaces: heat, water, food, electricity, pet/child contact

### Dimensional data

Rank dimension evidence in this order:

1. Explicit callouts in the image.
2. User-provided measurements.
3. Must-fit object dimensions.
4. Standard hardware sizes.
5. Proportional estimates from the image.

Never bury inferred dimensions. Mark them clearly.

### Print assumptions

- Printer type and nozzle
- Material
- Layer height
- Tolerance class
- Part count
- Need for supports
- Support-removal access
- Target orientation
- Minimum feature size
- Wall thickness
- Assembly clearance

### Target contract template

```markdown
# Target Contract

## Product

- Name:
- Primary function:
- Use scenario:
- Reference image(s):

## Known dimensions

| Feature | Target | Source | Confidence |
| --- | ---: | --- | --- |

## Functional features

| Feature | Requirement | Validation method |
| --- | --- | --- |

## Visual requirements

| Requirement | Evidence | Red line |
| --- | --- | --- |

## Print requirements

| Requirement | Default | User-confirmed? |
| --- | --- | --- |

## Variants

| Variant | Difference | Reason |
| --- | --- | --- |

## Assumptions needing confirmation

1.

## Acceptance criteria

1.
```
