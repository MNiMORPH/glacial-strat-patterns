"""Matplotlib hatch export: vector, resolution-independent facies fills.

``column_fill`` in :mod:`glacial_patterns.mpl` tiles a raster PNG - crisp and
faithful, but raster. For publication figures you often want *vector* fills
that stay sharp at any zoom and export cleanly to PDF/SVG. Matplotlib hatches
do that, at the cost of fidelity: the built-in hatch alphabet
(``/ \\ | - + x o O . *``) can only approximate the tiles.

Each facies maps to its best built-in hatch approximation in :data:`HATCH`.
Use :func:`column_fill_hatch` exactly like ``mpl.column_fill``. When you need
the true ornament (scattered clasts, folded laminae, festoons), use the raster
tiles instead - this export trades fidelity for vector output, and says so.
"""
from matplotlib.patches import Rectangle

from .catalog import resolve, BY_CODE

# code -> best-effort built-in matplotlib hatch (approximate; see module docs)
HATCH = {
    "Dmm": "o",     "Dms": "o-",   "Dcm": "OO",   "Gh": "oo",   "Gms": "o.",
    "SGp": "//",    "SGt": "//\\\\", "Sr": "//",   "Sh": "--",   "Sm": "..",
    "Fl": "-",      "Fm": ".",     "Cdm": "o/",   "Fd": "xx",   "SGc": "|-",
    "Em": "...",    "P": "---",    "R": "++",
}

# facies whose ornament the built-in hatches cannot render faithfully
APPROXIMATE = {"Dmm", "Dms", "Dcm", "Gms", "SGt", "Sr", "Cdm", "Fd", "SGc"}


def hatch_for(key):
    """Matplotlib hatch string for a facies, by code or alias."""
    return HATCH[resolve(key)["code"]]


def column_fill_hatch(ax, key, x0, x1, y0, y1, facecolor="none",
                      hatch_color="black", edgecolor="black", lw=1.2,
                      density=1, zorder=1):
    """Fill the rectangle (x0..x1, y0..y1) with a vector facies hatch.

    ``density`` (int >= 1) multiplies hatch line density; ``facecolor`` tints
    the background; ``hatch_color`` and ``edgecolor`` set the hatch and border
    colours independently.
    """
    code = resolve(key)["code"]
    h = HATCH[code] * max(1, int(density))
    lo, hi = sorted((y0, y1))
    w, ht = x1 - x0, hi - lo
    # first patch carries the hatch (its edgecolor drives the hatch colour)
    ax.add_patch(Rectangle((x0, lo), w, ht, facecolor=facecolor,
                           edgecolor=hatch_color, hatch=h, linewidth=0,
                           zorder=zorder))
    if edgecolor:
        ax.add_patch(Rectangle((x0, lo), w, ht, fill=False, edgecolor=edgecolor,
                               linewidth=lw, zorder=zorder + 0.1))


def _check_coverage():
    missing = [c for c in BY_CODE if c not in HATCH]
    if missing:
        raise AssertionError(f"HATCH missing facies: {missing}")


_check_coverage()
