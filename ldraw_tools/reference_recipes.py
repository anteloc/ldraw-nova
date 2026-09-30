"""Small parameterized constructions learned from inspected source references.

Parameters change brick courses and palette, never scale physical parts.
"""

RECIPES = {
    'arcade-bay': dict(default_height=3, description='Four-stud open arch with adjustable brick piers and a layered cornice.',
                       source='10276-1.mpd / 10276 - bk3-step185.ldr',
                       lesson='Use a dedicated arch and round-plate cornice accents; change the pier courses to suit the storey.',
                       interface='Base underside Y=0; feet at X=-30 and +30. Front is -Z. Base is a positioning frame.'),
    'street-lantern': dict(default_height=6, description='Slender round-brick street lantern with a moulded transparent light and dish shade.',
                           source='31038-1_Winter.mpd / 31038 - Lamp.ldr',
                           lesson='Reuse the transparent round-brick and inverted-dish lamp vocabulary on a stud-mounted, height-adjustable post.',
                           interface='Two-by-two-stud base underside Y=0. Reserve the dish envelope above the pavement. Base is a positioning frame.'),
}


def recipe_plan(name, *, height=None, colour=None, accent=None):
    if name not in RECIPES:
        raise ValueError('Unknown reference recipe')
    height = RECIPES[name]['default_height'] if height is None else height
    if isinstance(height,bool) or not isinstance(height,int) or not 2 <= height <= 10:
        raise ValueError('Height must be 2–10 brick courses')
    colour = (19 if name=='arcade-bay' else 0) if colour is None else colour
    accent = (28 if name=='arcade-bay' else 71) if accent is None else accent
    placements=[]
    def p(key,part,c,x,y,z=0,**kw):
        placements.append(dict(id=key,ref=part+'.dat',colour=c,at=[x,y,z],**kw))
    if name=='arcade-bay':
        p('foot','3710',colour,0,-8)
        for x,side in [(-30,'left'),(30,'right')]:
            p(side+'-pier','3005',colour,x,-32,repeat=dict(count=height,step=[0,-24,0]))
        arch_y=-8-24*height-24
        p('arch','3659',colour,0,arch_y)
        p('cornice-left','3004',colour,-20,arch_y-24)
        p('cornice-masonry','98283',colour,20,arch_y-24,yaw=180)
        for i,x in enumerate([-30,-10,10,30]):p('cornice-round-'+str(i),'85861',accent,x,arch_y-32)
        p('cornice-cap','3010',colour,0,arch_y-56)
        author='Orion Pobursky [OrionP]; parameterized adaptation by ldraw-nova'
    else:
        p('base','3022',colour,0,-8)
        p('centred-post-mount','87580',colour,0,-16)
        p('post','3062b',colour,0,-40,repeat=dict(count=height,step=[0,-24,0]))
        top=-16-24*height
        p('collar','85861',accent,0,top-8)
        p('light','3062b',46,0,top-32)
        p('shade','4740',colour,0,top-40)
        author='ldraw-nova; lamp vocabulary from Marc Giraudet [Mad_Marc]'
    return dict(version=1,author=author,license='Redistributable under CCAL version 2.0 : see CAreadme.txt',sections=[
        dict(name='recipe-'+name+'.ldr',description=RECIPES[name]['description'],anchors={'base':dict(at=[0,0,0])},steps=[placements])])


def generate_recipe(name, destination):
    """CLI used by the two selected example generate.py entry points."""
    import argparse
    from pathlib import Path
    from .common import get_parts, atomic_write, dumps, library_path
    from .builder import build_plan
    from .geometry import analyze_geometry
    from .external import render, compare_bom
    parser=argparse.ArgumentParser(description=RECIPES[name]['description'])
    parser.add_argument('--height',type=int)
    parser.add_argument('--colour',type=int)
    parser.add_argument('--accent',type=int)
    parser.add_argument('--outdir',type=Path,default=Path(destination))
    parser.add_argument('--render',action='store_true')
    args=parser.parse_args()
    parts=get_parts()
    plan=recipe_plan(name,height=args.height,colour=args.colour,accent=args.accent)
    text,model,diagnostics=build_plan(plan,parts)
    geometry=analyze_geometry(model,parts,detail='summary',contacts='all')
    passed=not any(d['severity']=='error' for d in diagnostics+geometry['diagnostics'])
    report=dict(checks_passed=passed,diagnostics=diagnostics,geometry=geometry)
    if not passed:
        print(dumps(report));return 1
    args.outdir.mkdir(parents=True,exist_ok=True)
    model_path=args.outdir/(name+'.mpd')
    previous=model_path.read_bytes() if model_path.is_file() else None
    atomic_write(args.outdir/'scene.plan.json',dumps(plan)+'\n')
    atomic_write(model_path,text)
    if previous != model_path.read_bytes() or args.render:
        # A previous review belongs to its source and rendered images. Keep no
        # stale preview beside an edited recipe, even when --render is omitted.
        for filename in ['visual-review.json','render.json','renders/leocad-bom.csv',
                         *['renders/'+v+'.png' for v in ['home','front','right','top']]]:
            (args.outdir/filename).unlink(missing_ok=True)
    atomic_write(args.outdir/'validation.json',dumps(report)+'\n')
    if args.render:
        from ldraw import inspect_model
        rendered=render(args.outdir/(name+'.mpd'),library_path(),args.outdir/'renders',views=['home','front','right','top'],bounds=inspect_model(model,parts).bounds)
        comparison=compare_bom(model,parts,args.outdir/'renders/leocad-bom.csv')
        atomic_write(args.outdir/'render.json',dumps(dict(rendered,comparison=comparison))+'\n')
        if not comparison['matches']:return 1
    print(dumps(dict(output=str(args.outdir),checks_passed=passed,placements=geometry['occurrence_count'],optimistic_components=geometry['optimistic_component_count'])))
    return 0
