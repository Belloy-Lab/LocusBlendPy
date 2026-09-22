"""Checks for the public reference-data guide and the preparation helper.

These tests keep the written workflow, the shell helper and
``ReferenceManager``'s file-name convention from drifting apart. The bash-based
comparison is skipped when no usable bash interpreter is available.
"""

import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from locusblend.reference import ReferenceManager

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS = REPO_ROOT / "docs" / "reference_data.md"
SCRIPT = REPO_ROOT / "scripts" / "prepare_1000g_reference.sh"

ANCESTRIES = ("AFR", "AMR", "EAS", "EUR", "SAS")
SAMPLE_CHROMS = ("1", "14", "22", "X")

VERIFIED_FLAGS = (
    "--pfile",
    "vzs",
    "--keep",
    "--remove",
    "--chr",
    "--set-missing-var-ids '@:#$r:$a'",
    "--new-id-max-allele-len 1000",
    "--make-bed",
    "--out",
)


def _find_usable_bash():
    """Return a bash executable that actually works, or None."""
    candidates = [
        os.environ.get("LOCUSBLEND_BASH"),
        shutil.which("bash"),
        r"C:\Program Files\Git\bin\bash.exe",
        "/bin/bash",
        "/usr/bin/bash",
    ]
    for candidate in candidates:
        if not candidate:
            continue
        if not os.path.isfile(candidate) and not shutil.which(candidate):
            continue
        try:
            probe = subprocess.run(
                [candidate, "-c", "echo ok"], capture_output=True, text=True, timeout=60
            )
        except (OSError, subprocess.SubprocessError):
            continue
        if probe.returncode == 0 and "ok" in probe.stdout:
            return candidate
    return None


def test_reference_data_doc_and_script_exist():
    assert DOCS.is_file(), DOCS
    assert SCRIPT.is_file(), SCRIPT


def test_reference_data_doc_is_public_facing():
    text = DOCS.read_text(encoding="utf-8")

    # recommended source: the official IGSR 30x GRCh38 collection
    assert "1000 Genomes 30x on GRCh38" in text
    assert "GRCh38" in text
    assert "3,202 samples" in text
    assert "2,504" in text
    assert "698" in text
    assert "genotype and phased VCF callsets" in text
    assert "PMID 36055201" in text
    for link in (
        "https://www.internationalgenome.org/data-portal/data-collection/30x-grch38",
        "https://www.internationalgenome.org/data",
        "https://www.cog-genomics.org/plink/2.0/",
        "https://www.ncbi.nlm.nih.gov/snp/",
        "https://ncbiinsights.ncbi.nlm.nih.gov/2025/03/18/dbsnp-release-157/",
    ):
        assert link in text, link

    # required software and the repository helper
    assert "PLINK 2" in text
    assert "scripts/prepare_1000g_reference.sh" in text
    assert "--print-template" in text

    # one keep list per supported ancestry
    for code in ANCESTRIES:
        assert f"{code}.txt" in text, code
        assert f"{code}.keep" not in text, code

    # variant IDs: filling in missing IDs vs. updating rsIDs
    assert "--set-missing-var-ids" in text
    assert "--update-name" in text
    assert "CHR:BP:REF:ALT" in text
    assert "allele-aware" in text
    assert "Build 157" in text

    # public file naming and chromosome coverage
    for entry in ("1000g/", "chr1.bed", "chr1.bim", "chr1.fam", "chrX.bed", "chrX.bim", "chrX.fam"):
        assert entry in text, entry
    assert "1-22 and X" in text

    # verification helper and usage example
    assert "locusblend.reference_status(" in text
    assert 'reference_dir="/path/to/reference_dir"' in text
    assert "locusblend.plot(" in text

    # public-facing only: no obsolete chromosome naming or insecure URLs
    for forbidden in ("ch23", "http://"):
        assert forbidden not in text, forbidden


def test_script_uses_the_verified_command_and_naming():
    text = SCRIPT.read_text(encoding="utf-8")

    assert text.startswith("#!/usr/bin/env bash")
    assert "set -euo pipefail" in text
    assert "command -v plink2" in text
    assert "ANCESTRIES=(AFR AMR EAS EUR SAS)" in text
    assert "CHROMOSOMES=(1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 X)" in text
    assert "src/locusblend/reference.py" in text  # naming template source of truth
    assert "docs/reference_data.md" in text  # points at the public guide

    for flag in VERIFIED_FLAGS:
        assert flag in text, flag

    # constraints: no historical chromosome naming remains, and the header
    # documents the public chrX convention
    assert "--rm-dup" not in text
    assert "ch23" not in text
    assert "chrX" in text
    assert "http://" not in text and "https://" not in text
    assert "1000g/${anc}" in text  # writes into OUTPUT_ROOT/1000g/<ANCESTRY>/
    assert "AFR.txt" in text and "SAS.txt" in text  # keep-list naming documented


def test_script_cli_behaviour():
    bash = _find_usable_bash()
    if bash is None:
        pytest.skip("no usable bash interpreter available")

    help_run = subprocess.run(
        [bash, SCRIPT.as_posix(), "--help"], capture_output=True, text=True, cwd=str(REPO_ROOT)
    )
    assert help_run.returncode == 0
    assert "Usage:" in help_run.stdout

    no_args = subprocess.run(
        [bash, SCRIPT.as_posix()], capture_output=True, text=True, cwd=str(REPO_ROOT)
    )
    assert no_args.returncode != 0
    assert "Usage:" in (no_args.stdout + no_args.stderr)


def test_script_output_template_matches_reference_manager():
    """The script's derived PLINK prefix must match ReferenceManager exactly."""
    bash = _find_usable_bash()
    if bash is None:
        pytest.skip("no usable bash interpreter available")

    run = subprocess.run(
        [bash, SCRIPT.as_posix(), "--print-template"],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    assert run.returncode == 0, run.stderr

    match = re.search(r"^bfile_prefix_template: (.+)$", run.stdout, flags=re.MULTILINE)
    assert match, run.stdout
    template = match.group(1).strip()

    for code in ANCESTRIES:
        manager = ReferenceManager(reference_dir=REPO_ROOT, ancestry=code)
        for chrom in SAMPLE_CHROMS:
            expected = manager.bfile_prefix(chrom).name
            actual = template.replace("{chrom}", chrom)
            assert actual == expected, (code, chrom, actual, expected)
            assert actual == f"chr{chrom}", (code, chrom, actual)

    # the file name carries no ancestry (the directory does); chrX is documented
    assert "{ancestry}" not in template
    assert "1000g/EUR/chr14" in run.stdout
    assert "chrX" in run.stdout
    assert "ch23" not in run.stdout
