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
    imbric = 28                            # consistent up-current tilt (degrees)
    for row in range(6):
        y = 7 + row * 13 + (row % 2) * 2
        x = 4 + (row % 2) * 7
        while x < tile + 6:
            s = 5.5 + (next(r) ** 1.5) * 6     # varied sizes, a few large
            els.append(_clast(x, y, "ell", s, imbric + (next(r) - .5) * 16))
            x += s * 1.5
    return tile, wrap9("\n".join(els), tile)


# --------------------------------------------------------------------- sand ---
def _stipple(tile, n, seed, rmin, rmax):
    """Irregular stipple: random positions and varied grain sizes (not a grid)."""
    r = _rng(seed)
    return "\n".join(
        f'<circle cx="{next(r)*tile:.1f}" cy="{next(r)*tile:.1f}" '
        f'r="{rmin + (rmax-rmin)*next(r):.2f}" fill="#3a3a3a"/>' for _ in range(n))


def sand_massive(tile=44, n=34, seed=4):                   # Sm
    """Massive sand: irregular stipple of varied grain size."""
    return tile, wrap9(_stipple(tile, n, seed, 0.7, 1.7), tile)


def sand_planar_xbed(tile=96, seth=32, seed=1):            # SGp
    """Planar cross-beds that show the process: foresets sweep down-current and
    flatten *tangentially* into the lower bounding surface (grainflow down a
    migrating dune's lee face). All foresets dip the same way -> palaeoflow."""
    els = []
    run = seth * 1.7                       # down-current reach of the sweep
    for y0 in range(0, tile, seth):
        yb = y0 + seth
        els.append(f'<line x1="0" y1="{yb}" x2="{tile}" y2="{yb}" '
                   f'stroke="#222" stroke-width="1.4"/>')
        x = -run
        while x < tile + run:
            # steep at the top, asymptotic (tangential) to the bounding surface
            els.append(f'<path d="M {x:.1f},{y0} C {x-0.18*run:.1f},{y0+0.45*seth:.1f} '
                       f'{x-run+0.30*run:.1f},{yb:.1f} {x-run:.1f},{yb:.1f}" '
                       f'fill="none" stroke="#6a6a6a" stroke-width="0.9"/>')
            x += 8                         # divides tile -> seamless across sets
    return tile, f'<g clip-path="url(#clip{tile})">' + "\n".join(els) + "</g>"


def sand_trough_xbed(tile=96, seth=32, seed=2):            # SGt (festoon)
    """Trough cross-beds: scoop-shaped erosional sets filled with nested,
    asymmetric foresets that climb out down-current - the signature of 3-D
    (sinuous-crested) dunes migrating and scouring."""
    els = []
    span = tile // 2                       # trough width (divides tile)
    for si, y0 in enumerate(range(0, tile, seth)):
        off = (si % 2) * (span // 2)       # stagger troughs between cosets
        yb = y0 + seth
        # concave-up scour surface at the base of the coset
        for c in range(-1, 4):
            cx = c * span + off
            els.append(f'<path d="M {cx-span/2:.1f},{y0} Q {cx:.1f},{yb+3:.1f} '
                       f'{cx+span/2:.1f},{y0}" fill="none" stroke="#222" stroke-width="1.2"/>')
            # nested foresets, asymmetric (steep down-current limb) = migration
            for k in range(1, 6):
                f = k / 6.0
                rx = (span / 2) * (1 - 0.12 * k)
                depth = (seth) * (1 - f) + 2
                els.append(f'<path d="M {cx-rx:.1f},{y0+seth*0.12*k:.1f} '
                           f'Q {cx+rx*0.35:.1f},{y0+depth:.1f} '
                           f'{cx+rx:.1f},{y0+seth*0.05*k:.1f}" '
                           f'fill="none" stroke="#6a6a6a" stroke-width="0.75"/>')
    return tile, f'<g clip-path="url(#clip{tile})">' + "\n".join(els) + "</g>"


def sand_ripple(tile=48, seed=6):                          # Sr (climbing ripples)
    """Climbing-ripple lamination: asymmetric ripples (gentle stoss, steep lee)
    with foresets dipping down-current, each train stepping up-current as it
    climbs - records simultaneous migration and rapid aggradation."""
    els = []
    wl = 16                                # ripple wavelength (divides tile)
    for row, y0 in enumerate(range(4, tile, 9)):
        climb = (row * 5) % wl             # up-current step per set = climbing
        for cx in range(-wl + climb, tile + wl, wl):
            # asymmetric crest: gentle stoss (left), steep lee (right)
            els.append(f'<path d="M {cx},{y0+7} C {cx+wl*0.55:.1f},{y0+5:.1f} '
                       f'{cx+wl*0.7:.1f},{y0-1:.1f} {cx+wl*0.82:.1f},{y0:.1f}" '
                       f'fill="none" stroke="#3f3f3f" stroke-width="1.0"/>')
            # lee-side foresets, dipping down-current (tangential at base)
            for j in range(1, 4):
                fx = cx + wl * (0.55 + 0.08 * j)
                els.append(f'<path d="M {fx:.1f},{y0} Q {fx-2:.1f},{y0+5:.1f} '
                           f'{fx-5:.1f},{y0+7:.1f}" fill="none" stroke="#8a8a8a" '
                           f'stroke-width="0.55"/>')
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


def mud_massive(tile=54, seed=8):                          # Fm (structureless mud)
    """Structureless silt & clay: near-blank with a few scattered silt flecks."""
    return tile, wrap9(_stipple(tile, 9, seed, 0.6, 1.0), tile)


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
def sand_laminated(tile=48, seed=15):                      # Sh (plane beds)
    """Horizontally laminated sand (upper-stage plane beds): near-parallel
    laminae with slight, hand-drawn waviness and uneven thickness."""
    els = [_wavy_polyline(y, tile, _wiggle(seed + y, tile, 0.5), "#666", 0.8)
           for y in range(4, tile, 6)]
    return tile, "\n".join(els)


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
