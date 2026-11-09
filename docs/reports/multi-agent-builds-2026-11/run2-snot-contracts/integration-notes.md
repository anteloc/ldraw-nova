# Integration notes — run 2 (SNOT + submodel contracts)

## r1 — 20:39–20:47 (all five modules final)
Scripted (1:47): build checks_passed, 1379 parts; **contract_check 49/49 PASS in scene**; contacts main group
1339/1379 (97.1 %); the 40 outside are all clipped glass (blind spots). No cross-module overlap errors.
Bounds Z -336 = SNOT kerb face (allowed by contract to Z -17).
Images opened: r1/whole/panels 01-home, 02-front, 03-back, 04-right; r1/cut-front/panels/03.

| # | module / submodel | finding | class |
|---|---|---|---|
| I1 | ground-walls / ground-rear | rear wall shows rows of bare side studs (unused 30414/11211 courses) | worker-catchable, NOT self-reported |
| I2 | floor2-bay / floor2-walls | bay glazing shows solid red wall right behind it — wall behind the bay not opened | worker-catchable, NOT self-reported |
| I3 | floor3-windows / floor3-walls | front flanking windows show solid red wall behind the panes | worker-catchable, partly self-reported ("front window-units" open) |
| I4 | floor3-cornice | front cornice is only stubs at the corners + a thin line; not a band | self-reported, left open |
| I5 | ground-awning | flat striped valance, not a sloped awning | self-reported, left open (envelope made a canopy hard → partly my contract) |
| I6 | ground-sign | reads as a row of yellow dots, not a sign | self-reported, left open (1-row panel limit) |
| I7 | street-kerb | top studs of the kerb bricks exposed | self-reported, left open |
| I8 | street-garden | back fence = one plain brown wall | worker-catchable (aesthetic), not reported |
| I9 | street-tree/lamp vs ground | trees at X ±13 hide the SNOT rustication piers; lamps in front of outer glazing | cross-module, **my contract** (allowed zones) |
Structural / contract defects found at integration: **0** (run 1 r1: 4 structural classes).
→ D1 repairs: H1 (I1, I5, I6), H2 (I2), H3 (I3, I4), H5 (I7, I8, I9 lamps/trees). H4 roof: no action.
- 20:46 H3 correction on I3: the wall openings existed; the red behind the panes was the room's *back* wall
  seen straight through the glass. My diagnosis "wall not opened" was wrong; the visual defect (glass reads
  as solid red) was real and was fixed by putting furniture behind the windows. I2 (floor2 bay) may be the same.

## r2 — 23:16–23:19 (after D1)
Build checks_passed, 1427 parts; contract 49/49 PASS; main group 1391/1427 (97.5 %), all 36 outside = glass.
Images opened: r2/whole/panels 01-home, 02-front, 03-back.
Fixed and verified: I1 (rear studs gone), I2 (bay shows interior plants), I3 (furniture behind floor3 windows),
I4 (continuous 2-tone cornice), I5 (scalloped striped awning, seated), I6 (word-block sign, no lettering), I7 (kerb
capped), I8 (tan garden wall + gate), I9 (trees at kerb line; lamps at X ±6).
Remaining (accepted, visual only): sign has no letters (1 stud row); awning scalloped; tree trunks heavy;
lamps now in front of inner glazing; roof corner urns are tall white stacks; plain side walls.
Decision: no D2 round — remaining items are taste, not defects.
