"""Worked example: a small glacial stratigraphic column.

A classic deglacial succession (base to top): subglacial till -> ice-contact
gravel -> glaciofluvial cross-bedded sand -> glaciolacustrine varves with
dropstones -> loess -> peat. Run::

    python examples/example_column.py
"""
import matplotlib.pyplot as plt

from glacial_patterns import mpl, resolve

# (facies key, top depth, bottom depth) in metres, base of section at bottom
UNITS = [
    ("Dmm", 8.0, 6.2),   # subglacial till
    ("Gh",  6.2, 5.3),   # ice-contact gravel
    ("SGt", 5.3, 4.0),   # outwash, trough cross-bedded
    ("SGp", 4.0, 3.2),   # outwash, planar cross-bedded
    ("Fl",  3.2, 1.6),   # glaciolacustrine varves
    ("Em",  1.6, 0.6),   # loess
    ("P",   0.6, 0.0),   # peat
]

fig, ax = plt.subplots(figsize=(3.4, 7))
for code, top, bot in UNITS:
    mpl.column_fill(ax, code, 0, 1, top, bot, tile_width=0.5)
    ax.text(1.12, (top + bot) / 2, f"{code}  {resolve(code)['alias']}",
            va="center", fontsize=9)

# ice-rafted dropstones in the varved interval
mpl.dropstone(ax, 0.42, 2.7, 0.11)
mpl.dropstone(ax, 0.66, 2.1, 0.08)

ax.set_xlim(0, 1)
ax.set_ylim(8, 0)                       # depth increases downward
ax.set_xticks([])
ax.set_ylabel("depth (m)")
ax.set_title("Deglacial succession", fontsize=11)
fig.tight_layout()
fig.savefig("examples/example_column.png", dpi=150, bbox_inches="tight")
print("wrote examples/example_column.png")
