"""Configuration objects for the future public LocusBlend API.

Models only the settings that the pipeline (``variants``, ``ld``, ``genes``,
``plotting``, ``compare``, ``export``) actually consumes, plus the string
constants that identify modes, LD sources, index-selection methods, gene display
modes and compare modes.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional, Tuple

from .reference import (
    DEFAULT_1000G_ANCESTRY,
    normalize_1000g_ancestry,
)

# --------------------------------------------------------------------------
# Visualization modes.
# --------------------------------------------------------------------------
MODE_STANDARD = "Standard locus zoom"
MODE_TWO_INDEX = "Two-index LocusBlend"
MODE_THREE_INDEX = "Three-index LocusBlend"
LOCUSBLEND_MODES = (MODE_STANDARD, MODE_TWO_INDEX, MODE_THREE_INDEX)
DEFAULT_MODE = MODE_THREE_INDEX

# Public API mode values -> full mode names used internally.
PUBLIC_MODE_STANDARD = "standard"
PUBLIC_MODE_TWO = "two"
PUBLIC_MODE_THREE = "three"
PUBLIC_MODE_MAP = {
    PUBLIC_MODE_STANDARD: MODE_STANDARD,
    PUBLIC_MODE_TWO: MODE_TWO_INDEX,
    PUBLIC_MODE_THREE: MODE_THREE_INDEX,
}

# --------------------------------------------------------------------------
# LD source options
# --------------------------------------------------------------------------
LD_SOURCE_1000G = "Use 1000G reference"
LD_SOURCE_UPLOADED_MATRIX = "Upload LD matrix"
LD_SOURCE_UPLOADED_LONG = "Upload LD long table"
LD_SOURCE_OPTIONS = (
    LD_SOURCE_1000G,
    LD_SOURCE_UPLOADED_MATRIX,
    LD_SOURCE_UPLOADED_LONG,
)

# --------------------------------------------------------------------------
# Index selection methods
# --------------------------------------------------------------------------
INDEX_SELECTION_MANUAL = "Manual input"
INDEX_SELECTION_AUTO_TOP = "Auto-select by LD clumping from dataset 1 (top)"
INDEX_SELECTION_AUTO_BOTTOM = "Auto-select by LD clumping from dataset 2 (bottom)"
INDEX_SELECTION_METHODS = (
    INDEX_SELECTION_MANUAL,
    INDEX_SELECTION_AUTO_TOP,
    INDEX_SELECTION_AUTO_BOTTOM,
)

# Auto-index source codes used by the package API (the labels above are the
# UI strings; these are the values stored in LocusBlendConfig).
AUTO_INDEX_SOURCE_TOP = "top"
AUTO_INDEX_SOURCE_BOTTOM = "bottom"

# Public API auto-index source values.
AUTO_INDEX_SOURCE_DATASET1 = "dataset1"
AUTO_INDEX_SOURCE_DATASET2 = "dataset2"
AUTO_INDEX_SOURCE_VALUES = (AUTO_INDEX_SOURCE_DATASET1, AUTO_INDEX_SOURCE_DATASET2)

# --------------------------------------------------------------------------
# Gene display modes (genes.load_genes_from_gtf / genes.load_genes_from_table)
# --------------------------------------------------------------------------
GENE_DISPLAY_PROTEIN_CODING = "protein_coding"
GENE_DISPLAY_ALL = "all"
GENE_DISPLAY_MODES = (GENE_DISPLAY_PROTEIN_CODING, GENE_DISPLAY_ALL)

# --------------------------------------------------------------------------
# Locus compare modes
# --------------------------------------------------------------------------
COMPARE_MODE_SEPARATE = "Three separate compare plots"
COMPARE_MODE_SINGLE_BLENDED = "Single blended compare plot"
COMPARE_MODES = (COMPARE_MODE_SEPARATE, COMPARE_MODE_SINGLE_BLENDED)

# --------------------------------------------------------------------------
# Defaults for a run.
# --------------------------------------------------------------------------
DEFAULT_CHROMOSOME = "14"
DEFAULT_CENTER_BP = 73238768
DEFAULT_WINDOW_KB = 500
DEFAULT_CLUMP_R2 = 0.01
DEFAULT_GENE_TRACK_GAP = 30000
# Display defaults for the combined locus figure. Not exposed as public API
# arguments.
DEFAULT_COMBINED_HEIGHT = 980
DEFAULT_VERTICAL_SPACING = 0.04
DEFAULT_RECOMB_MAX = 100
DEFAULT_COMPARE_SIZE = 560
# Defaults for the y-axis recommendation helper.
DEFAULT_MIN_YLIM = 7.0
DEFAULT_YLIM_PAD_FRAC = 0.12


def normalize_public_mode(value):
    """Map a public API mode value to the full mode name.

    ``"standard"`` / ``"two"`` / ``"three"`` map exactly to
    ``"Standard locus zoom"`` / ``"Two-index LocusBlend"`` /
    ``"Three-index LocusBlend"``. Anything else raises ``ValueError``.
    """
    key = str(value or "").strip().lower()
    if key not in PUBLIC_MODE_MAP:
        raise ValueError(
            f"Unsupported mode {value!r}. Use one of: "
            + ", ".join(repr(k) for k in PUBLIC_MODE_MAP)
            + "."
        )
    return PUBLIC_MODE_MAP[key]


def normalize_auto_index_source(value):
    """Return ``"dataset1"`` or ``"dataset2"``; anything else raises ValueError."""
    key = str(value or "").strip().lower()
    if key not in AUTO_INDEX_SOURCE_VALUES:
        raise ValueError(
            f"Unsupported auto_index_source {value!r}. Use one of: "
            + ", ".join(repr(v) for v in AUTO_INDEX_SOURCE_VALUES)
            + "."
        )
    return key


def get_required_n_indices(active_mode):
    """Return the number of index variants required by the active mode."""
    if active_mode == "Standard locus zoom":
        return 1
    if active_mode == "Two-index LocusBlend":
        return 2
    return 3


def parse_highlighted_genes(value):
    r"""Split highlighted-gene input into the set of lower-cased names.

    Strings are split on commas, semicolons and whitespace::

        {g.strip().lower() for g in re.split(r"[,;\s]+", raw) if g.strip()}

    which is the form ``genes.add_gene_track_to_subplot`` matches against.
    Iterables of gene names are accepted as well (each name is stripped and
    lower-cased); matching stays case-insensitive.
    """
    if value is None:
        return set()
    if isinstance(value, str):
        return {g.strip().lower() for g in re.split(r"[,;\s]+", value) if g.strip()}
    try:
        items = list(value)
    except TypeError:
        items = [value]
    return {str(g).strip().lower() for g in items if str(g).strip()}


@dataclass
class LocusBlendConfig:
    """Settings for a single LocusBlend run.

    Only the settings that the pipeline consumes are modelled; the public API
    entry point (``locusblend.plot``) fills the display defaults from the module
    constants above.
    """

    mode: str = DEFAULT_MODE
    ancestry: str = DEFAULT_1000G_ANCESTRY
    chromosome: Optional[str] = None
    center_bp: Optional[int] = None
    window_kb: float = DEFAULT_WINDOW_KB
    index_variants: Tuple[str, ...] = ()
    index_selection_method: str = INDEX_SELECTION_MANUAL
    auto_index_source: Optional[str] = None
    clump_r2: float = DEFAULT_CLUMP_R2
    ld_source: str = LD_SOURCE_1000G
    gene_display_mode: str = GENE_DISPLAY_PROTEIN_CODING
    highlighted_genes: str = ""
    show_recombination: bool = True
    title_top: str = ""
    title_bottom: str = ""

    def __post_init__(self):
        # Normalize the ancestry code once, at construction time.
        self.ancestry = normalize_1000g_ancestry(self.ancestry)
        self.index_variants = tuple(str(v) for v in (self.index_variants or ()))

    @property
    def required_n_indices(self) -> int:
        """Number of index variants required by ``mode``."""
        return get_required_n_indices(self.mode)

    @property
    def window_bp(self) -> Optional[int]:
        """Half-window size in base pairs (``window_kb * 1000``)."""
        if self.window_kb is None:
            return None
        return int(float(self.window_kb) * 1000)

    @property
    def highlighted_gene_names(self) -> set:
        """Lower-cased highlighted gene names used for gene-track matching."""
        return parse_highlighted_genes(self.highlighted_genes)
