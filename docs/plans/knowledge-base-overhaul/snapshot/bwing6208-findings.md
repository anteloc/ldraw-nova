# 6208 B-wing construction studies: visual audit

Planning evidence, 2026-11-01. Reviewed 13 selected studies: 11 completed source assemblies and 2 visibility cutaways. Also inspected the nested rubber-band definition alone and in its actual parent. All 22 authored views have matching hashes and were opened through seven sheets. Fresh context views for every study and three band views were inspected; all 15 context/dependency render jobs completed successfully. Original and extracted source hashes match their authored metadata.

| Study | Visual finding | Planned treatment |
|---|---|---|
| airframe | Hub, offset cockpit, long blade and two smaller wings make a distinct asymmetric ship. Set context adds a dock and two pilots. | Retain airframe composition; dock and pilots are context, not additional curated lessons. Distinguish set display frame from local airframe frame. |
| center | Compact structural hub receives independent front, skins, wing carrier and four-nozzle cluster. | Retain assembly hierarchy and attachment planning, with geometry verification deferred. |
| cockpit | Transparent canopy is separate from brown slope; controls, tub, rear dome and axle core are visible. Parent rotates the whole pod. | Retain local-frame cockpit composition, without claiming tested rotation or clearance. |
| cockpit-arm | Narrow plate-bonded Technic support sits between hub and offset cockpit under its shaped cover. | Retain support-before-skin lesson. |
| exhaust | Four round nozzle stacks form a two-by-two cluster; central shaft extends into the hub. | Retain nozzle repetition; correct stale twin-exhaust prose on every generated surface. Exclude mechanism operation from the lesson. |
| front | Oblique hinged armour surrounds perpendicular bracket construction. | Retain distinction between bracket SNOT and angled hinge surfaces. |
| front-core | Sixteen selected placements expose four opposed 44728 brackets and a 2436a bracket. Fresh line-highlight view locates the selection in the full front. | Retain explicitly as a visibility cutaway, not a source instruction step or independently validated module. |
| front-fins | Nine selected placements show side-stud bricks, tiled face and four fins. | Retain a second visibility cutaway with exact source-line provenance. |
| side-shell | Two opposed curved skins connect through round axlehole plates and Technic supports; parent rotation changes where the skins face. | Retain System surface on Technic fittings; do not infer world-facing direction from the section name. |
| wing-1 | Small handed wedge wing with root hinge and tip barrel; parent places it on one side of hub. | Retain actual handed parts and root interface. |
| wing-2 | Long narrow blade with reinforced root and triple weapon cluster; distinct mass from the two small wings. | Retain thin-wing silhouette lesson. |
| wing-3 | Opposite small wing uses opposite-handed wedges and its own parent orientation. | Retain paired construction; do not introduce reflected matrices. |
| wing-root | Narrow carrier shows three Technic pins and four locking hinge interfaces on the hub side. | Retain pin-supported hinge carrier; static image does not prove range of motion. |
| nested rubber band | Asymmetric closed loop is located within the centre body. Source contains LDCad path metadata and generated fallback mesh. | Preserve dependency and attribution. Do not present it as a verified tensioned mechanism or as an LSynth recipe. |

Preserve the existing teaching guide's useful distinctions: this is set 6208, not the atlas's 75050; camera front/back labels are not vehicle-relative; each source assembly has one nonempty state; the study order is not a source build sequence. Existing corrected teaching text should replace contradictory generated descriptions, while attributed original source stays unchanged.

No new geometry, collision, connectivity, elastic-tension or motion verification is claimed. The extraction can be a useful construction reference without being a certified reusable assembly.

Evidence: [individual records](bwing6208-audit.json), bwing6208-01..07 isolated sheets, bwing6208-contexts-01..05 parent sheets, and the rubberband render directories. The selected coverage is 14 sections/selections: 11 assemblies, 2 cutaways and 1 nested dependency. Repeated nested appearances across extracted study packages are not counted again.
