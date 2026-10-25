from types import SimpleNamespace
import pytest

from ldraw_tools.mechanism_catalog import inventory, model_inventory


class Library:
    def __init__(self, root, files):
        self.by_code = {}
        self.files = {}
        for code, content in files.items():
            p = root / (code + ".dat")
            p.write_text(content)
            self.files[code] = p
            self.by_code[code] = content.splitlines()[0][2:]

    def find_part(self, *, code):
        return SimpleNamespace(path=self.files[code]) if code in self.files else None


def test_all_assignments_missing_parts_and_transformed_alias(tmp_path):
    categories = tmp_path / "categories"
    (categories / "parts").mkdir(parents=True)
    (categories / "parts" / "technic.py").write_text(
        'SameName="old"\nSameName="shaft"\nRubberBeltFormed="85543-f3"\n'
    )
    library = Library(
        tmp_path,
        {
            "shaft": "0 Technic Axle Test\n0 !LDRAW_ORG Part\n",
            "cam": "0 Technic Cam Test\n0 !LDRAW_ORG Part\n",
            "old": "0 ~Moved to cam\n0 !LDRAW_ORG Part\n1 16 3 0 0 -1 0 0 0 1 0 0 0 -1 cam.dat\n",
            "joint": "0 Technic Universal Joint (Complete)\n0 !LDRAW_ORG Shortcut\n1 16 0 0 0 1 0 0 0 1 0 0 0 1 shaft.dat\n",
        },
    )
    report = inventory(library, categories=categories)
    rows = {r["ref"]: r for r in report["parts"]}
    assert (
        rows["old.dat"]["symbols"][0]["symbol"]
        == rows["shaft.dat"]["symbols"][0]["symbol"]
    )
    assert report["summary"]["supplied_technic_assignments"] == 3
    assert not rows["85543-f3.dat"]["installed"]
    assert "belt" in rows["85543-f3.dat"]["families"]
    old = rows["old.dat"]
    assert old["canonical_ref"] == "cam.dat" and old["families"] == ["cam"]
    assert old["alias_transform"] == [
        [-1.0, 0.0, 0.0, 3.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, -1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]
    assert rows["joint.dat"]["shortcut"] and not rows["joint.dat"]["alias_chain"]
    assert all(r["motion_profile"] == "unreviewed" for r in rows.values())


def test_nested_model_and_embedded_part_boundary(tmp_path):
    f = tmp_path / "test.mpd"
    f.write_text(
        "0 FILE main.ldr\n1 16 0 0 0 1 0 0 0 1 0 0 0 1 child.ldr\n"
        "0 FILE child.ldr\n1 16 0 0 0 1 0 0 0 1 0 0 0 1 embedded.dat\n"
        "0 FILE embedded.dat\n1 16 0 0 0 1 0 0 0 1 0 0 0 1 3705.dat\n"
    )
    assert model_inventory(f) == {"embedded.dat": 1}


def test_external_assembly_is_not_misreported_as_one_physical_part(tmp_path):
    f = tmp_path / "test.ldr"
    f.write_text("0 External assembly\n1 16 0 0 0 1 0 0 0 1 0 0 0 1 child.ldr\n")
    with pytest.raises(ValueError, match="Unresolved assembly"):
        model_inventory(f)


def test_supplied_technic_coverage_and_live_aliases(official):
    from ldraw_tools.catalog import assignments, category_path
    import ast

    report = inventory(official)
    rows = {r["ref"]: r for r in report["parts"]}
    expected = {
        v.value + ".dat"
        for _, v, _ in assignments(category_path() / "parts/technic.py")
        if isinstance(v, ast.Constant) and isinstance(v.value, str)
    }
    assert expected <= rows.keys()
    assert rows["6575.dat"]["canonical_ref"] == "6575a.dat"
    assert rows["6575.dat"]["alias_transform"][0][0] == -1
    assert rows["370526.dat"]["canonical_ref"] == "3705.dat"
    assert (
        rows["77590.dat"]["installed"] and "coupling" in rows["77590.dat"]["families"]
    )
