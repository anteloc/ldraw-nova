"""Rebuild the Technic mechanism studies from bundled, attributed source inputs.

No sibling checkout is required. Regeneration invalidates visual review; inspect
every new page before using mechanism review. --refresh-catalog only republishes
the gallery and derives current review status from existing evidence.
"""
from pathlib import Path
import argparse
import json
import shlex
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

from ldraw_tools.common import atomic_write, dumps, get_parts
from ldraw_tools.discovery import confined
from ldraw_tools.manuals import prepare_manual, regenerate_placement, sha, write_manual_viewer
from technic_catalog import write_catalog


def generate(outdir, *, names=None, renders=True):
    outdir = Path(outdir)
    seeds = json.loads((HERE / 'mechanism-selections.json').read_text())['references']
    if names and set(names) - {s['key'] for s in seeds}:
        raise ValueError('Unknown Technic mechanism selection')
    selected = [s for s in seeds if not names or s['key'] in names]
    # Reject changed provenance before replacing any existing study or review.
    for seed in selected:
        source = confined(HERE, seed['source'])
        if sha(source) != seed['source_sha256']:
            raise ValueError(f'{source.name} changed; review its provenance before rebuilding')
        for name, digest in seed['provenance_files'].items():
            if sha(confined(HERE, name)) != digest:
                raise ValueError(f'{name} changed; review its provenance before rebuilding')
    parts = get_parts()
    catalog = outdir / 'catalog.json'
    rows = {r['key']: r for r in json.loads(catalog.read_text())['examples']} if catalog.exists() else {}
    for seed in selected:
        name = seed['key']
        folder = outdir / 'mechanisms' / name
        # A failed refresh must not leave a catalog entry claiming current review.
        rows.pop(name, None)
        write_catalog(outdir, rows.values())
        report = prepare_manual(confined(HERE, seed['source']), seed['section'], folder,
            parts, title=seed['title'], views=seed['views'], notes=seed['operation'],
            renders=renders, normalize_rotations=True, repair_bfc=True, force=True)
        if not report['source_checks_passed'] or report['bom_matches'] is False:
            raise ValueError(f'{name}: inspect source-checks.json and BOM evidence')
        # Keep upstream selection records in the portable export as well.
        for path in seed['provenance_files']:
            dest = 'provenance/' + Path(path).name
            atomic_write(folder / dest, confined(HERE, path).read_text())
            report['artifact_hashes'][dest] = sha(folder / dest)
        atomic_write(folder / 'manual.json', dumps(report) + '\n')
        write_manual_viewer(folder, report, json.loads((folder / 'operation.json').read_text()))
        atomic_write(folder / 'generate.py', '''"""Rebuild the placement from this exported source and plan."""
from pathlib import Path
import sys

if __name__ == '__main__':
    folder = Path(__file__).resolve().parent
    for parent in folder.parents:
        if (parent / 'ldraw_tools').is_dir():
            sys.path.insert(0, str(parent))
            break
    from ldraw_tools.manuals import regenerate_placement
    print(regenerate_placement(folder))
''')
        regenerate_placement(folder)
        steps = sum(len(s['steps']) for s in report['sections'])
        source_groups = ('The source is a flat one-group selection: these pages show the retained '
                         'assembly from several views, not a recovered insertion sequence.'
                         if steps == 1 else
                         'Pages retain the source STEP groups; child assemblies have their own pages. '
                         'These groups are source construction evidence, not a swept insertion check.')
        operation = seed['operation']
        provenance_links = ' · '.join(f'[{Path(p).name}](provenance/{Path(p).name})'
                                      for p in seed['provenance_files'])
        resolved_folder = folder.resolve()
        export_source = shlex.quote(str(resolved_folder.relative_to(ROOT)
            if resolved_folder.is_relative_to(ROOT) else resolved_folder))
        guide = f'''# {seed['title']}

{seed['lesson']}

[Build pages](index.html) · [Source assembly](source.mpd) · [Editable plan](scene.plan.json) · [Operation notes](operation.json)

## Construction and interfaces

{operation['function']}

- Fixed structure: {operation['fixed']}
- Moving elements: {operation['moving']}
- Input: {operation['input']}
- Output: {operation['output']}

{operation['parent_context']}

## Adaptation ideas

{operation['reuse_notes']}

{seed['adaptation']}

## Source and build order

{seed['origin_summary']}

{source_groups}

{seed['construction_notes']}

The pinned input has SHA-256 `{seed['source_sha256']}`. Original authorship and
CCAL notices remain in the MPD. The upstream selection records travel with this
study: {provenance_links}. Nova's [extraction.json](extraction.json) records any
rotation normalization or BFC repair to the study copy.

## Reuse in a new model

From the repository root, export this reviewed directory:

```sh
./ldraw-agent mechanism export {export_source} \\
  --outdir output/my-{name}
./ldraw-agent build output/my-{name}/scene.plan.json --contacts none \\
  --output output/my-{name}/my-{name}.mpd
```

Export requires current visual review and a matching rendered BOM. The exported
`generate.py` rebuilds the placement from local files. Position the module through
`scene.plan.json`; its `source_origin` is a frame, not an asserted connector.
Adapt internal parts in the bundled MPD, preserve provenance, then review the
combined model. Apply fixed-member structural contracts only to fixed supports.

## Current evidence and scope

{report['physical_placements']} physical placements; {steps} nonempty source groups
across {len(report['sections'])} assembly section(s). Source checks pass.
{'Python and LeoCAD BOMs match.' if report['bom_matches'] else 'Rendering and BOM comparison are pending.'}
See [source checks](source-checks.json), [manual data](manual.json) and the separate
`visual-review.json` recorded after every generated image is opened.

{seed['qualification']}

Analytical mechanism verification remains **deferred**. Operation is intended or
inferred from the source. The study does not certify motion, loads or physical
buildability. Rebuilding pages clears their visual review.
'''
        atomic_write(folder / 'GUIDE.md', guide)
        prefix = f'mechanisms/{name}'
        rows[name] = dict(key=name, kind='mechanism', title=seed['title'],
            category=seed['category'], lesson=seed['lesson'],
            model=f'{prefix}/source.mpd', plan=f'{prefix}/scene.plan.json',
            guide=f'{prefix}/GUIDE.md', generator=f'{prefix}/generate.py',
            manual=f'{prefix}/index.html', operation=f'{prefix}/operation.json',
            physical_placements=report['physical_placements'], source_sha256=seed['source_sha256'],
            source_checks_passed=True, bom_matches=report['bom_matches'],
            analytical_verification='deferred', physical_validity='not_proven',
            **({'preview': f'{prefix}/renders/home.png'} if renders else {}))
        write_catalog(outdir, rows.values())
        print(f'{name}: {report["physical_placements"]} parts, {steps} source groups; '
              f'BOM match: {report["bom_matches"]}', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--outdir', type=Path, default=HERE)
    parser.add_argument('--name', action='append')
    parser.add_argument('--no-render', action='store_true')
    parser.add_argument('--refresh-catalog', action='store_true')
    args = parser.parse_args()
    if args.refresh_catalog:
        if args.name or args.no_render:
            parser.error('--refresh-catalog cannot regenerate selections')
        write_catalog(args.outdir, json.loads((args.outdir / 'catalog.json').read_text())['examples'])
    else:
        generate(args.outdir, names=args.name, renders=not args.no_render)
