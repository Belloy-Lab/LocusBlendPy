"""PLINK 2 command construction for LD calculation."""

import subprocess
from pathlib import Path

from locusblend import ld


def test_ld_command_includes_force_intersect(tmp_path, monkeypatch):
    """--extract plus --from-bp/--to-bp is an intersection; PLINK 2 needs --force-intersect."""
    prefix = tmp_path / "1000g_EUR_ch14"
    Path(str(prefix) + ".bed").write_text("", encoding="utf-8")
    Path(str(prefix) + ".fam").write_text("", encoding="utf-8")
    Path(str(prefix) + ".bim").write_text(
        "14 rsone007 0 73238768 A G\n"
        "14 rsone008 0 73239000 C T\n",
        encoding="utf-8",
    )

    # stand-in PLINK executable: only its path is recorded, it is never executed
    plink_exec = tmp_path / "plink"
    plink_exec.write_text("", encoding="utf-8")

    recorded = []

    def fake_run(cmd, **kwargs):
        recorded.append(list(cmd))
        out_prefix = cmd[cmd.index("--out") + 1]
        # Real PLINK 2 writes <prefix>.vcor with ID_A/ID_B/UNPHASED_R2.
        Path(out_prefix + ".vcor").write_text(
            "#CHROM_A POS_A ID_A REF_A ALT_A CHROM_B POS_B ID_B REF_B ALT_B UNPHASED_R2\n"
            "14 73238768 rsone007 A G 14 73239000 rsone008 C T 0.83\n"
            "14 73999000 rsother A G 14 73239000 rsone008 C T 0.42\n",
            encoding="utf-8",
        )
        return subprocess.CompletedProcess(cmd, 0, stdout="")

    monkeypatch.setattr(ld.subprocess, "run", fake_run)

    ld_maps, index_status, ref_snps = ld.compute_ld_maps_with_plink(
        bfile_prefix=str(prefix),
        chrom="14",
        start=73_000_000,
        end=73_500_000,
        window_snps=("rsone008",),
        idx1_ref="rsone007",
        idx2_ref=None,
        idx3_ref=None,
        plink_path=str(plink_exec),
    )

    assert len(recorded) == 1
    cmd = recorded[0]
    # both inclusion filters are present, so PLINK must be told to intersect them
    assert "--extract" in cmd
    assert "--from-bp" in cmd and "--to-bp" in cmd
    assert "--force-intersect" in cmd
    assert "--rm-dup" in cmd
    assert cmd[cmd.index("--rm-dup") + 1] == "force-first"
    # existing LD arguments are unchanged
    assert cmd[cmd.index("--from-bp") + 1] == "73000000"
    assert cmd[cmd.index("--to-bp") + 1] == "73500000"
    assert cmd[cmd.index("--ld-snp") + 1] == "rsone007"
    assert "--r2-unphased" in cmd
    assert "cols=chrom,pos,id,ref,alt" in cmd
    # the legacy PLINK 1.x flag must not be used
    assert "--r2" not in cmd
    assert cmd[cmd.index("--ld-window") + 1] == "999999"
    assert cmd[cmd.index("--ld-window-kb") + 1] == "1000"
    assert cmd[cmd.index("--ld-window-r2") + 1] == "0"
    assert "--allow-extra-chr" not in cmd
    # ID_B / UNPHASED_R2 are mapped back exactly like SNP_B / R2 used to be
    assert ld_maps["r2_1"]["rsone008"] == 0.83
    assert ld_maps["r2_1"]["rsone007"] == 1.0
    assert "rsother" not in ld_maps["r2_1"]
    assert index_status["variant 1"] is True
    assert ref_snps == ("rsone007", "rsone008")


def test_ld_command_reads_legacy_plink1_ld_output(tmp_path, monkeypatch):
    """Legacy PLINK 1.x <prefix>.ld / SNP_A,SNP_B,R2 output is still accepted."""
    prefix = tmp_path / "1000g_EUR_ch14"
    Path(str(prefix) + ".bed").write_text("", encoding="utf-8")
    Path(str(prefix) + ".fam").write_text("", encoding="utf-8")
    Path(str(prefix) + ".bim").write_text(
        "14 rsone007 0 73238768 A G\n"
        "14 rsone008 0 73239000 C T\n",
        encoding="utf-8",
    )

    plink_exec = tmp_path / "plink"
    plink_exec.write_text("", encoding="utf-8")

    def fake_run(cmd, **kwargs):
        out_prefix = cmd[cmd.index("--out") + 1]
        Path(out_prefix + ".ld").write_text(
            "CHR_A BP_A SNP_A CHR_B BP_B SNP_B R2\n"
            "14 73238768 rsone007 14 73239000 rsone008 0.83\n",
            encoding="utf-8",
        )
        return subprocess.CompletedProcess(cmd, 0, stdout="")

    monkeypatch.setattr(ld.subprocess, "run", fake_run)

    ld_maps, index_status, ref_snps = ld.compute_ld_maps_with_plink(
        bfile_prefix=str(prefix),
        chrom="14",
        start=73_000_000,
        end=73_500_000,
        window_snps=("rsone008",),
        idx1_ref="rsone007",
        idx2_ref=None,
        idx3_ref=None,
        plink_path=str(plink_exec),
    )

    assert ld_maps["r2_1"]["rsone008"] == 0.83
    assert ld_maps["r2_1"]["rsone007"] == 1.0
    assert index_status["variant 1"] is True
    assert ref_snps == ("rsone007", "rsone008")
