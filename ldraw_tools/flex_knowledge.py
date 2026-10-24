"""Family-specific LSynth decisions backed by the installed definitions."""
from __future__ import annotations

from dataclasses import asdict

from .flex import LINK_TYPES, availability, engine

FAMILIES = {
    'pneumatic': dict(purpose='Round pneumatic tubing between actual pump, valve, tee and cylinder nozzles.',
        design=['Transform nozzle bases and outward axes with their owning parts.',
                'Reserve straight departures and choose port orientation before dressing the machine.',
                'Use actual tees for branches; preserve circuit connections and account for slack.'],
        inspect=['End sleeves seated on the nozzles', 'Tight bends, crossings and neighbouring machinery'],
        example='examples/flex/pneumatic-press/README.md'),
    'electrical': dict(purpose='Electrical cables, including flat cables and branched light leads.',
        design=['Model and mount real plugs, motors, controllers and branch boxes separately.',
                'Keep the cable cross-section orientation consistent; set waypoint up vectors for flat cables.',
                'Reserve plug insertion and battery access; route branches individually from real junctions.'],
        inspect=['Twist and flat-face orientation', 'Entry into each plug', 'Clearance and supported slack'],
        example='lsynth-examples/README.md'),
    'optical': dict(purpose='Thin or broad optical guides and their distributor fittings.',
        design=['Use the correct end/distributor parts and account for asymmetric end geometry.',
                'Broad-guide and thin-fibre definitions are different; do not substitute by name similarity.'],
        inspect=['End fittings and visible width', 'Bends and fan spacing', 'Missing legacy dependencies'],
        example='lsynth-examples/FIBER_OPTICS_CABLE-Constraints.ldr'),
    'flex_system': dict(purpose='Flexible axles, or separate Flex-System inner cable and outer guide.',
        design=['Distinguish axle ends, inner cable terminations and fixed outer sleeve supports.',
                'Retain the correct end fittings and space for the intended relative travel.',
                'A guide curve does not establish torque transmission, friction or a working linkage.'],
        inspect=['End orientation and retention', 'Cable versus sleeve ownership', 'Bend and travel space'],
        example='lsynth-examples/TECHNIC_FLEX-SYSTEM-Constraints.ldr'),
    'segmented_hose': dict(purpose='Corrugated/ribbed hoses generated from repeated rings or a fixed segment count.',
        design=['Use broad curves; extra close markers can create visibly separated or intersecting rings.',
                'A length in the method name or FIXED count is not a verified stock-length constraint.'],
        inspect=['Gaps and overlaps between adjacent rings', 'End seats', 'Actual length against a chosen physical part'],
        example='lsynth-examples/TECHNIC_RIBBED_HOSE-Constraints.ldr'),
    'string': dict(purpose='String or rope, with optional grips; marker routes or wheel-guided STRING_BAND.',
        design=['Supply real anchors, sheaves, supported drums and hooks.',
                'Author slack deliberately; LSynth does not compute gravity, tension or wound-rope contact.',
                'Retain one physical length when claiming several poses of the same rope.'],
        inspect=['Anchor seating', 'Sheave planes and drum routing', 'Grip spacing and slack'],
        example='lsynth-examples/STRING_HOSE-Constraints.ldr'),
    'minifig_chain': dict(purpose='A complete minifigure chain represented by alternating links.',
        design=['Attach its real end links; keep alternating link orientation and fixed-count behaviour.',
                'Treat it as one item in the BOM; a smooth guide is not proof of link articulation.'],
        inspect=['End attachments', 'Adjacent links and excessive stretch'],
        example='lsynth-examples/MINIFIG_CHAIN_16L-Constraints.ldr'),
    'brick_arc': dict(purpose='A repeated brick shape study, not a flexible physical part.',
        design=['Each brick remains a rigid BOM item.', 'Design real connections if adapting the shape into an assembly.'],
        inspect=['Brick intersections', 'Actual connections between neighbours'],
        example='lsynth-examples/BRICK_ARC-Constraints.dat'),
    'belt': dict(purpose='Continuous rubber band, belt or moulded tread around wheels.',
        design=['Place supported, compatible wheels in a common routing plane.',
                'Order wheels around the loop; INSIDE/OUTSIDE choose wrap side and CROSS toggles it for subsequent wheels, including closure.',
                'Configured wheel radii do not establish traction, stock length or tension.'],
        inspect=['Both loop runs', 'Wheel ownership', 'Twist, tension and wheel engagement'],
        example='examples/flex/band.ldr'),
    'linked_track': dict(purpose='Separate rigid chain/tread links around a compatible wheel family.',
        design=['Install shafts, bearings and retention before wrapping the chain or tread.',
                'Match actual link and wheel families; the global wheel table is not a compatibility table.',
                'Adjust wheel spacing or the layout to close the loop; never stretch rigid links.'],
        inspect=['Closure seam', 'Link spacing and engagement', 'Return-run clearance and duplicate wheels'],
        example='examples/flex/chain.ldr'),
}


def family(name):
    n = name.upper()
    if n == 'BRICK_ARC': return 'brick_arc'
    if n.startswith('MINIFIG_CHAIN'): return 'minifig_chain'
    if n.startswith('STRING'): return 'string'
    if n.startswith('ELECTRIC'): return 'electrical'
    if n.startswith('FIBER'): return 'optical'
    if 'PNEUMATIC' in n: return 'pneumatic'
    if n in {'FLEXIBLE_AXLE', 'FLEX_CABLE', 'FLEX_SYSTEM_HOSE'} or n.startswith(('TECHNIC_AXLE', 'TECHNIC_FLEX-')):
        return 'flex_system'
    if n.startswith('HOSE_') or n in {'RIGID_HOSE', 'RUBBER_HOSE', 'RIBBED_HOSE', 'TECHNIC_RIBBED_HOSE'}:
        return 'segmented_hose'
    if n in LINK_TYPES: return 'linked_track'
    if n in {'RUBBER_BAND', 'RUBBER_BELT', 'TECHNIC_TREAD', 'RUBBER_TREAD', 'TECHNIC_TREAD_CRAWLER'}: return 'belt'
    raise ValueError(f'No reviewed family guidance for {name}; inspect the new engine definition before using it')


def resolve(token, cfg=None):
    cfg = cfg if cfg is not None else engine()[0]
    product = next((p for p in cfg.products if token.casefold() in {p.name.casefold(), p.nickname.casefold()}), None)
    method = product.method if product else token
    h, b = cfg.hose_type(method), cfg.band_type(method)
    if h is None and b is None:
        raise ValueError(f'Unknown exact synthesis type or product {token!r}; run flex types')
    return cfg, h if h is not None else b, 'hose' if h is not None else 'band'


def guide(token=None):
    cfg, _, _ = engine()
    if token is None:
        return dict(engine=availability(), families=FAMILIES,
                    methods=[dict(name=t.type, family=family(t.type), kind=k) for k, ts in
                             [('hose', cfg.hose_types), ('band', cfg.band_types)] for t in ts],
                    workflow=['flex guide TYPE', 'author visible constraints',
                              'declare the source in plan assets, or flex build SOURCE',
                              'review the asset in its assembly and open the images'])
    cfg, t, kind = resolve(token)
    data = dict(engine=availability(), requested=token, method=t.type, kind=kind,
                family=family(t.type), **FAMILIES[family(t.type)], definition=asdict(t),
                fill=('stretch' if t.fill == -1 else 'fixed_segments' if t.fill == 0 else
                      'fixed3' if t.fill == -2 else f'fixed_count:{t.fill}'),
                representation='links' if t.type in LINK_TYPES else 'posed_part',
                physical_validity='not_proven',
                limits=['Definition numbers control geometry, not material physics.',
                        'No general route planning, collision avoidance or motion simulation is supplied.'])
    data['constraints'] = ([c.type for c in cfg.hose_constraints] if kind == 'hose'
                           else [asdict(c) for c in cfg.band_constraints])
    if t.type == 'BRICK_ARC':
        data['limits'].append('Installed 3.1.0 emitted reflected brick placements in the straight fixture; the adapter correctly rejects them. Use as a shape study, not a validated brick assembly; do not relax rigid validation.')
    return data
