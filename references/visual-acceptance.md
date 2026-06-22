# Visual acceptance table

Use this table after rendering the front, side, top, three-quarter, and function-focused views. It prevents a technically plausible shell from drifting away from the reference product.

## Inputs

- Reference image or design board:
- Model version:
- Render paths:
- Reviewer:

## Acceptance table

| Reference requirement | Rendered evidence | Visual red line | Pass/Fail | Correction layer |
| --- | --- | --- | --- | --- |
| Main silhouette and proportion | | Must read as the intended product at thumbnail size | | Functional skeleton / shell |
| Part count and assembly relation | | No extra caps, limbs, faces, or duplicate parts | | Shell / assembly |
| Character or product identity | | Must not resemble a tube, placeholder, or unrelated object | | Modeling paradigm |
| Visible functional features | | Fill port, hook, nozzle, clip, or interface must be visible where expected | | Functional shell |
| Surface segmentation and seams | | No deep decorative cut through functional volume | | Detail layer |
| Material and finish cues | | No accidental faceting, slivers, or visual noise | | Normals / bevels |
| Function-focused view | | Feature can be understood and operated from the rendering | | Camera / geometry |

## Decision

- If any red line fails, identify the failed modeling paradigm before changing dimensions.
- Change the smallest responsible layer: target contract, functional skeleton, shell, detail, or render setup.
- Attach the completed table to `check_report.md` or include it in the version folder.
