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

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SVG_DIR = os.path.join(ROOT, "svg")
PNG_DIR = os.path.join(ROOT, "png")
META_DIR = os.path.join(ROOT, "metadata")


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
                         svg=f"svg/{code}.svg", png=f"png/{code}.png"))
    json.dump(rows, open(os.path.join(META_DIR, "facies.json"), "w"), indent=1)
    with open(os.path.join(META_DIR, "facies.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["code", "alias", "group", "description",
                                          "svg", "png"])
        w.writeheader()
        w.writerows(rows)
    contact_sheet(rows)
    print(f"built {len(rows)} facies -> svg/, png/, metadata/")


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


if __name__ == "__main__":
    build()
