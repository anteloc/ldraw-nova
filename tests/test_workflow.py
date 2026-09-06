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
