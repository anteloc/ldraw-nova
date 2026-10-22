# LSynth integration assessment — 2026-10-22

The Python port in `../lsynth-nova` is useful for agent-authored flexible geometry. Its README, configuration, CLI, synthesis code, bundled parts and 26 constraint examples supply enough information for a first integration. No additional reference models were needed.

The implementation adds `flex types` and `flex build`, optional installation through `setup.sh --with-lsynth`, three small sources under `examples/flex/`, and an [agent guide](../agent/flexible-parts.md). It calls the installed port's CLI with the bundled configuration. Existing parsing, embedded DAT support, plan assets, source validation, rendering and BOM comparison remain the foundations.

## Physical boundaries

LSynth stretches geometry segments to draw continuous material. Placing those segments directly in an assembly would violate the project's rigid-part rules and inflate its BOM. The adapter packages each continuous object as a classified embedded DAT, with a rigid placement in the assembly. Real chain/tread links remain separate physical placements. Visible wheel constraints remain physical parts; hose path markers are removed from the assembly.

Required LSynth geometry is embedded under unique names, including transitive dependencies. Source authors and licence notices are preserved. Installed library files and the sibling source tree were not edited. The manifest records source/configuration hashes, version, embedded source hashes, block identities, product hints and compatibility changes. Posed IDs do not assert a retail part number or manufactured length.

## Validation evidence

- Upstream suite: **40 passed**, including all 26 comparisons with double-precision C reference output.
- Project suite: **304 passed**. After the final ambiguity guard and filename-with-spaces coverage, the focused adapter suite passed **11 tests**. These cover physical counts, deterministic regeneration, dependency/credit preservation, legacy header repairs, nested MPDs and plan assets, unchanged previous output on failure, warnings despite successful subprocess exit, optional-dependency reporting, and rejection of nonrigid complete parts or conflicting embedded LSynth definitions.
- `setup.sh --with-lsynth`, `doctor`, `flex types`, shell syntax and whitespace checks succeeded.
- All **26 upstream constraint files** were tried through the adapter. **12** passed full assembly-source validation. This is a source-validation sweep, not 26 geometry or visual approvals. Results are in `output/lsynth-assessment/results.json` in the working checkout.

The 14 rejected legacy scenes have explicit reasons: three missing-part cases; two nonrigid-placement cases; one scene with both internal-part and nonrigid-placement errors; one unresolved inherited-colour case; three SYNTH blocks requiring explicit colours; and four scenes with LSynth warnings about unsolvable tangent arrangements. For example, the full rubber-band sample includes a bad pulley arrangement, while the small two-pulley band generates and reviews successfully. Matching the historical C output does not establish a valid assembly.

Four models completed source and geometry checks, LeoCAD rendering and exact Python/LeoCAD BOM comparison:

| Model | Physical placements | Review directory |
|---|---:|---|
| Three-marker hose | 1 | `output/flex/hose-review/` |
| Band and two pulleys | 3 | `output/flex/band-review/` |
| Chain and two gears | 26 | `output/flex/chain-review/` |
| Upstream ELECTRIC_CABLE scene | 14 | `output/lsynth-assessment/electric-review/` |

Home and top images were rendered. The **home image from each of these four directories was opened and inspected**: the hose is continuous with visible segment shading; the band has straight runs and curved pulley wraps; the chain shows individual links around its gears; the electric cable winds around the transparent support toward the lamp assembly. The first three are isolated geometry studies, not supported mechanisms. The manifests bind previews and BOMs to exact model bytes.

Contacts were deliberately skipped, and reviews retain that coverage warning. Posed geometry has no verified connector model. The band retains legacy alias/empty-meta warnings and invalid mirrored connector frames in the supplied `4185a.dat` shadow metadata; that wheel's affected connector entries cannot establish connectivity. These are not physical approvals. Material collision review, support, endpoint seating, stock length, bend radius, tension, elasticity and mechanical engagement remain unproven.

## Compatibility findings

Tested against lsynth-nova **3.1.0** and its bundled configuration:

- Some successful CLI exits include warnings or incomplete geometry. The adapter treats warnings as failures and requires generated content in every block.
- Reusing synthesized output can lose hidden hose constraints. Only the unsynthesized source is accepted for regeneration.
- The port reads `HOSE_RES` values from token index 4 instead of 3 and `BAND_RES` from index 4 instead of 3. The adapter rejects custom resolution and uses the defaults. The sibling implementation was left unchanged.
- LS22's author header is Latin-1; its embedded copy is transcoded to UTF-8. LS50/LS51 contain `BFC CERTIFY INVERTNEXT`; embedded copies use `BFC INVERTNEXT`. Each change is recorded, with original hashes and credits.
- Four-decimal matrix serialization can exceed the project's rigid-rotation tolerance. Only generated rigid links are eligible for a recorded projection to a proper rotation, bounded to 0.00005 change per coefficient. Actual scale, shear, reflections and source-placement defects remain validation errors. Continuous geometry is never normalized.

The integration supplies usable geometry and honest review coverage. It does not attempt a material simulator or certify that an arbitrary synthesized pose can be built from a particular manufactured part.
