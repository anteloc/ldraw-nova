# Optional voxel sculpture example

From the toolkit root, with the `sculpture` extra installed and `LDRAW_DIR` set:

```sh
.venv/bin/python examples/sculpture/generate.py
./ldraw-agent sculpture output/sculpture-example/owl.voxels.json --output output/sculpture-example/owl.mpd --title "Owl sculpture" --report output/sculpture-example/checks.json
```

This small owl bust demonstrates coloured voxels, a connected display base and
ordinary build steps. Continue with the usual rendering and visual review; the
report checks connections and instruction order, not force-based physical stability.
