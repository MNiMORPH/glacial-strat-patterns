"""Facies catalog: Eyles/Miall-style lithofacies codes with plain-name aliases.

Each entry maps a code to its generator in :mod:`patterns`, a friendly alias,
a depositional group, and a short description. This is the single source of
truth consumed by the builder, the matplotlib helper, and the metadata export.
"""
from . import patterns as P

FACIES = [
    # code    generator                 alias                     group             description
    ("Dmm", P.diamicton_massive,      "till (massive)",          "diamicton",
     "Diamicton, matrix-supported, massive - subglacial/lodgement till"),
    ("Dms", P.diamicton_stratified,   "stratified diamicton",    "diamicton",
     "Diamicton, matrix-supported, stratified - melt-out / waterlain till"),
    ("Dcm", P.diamicton_clast,        "clast-rich diamicton",    "diamicton",
     "Diamicton, clast-supported, massive - winnowed / coarse till"),
    ("Gh",  P.gravel_clast,           "gravel",                  "glaciofluvial",
     "Gravel, clast-supported, horizontally bedded - outwash / channel lag"),
    ("Sr",  P.sand_ripple,            "ripple-laminated sand",   "glaciofluvial",
     "Sand, ripple / climbing-ripple cross-laminated - waning flow"),
    ("Sm",  P.sand_massive,           "massive sand",            "glaciofluvial",
     "Sand, massive or faintly graded"),
    ("Gms", P.gravel_matrix,          "matrix-supported gravel", "glaciofluvial",
     "Gravel, matrix-supported - debris-flow / ice-marginal diamict"),
    ("Cdm", P.colluvium,              "colluvium (soliflucted)", "colluvial",
     "Soliflucted colluvial diamict - clasts aligned down-slope"),
    ("Fl",  P.rhythmite,              "rhythmite / varve",       "glaciolacustrine",
     "Laminated silt & clay rhythmites (varves) - distal glaciolacustrine"),
    ("Fm",  P.mud_massive,            "massive mud",             "glaciolacustrine",
     "Massive silt & clay - suspension settling; hosts dropstones"),
    ("Em",  P.loess,                  "loess",                   "eolian",
     "Massive eolian silt (loess)"),
    ("P",   P.peat,                   "peat / organic",          "organic",
     "Peat and organic-rich mud - bog / fen"),
    ("R",   P.bedrock,                "bedrock",                 "bedrock",
     "Undifferentiated bedrock / substrate"),
]

# What each facies *records* - the depositional process its ornament encodes.
# Machine-readable companion to the explanatory plate.
PROCESS = {
    "Dmm": "subglacial deposition; poorly sorted, no fabric",
    "Dms": "melt-out / waterlain till; weak sub-horizontal fabric",
    "Dcm": "winnowed or coarse subglacial / debris deposit",
    "Gh":  "bed-load gravel; imbrication records palaeoflow",
    "Gms": "en-masse debris flow; unsorted",
    "Sr":  "ripple migration with aggradation (climbing)",
    "Sm":  "rapid deposition or bioturbation; structureless",
    "Fl":  "seasonal suspension settling (varves)",
    "Fm":  "quiet-water suspension settling",
    "Cdm": "slope creep / solifluction; down-slope fabric",
    "Em":  "eolian silt fallout (loess)",
    "P":   "in-situ organic accumulation (bog / fen)",
    "R":   "substrate / basement",
}

BY_CODE = {c: dict(code=c, fn=fn, alias=al, group=g, description=d,
                   process=PROCESS.get(c, ""))
           for c, fn, al, g, d in FACIES}

ALIAS_TO_CODE = {al: c for c, fn, al, g, d in FACIES}


def resolve(key):
    """Look up a facies by code or by alias."""
    if key in BY_CODE:
        return BY_CODE[key]
    if key in ALIAS_TO_CODE:
        return BY_CODE[ALIAS_TO_CODE[key]]
    raise KeyError(f"unknown facies {key!r}; known codes: {list(BY_CODE)}")
