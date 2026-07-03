"""Matplotlib helper: fill stratigraphic-column boxes with facies patterns.

The pre-rasterised PNG tiles (from :mod:`glacial_patterns.build`) are tiled to
fill a column interval; dropstones are drawn as placed features over a fine
fill. This is the streamlined path for Python strat columns::

    import matplotlib.pyplot as plt
    from glacial_patterns import mpl
    fig, ax = plt.subplots()
    mpl.column_fill(ax, "Dmm", 0, 1, 0, 3)      # till from 0-3 m
    mpl.column_fill(ax, "Fl",  0, 1, 3, 5)      # varves 3-5 m
    mpl.dropstone(ax, 0.5, 4.2, 0.12)
    ax.set_xlim(0, 1); ax.set_ylim(6, 0)         # depth downward
"""
import os

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Ellipse

from .catalog import resolve

_PNG = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "png")
_cache = {}


def tile_image(key):
    """RGBA array for a facies tile, looked up by code or alias."""
    code = resolve(key)["code"]
    if code not in _cache:
        p = os.path.join(_PNG, f"{code}.png")
        if not os.path.exists(p):
            raise FileNotFoundError(f"{p} missing - run `python -m glacial_patterns.build`")
        _cache[code] = plt.imread(p)
    return _cache[code]


def column_fill(ax, key, x0, x1, y0, y1, tile_width=None, edge="black", lw=1.2,
                zorder=1):
    """Fill the rectangle (x0..x1, y0..y1) with a tiled facies pattern.

    ``tile_width`` is the width of one tile in data units (default: a third of
    the box width); vertical repeats are matched to keep tiles square.
    """
    img = tile_image(key)
    w, h = float(x1 - x0), abs(float(y1 - y0))
    tw = tile_width or w / 3.0
    nx = max(1, round(w / tw))
    ny = max(1, round(h / tw))
    big = np.tile(img, (ny, nx, 1))
    lo, hi = sorted((y0, y1))
    im = ax.imshow(big, extent=(x0, x1, lo, hi), origin="upper", aspect="auto",
                   interpolation="none", zorder=zorder)
    clip = Rectangle((x0, lo), w, h, transform=ax.transData)
    im.set_clip_path(clip)
    if edge:
        ax.add_patch(Rectangle((x0, lo), w, h, fill=False, edgecolor=edge,
                               linewidth=lw, zorder=zorder + 0.1))
    return im


def dropstone(ax, x, y, r, aspect=0.8, zorder=3):
    """A placed dropstone: a clast in a cleared halo with laminae deflected
    around it. Draw over an Fl/Fm fill to signal ice-rafted debris."""
    ax.add_patch(Ellipse((x, y), 2 * (r + 0.35 * r), 2 * (r + 0.3 * r),
                         facecolor="white", edgecolor="none", zorder=zorder - 0.1))
    ax.add_patch(Ellipse((x, y), 2 * r, 2 * r * aspect, facecolor="#cfcfcf",
                         edgecolor="#111", linewidth=1.3, zorder=zorder))
    for dy in (-(r + 0.15 * r), (r + 0.15 * r)):
        xs = np.linspace(x - 3 * r, x + 3 * r, 30)
        ys = y + dy + dy * 0.9 * np.exp(-((xs - x) / (1.3 * r)) ** 2)
        ax.plot(xs, ys, color="#555", linewidth=1.1, zorder=zorder - 0.05)


def boulder_pavement(ax, y, x0, x1, r=0.055, zorder=3):
    """A line of clasts along a surface at depth ``y`` - a boulder pavement /
    lag, marking a subglacial erosion surface or deflation lag."""
    n = max(3, int((x1 - x0) / (2.1 * r)))
    xs = np.linspace(x0 + r, x1 - r, n)
    for i, cx in enumerate(xs):
        rr = r * (0.8 + 0.4 * ((i * 37) % 5) / 4)
        ax.add_patch(Ellipse((cx, y), 2 * rr, 2 * rr * 0.62, facecolor="#cfcfcf",
                             edgecolor="#111", linewidth=1.1, zorder=zorder))


def erosion_contact(ax, y, x0, x1, amp=None, zorder=4):
    """A scalloped erosional contact line across a column at depth ``y``."""
    amp = amp if amp is not None else 0.02 * (x1 - x0)
    xs = np.linspace(x0, x1, 120)
    n = max(2, round((x1 - x0) / (4 * (amp + 1e-9))))
    ys = y - amp * np.abs(np.sin(np.pi * n * (xs - x0) / (x1 - x0)))
    ax.plot(xs, ys, color="black", linewidth=1.6, zorder=zorder)
