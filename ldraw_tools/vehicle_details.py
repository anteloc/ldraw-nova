"""Reusable vehicle fittings using dedicated library parts and explicit interfaces."""
from .architecture import Module
from .details import palettes

DETAILS = {
    'driver-cockpit': dict(description='Moulded seat, actual steering stand/wheel and printed dashboard on a two-by-six stud floor.',
                           parts=['4079','3829c01','3069bp25'], footprint_studs=[2,6], height_ldu=56,
                           interface='Base underside Y=0; front -Z. Seat back projects to Z=45; reserve the whole cabin before adding glazing.'),
    'pilot-cockpit': dict(description='Moulded pilot seat, hinged control stick and printed instrument slope on a two-by-eight stud floor.',
                          parts=['4079','4592','4593','3039p34'], footprint_studs=[2,8], height_ldu=56,
                          interface='Base underside Y=0, front -Z. Control stick is in a static upright pose; instrument slope fills the forward two rows.'),
    'wing-mirror': dict(description='Compact side mirror on a headlight-brick mount, with a real sideways tile attachment.',
                        parts=['4070','3070b'], footprint_studs=[1,1], height_ldu=36,
                        interface='Base underside Y=0, mirror faces -Z and projects to Z=-14; yaw the complete module to face outwards.'),
    'cargo-chest': dict(description='Purpose-made open cargo chest with moulded handles, mounted on a three-by-four stud pallet.',
                        parts=['30150'], footprint_studs=[3,4], height_ldu=52,
                        interface='Base underside Y=0; odd-width X lattice (use a half-stud centre offset on even-width decks). Remove floor tiles at the attachment.'),
    'navigation-lights': dict(description='Paired red port and green starboard lights on a slender four-stud crossbar.',
                              parts=['6141'], footprint_studs=[4,1], height_ldu=20,
                              interface='Base underside Y=0; -Z forward, red on -X and green on +X. Not a navigation-light compliance claim.'),
    'jet-engine-pod': dict(description='Purpose-made cylindrical aircraft engine with matching internal core and top attachment plate.',
                           parts=['4868b','4869'], footprint_studs=[2,5], height_ldu=50,
                           interface='Attachment stud body plane Y=0; engine hangs below it to Y=46. Intake faces -Z; attach below a wing socket plane.'),
}


def vehicle_colours(palette):
    available=palettes()
    if palette not in available or available[palette].get('family')!='vehicle':
        raise ValueError('Choose a vehicle palette: '+', '.join(k for k,v in available.items() if v.get('family')=='vehicle'))
    return available[palette]['roles']


def detail_module(name, palette='heritage-racing'):
    if name not in DETAILS:
        raise ValueError('Unknown vehicle detail; use vehicle details')
    c=vehicle_colours(palette)
    m=Module(f'vehicle-{name}-{palette}', DETAILS[name]['description'])
    if name in {'driver-cockpit','pilot-cockpit'}:
        pilot=name=='pilot-cockpit'
        m.add('3034' if pilot else '3795',c['chassis'],h=8,yaw=90,id='floor')
        m.add('4079',c['wood'],h=16,z=2 if pilot else 1,id='seat')
        m.step()
        if pilot:
            m.add('3039p34',c['chassis'],h=32,z=-2.5,id='instruments')
            m.add('4592',c['metal'],-.5,16,-.5,id='stick-base')
            m.add('4593',c['chassis'],-.5,16,-.5,id='control-stick')
        else:
            m.add('3829c01',c['chassis'],h=16,z=-1.5,id='steering')
            m.add('3069bp25',c['chassis'],h=16,z=-2.5,id='instruments')
        m.anchor('seat',h=16,z=2 if pilot else 1)
    elif name=='wing-mirror':
        m.add('3024',c['body'],h=8)
        m.add('4070',c['body'],h=32)
        m.add('3070b',c['metal'],h=22,z=-.7,matrix=[[1,0,0],[0,0,-1],[0,1,0]])
    elif name=='cargo-chest':
        for z in [-1,1]:m.add('3021',c['chassis'],h=8,z=z)
        m.add('30150',c['wood'],h=16)
    elif name=='navigation-lights':
        m.add('3710',c['roof'],h=8)
        for sign,colour in [(-1,'@colours.Trans_Red'),(1,'@colours.Trans_Green')]:
            m.add('6141',colour,sign*1.5,16)
        m.add('3069b',c['metal'],h=16)
    else:
        # 4868b's top stud body plane is local Y=-26; concentric core is
        # native-origin aligned, as in official 4868b/4869 geometry.
        m.add('4868b',c['roof'],h=-26,id='engine-shell')
        m.add('4869',c['metal'],h=-26,id='engine-core')
        m.anchors={'mount':{'at':[0,0,0]}}
    return m


def detail_plan(name, palette='heritage-racing'):
    plan=detail_module(name,palette).plan()
    plan['author']='ldraw-nova vehicle detail recipes'
    return plan
