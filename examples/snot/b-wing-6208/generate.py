"""Render an attributed construction study, without geometry repair or validation."""
import argparse
from collections import Counter
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from ldraw import Piece, inspect_model
from ldraw_tools.builder import serialize_mpd
from ldraw_tools.common import get_parts, jsonable, normalized
from ldraw_tools.document import (
    extract_section, parse_source, physical_context, section_table, source_blocks,
)
from ldraw_tools.external import render

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--outdir', type=Path, default=Path('output/b-wing-6208-study'))
    parser.add_argument('--only', help='Render one study key')
    args = parser.parse_args()
    selection = json.loads((HERE / 'study.json').read_text())
    source = HERE / 'original.mpd'
    if hashlib.sha256(source.read_bytes()).hexdigest() != selection['source_sha256']:
        raise ValueError('Source changed; review the pinned study before regenerating')
    parts = get_parts()
    model = parse_source(source)
    table = section_table(model)
    blocks = source_blocks(source)
    selected = [s for s in selection['studies'] if args.only is None or s['key'] == args.only]
    if not selected:
        raise ValueError('Unknown study key')
    for study in selected:
        folder = args.outdir / study['key']
        folder.mkdir(parents=True, exist_ok=True)
        section = table[normalized(study['section'])]
        text, extraction = extract_section(source, section.name, namespace='bwing-' + study['key'])
        path = folder / 'source.mpd'
        path.write_bytes(text.encode())
        indices = study.get('selected_placements')
        if indices is not None:
            # These flat-section visibility selections retain source poses and colours.
            extracted = parse_source(path)
            if extracted.submodels or len(set(indices)) != len(indices):
                raise ValueError('Cutaways require distinct placements in a flat section')
            if any(i < 0 or i >= len(extracted.pieces) for i in indices):
                raise ValueError('Cutaway index outside source section')
            keep = {id(extracted.pieces[i]) for i in indices}
            cutaway = replace(extracted, objects=[o for o in extracted.objects
                              if not isinstance(o, Piece) or id(o) in keep])
            path = folder / 'cutaway.mpd'
            path.write_bytes(serialize_mpd(cutaway).encode())
        (folder / 'extraction.json').write_text(json.dumps(extraction, indent=2) + '\n')
        parents = [dict(section=s.name, at=jsonable(p.position), matrix=p.matrix.rows)
                   for s in table.values() for p in s.pieces
                   if normalized(p.reference) == normalized(section.name)]
        placement_lines = [n for n, line in blocks[normalized(section.name)]
                           if line.split()[:1] == ['1']]
        metadata = dict(study, source_sha256=selection['source_sha256'],
                        source_nonempty_steps=sum(any(isinstance(p, Piece) for p in step)
                                                  for step in section.steps),
                        declared_parents=parents,
                        source_direct_part_inventory=dict(Counter(p.reference for p in section.pieces
                                                                  if normalized(p.reference) not in table)),
                        selected_source_lines=[placement_lines[i] for i in indices] if indices is not None else None,
                        geometry_verification='deferred', image_mode='cutaway' if indices is not None else 'completed_section')
        # Bounds are used only to frame the images, not to accept or repair geometry.
        physical, overlay = physical_context(parse_source(path), parts)
        bounds = inspect_model(physical, overlay).bounds
        render(path, parts.path.parent, folder / 'renders', views=study['views'], bounds=bounds)
        metadata['images'] = {view:dict(path=f'renders/{view}.png',
            sha256=hashlib.sha256((folder / 'renders' / f'{view}.png').read_bytes()).hexdigest())
            for view in study['views']}
        (folder / 'study.json').write_text(json.dumps(metadata, indent=2) + '\n')
        print(study['key'], flush=True)


if __name__ == '__main__':
    main()
