# Mounted flex and minimal synthesis findings

Planning decisions only. Four candidate entries / eleven model or route sections reviewed. Evidence: [source and image hashes](mounted-flex-audit.json), [native boards and observations](next-native/audit.json). Every selected press child was opened alone and in its actual parent. Minimal examples each contain one selected root; embedded posed meshes are dependencies.

## Pneumatic press: keep and correct

Prefer `examples/flex/pneumatic-press/named-review/model.mpd` and its named authoring source as the canonical mounted pneumatic starter. Consolidate the original compatibility representation; it is not a second lesson. Correct **C-frame** to **two-column portal frame**. The base is a plate deck, and controls are a logical grouping of separately mounted pump and valve.

Existing evidence records 41 physical placements (38 rigid, three hoses), six seated/coaxial sleeves, 16 LDU sleeves, 22 LDU leads, minimum bend radius 16.9 against 15, and route separation 11.2 against 10 outside 30 LDU endpoint zones. These are historical checks with their original scope, not measurements rerun in this audit. Preserve the named registry's rigid group plus three hose groups and explain why this differs from the older incomplete registry. Static pose only: no load, pressure, stock-length or travel certification.

| Section | Visual description and correction |
|---|---|
| `press.ldr` | Mounted static pump-valve-cylinder press on plate base; two-column portal frame, not documented C-frame. Three distinct hoses connect actual fittings; no pressure or loaded-stroke claim. |
| `press-bench.ldr` | Broad bonded studded plate base beneath all mounts; bench name does not imply a raised table. |
| `press-frame.ldr` | Two brick columns and Technic crossbeam form closed-top portal with a central anvil. Correct C-frame wording. |
| `press-ram.ldr` | Extended cylinder, upper pin and lower pressing shoe. Parent places it between columns over anvil; loaded gap and travel unproven. |
| `press-controls.ldr` | Separated pump and valve share a logical section; their physical connection is through base mounts and the parent supply hose, not a rigid control module. |
| `route-e8c880158836619b.ldr` | Short black curved supply hose between pump and valve; both end sleeves visible alone and in actual parent. |
| `route-8a9c27749e252068.ldr` | Red route rises from valve to upper cylinder port, with curved upper departure. |
| `route-8869bb380eddd979.ldr` | Blue route rises from valve to lower cylinder port; distinct route below red endpoint. |

## Minimal hose, band and chain: keep as tutorials

| Source | Observed result | Intended use |
|---|---|---|
| `examples/flex/hose.ldr` | Red S-shaped hose with two sleeves; no mounted fittings | Authoring/synthesis/BOM smoke, one physical posed hose |
| `examples/flex/band.ldr` | Red loop around two grey pulleys; no bearing frame | Loop syntax and BOM, three physical placements |
| `examples/flex/chain.ldr` | Yellow links around two grey gears; no shaft retention | Link synthesis and BOM, 24 links plus two gears |

Their source, synthesized asset and opened image hashes match the existing manifests. Contact-skipped reports do not prove connectivity. For actual mounted construction, route retrieval to the pneumatic press or supported retained-chain-drive. Avoid recommending the unsupported minimal wraps as complete mechanisms.

## Already reviewed: reuse evidence

`workshop-machine`, `mounted-frame-named` and `retained-chain-drive` were fully reviewed in [structural findings](structural-findings.md), including all eleven workshop sections/routes. Their current sources still match that audit. No rerender or additional coverage count is needed. Workshop is a static integration example; transport, full stroke and travel-dependent hose slack remain untested.

## Migration action

Keep one short flex guide: choose family → mount hardware → establish endpoints/tangents → route → validate scoped geometry → inspect isolated route and assembled context. Link tutorials for syntax and mounted packages for construction. Keep LSynth's raw corpus and constraint-lab fixtures outside default construction retrieval; their distinct dispositions are in the existing findings.
