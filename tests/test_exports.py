"""Tests for the matplotlib hatch export and the Inkscape pattern palette."""
import json
import os
import xml.dom.minidom as minidom

import pytest

from glacial_patterns import FACIES, BY_CODE
from glacial_patterns.hatch import HATCH, hatch_for

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_hatch_covers_every_facies():
    assert set(HATCH) == set(BY_CODE)


def test_hatch_for_by_code_and_alias():
    assert hatch_for("Dmm") == HATCH["Dmm"]
    assert hatch_for("till (massive)") == HATCH["Dmm"]


@pytest.mark.parametrize("h", list(HATCH.values()))
def test_hatch_strings_use_valid_symbols(h):
    assert set(h) <= set("/\\|-+xoO.*"), f"invalid hatch symbol in {h!r}"


def test_metadata_has_hatch_field():
    meta = json.load(open(os.path.join(ROOT, "metadata", "facies.json")))
    assert all("hatch" in m and m["hatch"] for m in meta)


def test_inkscape_palette_is_stock_tagged():
    p = os.path.join(ROOT, "inkscape", "glacial-patterns.svg")
    assert os.path.exists(p), "run `python -m glacial_patterns.build`"
    doc = minidom.parse(p)                       # also asserts well-formed XML
    pats = doc.getElementsByTagName("pattern")
    stock = [pt for pt in pats if pt.getAttribute("inkscape:isstock") == "true"]
    assert len(stock) == len(FACIES)
    assert all(pt.getAttribute("inkscape:stockid") for pt in stock)
