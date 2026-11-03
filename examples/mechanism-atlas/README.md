# Mechanism compatibility index

Current lessons live in semantic packages. [Browse the generated index](index.html), or use:

```sh
./ldraw-agent examples --family mechanism
./ldraw-agent knowledge show mechanism:KEY
```

The package README owns the lesson, scope, corrected descriptions and limits. The generated `catalog.json` retains explicit non-default scopes for compatibility; the gallery shows default-eligible lessons. Old aliases continue to resolve. Retired, held, diagnostic and inspiration sources require deliberate selection and cannot bypass export checks.

Legacy selection files and atlas generators are historical preparation inputs. Use the current package's editable plan/generator to reproduce a lesson. Legacy source preparation goes to a separate `--outdir` and does not admit its output. To refresh browsing from current metadata:

```sh
.venv/bin/python -c "from ldraw_tools.knowledge import write_compat_catalog; write_compat_catalog('mechanism', 'examples/mechanism-atlas')"
```

## Details

Use `examples --details` with this family, or a role-specific knowledge query.
