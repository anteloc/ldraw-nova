"""One-call review (look) and delivery (deliver) through the installed LeoCAD."""
import shutil

import pytest
from PIL import Image

from ldraw_tools.common import ROOT, library_path
from ldraw_tools.deliver import deliver
from ldraw_tools.kit import Model
from ldraw_tools.look import look

pytestmark = pytest.mark.skipif(shutil.which("leocad") is None, reason="LeoCAD CLI unavailable")


def test_look_makes_one_labelled_sheet_with_problems(official, tmp_path):
    result = look(ROOT / "examples/building-atlas/details/porch/porch.mpd", official, library_path(), tmp_path,
                  views=("home", "top"), problems=True)
    sheet = Image.open(result["sheet"])
    assert sheet.width > sheet.height and result["highlighted"] == 18   # the unbridged half is magenta
    assert "18 floating" in result["notes"][0]


def test_deliver_writes_summary_and_artifacts(official, tmp_path):
    model = Model("crate", "A small crate")
    base = model.place("3020", "Reddish_Brown", cell=(0, 0), level=0)
    model.place("3010", "Reddish_Brown", cell=(0, 0), level=base.top)
    path = tmp_path / "crate.mpd"
    model.save(path, quiet=True)
    result = deliver(path, official, library_path(), glb=False)
    summary = (tmp_path / "delivery/summary.md").read_text()
    assert result["verdict"] == "PASS" and result["bom_matches"]
    assert "**Check: PASS**" in summary and "```mermaid" in summary and "| 3020 Plate  2 x  4 | Reddish_Brown | 1 |" in summary
