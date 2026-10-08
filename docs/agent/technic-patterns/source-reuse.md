# Reusing Technic evidence without losing the construction

These lessons come from the [Mecha studies](../../../examples/technic-studies/README.md)
and its 10265 discovery audit. Apply them through Nova's existing
[discovery](../reference-discovery.md), [build pages](../build-manuals.md),
[snapping](../snapping.md) and [mechanism](../mechanisms.md) tools.

## Prefer the actual assembly over its label

Names, family categories and search ranks shortlist references. Expand the
selected section's physical inventory and read its source before assigning
mechanical roles. The W16's V8 label, double-bevel gears used on parallel axes,
and cam-driven Defender engine are concrete counterexamples to name-based
inference. Embedded DATs with numeric-only descriptions may still be important
gears; preserve their geometry and inspect their provenance/variant.

A whole shock DAT and a split rod/cylinder/spring assembly have different
physical boundaries. Do not count its internal primitives as loose parts, replace
an embedded definition with a guessed current part, or silently change the BOM.
Categories and bounding-box snapshots help select candidates; measured geometry
and connector frames locate real pivots and mounting interfaces.

## Keep selection, frame and occurrence identity together

Record original model hash, exact `FILE` section, selected physical occurrence
paths, composed transforms and effective colours. Mecha's hierarchical paths
such as `84/16` are not Nova's flattened `--occurrence` indices. Obtain current
Nova indices with `inspect`/`connectors` for the same selection before snapping
or writing a structural contract.

Extracting a section changes its frame relative to the outer scene. A flat
world-coordinate extract and a section-local extract therefore need different
placement transforms. Keep the extraction manifest and any old-to-new identity
map; do not copy occurrence IDs across them by appearance or filename.
If changing frames, transform axes and anchors as well as parts.

Use `extract`/`mechanism prepare` to preserve dependency sections, embedded DATs,
author and licence headers. Record permitted rotation/BFC repairs to the copy.
The source models, supplied categories and part library remain unchanged.

## A visible support may still be an incomplete interface

List fixed supports, moving members, input/output parts and omitted neighbours.
The suspension extract has floating tie-rod boundary pins; the W16 preview
hides its fixed heads and frame; the local rack and worm examples need parent
parts. Add the actual missing holders, drive parts or retained stack before
treating a study as a new self-contained model.

Trace keyed axle holes separately from round bearings and loose clutch gears.
Coaxial proximity or a connector contact does not mean rigid coupling, torque
transfer or axial retention. MPD sections describe source organization, not
rigid groups. Check bushes, axle stops and insertion access on both sides of
each new stack using the [structural workflow](../technic.md) where supported.

## Missing evidence is a reason to inspect

In the Mustang audit, tiny rounded source rotations suppressed many connector
results: raw analysis found 29 contacts and axle-hole evidence for 0/25 straight
axles; Mecha's bounded analysis correction found 921 contacts and 25/25 axles.
Those figures describe its historical analysis policy. Nova does not acquire
that policy by importing this guide.

When a plausible drivetrain appears disconnected, inspect transform validity,
embedded parts, shadow support, selection size and skipped-contact diagnostics.
Use Nova's recorded extraction normalization for permitted rounded rotations;
never silently normalize real scale/shear or introduce reflected physical parts.
Several contact records may describe one joint. Neither a dense graph nor a
zero-error report establishes complete mechanical coverage.

The Mustang's worm/crank route ends at a possible surface contact with beams.
Record that unresolved coupling rather than inventing a connector or deleting
the mechanism from the design notes. Distinguish an intentionally fixed member,
an intended moving one, and an unknown role.

## Keep observation and qualification together

For each reused core, retain: what was directly counted/measured, what the source
report checked, what was inferred or approximated, and what changes in this
model. A source sweep is not a new-model test; a rendered cutaway is not proof
of assembly order; sampled surface crossings do not test bore containment.

Mecha-specific spring scaling, hub projection, fixed boundary points, selector
cam profiles, prescribed paddle timing and added reconstruction gears must not
quietly become Nova construction rules. Preserve the useful physical pattern
and its limits. Continue the normal generation/review workflow with analytical
mechanism verification deferred.
