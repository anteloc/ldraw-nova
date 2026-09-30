"""System vehicles: measured running gear and editable family-specific plans.

X is width, -Z is forward, Y=0 is the road. Authoring helpers use X/Z studs
and h upwards in LDU, exactly like Module. No complete part is scaled/mirrored.
"""
from __future__ import annotations

from .architecture import Module, slab, line, lengths, WIDE_PLATES
from .common import jsonable
from .vehicle_details import detail_module, vehicle_colours


WHEEL_PACKS = {
    'classic': dict(holder='4600', rim='4624', tyre='3641', radius=18.0,
                    rim_x=30.0, tyre_x=30.0, holder_stud_y=0.0,
                    tyre_offset=0.0, source='4624c01.dat',
                    description='Small wheel-pin running gear for compact four-stud bodies.'),
    'touring': dict(holder='6157', rim='6014b', tyre='6015', radius=25.0,
                    rim_x=40.0, tyre_x=46.0, holder_stud_y=8.0,
                    tyre_offset=-6.0, source='6014bc01.dat',
                    description='Extended wheel pins, separate rims and wide tyres for six-stud bodies.'),
}

DESIGNS = {
    'grand-tourer': dict(title='Grand tourer', palette='heritage-racing', length=18, wheelbase=10,
                        lesson='Long sculpted bonnet, inset low cabin, continuous shoulders and a short rear deck.'),
    'delivery-van': dict(title='Delivery van', palette='coastal-delivery', length=18, wheelbase=10,
                        lesson='Short bonnet, upright cab and a taller quiet cargo box with a restrained belt line.'),
    'pickup': dict(title='Workshop pickup', palette='desert-utility', length=20, wheelbase=12,
                   lesson='Separate cab and open load bed, capped bed rails, contrasting bumpers and functional cargo space.'),
    'tipper-truck': dict(title='Site tipper truck', palette='desert-utility', length=22, wheelbase=14,
                        profile='road', lesson='Forward cab with moulded seats, mirrors and a dedicated tipper bucket carried on a System chassis.'),
    'touring-motorcycle': dict(title='Touring motorcycle', palette='heritage-racing', length=10,
                               profile='motorcycle', lesson='Dedicated motorcycle frame and vintage fairing, separate spoked wheels/tyres and a rear luggage rack.'),
    'harbour-launch': dict(title='Harbour launch', palette='coastal-delivery', length=14,
                           profile='watercraft', lesson='Purpose-made boat hull, open helm with a real seat and steering wheel, navigation lights and life ring.'),
    'courier-jet': dict(title='Courier jet', palette='coastal-delivery', length=26,
                       profile='aircraft', lesson='Matched aircraft nose/glass and tapered rear, swept wings, dedicated engine pods and an equipped cockpit.'),
}


def tiled_strip(module, x, z, length, h, colour, *, axis='z'):
    """Quiet sill/bed rail with the fewest available ordinary tile seams."""
    refs = {1:'3070b', 2:'3069b', 3:'63864', 4:'2431', 6:'6636', 8:'4162'}
    cursor = 0
    for n in lengths(length):
        module.add(refs[n], colour, x+cursor+n/2 if axis=='x' else x, h,
                   z if axis=='x' else z+cursor+n/2, yaw=0 if axis=='x' else 90)
        cursor += n


def smooth_deck(module, width, start, depth, h, colour):
    """Broad 4/6-wide tiled surface; start/depth on the integer stud grid."""
    if width not in {4,6} or not isinstance(depth, int) or depth < 0:
        raise ValueError('Smooth deck needs width 4 or 6 and nonnegative integer depth')
    for z in range(start, start+depth-1, 2):
        module.add('87079' if width==4 else '69729', colour, h=h, z=z+1)
    if depth % 2:
        module.add('2431' if width==4 else '6636', colour, h=h, z=start+depth-.5)


def wheel_report(parts, name=None):
    if name is not None and name not in WHEEL_PACKS:
        raise ValueError('Unknown wheel pack; use vehicle wheels')
    result = {}
    for key, pack in WHEEL_PACKS.items():
        if name and key != name:
            continue
        measured = {}
        for role in ('holder', 'rim', 'tyre'):
            code = pack[role]
            geometry = parts.geometry(code)
            if not geometry.complete:
                raise ValueError(f'Incomplete wheel geometry: {code}')
            measured[role] = dict(ref=code+'.dat', description=parts.by_code[code],
                                  bounds=jsonable(geometry.bounds))
        result[key] = dict(**pack, measured=measured,
                           track_ldu=2*pack['tyre_x'],
                           holder_at=[0, -pack['radius']-5, 0],
                           deck_top_y=-pack['radius']-13+pack['holder_stud_y'],
                           note='Rim/tyre transform comes from the named official shortcut. '
                                'Holder pins run along X at local Y=5. Separate BOM leaves; '
                                'inspect connector coverage and rolling clearance after assembly.')
    return result


def axle(pack='touring', *, rim_colour=71):
    """One wheel pair at Z=0, tyres on Y=0; deck anchor is a stud body plane."""
    if pack not in WHEEL_PACKS:
        raise ValueError('Unknown wheel pack')
    p = WHEEL_PACKS[pack]
    m = Module(f'axle-{pack}', 'Fixed wheel-pin axle; separate rims and tyres; ground Y=0')
    m.add(p['holder'], 0, h=p['radius']+5, id='holder')
    for side, sign in [('left', -1), ('right', 1)]:
        # Both outside faces point outwards using rotations, never reflections.
        m.add(p['rim'], rim_colour, sign*p['rim_x']/20, p['radius'],
              yaw=-90*sign, id=side+'-rim')
        m.add(p['tyre'], 256, sign*p['tyre_x']/20, p['radius'],
              yaw=-90*sign, id=side+'-tyre')
    m.anchor('deck', h=p['radius']+5-p['holder_stud_y'])
    return m


def fascia(name, width=6, *, body=4, trim=71, lamps=47, rear=False):
    """One-stud-deep SNOT light/bumper strip; support underside Y=0, front -Z."""
    m = Module(name, 'Stud-mounted lamps and grille; reserve the projecting front envelope')
    orient = [[1,0,0],[0,0,-1],[0,1,0]]
    for x in range(-width//2, width//2):
        m.add('4070', body, x+.5, 24, 0)
        if x in [-width//2, width//2-1]:
            m.add('6141', lamps, x+.5, 14, -.7, matrix=orient)
    for x in [-1, 1]:
        m.add('2412b' if not rear else '3069b', 0 if not rear else body,
              x, 14, -.7, matrix=orient)
    line(m, -width/2, 0, width, 32, trim, plate=True)
    return m


def vehicle_plan(name, palette=None):
    if name not in DESIGNS:
        raise ValueError('Unknown vehicle; use vehicle list')
    design = DESIGNS[name]
    palette = palette or design['palette']
    c = vehicle_colours(palette)
    if design.get('profile') in {'motorcycle','watercraft','aircraft'}:
        from .vehicle_families import family_model
        plan=family_model(name,palette).plan()
        plan['author']='ldraw-nova vehicle examples'
        return plan
    length, wb = design['length'], design['wheelbase']
    half = length//2
    root = Module(name, design['title']+'; six-stud System body, front -Z, ground Y=0')
    running = axle(rim_colour=c['metal'])
    for sign, label in [(-1, 'front'), (1, 'rear')]:
        root.add(running, 0, z=sign*wb/2, id=label+'-axle')

    chassis = Module(name+'-chassis', 'Bonded narrow spine; reserved wheel wells; body deck at h=38')
    # First plate underside h=22 mates the unusual h=22 holder stud plane.
    for h, runs in [(30, list(lengths(length))), (38, [2, *lengths(length-2)])]:
        cursor = -half
        for n in runs:
            chassis.add(WIDE_PLATES[n], c['chassis'], h=h, z=cursor+n/2,
                        yaw=0 if n==1 else 90)
            cursor += n
    # Cross plates bridge spine seams only outside each tyre's Z envelope.
    for z0, depth in [(-half, 2), (-wb/2+2, wb-4), (wb/2+2, 2)]:
        slab(chassis, -3, z0, 6, depth, 46, c['chassis'])
    root.add(chassis, c['chassis'], id='chassis')

    body = Module(name+'-body', 'Shaped body with four reserved wheel wells and a continuous shoulder line')
    for z in [-wb/2, wb/2]:
        for sign in [-1, 1]:
            body.add('98282', c['body'], sign, 62, z, yaw=-90*sign)
    # Fill only the intervals ahead of, between and behind the arches.
    for z0, depth in [(-half, 2), (-wb/2+2, wb-4), (wb/2+2, 2)]:
        slab(body, -3, z0, 6, depth, 54, c['body'])
        slab(body, -3, z0, 6, depth, 62, c['body'])
    # Four-wide deck ties all four fenders into the chassis; outer shoulders
    # are supported by the fenders' outer stud rows, above the tyre crown.
    slab(body, -2, -half, 4, length, 70, c['body'])
    for x in [-2.5, 2.5]:
        line(body, x, -half, length, 70, c['body'], axis='z', plate=True)
    root.add(body, c['body'], id='body')

    front = fascia(name+'-front', body=c['body'], trim=c['metal'], lamps=c['headlamp'])
    back = fascia(name+'-rear', body=c['body'], trim=c['metal'], lamps=c['tail_lamp'], rear=True)
    # Face strips are beyond the core footprint and attach through their caps.
    root.add(front, c['body'], h=38, z=-half-.5, id='front-fascia')
    root.add(back, c['body'], h=38, z=half+.5, yaw=180, id='rear-fascia')
    # A transverse cap bridges each fascia's top row back onto the body.
    for z in [-half, half]:
        root.add('69729', c['metal'], h=78, z=z)

    cabin = Module(name+'-cabin', 'Glazing, supported roof and readable passenger/cargo volumes')
    if name == 'grand-tourer':
        for z, yaw in [(-1.5, 0), (1.5, 180)]:
            cabin.add('2437', c['glass'], h=102, z=z, yaw=yaw)
        slab(cabin, -2, -2, 4, 4, 110, c['roof'])
        # Fill the double curves' raised centre sockets; the end sockets sit
        # on the h=110 roof plate, the middle sockets on this h=118 infill.
        cabin.add('3020', c['roof'], h=118)
        for x in [-1.5, -.5, .5, 1.5]:
            cabin.add('93273', c['roof'], x, 110, 0)
        # Curved bonnet on real plate sockets; quieter tiled rear deck.
        for x in [-2.5,-1.5,-.5,.5,1.5,2.5]:
            cabin.add('50950', c['body'], x, 94, -half+2.5)
        for h in [78,86]:
            slab(cabin, -3, -half+4, 6, half-7, h, c['body'])
        smooth_deck(cabin, 6, -half+4, half-7, 94, c['body'])
        smooth_deck(cabin, 6, 3, half-4, 78, c['body'])
        for x in [-2.5, 2.5]:
            tiled_strip(cabin, x, -3, 6, 78, c['body'])
    else:
        # Six-wide windscreen, genuinely distinct from the tourer's low cabin.
        shift=-3 if name=='tipper-truck' else 0
        cabin.add('4176', c['glass'], h=118, z=-3.5+shift)
        # Local cab is one stud deeper than the original block-seat version;
        # the moulded 4079 back projects 5 LDU past its two-stud floor.
        for x in [-2.5, 2.5]:
            cabin.add('3005', c['roof'], x, 94, .5+shift)
            cabin.add('3005', c['roof'], x, 118, .5+shift)
            cabin.add(detail_module('wing-mirror',palette),c['body'],x,70,-2.5+shift,yaw=-90 if x>0 else 90)
        for x in [-1, 1]:
            cabin.add('4079', c['wood'], x, 78, -1+shift,id='driver-seat' if x<0 else 'passenger-seat')
        cabin.add('3829c01', c['chassis'], -1, 78, -2.5+shift)
        cabin.add('3069bp25',c['chassis'],1,78,-2.5+shift)
        # Longitudinal roof plates span the open seating area; short strips
        # with matching tile seams would leave the middle roof floating.
        for x in [-2,0,2]:cabin.add('3020',c['roof'],x,126,-2+shift,yaw=90)
        cabin.add('3666',c['roof'],h=126,z=.5+shift)
        smooth_deck(cabin, 6, -4+shift, 4 if name=='tipper-truck' else 5, 134, c['roof'])
        if name=='tipper-truck':
            cabin.add('2431',c['roof'],h=134,z=-2.5)
            for x in [-2,0,2]:cabin.add('3039',c['body'],x,94,-8.5)
        else:
            for x in [-2.5,-1.5,-.5,.5,1.5,2.5]:
                cabin.add('50950', c['body'], x, 94, -half+2.5)
        if name!='tipper-truck':smooth_deck(cabin, 6, -half+4, half-9, 78, c['body'])
        if name == 'delivery-van':
            for h in [94,118]:
                for x in [-2.5, 2.5]:
                    line(cabin, x, 1, half-2, h, c['body'] if h==94 else c['roof'], axis='z')
                line(cabin, -2, half-1.5, 4, h, c['body'] if h==94 else c['roof'])
                line(cabin, -2, 1.5, 4, h, c['body'] if h==94 else c['roof'])
            slab(cabin, -3, 1, 6, half-2, 126, c['roof'])
            smooth_deck(cabin, 6, 1, half-2, 134, c['roof'])
        elif name=='tipper-truck':
            for h in [94,118]:line(cabin,-3,-1.5,6,h,c['body'])
            cabin.add('4080',c['body'],h=78,z=4,id='tipper-bucket')
            # Bucket is in its fixed transport pose on actual deck studs;
            # no tipping hinge or hydraulic mechanism is claimed.
            cabin.add('6141','@colours.Trans_Orange',-2.5,134,-2.5)
            cabin.add('6141','@colours.Trans_Orange',2.5,134,-2.5)
        else:
            # Open bed: lower than cab, visible tiled floor and capped side rails.
            line(cabin, -3, 1.5, 6, 94, c['body'])
            line(cabin, -3, 1.5, 6, 118, c['body'])
            for x in [-2.5, 2.5]:
                line(cabin, x, 2, half-3, 94, c['body'], axis='z')
                tiled_strip(cabin, x, 2, half-3, 102, c['trim'])
            line(cabin, -2, half-1.5, 4, 94, c['body'])
            # Pallet uses studs, so the chest replaces the corresponding bed tiles.
            cabin.add(detail_module('cargo-chest',palette),c['wood'],.5,70,5)
            smooth_deck(cabin,4,2,1,78,c['wood'])
            smooth_deck(cabin,4,7,half-9,78,c['wood'])
            for z in range(3,7):cabin.add('3070b',c['wood'],-1.5,78,z+.5)
            smooth_deck(cabin, 4, half-2, 1, 102, c['trim'])
    root.add(cabin, c['body'], id='cabin')
    plan = root.plan()
    plan['author'] = 'ldraw-nova vehicle examples'
    return plan


def design_brief(name, palette=None):
    if name not in DESIGNS:
        raise ValueError('Unknown vehicle; use vehicle list')
    d = DESIGNS[name]
    profile=d.get('profile','road')
    vehicle_colours(palette or d['palette'])
    result=dict(subject=d['title'], construction='System and dedicated vehicle parts; no Technic mechanisms',
                profile=profile, axes='X width, -Z forward, negative Y up; see model-specific datum in the guide',
                body_length_studs=d['length'],
                palette=palette or d['palette'], silhouette=d['lesson'],
                focal_feature='Front light/grille identity and overall silhouette',
                supporting_features=['Matched wheel arches and stance', 'Contrasting glazing and roof'],
                quiet_surfaces=['Bonnet', 'Roof', 'Cargo sides or bed'],
                review_views=['home','front','back','left','right','top','bottom'],
                limitations=['Teaching starting point: adapt shapes and interfaces to the requested subject.',
                             'Driver fit, dynamics, rolling friction and retail part/colour availability require separate review.'])
    if profile=='road':result.update(body_width_studs=6,wheelbase_studs=d['wheelbase'],wheel_pack='touring',ground_y=0)
    elif profile=='motorcycle':
        result.update(ground_y=0, focal_feature='Vintage fairing and exposed spoked wheels',
                      supporting_features=['Moulded frame, saddle and handlebars', 'Rear luggage rack'],
                      quiet_surfaces=['Front fender', 'Fairing'],
                      dedicated_parts=['50859b','85983','50862','50861'])
    elif profile=='watercraft':
        result.update(datum='Hull interior floor Y=0; not a waterline', focal_feature='Low open boat hull and glazed helm',
                      supporting_features=['Seat, helm and instruments', 'Navigation lights and life ring'],
                      quiet_surfaces=['Hull sides', 'Bow'],
                      dedicated_parts=['2551','4079','3829c01','30340'])
    else:
        result.update(datum='Nose interior floor Y=0; in-flight display pose', focal_feature='Streamlined cockpit and swept wing silhouette',
                      supporting_features=['Matched jet engine pods', 'T-tail and tapered fuselage'],
                      quiet_surfaces=['Nose', 'Fuselage roof'],
                      dedicated_parts=['87611','87612','87613','87616','30355','30356','4868b','4869','4867'])
    if name in {'delivery-van','pickup','tipper-truck'}:
        result['dedicated_parts']=['4079','3829c01','3069bp25','4176','98282']
        if name=='pickup':result['dedicated_parts'].append('30150')
        if name=='tipper-truck':result['dedicated_parts'].append('4080')
    result['interior']='Display glazing; driver fit untested' if name=='grand-tourer' else 'Dedicated seat and controls; figure fit and headroom untested'
    return result
