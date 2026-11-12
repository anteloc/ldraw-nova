# Spaceship compatibility index

Current lessons live in semantic packages. [Browse the generated index](index.html), or use:

```sh
./ldraw-agent examples --family spaceship --limit 8
./ldraw-agent knowledge search "hull attachment" --family spaceship --limit 6
./ldraw-agent knowledge show spaceship:KEY
```

The package README owns the lesson, scope, corrected descriptions and limits. The generated `catalog.json` retains explicit non-default scopes for compatibility; the gallery shows default-eligible lessons. Old aliases continue to resolve. Retired, held, diagnostic and inspiration sources require deliberate selection and cannot bypass export checks.

Legacy selection files and atlas generators are historical preparation inputs. Use the current package's editable plan/generator to reproduce a lesson. Legacy source preparation goes to a separate `--outdir` and does not admit its output. To refresh browsing from current metadata:

```sh
.venv/bin/python -c "from ldraw_tools.knowledge import write_compat_catalog; write_compat_catalog('spaceship', 'examples/spaceship-atlas')"
```

## Details

Use `examples --details` with this family, or a role-specific knowledge query.

## Select principles for the new brief

No spacecraft is a default template. Define scale, silhouette and proportions,
then compare at least three suitable source models when available. Record the
principle borrowed from each, its intended role and evidence limits. Keep the
new outline grounded in the user's brief. A narrow named-ship study can focus
on its specific source.

Spaceship searches and this gallery interleave sources; sibling sections no
longer occupy the whole first page. Search results preserve scores and original
retrieval ranks. Use `--diversify none` for a focused comparison of sibling details.
The normal family list includes modules; `--details` narrows it to modules.

The [spacecraft guide](../../docs/agent/guides/design-models.md#compare-construction-sources-before-selecting-one)
compares brackets and curved skins, hinged shells, clip-mounted wings, offset
cockpits, concentric nacelles and small hulls. The 6208 studies retain their deferred
geometry/motion checks. Cross-listed submodel lessons retain their original
aliases, evidence and export gates. None of these search improvements certifies
new geometry or motion.
