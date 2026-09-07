"""Generate original, contrasting building examples and their reusable modules.

Run from the repository root. JSON plans and MPDs are ordinary toolkit inputs;
this authoring script is not a new model format. See README.md for lessons.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from ldraw_tools.architecture import (
    Module, room, gable, flat_roof, porch, tree, lamp, bench, planter, stairs,
    fence, beacon, utility_stack, window4, door4, slab, line, ring, attach_roof,
    display4, fountain, solar_array,
)
from ldraw_tools.builder import build_plan
from ldraw_tools.common import atomic_write, dumps, get_parts, library_path
from ldraw_tools.geometry import analyze_geometry
from ldraw_tools.external import render, compare_bom

ROOT=Path(__file__).resolve().parent
DESIGNS={}


def snapshot_manifest(folder,source_sha,images):
    return dict(source_sha256=source_sha,renderer='LeoCAD',visual_review='Recorded separately in visual-review.json; verify its source hash.',
                images={Path(p).name:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in images})


def example(key,title,category,lesson,source,*,scale='minifigure',fit='',avoid='',modules=()):
    def register(fn):
        DESIGNS[key]=dict(key=key,title=title,category=category,lesson=lesson,source=source,
                          scale=scale,fit=fit,avoid=avoid,modules=list(modules),factory=fn)
        return fn
    return register


def site(name,title,ground=2):
    m=Module(name,title)
    m.add('3811',ground,id='site',purpose='32x32 stud ground; reserve footprints before laying paths')
    return m


def path(m,x0,z0,w,d,c=19,*,h=8,reserved=()):
    # Union intersecting paths on a one-stud lattice; never layer paving tiles.
    paved=getattr(m,'_paved',set())
    for x in range(x0,x0+w):
        for z in range(z0,z0+d):
            if any(a<=x<a+cw and b<=z<b+cd for a,b,cw,cd in reserved):continue
            if (x,z) not in paved:m.add('3070b',c,x+.5,h,z+.5)
            paved.add((x,z))
    m._paved=paved


def notched_terrace(m,x0,z0,w,d,h,c,notch_end):
    """Reserve the central six-stud stair lane in each lower terrace layer."""
    depth=notch_end-z0
    slab(m,x0,z0,-3-x0,depth,h,c)
    slab(m,3,z0,x0+w-3,depth,h,c)
    slab(m,x0,notch_end,w,d-depth,h,c)


def house(m,name,x,z,*,w=14,d=12,c=19,trim=15,roof=72,windows=(-4,4),door=0,h=0,
          material=None,roof_style='gable',open_back=False,door_style='traditional',door_width=4,dormer=False):
    shell=room(name,w,d,body=c,trim=trim,door=door,windows=windows,material=material,open_back=open_back,
               door_style=door_style,door_width=door_width)
    top=gable(name+'-roof',w+2,d,roof=roof,gable_colour=c,dormer=dormer) if roof_style=='gable' else flat_roof(name+'-roof',w,d,trim,roof)
    attach_roof(m,shell,top,x,h,z,id=name,colour=c)
    return shell


def small_chimney(m,x,z,h,c=71):
    for i in range(3):m.add('3003',c,x,h+24*(i+1),z)
    m.add('3022',72,x,h+80,z)


def sign_panel(name,pattern,colour=15):
    m=Module(name,'Upright 2x4 patterned sign on side-stud mounts; bottom Y=0, front -Z')
    m.add('3020',72,h=8)
    for x in [-1,1]:m.add('11211',colour,x,32,-.5)
    m.add(pattern,colour,0,22,-1.4,matrix=[[1,0,0],[0,0,-1],[0,1,0]])
    return m


def stall(name,c=4):
    m=Module(name,'Four-stud market stall; supported counter, posts and striped canopy')
    slab(m,-3,-2,6,4,8,70)
    for x in [-2.5,2.5]:
        for z in [-1.5,1.5]:
            for row in range(4):m.add('3005',70,x,32+24*row,z)
    slab(m,-3,-2,6,4,112,15)
    for i in range(6):
        line(m,-2.5+i,-2,4,120,c if i%2 else 15,axis='z',plate=True)
    for x in [-1,1]:m.add('3003',70,x,32,-1)
    slab(m,-2,-2,4,2,40,19)
    for x in [-1.5,-.5,.5,1.5]:m.add('6141',14,x,48,-1.5)
    return m


def clock(name='clock',colour=19):
    m=Module(name,'Printed civic clock, standing on a two-stud support surface')
    m.add('3003p0b',colour,h=24);m.add('3022',colour,h=32)
    return m


def crest(name,pattern,colour=15):
    m=Module(name,'Upright two-stud emblem on a side-stud mount; base Y=0, face -Z')
    m.add('3022',colour,h=8);m.add('11211',colour,0,32,-.5)
    m.add(pattern,colour,0,22,-1.4,matrix=[[1,0,0],[0,0,-1],[0,1,0]])
    return m


@example('cottage','Willow Porch Cottage','Detached homes and gardens',
         'A low gable, deep porch and asymmetrical garden make a modest house inviting.',
         'https://www.lego.com/en-us/product/cozy-house-31139',
         fit='The porch is centred on the door; a tree frames the left edge and a bench faces the garden.',
         avoid='Do not put a lamppost in the small front garden or cover the porch approach with planting.',modules=['porch','tree','bench','planter'])
def cottage():
    m=site('cottage','Willow Porch Cottage: sheltered entry, slate roof and flowering garden')
    house(m,'cottage-shell',0,3,w=16,d=12,c=19,trim=15,roof=72,windows=(-5,5),dormer=True)
    m.add(porch(w=8),15,0,0,-5,id='entry-porch',purpose='Rear edge Z=-3 abuts the shell face; four-stud entry remains clear')
    path(m,-2,-15,4,8)
    m.add(tree(),2,-12,0,-8);m.add(bench(),70,10,0,1,yaw=-90)
    m.add(planter(),5,10,0,-6);m.add(fence(8,15),15,-10,0,13)
    return m


@example('market-court','Marigold Market Court','Commercial and hospitality',
         'Two different shops and a produce stall share one pedestrian court.',
         'https://www.lego.com/en-us/product/main-street-31141',
         fit='Keep the middle court open; repeat cream trim but vary roof colour and storefront width.',
         avoid='Do not mirror every detail or fill the court with furniture.',modules=['stall','lamp','bench'])
def market():
    m=site('market-court','Marigold Market Court: two shops around an open plaza',71)
    house(m,'bakery',-8,5,w=10,d=12,c=226,trim=19,roof=320,windows=(),door=0,door_style='glazed')
    house(m,'tea-shop',8,6,w=10,d=10,c=378,trim=19,roof=288,windows=(),door=0,door_style='glazed')
    path(m,-3,-14,6,20,19)
    path(m,-13,-9,26,6,19)
    m.add(stall('produce-stall',25),25,-8,0,-12)
    m.add(lamp(),0,11,0,-12);m.add(bench(),70,8,0,-1)
    return m


@example('museum','Aster Museum Pavilion','Civic and cultural',
         'Symmetry, a columned portico and a stepped pediment establish a civic focal point.',
         'https://www.lego.com/en-us/product/natural-history-museum-10326',
         fit='Pair lamps beside the central approach; reserve the central axis for the portico.',
         avoid='Avoid striped shop awnings and random bright accents on the classical front.',modules=['portico','lamp','clock'])
def museum():
    m=site('museum','Aster Museum Pavilion: olive stonework and a ceremonial portico',71)
    shell=room('museum-hall',22,12,body=330,trim=19,windows=(-8,8))
    roof=flat_roof('museum-roof',22,12,19,72)
    attach_roof(m,shell,roof,z=5,id='museum-hall')
    p=porch('portico',trim=19,roof=19,w=12,d=6)
    # Pediment grows upwards from the porch canopy; all courses have support.
    for row,width in enumerate([10,8,6,4]):line(p,-width/2,-2.5,width,192+24*row,19)
    p.add(clock('museum-clock'),19,0,264,-2)
    m.add(p,19,0,0,-4)
    path(m,-3,-15,6,8,19)
    for x in [-7,7]:m.add(lamp(),0,x,0,-10)
    for x in [-13,13]:m.add(planter(14),14,x,0,9)
    return m


@example('fire-station','Cinder Bay Fire Station','Emergency services',
         'A wide vehicle portal, hose tower and red/white bands make the function readable.',
         'https://www.lego.com/en-us/product/fire-station-60320',
         fit='The vehicle apron stays empty; the tower sits behind one edge of the garage.',
         avoid='Do not put trees, benches or stairs in the vehicle exit.',modules=['beacon'])
def fire_station():
    m=site('fire-station','Cinder Bay Fire Station: open appliance bay, hose tower and clear apron',71)
    g=Module('fire-garage','Wide clear vehicle opening, bonded red/white walls and supported lintel')
    slab(g,-9,-6,18,12,8,72)
    for row in range(7):
        h=32+24*row;c=15 if row in [1,5] else 4
        line(g,-9,5.5,18,h,c,bond=bool(row%2))
        for x in [-8.5,8.5]:line(g,x,-5,10,h,c,axis='z',bond=bool(row%2))
        line(g,-9,-5.5,4,h,c);line(g,5,-5.5,4,h,c)
    # 10-stud opening bridged by two full 1x12 plates (60479), not floating strips.
    g.add('60479',15,0,184,-5.5)
    line(g,-9,-5.5,3,184,15,plate=True);line(g,6,-5.5,3,184,15,plate=True)
    line(g,-9,5.5,18,184,15,plate=True)
    for x in [-8.5,8.5]:line(g,x,-5,10,184,15,axis='z',plate=True)
    ring(g,18,12,192,15)
    g.anchor('roof',h=192)
    garage_roof=flat_roof('fire-garage-roof',18,12,15,72)
    garage_roof.add(crest('fire-emblem','3068bp57'),15,0,40,-5)
    attach_roof(m,g,garage_roof,-3,0,5,id='garage')
    tower=room('hose-tower',6,6,body=4,trim=15,door=None,windows=(),sides=False,rows=12,slits=True)
    attach_roof(m,tower,flat_roof('hose-tower-cap',6,6,15,72),11,0,7,id='hose-tower')
    path(m,-8,-15,10,14,72)
    for x in [-9,3]:m.add(beacon(),15,x,0,-10)
    return m


@example('school','Sunbeam Learning Courtyard','Education',
         'A classroom wing, clock block and courtyard create a small campus with an obvious entrance.',
         'https://www.lego.com/en-us/product/heartlake-international-school-41731',
         fit='Use the courtyard for gathering and the quieter side for a garden bench.',
         avoid='Keep trees outside the classroom window band and the entrance axis.',modules=['clock','bench','tree'])
def school():
    m=site('school','Sunbeam Learning Courtyard: classroom wing, clock tower and assembly court',2)
    house(m,'classrooms',-4,6,w=20,d=10,c=226,trim=15,roof=272,windows=(-7,7),door=0,roof_style='flat',door_style='glazed')
    tower=room('school-clock-tower',6,8,body=25,trim=15,door=None,windows=(),sides=False,rows=9,slits=True)
    cap=flat_roof('school-clock-cap',6,8,15,272);cap.add(clock('school-clock',15),15,0,40,-2)
    attach_roof(m,tower,cap,11,0,7,id='clock-block')
    path(m,-10,-12,18,12,19)
    m.add(bench(15),15,9,0,-9,yaw=-90)
    m.add(tree(2,14),2,-12,0,-9)
    return m


@example('clinic','Seabreeze Community Clinic','Healthcare',
         'A low horizontal wing, a taller glazed reception and a clear medical marker distinguish a clinic.',
         'https://www.lego.com/en-us/product/heartlake-city-hospital-42621',
         fit='A broad level approach leads to reception; a quiet planted side court balances the sign.',
         avoid='No stairs at the main entrance; the cross is a functional identifier, not scattered decoration.',modules=['medical-marker','planter','bench'])
def clinic():
    m=site('clinic','Seabreeze Community Clinic: white and turquoise wings with a level entrance',71)
    house(m,'clinic-wing',-5,6,w=18,d=10,c=15,trim=3,roof=71,windows=(-6,6),door=0,roof_style='flat',door_style='glazed')
    reception=room('clinic-reception',6,10,body=3,trim=15,door=0,windows=(),sides=True,rows=7,door_style='glazed')
    cap=flat_roof('reception-cap',6,10,15,71)
    marker=Module('medical-marker','Upright red medical cross on a white pedestal; bottom Y=0')
    marker.add('3020',15,h=8)
    # A 3x3 pixel cross in an upright plane; studded masonry, no unsupported arms.
    for row in range(3):
        for col in range(3):marker.add('3005',4 if row==1 or col==1 else 15,col-1.5,32+row*24,.5)
    cap.add(marker,15,0,40,0)
    attach_roof(m,reception,cap,10,0,6,id='reception')
    path(m,7,-15,6,16,71)
    m.add(bench(15),15,-5,0,-7)
    for x in [-11,2]:m.add(planter(5),5,x,0,-7)
    return m


@example('workshop','Copperworks Repair Yard','Industrial and workshops',
         'Repeated glazed roof bays and a separate utility stack communicate a workshop.',
         'https://www.lego.com/en-us/product/corner-garage-10264',
         fit='Keep the working yard sparse, use darker materials low down, and group equipment to one side.',
         avoid='Do not use domestic flower boxes or a ceremonial entrance.',modules=['utility-stack','beacon'])
def workshop():
    m=site('workshop','Copperworks Repair Yard: brick workshop, repeated roof lights and service stack',72)
    shell=room('workshop-shell',20,12,body=484,trim=72,door=0,windows=(-7,7),material='masonry',door_style='glazed')
    top=Module('rooflight-roof','Three supported gable rooflight bays with contrasting trans-light-blue slope glazing')
    for i in range(3):
        bay=gable(f'roof-light-{i}',20,4,roof=72,gable_colour=72)
        for step in bay.steps:
            for piece in step:
                if piece['ref']=='3039.dat' and piece.get('yaw')==180:piece['colour']=43
        top.add(bay,72,0,0,-4+4*i)
    attach_roof(m,shell,top,-2,0,5,id='workshop')
    m.add(utility_stack(),72,12,0,7)
    path(m,-9,-13,18,12,71,reserved=[(x-1,-13,2,2) for x in [-10,-8,-6]])
    # Low material stacks remain beside the door approach.
    for x in [-10,-8,-6]:
        for row in range(3):m.add('3003',70,x,24*(row+1),-12)
    m.add(beacon(),15,11,0,-7)
    return m


@example('railway-station','Hawthorn Halt','Transport terminals',
         'An elongated platform, shelter and ticket house establish direction and passenger circulation.',
         'https://www.lego.com/en-us/product/train-station-60335',
         fit='The canopy runs along the platform; benches face the implied track edge at the front.',
         avoid='Do not put furnishings in the platform edge strip; no rolling-stock clearance is claimed.',modules=['platform-canopy','bench','clock','lamp'])
def station():
    m=site('railway-station','Hawthorn Halt: ticket house and a long sheltered platform',71)
    house(m,'ticket-house',-8,7,w=10,d=10,c=19,trim=288,roof=320,windows=(),door=0)
    canopy=porch('platform-canopy',trim=288,roof=72,w=16,d=6)
    m.add(canopy,288,6,0,-1)
    path(m,-15,-10,30,6,71,reserved=[(-14,-8,2,2)])
    path(m,-15,-12,30,2,14)
    m.add(bench(),70,4,8,-1);m.add(bench(),70,9,8,-1)
    m.add(lamp(),0,-13,0,-7)
    return m


@example('farmstead','Red Barn Farmstead','Agriculture',
         'A tall barn, smaller granary, fenced yard and crop patch make a working cluster.',
         'https://www.lego.com/en-us/product/barn-farm-animals-60346',
         fit='Leave a broad barn approach; use fences to describe the yard rather than enclose every edge.',
         avoid='Avoid urban paving and lampposts; the crops belong in rows away from vehicle access.',modules=['fence','tree'])
def farm():
    m=site('farmstead','Red Barn Farmstead: high red gable, low granary and planted field',2)
    house(m,'red-barn',-5,6,w=14,d=14,c=4,trim=15,roof=72,windows=(),door_width=8)
    house(m,'granary',10,7,w=6,d=8,c=19,trim=70,roof=484,windows=(),door=0)
    for x in [-11,9]:m.add(fence(8),70,x,0,-3)
    path(m,-7,-15,4,14,19)
    slab(m,3,-13,10,6,8,70)
    for x in [3.5,5.5,7.5,9.5,11.5]:
        for z in [-12.5,-10.5,-8.5]:m.add('3062b',2,x,32,z);m.add('24866',14,x,40,z)
    return m


def battlement(name,w,d,c=71):
    m=Module(name,'Square tower top: connected deck, low parapet and alternating merlons')
    slab(m,-w/2,-d/2,w,d,8,c);ring(m,w,d,32,c,plate=False)
    for x in range(-w//2,w//2,2):
        for z in [-d/2+.5,d/2-.5]:m.add('3005',c,x+.5,56,z)
    for z in range(-d//2+2,d//2-1,2):
        for x in [-w/2+.5,w/2-.5]:m.add('3005',c,x,56,z+.5)
    return m


@example('gatehouse','Greywatch Gatehouse','Castles and fortifications',
         'Paired crenellated towers flank an open arch and a clear defended approach.',
         'https://www.lego.com/en-us/product/lion-knights-castle-10305',
         fit='Keep the gate visually dominant; use sparse green at the foot of heavy stone walls.',
         avoid='Do not add cottage windows everywhere or block the gate with a tree.',modules=['battlement','arch'])
def castle():
    m=site('gatehouse','Greywatch Gatehouse: two crenellated towers and a real arched passage',330)
    for x in [-8,8]:
        tower=room(f'gate-tower-{x}',8,10,body=71,trim=72,door=None,windows=(),sides=False,rows=10,material='masonry',slits=True)
        attach_roof(m,tower,battlement(f'tower-cap-{x}',8,10),x,0,4,id=f'tower-{x}')
    gate=Module('gate-arch','Six-stud arch carried by bonded stone piers, with a parapet above')
    slab(gate,-4,-2,8,4,8,72)
    for x in [-3.5,3.5]:
        for row in range(5):mref='3005';gate.add(mref,71,x,32+24*row,-.5)
    # Arch 3307 outer width six; support piers at +/-2.5 instead of +/-3.5.
    for x in [-2.5,2.5]:
        for row in range(5):gate.add('3005',71,x,32+24*row,-.5)
    gate.add('3307',71,0,176,-.5)
    line(gate,-4,-.5,8,184,72,plate=True)
    line(gate,-4,-.5,8,208,71)
    for x in [-3.5,-1.5,.5,2.5]:gate.add('3005',71,x,232,-.5)
    m.add(gate,71,0,0,-1)
    path(m,-2,-15,4,12,19)
    return m


@example('medieval-village','Hazelbridge Village','Historic vernacular villages',
         'A tall timber inn and a smaller smithy frame a shared working square.',
         'https://www.lego.com/en-us/product/medieval-town-square-10332',
         fit='Use shared timber/stone colours but different roof heights; put the stall on the square edge.',
         avoid='Avoid identical paired façades and modern lighting.',modules=['stall','bench','utility-stack'])
def medieval():
    m=site('medieval-village','Hazelbridge Village: timber inn, low smithy and a market edge',330)
    lower=room('inn-lower',12,10,body=19,trim=70,door=0,windows=(-4,4),material='masonry',timber=True)
    upper=room('inn-upper',12,10,body=19,trim=70,door=None,windows=(-3,3),timber=True)
    m.add(lower,19,-8,0,7,id='inn-lower')
    m.add(upper,19,id='inn-upper',attach={'to':'inn-lower','anchor':'roof','using':'base'})
    m.add(gable('inn-roof',14,10,roof=272,gable_colour=19),272,id='inn-roof',attach={'to':'inn-upper','anchor':'roof','using':'base'})
    house(m,'smithy',9,7,w=8,d=10,c=71,trim=70,roof=72,windows=(),door=0)
    m.add(stall('village-stall',320),320,9,0,-8)
    path(m,-2,-15,6,24,19)
    m.add(bench(),70,-9,0,-6)
    return m


@example('temple','Jade Terrace Pavilion','Temples and East Asian pavilions',
         'Three diminishing roof tiers and repeated red columns establish a vertical ceremonial rhythm.',
         'https://www.lego.com/en-us/product/temple-of-airjitzu-70751',
         fit='Keep a clear central stair and frame the entrance with paired planters.',
         avoid='Do not describe this stylized pavilion as an accurate reconstruction of a particular culture or monument.',modules=['stairs','planter','tiered-canopy'])
def temple():
    m=site('temple','Jade Terrace Pavilion: tiered jade roofs and red column galleries',330)
    notched_terrace(m,-9,-6,18,18,8,71,-4)
    notched_terrace(m,-8,-5,16,16,16,71,-4)
    slab(m,-7,-4,14,14,24,19)
    tower=Module('pavilion-tiers','Diminishing column galleries, complete floor diaphragms and broad eaves')
    for level,(w,d) in enumerate([(14,12),(10,8),(6,4)]):
        base=level*144
        slab(tower,-w/2,-d/2,w,d,base+8,19)
        for x in [-w/2+.5,w/2-.5]:
            for z in [-d/2+.5,d/2-.5]:
                for row in range(4):tower.add('3005',4,x,base+32+24*row,z)
        slab(tower,-w/2-1,-d/2-1,w+2,d+2,base+112,288)
        # Full second layer carries the next gallery; corner finials sit outside it.
        slab(tower,-w/2-1,-d/2-1,w+2,d+2,base+120,288)
        slab(tower,-w/2,-d/2,w,d,base+128,297)
        slab(tower,-w/2,-d/2,w,d,base+136,288)
        slab(tower,-w/2,-d/2,w,d,base+144,288)
        for x in [-w/2-.5,w/2+.5]:
            for z in [-d/2-.5,d/2+.5]:tower.add('4589',297,x,base+144,z)
    tower.add('3942c',297,0,480,0)
    m.add(tower,4,0,24,3)
    m.add(stairs(6,3),71,0,0,-5.5)
    path(m,-3,-15,6,8,19)
    for x in [-11,11]:m.add(planter(5),5,x,0,-7)
    return m


@example('conservatory','Fernlight Glasshouse','Gardens and recreational buildings',
         'A transparent envelope and repeated dark mullions let planting become the interior focus.',
         'https://www.lego.com/en-us/product/the-botanical-garden-21353',
         fit='Keep dense plants inside the glazed volume and quiet paths outside.',
         avoid='Do not fill the roof with opaque decoration or block every view through the glazing.',modules=['window4','bench','planter'])
def conservatory():
    m=site('conservatory','Fernlight Glasshouse: repeated glazed bays, roof lantern and internal planting',2)
    glasshouse=Module('glasshouse-shell','Repeated glazing within an open structural frame; front entry remains clear')
    slab(glasshouse,-11,-6,22,12,8,71)
    for side,z in [('front',-5.5),('back',5.5)]:
        for x in [-8,-4,0,4,8]:
            if side=='front' and x==0:continue
            glasshouse.add(display4(288),288,x,8,z,yaw=0 if side=='front' else 180)
        for x in [-10.5,10.5]:
            for row in range(6):glasshouse.add('3005',288,x,32+24*row,z)
    glasshouse.add(door4(288,288,'glazed'),288,0,8,-5.5)
    for x in [-10.5,10.5]:
        for z in [-2,2]:
            glasshouse.add(display4(288),288,x,8,z,yaw=90 if x<0 else -90)
        for z in [-4.5,4.5]:
            for row in range(6):glasshouse.add('3005',288,x,32+24*row,z)
    ring(glasshouse,22,12,160,288)
    glasshouse.anchor('roof',h=160)
    r=gable('glass-roof',22,12,roof=47,gable_colour=47,tiers=3)
    attach_roof(m,glasshouse,r,0,0,4,id='glasshouse')
    for x in [-6,6]:
        for z in [1,7]:m.add(planter(5 if x<0 else 14),5,x,8,z)
    path(m,-2,-15,4,13,19)
    m.add(bench(),70,9,0,-8)
    m.add(fountain(),71,-10,0,-10)
    return m


@example('treehouse','Canopy Field Station','Treehouses and nature shelters',
         'An elevated hut, visible support trunk, access stair and surrounding canopy form a vertical nature scene.',
         'https://www.lego.com/en-us/product/tree-house-21318',
         fit='Let the trunk remain visible below the platform; foliage frames the hut instead of intersecting it.',
         avoid='Never float a hut in leaves; the platform needs a continuous load path and access.',modules=['stairs','tree','platform'])
def treehouse():
    m=site('treehouse','Canopy Field Station: raised woodland hut with a broad stair and foliage',330)
    support=Module('tree-platform','Raised 12x12 deck carried by a central trunk and four timber posts')
    slab(support,-3,-3,6,6,8,70)
    for row in range(6):support.add('6222',70,0,32+24*row,0)
    for x in [-4.5,4.5]:
        for z in [-4.5,4.5]:
            support.add('3024',70,x,8,z)
            for row in range(6):support.add('3005',70,x,32+24*row,z)
    slab(support,-6,-6,12,12,160,70);support.anchor('deck',h=160)
    m.add(support,70,0,0,5,id='platform')
    hut=room('canopy-hut',8,8,body=19,trim=70,door=0,windows=(),material='log')
    m.add(hut,19,id='hut',attach={'to':'platform','anchor':'deck','using':'base'})
    m.add(gable('canopy-roof',10,8,roof=288,gable_colour=19),288,id='roof',attach={'to':'hut','anchor':'roof','using':'base'})
    # Twenty 8-LDU rises reach the deck; stair runs along one side of the site.
    m.add(stairs(4,20),71,-8,0,0)
    # Bridge landing at the stair rear to the platform's back left corner.
    slab(m,-10,10,4,2,160,70)
    m.add('3020',70,-6,168,10,purpose='Bridge the seam between walkway and platform with real studs')
    for x in [-9,-1]:
        for row in range(6):m.add('3003',70,x,24*(row+1),11)
        m.add('3022',70,x,152,11)
    m.add(tree(288,5),2,11,0,-7);m.add(tree(2,14),2,-12,0,10)
    return m


@example('lighthouse','Saltwind Light and Keeper Cottage','Coastal and maritime',
         'A slender banded tower and low cottage balance a waterside composition.',
         'https://www.lego.com/en-us/product/motorised-lighthouse-21335',
         fit='The beacon is the skyline focus; the cottage stays lower and the water remains uncluttered.',
         avoid='Do not imply a working Fresnel lens or motor; this is a static architectural study.',modules=['beacon','fence'])
def lighthouse():
    m=site('lighthouse','Saltwind Light: striped round beacon tower and a red-roof keeper cottage',1)
    slab(m,-14,-9,28,22,8,71)
    tower=Module('striped-light','Round lighthouse tower; 4x4 drum, wide gallery, transparent lantern and cap')
    slab(tower,-3,-3,6,6,8,72)
    for row in range(16):tower.add('6222',15 if row//3%2==0 else 4,h=32+24*row)
    slab(tower,-3,-3,6,6,400,72)
    for x in [-2.5,2.5]:
        for z in [-2.5,2.5]:tower.add('3062b',72,x,424,z)
    ring(tower,6,6,432,72)
    for row in range(3):tower.add('3941',46,h=424+24*row)
    tower.add('4285b',72,h=488);tower.add('3942c',72,h=536)
    m.add(tower,15,-7,8,4)
    house(m,'keeper-cottage',7,5,w=10,d=10,c=15,trim=72,roof=320,windows=(),door=0,h=8)
    path(m,-12,-7,24,4,19,h=16,reserved=[(4,-7,1,1),(11,-7,1,1)])
    m.add(fence(8,72),72,8,8,-7)
    return m


@example('winter-lodge','Snowbell Alpine Lodge','Seasonal and alpine buildings',
         'A steep snow roof, warm timber walls and sheltered porch create a winter retreat.',
         'https://www.lego.com/en-us/product/alpine-lodge-10325',
         fit='Keep snow as broad roof/ground masses; warm accents cluster around the entrance.',
         avoid='Do not scatter white studs indiscriminately or place foliage through the roof.',modules=['porch','tree','bench'])
def winter():
    m=site('winter-lodge','Snowbell Alpine Lodge: steep white gable, log walls and a warm porch',15)
    house(m,'alpine-lodge',1,4,w=16,d=14,c=70,trim=19,roof=15,windows=(-5,5),material='log',dormer=True)
    m.add(porch('lodge-porch',trim=70,roof=15,w=8),70,1,0,-5)
    path(m,-1,-15,4,8,71)
    m.add(tree(288,15),288,-12,0,-9)
    m.add(bench(),70,11,0,-6)
    return m


@example('wizard-tower','Moonflower Observatory','Fantasy and enchanted buildings',
         'Offset tower masses, a pointed roof and restrained magical colour create a fantasy silhouette.',
         'https://www.lego.com/en-us/product/hogwarts-castle-and-grounds-76419',
         fit='Use the high spire as the focal feature; keep magical accents small and repeat the same palette.',
         avoid='Do not use arbitrary floating geometry or add a different bright colour to every tier.',modules=['tree','planter'])
def wizard():
    m=site('wizard-tower','Moonflower Observatory: asymmetrical stone towers and purple roof spires',330)
    for name,x,z,w,d,rows in [('observatory',-4,5,12,12,12),('study',8,5,8,10,6)]:
        shell=room(name,w,d,body=19,trim=72,door=0 if name=='study' else None,
                   windows=(-3,3) if name=='observatory' else (),rows=rows)
        if name=='observatory':
            cap=Module('observatory-conical-roof','Two complementary tiled half-cones form a supported circular spire')
            slab(cap,-w/2,-d/2,w,d,8,72)
            cap.add('1746',85,0,152,0)
            cap.add('1746',85,0,152,0,yaw=180)
            cap.add('3942c',297,0,200,0)
        else:
            cap=gable(name+'-spire',w+2,d,roof=85,gable_colour=19)
            cap.add('3942c',297,0,8+24*(d//2-1)+56,0)
        attach_roof(m,shell,cap,x,0,z,id=name)
    path(m,6,-15,4,15,19)
    m.add(tree(288,5),2,-12,0,-9);m.add(planter(5),5,1,0,-8)
    return m


@example('moon-base','Selene Research Outpost','Science fiction and space habitats',
         'Two low habitats, a linking passage and a separate landing pad form a coherent functional compound.',
         'https://www.lego.com/en-us/product/lunar-research-base-60350',
         fit='Use white hulls, dark equipment and localized blue glazing; beacons define the landing edge.',
         avoid='Keep terrestrial landscaping and Victorian lamps out; the dish is static, not an articulated mechanism.',modules=['beacon','solar-array','dish'])
def moon():
    m=site('moon-base','Selene Research Outpost: paired habitats, connector and landing pad',72)
    for x in [-9,9]:house(m,f'habitat-{x}',x,7,w=10,d=10,c=15,trim=272,roof=71,windows=(),door=0,roof_style='flat',door_style='hatch')
    # Low solid service corridor joins the rear walls; an exposed doorway is not claimed here.
    corridor=room('service-link',8,4,body=71,trim=272,door=None,windows=(),sides=False,rows=3)
    attach_roof(m,corridor,flat_roof('service-link-roof',8,4,15,72),0,0,8,id='service-link')
    path(m,-7,-14,14,12,71,reserved=[(x-1,z-1,2,2) for x in [-6,6] for z in [-13,-3]])
    path(m,-4,-11,8,6,72)
    for x in [-6,6]:
        for z in [-13,-3]:m.add(beacon(),15,x,0,z)
    dish=Module('communications-dish','Static upward-facing six-stud dish on a low mast')
    dish.add('3022',72,h=8)
    for row in range(3):dish.add('3941',15,h=32+24*row)
    dish.add('4285b',15,h=96)
    m.add(dish,15,12,0,-9)
    m.add(solar_array(),272,-11,0,-7)
    return m


@example('skyline','Three Rivers Skyline','Microscale architecture and landmarks',
         'Three different tower silhouettes around a shared plinth demonstrate massing at a declared small scale.',
         'https://www.lego.com/en-us/product/new-york-city-21028',scale='microscale',
         fit='Use tiny repeated window bands and broad quiet plinths; tower spacing is part of the composition.',
         avoid='Never mix full minifigure doors, trees or lampposts into this scene.',modules=['terraced-tower','spire'])
def skyline():
    m=site('skyline','Three Rivers Skyline: stepped limestone tower, glass slab and low cultural pavilion',0)
    slab(m,-15,-10,30,22,8,71)
    # Solid stepped tower: setbacks sit completely on the preceding tier.
    h=8
    for w,d,levels,c in [(8,8,6,19),(6,6,4,19),(4,4,3,19),(2,2,2,19)]:
        for row in range(levels):
            for z in range(-d//2,d//2):line(m,-10-w/2,4+z+.5,w,h+24,c)
            h+=24
            slab(m,-10-w/2,4-d/2,w,d,h+8,72);h+=8
    m.add('3942c',297,-10,h+48,4)
    h=8
    for row in range(14):
        for z in range(6):line(m,-1,-1+z+.5,8,h+24,43)
        h+=24;slab(m,-1,-1,8,6,h+8,15);h+=8
    slab(m,-1,-1,8,6,h+8,72)
    for row in range(3):
        for z in range(6):line(m,9,-1+z+.5,4,32+24*row,15)
    slab(m,8,-2,6,8,88,19)
    path(m,-14,-8,28,4,19,h=16)
    return m


@example('frontier','Mesa Crossing Trading Post','Western and frontier',
         'A false-front shop, boardwalk and small stable establish a frontier settlement.',
         'https://www.lego.com/cdn/product-assets/product.bi.core.pdf/4585106.pdf',
         fit='Timber porches and a dusty open yard belong here; keep the false front above the lower roof.',
         avoid='Do not rely on lettering alone to distinguish the building from a modern shop.',modules=['porch','fence','bench'])
def frontier():
    m=site('frontier','Mesa Crossing: false-front trading post, boardwalk and a small stable',19)
    shell=house(m,'trading-post',-6,6,w=14,d=10,c=70,trim=19,roof=72,windows=(-5,5),roof_style='flat',material='log')
    front=Module('false-front','Supported stepped false front with a central sign field')
    for row,width in enumerate([14,12,8]):line(front,-width/2,0,width,24*(row+1),19)
    m.add(front,19,-6,200,1.5)
    m.add(porch('boardwalk-porch',trim=70,roof=19,w=14),70,-6,0,-1)
    house(m,'stable',10,7,w=6,d=8,c=19,trim=70,roof=484,windows=(),door=0)
    path(m,-14,-8,18,4,70)
    m.add(fence(8),70,9,0,-3)
    return m


@example('desert-sanctuary','Sunwell Desert Sanctuary','Adventure ruins and ancient monuments',
         'A stepped platform, open colonnade and paired pylons express an archaeological adventure setting.',
         'https://www.lego.com/en-us/service/building-instructions/5988',
         fit='Use a clear ceremonial axis and sparse warm stone accents; leave the ruins visually open.',
         avoid='Do not invent historical accuracy or place unrelated medieval/gothic decoration on the sanctuary.',modules=['stairs','columns'])
def desert():
    m=site('desert-sanctuary','Sunwell Desert Sanctuary: paired pylons, open court and columned inner shrine',19)
    notched_terrace(m,-12,-4,24,18,8,484,-2)
    notched_terrace(m,-11,-3,22,16,16,19,-2)
    slab(m,-10,-2,20,14,24,19)
    for x in [-7,7]:
        h=24
        for w,d,rows in [(6,6,4),(4,4,3),(2,2,2)]:
            for row in range(rows):
                for z in range(d):line(m,x-w/2,z+1.5-d/2,w,h+24,19 if row%2 else 484)
                h+=24
        m.add('3942c',297,x,h+48,1)
    shrine=Module('colonnaded-shrine','Open inner shrine with paired columns and a complete lintel deck')
    slab(shrine,-5,-3,10,6,8,19)
    for x in [-4,4]:
        for z in [-2,2]:
            for row in range(5):shrine.add('3941',19,x,32+24*row,z)
    slab(shrine,-5,-3,10,6,136,19);slab(shrine,-5,-3,10,6,144,484)
    m.add(shrine,19,0,24,9)
    m.add(stairs(6,3),71,0,0,-3.5)
    path(m,-3,-15,6,10,484)
    return m


def generate(keys=None, outdir=ROOT, *, snapshots=False, views=('home','front','top')):
    outdir=Path(outdir);outdir.mkdir(parents=True,exist_ok=True)
    parts=get_parts();library=library_path();records=[]
    for key in keys or DESIGNS:
        meta=DESIGNS[key];folder=outdir/key;folder.mkdir(parents=True,exist_ok=True)
        module=meta['factory']();plan=module.plan()
        atomic_write(folder/'scene.plan.json',dumps(plan)+'\n')
        text,model,diagnostics=build_plan(plan,parts)
        geometry=analyze_geometry(model,parts,detail='summary',contacts='none')
        diagnostics+=geometry['diagnostics']
        passed=not any(d['severity']=='error' for d in diagnostics)
        sha=hashlib.sha256(text.encode()).hexdigest()
        report=dict(checks_passed=passed,source_sha256=sha,physical_validity='not_proven',diagnostics=diagnostics,geometry=geometry)
        atomic_write(folder/'validation.json',dumps(report)+'\n')
        record={k:v for k,v in meta.items() if k!='factory'}
        record.update(physical_placements=geometry['occurrence_count'],sections=len(plan['sections']),source_sha256=sha,checks_passed=passed)
        atomic_write(folder/'design-brief.json',dumps(record)+'\n')
        if not passed:
            print(key,'FAILED',[(d['code'],d.get('message'),d.get('section'),d.get('line_number')) for d in diagnostics if d['severity']=='error'][:12],flush=True)
            records.append(record);continue
        atomic_write(folder/(key+'.mpd'),text)
        print(key,geometry['occurrence_count'],'parts',len(plan['sections']),'sections: checks pass',flush=True)
        if snapshots:
            from ldraw import inspect_model
            result=render(folder/(key+'.mpd'),library,folder,views=views,bounds=inspect_model(model,parts).bounds)
            atomic_write(folder/'render-manifest.json',dumps(snapshot_manifest(folder,sha,result['images']))+'\n')
            comparison=compare_bom(model,parts,folder/'leocad-bom.csv')
            comparison['source_sha256']=sha
            atomic_write(folder/'bom-comparison.json',dumps(comparison)+'\n')
            if not comparison['matches']:raise ValueError(key+' BOM mismatch')
            record['bom_matches']=True
        records.append(record)
    atomic_write(outdir/'last-run.json',dumps(records)+'\n')
    return records


def detail_factories():
    return {
        'porch':lambda:porch(), 'bench':bench, 'tree':tree, 'lamppost':lamp,
        'flower-box':planter, 'stairs':lambda:stairs(6,3), 'fence':fence,
        'beacon':beacon, 'chimney':utility_stack, 'window':window4,
        'glazed-door':lambda:door4(15,15,'glazed'), 'display-window':display4,
        'fountain':fountain, 'solar-array':solar_array,
        'market-stall':lambda:stall('teaching-stall',25), 'clock':clock,
        'battlement':lambda:battlement('teaching-battlement',8,10),
        'dormer-roof':lambda:gable('teaching-dormer-roof',18,12,dormer=True),
    }


def generate_details(outdir=ROOT, *, snapshots=False):
    from ldraw import inspect_model
    parts=get_parts();library=library_path();records=[]
    for key,factory in detail_factories().items():
        m=factory();folder=Path(outdir)/'details'/key;folder.mkdir(parents=True,exist_ok=True)
        plan=m.plan();text,model,ds=build_plan(plan,parts)
        g=analyze_geometry(model,parts,detail='summary',contacts='all')
        ds+=g['diagnostics'];passed=not any(d['severity']=='error' for d in ds)
        if not passed:raise ValueError(f'Detail {key}: '+dumps(ds))
        sha=hashlib.sha256(text.encode()).hexdigest()
        atomic_write(folder/'scene.plan.json',dumps(plan)+'\n');atomic_write(folder/(key+'.mpd'),text)
        atomic_write(folder/'validation.json',dumps(dict(checks_passed=passed,source_sha256=sha,diagnostics=ds,geometry=g))+'\n')
        record=dict(key=key,description=m.description,root=m.name+'.ldr',anchors=m.anchors,bounds_ldu=g['bounds'],
                    physical_placements=g['occurrence_count'],contact_count=g['contact_count'],
                    optimistic_component_count=g['optimistic_component_count'],placement_notes=m.notes,
                    source_sha256=sha,model=f'details/{key}/{key}.mpd',plan=f'details/{key}/scene.plan.json')
        atomic_write(folder/'interface.json',dumps(record)+'\n')
        if snapshots:
            result=render(folder/(key+'.mpd'),library,folder,views=['home'],bounds=inspect_model(model,parts).bounds)
            atomic_write(folder/'render-manifest.json',dumps(snapshot_manifest(folder,sha,result['images']))+'\n')
            comparison=compare_bom(model,parts,folder/'leocad-bom.csv');comparison['source_sha256']=sha
            atomic_write(folder/'bom-comparison.json',dumps(comparison)+'\n')
            if not comparison['matches']:raise ValueError(key+' detail BOM mismatch')
        records.append(record);print('detail',key,g['occurrence_count'],'parts: checks pass',flush=True)
    atomic_write(Path(outdir)/'details/catalog.json',dumps(records)+'\n')
    return records


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('examples',nargs='*',choices=list(DESIGNS))
    parser.add_argument('--outdir',type=Path,default=ROOT)
    parser.add_argument('--render',action='store_true')
    parser.add_argument('--details',action='store_true',help='Generate the reusable detail collection too')
    parser.add_argument('--views',nargs='+',default=['home','front','top'])
    args=parser.parse_args()
    result=generate(args.examples,args.outdir,snapshots=args.render,views=args.views)
    if args.details:generate_details(args.outdir,snapshots=args.render)
    sys.exit(0 if all(r['checks_passed'] for r in result) else 1)
