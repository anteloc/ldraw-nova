"""Appearance warnings: visible defects that structural checks pass.

Cases come from measured models: a 1 x 2 plate inside a 1 x 8 plate at the same
height (found in the airliner, missed because 3023 has no body profile), bare
sideways studs, a wall directly behind a pane, and the legitimate shapes that
must stay quiet (stacked bricks, a brick under an arch).
"""
from ldraw import Model, Piece, Vector, Matrix

from ldraw_tools.geometry import analyze_geometry

X90 = Matrix([[1, 0, 0], [0, 0, -1], [0, 1, 0]])


def model(*pieces):
    return Model.from_pieces([Piece.place(ref, colour=colour, position=Vector(*at), **({'matrix': matrix} if matrix else {}))
                              for ref, colour, at, matrix in pieces], name='main.ldr')


def codes(report, prefix='appearance.'):
    return [d for d in report['diagnostics'] if d['code'].startswith(prefix)]


def test_stacked_bricks_and_brick_under_arch_are_quiet(official):
    stacked = analyze_geometry(model(('3001.dat', 4, (0, 0, 0), None), ('3001.dat', 1, (0, -24, 0), None)), official)
    assert stacked['appearance']['deep_overlaps'] == 0 and not codes(stacked)
    arch = analyze_geometry(model(('3307.dat', 15, (0, 0, 0), None), ('3005.dat', 4, (0, 24, 0), None)), official)
    assert arch['appearance']['deep_overlaps'] == 0


def test_plate_inside_plate_is_reported_with_both_placements(official):
    report = analyze_geometry(model(('3460.dat', 15, (0, 0, 0), None), ('3023.dat', 4, (0, 0, 0), None)), official)
    deep = [d for d in codes(report) if d['code'] == 'appearance.deep_overlap']
    assert len(deep) == 1 and sorted(deep[0]['instances']) == [0, 1] and deep[0]['depth'] >= 2


def test_bare_side_stud_is_reported_until_covered(official):
    bare = analyze_geometry(model(('87087.dat', 4, (0, 0, 0), None)), official)
    studs = [d for d in codes(bare) if d['code'] == 'appearance.exposed_side_studs']
    assert studs and studs[0]['count'] == 1 and studs[0]['examples'][0]['facing'] == '-Z'
    # A tile seated on the stud: origin = stud base - R * socket = (0,10,-10) - (0,0,8).
    covered = analyze_geometry(model(('87087.dat', 4, (0, 0, 0), None), ('3070b.dat', 15, (0, 10, -18), X90)), official)
    assert covered['appearance']['exposed_side_studs'] == 0


def test_wall_directly_behind_pane_is_reported(official):
    pane = ('60601.dat', 47, (0, 0, 0), None)
    clear = analyze_geometry(model(pane), official)
    assert clear['appearance']['glass_obstructed'] == 0
    walled = analyze_geometry(model(pane, ('3010.dat', 4, (0, 0, 10), None), ('3010.dat', 4, (0, 24, 10), None)), official)
    glass = [d for d in codes(walled) if d['code'] == 'appearance.glass_obstructed']
    assert len(glass) == 1 and glass[0]['instances'][0] == 0 and glass[0]['facing'] == '+Z'


def test_floating_group_names_nearest_support_and_gap(official):
    report = analyze_geometry(model(('3001.dat', 4, (0, 0, 0), None), ('3003.dat', 1, (0, -24, 100), None)), official)
    floating = [d for d in report['diagnostics'] if d['code'] == 'assembly.floating_group']
    assert len(floating) == 1
    assert floating[0]['instances'] == [1] and floating[0]['nearest_instance'] == 0
    assert floating[0]['gap'] == [0.0, 0.0, -60.0]  # the 2 x 2 brick's box starts 60 LDU behind
