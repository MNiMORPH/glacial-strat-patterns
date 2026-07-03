"""Sedimentary-structure overlays for stratigraphic columns.

Structures are a *different class* from lithologies. A lithology (sand, gravel,
mud, diamicton, ...) is a **fill** (see :func:`glacial_patterns.mpl.column_fill`).
A structure (cross-bedding, ripples, folds, ...) is drawn **over** a lithology
as a band or lens that need not fill the interval - the way measured-section
keys separate "Lithology" from "Sedimentary Structures".

Every function draws into a rectangle ``(x0..x1, y0..y1)`` on top of whatever
fill is already there, clipped to that rectangle. Flow is left-to-right
(``FLOW = 1``); set it to ``-1`` to mirror.
"""
import numpy as np
from matplotlib.patches import Rectangle

FLOW = 1


def _band(y0, y1):
    lo, hi = sorted((float(y0), float(y1)))
    return lo, hi, hi - lo


def _clip(ax, artists, x0, x1, lo, hi):
    clip = Rectangle((x0, lo), x1 - x0, hi - lo, transform=ax.transData)
    for a in artists:
        a.set_clip_path(clip)


def planar_lamination(ax, x0, x1, y0, y1, spacing=None, color="#555", lw=0.9,
                      zorder=2):
    """Straight parallel laminae - upper-stage plane beds."""
    lo, hi, h = _band(y0, y1)
    sp = spacing or h / 6.0
    arts = [ax.plot([x0, x1], [y, y], color=color, lw=lw, zorder=zorder)[0]
            for y in np.arange(lo + sp / 2, hi, sp)]
    _clip(ax, arts, x0, x1, lo, hi)


def cross_bedding(ax, x0, x1, y0, y1, nsets=2, color="#555", lw=0.9, zorder=2):
    """Planar cross-beds: *large* sets of tangential foresets sweeping
    down-current, truncated by set-bounding surfaces."""
    lo, hi, h = _band(y0, y1)
    W = x1 - x0
    seth = h / nsets
    run = seth * 1.7 * FLOW
    arts = []
    t = np.linspace(0, 1, 24)
    for s in range(nsets):
        yb = lo + s * seth
        arts.append(ax.plot([x0, x1], [yb, yb], color="black", lw=1.3,
                            zorder=zorder)[0])
        for x in np.arange(x0 - abs(run), x1 + abs(run), W / 4.5):
            fx = x + run * t ** 1.7           # steep top -> tangential base
            fy = (yb + seth) - seth * t
            arts.append(ax.plot(fx, fy, color=color, lw=lw, zorder=zorder)[0])
    _clip(ax, arts, x0, x1, lo, hi)


def trough_cross_bedding(ax, x0, x1, y0, y1, nsets=2, ncols=3, color="#555",
                         lw=0.8, zorder=2):
    """Trough (festoon) cross-beds: concave-up scours filled with fanning
    tangential foresets."""
    lo, hi, h = _band(y0, y1)
    W = x1 - x0
    seth = h / nsets
    span = W / ncols
    arts = []
    for s in range(nsets):
        yb = lo + s * seth
        off = (s % 2) * span / 2
        for c in range(-1, ncols + 1):
            cx = x0 + c * span + off
            xx = np.linspace(cx - span / 2, cx + span / 2, 30)
            arts.append(ax.plot(xx, yb + (seth * 0.9) *
                                (1 - ((xx - cx) / (span / 2)) ** 2),
                                color="black", lw=1.1, zorder=zorder)[0])
            for k in range(1, 4):
                fr = k / 4.0
                xx2 = np.linspace(cx - span / 2 * (1 - 0.2 * k),
                                  cx + span / 2 * (1 - 0.05 * k), 24)
                arts.append(ax.plot(xx2, yb + 2 + (seth * 0.9 * fr) *
                                    (1 - ((xx2 - cx - FLOW * span * 0.12) /
                                          (span / 2)) ** 2),
                                    color=color, lw=lw, zorder=zorder)[0])
    _clip(ax, arts, x0, x1, lo, hi)


def climbing_ripples(ax, x0, x1, y0, y1, wl=None, color="#3f3f3f", lw=1.0,
                     zorder=2):
    """Climbing ripples drawn as stacked chevron / sawtooth laminae that climb
    up-current (per field-log convention; cf. reference keys)."""
    lo, hi, h = _band(y0, y1)
    W = x1 - x0
    wl = wl or W / 5.0
    rows = max(2, int(h / (0.6 * wl)))
    arts = []
    for r in range(rows):
        yb = lo + (r + 0.5) * h / rows
        climb = FLOW * (r % 3) * wl / 3.0
        xs = np.arange(x0 - wl, x1 + wl, wl) + climb
        # asymmetric chevron: gentle stoss then steep lee
        px, py = [], []
        for x in xs:
            px += [x, x + FLOW * wl * 0.7, x + FLOW * wl]
            py += [yb, yb - h / rows * 0.5, yb]
        arts.append(ax.plot(px, py, color=color, lw=lw, zorder=zorder)[0])
    _clip(ax, arts, x0, x1, lo, hi)


def wave_ripples(ax, x0, x1, y0, y1, wl=None, color="#555", lw=1.0, zorder=2):
    """Wave (oscillatory) ripples: smooth, symmetric undulating laminae."""
    lo, hi, h = _band(y0, y1)
    W = x1 - x0
    wl = wl or W / 4.0
    xs = np.linspace(x0, x1, 200)
    arts = []
    for i in range(max(2, int(h / (0.5 * wl)))):
        yb = lo + (i + 0.5) * h / max(2, int(h / (0.5 * wl)))
        arts.append(ax.plot(xs, yb + 0.14 * wl * np.sin(2 * np.pi * xs / wl),
                            color=color, lw=lw, zorder=zorder)[0])
    _clip(ax, arts, x0, x1, lo, hi)


def folds(ax, x0, x1, y0, y1, ntrains=3, color="#333", lw=1.0, zorder=3):
    """Convolute / recumbent folds as a *deformed band* over a lithology - a
    set of tight folds that need not fill the interval (per Ridge, 1997)."""
    lo, hi, h = _band(y0, y1)
    xs = np.linspace(x0, x1, 240)
    ph = (xs - x0) / (x1 - x0) * 2 * np.pi * ntrains
    prof = np.sin(ph) + 0.35 * np.sin(2 * ph - 0.6)     # asymmetric, overturned
    amp = 0.12 * h
    nlam = max(4, int(h / (0.11 * (x1 - x0))))
    arts = []
    for i in range(nlam):
        yb = lo + (i + 0.5) / nlam * h
        arts.append(ax.plot(xs, yb + amp * prof * (0.8 + 0.25 * np.sin(i * 1.3)),
                            color=color, lw=lw, zorder=zorder)[0])
    for fx, fy in ((0.28, 0.4), (0.6, 0.62), (0.82, 0.3)):  # recumbent hooks
        cx, cy, s = x0 + fx * (x1 - x0), lo + fy * h, 0.05 * (x1 - x0)
        t = np.linspace(0, 1.8 * np.pi, 40)
        arts.append(ax.plot(cx - s * (1 - t / 6) * np.cos(t),
                            cy + s * (1 - t / 6) * np.sin(t),
                            color=color, lw=lw, zorder=zorder)[0])
    _clip(ax, arts, x0, x1, lo, hi)


def dispersed_clasts(ax, x0, x1, y0, y1, n=14, seed=0, zorder=3):
    """Scattered / dispersed clasts (lonestones, ice-rafted debris) of varied
    size - drawn over a finer fill."""
    from matplotlib.patches import Ellipse
    lo, hi, h = _band(y0, y1)
    rng = np.random.RandomState(seed)
    W = x1 - x0
    arts = []
    for _ in range(n):
        cx = x0 + rng.rand() * W
        cy = lo + rng.rand() * h
        s = (0.02 + 0.04 * rng.rand() ** 2) * W
        e = Ellipse((cx, cy), 2 * s, 1.3 * s, angle=rng.rand() * 180,
                    facecolor="#d2d2d2", edgecolor="#222", lw=1.0, zorder=zorder)
        ax.add_patch(e)
        arts.append(e)
    _clip(ax, arts, x0, x1, lo, hi)
