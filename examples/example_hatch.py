"""Vector-hatch version of the deglacial column (see example_column.py).

Uses matplotlib hatches instead of raster tiles - sharp at any zoom, small
vector PDF/SVG output. Hatches are approximate; the raster tiles are faithful.
Run: ``python examples/example_hatch.py``
"""
import matplotlib.pyplot as plt

from glacial_patterns import resolve
from glacial_patterns.hatch import column_fill_hatch

UNITS = [
    ("Dmm", 8.0, 6.2), ("Gh", 6.2, 5.3), ("SGt", 5.3, 4.0), ("SGp", 4.0, 3.2),
    ("Fl", 3.2, 1.6), ("Em", 1.6, 0.6), ("P", 0.6, 0.0),
]

fig, ax = plt.subplots(figsize=(3.4, 7))
for code, top, bot in UNITS:
    column_fill_hatch(ax, code, 0, 1, top, bot)
    ax.text(1.12, (top + bot) / 2, f"{code}  {resolve(code)['alias']}",
            va="center", fontsize=9)

ax.set_xlim(0, 1)
ax.set_ylim(8, 0)
ax.set_xticks([])
ax.set_ylabel("depth (m)")
ax.set_title("Deglacial succession (vector hatch)", fontsize=11)
fig.tight_layout()
fig.savefig("examples/example_hatch.png", dpi=150, bbox_inches="tight")
# also a true-vector PDF, to show the point of the hatch export
fig.savefig("examples/example_hatch.pdf", bbox_inches="tight")
print("wrote examples/example_hatch.png and .pdf")
