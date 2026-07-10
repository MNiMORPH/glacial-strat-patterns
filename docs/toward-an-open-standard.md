# Toward an open standard for glacial & Quaternary strat-column ornaments

*A call for collaboration.* This note invites glacial sedimentologists,
Quaternary geologists, and geological mappers to help turn this pattern library
into a **community-reviewed, citable set of stratigraphic-column ornaments** for
glacial and Quaternary sediments.

> **Status: provisional.** The current patterns were drafted by reading the
> published measured-section literature and the USGS/FGDC standard, with expert
> feedback from one glacial geomorphologist. They are a *starting point*, not an
> agreed standard. Every form is open to correction.

## Why this is worth doing

Stratigraphic columns are how we record and communicate glacial and Quaternary
successions, yet there is **no open, community-endorsed ornament set** designed
for them. The most complete open standard — the U.S. FGDC *Digital Cartographic
Standard for Geologic Map Symbolization* (FGDC-STD-013-2006) — is excellent for
bedrock and general lithology but **thin and generic for glacial/Quaternary
facies**: diamictons, rhythmites with dropstones, glaciotectonites,
ice-contact/collapse structures, and the like. In practice everyone redraws
these by hand, inconsistently, in each figure and thesis.

A shared, open, well-designed set would:

- make measured sections **consistent and comparable** across workers, papers,
  and regions;
- lower the barrier for students and mappers (drop-in SVG / matplotlib /
  Inkscape / QGIS assets);
- give the community a **citable** reference so figures can point to a source;
- encode **process and form** (foreset dip, imbrication, fold style) rather than
  arbitrary texture, so an ornament *teaches* what it records.

## What we are asking for

We would value help from people who log and draw glacial sections:

1. **Review the ornaments** against how you and your subfield actually draw them
   (see the open questions below). Tell us what is wrong, missing, or non-standard.
2. **Contribute reference legends** from published or in-house measured-section
   keys, so forms are anchored in practice rather than invented.
3. **Propose facies and structures** we lack (e.g. glaciomarine diamict,
   subaqueous outwash, dropstone-rich mud, boulder pavements, till fabric).
4. **Help converge on canonical forms** — where conventions differ between
   subfields (e.g. till types, diamict facies codes), help decide what the
   default should be and what should be an option.

## Toward "official"

A realistic path from *provisional library* to *community standard*:

1. **Iterate against the literature and expert review** (this stage) — refine
   each ornament until practitioners recognise it.
2. **Convene a small working group** of glacial sedimentologists / Quaternary
   mappers to agree a core set and a facies-code scheme, building on established
   frameworks (Eyles, Eyles & Miall 1983 lithofacies codes; Evans & Benn,
   *A Practical Guide to the Study of Glacial Sediments*; Miall architectural
   elements) and aligning with FGDC lithologic patterns where they connect.
3. **Publish** the set as a citable, versioned resource — e.g. a data/methods
   note or journal supplement with a DOI — and keep the repository as the living
   reference implementation.
4. **Seek endorsement / alignment** with relevant bodies as appropriate
   (e.g. INQUA, GSA/USGS map-symbol efforts, national surveys), if the community
   wants it.

*(Venue, timing, and whether to pursue formal endorsement are open — see
"Decisions for the maintainers" below.)*

## Where expert input is most needed now

Concrete, per-ornament questions where practice may diverge from our current draft:

- **Diamictons (Dmm / Dms / Dcm).** Is scattered-clast-in-matrix the right base?
  Should subglacial (lodgement/deformation), melt-out, flow, and glaciomarine
  diamicts have *distinct* ornaments, or one ornament plus annotation?
- **Gravel imbrication.** We draw a-axes dipping up-current; confirm the sense
  and whether imbrication should be a fill fabric, a discrete symbol, or both.
- **Ripple & cross-lamination.** Foreset/lee dip is drawn down-current
  (left-to-right flow). Confirm the current-ripple, climbing-ripple, and
  wave-ripple forms match convention.
- **Rhythmites vs. mud.** Varve couplets vs. massive mud (broken-dash) — are the
  distinctions and forms right? How should dropstones-in-rhythmite be shown?
- **Deformation.** Convolute/recumbent folds and ice-contact collapse are drawn
  as *overlays* over a lithology (a deformed band). Confirm fold style and
  whether glaciotectonite deserves its own treatment.
- **Scale & grain size.** Should column width encode grain size (a clay→boulder
  axis), as many logs do? What default grain-size scale?
- **Colour.** The set is black line-work by design (works in any medium). Is a
  standard colour scheme wanted, and should it follow a specific source?

## How to contribute

- Open a **GitHub issue** with a sketch, photo, or reference-legend scan, and a
  note on the subfield/region it reflects.
- Or open a **pull request** against the generators
  (`glacial_patterns/patterns.py`, `glacial_patterns/structures.py`).
- Reference legends and section photos are especially welcome — forms grounded
  in published practice carry the most weight.

Contributors are credited. Pattern assets are CC-BY-4.0 and code is MIT (see
`LICENSE` / `LICENSE-patterns.md`); provenance to source standards and legends is
preserved.

## Decisions for the maintainers (to fill in)

- **Lead / point of contact:** _<name, affiliation, email>_
- **Target venue for a citable release:** _<e.g. journal data note, Zenodo DOI>_
- **Working-group members to invite:** _<names / labs>_
- **Whether to pursue formal endorsement**, and with which body.
- **Governance:** how proposals are reviewed and decisions recorded.

---

*Maintained at <https://github.com/MNiMORPH/glacial-strat-patterns>. This note is
a draft; comments and corrections are welcome via GitHub issues.*
