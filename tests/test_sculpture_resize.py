import hashlib
import json
from pathlib import Path

import pytest

from ldraw_tools.sculpture.resize import resample_voxels


@pytest.fixture
def palette(tmp_path):
    (tmp_path / 'LDConfig.ldr').write_text(
        '0 !COLOUR Red CODE 4 VALUE #FF0000 EDGE #333333\n'
        '0 !COLOUR Blue CODE 1 VALUE #0000FF EDGE #333333\n'
        '0 !COLOUR Purple CODE 22 VALUE #800080 EDGE #333333\n')
    return tmp_path


def source(tmp_path, rows):
    path = tmp_path / 'cells.json'
    path.write_text(json.dumps({'voxels': rows}))
    return path


def test_upsampling_preserves_aspect_colors_and_empty_cells(tmp_path, palette):
    rows = [[x+10,y-5,z+2,4 if x < 2 else 1] for x in range(4) for y in range(2) for z in range(2)
            if (x,y,z) != (1,1,1)]
    path = source(tmp_path, rows)
    data, report = resample_voxels(path, resolution=8, library=palette)
    cells = {tuple(r[:3]):r[3] for r in data['voxels']}
    assert report['dimensions'] == [8,4,4]
    assert len(cells) == len(rows)*8
    for row in rows:
        xyz = [row[0]-10,row[1]+5,row[2]-2]
        for dx in range(2):
            for dy in range(2):
                for dz in range(2):
                    assert cells[(xyz[0]*2+dx,xyz[1]*2+dy,xyz[2]*2+dz)] == row[3]
    assert (2,2,2) not in cells


def test_shrinking_averages_rgb_not_ldraw_identifiers(tmp_path, palette):
    rows = [[x,y,z,4 if x%2 == 0 else 1] for x in range(16) for y in range(2) for z in range(2)]
    data, report = resample_voxels(source(tmp_path,rows),resolution=8,library=palette)
    assert report['dimensions'] == [8,1,1]
    assert {r[3] for r in data['voxels']} == {22}


def test_repeated_voxel_resize_retains_a_saved_color_edit(tmp_path, palette):
    rows = [[x,y,z,4] for x in range(8) for y in range(2) for z in range(2)]
    rows[-1][-1] = 1
    path = source(tmp_path,rows)
    grown, _ = resample_voxels(path,resolution=16,library=palette)
    path.write_text(json.dumps(grown))
    restored, _ = resample_voxels(path,resolution=8,library=palette)
    assert restored == {'voxels':rows}


@pytest.mark.parametrize('resolution',[0,7,97,True,16.5])
def test_invalid_size_preserves_input(tmp_path,palette,resolution):
    path=source(tmp_path,[[0,0,0,4]])
    original=path.read_bytes()
    with pytest.raises(ValueError): resample_voxels(path,resolution=resolution,library=palette)
    assert path.read_bytes()==original


def test_resizing_obeys_world_and_occupied_cell_limits(tmp_path,palette):
    sparse = source(tmp_path,[[0,0,0,4],[7,7,7,4]])
    with pytest.raises(ValueError,match='world'): resample_voxels(sparse,resolution=96,library=palette)
    dense = source(tmp_path,[[x,y,z,4] for x in range(8) for y in range(8) for z in range(8)])
    with pytest.raises(ValueError,match='occupied'): resample_voxels(dense,resolution=48,library=palette)


def test_resize_cli_repacks_checks_connectivity_and_writes_editable_revision(tmp_path,palette,monkeypatch):
    from ldraw_tools import cli
    rows=[[x,y,z,4] for x in range(8) for y in range(2) for z in range(2)]
    path=source(tmp_path,rows);output=tmp_path/'resized.mpd'
    monkeypatch.setattr(cli,'get_parts',lambda *a,**k:object())
    monkeypatch.setattr(cli,'validate_text',lambda *a,**k:(object(),[]))
    args=cli.parser().parse_args(['--library',str(palette),'resize-sculpture',str(path),'--resolution','16','--output',str(output)])
    report,status=cli.run(args)
    assert status==0 and report['stud_components']==1 and report['connected_instruction_prefixes']
    assert report['resize']['dimensions']==[16,4,4]
    marker=json.loads(output.with_suffix('.sculpture.json').read_text())
    assert marker['model_sha256']==hashlib.sha256(output.read_bytes()).hexdigest()
    assert 'source_glb_sha256' not in marker
    assert output.read_text().count('0 STEP')==report['brick_count']
