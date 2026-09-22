"""Import and package-surface checks."""

import importlib
import re
from pathlib import Path

import pytest

SUBMODULES = [
    "api",
    "colors",
    "compare",
    "config",
    "export",
    "genes",
    "io",
    "ld",
    "models",
    "plotting",
    "reference",
    "variants",
]

HARD_CODED_PATH_PATTERNS = (
    r"[A-Za-z]:[\\/][\w.-]{2,}",  # Windows drive-letter paths (e.g. C:\data, D:/ref)
    r"(?<![\w.])/(?:home|Users|srv|mnt|storage)/",  # POSIX absolute paths
)


def test_import_locusblend():
    import locusblend

    # __version__ comes from the installed distribution metadata (pyproject.toml
    # is the single source of truth), so only its presence is asserted here.
    assert isinstance(locusblend.__version__, str)
    assert locusblend.__version__
    assert callable(locusblend.plot)
    assert callable(locusblend.reference_status)

    for name in (
        "LocusBlendConfig",
        "LocusBlendResult",
        "IndexVariant",
        "ReferenceManager",
        "ReferenceStatus",
        "ReferenceValidation",
    ):
        assert hasattr(locusblend, name), name


@pytest.mark.parametrize("submodule", SUBMODULES)
def test_submodule_imports(submodule):
    module = importlib.import_module(f"locusblend.{submodule}")
    assert module is not None


def test_package_sources_avoid_hard_coded_absolute_paths():
    """Architectural guard: the package builds no hard-coded absolute paths."""
    import locusblend

    package_dir = Path(locusblend.__file__).resolve().parent
    offenders = []

    for path in sorted(package_dir.glob("*.py")):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for pattern in HARD_CODED_PATH_PATTERNS:
                if re.search(pattern, line):
                    offenders.append(f"{path.name}:{number}")

    assert offenders == []
