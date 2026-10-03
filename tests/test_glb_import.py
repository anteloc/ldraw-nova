import hashlib
from io import BytesIO
import json
import struct

import numpy as np
import pytest

trimesh = pytest.importorskip("trimesh")
from PIL import Image
from ldraw_tools.sculpture.glb_import import validate_glb, voxelize_glb, convert_glb, surface_colors, ldraw_palette
from ldraw_tools.sculpture.conversion import convert


@pytest.fixture
def palette(tmp_path):
    library = tmp_path / "library"
    library.mkdir()
    (library / "LDConfig.ldr").write_text(
        "0 !COLOUR Red CODE 4 VALUE #FF0000 EDGE #333333\n"
        "0 !COLOUR Blue CODE 1 VALUE #0000FF EDGE #333333\n"
        "0 !COLOUR Main CODE 16 VALUE #FF0000 EDGE #333333\n"
        "0 !COLOUR Clear CODE 40 VALUE #00FF00 EDGE #333333 ALPHA 128\n")
    return library


def save(tmp_path, scene):
    path = tmp_path / "mesh.glb"
    path.write_bytes(scene.export(file_type="glb"))
    return path


def colored_box(color, extents=(1, 1, 1)):
    box = trimesh.creation.box(extents)
    box.visual = trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(baseColorFactor=[*color, 255]))
    return box


def alter_document(data, change):
    size = struct.unpack_from("<I", data, 12)[0]
    document = json.loads(data[20:20 + size]); change(document)
    encoded = json.dumps(document).encode(); encoded += b" " * (-len(encoded) % 4)
    tail = data[20 + size:]
    return struct.pack("<4sII", b"glTF", 2, 20 + len(encoded) + len(tail)) + struct.pack("<II", len(encoded), 0x4E4F534A) + encoded + tail


def test_scene_transforms_instances_material_colors_and_proportions(tmp_path, palette):
    scene = trimesh.Scene()
    scene.add_geometry(colored_box([255, 0, 0]), node_name="red")
    transform = trimesh.transformations.translation_matrix([0, 2, 0])
    scene.add_geometry(colored_box([0, 0, 255]), node_name="blue", transform=transform)
    data, report = voxelize_glb(save(tmp_path, scene), resolution=16, library=palette)
    rows = np.array(data["voxels"])
    assert report["mesh_instances"] == 2
    assert report["dimensions"] == [7, 7, 16]
    assert set(rows[:, 3]) == {1, 4}
    assert rows[rows[:, 3] == 1, 2].min() > rows[rows[:, 3] == 4, 2].max()
    assert list(rows[:, :3].min(axis=0)) == [0, 0, 0]
    again, again_report = voxelize_glb(tmp_path / "mesh.glb", resolution=16, library=palette)
    assert data == again and report == again_report


def test_texture_detail_is_sampled_between_vertices(tmp_path, palette):
    plane = trimesh.Trimesh(vertices=[[0,0,0],[1,0,0],[1,1,0],[0,1,0]], faces=[[0,1,2],[0,2,3]], process=False)
    texture = np.full((16,16,3), [255,0,0], dtype=np.uint8)
    texture[4:12,4:12] = [0,0,255]
    plane.visual = trimesh.visual.TextureVisuals(uv=[[0,0],[1,0],[1,1],[0,1]],
        material=trimesh.visual.material.PBRMaterial(baseColorTexture=Image.fromarray(texture), baseColorFactor=[255,255,255,255]))
    data, report = voxelize_glb(save(tmp_path, trimesh.Scene(plane)), resolution=16, library=palette)
    assert report["palette_colors"] == 2
    cells = {tuple(r[:3]):r[3] for r in data["voxels"]}
    assert cells[(8,0,6)] == 1  # Center texture is blue although all four vertices are red.
    assert cells[(0,0,0)] == 4
    plane.visual.material.baseColorFactor = [128,255,255,255]
    assert surface_colors(plane, np.array([[0,0,0]]))[0,0] == 128


def test_vertex_color_interpolation():
    mesh = trimesh.Trimesh(vertices=[[0,0,0],[1,0,0],[0,1,0]], faces=[[0,1,2]], process=False)
    mesh.visual.vertex_colors = [[255,0,0,255],[0,0,255,255],[255,0,0,255]]
    rgb = surface_colors(mesh, np.array([[0.5,0,0]]))[0]
    assert np.allclose(rgb, [127.5,0,127.5])


def test_vertex_tint_is_preserved_when_a_material_is_also_present(tmp_path, palette):
    mesh = colored_box([255,255,255])
    mesh.visual.vertex_attributes['color'] = np.tile([0.,0.,1.,1.],(len(mesh.vertices),1))
    path = save(tmp_path,trimesh.Scene(mesh))
    data,_ = voxelize_glb(path,resolution=8,library=palette)
    assert {row[3] for row in data['voxels']} == {1}


def test_palette_excludes_inherited_and_transparent_colors(palette):
    codes, _ = ldraw_palette(palette)
    assert list(codes) == [1,4]


@pytest.mark.parametrize("change", [
    lambda d: d["buffers"][0].update(uri="file:///etc/passwd"),
    lambda d: d.update(images=[{"uri":"https://example.org/texture.png"}]),
    lambda d: d.update(extensionsRequired=["KHR_draco_mesh_compression"]),
    lambda d: d["meshes"][0]["primitives"][0].update(mode=1),
    lambda d: d["accessors"][0].update(count=1_000_000_000),
    lambda d: d["bufferViews"][0].update(byteLength=1_000_000_000),
    lambda d: d.update(skins=[{}]),
    lambda d: d['materials'][0]['pbrMetallicRoughness'].update(baseColorTexture={'index':0,'texCoord':1}),
])
def test_rejects_unsafe_or_unbounded_glb_before_loading(tmp_path, palette, monkeypatch, change):
    path = save(tmp_path, trimesh.Scene(colored_box([255,0,0])))
    path.write_bytes(alter_document(path.read_bytes(), change))
    monkeypatch.setattr(trimesh,"load_scene",lambda *a, **k: pytest.fail("Unsafe GLB reached loader"))
    with pytest.raises(ValueError): voxelize_glb(path, resolution=16, library=palette)


@pytest.mark.parametrize("data", [b"", b"not a GLB"*3, struct.pack("<4sII",b"glTF",2,25)+b"broken JSON!"])
def test_rejects_bad_container(data):
    with pytest.raises(ValueError): validate_glb(data)


def test_subdivision_budget_and_resolution_are_checked(tmp_path, palette, monkeypatch):
    import ldraw_tools.sculpture.glb_import as module
    path = save(tmp_path, trimesh.Scene(colored_box([255,0,0])))
    for value in [0,97,True,16.5]:
        with pytest.raises(ValueError, match="resolution"): voxelize_glb(path,resolution=value,library=palette)
    monkeypatch.setattr(module,"MAX_SAMPLES",1)
    with pytest.raises(ValueError, match="too complex"): voxelize_glb(path,resolution=16,library=palette)


def test_voxelized_mesh_uses_existing_packer_and_preserves_surface(tmp_path, palette):
    path = save(tmp_path, trimesh.Scene(colored_box([255,0,0])))
    data, _ = voxelize_glb(path,resolution=8,library=palette)
    source = tmp_path / "voxels.json"; source.write_text(json.dumps(data))
    text, report = convert(source)
    assert report["checks_passed"] and report["stud_components"] == 1
    assert report["connected_instruction_prefixes"]
    assert {tuple(r) for r in data["voxels"]} <= {tuple(r) for r in report["voxel_data"]["voxels"]}
    assert text.count("0 STEP") == report["brick_count"]


def test_cli_writes_revision_bound_editable_artifacts(tmp_path, palette, monkeypatch):
    from ldraw_tools import cli
    path = save(tmp_path,trimesh.Scene(colored_box([255,0,0])))
    output = tmp_path / "import.mpd"
    monkeypatch.setattr(cli,"get_parts",lambda *a, **k: object())
    monkeypatch.setattr(cli,"validate_text",lambda *a, **k: (object(),[]))
    args = cli.parser().parse_args(["--library",str(palette),"glb-sculpture",str(path),"--resolution","8","--output",str(output)])
    report, status = cli.run(args)
    assert status == 0 and report["import"]["voxelizer"] == "trimesh-subdivide"
    voxels = output.with_suffix(".repaired.voxels.json")
    marker = json.loads(output.with_suffix(".sculpture.json").read_text())
    assert marker["model_sha256"] == hashlib.sha256(output.read_bytes()).hexdigest()
    assert marker["voxel_sha256"] == hashlib.sha256(voxels.read_bytes()).hexdigest()
    original = output.read_bytes()
    path.write_bytes(b"broken GLB")
    with pytest.raises(ValueError): cli.run(args)
    assert output.read_bytes() == original


def test_auto_size_targets_actual_packed_bricks_and_keeps_surface_colors(tmp_path, palette):
    path = save(tmp_path, trimesh.Scene(colored_box([255,0,0])))
    text, report = convert_glb(path, library=palette, target_bricks=3000)
    metadata = report['import']
    assert metadata['target_bricks'] == 3000 and metadata['target_reached']
    assert 2700 <= report['brick_count'] <= 3300
    assert text.count('0 STEP') == report['brick_count'] == metadata['brick_count']
    assert report['checks_passed'] and report['stud_components'] == 1
    assert report['connected_instruction_prefixes']
    surface, _ = voxelize_glb(path, resolution=metadata['resolution'], library=palette)
    assert {tuple(row) for row in surface['voxels']} <= {tuple(row) for row in report['voxel_data']['voxels']}
    assert len(metadata['size_trials']) <= 5


def test_auto_size_keeps_best_connected_result_when_larger_sizes_hit_limits(tmp_path, palette, monkeypatch):
    import ldraw_tools.sculpture.glb_import as module
    path = save(tmp_path, trimesh.Scene(colored_box([255,0,0])))
    original = module.voxelize_glb
    def bounded(path, *, resolution, library):
        if resolution > 8: raise ValueError('Voxel grid is too large; lower the resolution')
        return original(path, resolution=resolution, library=library)
    monkeypatch.setattr(module,'voxelize_glb',bounded)
    _, report = convert_glb(path, library=palette)
    assert report['checks_passed'] and report['stud_components'] == 1
    assert report['import']['target_reached'] is False
    assert report['import']['resolution'] == 8
    assert any(not trial['converted'] for trial in report['import']['size_trials'])


def test_auto_size_rejects_unsafe_input_before_search(tmp_path, palette, monkeypatch):
    import ldraw_tools.sculpture.glb_import as module
    path = save(tmp_path, trimesh.Scene(colored_box([255,0,0])))
    path.write_bytes(alter_document(path.read_bytes(),lambda d:d['buffers'][0].update(uri='https://example.org/mesh.bin')))
    monkeypatch.setattr(module,'voxelize_glb',lambda *a,**k:pytest.fail('Unsafe input reached size search'))
    with pytest.raises(ValueError): convert_glb(path,library=palette)


def test_cli_defaults_to_auto_size_and_allows_explicit_manual_override():
    from ldraw_tools import cli
    auto = cli.parser().parse_args(['glb-sculpture','mesh.glb','--output','model.mpd'])
    assert auto.resolution is None and auto.target_bricks == 3000
    manual = cli.parser().parse_args(['glb-sculpture','mesh.glb','--output','model.mpd','--resolution','16'])
    assert manual.resolution == 16
    with pytest.raises(SystemExit):
        cli.parser().parse_args(['glb-sculpture','mesh.glb','--output','model.mpd','--resolution','16','--target-bricks','3000'])
