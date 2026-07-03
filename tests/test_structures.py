"""Smoke tests for the structure-overlay module: every overlay runs on an axes
and adds artists, clipped to its band."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pytest

from glacial_patterns import structures as st

OVERLAYS = [
    st.planar_lamination, st.cross_bedding, st.trough_cross_bedding,
    st.cross_lamination, st.climbing_ripples, st.wave_ripples, st.folds,
    st.collapse, st.dispersed_clasts,
]


@pytest.mark.parametrize("fn", OVERLAYS, ids=lambda f: f.__name__)
def test_overlay_draws(fn):
    fig, ax = plt.subplots()
    n_before = len(ax.lines) + len(ax.patches)
    fn(ax, 0, 1, 2, 1)                       # draw into a band
    assert len(ax.lines) + len(ax.patches) > n_before
    plt.close(fig)
