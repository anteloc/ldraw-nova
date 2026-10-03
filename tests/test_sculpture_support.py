import numpy as np
import pytest

pytest.importorskip("scipy")
pytest.importorskip("networkx")

from ldraw_tools.sculpture.brick_structure import Brick
from ldraw_tools.sculpture.voxel_support import (
    SupportAudit,
    add_voxel_supports,
    audit_supports,
)


def test_audit_requires_stud_contacts_without_deleting_bricks():
    bricks = [
        Brick(h=2, w=2, x=0, y=0, z=0),
        Brick(h=2, w=2, x=0, y=0, z=1),
        Brick(h=1, w=2, x=2, y=0, z=0),
    ]
    voxels = np.zeros((3, 2, 2), dtype=bool)
    for brick in bricks:
        voxels[brick.slice] = True
    audit = audit_supports(bricks, voxels)
    assert not audit.conflicts[0, 0, 1]
    assert audit.conflicts[2, :, 0].all()
    assert audit.components == 2
    assert len(bricks) == 3


def test_self_supporting_floating_pair_is_reported():
    bricks = [
        Brick(h=2, w=2, x=0, y=0, z=0),
        Brick(h=1, w=1, x=3, y=0, z=2),
        Brick(h=1, w=1, x=3, y=0, z=3),
    ]
    voxels = np.zeros((4, 2, 4), dtype=bool)
    for brick in bricks:
        voxels[brick.slice] = True
    audit = audit_supports(bricks, voxels)
    assert audit.conflicts[3, 0, 2:4].all()
    assert len(bricks) == 3


def test_local_thickening_preserves_cells_colors_and_unaffected_areas():
    voxels = np.ones((20, 2, 1), dtype=bool)
    colors = np.random.default_rng(42).integers(1, 8, size=voxels.shape)
    original_colors = colors.copy()
    conflicts = np.zeros_like(voxels)
    conflicts[15:, :, 0] = True
    audit = SupportAudit(conflicts, voxels & ~conflicts)
    repaired, rgb = add_voxel_supports(voxels, colors, audit)
    assert repaired[:, :, 0].all()
    assert repaired[14:, :, 1].all()  # overlap with the existing main structure
    assert not repaired[:14, :, 1].any()
    assert np.array_equal(rgb[:, :, 0], original_colors[:, :, 0])
    assert np.array_equal(rgb[14:, :, 1], original_colors[14:, :, 0])
    assert np.array_equal(colors, original_colors)
    assert voxels.shape == (20, 2, 1)


def test_broad_thickening_reinforces_the_affected_flat_section():
    voxels = np.ones((20, 2, 1), dtype=bool)
    colors = np.ones(voxels.shape, dtype=int)
    conflicts = np.zeros_like(voxels)
    conflicts[19, :, 0] = True
    repaired, _ = add_voxel_supports(
        voxels, colors, SupportAudit(conflicts, voxels & ~conflicts), broad=True
    )
    assert repaired[:, :, 1].all()


def test_island_gets_a_two_layer_bridge_to_main_structure():
    voxels = np.zeros((9, 2, 5), dtype=bool)
    voxels[:2, :, :3] = True
    voxels[7:, :, 4] = True
    colors = np.ones(voxels.shape, dtype=int)
    conflicts = np.zeros_like(voxels)
    conflicts[7:, :, 4] = True
    audit = SupportAudit(conflicts, voxels & ~conflicts)
    repaired, _ = add_voxel_supports(voxels, colors, audit)
    # The bridge descends to the nearest anchor, then crosses to the main model.
    assert repaired[1:8, 0, 2:4].all()
    assert repaired[7, 0, 2:5].all()
    assert repaired[:, :, : voxels.shape[2]][voxels].all()


def test_no_conflicts_and_repair_limits_leave_the_model_unchanged():
    voxels = np.ones((20, 2, 1), dtype=bool)
    colors = np.ones(voxels.shape, dtype=int)
    clean = SupportAudit(np.zeros_like(voxels), voxels)
    assert add_voxel_supports(voxels, colors, clean)[0] is voxels
    conflicts = SupportAudit(voxels, np.zeros_like(voxels))
    assert add_voxel_supports(voxels, colors, conflicts, max_added=1)[0] is voxels
    assert add_voxel_supports(voxels, colors, conflicts, max_grid_cells=40)[0] is voxels


def test_repair_does_not_exceed_supported_editor_dimensions_or_voxel_count():
    for shape in [(1, 1, 96), (100, 100, 10)]:
        voxels = np.ones(shape, dtype=bool)
        colors = np.ones((*shape, 3))
        conflicts = np.zeros_like(voxels)
        conflicts[:, :, -1] = True
        audit = SupportAudit(conflicts, voxels & ~conflicts)
        assert add_voxel_supports(voxels, colors, audit)[0] is voxels


def hollow_box(shape=(9, 9, 9)):
    voxels = np.ones(shape, dtype=bool)
    voxels[1:-1, 1:-1, 1:-1] = False
    colors = np.random.default_rng(42).integers(1, 8, size=shape)
    conflicts = np.zeros_like(voxels)
    conflicts[4, 4, -1] = True
    return voxels, colors, SupportAudit(conflicts, voxels & ~conflicts)


def test_internal_repair_preserves_the_entire_exterior_and_existing_colors():
    voxels, colors, audit = hollow_box()
    repaired, rgb = add_voxel_supports(voxels, colors, audit, inside_only=True)
    added = repaired & ~voxels
    assert added.any()
    assert repaired.shape == voxels.shape  # no bounding-box expansion
    for axis in range(3):
        assert np.array_equal(
            np.take(repaired, [0, -1], axis=axis), np.take(voxels, [0, -1], axis=axis)
        )
    assert np.array_equal(rgb[voxels], colors[voxels])
    assert np.array_equal(rgb[4, 4, 7], colors[4, 4, 8])
    assert not repaired[4, 4, 1]  # local repair stays near the conflict


def test_broad_internal_repair_can_fill_the_affected_enclosed_cavity():
    voxels, colors, audit = hollow_box()
    repaired, rgb = add_voxel_supports(
        voxels, colors, audit, inside_only=True, broad=True
    )
    assert repaired.all()
    assert np.array_equal(rgb[voxels], colors[voxels])


def test_internal_repair_does_not_fill_cavities_open_to_outside_air():
    voxels, colors, audit = hollow_box()
    voxels[4, 4, 0] = False  # open a hole far from the roof conflict
    for broad in (False, True):
        repaired, _ = add_voxel_supports(
            voxels, colors, audit, inside_only=True, broad=broad
        )
        assert repaired is voxels


def test_broad_internal_repair_leaves_unaffected_enclosed_bodies_alone():
    box, box_colors, _ = hollow_box((7, 7, 7))
    voxels = np.zeros((16, 7, 7), dtype=bool)
    voxels[:7] = box
    voxels[9:] = box
    colors = np.zeros(voxels.shape, dtype=int)
    colors[:7] = box_colors
    colors[9:] = box_colors
    conflicts = np.zeros_like(voxels)
    conflicts[3, 3, 6] = True
    audit = SupportAudit(conflicts, voxels & ~conflicts)
    repaired, _ = add_voxel_supports(
        voxels, colors, audit, inside_only=True, broad=True
    )
    assert repaired[:7].all()
    assert np.array_equal(repaired[9:], voxels[9:])


def test_internal_supports_respect_budget_without_creating_partial_repairs():
    voxels, colors, audit = hollow_box()
    repaired, _ = add_voxel_supports(
        voxels, colors, audit, inside_only=True, max_added=1
    )
    assert repaired is voxels
