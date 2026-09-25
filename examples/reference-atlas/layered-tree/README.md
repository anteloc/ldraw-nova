# Layered woodland tree

Round trunk courses and rotated foliage layers create a broad canopy with irregular edges.

Source: `4208-1.mpd` / `4208 - tree.ldr`. Scale: minifigure.

The green base is four studs square, but foliage spreads about 11.6 studs. Reserve that canopy envelope and adjust layer angles instead of simply scaling the source. Connection analysis leaves 5 optimistic groups; inspect those unresolved interfaces during adaptation.

The `source_origin` anchor is a positioning frame, not a claimed mechanical connector. The source retains its original coordinates and palette. Read the measured bounds, parent placements and connection coverage in [card.json](card.json) before adapting it.

[Editable plan](scene.plan.json) · [Source MPD](source.mpd) · [Preview](renders/home.png) · [Attribution and repairs](extraction.json).

Run `./ldraw-agent build PATH/scene.plan.json --output output/example.mpd`, then inspect the combined assembly and review its renders.
