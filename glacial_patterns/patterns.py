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


def _wiggle(seed, tile, amp):
    """A gentle wander that is *periodic* over ``tile`` (sum of low harmonics
    with integer frequencies), so a wavy line stays seamless when tiled. Gives
    laminae/foresets an uneven, hand-drawn look instead of ruled-straight."""
    r = _rng(seed)
    comps = [(k, amp * (0.4 + 0.6 * next(r)) / k, next(r) * 2 * math.pi)
             for k in (1, 2, 3)]
    return lambda x: sum(a * math.sin(2 * math.pi * k * x / tile + ph)
                         for k, a, ph in comps)


def _wavy_polyline(y, tile, wig, stroke="#555", sw=0.8, step=3):
    pts = " ".join(f"{x},{y + wig(x):.1f}" for x in range(0, tile + step, step))
    return f'<polyline points="{pts}" fill="none" stroke="{stroke}" stroke-width="{sw}"/>'


def _clast(cx, cy, kind, s, rot, fill="#d2d2d2", stroke="#222", sw=1.1):
    if kind == "dot":
        return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{s:.1f}" fill="{stroke}"/>'
    if kind == "ell":
        return (f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{s:.1f}" ry="{s*0.62:.1f}" '
                f'transform="rotate({rot:.0f} {cx:.1f} {cy:.1f})" fill="{fill}" '
                f'stroke="{stroke}" stroke-width="{sw}"/>')
    # angular clast: irregular polygon, vertex count & radii jittered from
    # position so no two clasts are the same shape
    h = int(abs(cx * 131.1 + cy * 57.7)) % 1000
    nv = 5 + (h % 3)                            # 5-7 vertices
    pts = []
    for i in range(nv):
        rr = 0.68 + (((h >> i) ^ (i * 37)) % 100) / 100.0 * 0.5   # 0.68..1.18
        a = math.radians(rot + i * 360.0 / nv)
        pts.append(f"{cx + s*rr*math.cos(a):.1f},{cy + s*rr*math.sin(a):.1f}")
    return (f'<polygon points="{" ".join(pts)}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}"/>')


def _scatter(tile, n, smin, smax, seed, kinds=("ang", "ell"), align=0.0, skew=2.0):
    """Scatter n clasts of widely varied size (poorly-sorted diamict look).

    ``skew`` biases the size distribution toward smaller clasts with occasional
    large ones (skew>1); ``align`` (0..1) flattens clast long-axes toward
    horizontal (a crude fabric). Larger clasts drawn last so they sit on top.
    """
    r = _rng(seed)
    grains = []
    for _ in range(n):
        cx, cy = next(r) * tile, next(r) * tile
        s = smin + (smax - smin) * (next(r) ** skew)
        kind = kinds[int(next(r) * len(kinds)) % len(kinds)]
        rot = (next(r) - 0.5) * 70 * (1 - align)   # align -> near-horizontal
        grains.append((s, _clast(cx, cy, kind, s, rot)))
    grains.sort(key=lambda g: g[0])
    return "\n".join(g for _, g in grains)


# ---------------------------------------------------------------- diamicton ---
def diamicton_massive(tile=88, density=13, seed=7):       # Dmm
    """Massive till: poorly-sorted, matrix-supported - clasts of widely varied
    size and random orientation (no fabric), floating in a stippled matrix."""
    inner = (_stipple(tile, 18, seed + 99, 0.7, 1.4)
             + _scatter(tile, density, 3, 12, seed, kinds=("ang", "ang", "ell"), skew=2.4))
    return tile, wrap9(inner, tile)


def diamicton_stratified(tile=88, density=11, seed=5):     # Dms
    """Stratified till: as massive, but with a weak sub-horizontal fabric and
    faint discontinuous partings (waterlain / melt-out)."""
    partings = "".join(_wavy_polyline(y, tile, _wiggle(seed + y, tile, 1.4),
                                      "#8a8a8a", 0.6)
                       for y in range(16, tile, 22))
    inner = (_stipple(tile, 14, seed + 3, 0.7, 1.3)
             + _scatter(tile, density, 3, 10, seed, kinds=("ang", "ell"),
                        align=0.6, skew=2.2))
    return tile, partings + wrap9(inner, tile)


def diamicton_clast(tile=88, density=20, seed=11):         # Dcm
    """Clast-supported diamict: densely packed, varied clasts, little matrix."""
    inner = _scatter(tile, density, 5, 12, seed, kinds=("ang", "ell", "ang"), skew=1.4)
    return tile, wrap9(inner, tile)


# ------------------------------------------------------------------- gravel ---
def gravel_clast(tile=84, seed=3):                         # Gh (clast-supported)
    """Clast-supported gravel, crudely bedded and *imbricated*: disc/blade
    clasts consistently tilted (a-axis dipping up-current) - the classic
    palaeocurrent fabric of bed-load gravel."""
    r = _rng(seed); els = []
    imbric = -30 * FLOW                    # a-axes dip up-current (signed by FLOW)
    for row in range(6):
        y = 7 + row * 13 + (row % 2) * 2
        x = 4 + (row % 2) * 7
        while x < tile + 6:
            s = 5.5 + (next(r) ** 1.5) * 6     # varied sizes, a few large
            els.append(_clast(x, y, "ell", s, imbric + (next(r) - .5) * 16))
            x += s * 1.5
    return tile, wrap9("\n".join(els), tile)


# --------------------------------------------------------------------- sand ---
def _stipple(tile, n, seed, rmin, rmax, fill="#3a3a3a"):
    """Irregular stipple: random positions and varied grain sizes (not a grid)."""
    r = _rng(seed)
    return "\n".join(
        f'<circle cx="{next(r)*tile:.1f}" cy="{next(r)*tile:.1f}" '
        f'r="{rmin + (rmax-rmin)*next(r):.2f}" fill="{fill}"/>' for _ in range(n))


def _sand_ground(tile, seed, n=55):
    """A light sand stipple ground, so 'cross-bedded/ripple sand' reads as sand
    even where the structure is sparse (per FGDC 609-611)."""
    return wrap9(_stipple(tile, n, seed + 7, 0.5, 0.9, fill="#9a9a9a"), tile)


def sand_massive(tile=44, n=34, seed=4):                   # Sm
    """Massive sand: irregular stipple of varied grain size."""
    return tile, wrap9(_stipple(tile, n, seed, 0.7, 1.7), tile)


# Flow convention: FLOW = +1 draws transport left-to-right (down-current = +x),
# the standard convention (USGS / general practice). Foreset & ripple marks and
# clast imbrication all derive their direction from it.
FLOW = 1


def sand_ripple(tile=54, seed=6):                          # Sr (ripple x-lam)
    """Ripple cross-lamination: climbing trains of asymmetric current ripples.

    Convention (why the direction matters): the steep **lee face points
    down-current** and the **foreset laminae dip down-current** - to the right
    for FLOW=+1 (left-to-right). The gentle stoss faces up-current. Both the
    crest asymmetry and the foreset dip are keyed to FLOW via ``X(f)``, so the
    ornament flips consistently if the flow convention is reversed.
    """
    d = FLOW                               # +1 => down-current is +x (rightward)
    els = [_sand_ground(tile, seed)]       # sand lithology reads through
    wl = 18                                # ripple wavelength (divides tile)

    def X(cx, f):                          # fraction f in [0,1], mirrored for d<0
        return cx + wl * (0.5 + (f - 0.5) * d)

    for row, y0 in enumerate(range(6, tile + 6, 9)):
        climb = (row * 6) % wl             # phase step per row = climbing
        for cx in range(-wl + climb, tile + wl, wl):
            # crest: gentle stoss (up-current) -> peak -> steep lee (down-current)
            els.append(f'<path d="M {X(cx,0):.1f},{y0+4} '
                       f'C {X(cx,0.5):.1f},{y0+3} {X(cx,0.75):.1f},{y0-3} '
                       f'{X(cx,0.85):.1f},{y0-3} C {X(cx,0.9):.1f},{y0-3} '
                       f'{X(cx,0.95):.1f},{y0+1} {X(cx,1):.1f},{y0+4}" '
                       f'fill="none" stroke="#3f3f3f" stroke-width="1.0"/>')
            for f in (0.80, 0.87, 0.94):   # foresets on the lee, dipping down-current
                fx = X(cx, f)
                els.append(f'<line x1="{fx:.1f}" y1="{y0-2:.1f}" '
                           f'x2="{fx + d*2.6:.1f}" y2="{y0+3:.1f}" '
                           f'stroke="#8a8a8a" stroke-width="0.55"/>')
    return tile, f'<g clip-path="url(#clip{tile})">' + "\n".join(els) + "</g>"


# --------------------------------------------------------- fines / rhythmite ---
def rhythmite(tile=55, couplet=11, seed=0):                # Fl (varve)
    """Rhythmites (varves): couplets of a dark winter clay and lighter summer
    silt, drawn with gently wavy, uneven-thickness laminae - suspension
    settling, not ruled lines. Fixed couplet pitch (divides tile) keeps the
    repeat seamless while thickness and waviness vary couplet to couplet."""
    els = []
    for y in range(0, tile, couplet):
        wig = _wiggle(seed + y, tile, 1.1)
        th = 1.8 + (int(abs(y * 53.3)) % 100) / 100.0 * 1.8   # clay thickness
        top = " ".join(f"{x},{y + wig(x):.1f}" for x in range(0, tile + 3, 3))
        bot = " ".join(f"{x},{y + th + wig(x):.1f}" for x in range(tile, -3, -3))
        els.append(f'<polygon points="{top} {bot}" fill="#555"/>')
        els.append(_wavy_polyline(y + th + 3.0, tile, wig, "#9a9a9a", 0.6))
        els.append(_wavy_polyline(y + th + 6.0, tile, wig, "#b4b4b4", 0.5))
    return tile, "\n".join(els)


def mud_massive(tile=48, seed=8):                          # Fm (structureless mud)
    """Massive silt & clay - the standard mudstone ornament: broken horizontal
    dashes in offset rows."""
    r = _rng(seed); els = []
    for row, y in enumerate(range(6, tile, 8)):
        x = -next(r) * 12
        while x < tile + 4:
            w = 6 + next(r) * 7
            els.append(f'<line x1="{x:.1f}" y1="{y}" x2="{x+w:.1f}" y2="{y}" '
                       f'stroke="#555" stroke-width="1.0"/>')
            x += w + 7 + next(r) * 7
    return tile, wrap9("\n".join(els), tile)


# ------------------------------------------------------------------- eolian ---
def loess(tile=34, seed=9):                                # Em
    """Loess: dense, fine, *irregular* eolian-silt stipple (no grid)."""
    return tile, wrap9(_stipple(tile, 60, seed, 0.55, 1.0), tile)


# ------------------------------------------------------------------ organic ---
def peat(tile=48, seed=10):                                # P (organic / peat)
    """Peat / organic mud: compressed fibrous lenses - irregular, discontinuous
    horizontal dashes of varied length, denser than a ruled dash ornament."""
    r = _rng(seed); els = []
    for y in range(6, tile, 9):
        x = -next(r) * 14
        while x < tile + 6:
            w = 8 + next(r) * 12
            yy = y + (next(r) - 0.5) * 2.4
            els.append(f'<rect x="{x:.1f}" y="{yy:.1f}" width="{w:.1f}" '
                       f'height="2.6" rx="1.3" fill="#2b2b2b"/>')
            x += w + 6 + next(r) * 10
    return tile, wrap9("\n".join(els), tile)


# ------------------------------------------------------- more glaciofluvial ---


def gravel_matrix(tile=88, density=13, seed=17):           # Gms (debris flow)
    """Matrix-supported gravel: varied clasts floating (not touching) in a
    stippled sandy matrix - en-masse debris-flow emplacement, no sorting."""
    inner = (_stipple(tile, 46, seed + 5, 0.6, 1.1)
             + _scatter(tile, density, 4, 11, seed, kinds=("ell", "ang", "ell"), skew=2.0))
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
