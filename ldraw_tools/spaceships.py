"""Spaceship design briefs and attributed construction kits.

Fictional propulsion is a design vocabulary, not an engineering simulation.
"""
from copy import deepcopy
import json
import os
from pathlib import Path
import shutil

from .common import ROOT
from .knowledge import resolve, require_exportable
from .manuals import export_manual


def default_reference():
    """Compatibility accessor for the explicitly selected Halcyon study."""
    folder = Path(resolve('halcyon', family='spaceship')['guide']).parent
    return dict(key='halcyon', title='Halcyon SNOT interceptor', category='starfighter',
        use='design-reference', default=False, construction='SNOT',
        lesson='Build a supported core with sideways hull skins and axial engine modules in their own local frames; use smooth contours and thin wings.',
        model=str(folder/'halcyon.mpd'), plan=str(folder/'halcyon.plan.json'),
        generator=str(folder/'generate.py'), guide=str(folder/'README.md'),
        preview=str(folder/'halcyon.png'), visual_review=str(folder/'visual-review.md'))


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
    design = deepcopy(ARCHETYPES[archetype])
    design['inspiration_references'] = [key for key in design['references'] if key.endswith('-study')]
    design['references'] = [key for key in design['references'] if key not in design['inspiration_references']]
    return dict(version=1, family='spaceship', archetype=archetype, **design,
        construction=None, default_reference=None, construction_options=['System', 'SNOT', 'Technic'],
        construction_strategy='Choose construction techniques from the requested silhouette, scale and interfaces. Establish supported attachment faces and adapt local modules to the brief. Halcyon is an optional core-and-skin lesson, not a default shape.',
        coordinates='X width, -Z forward, negative Y up; choose the hull or stand datum explicitly.',
        scale='Choose minifigure, display or microscale before selecting the canopy and detail sizes.',
        part_queries={
            'cockpit': 'a spacecraft canopy with a compatible cockpit rim and pilot controls',
            'hull': 'matched left and right wedge plates and slopes for an angular spaceship hull',
            'snot_mounts': 'side-stud bricks and brackets to support perpendicular spaceship hull panels and axial engine modules',
            'engines': 'a cylindrical thruster nacelle with concentric shells, grille intake and exhaust nozzle',
            'surface_detail': 'a small recessed spaceship machinery bay with grilles, bars, clips and dishes',
            'supports': 'a braced frame for long wings, cantilevered engines and a display stand'},
        interfaces='Record each module origin, bounds, exact mounting parts, attachment frames, and parent dependencies. Use proper rotations and real left/right parts.',
        review=['hull surfaces and engine modules seated on real attachment faces', 'smooth exterior contours and thin wing edges', 'front/top silhouette', 'side thickness and cockpit proportions', 'rear engine spacing', 'underside and stand attachments', 'bare frame and exposed wing roots', 'open cockpit or removable hull where interiors matter', 'quiet surfaces beside concentrated detail'],
        mechanism_scope='Study folding-wing, ramp or landing-gear mechanisms when requested. Static pose review does not verify motion; use explicit motion checks for animation or movement claims.',
        palette_note='Suggested design roles; inspect actual part/colour availability. Preserve functional and printed colours when adapting a source.',
        next='Retrieve relevant constructions for this brief, design its module layout, build, inspect interfaces, render and refine. Inspiration sources require explicit selection. A brief is not a generated model.')


def export_spaceship(key, outdir, *, force=False):
    row = require_exportable(resolve(key, family='spaceship'))
    if row['id'] == 'halcyon':
        reference = default_reference()
        source = Path(reference['guide']).parent.resolve()
        target = Path(outdir).resolve()
        if target == source or target.is_relative_to(source) or source.is_relative_to(target):
            raise ValueError('Choose a separate export directory')
        if target.exists() and any(target.iterdir()) and not force:
            raise ValueError('Export destination exists; use --force')
        target.mkdir(parents=True, exist_ok=True)
        for name in ['halcyon.mpd', 'halcyon.plan.json', 'generate.py', 'brief.json',
                     'README.md', 'visual-review.md', 'halcyon.png', 'core.png',
                     'modules.png', 'skins.png', 'views.png']:
            shutil.copyfile(source/name, target/name)
        guide = target/'README.md'
        guide.write_text(guide.read_text().replace('](../../../', ']('+os.path.relpath(ROOT, target)+'/'))
        return dict(output=str(target), title=reference['title'], scope='design-reference',
            plan=str(target/'halcyon.plan.json'), source=str(target/'halcyon.mpd'),
            next='Adapt the generator and plan to the new SNOT spacecraft; build and review the resulting model.')
    report = export_manual(Path(row['guide']).parent, outdir, force=force)
    return dict(report, title=row['title'], next='Build scene.plan.json, inspect the new mounting interfaces and render the combined spacecraft.')
