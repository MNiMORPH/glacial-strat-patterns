"""Tests for the facies catalog, generators, and shipped assets.

Run: ``pytest``. These need no SVG renderer (they don't rasterise); they check
that every generator produces a valid tile, the catalog is internally
consistent, alias/code lookup works, and the committed assets and metadata
match the catalog.
"""
import json
import os

import pytest

from glacial_patterns import FACIES, BY_CODE, PROCESS, resolve
from glacial_patterns.build import swatch_svg

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_codes_unique():
    codes = [c for c, *_ in FACIES]
    assert len(codes) == len(set(codes)), "duplicate facies code"


def test_aliases_unique():
    aliases = [al for _, _, al, *_ in FACIES]
    assert len(aliases) == len(set(aliases)), "duplicate alias"


@pytest.mark.parametrize("code", list(BY_CODE))
def test_generator_returns_valid_tile(code):
    tile, inner = BY_CODE[code]["fn"]()
    assert isinstance(tile, int) and tile > 0
    assert isinstance(inner, str) and inner.strip()


@pytest.mark.parametrize("code", list(BY_CODE))
def test_generator_is_deterministic(code):
    """Seeded PRNG -> identical output across calls (reproducible tiles)."""
    assert BY_CODE[code]["fn"]() == BY_CODE[code]["fn"]()


@pytest.mark.parametrize("code", list(BY_CODE))
def test_swatch_svg_is_wellformed(code):
    svg = swatch_svg(code, BY_CODE[code]["fn"])
    assert svg.startswith("<?xml") or svg.lstrip().startswith("<svg")
    assert f"pat_{code}" in svg and svg.count("<pattern") == 1


def test_process_covers_every_facies():
    assert set(PROCESS) == set(BY_CODE)
    assert all(PROCESS[c].strip() for c in PROCESS)
    assert resolve("Dmm")["process"]


def test_resolve_by_code_and_alias():
    assert resolve("Dmm")["code"] == "Dmm"
    assert resolve("till (massive)")["code"] == "Dmm"
    with pytest.raises(KeyError):
        resolve("not-a-facies")


def test_shipped_assets_match_catalog():
    for code, *_ in FACIES:
        assert os.path.exists(os.path.join(ROOT, "svg", f"{code}.svg")), code
        assert os.path.exists(os.path.join(ROOT, "png", f"{code}.png")), code


def test_metadata_matches_catalog():
    meta = json.load(open(os.path.join(ROOT, "metadata", "facies.json")))
    assert {m["code"] for m in meta} == {c for c, *_ in FACIES}
