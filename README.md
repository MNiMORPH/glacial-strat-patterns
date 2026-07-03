# glacial-strat-patterns

**Tileable fill patterns for glacial / Quaternary stratigraphic columns** — the
kind of black line-work you pour into a measured section, but with a real
glacial vocabulary that the USGS/FGDC lithologic set lacks: diamicton/till
families, rhythmites, **dropstones that deflect the laminae**, cross-bedded
outwash, loess, peat.

SVG is the source of truth; the patterns are generated parametrically, tile
seamlessly, and come with a one-call **matplotlib** helper for drawing columns
in Python.

![contact sheet](contact_sheet.png)

## Why this exists

The FGDC patterns (Dave Quinn's `geologic-patterns` repackages them) are the de
facto open set, but their glacial/Quaternary coverage is thin and generic. This
library fills that gap: patterns designed for glacial sedimentology, keyed to
**Eyles/Miall-style lithofacies codes** (`Dmm`, `Dms`, `Sr`, `Fl`, …) with
plain-name aliases, and **parametric** so a facies is a family you tune (clast
density, lamina spacing, stipple density) rather than one frozen tile.

## Facies (18)

| Code | Alias | Group | |
|------|-------|-------|--|
| `Dmm` | till (massive) | diamicton | matrix-supported, massive — lodgement/subglacial till |
| `Dms` | stratified diamicton | diamicton | matrix-supported, stratified — melt-out / waterlain |
| `Dcm` | clast-rich diamicton | diamicton | clast-supported, massive |
| `Gh` | gravel | glaciofluvial | clast-supported, horizontally bedded |
| `Gms` | matrix-supported gravel | glaciofluvial | debris-flow / ice-marginal diamict |
| `SGp` | planar cross-beds | glaciofluvial | sand & gravel, planar foresets |
| `SGt` | trough cross-beds | glaciofluvial | sand & gravel, festoon sets |
| `Sr` | ripple lamination | glaciofluvial | climbing-ripple cross-lamination |
| `Sh` | laminated sand | glaciofluvial | horizontal plane beds |
| `Sm` | massive sand | glaciofluvial | massive / faintly graded |
| `Fl` | rhythmite / varve | glaciolacustrine | laminated silt & clay couplets |
| `Fm` | massive mud | glaciolacustrine | structureless silt & clay |
| `Cdm` | colluvium (soliflucted) | colluvial | diamict; clasts aligned down-slope |
| `Fd` | deformed / folded | deformation | glaciotectonite / soft-sediment folds |
| `SGc` | ice-contact (collapsed) | deformation | bedded sand faulted into grabens |
| `Em` | loess | eolian | massive eolian silt |
| `P` | peat / organic | organic | bog / fen |
| `R` | bedrock | bedrock | undifferentiated substrate |

### Placed features (not tiles)

Some glacial elements sit *in* the sediment rather than filling an interval, so
they're drawn as placed features over a fill:

- `mpl.dropstone(ax, x, y, r)` — ice-rafted clast deflecting the laminae (use over `Fl`/`Fm`)
- `mpl.boulder_pavement(ax, y, x0, x1)` — a clast line marking a subglacial pavement / lag
- `mpl.erosion_contact(ax, y, x0, x1)` — a scalloped erosional surface

## Quickstart

```bash
pip install -e .        # numpy, matplotlib, pillow
```

```python
import matplotlib.pyplot as plt
from glacial_patterns import mpl

fig, ax = plt.subplots(figsize=(3, 6))
mpl.column_fill(ax, "Dmm", 0, 1, 8, 6)     # till, 8–6 m
mpl.column_fill(ax, "Fl",  0, 1, 3, 1.5)   # varves, 3–1.5 m
mpl.dropstone(ax, 0.5, 2.4, 0.1)           # ice-rafted clast
ax.set_xlim(0, 1); ax.set_ylim(8, 0)       # depth downward
plt.show()
```

You can address a facies by code (`"Dmm"`) or alias (`"till (massive)"`).
A full worked section is in [`examples/example_column.py`](examples/example_column.py):

![example column](examples/example_column.png)

Not using Python? The `svg/<code>.svg` tiles drop straight into Inkscape /
Illustrator / QGIS as pattern fills; `metadata/facies.csv` is the index.

## Regenerating the assets

```bash
python -m glacial_patterns.build      # writes svg/, png/, metadata/, contact_sheet
```

Regeneration needs the `inkscape` CLI (used to rasterise SVG → PNG). Editing a
generator in `glacial_patterns/patterns.py` and rebuilding updates every asset.

## Design notes

- **SVG-native tiling.** Each pattern is an SVG `<pattern>`; discrete ornaments
  are wrapped across tile edges (`wrap9`) so repeats are seamless.
- **Deterministic.** Scatter uses a seeded PRNG, so tiles are reproducible.
- **Codes + aliases.** Lithofacies code is the primary key; a friendly alias
  resolves to the same facies.

## Roadmap

Optional colour variants per facies, a matplotlib hatch export, per-facies
parameter presets, and further ornaments (striated/faceted-clast markers,
till fabric arrows, iceberg-turbate). Contributions of regional facies schemes
welcome.

## Licence

- **Code** (`glacial_patterns/`, `examples/`): MIT (`LICENSE`).
- **Pattern assets** (`svg/`, `png/`): CC-BY-4.0 (`LICENSE-patterns.md`) —
  original designs, informed by the public-domain FGDC standard but not copied
  from it.

See also the sibling repo
[gsc-of8572-swatches](https://github.com/MNiMORPH/gsc-of8572-swatches) for GSC
surficial *map-face* colours — the complement to these column fills.
