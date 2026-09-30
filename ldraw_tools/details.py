"""Small authored design recipes, with real part interfaces and named colours."""
import json

from .common import DATA, jsonable
from .catalog import resolve_colour

RECIPES = {
    'arched-window': 'Six-stud window bay: projecting sill, contrasting piers, arch and flower accents. Support plane Y=0; highest body plane Y=-128; front is -Z.',
    'striped-awning': 'Eight-stud canopy with alternating fabric stripes and scalloped slope profile. Place on an exposed stud row at Z=0, Y=0; front projects to Z=-50.',
    'flower-planter': 'Four-stud stone planter with a layered leaf canopy and small flowers. Bottom plane Y=0. Reserve its foliage envelope, not just the base footprint.',
    'book-sign': 'Stud-mounted upright gold BOOKS sign, using a real patterned tile and side-stud bricks. Bottom Y=0, front -Z. Use above a door or awning.',
}


def palettes():
    return json.loads((DATA/'design-palettes.json').read_text())


def palette_report(parts, name=None):
    values=palettes()
    if name and name not in values:raise ValueError(f'Unknown palette {name}; use design palettes')
    return {key:{**value,'resolved':{role:jsonable(parts.colours_by_code[resolve_colour(symbol,parts)]) for role,symbol in value['roles'].items()}}
            for key,value in values.items() if not name or key==name}


def detail_section(name, palette='botanical-bookshop'):
    if name not in RECIPES:raise ValueError(f'Unknown detail {name}; use design details')
    if palette not in palettes():raise ValueError(f'Unknown palette {palette}')
    c=palettes()[palette]['roles']
    if palettes()[palette].get('family') == 'vehicle':
        raise ValueError('Architectural details need an architectural palette; use vehicle plan for vehicle palettes')
    def p(id,ref,role,at,**kw):
        return dict(id=id,ref=ref if ref.startswith('@') or ref.endswith('.dat') else ref+'.dat',colour=c.get(role,role),at=at,**kw)
    if name=='arched-window':
        steps=[[
            p('sill','@plates.Plate2X6','trim',[0,-8,-10]),
            p('frame','@windows.Window1X4X3WithoutShutterTabs','shopfront',[0,-80,0]),
            # Matching 1x2 panes: local pivots verified from OMR 10270 lines 699–709.
            p('left-pane','@windows.Window1X2X3PaneWithThickCornerTabs','glass',[-32,-76,4],yaw=-90),
            p('right-pane','@windows.Window1X2X3PaneWithThickCornerTabs','glass',[32,-76,4],yaw=90),
            p('left-pier','3005','trim',[-50,-32,0],repeat={'count':3,'step':[0,-24,0]}),
            p('right-pier','3005','trim',[50,-32,0],repeat={'count':3,'step':[0,-24,0]}),
            p('arch','@arches.Arch1X6X2WithThickTopAndReinforcedUnderside','trim',[0,-128,0]),
            *[p(f'flower-{x}','@plates.Plate1X1With5Petals','flowers',[x,-16,-20]) for x in [-30,10,30]]]]
    elif name=='striped-awning':
        steps=[[p('beam','3034','trim',[0,-8,-10])], [
            p(f'stripe-{i}','@slopes.SlopeBrick333X1','trim' if i%2 else 'shopfront',[-70+20*i,-32,0]) for i in range(8)]]
        # 4286 underside sockets are at Z=-20/-40. The beam's front stud row
        # carries Z=-20; its rear row at Z=0 anchors to the containing cornice.
    elif name=='flower-planter':
        steps=[[p('base','3031','trim',[0,-8,0]),p('soil','3022','wood',[0,-16,0]),
                *[p(f'flower-{x}','@plates.Plate1X1With5Petals','flowers',[x,-16,-30]) for x in [-30,10,30]]],
               [p('trunk','@bricks.Brick1X1RoundWithHollowStud','wood',[-10,-40,-10],repeat={'count':3,'step':[0,-24,0]}),
                p('lower-leaves','@plants.PlantLeaves6X5','plants',[-10,-96,-10]),
                p('branch-1','3062b','wood',[-10,-120,-10]),
                p('middle-leaves','@plants.PlantLeaves6X5','@colours.Green',[-10,-128,-10],yaw=90),
                p('branch-2','3062b','wood',[-10,-152,-10]),
                p('upper-leaves','@plants.PlantLeaves4X3','plants',[-10,-160,-10],yaw=180),
                p('crown','@plants.PlantLeaves4X3','@colours.Bright_Green',[-10,-168,-10])]]
    else:
        # Side studs on 11211 have local centres (±10,10,-10). A vertical
        # 2x4 tile rotated +90° about X mates its underside at Z=-20
        # to all four side studs; the printed face points towards -Z.
        orient=[[1,0,0],[0,0,-1],[0,1,0]]
        # A two-stud-wide foot fits between the adjacent upper window sills;
        # each side-stud mount engages one row on this shared foot.
        steps=[[p('base','3022','trim',[0,-8,0]),
                p('mount-left','@bricks.Brick1X2WithTwoStudsOnOneSide','shopfront',[-20,-32,-10]),
                p('mount-right','@bricks.Brick1X2WithTwoStudsOnOneSide','shopfront',[20,-32,-10]),
                p('books-sign','@tiles.Tile2X4WithMetallicGold_Books_Pattern','shopfront',[0,-22,-28],matrix=orient),
                p('binding','3020','metal',[0,-40,0])]]
    return dict(name=f'detail-{name}.ldr',description=RECIPES[name],anchors={'base':{'at':[0,0,0]}},steps=steps)


def detail_plan(name, palette='botanical-bookshop'):
    return dict(version=1,author='ldraw-nova detail recipes',sections=[detail_section(name,palette)])
