"""Worked example: a small glacial stratigraphic column.

A classic deglacial succession (base to top): subglacial till -> ice-contact
gravel -> glaciofluvial sand (with cross-bed structures) -> glaciolacustrine
varves with dropstones -> loess -> peat. Shows the two-class model: lithology
*fills* with sedimentary-structure *overlays*. Run::

    python examples/example_column.py
"""
import matplotlib.pyplot as plt

from glacial_patterns import mpl, structures as st, resolve

# (lithology fill key, top depth, bottom depth) in metres
UNITS = [
    ("Dmm", 8.0, 6.2),   # subglacial till
    ("Gh",  6.2, 5.3),   # ice-contact gravel
    ("Sm",  5.3, 3.2),   # glaciofluvial sand (structures overlaid below)
    ("Fl",  3.2, 1.6),   # glaciolacustrine varves
    ("Em",  1.6, 0.6),   # loess
    ("P",   0.6, 0.0),   # peat
]
LABELS = {"Dmm": 7.1, "Gh": 5.75, "Sm": 4.25, "Fl": 2.4, "Em": 1.1, "P": 0.3}

fig, ax = plt.subplots(figsize=(3.4, 7))
for code, top, bot in UNITS:
    mpl.column_fill(ax, code, 0, 1, top, bot, tile_width=0.5)
    ax.text(1.12, LABELS[code], f"{code}  {resolve(code)['alias']}",
            va="center", fontsize=9)

# structure overlays on the sand (a different class, drawn over the lithology)
st.trough_cross_bedding(ax, 0, 1, 5.3, 4.2)   # lower outwash: trough cross-beds
st.cross_bedding(ax, 0, 1, 4.2, 3.2)          # upper outwash: planar cross-beds

# placed features: a subglacial boulder pavement capping the till, an
# erosional contact at the base of the lake beds, and ice-rafted dropstones
mpl.boulder_pavement(ax, 6.2, 0, 1)
mpl.erosion_contact(ax, 3.2, 0, 1)
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
