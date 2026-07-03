"""Tileable SVG fill patterns for glacial / Quaternary stratigraphic columns.

Each generator returns ``(tile, inner_svg)`` where ``tile`` is the square tile
edge (SVG user units) and ``inner_svg`` is black line-work drawn on a
transparent ground (the white background is added by the renderer). Discrete
ornaments (clasts, stipple) are wrapped across tile edges with :func:`wrap9`
so the pattern tiles seamlessly.

The generators are deliberately parametric: clast density and size, lamina
spacing, and stipple density are arguments, so a facies is a *family* you tune
to a section rather than one frozen tile. Codes follow the Eyles/Miall
lithofacies convention (Dmm, Dms, Sr, Fl, ...) with plain-name aliases in
``catalog.py``.
"""
import math
import itertools

# deterministic pseudo-random so tiles are reproducible (no Math.random churn)
def _rng(seed):
    x = (seed * 2654435761) & 0xFFFFFFFF
    while True:
        x ^= (x << 13) & 0xFFFFFFFF
        x ^= x >> 17
        x ^= (x << 5) & 0xFFFFFFFF
        yield (x & 0xFFFF) / 0xFFFF


def wrap9(inner, tile):
    """Nine translated copies so ornaments crossing an edge reappear opposite.
    The SVG <pattern> clips each copy to the tile, giving a seamless repeat."""
    g = []
    for ox, oy in itertools.product((-tile, 0, tile), repeat=2):
        g.append(f'<g transform="translate({ox} {oy})">{inner}</g>')
    return "\n".join(g)


def _clast(cx, cy, kind, s, rot, fill="#d2d2d2", stroke="#222", sw=1.1):
    if kind == "dot":
        return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{s:.1f}" fill="{stroke}"/>'
    if kind == "ell":
        return (f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{s:.1f}" ry="{s*0.62:.1f}" '
                f'transform="rotate({rot:.0f} {cx:.1f} {cy:.1f})" fill="{fill}" '
                f'stroke="{stroke}" stroke-width="{sw}"/>')
    pts = []                                    # angular clast: irregular pentagon
    for i, r in enumerate((1.0, 0.72, 1.06, 0.8, 0.94)):
        a = math.radians(rot + i * 72)
        pts.append(f"{cx + s*r*math.cos(a):.1f},{cy + s*r*math.sin(a):.1f}")
    return (f'<polygon points="{" ".join(pts)}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}"/>')


def _scatter(tile, n, smin, smax, seed, kinds=("ang", "ell"), align=0.0):
    """Scatter n clasts; ``align`` (0..1) flattens toward horizontal (fabric)."""
    r = _rng(seed)
    els = []
    for _ in range(n):
        cx, cy = next(r) * tile, next(r) * tile
        s = smin + next(r) * (smax - smin)
        kind = kinds[int(next(r) * len(kinds)) % len(kinds)]
        rot = (next(r) - 0.5) * 60 * (1 - align)   # align -> near-horizontal
        els.append(_clast(cx, cy, kind, s, rot))
    return "\n".join(els)


def _fines(tile, n, seed, r_=1.0):
    r = _rng(seed)
    return "\n".join(
        f'<circle cx="{next(r)*tile:.1f}" cy="{next(r)*tile:.1f}" r="{r_}" fill="#333"/>'
        for _ in range(n))


# ---------------------------------------------------------------- diamicton ---
def diamicton_massive(tile=84, density=8, seed=7):        # Dmm
    inner = _scatter(tile, density, 5, 9, seed) + _fines(tile, density + 4, seed + 99, 1.7)
    return tile, wrap9(inner, tile)


def diamicton_stratified(tile=84, density=8, seed=5):      # Dms
    partings = "".join(
        f'<line x1="0" y1="{y}" x2="{tile}" y2="{y}" stroke="#888" '
        f'stroke-width="0.7" stroke-dasharray="7 5"/>' for y in range(14, tile, 20))
    inner = _scatter(tile, density, 5, 8, seed, align=0.7) + _fines(tile, density, seed + 3, 1.5)
    return tile, partings + wrap9(inner, tile)


def diamicton_clast(tile=84, density=15, seed=11):         # Dcm
    inner = _scatter(tile, density, 6, 11, seed, kinds=("ang", "ell", "ang"))
    return tile, wrap9(inner, tile)


# ------------------------------------------------------------------- gravel ---
def gravel_clast(tile=84, seed=3):                         # Gh (clast-supported)
    r = _rng(seed); els = []
    for row in range(6):
        y = 7 + row * 13 + (row % 2) * 2
        x = 4 + (row % 2) * 7
        while x < tile + 6:
            s = 6 + next(r) * 4
            els.append(_clast(x, y, "ell", s, (next(r) - .5) * 40))
            x += s * 1.7
    return tile, wrap9("\n".join(els), tile)


# --------------------------------------------------------------------- sand ---
def sand_massive(tile=40, n=26, seed=4):                   # Sm
    return tile, wrap9(_fines(tile, n, seed, 1.2), tile)


def sand_planar_xbed(tile=90, seth=30, dip=24, seed=1):    # SGp
    els = []
    for y0 in range(0, tile, seth):
        els.append(f'<line x1="0" y1="{y0}" x2="{tile}" y2="{y0}" stroke="#222" stroke-width="1.4"/>')
        run = seth / math.tan(math.radians(dip))
        x = -tile
        while x < tile * 2:
            els.append(f'<line x1="{x:.1f}" y1="{y0+seth}" x2="{x+run:.1f}" y2="{y0}" '
                       f'stroke="#6a6a6a" stroke-width="0.8"/>')
            x += 11
    return tile, f'<g clip-path="url(#clip{tile})">' + "\n".join(els) + "</g>"


def sand_trough_xbed(tile=96, seth=30, seed=2):            # SGt (festoon)
    """Nested concave-up trough sets, stacked to fill each coset; set
    boundaries truncate the festoons above."""
    els = []
    span = tile // 2
    for si, y0 in enumerate(range(0, tile, seth)):
        els.append(f'<line x1="0" y1="{y0}" x2="{tile}" y2="{y0}" stroke="#222" stroke-width="1.3"/>')
        for ri, yb in enumerate(range(y0 + 8, y0 + seth + 8, 9)):
            off = ((si + ri) % 2) * (span // 2)
            for c in range(-1, 4):
                cx = c * span + off
                for k in range(1, 4):
                    rx = k * (span / 6)
                    els.append(f'<path d="M {cx-rx:.1f} {yb} Q {cx:.1f} {yb-2*k-3} '
                               f'{cx+rx:.1f} {yb}" fill="none" stroke="#6a6a6a" stroke-width="0.8"/>')
    return tile, f'<g clip-path="url(#clip{tile})">' + "\n".join(els) + "</g>"


def sand_ripple(tile=48, seed=6):                          # Sr (climbing ripples)
    """Climbing-ripple trains: asymmetric crests with stoss-side foreset hatch,
    each row offset up-current to suggest climb."""
    els = []
    for row, y0 in enumerate(range(4, tile, 10)):
        shift = (row % 2) * 8
        for cx in range(-10 + shift, tile + 12, 15):
            els.append(f'<path d="M {cx} {y0+7} Q {cx+5} {y0-1} {cx+11} {y0+7}" '
                       f'fill="none" stroke="#444" stroke-width="1.0"/>')
            for fx in range(cx + 2, cx + 10, 2):
                els.append(f'<line x1="{fx}" y1="{y0+7}" x2="{fx+2.4}" y2="{y0+1}" '
                           f'stroke="#888" stroke-width="0.6"/>')
    return tile, f'<g clip-path="url(#clip{tile})">' + "\n".join(els) + "</g>"


# --------------------------------------------------------- fines / rhythmite ---
def rhythmite(tile=48, couplet=12, seed=0):                # Fl (varve)
    els = []
    for y in range(0, tile, couplet):
        els.append(f'<rect x="0" y="{y}" width="{tile}" height="2.6" fill="#555"/>')
        els.append(f'<line x1="0" y1="{y+5.5:.1f}" x2="{tile}" y2="{y+5.5:.1f}" stroke="#999" stroke-width="0.7"/>')
        els.append(f'<line x1="0" y1="{y+8.5:.1f}" x2="{tile}" y2="{y+8.5:.1f}" stroke="#999" stroke-width="0.7"/>')
    return tile, "\n".join(els)


def mud_massive(tile=54, seed=8):                          # Fm (structureless mud)
    return tile, wrap9(_fines(tile, 8, seed, 0.8), tile)


# ------------------------------------------------------------------- eolian ---
def loess(tile=30, seed=9):                                # Em
    els = []
    for i, j in itertools.product(range(6), range(6)):
        jx = ((i * 7 + j * 13) % 5 - 2) * 0.4
        jy = ((i * 11 + j * 5) % 5 - 2) * 0.4
        els.append(f'<circle cx="{i*5+2+jx:.1f}" cy="{j*5+2+jy:.1f}" r="0.9" fill="#333"/>')
    return tile, wrap9("\n".join(els), tile)


# ------------------------------------------------------------------ organic ---
def peat(tile=48, seed=10):                                # P (organic / peat)
    els = []
    for row, y in enumerate(range(6, tile, 11)):
        x = (row % 2) * 12
        while x < tile + 12:
            els.append(f'<rect x="{x}" y="{y}" width="16" height="3.2" rx="1.4" fill="#2b2b2b"/>')
            x += 24
    return tile, wrap9("\n".join(els), tile)


# ------------------------------------------------------- more glaciofluvial ---
def sand_laminated(tile=44, seed=15):                      # Sh (plane beds)
    """Horizontally laminated sand: even, closely spaced plane-bed laminae."""
    els = [f'<line x1="0" y1="{y}" x2="{tile}" y2="{y}" stroke="#666" '
           f'stroke-width="0.8"/>' for y in range(4, tile, 6)]
    return tile, "\n".join(els)


def gravel_matrix(tile=84, density=11, seed=17):           # Gms (debris flow)
    """Matrix-supported gravel: floating clasts in a stippled sandy matrix."""
    inner = (_fines(tile, 40, seed + 5, 0.9)
             + _scatter(tile, density, 6, 10, seed, kinds=("ell", "ang", "ell")))
    return tile, wrap9(inner, tile)


# --------------------------------------------------- colluvial / deformation ---
def colluvium(tile=80, density=10, seed=13):               # Cdm (soliflucted)
    """Soliflucted colluvial diamict: elongate clasts aligned down-slope with
    wavy solifluction partings."""
    waves = []
    for y0 in range(12, tile, 22):
        pts = ",".join(f"{x} {y0 + 3*math.sin(x/tile*2*math.pi*2):.1f}"
                       for x in range(0, tile + 4, 4))
        waves.append(f'<polyline points="{pts}" fill="none" stroke="#999" '
                     f'stroke-width="0.7"/>')
    r = _rng(seed); cl = []
    for _ in range(density):
        cx, cy = next(r) * tile, next(r) * tile
        cl.append(_clast(cx, cy, "ell", 6 + next(r) * 3, 28 + (next(r) - .5) * 16))
    return tile, "".join(waves) + wrap9("".join(cl), tile)


def deformed_fines(tile=64, seed=14):                      # Fd (glaciotectonite)
    """Folded / contorted laminae - soft-sediment or glaciotectonic deformation."""
    els = []
    for y0 in range(0, tile, 7):
        ph = 2 * math.pi * 2 * (y0 / tile)
        amp = 3 + 1.5 * math.sin(y0)
        pts = " ".join(f"{x},{y0 + amp*math.sin(x/tile*2*math.pi + ph):.1f}"
                       for x in range(0, tile + 3, 3))
        els.append(f'<polyline points="{pts}" fill="none" stroke="#555" '
                   f'stroke-width="0.9"/>')
    return tile, "\n".join(els)


def collapsed_beds(tile=90, seed=16):                      # SGc (ice-contact)
    """Ice-contact / collapse structures: bedded sand cut by small normal
    faults that offset the laminae into grabens."""
    def off(x):
        return 4 if tile * 0.32 < x < tile * 0.68 else 0   # central graben
    els = []
    for y0 in range(6, tile, 8):
        els.append(f'<path d="M 0 {y0} L {tile*0.32:.0f} {y0} '
                   f'L {tile*0.32:.0f} {y0+4} L {tile*0.68:.0f} {y0+4} '
                   f'L {tile*0.68:.0f} {y0} L {tile} {y0}" fill="none" '
                   f'stroke="#666" stroke-width="0.8"/>')
    for fx in (tile * 0.32, tile * 0.68):                  # fault planes
        els.append(f'<line x1="{fx:.0f}" y1="0" x2="{fx:.0f}" y2="{tile}" '
                   f'stroke="#222" stroke-width="1.1"/>')
    return tile, "\n".join(els)


# ------------------------------------------------------------------ bedrock ---
def bedrock(tile=52, seed=12):                             # R (undifferentiated)
    r = _rng(seed); els = []
    for _ in range(11):
        cx, cy = next(r) * tile, next(r) * tile
        a = next(r) * math.pi
        dx, dy = 5 * math.cos(a), 5 * math.sin(a)
        els.append(f'<line x1="{cx-dx:.1f}" y1="{cy-dy:.1f}" x2="{cx+dx:.1f}" y2="{cy+dy:.1f}" '
                   f'stroke="#333" stroke-width="1.1"/>')
        els.append(f'<line x1="{cx-dy*0.5:.1f}" y1="{cy+dx*0.5:.1f}" x2="{cx+dy*0.5:.1f}" '
                   f'y2="{cy-dx*0.5:.1f}" stroke="#333" stroke-width="1.1"/>')
    return tile, wrap9("\n".join(els), tile)
