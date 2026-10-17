import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from ldraw_tools.builder import build_plan
from ldraw_tools.common import ROOT
from ldraw_tools.geometry import analyze_geometry
from ldraw_tools.validation import validate_text
from conftest import mpd, ref


def simple_plan():
    return dict(version=1,author="Tests",sections=[dict(name="main.ldr",description="Stack",steps=[
        [dict(id="lower",ref="3001.dat",colour=4,at=[0,0,0])],
        [dict(id="upper",ref="3001.dat",colour=1,on="lower")]])])


def test_on_uses_upper_body_height(parts):
    plan=simple_plan()
    plan["sections"][0]["steps"][1][0]["ref"]="3022.dat"
    text,model,issues=build_plan(plan,parts)
    assert not issues
    assert model.pieces[1].position.y==-8
    assert text.startswith("0 FILE") and "\n" not in text.replace("\r\n","")


def test_bad_on_alignment_rejected(parts):
    plan=simple_plan()
    plan["sections"][0]["steps"][1][0]["offset_studs"]=[0.25,0]
    with pytest.raises(ValueError,match="aligned"):
        build_plan(plan,parts)


def test_bad_forward_on_rejected(parts):
    plan=simple_plan()
    plan["sections"][0]["steps"][1][0]["on"]="not-yet-placed"
    with pytest.raises(ValueError,match="earlier"):
        build_plan(plan,parts)


@pytest.mark.parametrize("key,value",[("at",[0,0]),("colour",True),("yaw",float('inf')),("unknown",1)])
def test_schema_rejects_invalid_plan(parts,key,value):
    import jsonschema
    plan=simple_plan();plan["sections"][0]["steps"][0][0][key]=value
    with pytest.raises(jsonschema.ValidationError):
        build_plan(plan,parts)


def test_overlapping_regular_bodies_are_errors(parts):
    model,_=validate_text(mpd(ref()+"\n"+ref(position="10 0 0")),parts)
    report=analyze_geometry(model,parts)
    assert "assembly.body_overlap" in {d["code"] for d in report["diagnostics"]}
    assert report["physical_validity"]=="not_proven"


def test_floating_parts_report_groups(parts):
    model,_=validate_text(mpd(ref()+"\n"+ref(position="200 0 0")),parts)
    report=analyze_geometry(model,parts)
    assert len(report["optimistic_components"])==2


def test_real_stud_connection_not_body_collision(official):
    _,model,issues=build_plan(simple_plan(),official)
    assert not issues
    report=analyze_geometry(model,official)
    assert report["complete"]
    assert not report["diagnostics"]
    assert report["overlap_candidate_count"]==1
    assert len(report["contacts"])>=8
    assert len(report["optimistic_components"])==1


def test_real_bridge_example(official):
    plan=json.loads((ROOT/"examples/bridge.plan.json").read_text())
    _,model,issues=build_plan(plan,official)
    assert not issues
    report=analyze_geometry(model,official)
    assert report["occurrence_count"]==5
    assert report["complete"] and not report["diagnostics"]
    assert len(report["optimistic_components"])==1
    assert sum(row.quantity for row in model.bill_of_materials(parts=official))==5


def test_cli_failure_does_not_write(tmp_path,official):
    plan=simple_plan()
    plan["sections"][0]["steps"][1][0].pop("on")
    plan["sections"][0]["steps"][1][0]["at"]=[10,0,0]
    source=tmp_path/"plan.json";source.write_text(json.dumps(plan))
    target=tmp_path/"model.mpd"
    result=subprocess.run([sys.executable,"-m","ldraw_tools.cli","build",str(source),"--output",str(target)],capture_output=True,text=True)
    assert result.returncode==1
    assert not target.exists()
    assert not json.loads(result.stdout)["written"]


def test_external_failures_cannot_pass(monkeypatch,tmp_path):
    from ldraw_tools.external import cad_check
    def fake_run(*args,**kwargs):
        return subprocess.CompletedProcess(args[0],0,"","")
    monkeypatch.setattr(subprocess,"run",fake_run)
    source=tmp_path/"model.mpd"
    source.write_text(mpd(ref()))
    with pytest.raises(ValueError,match="render failed"):
        cad_check(source,tmp_path)


def test_cli_palette_blocks_generation_before_writing_and_preserves_force_target(tmp_path, parts, monkeypatch):
    monkeypatch.setenv("LDRAW_DIR", str(parts.library_root))
    source = tmp_path / 'plan.json'; source.write_text(json.dumps(simple_plan()))
    palette = tmp_path / 'palette.csv'; palette.write_text('part_id,color_id,max_quantity\n3001,4,2\n')
    target = tmp_path / 'model.mpd'
    command = [sys.executable, '-m', 'ldraw_tools.cli', 'build', str(source), '--output', str(target)]
    failed = subprocess.run(command + ['--parts-palette', str(palette)], capture_output=True, text=True)
    assert failed.returncode != 0
    assert '3001.dat color 1' in json.loads(failed.stdout)['error']
    assert not target.exists()
    unrestricted = subprocess.run(command, capture_output=True, text=True)
    assert unrestricted.returncode == 0, unrestricted.stdout
    original = target.read_bytes()
    failed = subprocess.run(command + ['--force', '--parts-palette', str(palette)], capture_output=True, text=True)
    assert failed.returncode != 0
    assert target.read_bytes() == original
    palette.write_text('part_id,color_id,max_quantity\n3001,4,2\n3001,1,1\n')
    allowed = subprocess.run(command + ['--force', '--parts-palette', str(palette)], capture_output=True, text=True)
    assert allowed.returncode == 0, allowed.stdout
    assert json.loads(allowed.stdout)['parts_palette']['physical_parts'] == 2
    palette.write_text('part_id,color_id,max_quantity\n3001,4,2\n3001,1,0\n')
    exhausted = subprocess.run(command + ['--force', '--parts-palette', str(palette)], capture_output=True, text=True)
    assert exhausted.returncode != 0
    assert target.read_bytes() == original


@pytest.mark.parametrize('extension', ['ldr', 'xml', 'io'])
def test_cli_build_accepts_uploaded_inventory_formats(tmp_path, parts, monkeypatch, extension):
    import zipfile

    monkeypatch.setenv('LDRAW_DIR', str(parts.library_root))
    source = tmp_path / 'plan.json'
    source.write_text(json.dumps(simple_plan()))
    palette = tmp_path / ('palette.' + extension)
    target = tmp_path / 'model.mpd'
    model = '1 4 0 0 0 1 0 0 0 1 0 0 0 1 3001.dat\n'
    model += model.replace('1 4 ', '1 1 ')
    if extension == 'io':
        with zipfile.ZipFile(palette, 'w') as archive:
            archive.writestr('model.ldr', model)
    elif extension == 'xml':
        palette.write_text('<INVENTORY>' + ''.join(
            f'<ITEM><ITEMTYPE>P</ITEMTYPE><ITEMID>3001</ITEMID><COLOR>{color}</COLOR><MINQTY>1</MINQTY></ITEM>'
            for color in (5, 7)) + '</INVENTORY>')
    else:
        palette.write_text(model)
    result = subprocess.run([sys.executable, '-m', 'ldraw_tools.cli', 'build', str(source),
        '--output', str(target), '--parts-palette', str(palette)], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout
    assert target.is_file()
    assert json.loads(result.stdout)['parts_palette']['physical_parts'] == 2
