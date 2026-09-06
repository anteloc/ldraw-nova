"""Original Copper Lane streetscape; generate editable modular JSON, then use build.

No OMR geometry is copied. Window/door origins are verified against the supplied
library; door pivot alignment is also evidenced in 10270-1.mpd lines 3919–3921.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

AUTHOR = "ldraw-astra example generator"


def place(id, ref, colour, at=None, **kw):
    return dict(id=id, ref=ref+'.dat' if '.' not in ref else ref, colour=colour,
                **({'at':at} if at is not None else {}), **kw)


def section(name, description, steps, anchors=None):
    return dict(name=name+'.ldr', description=description, steps=steps,
                **({'anchors':anchors} if anchors else {}))


def write(path, sections, **kw):
    path.write_text(json.dumps(dict(version=1,author=AUTHOR,sections=sections,**kw),indent=2)+'\n')


def floor(name, ground=False, interior=False):
    steps = [[place('deck','91405',70,[0,0,0])]]
    # A running bond of 1x1/1x2 bricks. Front and rear own the corner studs.
    for row in range(6):
        entries=[]
        for side in ['front','back','left','right']:
            n=16 if side in ['front','back'] else 14
            blocked=set()
            if side=='front':
                if ground:
                    blocked.update(range(2,6))  # six-brick-high door
                    if row in (1,2,3,4):blocked.update([9,10,13,14])
                elif row in (1,2,3,4):blocked.update([2,3,7,8,12,13])
            if side=='back' and row in (1,2,3,4):blocked.update([3,4,11,12])
            i=0
            while i<n:
                if i in blocked:i+=1;continue
                width=2 if i+1<n and i+1 not in blocked and (i>0 or row%2==0) else 1
                along=-150+20*i+10*(width-1)+(20 if side in ['left','right'] else 0)
                x,z=(along,-150) if side=='front' else (along,150) if side=='back' else (-150,along) if side=='left' else (150,along)
                entries.append(place(f'{side}-{row}-{i}','3004' if width==2 else '3005',15 if row==5 else 16,[x,-24*(row+1),z],yaw=90 if side in ['left','right'] else 0))
                i+=width
        steps.append(entries)
    windows=[]
    front=[40,120] if ground else [-100,0,100]
    for side,centres,z,yaw in [('front',front,-150,0),('back',[-80,80],150,180)]:
        for i,x in enumerate(centres):windows.append(place(f'{side}-window-{i}','lane-window.ldr',15,[x,-72,z],yaw=yaw))
    if ground:
        windows.append(place('entrance','lane-door.ldr',15,[-80,-144,-150]))
    steps.append(windows)
    steps.append([place('front-cornice','3460',15,[-80,-152,-150],repeat={'count':2,'step':[160,0,0]}),
                  place('rear-cornice','3460',15,[-80,-152,150],repeat={'count':2,'step':[160,0,0]}),
                  place('left-cornice','3666',15,[-150,-152,-60],yaw=90,repeat={'count':2,'step':[0,0,120]}),
                  place('right-cornice','3666',15,[150,-152,-60],yaw=90,repeat={'count':2,'step':[0,0,120]}),
                  *[place(f'corner-cap-{x}-{z}','3024',15,[x,-152,z]) for x in [-150,150] for z in [-130,130]]])
    if interior:
        steps.append([place('bookcase','lane-bookcase.ldr',70,[-80,0,110]),place('reading-table','lane-table.ldr',70,[40,0,0])])
    return section(name,'Lift-off storey with bonded walls, glazed windows and cornice',steps,
                   {'base':{'at':[0,8,0]},'next':{'at':[0,-152,0]}})


def roof():
    steps=[[place('deck','91405',70,[0,0,0])]]
    for tier in range(4):
        front=-130+20*tier
        entries=[place(f'front-{tier}','3039',16,[-140,-24*(tier+1),front],repeat={'count':8,'step':[40,0,0]}),
                 place(f'back-{tier}','3039',16,[-140,-24*(tier+1),-front],yaw=180,repeat={'count':8,'step':[40,0,0]})]
        # Solid support beneath the sloping roof courses; no floating slope strips.
        for j in range(6-tier):
            z=-100+20*tier+40*j
            entries.append(place(f'fill-{tier}-{j}','3007',16,[-80,-24*(tier+1),z],repeat={'count':2,'step':[160,0,0]}))
        steps.append(entries)
    steps.append([place(f'top-tile-{x}-{z}','3068b',16,[x,-104,z]) for z in [-40,0,40] for x in range(-140,141,40) if (x,z)!=(100,40)])
    # Chimney uses an exposed pair of studs at the rear roof edge.
    steps.append([place('chimney','3003',71,[100,-120,60],repeat={'count':3,'step':[0,-24,0]}),place('chimney-cap','3022',0,[100,-176,60])])
    return section('lane-roof','Four-course sloped roof with supported core and chimney',steps,{'base':{'at':[0,8,0]}})


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--outdir',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--floors',type=int,default=3,choices=range(2,6))
    args=parser.parse_args();args.outdir.mkdir(parents=True,exist_ok=True)
    window=section('lane-window','Two stacked window frames with matching glazing',[[place('frame','60592',16,[0,0,0],repeat={'count':2,'step':[0,-48,0]}),place('glass','60601',47,[0,0,0],repeat={'count':2,'step':[0,-48,0]})]])
    door=section('lane-door','Glazed entrance with a closed hinged door',[[place('frame','60596',16,[0,0,0]),place('door','60623',2,[-32,0,5])]])
    bookcase=section('lane-bookcase','Three shelf bookcase with coloured brick books',[
        [place('left','3005',16,[-50,-24,0],repeat={'count':3,'step':[0,-32,0]}),place('right','3005',16,[50,-24,0],repeat={'count':3,'step':[0,-32,0]})],
        [place('shelves','3666',16,[0,-32,0],repeat={'count':3,'step':[0,-32,0]})],
        [place(f'books-{j}','3005',c,[-30,-24-32*j,0],repeat={'count':4,'step':[20,0,0]}) for j,c in enumerate([4,1,2])]])
    table=section('lane-table','Reading table on four legs',[[place(f'leg-{x}-{z}','3005',16,[x,-24,z]) for x in [-30,30] for z in [-10,10]], [place('top','3020',16,[0,-32,0])]])
    tree=section('lane-tree','Brick-built ornamental tree in a square planter',[
        [place('planter','3031',70,[0,-8,0]),place('trunk','3062b',70,[-10,-32,-10],repeat={'count':6,'step':[0,-24,0]})],
        [place('canopy','3020',2,[0,-160,0]),place('crown','3003',2,[0,-184,0]),place('crown-cap','3022',10,[0,-192,0])]])
    lamp=section('lane-lamp','Street lamp with round column and translucent lantern',[
        [place('foot','3022',0,[0,-8,0]),place('shaft','3941',0,[0,-32,0],repeat={'count':5,'step':[0,-24,0]})],
        [place('lantern','3003',46,[0,-152,0]),place('cap','3022',0,[0,-160,0])]])
    write(args.outdir/'details.plan.json',[window,door,bookcase,table,tree,lamp])
    write(args.outdir/'buildings.plan.json',[floor('lane-ground',True,True),floor('lane-upper',False,True),roof()],includes=['details.plan.json'])
    scene=[place('base','3811',71,[0,0,0])]
    for z in [-300,-260,-220,-180,-140,-100]:
        # Leave exposed studs for the planters and lamps; avoid tile/fixture overlap.
        for x in range(-300,301,40):
            if z in [-260,-220] and x in [-300,-260,260,300]:continue
            if z==-140 and x in [-220,220]:continue
            scene.append(place(f'paving-{x}-{z}','3068b',72 if z==-300 else 71,[x,-8,z]))
    steps=[scene]
    for label,x,colour in [('bookshop',-160,19),('townhouse',160,3)]:
        stack=[place(label+'-ground','lane-ground.ldr',colour,[x,-8,80])]
        previous=label+'-ground'
        for i in range(1,args.floors if label=='bookshop' else args.floors-1):
            id=f'{label}-floor-{i}'
            stack.append(place(id,'lane-upper.ldr',colour,attach={'to':previous,'anchor':'next','using':'base'}));previous=id
        stack.append(place(label+'-roof','lane-roof.ldr',320 if label=='bookshop' else 272,attach={'to':previous,'anchor':'next','using':'base'}))
        # Placement IDs and attachment targets are local to a SECTION, across its steps.
        steps.append(stack)
    steps.append([place('left-tree','lane-tree.ldr',2,[-280,0,-240]),place('right-tree','lane-tree.ldr',2,[280,0,-240]),
                  place('lamps','lane-lamp.ldr',0,[-220,0,-140],repeat={'count':2,'step':[440,0,0]})])
    write(args.outdir/'scene.plan.json',[section('copper-lane','Copper Lane bookshop and townhouse streetscape',steps)],includes=['buildings.plan.json'])
    print(args.outdir/'scene.plan.json')


if __name__=='__main__':main()
