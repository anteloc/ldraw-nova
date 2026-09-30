"""Small architectural construction vocabulary for the building atlas.

Coordinates at this authoring layer: X/Z in studs, h in LDU upwards. Every
emitted placement is ordinary LDraw: [20*x, -h, 20*z]. Modules use bottom Y=0
and face -Z. These helpers never infer stacking from category bounding boxes.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from builtins import id as id_key

AUTHOR = 'ldraw-nova building atlas'
BRICKS = {1:'3005', 2:'3004', 3:'3622', 4:'3010', 6:'3009', 8:'3008'}
PLATES = {1:'3024', 2:'3023b', 3:'3623', 4:'3710', 6:'3666', 8:'3460'}
WIDE_PLATES = {1:'3023b', 2:'3022', 3:'3021', 4:'3020', 6:'3795', 8:'3034'}


@dataclass
class Module:
    name: str
    description: str
    steps: list = field(default_factory=lambda:[[]])
    anchors: dict = field(default_factory=lambda:{'base':{'at':[0,0,0]}})
    children: dict = field(default_factory=dict)
    notes: list = field(default_factory=list)
    serial: int = 0

    def step(self):
        if self.steps[-1]: self.steps.append([])
        return self

    def anchor(self, name, x=0, h=0, z=0):
        self.anchors[name] = {'at':[20*x,-h,20*z]}
        return self

    def add(self, ref, colour, x=0, h=0, z=0, *, yaw=0, id=None, purpose=None, matrix=None, attach=None):
        if isinstance(ref, Module):
            # Keep distinct objects until plan() checks the entire namespace;
            # indexing by name here would silently replace an earlier definition.
            self.children[id_key(ref)] = ref
            ref = ref.name+'.ldr'
        elif not (ref.startswith('@') or ref.endswith(('.ldr','.dat'))):
            ref += '.dat'
        self.serial += 1
        p = dict(id=id or f'p{self.serial:04d}', ref=ref, colour=colour)
        if attach: p['attach']=attach
        else:
            p['at']=[20*x,-h,20*z]
            if matrix is not None: p['matrix']=matrix
            elif yaw: p['yaw']=yaw
        if purpose: p['purpose']=purpose
        self.steps[-1].append(p)
        return p['id']

    def section(self):
        return dict(name=self.name+'.ldr',description=self.description,anchors=self.anchors,
                    steps=[s for s in self.steps if s])

    def plan(self):
        modules={};objects=set()
        def visit(m):
            if id(m) in objects:return
            objects.add(id(m))
            if m.name in modules:
                if modules[m.name].section()!=m.section():
                    raise ValueError('Conflicting module definitions: '+m.name)
            else:modules[m.name]=m
            for child in m.children.values(): visit(child)
        visit(self)
        return dict(version=1,author=AUTHOR,sections=[m.section() for m in modules.values()])


def lengths(n, maximum=8):
    """Tile an integer stud interval with real standard part lengths."""
    if n<0 or int(n)!=n: raise ValueError('Interval length must be a nonnegative integer')
    while n:
        k=next(k for k in [8,6,4,3,2,1] if k<=min(n,maximum))
        yield k
        n-=k


def line(m,x,z,n,h,colour,*,axis='x',plate=False,bond=False,material=None):
    # x/z is the first cell's lower corner along the run, centre across it.
    widths=list(lengths(n,4 if bond else 8))
    if bond and n>1: widths=[1,*lengths(n-1,4)]
    cursor=0
    for width in widths:
        ref=(PLATES if plate else BRICKS)[width]
        if material=='log' and width==4: ref='30137'
        if material=='masonry' and width==2: ref='@bricks.Brick1X2WithEmbossedBricks'
        m.add(ref,colour,x+cursor+width/2 if axis=='x' else x,h,
              z if axis=='x' else z+cursor+width/2,yaw=0 if axis=='x' else 90)
        cursor+=width


def slab(m,x0,z0,w,d,h,colour,*,tile=False):
    """Plate/tile rectangle at body-top h; x0/z0 are its lower bounds."""
    if min(w,d)<0 or int(w)!=w or int(d)!=d: raise ValueError('Integer slab dimensions required')
    z=z0
    while z<z0+d:
        depth=min(2,z0+d-z)
        x=x0
        for width in lengths(w,2 if tile else 8):
            if tile:
                if depth==2 and width==2: m.add('3068b',colour,x+1,h,z+1)
                else:
                    for ix in range(width):
                        for iz in range(depth):m.add('3070b',colour,x+ix+.5,h,z+iz+.5)
            else:
                ref=(WIDE_PLATES if depth==2 else PLATES)[width]
                m.add(ref,colour,x+width/2,h,z+depth/2,yaw=90 if width==1 and depth==2 else 0)
            x+=width
        z+=depth


def ring(m,w,d,h,c,*,plate=True):
    line(m,-w/2,-d/2+.5,w,h,c,plate=plate)
    line(m,-w/2,d/2-.5,w,h,c,plate=plate)
    line(m,-w/2+.5,-d/2+1,d-2,h,c,axis='z',plate=plate)
    line(m,w/2-.5,-d/2+1,d-2,h,c,axis='z',plate=plate)


def window4(trim=15,glass=47):
    m=Module(f'window4-{trim}-{glass}','Four-stud glazed bay; bottom Y=0, body height 72 LDU, front -Z')
    m.add('@windows.Window1X4X3WithoutShutterTabs',trim,h=72)
    m.add('@windows.Window1X2X3PaneWithThickCornerTabs',glass,-1.6,68,.2,yaw=-90)
    m.add('@windows.Window1X2X3PaneWithThickCornerTabs',glass,1.6,68,.2,yaw=90)
    return m


def door4(trim=15,leaf=70,style='traditional'):
    m=Module(f'door4-{trim}-{leaf}-{style}','Four-stud closed hinged entrance; bottom Y=0, height 144 LDU; front -Z')
    m.add('@doors.Door1X4X6Frame',trim,h=144)
    ref={'traditional':'60623','glazed':'60797c04','hatch':'60616a'}[style]
    m.add(ref,leaf if style=='traditional' else trim,-1.6,144,.25)
    return m


def display4(trim=288):
    m=Module(f'display4-{trim}','Four-stud full-height fixed glazing; bottom Y=0, height 144 LDU')
    m.add('60596',trim,h=144)
    m.add('57895',47,0,139,.25)
    return m


def room(name,w=14,d=12,*,body=19,trim=15,door=0,windows=(-4,4),sides=True,rows=6,
         open_back=False,material=None,glass=47,timber=False,door_style='traditional',door_width=4,slits=False):
    """A reserved-opening shell, deck, lintels and named roof/door interfaces.

    door/windows are front centre X values in studs; door=None closes the front.
    Windows occupy brick courses 1..3, door courses 0..5. The roof anchor is
    the top of a plate ring, not the shell's full stud-inclusive bounds.
    """
    m=Module(name,f'{w} by {d} stud shell with reserved door/window openings and removable roof interface')
    slab(m,-w/2,-d/2,w,d,8,70)
    openings={s:[] for s in ['front','back','left','right']}
    for bottom in range(1,rows-2,6):
        for x in windows:openings['front'].append((x,4,bottom,bottom+2,'window'))
    if door is not None:openings['front'].append((door,door_width,0,5,'door'))
    if slits:
        openings['front'].extend((x,1,5,7,'slit') for x in [-1.5,1.5])
    if sides and d>=8:
        for side in ['left','right']:openings[side].append((0,4,1,3,'window'))
    if not open_back and w>=10:openings['back'].append((0,4,1,3,'window'))
    for side,holes in openings.items():
        width=w if side in ['front','back'] else d-2
        lower=-width/2
        for a in holes:
            if a[0]-a[1]/2<lower or a[0]+a[1]/2>lower+width:raise ValueError(f'Opening outside {name}/{side}')
        for i,a in enumerate(holes):
            for b in holes[i+1:]:
                if (max(a[2],b[2])<=min(a[3],b[3]) and
                        min(a[0]+a[1]/2,b[0]+b[1]/2)>max(a[0]-a[1]/2,b[0]-b[1]/2)):
                    raise ValueError('Overlapping openings')
    for row in range(rows):
        m.step()
        for side in openings:
            if open_back and side=='back':continue
            n=w if side in ['front','back'] else d-2
            lower=-n/2
            blocked={i for i in range(n) if any(r0<=row<=r1 and cx-width/2<=lower+i<cx+width/2
                                             for cx,width,r0,r1,_ in openings[side])}
            i=0
            while i<n:
                if i in blocked:i+=1;continue
                end=i+1
                while end<n and end not in blocked:end+=1
                # Contrasting exposed corner piers; alternate runs bridge seams.
                colour=trim if timber and (row in [0,rows-1]) else body
                x=lower+i if side in ['front','back'] else (-w/2+.5 if side=='left' else w/2-.5)
                z=(-d/2+.5 if side=='front' else d/2-.5) if side in ['front','back'] else lower+i
                axis='x' if side in ['front','back'] else 'z'
                if timber:
                    for j in range(end-i):
                        c=trim if row in [0,rows-1] or (i+j)%4==0 or i+j==n-1 else body
                        line(m,x+j if axis=='x' else x,z if axis=='x' else z+j,1,8+(row+1)*24,c,axis=axis)
                else:
                    line(m,x,z,end-i,8+(row+1)*24,colour,axis=axis,
                         bond=bool(row%2),material=material if row<2 or material=='log' else None)
                i=end
    m.step()
    for side,holes in openings.items():
        if side=='back' and open_back:continue
        for centre,width,r0,_,kind in holes:
            if kind=='slit':continue
            module=door4(trim,70,door_style) if kind=='door' else window4(trim,glass)
            x=centre if side in ['front','back'] else (-w/2+.5 if side=='left' else w/2-.5)
            z=(-d/2+.5 if side=='front' else d/2-.5) if side in ['front','back'] else centre
            for dx in ([-2,2] if kind=='door' and width==8 else [0]):
                m.add(module,trim,x+dx,8+24*r0,z,yaw={'front':0,'back':180,'left':90,'right':-90}[side])
    top=8+rows*24
    m.step();ring(m,w,d,top+8,trim)
    m.anchor('roof',h=top+8).anchor('doorstep',door or 0,8,-d/2)
    return m


def gable(name,w=16,d=14,*,roof=72,gable_colour=19,tiers=None,dormer=False):
    """Supported slope courses; the shrinking core remains under every tier."""
    if w%2 or d%2 or min(w,d)<4:raise ValueError('Gable needs even dimensions >=4')
    m=Module(name,'Removable gabled roof: supported slope courses, contrasting gable core and tiled ridge')
    slab(m,-w/2,-d/2,w,d,8,gable_colour)
    tiers=tiers or d//2-1
    for level in range(tiers):
        m.step();h=8+24*(level+1)
        for x in range(-w//2+1,w//2,2):
            if not (dormer and level==0 and abs(x)<4):m.add('3039',roof,x,h,-d/2+1.5+level)
            m.add('3039',roof,x,h,d/2-1.5-level,yaw=180)
        depth=d-4-2*level
        for z in range(int(-depth/2),int(depth/2)):
            line(m,-w/2,z+.5,w,h,gable_colour,bond=bool(level%2))
    m.step();ridge_depth=d-2*tiers
    slab(m,-w/2,-ridge_depth/2,w,ridge_depth,8+24*tiers+8,roof,tile=True)
    if dormer:
        m.step()
        for x in [-3.5,3.5]:m.add('3040b',roof,x,32,-d/2+1.5)
        for x in [-1,1]:
            m.add('60592',15,x,56,-d/2+.5);m.add('60601',47,x,56,-d/2+.5)
        for x in [-2.5,2.5]:
            for h in [32,56]:m.add('3005',15,x,h,-d/2+.5)
        m.add('3795',15,0,64,-d/2+1)
        m.add('3039',roof,-1.5,88,-d/2+1,yaw=90)
        m.add('3039',roof,1.5,88,-d/2+1,yaw=-90)
        m.add('3003',roof,0,88,-d/2+1);m.add('3068b',roof,0,96,-d/2+1)
    m.anchor('ridge',h=8+24*tiers+8)
    return m


def flat_roof(name,w,d,c=15,accent=72):
    m=Module(name,'Flat lift-off roof with a low parapet and recessed quiet roof surface')
    slab(m,-w/2,-d/2,w,d,8,c)
    ring(m,w,d,32,c,plate=False)
    slab(m,-w/2+1,-d/2+1,w-2,d-2,16,accent,tile=True)
    ring(m,w,d,40,c)
    return m


def attach_roof(scene,shell,roof,x=0,h=0,z=0,*,id='building',colour=19):
    scene.add(shell,colour,x,h,z,id=id)
    scene.add(roof,colour,id=id+'-roof',attach={'to':id,'anchor':'roof','using':'base'})


def porch(name='porch',*,trim=15,roof=72,w=8,d=4,height=144):
    m=Module(f'{name}-{trim}-{roof}-{w}-{d}-{height}', 'Supported porch: base underside Y=0, entry at rear +Z; keep middle four studs clear')
    slab(m,-w/2,-d/2,w,d,8,trim)
    for x in [-w/2+.5,w/2-.5]:
        for z in [-d/2+.5,d/2-.5]:
            for row in range(height//24):m.add('3005',trim,x,8+24*(row+1),z)
    m.step();slab(m,-w/2,-d/2,w,d,8+height+8,roof)
    slab(m,-w/2,-d/2,w,d,8+height+16,roof,tile=True)
    m.anchor('entry',h=8,z=d/2).anchor('canopy',h=8+height+16)
    m.notes=['Centre on a real entrance; rear edge abuts the wall, not its centre plane.',
             'Match column trim to the building and keep the approach four studs wide.']
    return m


def bench(c=70):
    m=Module(f'bench-{c}','Four-stud garden/platform bench; bottom Y=0; front -Z')
    for x in [-1.5,1.5]:
        for z in [-.5,.5]:m.add('3005',0,x,24,z)
    slab(m,-2,-1,4,2,32,c)
    line(m,-2,.5,4,56,c)
    m.notes=['Face the view or path; leave a two-stud approach in front.', 'Use garden timber for rural scenes, dark frames for transport scenes.']
    return m


def tree(c=288,flower=5):
    m=Module(f'leaf-tree-{c}-{flower}','Layered garden tree; bottom Y=0; foliage needs a nine-stud clearing')
    slab(m,-2,-2,4,4,8,19)
    slab(m,-1,-1,2,2,16,70)
    for i in range(5):m.add('3062b',70,-.5,40+24*i,-.5)
    for i,(ref,yaw) in enumerate([('2417',0),('2417',90),('2423',180),('2423',0)]):
        m.add(ref,c if i%2==0 else 2,-.5,144+32*i,-.5,yaw=yaw)
        if i<3:m.add('3062b',70,-.5,168+32*i,-.5)
    for x in [-1.5,.5,1.5]:m.add('24866',flower,x,16,-1.5)
    m.anchor('trunk',-.5,136,-.5)
    m.notes=['Reserve a nine-stud canopy clearing rather than only the four-stud plinth.',
             'Frame a building asymmetrically; do not put foliage across its focal entrance.']
    return m


def lamp():
    m=Module('fluted-lamp','Fluted lamppost with warm lantern; bottom Y=0, 2x2 stud foot')
    m.add('3022',0,h=8);m.add('2039',0,h=176);m.add('6141',297,h=184)
    m.add('3062b',46,h=208);m.add('4740',0,h=216);m.add('4589',0,h=240)
    m.notes=['Place beside the path, outside a door swing and away from important lettering.',
             'Best with traditional town, station or civic architecture; use the beacon for a space base.']
    return m


def planter(c=5):
    m=Module(f'flower-box-{c}','Four by two stud planter with flowers; bottom Y=0')
    m.add('3020',72,h=8)
    for x in [-1.5,-.5,.5,1.5]:
        m.add('3062b',2,x,32,.5);m.add('24866',c,x,40,.5)
        m.add('3005',19,x,32,-.5)
    return m


def stairs(w=4,rises=3):
    m=Module(f'stairs-{w}-{rises}','Supported steps, 8 LDU rise and one-stud tread; front -Z')
    for i in range(rises):slab(m,-w/2,-rises/2+i,w,rises-i,8*(i+1),71)
    m.anchor('landing',h=8*rises,z=rises/2)
    m.notes=['The landing must meet the destination deck exactly; reserve the approach before paving.']
    return m


def fence(w=8,c=70):
    m=Module(f'fence-{w}-{c}','Supported garden fence; underside Y=0; do not cross circulation routes')
    for x in [-w/2+.5,w/2-.5]:
        m.add('3005',c,x,24,.5);m.add('3005',c,x,48,.5)
    line(m,-w/2,.5,w,56,c,plate=True)
    m.notes=['Footprint is X=-w/2..w/2, Z=0..1; both posts lie on the site stud lattice.']
    return m


def beacon():
    m=Module('landing-beacon','Low blue landing beacon; functional industrial lighting')
    m.add('3022',72,h=8);m.add('3941',15,h=32);m.add('3941',43,h=56);m.add('4740',72,h=64)
    return m


def utility_stack():
    m=Module('utility-stack','Banded industrial chimney on a 4x4 stud equipment plinth')
    slab(m,-2,-2,4,4,8,72)
    for row in range(9):m.add('3941',71 if row%3 else 72,h=32+24*row)
    m.add('4740',72,h=232)
    return m


def fountain():
    m=Module('garden-fountain','Six-stud pool and central water column; base Y=0, front -Z')
    slab(m,-3,-3,6,6,8,71);ring(m,6,6,32,71,plate=False);ring(m,6,6,40,19)
    for x in [-1.5,-.5,.5,1.5]:
        for z in [-1.5,-.5,.5,1.5]:
            if abs(x)>.5 or abs(z)>.5:m.add('3070b',43,x,16,z)
    m.add('3941',71,h=32);m.add('3941',43,h=56);m.add('4740',43,h=64);m.add('6141',43,h=72)
    m.notes=['Reserve a six-stud pool plus pedestrian clearance.',
             'Use as a secondary focal point in a garden court, away from the main doorway axis.']
    return m


def solar_array():
    m=Module('solar-array','Eight by four stud static solar rack; base Y=0; all panels rest on real supports')
    for x in [-3,3]:
        for z in [-1,1]:m.add('3003',72,x,24,z)
    slab(m,-4,-2,8,4,32,72)
    for x in [-2,2]:
        for z in [-1.5,-.5,.5,1.5]:m.add('2431p70',272,x,40,z)
    m.notes=['Reserve an eight-by-four equipment footprint on bare studs.',
             'Group beside a habitat or workshop; avoid using the panel as unrelated façade ornament.']
    return m
