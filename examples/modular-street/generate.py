"""Original Copper Lane streetscape; generate editable modular JSON, then use build.

No OMR geometry is copied. Window/door origins are verified against the supplied
library; door pivot alignment is also evidenced in 10270-1.mpd lines 3919–3921.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from ldraw_tools.details import palettes, detail_section

AUTHOR = "ldraw-nova example generator"


def place(id, ref, colour, at=None, **kw):
    return dict(id=id, ref=ref+'.dat' if '.' not in ref and not ref.startswith('@') else ref, colour=colour,
                **({'at':at} if at is not None else {}), **kw)


def section(name, description, steps, anchors=None):
    return dict(name=name+'.ldr', description=description, steps=steps,
                **({'anchors':anchors} if anchors else {}))


def write(path, sections, **kw):
    path.write_text(json.dumps(dict(version=1,author=AUTHOR,sections=sections,**kw),indent=2)+'\n')


def floor(name, ground=False, interior=False, palette='botanical-bookshop', shop=False):
    c=palettes()[palette]['roles']
    steps=[[place('deck','91405',c['wood'],[0,0,0])]]
    door_cells=set(range(1,5)) if shop else set(range(2,6))
    bay_cells=set(range(1,7))|set(range(9,15))
    for row in range(6):
        entries=[]
        for side in ['front','back','left','right']:
            n=16 if side in ['front','back'] else 14
            blocked=set()
            if side=='front':
                if ground and shop:blocked=door_cells|set(range(6,10))|set(range(11,15))
                elif ground:
                    blocked=door_cells|(set(range(9,15)) if row else set())
                elif row:blocked=bay_cells
            if side=='back' and row in (1,2,3,4):blocked.update([3,4,11,12])
            if side==('left' if palette=='botanical-bookshop' else 'right') and row in (1,2,3,4):blocked.update([3,4,9,10])
            i=0
            while i<n:
                if i in blocked:i+=1;continue
                width=2 if i+1<n and i+1 not in blocked and (i>0 or row%2==0) else 1
                along=-150+20*i+10*(width-1)+(20 if side in ['left','right'] else 0)
                x,z=(along,-150) if side=='front' else (along,150) if side=='back' else (-150,along) if side=='left' else (150,along)
                ref='@bricks.Brick1X2WithEmbossedBricks' if width==2 and row in (0,1) else '3004' if width==2 else '3005'
                colour=c['trim'] if side=='front' and (i in (0,15) or ground and shop) else c['body']
                entries.append(place(f'{side}-{row}-{i}',ref,colour,[x,-24*(row+1),z],yaw=90 if side in ['left','right'] else 0))
                i+=width
        steps.append(entries)
    windows=[place(f'back-window-{x}','lane-window.ldr',15,[x,-72,150],yaw=180) for x in [-80,80]]
    windows.extend(place(f'side-window-{z}','lane-window.ldr',c['trim'],[-150 if palette=='botanical-bookshop' else 150,-72,z],yaw=90 if palette=='botanical-bookshop' else -90) for z in [-60,60])
    bay_ref='detail-arched-window.ldr' if palette=='botanical-bookshop' else 'lane-house-window.ldr'
    if ground:
        windows.append(place('entrance','lane-door.ldr' if shop else 'lane-house-door.ldr',c['shopfront'],[-100 if shop else -80,-144,-150]))
        if shop:
            for x in [0,100]:
                windows.extend([place(f'display-frame-{x}','@doors.Door1X4X6Frame',c['shopfront'],[x,-144,-150]),
                                place(f'display-glass-{x}','@others.GlassForWindow1X4X6',c['glass'],[x,-139,-145])])
        else:windows.append(place('front-bay',bay_ref,c['trim'],[80,-24,-150]))
    else:
        windows.extend([place(f'front-bay-{x}',bay_ref,c['trim'],[x,-24,-150]) for x in [-80,80]])
    steps.append(windows)
    # Eight-LDU shim aligns ordinary walls with the 128-LDU ornamental bays.
    for y in [-152,-160]:
        rim=[place(f'back-band-{y}','3460',c['trim'],[-80,y,150],repeat={'count':2,'step':[160,0,0]}),
             place(f'left-band-{y}','3666',c['trim'],[-150,y,-60],yaw=90,repeat={'count':2,'step':[0,0,120]}),
             place(f'right-band-{y}','3666',c['trim'],[150,y,-60],yaw=90,repeat={'count':2,'step':[0,0,120]}),
             *[place(f'corner-{y}-{x}-{z}','3024',c['trim'],[x,y,z]) for x in [-150,150] for z in [-130,130]]]
        if y==-160:
            rim.append(place('projecting-cornice','3034',c['trim'],[-80,y,-160],repeat={'count':2,'step':[160,0,0]}))
        elif ground and shop:
            rim.append(place('lintel-course','3460',c['trim'],[-80,y,-150],repeat={'count':2,'step':[160,0,0]}))
        else:
            occupied=set(range(9,15)) if ground else bay_cells
            rim.extend(place(f'front-shim-{i}','3024',c['trim'],[-150+20*i,y,-150]) for i in range(16) if i not in occupied)
        steps.append(rim)
    if ground and shop:
        steps.append([place('awning-left','detail-striped-awning.ldr',15,[-80,-160,-170]),
                      place('awning-right','detail-striped-awning.ldr',15,[80,-160,-170]),
                      place('book-emblem','detail-book-sign.ldr',15,[0,-192,-180])])
    if interior:
        steps.append([place('bookcase','lane-bookcase.ldr',c['wood'],[-80,0,110]),place('reading-table','lane-table.ldr',c['wood'],[40,0,0])])
    return section(name,'Ornamental storey with carved window bays, masonry base and projecting cornice',steps,
                   {'base':{'at':[0,8,0]},'next':{'at':[0,-160,0]}})

def roof(name='lane-roof', dormer=True):
    steps=[[place('deck','91405',70,[0,0,0])]]
    for tier in range(4):
        front=-130+20*tier
        entries=[place(f'front-{tier}-{x}','3039',16,[x,-24*(tier+1),front]) for x in range(-140,141,40) if not (dormer and tier==0 and abs(x)<80) and (dormer or tier>0)]
        entries.append(place(f'back-{tier}','3039',16,[-140,-24*(tier+1),-front],yaw=180,repeat={'count':8,'step':[40,0,0]}))
        # Solid support beneath the sloping roof courses; no floating slope strips.
        for j in range(6-tier):
            z=-100+20*tier+40*j
            entries.append(place(f'fill-{tier}-{j}','3007',16,[-80,-24*(tier+1),z],repeat={'count':2,'step':[160,0,0]}))
        steps.append(entries)
    steps.append([place(f'top-tile-{x}-{z}','3068b',16,[x,-104,z]) for z in [-40,0,40] for x in range(-140,141,40) if (x,z)!=(100,40)])
    # Chimney uses an exposed pair of studs at the rear roof edge.
    steps.append([place('chimney','3003',71,[100,-120,60],repeat={'count':3,'step':[0,-24,0]}),place('chimney-cap','3022',0,[100,-176,60])])
    if dormer:
        steps.append([place('dormer-frame','60592',15,[-20,-48,-150],repeat={'count':2,'step':[40,0,0]}),
                      place('dormer-glass','60601',47,[-20,-48,-150],repeat={'count':2,'step':[40,0,0]}),
                      *[place(f'dormer-pier-{x}','3005',15,[x,-24,-150],repeat={'count':2,'step':[0,-24,0]}) for x in [-50,50]],
                      place('dormer-cap','3795',15,[0,-56,-140]),
                      place('dormer-roof-left','3039',16,[-30,-80,-140],yaw=90),place('dormer-roof-right','3039',16,[30,-80,-140],yaw=-90),
                      place('dormer-roof-centre','3003',16,[0,-80,-140]),place('dormer-ridge','3068b',16,[0,-88,-140])])
    else:
        steps.append([place('front-roof-core','3008',16,[-80,-24,-130],repeat={'count':2,'step':[160,0,0]})])
        # A stepped street-facing pediment and clock distinguish the lower house.
        for row,width in enumerate([16,12,8,4]):
            steps.append([place(f'pediment-{row}-{x}','3004',19,[x,-24*(row+1),-150]) for x in range(-width*10+20,width*10,40)])
        steps.append([place('clock','3003p0b',19,[0,-120,-140]),place('clock-cap','3022',19,[0,-128,-140])])
    return section(name,'Supported roof with dormer or stepped clock pediment',steps,{'base':{'at':[0,8,0]}})


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
    details=[window,door,bookcase,table]
    house_door=json.loads(json.dumps(door));house_door['name']='lane-house-door.ldr'
    house_door['steps'][0][1]['colour']='@colours.Reddish_Brown'
    details.append(house_door)
    for name in ['arched-window','striped-awning','flower-planter','book-sign']:
        details.append(detail_section(name))
    house_window=detail_section('arched-window','rose-townhouse');house_window['name']='lane-house-window.ldr'
    details.append(house_window)
    tall_tree=detail_section('flower-planter','rose-townhouse');tall_tree['name']='lane-tall-tree.ldr'
    for piece in tall_tree['steps'][1]:piece['at'][1]-=48
    tall_tree['steps'][1].insert(0,place('lower-trunk','3062b',70,[-10,-40,-10],repeat={'count':2,'step':[0,-24,0]}))
    details.append(tall_tree)
    lamp=section('lane-lamp','Fluted street lamp with brass collar and a translucent lantern',[[
        place('foot','3022',0,[0,-8,0]),place('fluted-column','@supports.Support2X2X7LamppostWith6BaseFlutes',0,[0,-176,0]),
        place('collar','6141',297,[0,-184,0]),place('lantern','3062b',46,[0,-208,0]),
        place('shade','4740',0,[0,-216,0]),place('finial','4589',0,[0,-240,0])]])
    details.append(lamp)
    write(args.outdir/'details.plan.json',details)
    write(args.outdir/'buildings.plan.json',[
        floor('lane-ground',True,True,shop=True),floor('lane-upper',False,True),
        floor('lane-house-ground',True,True,palette='rose-townhouse'),floor('lane-house-upper',False,True,palette='rose-townhouse'),
        roof(),roof('lane-house-roof',False)],includes=['details.plan.json'])
    scene=[place('base','3811',71,[0,0,0])]
    for z in [-300,-260,-220,-180,-140,-100]:
        # Leave exposed studs for the planters and lamps; avoid tile/fixture overlap.
        for x in range(-300,301,40):
            if z in [-260,-220] and x in [-300,-260,260,300]:continue
            if z==-140 and x in [-220,220]:continue
            scene.append(place(f'paving-{x}-{z}','3068b',72 if z==-300 else 71,[x,-8,z]))
    steps=[scene]
    for label,x,colour in [('bookshop',-160,'@colours.Tan'),('townhouse',160,'@colours.Sand_Green')]:
        stack=[place(label+'-ground','lane-ground.ldr' if label=='bookshop' else 'lane-house-ground.ldr',colour,[x,-8,80])]
        previous=label+'-ground'
        for i in range(1,args.floors if label=='bookshop' else args.floors-1):
            id=f'{label}-floor-{i}'
            stack.append(place(id,'lane-upper.ldr' if label=='bookshop' else 'lane-house-upper.ldr',colour,attach={'to':previous,'anchor':'next','using':'base'}));previous=id
        stack.append(place(label+'-roof','lane-roof.ldr' if label=='bookshop' else 'lane-house-roof.ldr','@colours.Dark_Blue' if label=='bookshop' else '@colours.Dark_Red',attach={'to':previous,'anchor':'next','using':'base'}))
        # Placement IDs and attachment targets are local to a SECTION, across its steps.
        steps.append(stack)
    steps.append([place('left-tree','detail-flower-planter.ldr',2,[-280,0,-240]),place('right-tree','lane-tall-tree.ldr',2,[280,0,-240]),
                  place('lamps','lane-lamp.ldr',0,[-220,0,-140],repeat={'count':2,'step':[440,0,0]})])
    write(args.outdir/'scene.plan.json',[section('copper-lane','Leaf and Letter: botanical bookshop and Rose House on Copper Lane',steps)],includes=['buildings.plan.json'])
    print(args.outdir/'scene.plan.json')


if __name__=='__main__':main()
