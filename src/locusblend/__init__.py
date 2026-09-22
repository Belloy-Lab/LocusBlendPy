"""LocusBlend: regional GWAS visualization with multi-variant LD coloring.

Public entry points:

* :func:`locusblend.plot` - build the combined locus figure (dataset 1,
  dataset 2 and the GENCODE gene track) plus the locus-compare figure from two
  summary-statistic datasets;
* :func:`locusblend.reference_status` - inspect a prepared reference directory.

Reference data (1000 Genomes PLINK panels, GENCODE annotation and the optional
recombination BigWig) are never bundled or downloaded: point the package at
them with ``reference_dir=...`` or ``LOCUSBLEND_REFERENCE_DIR``. The package is
UI-agnostic. The public API is still stabilizing.
"""

from importlib.metadata import PackageNotFoundError, version

from . import (
    api,
    colors,
    compare,
    config,
    export,
    genes,
    io,
    ld,
    models,
    paths,
    plotting,
    reference,
    variants,
)
from .api import plot
from .config import LocusBlendConfig
from .models import IndexVariant, LocusBlendResult
from .reference import (
    ReferenceManager,
    ReferenceStatus,
    ReferenceValidation,
    reference_status,
)

# pyproject.toml is the single source of truth for the release version; it is
# read back from the installed distribution metadata instead of being
# duplicated here. "0+unknown" only appears in a source tree that is not
# installed as a distribution.
try:
    __version__ = version("locusblend")
except PackageNotFoundError:  # pragma: no cover - uninstalled source checkout
    __version__ = "0+unknown"

__all__ = [
    "IndexVariant",
    "LocusBlendConfig",
    "LocusBlendResult",
    "ReferenceManager",
    "ReferenceStatus",
    "ReferenceValidation",
    "__version__",
    "api",
    "colors",
    "compare",
    "config",
    "export",
    "genes",
    "io",
    "ld",
    "models",
    "paths",
    "plot",
    "plotting",
    "reference",
    "reference_status",
    "variants",
]
