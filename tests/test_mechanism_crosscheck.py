"""Cross-check the kinematic graph against an independent implementation.

LegoTechnicSimulation (a sibling checkout, MIT licence, read in place and never
copied) reports 31 rigid units, 42 revolute joints and 5 gear meshes for its
Walker1 sample. Nova must find the same joints and meshes, and must never fuse
parts that it keeps apart. The only difference allowed is at the four 32013
angle connectors, where Walker1 puts each 6L axle 2 LDU off the pin hole: Nova
seats a pin within 0.2 LDU, the other project within 3.
"""
from collections import defaultdict
from itertools import combinations
from pathlib import Path

import numpy as np
import pytest

from ldraw_tools.connection_adapter import connection_contacts
from ldraw_tools.connectivity import inspect_connections
from ldraw_tools.mechanism import analyse
from ldraw_tools.validation import validate_file

WALKER = Path(__file__).resolve().parents[2] / 'LegoTechnicSimulation' / 'sample_models' / 'Walker1' / 'Walker1.ldr'
CONNECTORS = ('2780', '3673', '4459', '6558', '32556', '3749', '43093', '11214', '3704', '3705', '3706', '3707',
              '4519', '32062', '44294', '60485', '32073', '3737', '3708')


@pytest.mark.skipif(not WALKER.exists(), reason='LegoTechnicSimulation checkout not beside this repository')
def test_walker_matches_the_independent_reading(official):
    model, _ = validate_file(WALKER, official, assembly=True)
    inspection = inspect_connections(model, official)
    graph = analyse(inspection, connection_contacts(inspection))
    assert len(graph['joints']) == 42
    assert len(graph['meshes']) == 5
    ratios = sorted(tuple(m['ratio']) for m in graph['meshes'])
    assert ratios == [(8, 24), (12, 14), (12, 14), (20, 12), (24, 24)]
    groups = defaultdict(set)
    for group, members in graph['members'].items():
        for index in members:
            if index >= 0 and graph['items'][index].occurrence.part_code not in CONNECTORS:
                groups[group].add(graph['items'][index].occurrence.part_code)
    # The four angle connectors stand alone: Walker1's axle misses each pin hole by 2 LDU. Without them the
    # structural groups are the other project's 31 units, less the one merge it makes through those connectors.
    structural = [codes for codes in groups.values() if codes]
    alone = [codes for codes in structural if codes == {'32013'}]
    assert len(alone) == 4 and len(structural) - len(alone) == 32
