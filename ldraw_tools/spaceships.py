"""Spaceship design briefs and attributed construction kits.

Fictional propulsion is a design vocabulary, not an engineering simulation.
"""
from copy import deepcopy
import json

from .common import ROOT
from .discovery import confined
from .manuals import export_manual


ARCHETYPES = {
    'starfighter': {
        'title': 'Advanced starfighter',
        'silhouette': 'A readable nose-to-cockpit spine, distinctive wing arrangement and clearly separate engine masses.',
        'modules': ['load-bearing spine', 'cockpit tub and canopy', 'nose armour', 'wing roots and matched wing panels', 'engine pods and exhausts', 'landing feet or display mount'],
        'focal_feature': 'Choose one: split wings, a rotating-looking cockpit, oversized engines, or an asymmetric main blade.',
        'detail_strategy': 'Use smooth nose armour and broad wing surfaces beside concentrated engine plumbing and service recesses.',
        'palette': {'hull': 71, 'shadow': 72, 'frame': 0, 'markings': 320, 'canopy': 40, 'exhaust': 47},
        'references': ['b-wing', 'x-wing-wing', 'x-wing-nacelle', 'canopy-cockpit'],
    },
    'freighter': {
        'title': 'Detailed light freighter',
        'silhouette': 'A broad cargo hull with an offset or raised cockpit, a readable loading opening and a strong rear engine band.',
        'modules': ['internal frame', 'cargo floor and partitions', 'cockpit and access corridor', 'upper and lower hull panels', 'loading ramp and landing feet', 'engines', 'antenna and service bays'],
        'focal_feature': 'Choose one asymmetric cockpit or antenna feature, supported by coherent hull seams.',
        'detail_strategy': 'Group pipes, vents and machinery into service bays; leave broad hull panels quiet. Give the underside a deliberate design.',
        'palette': {'hull': 71, 'shadow': 72, 'frame': 0, 'markings': 308, 'canopy': 40, 'exhaust': 43},
        'references': ['falcon-greebles', 'y-wing-armour', 'x-wing-nacelle'],
    },
    'capital-ship': {
        'title': 'Large display-scale capital ship',
        'silhouette': 'A clear wedge, hammerhead or elongated spine with layered superstructure and a visible engine cluster.',
        'modules': ['internal truss and display mount', 'lower hull', 'paired upper hull panels', 'edge trenches', 'bridge and superstructure', 'engine block', 'hangar opening'],
        'focal_feature': 'A recognisable bridge or engine cluster; preserve large negative spaces and the primary hull outline.',
        'detail_strategy': 'Concentrate small mechanical details in recessed trenches and hangars. Reduce detail size relative to the main hull to establish scale.',
        'palette': {'hull': 71, 'shadow': 72, 'frame': 0, 'markings': 7, 'canopy': 0, 'exhaust': 43},
        'references': ['star-destroyer-study', 'y-wing-armour', 'falcon-greebles'],
    },
}


def design_brief(archetype):
    if archetype not in ARCHETYPES:
        raise ValueError('Choose starfighter, freighter or capital-ship')
    return dict(version=1, family='spaceship', archetype=archetype, **deepcopy(ARCHETYPES[archetype]),
        coordinates='X width, -Z forward, negative Y up; choose the hull or stand datum explicitly.',
        scale='Choose minifigure, display or microscale before selecting the canopy and detail sizes.',
        part_queries={
            'cockpit': 'a spacecraft canopy with a compatible cockpit rim and pilot controls',
            'hull': 'matched left and right wedge plates and slopes for an angular spaceship hull',
            'engines': 'a cylindrical thruster nacelle with concentric shells, grille intake and exhaust nozzle',
            'surface_detail': 'a small recessed spaceship machinery bay with grilles, bars, clips and dishes',
            'supports': 'a braced frame for long wings, cantilevered engines and a display stand'},
        interfaces='Record each module origin, bounds, exact mounting parts, attachment frames, and parent dependencies. Use proper rotations and real left/right parts.',
        review=['front/top silhouette', 'side thickness and cockpit proportions', 'rear engine spacing', 'underside and stand attachments', 'bare frame and exposed wing roots', 'open cockpit or removable hull where interiors matter', 'quiet surfaces beside concentrated detail'],
        mechanism_scope='Study actual folding-wing, ramp or landing-gear mechanisms using the mechanism workflow when requested; analytical mechanism verification remains deferred.',
        palette_note='Suggested design roles; inspect actual part/colour availability. Preserve functional and printed colours when adapting a source.',
        next='Choose and study references, design an original module layout, build, inspect interfaces, render and refine. A brief is not a generated model.')


def export_spaceship(key, outdir, *, force=False):
    atlas = ROOT/'examples/spaceship-atlas'
    catalog = json.loads((atlas/'catalog.json').read_text())
    row = next((r for r in [*catalog['examples'],*catalog['details']] if r['key'] == key), None)
    if row is None:
        raise ValueError('Unknown spaceship reference; use spaceship list or spaceship details')
    if row.get('use') == 'inspiration':
        raise ValueError('This source is an inspiration study with unresolved source errors. Study its guide or export a reusable module instead.')
    report = export_manual(confined(atlas, key), outdir, force=force)
    return dict(report, title=row['title'], next='Build scene.plan.json, inspect the new mounting interfaces and render the combined spacecraft.')
