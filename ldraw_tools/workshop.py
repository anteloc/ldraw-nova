"""Complete, deliberately bounded workshop constructions emitting ordinary plans.

The 120 LDU chain-wheel spacing and extended cylinder pose are reviewed choices,
not arbitrary length parameters. Compose/rotate modules and change the palette;
study different mechanical dimensions separately.
"""
from __future__ import annotations

from .builder import rotation
from .common import jsonable
from .technic_recipes import structure_plan


def part(name, ref, at, colour=71, matrix=None):
    result = dict(id=name, ref=ref + '.dat', at=list(at), colour=colour)
    if matrix is not None:
        result['matrix'] = jsonable(matrix)
    return result


def named_structure(name='box-chassis', **options):
    plan, contract = structure_plan(name, **options)
    ids = [p['id'] for step in plan['sections'][0]['steps'] for p in step]
    for joint in contract['required_joints']:
        joint['between'] = [ids[i] for i in joint['between']]
    for step in contract['assembly']:
        step['connector'] = ids[step['connector']]
        step['before'] = [ids[i] for i in step['before']]
    plan['sections'][0]['structure'] = contract
    return plan


def chain_drive(*, colour=71, accent=14):
    """Two retained shafts and a 24-link loop, with a supported hand crank."""
    shaft_matrix = rotation('y', -90)
    crank_matrix = rotation('x', 90)
    # The even-width plate has half-stud rows; offset it so the 1-wide rails
    # at z=+/-40 actually engage its studs. Keep this socket offset at the mount.
    steps = [[part('base', '3036', [0, 0, 10], colour)]]
    for y in (-24, -48):
        steps.append([part(f'rail-{z}-{y}', '3008', [0, y, z], colour) for z in (-40, 40)])
    steps.append([part(f'bearing-{x}-{z}', '3700', [x, -72, z], accent)
                  for x in (-60, 60) for z in (-40, 40)])
    steps.append([part(f'cap-{z}', '3460', [0, -80, z], colour) for z in (-40, 40)])
    required = []
    for z in (-40, 40):
        lower, upper = f'rail-{z}--24', f'rail-{z}--48'
        required += [dict(between=['base', lower], minimum=8),
                     dict(between=[lower, upper], minimum=8)]
        for x in (-60, 60):
            bearing = f'bearing-{x}-{z}'
            required += [dict(between=[upper, bearing], minimum=2),
                         dict(between=[bearing, f'cap-{z}'], minimum=2)]
    for label, x in [('drive', -60), ('idler', 60)]:
        axle = label + '-axle'
        steps.append([part(axle, '3737' if label == 'drive' else '3707', [x, -62, 0], 0, shaft_matrix)])
        attached = [part(label + '-gear', '4019', [x, -62, 0], 7)]
        attached += [part(f'{label}-spacer-{z}', '32123a', [x, -62, z], 14) for z in (-25, -15, 15, 25)]
        attached += [part(f'{label}-stop-{z}', '3713', [x, -62, z], 0) for z in (-60, 60)]
        steps.append(attached)
        required.extend([dict(between=[axle, p['id']]) for p in attached])
        required.extend([dict(between=[axle, f'bearing-{x}-{z}']) for z in (-40, 40)])
    steps.append([part('crank', '6632', [-60, -62, 75], accent, crank_matrix),
                  part('crank-stop', '3713', [-60, -62, 90], 0),
                  part('handle-axle', '32073', [-60, -102, 105], 0, shaft_matrix)])
    steps.append([part('handle-inner', '32123a', [-60, -102, 65], 14)] +
                 [part(f'handle-grip-{z}', '3713', [-60, -102, z], 0) for z in (90, 110, 130)])
    required += [dict(between=list(p)) for p in [('drive-axle', 'crank'), ('drive-axle', 'crank-stop'),
                                         ('handle-axle', 'crank'), ('handle-axle', 'handle-inner'),
                                         *[('handle-axle', f'handle-grip-{z}') for z in (90, 110, 130)]]]
    steps.append([dict(id='chain', colour=72, flex=dict(method='TECHNIC_CHAIN_LINK', wheels=['drive-gear', 'idler-gear']))])
    section = dict(name='chain-drive.ldr', description='Hand-cranked retained chain conveyor; fixed delivered pose',
                   steps=steps, anchors={'origin': {'at': [0, 0, 0]}},
                   structure=dict(scope='joints', required_joints=required,
                       retained_axles=['drive-axle', 'idler-axle', 'handle-axle'],
                       assembly=[dict(connector='drive-axle', before=['drive-gear', 'crank-stop']),
                                 dict(connector='idler-axle', before=['idler-gear', 'idler-stop-60']),
                                 dict(connector='handle-axle', before=['handle-inner', 'handle-grip-90'])]))
    return dict(version=1, author='LDraw Nova workshop constructions', sections=[section])


def workshop_plan(*, colour=71, accent=14):
    """Braced bench, chain conveyor and mounted three-hose pneumatic stop."""
    bench = dict(name='workbench.ldr', description='Two bonded plate courses; underside mounts on two braced trestles', steps=[[
        part('lower-front', '92438', [0, 8, -80], 72), part('lower-rear', '92438', [0, 8, 80], 72)], [
        part('upper-middle', '92438', [0, 0, 0], 72),
        *[part(f'upper-{x}-{z}', '3035', [x, 0, z], 72) for x in (-80, 80) for z in (-120, 120)]]])
    trestle = named_structure(colour=colour, accent=accent)['sections'][0]
    bridge_steps = [[part(f'foot-{x}', '3022', [x, 0, 60], colour) for x in (-140, 140)]]
    for row in range(9):
        bridge_steps.append([part(f'column-{x}-{row}', '3003', [x, -24 * (row + 1), 60],
                                  accent if row % 2 else colour) for x in (-140, 140)])
    bridge_steps.append([part('beam', '3703', [0, -240, 50], colour),
                         *[part(f'cap-{x}', '3004', [x, -240, 70], accent) for x in (-140, 140)]])
    bridge_steps.append([part('top', '4282', [0, -248, 60], accent)])
    bridge_joints = []
    for x in (-140, 140):
        previous = f'foot-{x}'
        for row in range(9):
            current = f'column-{x}-{row}'
            bridge_joints.append(dict(between=[previous, current], minimum=4))
            previous = current
        bridge_joints += [dict(between=[previous, 'beam'], minimum=2),
                          dict(between=[previous, f'cap-{x}'], minimum=2),
                          dict(between=[f'cap-{x}', 'top'], minimum=2)]
    bridge_joints.append(dict(between=['beam', 'top'], minimum=16))
    bridge = dict(name='stop-frame.ldr', description='Wide bonded gantry clears the conveyor shafts', steps=bridge_steps,
                  structure=dict(scope='joints', required_joints=bridge_joints))
    cylinder_matrix = [[0, 0, -1], [0, -1, 0], [-1, 0, 0]]
    ram = dict(name='stop-ram.ldr', description='Extended cylinder with both eyes pinned and a stop face', steps=[[
        part('cylinder', '74981-f2', [0, -230, 30], colour, cylinder_matrix),
        part('mount-pin', '3673', [0, -230, 40], 0, rotation('y', 90))], [
        part('head-pin', '3673', [0, -114, 40], 0, rotation('y', 90))], [
        part('head', '3701', [0, -124, 50], accent)], [
        part('stop', '3020', [0, -100, 40], 0)]])
    controls = dict(name='controls.ldr', description='Stud-mounted hand pump and pneumatic valve', steps=[[part('pump-base', '3003', [-120, -24, -20], colour),
        part('valve-base', '3004', [40, -24, -110], colour)], [
        part('pump-pad', '3022', [-120, -32, -20], colour),
        part('valve-pad', '3023', [40, -32, -110], colour)], [
        part('pump', '2797c01-f1', [-120, -46, -20], colour, rotation('y', -90)),
        part('valve', '4694c01-f1', [40, -88, -110], colour, rotation('y', -90))]])
    root_steps = [[dict(id=f'trestle-{x}', ref=trestle['name'], colour=colour, at=[x + 10, 106, 10]) for x in (-80, 80)]]
    pins, required = [], []
    for x in (-80, 80):
        for side in (-1, 1):
            for z in (-100, -40, 40, 100):
                name = f'mount-{x}-{side}-{z}'
                pins.append(part(name, '4274', [x + 10 + side * 40, 16, z + 10], 7, rotation('z', -90)))
                required += [dict(between=[name, f'trestle-{x}/rail-{side}']),
                             dict(between=[name, 'bench/lower-' + ('front' if z < 0 else 'rear')])]
    root_steps += [pins, [dict(id='bench', ref=bench['name'], colour=72, at=[0, 0, 0])],
                   [dict(id='conveyor', ref='chain-drive.ldr', colour=colour, at=[0, -8, 50])],
                   [dict(id='gantry', ref=bridge['name'], colour=colour, at=[0, -8, 0])],
                   [dict(id='ram', ref=ram['name'], colour=colour, at=[0, -8, 0]),
                    dict(id='controls', ref=controls['name'], colour=colour, at=[0, 0, 0])]]
    required += [dict(between=pair, minimum=n) for pair, n in [
        (['conveyor/base', 'bench/upper-middle'], 4),
        *[(['conveyor/base', f'bench/upper-{x}-120'], 8) for x in (-80, 80)],
        (['controls/pump', 'controls/pump-pad'], 4),
        (['controls/pump-pad', 'controls/pump-base'], 4),
        (['controls/pump-base', 'bench/upper-middle'], 4),
        (['controls/valve', 'controls/valve-pad'], 2),
        (['controls/valve-pad', 'controls/valve-base'], 2),
        (['controls/valve-base', 'bench/upper-80--120'], 2),
        (['ram/mount-pin', 'ram/cylinder'], 1), (['ram/mount-pin', 'gantry/beam'], 1),
        (['ram/head-pin', 'ram/cylinder'], 1), (['ram/head-pin', 'ram/head'], 1),
        (['ram/head', 'ram/stop'], 4),
        *[([f'gantry/foot-{x}', 'bench/upper-middle'], 4) for x in (-140, 140)],
        *[(['control-guard', f'bench/upper-{x}--120'], 4) for x in (-80, 80)],
        *[([f'guard-tile-{x}', 'control-guard'], 2) for x in (-60, -20, 20, 60)]]]
    for name, colour_, start, end, via in [
        ('supply', 0, ('controls/pump', 'outlet'), ('controls/valve', 'inlet'), []),
        ('raise', 4, ('controls/valve', 'upper'), ('ram/cylinder', 'base'), [dict(at=[80, -152, -30], direction=[0.2, -1, 0.5])]),
        ('lower', 1, ('controls/valve', 'lower'), ('ram/cylinder', 'rod'), [dict(at=[74, -112, -36], direction=[0.2, -1, 0.5])]),
    ]:
        root_steps.append([dict(id=name, colour=colour_, flex=dict(method='TECHNIC_PNEUMATIC_HOSE_BEVELED',
            **{'from': dict(part=start[0], port=start[1], lead=22), 'to': dict(part=end[0], port=end[1], lead=22)},
            via=via, checks=dict(min_radius=15, tube_radius=5, min_separation=10)))])
    root_steps.append([part('control-guard', '3008', [0, -24, -150], colour)])
    root_steps.append([part(f'guard-tile-{x}', '3069b', [x, -32, -150], accent if i % 2 else 0)
                       for i, x in enumerate((-60, -20, 20, 60))])
    root = dict(name='workshop.ldr', description='Hand-cranked chain conveyor with a pneumatic stop on a braced workbench',
                steps=root_steps, structure=dict(scope='joints', required_joints=required,
                    assembly=[dict(connector=p['id'], before=['bench/lower-front', 'bench/lower-rear']) for p in pins]))
    return dict(version=1, author='LDraw Nova workshop constructions',
                sections=[root, trestle, bench, *chain_drive(colour=colour, accent=accent)['sections'], bridge, ram, controls])
