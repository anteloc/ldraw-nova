"""Annotate this reference and reuse the existing manual/catalog workflows.

No placement reconstruction, new LDraw parser, or discovery database is needed.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import shutil
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[3]))

from ldraw_tools.common import get_parts, normalized
from ldraw_tools.document import parse_source, source_blocks, section_table
from ldraw_tools.manuals import current_manual, prepare_manual
from ldraw_tools.reference_catalog import write_gallery

HERE = Path(__file__).resolve().parent


def annotate(source, annotations):
    """Add descriptions and comments while retaining every operational record."""
    if hashlib.sha256(source.read_bytes()).hexdigest() != annotations['source_sha256']:
        raise ValueError('Source changed; review the annotations before updating the pinned hash')
    blocks = source_blocks(source)
    labels = {normalized(a['section']):a for a in annotations['sections']}
    if set(labels) != set(blocks) or len(labels) != len(annotations['sections']):
        raise ValueError('Annotations must identify every FILE section exactly once')
    lines=[]
    for key,content in blocks.items():
        a=labels[key]
        lines += ['0 FILE '+a['section'], '0 '+a['title'], '0 Name: '+a['section']]
        if not any(text.startswith('0 Author:') for _,text in content):
            lines += ['0 Author: Unspecified (original main.ldr header credits LEGO)']
        lines += ['0 !LDRAW_ORG Model', '0 // Category: '+a['category'], '0 // Lesson: '+a['lesson']]
        if a['context_steps']:
            lines += ['0 // Main construction context: source STEP '+', '.join(map(str,a['context_steps']))+
                      '; corresponding area, not a declared parent or identical assembly.']
        lines += ['0 // Original FILE identity and all placement/step records retained; see original.ldr.']
        for number,text in content:
            if text.startswith(('0 Name:', '0 !LDRAW_ORG ')):
                continue
            if key=='main.ldr' and text=='0 10248 Ferrari F40':
                continue
            lines.append(text)
        lines.append('0 NOFILE')
    return '\r\n'.join(lines)+'\r\n'


def build_metadata(annotations):
    original=HERE/'original.ldr'
    result=annotate(original,annotations)
    (HERE/'ferrari-f40.mpd').write_bytes(result.encode())
    model=parse_source(original)
    table=section_table(model)
    # Main is flat. Declared submodel links are deliberately kept separate
    # from the curated main construction context.
    rows=[]
    for a in annotations['sections']:
        sub=table[normalized(a['section'])]
        parents=[s.name for s in table.values() for p in s.pieces
                 if normalized(p.reference)==normalized(sub.name)]
        children=Counter(p.reference for p in sub.pieces if normalized(p.reference) in table)
        rows.append(dict(a,declared_parents=parents,declared_children=dict(children),
                         reachable_from_main=sub is model,
                         source_steps=sum(any(getattr(p,'reference',None) for p in step) for step in sub.steps)))
    manifest=dict(version=1,original_filename='10248 Ferrari F40.ldr',source_sha256=annotations['source_sha256'],
                  annotated_sha256=hashlib.sha256(result.encode()).hexdigest(),
                  method='Descriptions, header correction and study comments only. Type 1-5, STEP, ROTSTEP and other operational records are unchanged.',
                  geometry_edited=False,main_is_flat=True,sections=rows)
    (HERE/'sections.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return rows


def build_gallery(rows, study_root):
    entries=[]
    source_hash=json.loads((HERE/'annotations.json').read_text())['source_sha256']
    for number,row in enumerate(rows):
        folder,manual=current_manual(study_root/f'{number:02}')
        extraction=json.loads((folder/'extraction.json').read_text())
        checks=json.loads((folder/'source-checks.json').read_text())
        if manual['source']['sha256'] != source_hash:
            raise ValueError('Overview belongs to a different source')
        if manual['source']['section'] != row['section']:
            raise ValueError('Overview section does not match annotation')
        target=HERE/'catalog'/f'{number:02}'
        (target/'renders').mkdir(parents=True,exist_ok=True)
        for name in ['source.mpd','extraction.json','source-checks.json','bom.json','bom-comparison.json','renders/home.png']:
            shutil.copyfile(folder/name,target/name)
        geometry=checks['geometry']; bounds=geometry['bounds']
        size=[(high-low)/unit for low,high,unit in zip(bounds['min'],bounds['max'],[20,8,20])]
        passed=manual['source_checks_passed']
        visual_review='pending'
        review_path=folder/'visual-review.json'
        if review_path.is_file():
            review=json.loads(review_path.read_text())
            if (review.get('status')=='visually_reviewed'
                    and review.get('manual_sha256')==hashlib.sha256((folder/'manual.json').read_bytes()).hexdigest()
                    and review.get('viewed_images')==['renders/home.png']):
                visual_review=dict(decision='technique',views=['home'],note=review['note'],
                                   image_sha256=manual['artifact_hashes']['renders/home.png'])
        card=dict(id=f'{number:02}',model='10248 Ferrari F40.ldr',section=row['section'],parser_section=row['section'],
                  description=row['title'],kind='models' if number==0 else 'submodels',
                  parent_description='F40: saved callout, not referenced by the main car' if number else 'Complete flattened car',
                  status='reference' if passed and manual['bom_matches'] is True else 'adaptation_needed',
                  assembly_checks_passed=passed,
                  source_sha256=manual['source']['sha256'],geometry=geometry,contacts_checked=False,
                  inventory=dict(expanded_leaf_count=manual['physical_placements']),
                  size_studs_plates_studs=size,bom_comparison=dict(matches=manual['bom_matches']),views=['home'],
                  semantic_annotation=row,source_repairs=extraction['changes'],visual_review=visual_review,
                  evidence_scope='Isolated extracted section; contacts not checked. Rendered with bounded rotation normalization where recorded. See visual-review.md for overview inspection.',
                  physical_validity='not_proven')
        (target/'card.json').write_text(json.dumps(card,indent=2)+'\n')
        context=('Main source steps '+', '.join(map(str,row['context_steps']))+'. ') if row['context_steps'] else ''
        entry=dict(title=row['title'],role=row['category'],lesson=row['lesson'],tags=[row['lesson']],card=card,
                   placement_notes=context+'Declared parents: '+(', '.join(row['declared_parents']) or 'none')+
                   '. Main car and saved callouts contain variant, colour and construction differences. Read the reference README before reusing.',
                   gallery_directory=f'catalog/{number:02}')
        entries.append(entry)
    write_gallery(HERE,entries)
    catalog=dict(version=1,title='Ferrari F40 semantic section catalog',source_sha256=entries[0]['card']['source_sha256'],
                 count=len(entries),scope='Overview catalog; five separate build studies are linked in README.md.',
                 entries=[dict(section=e['card']['section'],title=e['title'],category=e['role'],
                               card=e['gallery_directory']+'/card.json',preview=e['gallery_directory']+'/renders/home.png',
                               source_checks_passed=e['card']['assembly_checks_passed']) for e in entries])
    (HERE/'catalog.json').write_text(json.dumps(catalog,indent=2)+'\n')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalog-root',type=Path,help='Reuse 00..73 overview folders made by manual prepare')
    parser.add_argument('--render-overviews',type=Path,help='Generate those folders with existing manual tooling')
    parser.add_argument('--studies-out',type=Path,help='Prepare the five focused build studies; review images before export')
    args=parser.parse_args()
    annotations=json.loads((HERE/'annotations.json').read_text())
    rows=build_metadata(annotations)
    if args.render_overviews or args.studies_out:
        parts=get_parts()
    if args.render_overviews:
        for n,row in enumerate(rows):
            prepare_manual(HERE/'original.ldr',row['section'],args.render_overviews/f'{n:02}',parts,
                           title=row['title'],kind='construction',overview=True,views=('home',),
                           normalize_rotations=True,force=True)
            print('Overview',n,flush=True)
        args.catalog_root=args.render_overviews
    if args.catalog_root:
        build_gallery(rows,args.catalog_root)
    if args.studies_out:
        for study in json.loads((HERE/'studies.json').read_text())['studies']:
            prepare_manual(HERE/'ferrari-f40.mpd',study['section'],args.studies_out/study['key'],parts,
                           title=study['title'],notes=study['notes'],kind='construction',views=('home','back'),
                           normalize_rotations=True,force=True)
            print('Study',study['key'],flush=True)


if __name__=='__main__':
    main()
