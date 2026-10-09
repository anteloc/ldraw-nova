"""Every recipe page's generator runs and passes check (previews are built separately)."""
import importlib.util
import re

import pytest

from ldraw_tools.common import ROOT

spec = importlib.util.spec_from_file_location("build_recipes", ROOT / "scripts/build_recipes.py")
build_recipes = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build_recipes)
PAGES = list(build_recipes.recipes())


@pytest.mark.parametrize("page, code", PAGES, ids=[page.stem for page, _ in PAGES])
def test_recipe_passes_check(official, page, code, tmp_path):
    passed, mpd, text = build_recipes.run(page, code, tmp_path)
    assert passed and mpd.exists(), text
    assert (ROOT / "docs/reference/img" / f"{page.stem}.png").exists(), "run scripts/build_recipes.py to add the preview"


def test_catalog_links_every_recipe():
    catalog = (ROOT / "docs/reference/README.md").read_text()
    for page, _ in PAGES:
        assert f"({page.name})" in catalog, f"{page.name} missing from docs/reference/README.md"
    assert len(PAGES) >= 5


def test_recipe_pages_stay_short():
    for page, _ in PAGES:
        assert len(page.read_text().encode()) <= 5200, f"{page.name} is over 5 KB"
        assert "```mermaid" in page.read_text(), f"{page.name} needs a connection diagram"
