# Mechanism authoring and animation workflow — 2026-10-25

The agent path now starts with a small original
[supported gear drive](../../examples/technic-studies/gear-drive/README.md),
then extends measured connections. Construction and motion keep their ordinary
JSON formats. The broad [parts catalog](../agent/technic-catalog.md), finite
interfaces and [mechanism guidance](../agent/advanced-mechanisms.md) remain
available independently of any imported model study.

General lessons are executable regressions in Mecha: a gear must carry its
keyed axle; the occupied hole defines the pivot; opposed coaxial gears are not
an external pair; mixed pin/axle sections have different freedoms; carriers
compose with relative shaft motion; and nonzero/asymmetric inputs are required.
Differential and Cardan helpers keep their stated geometric assumptions.

Mecha's new `transmission.port`, `shaft` and `mesh` helpers generate existing
plan fields and reject source fit errors, duplicate ownership, unsupported spur
profiles and competing follower drives. They support prepared mechanism views
and leave edited plans as drafts for final checking. They do not infer physical
connections or solve arbitrary closed loops.

Blender preparation and reopening now include off-grid inputs and evaluated
timeline checks with animation active. A generic adversarial fixture confirms
that a displaced keyed gear fails those checks and that diagnostics preserve
the action and scene time. Background rebuild and restoration tests also pass.

Final full-suite results: **431 Nova tests** and **487 Mecha tests** passed.
The original starter reproduces byte-for-byte in both repositories; the saved
motion plan exactly matches the current recipe. New guide/example links resolve.

See the starter's [validation record](../../examples/technic-studies/gear-drive/validation.md)
for source identity, BOM/visual review, 25 mechanical checks, saved animation,
finite sampling and collision-diagnostic limits. The broad catalog remains a
discovery inventory; its unknown motion profiles are deliberately explicit.
