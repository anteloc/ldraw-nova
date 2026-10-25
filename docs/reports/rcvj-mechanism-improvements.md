# RCVJ mechanism and catalog improvements — 2026-10-25

The work spans `ldraw-nova` (catalog, construction guidance and preserved study)
and `ldraw-mecha` (motion checks, helpers and regression tooling). Neither gains
a runtime dependency on the sibling checkout.

## What changed

- [RCVJ study](../../examples/technic-studies/rcvj/README.md): original supplied
  bytes retained, 127 designer-model occurrences reconciled, 12 interfaces
  measured and 22 executable checks authored. The old animation violates 14
  checks at each of three nonzero inputs; the CLI check returns exit 1.
- [Advanced construction guidance](../agent/advanced-mechanisms.md): occupied
  pin/axle sections, rigid groups, carriers, differential angle bisection,
  Cardan phasing, alias transforms and independent geometric checks.
- [Mechanism catalog](../agent/technic-catalog.md): all 1,352 supplied Technic
  assignments, including duplicate sanitized names, plus installed mechanical
  name matches and dated LDraw tracker records. The snapshot has 5,643 discovery
  references; availability, aliases, shortcuts and unreviewed motion are explicit.
  Supplied categories and the installed library were not modified.
- Mecha adds `rigid`, `coaxial` and `rotation` checks, finite bearing overlap,
  cross-body coverage, `--require-constrained` preflight and carrier/differential/
  phased double-Cardan signal helpers. Blender evaluates invariants from actual
  scene matrices. Existing plans and default CLI behaviour remain compatible.
- `3648a` is now a supported Mecha spur profile. Crown geometry remains a
  separate review case; metadata inference is not promoted to verified motion.

## Verification

- Nova: **431 tests passed**; the final catalog fallback refinement additionally
  passes all four catalog tests. CLI exports contain all selected rows despite
  display limits, and RCVJ reports all 34 references installed.
- Mecha: **475 tests passed**. New tests exercise bad axes, independently
  rotating keyed gears, wrong pivots, axial escape, moving carriers, unequal
  differential inputs, multi-turn Cardan phases and actual RCVJ frames.
- Blender **5.2.2 LTS**: nonzero mixed poses, moved/rotated roots, intentional
  scene corruption, save/reopen, rebuild without leaks and source restoration
  pass. A separate `rig --require-constrained --reopen` run passes in fresh
  processes. Reproduction commands are in Mecha's `docs/rcvj.md`.
- The original model passes Nova file/geometry checks with recorded warnings.
  Its home/front/top source views were opened. Byte hashes match the preserved
  copy. New/updated documentation links and whitespace checks pass.

## Limits

The full articulated RCVJ rig remains unresolved. Both carrier assignments,
crown contacts and the remaining spatial link closures must be solved before
the workbook can become ready. The checks are necessary local invariants;
constraint participation, ideal double-Cardan equations and transform agreement
do not establish complete mobility, clearance or physical buildability.

Catalog completeness is bounded by the supplied table, installed library and
explicit watchlist. Supplementary name matches favour discovery and can include
decorative/printed candidates; neither those tags nor SNAP freedoms establish
function. The model and its derived evidence retain the designer's CC BY-NC-SA
licence, separately from toolkit code and LDraw part licences.
