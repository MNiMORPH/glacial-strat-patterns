"""Lithology fills + structure overlays.

Demonstrates the two-class model: lithologies (till, gravel, sand, mud, peat)
are *fills*; sedimentary structures (cross-bedding, climbing ripples, folds)
are drawn *over* a lithology as bands that need not fill the interval. Placed
features (dropstones, pebble lag) sit on top. Run:

    python examples/example_structures.py
"""
import matplotlib.pyplot as plt

from glacial_patterns import mpl, structures as st

X0, X1 = 0, 1
fig, ax = plt.subplots(figsize=(3.6, 7.5))

# --- lithology fills ---
mpl.column_fill(ax, "Dmm", X0, X1, 10.0, 6.8, tile_width=0.5)   # till
mpl.column_fill(ax, "Gh",  X0, X1, 6.8, 6.0, tile_width=0.5)    # gravel
mpl.column_fill(ax, "Sm",  X0, X1, 6.0, 3.4, tile_width=0.5)    # sand
mpl.column_fill(ax, "Fl",  X0, X1, 3.4, 1.6, tile_width=0.5)    # varves
mpl.column_fill(ax, "Fm",  X0, X1, 1.6, 0.6, tile_width=0.5)    # mud
mpl.column_fill(ax, "P",   X0, X1, 0.6, 0.0, tile_width=0.5)    # peat

# --- structure overlays (a different class; drawn over the lithology) ---
st.cross_bedding(ax, X0, X1, 6.0, 4.6, nsets=2)                 # big cross-beds
st.climbing_ripples(ax, X0, X1, 4.6, 3.4)                       # climbing ripples
st.folds(ax, X0, X1, 2.7, 2.1)                                  # deformed band (partial)

# --- placed features ---
mpl.dropstone(ax, 0.5, 3.0, 0.10)
mpl.dropstone(ax, 0.35, 1.9, 0.08)
mpl.pebble_lag(ax, 6.8, X0, X1, imbricate=True)

for text, y in [("till (Dmm)", 8.4), ("gravel (Gh) + lag", 6.4),
                ("cross-bedded sand", 5.3), ("climbing ripples", 4.0),
                ("varves + dropstones\n+ deformed band", 2.5),
                ("mud (Fm)", 1.1), ("peat (P)", 0.3)]:
    ax.text(1.1, y, text, va="center", fontsize=8.5)

ax.set_xlim(0, 1)
ax.set_ylim(10, 0)
ax.set_xticks([])
ax.set_ylabel("depth (m)")
ax.set_title("Lithology fills + structure overlays", fontsize=11)
fig.tight_layout()
fig.savefig("examples/example_structures.png", dpi=150, bbox_inches="tight")
print("wrote examples/example_structures.png")
