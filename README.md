# DTPP Skill

`design-to-printable-product-modeling` is a Codex / agent skill for turning product design images into functional 3D-printable models.

Short alias: `dtpp`。大小写不敏感，`dtpp`、`DTPP`、`Dtpp`、`dTpP` 都应触发同一个 skill。

## What it does

The skill guides an agent through a product-development loop:

1. Read the uploaded product image or concept.
2. Create a measurable `target_contract.md`.
3. Separate visual styling from functional geometry.
4. Build a scripted Blender model rather than an opaque hand-edited scene.
5. Export versioned STL / BLEND outputs.
6. Render preview images from multiple views.
7. Re-import and validate geometry.
8. Iterate only on failed criteria until the model is ready for slicing or asks for missing critical constraints.

## Use cases

- Functional plant accessories
- Drippers and water reservoirs
- Clips, hooks, holders, caps, and small mechanisms
- Lamp shades and diffuser shells
- Incense holders
- Pet products
- Packaging and structural prototypes
- Small printable product shells

## Install

Copy this folder into your global Codex skills directory:

```text
C:\Users\Administrator\.codex\skills\design-to-printable-product-modeling
```

Or keep the same folder structure in any project-level skills directory supported by your agent runtime.

## Structure

```text
dtpp-skill/
├── README.md
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── case-caterpillar-dripper.md
│   ├── intake-schema.md
│   ├── modeling-playbook.md
│   ├── prompt-templates.md
│   └── validation-checklist.md
└── scripts/
    ├── inspect_3mf.py
    └── validate_stl_blender.py
```

## Example trigger

```text
dtpp 目标模式。按照这张产品图，自己迭代建模，最后输出可用于 FDM 打印的 STL、预览图和验证报告。
```

## Core rule

Do not mark a model as printable only because it looks correct. Functional 3D-printed products need explicit geometry validation, printability validation, and feature-specific validation.
