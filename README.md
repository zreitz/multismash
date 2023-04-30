# multiSMASH: A workflow and scripts for large-scale antiSMASH analyses

## Standalone scripts

The following standalone scripts are available in `workflow/scripts`:

### count_regions.py
Given a bunch of antismash results, count the BGC regions
```
usage: count_regions.py [-h] [--contig] [--hybrid] asdir outpath

positional arguments:
  asdir       directory containing antiSMASH directories
  outpath     desired path+name for the output TSV

options:
  -h, --help  show this help message and exit
  --contig    each row of the table is an individual contig rather than a genome
  --hybrid    hybrid regions are only counted once, as 'hybrid'
```

Example output: `results/example/region_counts.tsv`

### tabulate_regions.py
Given a bunch of antismash results, tabulate BGC regions

```
usage: tabulate_regions.py [-h] asdir outpath

positional arguments:
  asdir       directory containing antiSMASH directories
  outpath     desired path+name for the output TSV

options:
  -h, --help  show this help message and exit
```

Example output: `results/example/all_regions.tsv`