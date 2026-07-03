"""glacial-strat-patterns: tileable fill patterns for glacial/Quaternary
stratigraphic columns.

SVG is the source of truth; :func:`glacial_patterns.build.build` renders SVG +
PNG tiles from the parametric generators in :mod:`glacial_patterns.patterns`,
catalogued in :mod:`glacial_patterns.catalog`. See :mod:`glacial_patterns.mpl`
for a matplotlib column-fill helper.
"""
from .catalog import FACIES, BY_CODE, resolve  # noqa: F401

__all__ = ["FACIES", "BY_CODE", "resolve"]
__version__ = "0.1.0"
