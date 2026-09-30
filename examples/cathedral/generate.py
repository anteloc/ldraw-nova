"""Aurelia Cathedral: original Gothic architectural display model.

Run from the repository root: .venv/bin/python output/cathedral/generate.py
Coordinates follow the existing Module API: X/Z studs, height in LDU.
"""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from ldraw_tools.architecture import Module, line, slab, ring, gable
from ldraw_tools.common import atomic_write, dumps

OUT = Path(__file__).resolve().parent
STONE, TRIM, WEATHER, ROOF, DARK, GOLD = 19, 15, 28, 72, 70, 297
BLUE, AMBER = 33, 46
FACE = [[1, 0, 0], [0, 0, -1], [0, 1, 0]]


def wall(m, lower, length, fixed, base, rows, *, axis='x', holes=(), colour=STONE):
    """Bonded one-stud wall; holes are (centre, width, first row, last row)."""
    for row in range(rows):
        blocked = {i for i in range(length) if any(
            lo <= row <= hi and c-w/2 <= lower+i < c+w/2
            for c, w, lo, hi in holes)}
        i = 0
        m.step()
        while i < length:
            if i in blocked:
                i += 1
                continue
            end = i+1
            while end < length and end not in blocked:
                end += 1
            h = base+24*(row+1)
            line(m, lower+i if axis == 'x' else fixed,
                 fixed if axis == 'x' else lower+i, end-i, h,
                 WEATHER if row == 0 else colour, axis=axis, bond=bool(row % 2))
            i = end


def lancet(name, *, tall=False, glass=True, tint=BLUE):
    """Six-stud pointed bay. Base 0; head 120 or 168; no extra sill."""
    m = Module(name, 'Paired Jev-selected 13965 pointed arches; reserved six-stud bay')
    courses = 4 if tall else 2
    for row in range(courses):
        for x in [-2.5, 2.5]:
            m.add('3005', TRIM, x, 24*(row+1), 0)
    if glass:
        for level in range(courses//2):
            for x in [-1, 1]:
                h = 48*(level+1)
                m.add('60592', STONE, x, h)
                m.add('60601p01', tint if (level+int(x)) % 2 else AMBER, x, h,
                      purpose='Jev-selected Gothic-patterned glass, in its matching frame')
    top = 24*courses+72
    m.add('13965', TRIM, -2.5, top, yaw=90)
    m.add('13965', TRIM, 2.5, top, yaw=-90)
    for x in [-2.5, 2.5]:
        m.add('3005', TRIM, x, top, purpose='Fill 24-LDU dropped outer arch stud')
    m.anchor('top', h=top)
    return m


def pinnacle():
    m = Module('cathedral-pinnacle', 'Two-stud stone pinnacle with slate taper and gold tip')
    m.add('3941', TRIM, h=24)
    m.add('3942c', ROOF, h=72)
    m.add('4589', ROOF, h=96)
    m.add('6141', GOLD, h=104)
    return m


def cross():
    m = Module('cathedral-cross', 'Brick-built cross on a two-stud base, aligned to real studs')
    m.add('3022', TRIM, h=8)
    m.add('3005', TRIM, .5, 32, .5)
    m.add('3622', TRIM, .5, 56, .5)
    m.add('3005', TRIM, .5, 80, .5)
    return m


def roof(name, length, width, *, crosses=False):
    m = gable(name, length, width, roof=ROOF, gable_colour=STONE)
    # Studded ridge provides genuine mounting surfaces for crosses and fleche.
    for step in m.steps:
        for p in step:
            if p['ref'] == '3068b.dat':
                p['ref'] = '3022.dat'
    return m


def shed(name, length):
    m = Module(name, 'Six-stud side-aisle lean-to; supported slate slope courses')
    slab(m, -length/2, -3, length, 6, 8, STONE)
    for level in range(5):
        h = 8+24*(level+1)
        m.step()
        for x in range(-length//2+1, length//2, 2):
            m.add('3039', ROOF, x, h, -1.5+level)
        for z in range(-1+level, 3):
            line(m, -length/2, z+.5, length, h, STONE, bond=bool(level % 2))
    return m


def rose():
    m = Module('cathedral-rose', 'Six-stud blue rose window with eight pale stone ribs and amber centre')
    # The backing plate mates two side studs at its lower central socket row.
    # The round spacer raises the web's hub 8 LDU so its outer rim clears the glass.
    m.add('11213', BLUE, 0, 0, -.4, matrix=FACE)
    m.add('4032a', BLUE, 0, 0, -.8, matrix=FACE)
    m.add('4285b', TRIM, 0, 0, -1.2, matrix=FACE)
    m.add('14769', AMBER, 0, 0, -1.6, matrix=FACE)
    return m


def foundation():
    m = Module('cathedral-foundation', '48 by 72 stud bonded display base and raised cathedral platform')
    slab(m, -24, -36, 48, 72, 8, 72)
    # Crosswise second layer bridges seams in the lower plate courses.
    layer = Module('cathedral-base-crossbond', 'Orthogonal base layer')
    slab(layer, -36, -24, 72, 48, 8, 71)
    m.add(layer, 71, h=8, yaw=90)
    slab(m, -21, -26, 42, 58, 24, STONE)
    # Paved forecourt and perimeter walks. Tiles never cover an attachment stud.
    slab(m, -21, -34, 42, 8, 24, 71, tile=True)
    for x in [-23, 21]:
        slab(m, x, -34, 2, 68, 24, 71, tile=True)
    slab(m, -21, 32, 42, 2, 24, 71, tile=True)
    for x in [-3, -1, 1]:
        for z in [-33, -31, -29, -27]:
            # Replace existing paving with an axial dark stone inlay.
            target = [20*(x+1), -24, 20*z]
            for step in m.steps:
                for p in step:
                    if p.get('at') == target and p['ref'] == '3068b.dat':
                        p['colour'] = 72
    m.anchor('platform', h=24)
    return m


def tower():
    m = Module('cathedral-bell-tower', 'Thirty-course bell tower with lancets, open belfry and four pinnacles')
    openings = [(0, 6, 3, 9), (0, 6, 13, 17), (0, 6, 22, 28)]
    wall(m, -4, 8, -4.5, 0, 30, holes=openings)
    wall(m, -4, 8, 4.5, 0, 30, holes=openings)
    for x in [-3.5, 3.5]:
        wall(m, -4, 8, x, 0, 30, axis='z', holes=openings)
    for fixed, yaw in [(-4.5, 0), (4.5, 180)]:
        m.add(lancet('cathedral-tower-lower', tall=True), STONE, 0, 72, fixed, yaw=yaw)
        m.add(lancet('cathedral-tower-middle'), STONE, 0, 312, fixed, yaw=yaw)
        m.add(lancet('cathedral-belfry-arch', tall=True, glass=False), STONE, 0, 528, fixed, yaw=yaw)
    for x, yaw in [(-3.5, 90), (3.5, -90)]:
        m.add(lancet('cathedral-tower-lower', tall=True), STONE, x, 72, 0, yaw=yaw)
        m.add(lancet('cathedral-tower-middle'), STONE, x, 312, 0, yaw=yaw)
        m.add(lancet('cathedral-belfry-arch', tall=True, glass=False), STONE, x, 528, 0, yaw=yaw)
    # Projecting front piers emphasize the towers without covering the windows.
    for x in [-3.5, 3.5]:
        for row in range(30):
            if row in [10, 20]:
                for dh in [-8, 0]:
                    m.add('3024', TRIM, x, 24*(row+1)+dh, -5.5)
            else:
                m.add('3005', TRIM, x, 24*(row+1), -5.5)
    slab(m, -5, -6, 10, 12, 728, TRIM)
    ring(m, 10, 12, 752, STONE, plate=False)
    ring(m, 10, 12, 760, TRIM)
    slab(m, -4, -5, 8, 10, 736, ROOF, tile=True)
    pin = pinnacle()
    for x in [-4, 4]:
        for z in [-5, 5]:
            m.add(pin, TRIM, x, 760, z)
    # Intermediate projecting string courses are plates over actual wall tops.
    # Leave them as front relief ledges supported by the projecting piers.
    for h in [248, 488]:
        line(m, -4, -5.5, 8, h, TRIM, plate=True)
    m.anchor('base')
    return m


def nave():
    m = Module('cathedral-nave', 'Long nave, five pointed arcades each side and glazed clerestory')
    centres = [-16, -8, 0, 8, 16]
    holes = [(c, 6, 2, 8) for c in centres] + [(c, 6, 14, 18) for c in centres]
    # The flying buttress feet replace one wall cell, never intersect it.
    holes += [(z, 1, 15, 17) for z in [-12.5, -4.5, 19.5]]
    for x, yaw in [(-7.5, 90), (7.5, -90)]:
        wall(m, -22, 45, x, 0, 19, axis='z', holes=holes)
        for z in centres:
            m.add(lancet('cathedral-nave-arcade', tall=True, glass=False), STONE, x, 48, z, yaw=yaw)
            m.add(lancet('cathedral-clerestory'), STONE, x, 336, z, yaw=yaw)
        line(m, x, -22, 45, 464, TRIM, axis='z', plate=True)
    # Eastern wall opens into the chancel at floor level.
    wall(m, -8, 16, 23.5, 0, 19, holes=[(0, 6, 0, 6), (0, 6, 14, 18)])
    m.add(lancet('cathedral-east-arcade', tall=True, glass=False), STONE, 0, 0, 23.5, yaw=180)
    m.add(lancet('cathedral-clerestory'), STONE, 0, 336, 23.5, yaw=180)
    line(m, -8, 23.5, 16, 464, TRIM, plate=True)
    m.anchor('roof', h=464)
    return m


def facade():
    m = Module('cathedral-west-front', 'Deep pointed entrance and recessed rose window between the towers')
    holes = [(0, 6, 0, 5), (0, 8, 10, 15), (0, 12, 17, 18)]
    wall(m, -8, 16, -.5, 0, 19, holes=holes)
    m.add('35565', STONE, 0, 144, -.5, purpose='Jev-ranked full pointed doorway panel')
    for row in range(5):
        if row == 2:
            m.add('11211', DARK, 0, 24*(row+1), 1)
            for x in [-1.5, 1.5]:
                m.add('3005', DARK, x, 24*(row+1), 1)
        else:
            line(m, -2, 1, 4, 24*(row+1), DARK)
    for x in [-.5, .5]:
        m.add('6141', GOLD, x, 62, .1, matrix=FACE)
    for x in [-2.5, 2.5]:
        for row in range(5):
            m.add('3005', TRIM, x, 24*(row+1), -2.5)
    m.add('13965', TRIM, -2.5, 192, -2.5, yaw=90)
    m.add('13965', TRIM, 2.5, 192, -2.5, yaw=-90)
    for x in [-2.5, 2.5]:
        m.add('3005', TRIM, x, 192, -2.5)
    line(m, -3, -2.5, 6, 200, TRIM, plate=True)
    # Recessed rose backing is one stud behind the main facade.
    for row in range(6):
        h = 264+24*row
        if h == 312:
            line(m, -4, .5, 3, h, STONE)
            m.add('11211', STONE, 0, h, .5)
            line(m, 1, .5, 3, h, STONE)
        else:
            line(m, -4, .5, 8, h, STONE)
    m.add(rose(), TRIM, 0, 312, 0)
    # An open miniature arcade gives the upper front a distinct Gothic rhythm.
    for x in [-4, 0, 4]:
        for dx in [-1.5, 1.5]:
            m.add('3005', TRIM, x+dx, 432, -.5)
        m.add('3659', TRIM, x, 456, -.5)
    # Thin contrasting pilasters run alongside the rose rather than across it.
    for x in [-6.5, 6.5]:
        for row in range(19):
            m.add('3005', TRIM, x, 24*(row+1), -1.5)
    line(m, -8, -.5, 16, 464, TRIM, plate=True)
    return m


def aisle(name, start, end):
    m = Module(name, 'Low side aisle with Gothic glass and a separately removable lean-to roof')
    length = end-start
    centres = [-8] if start < 0 else [20]
    holes = [(c, 6, 2, 6) for c in centres]
    wall(m, start, length, 13.5, 0, 8, axis='z', holes=holes)
    for z in centres:
        m.add(lancet(name+'-window'), STONE, 13.5, 48, z, yaw=-90)
    for z in [start+.5, end-.5]:
        wall(m, 8, 5, z, 0, 8)
    line(m, 13.5, start, length, 200, TRIM, axis='z', plate=True)
    m.add(shed(name+'-roof', length), STONE, 11, 200, (start+end)/2, yaw=-90)
    return m


def transept():
    m = Module('cathedral-transept', 'Projecting transept chapel with triple Gothic windows and a slate gable')
    # Local footprint X -7..7, Z -7..6; front is the exposed end.
    wall(m, -7, 14, -6.5, 0, 12, holes=[(-3, 6, 3, 9), (3, 6, 3, 9)])
    for x in [-6.5, 6.5]:
        wall(m, -6, 12, x, 0, 12, axis='z', holes=[(0, 6, 3, 9)])
        m.add(lancet('cathedral-transept-lancet', tall=True), STONE, x, 72, 0, yaw=90 if x<0 else -90)
    for x in [-3, 3]:
        m.add(lancet('cathedral-transept-lancet', tall=True), STONE, x, 72, -6.5)
    line(m, -7, -6.5, 14, 296, TRIM, plate=True)
    for x in [-6.5, 6.5]:
        line(m, x, -6, 12, 296, TRIM, axis='z', plate=True)
    m.add(roof('cathedral-transept-roof', 14, 14), STONE, 0, 296, -1, yaw=90)
    return m


def flying_buttress():
    m = Module('cathedral-flying-buttress', 'Twelve-stud raised arch between nave pier and freestanding stepped pier')
    # Local inner foot X=0, outer foot X=11; all studs centred on this axis.
    for row in range(15):
        if row < 6:
            for z in [-1, 0, 1]:
                line(m, 9.5, z, 3, 24*(row+1), WEATHER if row==0 else STONE)
        else:
            m.add('3005', STONE, 11, 24*(row+1))
    m.add('18838', TRIM, 5.5, 432)
    # Raised arch end studs are 48 LDU below its top.
    for x in [0, 11]:
        m.add('3005', STONE, x, 408)
        m.add('3005', STONE, x, 432)
    m.add('4589', TRIM, 11, 456)
    m.add('6141', GOLD, 11, 464)
    return m


def furnishings():
    m = Module('cathedral-interior', 'Central processional aisle, pews and an elevated altar')
    # Floor tiles cover only the interior; masonry and buttress footprints stay bare.
    slab(m, -7, -20, 14, 43, 8, 71)
    slab(m, -1, -20, 2, 36, 16, 72, tile=True)
    for z in [-15, -11, -7, -3, 1, 5, 9, 13]:
        for x in [-4, 4]:
            for dx in [-1.5, 1.5]:
                m.add('3005', DARK, x+dx, 32, z+.5)
            line(m, x-2, z+.5, 4, 40, DARK, plate=True)
            line(m, x-2, z+1.5, 4, 32, DARK)
            line(m, x-2, z+1.5, 4, 56, DARK)
    slab(m, -4, 17, 8, 5, 16, TRIM)
    for x in [-2, 2]:
        m.add('3003', TRIM, x, 40, 20)
    slab(m, -3, 19, 6, 2, 48, TRIM)
    return m


def build_scene():
    m = Module('aurelia-cathedral', 'Aurelia Cathedral: twin Gothic towers, rose window, nave and flying buttresses')
    m.add(foundation(), STONE, id='foundation')
    m.step()
    m.add(nave(), STONE, h=24, id='nave')
    m.add(facade(), STONE, h=24, z=-22, id='west-front')
    t = tower()
    for x in [-12, 12]:
        m.add(t, STONE, x, 24, -18)
    # Nave roof's long local X axis becomes the model's longitudinal Z axis.
    m.add(roof('cathedral-nave-roof', 48, 16), STONE, 0, 488, 1, yaw=90, id='nave-roof')
    cr = cross()
    m.add(cr, TRIM, 0, 672, -20)
    m.add(cr, TRIM, 0, 672, 22)
    sp = Module('cathedral-fleche', 'Slender crossing fleche on a four-stud ridge saddle')
    sp.add('3031', ROOF, h=8)
    sp.add('3943b', ROOF, h=56)
    sp.add('3942c', ROOF, h=104)
    sp.add('4589', ROOF, h=128)
    sp.add('6141', GOLD, h=136)
    m.add(sp, ROOF, 0, 672, 8)
    for side in [1, -1]:
        for start, end in [(-13, 1), (15, 25)]:
            a = aisle('cathedral-aisle-'+str(start).replace('-','m'), start, end)
            # Reflect by a rigid 180-degree turn plus longitudinal translation.
            if side == 1:
                m.add(a, STONE, h=24)
            else:
                m.add(a, STONE, h=24, z=start+end, yaw=180)
        m.add(transept(), STONE, side*14, 24, 8, yaw=-90 if side==1 else 90)
    b = flying_buttress()
    for z in [-12.5, -4.5, 19.5]:
        m.add(b, STONE, 7.5, 24, z)
        m.add(b, STONE, -7.5, 24, z, yaw=180)
    m.add(furnishings(), STONE, h=24)
    # East chapel extends beyond the nave, giving the rear a stepped silhouette.
    ch = Module('cathedral-east-chapel', 'Square-ended choir chapel with three lancets and a lower roof')
    wall(ch, -6, 12, 3.5, 0, 10, holes=[(0, 6, 2, 8)])
    for x in [-5.5, 5.5]:
        wall(ch, -4, 7, x, 0, 10, axis='z', holes=[(0, 6, 2, 8)])
        ch.add(lancet('cathedral-choir-lancet', tall=True), STONE, x, 48, 0, yaw=90 if x<0 else -90)
    ch.add(lancet('cathedral-choir-lancet', tall=True), STONE, 0, 48, 3.5, yaw=180)
    ring(ch, 12, 8, 248, TRIM)
    ch.add(roof('cathedral-choir-roof', 8, 12), STONE, 0, 248, 0, yaw=90)
    m.add(ch, STONE, 0, 24, 28)
    plan = m.plan()
    plan['author'] = 'Original design generated with ldraw-nova for the workspace owner'
    return plan


if __name__ == '__main__':
    plan = build_scene()
    atomic_write(OUT/'cathedral.plan.json', dumps(plan)+'\n')
    brief = dict(title='Aurelia Cathedral', subject='Original Gothic cathedral architectural display model',
                 scale='Architectural display; compressed interior, not a scale replica of a real cathedral',
                 footprint_studs=[48,72], palette=dict(stone='Tan', trim='White', roof='Dark Bluish Grey', glass=['Trans Dark Blue','Trans Yellow']),
                 primary_focus='Twin bell towers framing a pale ribbed blue rose window and deep pointed portal',
                 supporting_features=['Long slate nave with clerestory','Six flying buttresses','Projecting transept chapels','Open belfries and slender pinnacles'],
                 interior=['Central processional aisle','Sixteen pews','Raised altar'],
                 modules=[dict(name=s['name'],description=s['description'],anchors=s['anchors']) for s in plan['sections']],
                 construction='Real library parts; rigid transforms; reserved openings; editable Python generator and JSON plan',
                 limitations=['Physical buildability, strength and retail part/colour availability require separate review'])
    atomic_write(OUT/'design-brief.json', dumps(brief)+'\n')
    print(f'Wrote {len(plan["sections"])} sections to {OUT / "cathedral.plan.json"}')
