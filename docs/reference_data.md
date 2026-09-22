# Reference data

LocusBlend calculates LD from a local, ancestry-matched 1000 Genomes reference
panel. Reference data are not bundled or downloaded: you prepare the panel once
and point the package at it with `reference_dir=...`.

## Recommended source

Use the official IGSR collection **1000 Genomes 30x on GRCh38**:

- sequenced and aligned on **GRCh38**;
- **3,202 samples** in total: the **2,504 unrelated Phase 3 samples** form the
  unrelated reference panel, and an additional **698 related samples** are also
  available;
- **genotype and phased VCF callsets** are available for download.

The dataset is described in Byrska-Bishop et al., *Cell* 2022 (PMID 36055201).

- Data collection (1000 Genomes 30x on GRCh38):
  <https://www.internationalgenome.org/data-portal/data-collection/30x-grch38>
- IGSR data and download page: <https://www.internationalgenome.org/data>

Select the callset and chromosome files you need from the collection page
rather than hard-coding deep FTP paths, which change over time.

## Required software

- **PLINK 2** — <https://www.cog-genomics.org/plink/2.0/> — to convert the
  genotypes and write the reference files.
- Standard command-line download and decompression tools for the files you
  select (for example `curl`/`wget` and `gzip`/`bgzip`).

## Choose samples by ancestry

LocusBlend supports five ancestry groups: **AFR**, **AMR**, **EAS**, **EUR**,
**SAS**. Derive one sample keep list per super-population from the official
IGSR sample and population metadata for the collection; do not assemble
population membership by hand.

For the recommended LocusBlend LD panel, use the unrelated **2,504-sample Phase
3 panel**. The 698 additional related samples are available from IGSR but
should not be included automatically.

Example keep lists (one per super-population, all in one keep directory):

```text
AFR.txt
AMR.txt
EAS.txt
EUR.txt
SAS.txt
```

## Convert to PLINK binary files

The goal is one PLINK BED/BIM/FAM set per ancestry and chromosome, for
chromosomes **1-22 and X**, named `chr1.*` … `chr22.*` and `chrX.*`.

The helper `scripts/prepare_1000g_reference.sh` implements this workflow and
derives the file names from the installed package, so they always match what
LocusBlend expects:

```bash
bash scripts/prepare_1000g_reference.sh <PGEN_PREFIX> <KEEP_DIR> <OUTPUT_ROOT> [REMOVE_FILE]
```

- `<PGEN_PREFIX>` — PLINK 2 PGEN dataset prefix (`.pgen`/`.pvar`/`.psam`), for
  example built from the IGSR GRCh38 VCFs with `plink2 --vcf … --make-pgen`;
- `<KEEP_DIR>` — directory holding the per-ancestry keep lists;
- `<OUTPUT_ROOT>` — reference root; output is written to
  `<OUTPUT_ROOT>/1000g/<ANCESTRY>/`;
- `[REMOVE_FILE]` — optional sample-removal list if you deliberately exclude
  samples.

For each ancestry and chromosome the script runs one PLINK 2 command of this
form (shown here for EUR chromosome 14):

```bash
plink2 \
  --pfile <PGEN_PREFIX> vzs \
  --keep <KEEP_DIR>/EUR.txt \
  --chr 14 \
  --set-missing-var-ids '@:#$r:$a' \
  --new-id-max-allele-len 1000 \
  --make-bed \
  --out <OUTPUT_ROOT>/1000g/EUR/chr14
```

`bash scripts/prepare_1000g_reference.sh --print-template` shows the exact
output names without running PLINK 2.

## Variant IDs and rsIDs

### Missing variant IDs

PLINK 2's `--set-missing-var-ids`
(<https://www.cog-genomics.org/plink/2.0/data#set_all_var_ids>) assigns an ID
only to variants whose ID is missing; variants that already have an ID are left
untouched. A chromosome/position/allele identifier such as `CHR:BP:REF:ALT` is
a good fallback unique ID, and the helper script uses
`--set-missing-var-ids '@:#$r:$a'` for exactly that purpose.

This is **not** an rsID update — it only fills in missing IDs.

### Updating rsIDs

If you specifically want current rsIDs, map them from NCBI dbSNP
(<https://www.ncbi.nlm.nih.gov/snp/>; current release Build 157, see
<https://ncbiinsights.ncbi.nlm.nih.gov/2025/03/18/dbsnp-release-157/>):

- use the GRCh38-compatible dbSNP records;
- match **allele-aware** — on chromosome, position *and* alleles — never by
  position alone;
- build a two-column mapping file: the existing ID in column 1 and the new rsID
  in column 2;
- apply it with PLINK 2 `--update-name`
  (<https://www.cog-genomics.org/plink/2.0/data>), which by default reads the
  new ID from column 2 and the old ID from column 1.

Not every variant has an rsID, and valid existing rsIDs should not be
overwritten unnecessarily. LocusBlend does not require rsIDs: the fallback IDs
above are sufficient for indexing and plotting.

## Expected directory layout

```text
reference_dir/
└── 1000g/
    ├── AFR/
    │   ├── chr1.bed
    │   ├── chr1.bim
    │   ├── chr1.fam
    │   └── ...
    ├── AMR/
    ├── EAS/
    ├── EUR/
    │   ├── chr1.bed
    │   ├── chr1.bim
    │   ├── chr1.fam
    │   ├── ...
    │   ├── chrX.bed
    │   ├── chrX.bim
    │   └── chrX.fam
    └── SAS/
```

Each ancestry directory must contain chromosomes **1-22 and X**: `chr1.*`
through `chr22.*` and `chrX.*`.

## Verify the reference

```python
import locusblend

status = locusblend.reference_status(reference_dir="/path/to/reference_dir", ancestry="EUR", chrom="14")
print(status.describe())
```

## Use with LocusBlend

```python
result = locusblend.plot(
    ...,
    reference_dir="/path/to/reference_dir",
    ancestry="EUR",
)
```
