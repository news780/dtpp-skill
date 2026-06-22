# Case Reference: Caterpillar Planter Dripper

Use this only as a worked example. Do not force every product into this structure.

## Target image interpretation

The product board shows a cute caterpillar planter dripper:

- green caterpillar character hanging over a pot rim,
- overall size around 103 mm long and 43 mm high,
- rounded head, two antennae, black eyes, short legs,
- body segmented as shallow rounded lobes,
- inverted U hook slot over the pot rim,
- top fill port with removable cap/plug,
- internal continuous reservoir shown in a cutaway,
- bottom drip nozzle close to the soil,
- use steps: open fill port, add water, hang on pot edge.

## Functional requirements extracted from the case

- Continuous water chamber; segmentation must not cut the chamber.
- About 2.8 mm wall thickness.
- Fill port around 9 mm.
- Separate vented plug.
- Short bottom drip nozzle.
- 0.8 mm and 1.0 mm drip-hole test variants.
- 12 mm and 15 mm pot-rim slot variants with clearance.
- Support-free or support-light internal reservoir.
- STL exports must be manifold, normals outward, and free of loose fragments.

## Lessons from the failed iteration

A mesh can be watertight in the narrow manifold sense and still be functionally wrong. In this case, a body STL had no non-manifold edges or boundary edges, but it had multiple connected components and high genus, consistent with tunnels or through-holes. The printed object could not hold water because the topology encoded hollow waist passages.

Therefore, for reservoir products, validation must include:

- connected components,
- Euler/genus or equivalent tunnel detection,
- actual fluid chamber continuity,
- inspection of 3MF references to ensure the slicer file uses the corrected STL,
- separation of support blockers from real geometry fixes.

## Visual lessons

The first functional version passed basic checks but looked like several parallel corrugated tubes. The correct visual direction was not more tube tweaking. It required changing the modeling paradigm:

- one clear character,
- one head,
- two antennae only,
- shallow body segmentation,
- rounded toy-like shell,
- hidden hook slot integrated into the belly,
- one fill port, not multiple caps from preview variants.

## Generic transfer

For any functional consumer product, split the task into:

1. Functional skeleton.
2. Product shell.
3. Fit-critical interfaces.
4. Print validation.
5. Visual acceptance.

The caterpillar is only one example. The reusable method is the gate-based loop.
