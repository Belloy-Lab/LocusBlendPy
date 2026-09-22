# LocusBlend

LocusBlend visualizes GWAS summary statistics across a genomic region. Given two
summary-statistic datasets and a locus, it builds an interactive locus figure
with multi-variant linkage-disequilibrium (LD) coloring and a GENCODE gene
track, together with a locus-comparison figure of the two datasets.

If you prefer a graphical interface, use the LocusBlend web application:
<https://locusblend.wustl.edu>

## Installation

Install LocusBlend from GitHub:

```bash
pip install git+https://github.com/Belloy-Lab/LocusBlendPy.git
```

Python 3.9 or newer is required. LD calculation needs a local PLINK executable
and a local 1000 Genomes reference panel; see [Reference data](#reference-data).

## Quick start

```python
import locusblend

result = locusblend.plot(
    dataset1="trait1.tsv.gz",
    dataset2="trait2.tsv.gz",
    reference_dir="/path/to/reference_dir",
    ancestry="EUR",
    mode="three",
)

result.locus_figure.show()
```

`dataset1` and `dataset2` are summary-statistic files (see
[Input format](#input-format)) or already-loaded `pandas.DataFrame` objects.
`ancestry` selects the reference panel, and `mode` chooses how many index
variants are shown (see [Plot modes](#plot-modes)).

## Input format

Input files may be `.csv`, `.tsv`, `.txt`, or the `.gz`-compressed equivalents.
Coordinates must be GRCh38/hg38; no liftover is performed.

| Column   | Required | Description |
| -------- | -------- | ----------- |
| `CHR`    | yes      | Chromosome (1-22 or X; `23`/`chr23` is accepted for X) |
| `BP`     | yes      | Base-pair position (GRCh38) |
| `P`      | yes      | Association p-value |
| `A1`     | yes      | Effect allele |
| `A2`     | yes      | Other allele |
| `rsid`   | no       | Variant identifier; recommended, used as the variant label and for matching index variants |
| `BETA`   | no       | Effect size |
| `SE`     | no       | Standard error |
| `A1FREQ` | no       | Effect-allele frequency |
| `N`      | no       | Sample size |

Common aliases (for example `#chr`, `pos`, `pval`, `SNP`, `EA`/`NEA`,
`effect_allele`/`other_allele`, `EAF`/`MAF`) are recognized automatically and
matched case-insensitively. Optional columns are retained with the dataset; only
the required columns are needed to build the figures.

## Reference data

LD calculation requires a local, ancestry-matched 1000 Genomes GRCh38 reference
panel. Supported ancestries: **AFR**, **AMR**, **EAS**, **EUR**, **SAS**.

Supply the reference directory with `reference_dir=...`. The reference data
guide covers downloading 1000 Genomes data, preparing PLINK binary files, and
rsID handling: [docs/reference_data.md](docs/reference_data.md).

## Plot modes

Set the mode with `mode=` (`"three"` is the default):

| `mode`       | Mode | Description |
| ------------ | ---- | ----------- |
| `"standard"` | Standard locus zoom | One index variant. |
| `"two"`      | Two-index LocusBlend | Two index variants, with blended LD coloring. |
| `"three"`    | Three-index LocusBlend | Three index variants, with blended LD coloring. |

Index variants are selected automatically by LD clumping (from dataset 1 by
default; use `auto_index_source="dataset2"` to change that), or supplied
explicitly with `index_variants=[...]` — one entry per index variant required by
the chosen mode.

## Output

`locusblend.plot()` returns a `LocusBlendResult` holding the main Plotly
figures:

- `result.locus_figure` — the combined three-row figure: dataset 1, dataset 2
  and the GENCODE gene track;
- `result.compare_figure` — the locus-comparison figure for the active index
  variants.

Both are standard Plotly figures, so you can display them interactively or
export them. Pass `output="figure.png"` to `plot()` to also write the combined
locus figure to a PNG file.

## Citation

If you use LocusBlend in your research, please cite the LocusBlend publication.

## License

LocusBlend is released under the [MIT License](LICENSE).
