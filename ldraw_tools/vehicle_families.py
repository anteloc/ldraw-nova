"""Vehicle families whose construction is not a car chassis with a different body."""
from .architecture import Module
from .vehicle_details import detail_module, vehicle_colours
from .vehicles import smooth_deck


def motorcycle(palette):
    c=vehicle_colours(palette)
    m=Module('touring-motorcycle','Vintage System motorcycle; front -Z, both tyres meet Y=0')
    # 85983c01 -> 50859bc01 -> 50862c01 establishes these fitting offsets.
    # Use proper yaw rotations for the symmetric wheels, not the shortcut's
    # legacy reflected wheel matrix. Tyre radius includes its actual tread.
    radius=26.614
    frame_h=radius-3.7
    body_h=frame_h+41.5
    m.add('50859b',c['chassis'],h=frame_h,z=-.5,id='frame-and-handlebars')
    m.add('85983',c['body'],h=body_h,z=2.5,id='vintage-fairing')
    m.step()
    for label,z in [('front',-53.5),('rear',53.5)]:
        m.add('50862',c['metal'],h=radius,z=z/20,yaw=90,id=label+'-rim')
        m.add('50861',256,h=radius,z=z/20,yaw=90,id=label+'-tyre')
    m.step()
    m.add('3839b',c['metal'],h=body_h+8,z=2.5,yaw=90,id='luggage-rack')
    m.add('3069b',c['wood'],h=body_h+16,z=2.5,yaw=90,id='rack-pad')
    m.anchor('rack',h=body_h+8,z=2.5)
    return m


def launch(palette):
    c=vehicle_colours(palette)
    m=Module('harbour-launch','Open harbour launch; hull floor datum Y=0, front -Z; no buoyancy claim')
    m.add('2551',c['body'],id='moulded-hull')
    m.add('3035',c['roof'],h=8,z=1,yaw=90,id='cockpit-deck')
    m.step()
    m.add('3823',c['glass'],h=56,z=-1.5,id='windscreen')
    m.add('4079',c['wood'],h=16,z=1,id='helmsman-seat')
    m.add('3829c01',c['chassis'],h=16,z=-.5,id='helm')
    m.add('3069bp25',c['chassis'],h=16,z=-1.5,id='instruments')
    m.add(detail_module('navigation-lights',palette),c['roof'],h=56,z=-1.5,id='navigation-lights')
    m.step()
    m.add('30340','@colours.Orange',.5,16,4.5,id='life-ring')
    m.add('6141',c['metal'],h=48,z=-7.5,id='bow-marker')
    return m


def jet(palette):
    c=vehicle_colours(palette)
    m=Module('courier-jet','Twin-engine courier aircraft; fuselage floor datum Y=0; displayed in flight, front -Z')
    m.add('87611',c['body'],z=-1,id='nose-bottom')
    m.add('87613',c['roof'],h=96,id='nose-shell')
    m.add('87612',c['glass'],h=96,id='matched-cockpit-glass')
    # The centre floor ties the moulded nose and rear interfaces together.
    m.add('3032',c['body'],h=0,z=3,id='centre-floor')
    m.add('2445',c['chassis'],h=-24,z=4,yaw=90,id='underbody-bond')
    m.add('3021',c['chassis'],h=-16,z=2.5,yaw=90,id='wing-root-support')
    m.add('3003',c['chassis'],h=0,z=7,id='rear-interface-support')
    m.add('87616',c['roof'],h=96,z=7,id='tapered-rear')
    m.step()
    # Nose floor studs run at local Y=0; seat and instruments have real bases.
    m.add('4079',c['wood'],h=8,z=-3,id='pilot-seat')
    m.add('3039p34',c['chassis'],h=24,z=-5.5,id='instrument-panel')
    m.add('4592',c['metal'],-.5,8,-4.5,id='stick-base')
    m.add('4593',c['chassis'],-.5,8,-4.5,id='control-stick')
    # Four-stud fuselage centre with real plane windows and a removable cap.
    for x in [-2.5,2.5]:
        # Nose side pockets stop 24 LDU below its top; fill to that measured
        # plane, rather than treating the entire moulding as a solid box.
        m.add('3245a',c['roof'],x,48,0,yaw=90)
        for h in [56,64,72]:m.add('3023b',c['roof'],x,h,0,yaw=90)
        m.add('3010',c['body'],x,24,3,yaw=90)
        for z in [2,4,6]:
            m.add('2377',c['roof'],x,72,z,yaw=90 if x<0 else -90)
    m.add('32083',c['roof'],h=96,z=3,yaw=90,id='shaped-cabin-roof')
    # 3039 spans local Z=-30..10: its origin is not the footprint centre.
    for sign in [-1,1]:m.add('3039',c['roof'],sign*1.5,96,6,yaw=-90*sign)
    m.add('3003',c['roof'],h=96,z=6)
    smooth_deck(m,4,1,6,104,c['roof'])
    m.step()
    # Turn the genuine left/right wing pair so its long span runs across X.
    # The root rows lie under the centre-floor sockets; plates on top bridge
    # their junction into the fuselage, with no stretched or mirrored parts.
    m.add('30355',c['body'],-6,-8,3,yaw=90,id='port-wing')
    m.add('30356',c['body'],6,-8,3,yaw=-90,id='starboard-wing')
    for sign in [-1,1]:
        m.add(detail_module('jet-engine-pod',palette),c['roof'],sign*5,-16,3,id='port-engine' if sign<0 else 'starboard-engine')
    # Tail plane has stepped underside sockets; a 2x2 pedestal carries the
    # lowest pair, leaving the other stepped interfaces clear.
    m.add('3022',c['body'],h=104,z=13)
    m.add('4867',c['roof'],h=128,z=10.5,id='tail-plane')
    m.add('3936',c['roof'],-2,208,15,yaw=90,id='port-stabilizer')
    m.add('3935',c['roof'],2,208,15,yaw=-90,id='starboard-stabilizer')
    m.add('3068b',c['roof'],h=216,z=16,id='tail-cap')
    m.anchor('floor',z=3)
    return m


def family_model(name,palette):
    return {'touring-motorcycle':motorcycle,'harbour-launch':launch,'courier-jet':jet}[name](palette)
