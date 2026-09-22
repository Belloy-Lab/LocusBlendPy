"""PLINK 2 command construction for automatic index-variant clumping."""

import subprocess
from pathlib import Path

import pandas as pd

from locusblend import variants


def _write_fake_bfile(prefix):
    for suffix in (".bed", ".bim", ".fam"):
        Path(str(prefix) + suffix).write_text("", encoding="utf-8")


def test_clump_command_intersects_candidates_with_locus_window(tmp_path, monkeypatch):
    """--extract plus --from-bp/--to-bp is an intersection; PLINK 2 needs --force-intersect."""
    prefix = tmp_path / "1000g_EUR_ch14"
    _write_fake_bfile(prefix)

    # stand-in PLINK executable: only its path is recorded, it is never executed
    plink_exec = tmp_path / "plink"
    plink_exec.write_text("", encoding="utf-8")

    candidates = pd.DataFrame(
        {
            "REF_SNP": ["rsone007", "rsone008"],
            "DISPLAY_ID": ["rsone007", "rsone008"],
            "CHR": ["14", "14"],
            "BP": [73_238_768, 73_239_000],
            "P": [1e-12, 1e-8],
        }
    )

    recorded = {}

    def fake_run(cmd, **kwargs):
        recorded["cmd"] = list(cmd)
        out_prefix = cmd[cmd.index("--out") + 1]
        Path(out_prefix + ".clumped").write_text(
            "CHR F SNP BP P TOTAL NSIG S05 S01 S001 S0001 SP2\n"
            "14 rsone007 rsone007 73238768 1e-12 1 1 1 1 1 1 0.9\n",
            encoding="utf-8",
        )
        return subprocess.CompletedProcess(cmd, 0, stdout="")

    monkeypatch.setattr(variants.subprocess, "run", fake_run)

    selected = variants.run_plink_clump_for_auto_indices(
        candidates=candidates,
        bfile_prefix=str(prefix),
        selected_chrom="14",
        start_bp=73_000_000,
        end_bp=73_500_000,
        max_indices=1,
        clump_r2=0.01,
        plink_path=str(plink_exec),
    )

    cmd = recorded["cmd"]
    # both inclusion filters are present, so PLINK must be told to intersect them
    assert "--extract" in cmd
    assert "--from-bp" in cmd and "--to-bp" in cmd
    assert "--force-intersect" in cmd
    assert "--rm-dup" in cmd
    assert cmd[cmd.index("--rm-dup") + 1] == "force-first"
    assert cmd[cmd.index("--from-bp") + 1] == "73000000"
    assert cmd[cmd.index("--to-bp") + 1] == "73500000"
    # thresholds and the returned selection are unchanged
    assert cmd[cmd.index("--clump-r2") + 1] == "0.01"
    assert selected["REF_SNP"].tolist() == ["rsone007"]
