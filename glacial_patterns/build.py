"""Build all facies assets from the generators: SVG + PNG tiles, metadata, and
a contact sheet. Run as ``python -m glacial_patterns.build``.

SVG is the source of truth; PNGs are pre-rasterised (via inkscape) so the
matplotlib helper and quick previews need no SVG renderer at fill time.
"""
import csv
import json
import os
import subprocess

from .catalog import FACIES
from .hatch import HATCH

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SVG_DIR = os.path.join(ROOT, "svg")
PNG_DIR = os.path.join(ROOT, "png")
META_DIR = os.path.join(ROOT, "metadata")
INK = "http://www.inkscape.org/namespaces/inkscape"


def pattern_defs(code, fn):
    """Return (tile, <defs> body registering the <pattern> and its clip)."""
    tile, inner = fn()
    clip = (f'<clipPath id="clip{tile}"><rect width="{tile}" height="{tile}"/>'
            f'</clipPath>')
    pat = (f'<pattern id="pat_{code}" patternUnits="userSpaceOnUse" '
           f'width="{tile}" height="{tile}">'
           f'<rect width="{tile}" height="{tile}" fill="white"/>{inner}</pattern>')
    return tile, clip + pat


def swatch_svg(code, fn, px=120):
    """Standalone SVG: a px x px box filled by the tiling pattern."""
    tile, defs = pattern_defs(code, fn)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{px}" height="{px}" '
            f'viewBox="0 0 {px} {px}">\n<defs>{defs}</defs>\n'
            f'<rect width="{px}" height="{px}" fill="url(#pat_{code})" '
            f'stroke="black" stroke-width="1"/>\n</svg>\n')


def rasterize(svg_path, png_path, width=240):
    subprocess.run(["inkscape", svg_path, "-o", png_path, "-w", str(width)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def build(px=120, raster_w=240):
    for d in (SVG_DIR, PNG_DIR, META_DIR):
        os.makedirs(d, exist_ok=True)
    rows = []
    for code, fn, alias, group, desc in FACIES:
        svg = swatch_svg(code, fn, px)
        sp = os.path.join(SVG_DIR, f"{code}.svg")
        pp = os.path.join(PNG_DIR, f"{code}.png")
        open(sp, "w").write(svg)
        rasterize(sp, pp, raster_w)
        rows.append(dict(code=code, alias=alias, group=group, description=desc,
                         hatch=HATCH.get(code, ""),
                         svg=f"svg/{code}.svg", png=f"png/{code}.png"))
    json.dump(rows, open(os.path.join(META_DIR, "facies.json"), "w"), indent=1)
    with open(os.path.join(META_DIR, "facies.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["code", "alias", "group", "description",
                                          "hatch", "svg", "png"])
        w.writeheader()
        w.writerows(rows)
    contact_sheet(rows)
    inkscape_palette(rows)
    explanatory_plate()
    print(f"built {len(rows)} facies -> svg/, png/, metadata/, inkscape/, plate")


def contact_sheet(rows, path=None, ncols=6):
    """Grid of labelled column segments, one per facies."""
    path = path or os.path.join(ROOT, "contact_sheet.svg")
    W, H, gx, gy, top, labh = 120, 170, 20, 16, 12, 42
    cellh = H + labh
    defs, body = [], []
    for i, r in enumerate(rows):
        code = r["code"]
        fn = next(f for c, f, *_ in FACIES if c == code)
        _, d = pattern_defs(code, fn)
        defs.append(d)
        col, row = i % ncols, i // ncols
        x = gx + col * (W + gx)
        y = top + row * (cellh + gy)
        body.append(f'<rect x="{x}" y="{y}" width="{W}" height="{H}" '
                    f'fill="url(#pat_{code})" stroke="black" stroke-width="1.5"/>')
        body.append(f'<text x="{x+W/2}" y="{y+H+18}" text-anchor="middle" '
                    f'font-family="sans-serif" font-size="15" font-weight="bold">{code}</text>')
        body.append(f'<text x="{x+W/2}" y="{y+H+35}" text-anchor="middle" '
                    f'font-family="sans-serif" font-size="11" fill="#444">{r["alias"]}</text>')
    nrows = (len(rows) + ncols - 1) // ncols
    tw = gx + ncols * (W + gx)
    th = top + nrows * (cellh + gy)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{tw}" height="{th}" '
           f'viewBox="0 0 {tw} {th}">\n<defs>{"".join(defs)}</defs>\n'
           f'<rect width="100%" height="100%" fill="white"/>\n' + "\n".join(body) +
           "\n</svg>\n")
    open(path, "w").write(svg)
    rasterize(path, path.replace(".svg", ".png"), min(1800, tw * 2))


def inkscape_palette(rows, path=None, ncols=6):
    """A single SVG of all facies as Inkscape stock <pattern>s plus a visible
    labelled palette. Open it in Inkscape and copy patterns, or drop it in your
    user patterns folder (see the header comment) to get them in Fill & Stroke.
    """
    path = path or os.path.join(ROOT, "inkscape", "glacial-patterns.svg")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tiles, defs, body = set(), [], []
    W, H, gx, gy, top, labh = 96, 118, 20, 30, 54, 34
    cellh = H + labh
    for i, r in enumerate(rows):
        code = r["code"]
        fn = next(f for c, f, *_ in FACIES if c == code)
        tile, inner = fn()
        tiles.add(tile)
        label = f"Glacial: {code} - {r['alias']}"
        defs.append(f'<pattern id="gsp_{code}" inkscape:stockid="{label}" '
                    f'inkscape:isstock="true" inkscape:label="{label}" '
                    f'patternUnits="userSpaceOnUse" width="{tile}" height="{tile}">'
                    f'<rect width="{tile}" height="{tile}" fill="white"/>{inner}</pattern>')
        col, row = i % ncols, i // ncols
        x, y = gx + col * (W + gx), top + row * (cellh + gy)
        body.append(f'<rect x="{x}" y="{y}" width="{W}" height="{H}" '
                    f'fill="url(#gsp_{code})" stroke="black" stroke-width="1.2"/>')
        body.append(f'<text x="{x+W/2}" y="{y+H+17}" text-anchor="middle" '
                    f'font-family="sans-serif" font-size="14" font-weight="bold">{code}</text>')
        body.append(f'<text x="{x+W/2}" y="{y+H+31}" text-anchor="middle" '
                    f'font-family="sans-serif" font-size="10" fill="#444">{r["alias"]}</text>')
    clips = "".join(f'<clipPath id="clip{t}"><rect width="{t}" height="{t}"/></clipPath>'
                    for t in sorted(tiles))
    nrows = (len(rows) + ncols - 1) // ncols
    tw = gx + ncols * (W + gx)
    th = top + nrows * (cellh + gy)
    header = ("<!-- glacial-strat-patterns Inkscape pattern palette.\n"
              "     Use: open in Inkscape and copy a swatch, OR copy this file into\n"
              "     your Inkscape user patterns folder (Edit > Preferences > System >\n"
              "     'User config' -> ../patterns/) so the fills appear as stock\n"
              "     patterns in Object > Fill and Stroke > Pattern. CC-BY-4.0. -->\n")
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" '
           f'xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:inkscape="{INK}" '
           f'width="{tw}" height="{th}" viewBox="0 0 {tw} {th}">\n{header}'
           f'<defs>{clips}{"".join(defs)}</defs>\n'
           f'<rect width="100%" height="100%" fill="white"/>\n'
           f'<text x="{gx}" y="30" font-family="sans-serif" font-size="20" '
           f'font-weight="bold">Glacial / Quaternary strat-column patterns</text>\n'
           + "\n".join(body) + "\n</svg>\n")
    open(path, "w").write(svg)
    rasterize(path, path.replace(".svg", ".png"), min(1800, tw * 2))


# process annotations: (code, title, caption, arrow) where arrow is one of
# 'flow-left' 'flow-right' 'climb' 'settle' 'fabric' or None. Kept geologically
# honest - foreset/ripple dip = transport; imbricate a-axes dip up-current.
# caption lines separated by '|' (each rendered on its own row)
EXPLAIN = [
    ("Gh",  "Imbrication",       "disc clasts tilted;|a-axes dip up-current", "fabric"),
    ("SGp", "Planar cross-beds", "foresets dip down-current,|tangential to the base", "flow-left"),
    ("SGt", "Trough cross-beds", "festoon scours:|migrating 3-D dunes", "flow-right"),
    ("Sr",  "Climbing ripples",  "migrate + aggrade;|ripples climb up-current", "climb"),
    ("Fl",  "Rhythmites",        "graded seasonal couplets;|suspension settling", "settle"),
    ("Dmm", "Massive till",      "poorly sorted, matrix-supported;|no sorting, no fabric", None),
]

_ARROW = {                                 # (x1,y1,x2,y2) in a 0..W,0..H panel
    "flow-left":  lambda W, H: (W * 0.72, H * 0.30, W * 0.28, H * 0.60),
    "flow-right": lambda W, H: (W * 0.28, H * 0.30, W * 0.72, H * 0.40),
    "climb":      lambda W, H: (W * 0.30, H * 0.74, W * 0.66, H * 0.28),
    "settle":     lambda W, H: (W * 0.50, H * 0.22, W * 0.50, H * 0.74),
    "fabric":     lambda W, H: (W * 0.30, H * 0.60, W * 0.70, H * 0.40),
}


def explanatory_plate(rows_unused=None, path=None, ncols=3):
    """A teaching plate: key facies with a process arrow and a caption, showing
    what each ornament records. Highlights the pattern-and-process design."""
    path = path or os.path.join(ROOT, "explanatory_plate.svg")
    W, H, gx, gy, top, caph = 210, 150, 26, 66, 60, 46
    cellh = H + caph
    tiles, defs, body = set(), [], []
    defs.append('<marker id="ah" markerWidth="9" markerHeight="9" refX="7" refY="3" '
                'orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#b5271f"/></marker>')
    for i, (code, title, caption, arrow) in enumerate(EXPLAIN):
        fn = next(f for c, f, *_ in FACIES if c == code)
        tile, d = pattern_defs(code, fn)
        tiles.add(tile)
        defs.append(d)
        col, row = i % ncols, i // ncols
        x, y = gx + col * (W + gx), top + row * (cellh + gy)
        body.append(f'<rect x="{x}" y="{y}" width="{W}" height="{H}" '
                    f'fill="url(#pat_{code})" stroke="black" stroke-width="1.5"/>')
        if arrow:
            ax1, ay1, ax2, ay2 = _ARROW[arrow](W, H)
            body.append(f'<line x1="{x+ax1:.0f}" y1="{y+ay1:.0f}" x2="{x+ax2:.0f}" '
                        f'y2="{y+ay2:.0f}" stroke="#b5271f" stroke-width="3.2" '
                        f'marker-end="url(#ah)" opacity="0.9"/>')
        body.append(f'<text x="{x}" y="{y+H+20}" font-family="sans-serif" '
                    f'font-size="15" font-weight="bold">{code} · {title}</text>')
        for li, line in enumerate(caption.split("|")):
            body.append(f'<text x="{x}" y="{y+H+37+li*15}" font-family="sans-serif" '
                        f'font-size="11.5" fill="#333">{line}</text>')
    clips = "".join(f'<clipPath id="clip{t}"><rect width="{t}" height="{t}"/></clipPath>'
                    for t in sorted(tiles))
    nrows = (len(EXPLAIN) + ncols - 1) // ncols
    tw = gx + ncols * (W + gx)
    th = top + nrows * (cellh + gy)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{tw}" height="{th}" '
           f'viewBox="0 0 {tw} {th}">\n<defs>{clips}{"".join(defs)}</defs>\n'
           f'<rect width="100%" height="100%" fill="white"/>\n'
           f'<text x="{gx}" y="34" font-family="sans-serif" font-size="20" '
           f'font-weight="bold">Reading the ornament: pattern and process</text>\n'
           f'<text x="{gx}" y="52" font-family="sans-serif" font-size="12" '
           f'fill="#b5271f">red arrows show the process direction the strokes record</text>\n'
           + "\n".join(body) + "\n</svg>\n")
    open(path, "w").write(svg)
    rasterize(path, path.replace(".svg", ".png"), min(1600, tw * 2))


if __name__ == "__main__":
    build()
