"""Minimal LocusBlend example: build the locus and locus-compare figures.

Set dataset1/dataset2 to your own GRCh38 summary-statistic files. The example
expects a local 1000 Genomes reference panel at
reference_dir/1000g/<ANCESTRY>/chr<chrom>.bed/.bim/.fam and PLINK on PATH; see
docs/reference_data.md.
"""

import locusblend


def main():
    result = locusblend.plot(
        dataset1="trait1.tsv.gz",
        dataset2="trait2.tsv.gz",
        reference_dir="/path/to/reference_dir",
        ancestry="EUR",
        mode="three",
    )

    # Index variants are selected automatically by LD clumping (dataset 1 by
    # default); result.compare_figure holds the locus-compare figure.
    result.locus_figure.show()


if __name__ == "__main__":
    main()
