# multiSMASH: A workflow and scripts for large-scale antiSMASH analyses

## Snakemake pipeline

This pipeline runs antiSMASH on a directory of genome files, tabulates the results, and runs BiG-SCAPE clustering. Currently undocumented, but please leave an issue if you have problems. 

The workflow is in [workflow/Snakefile](workflow/Snakefile), and relies on information provided in a configuration file, see [config/config.yaml](config/config.yaml) for an example.

The workflow can be run from the command line with something like:

`snakemake --cores 1 --use-conda --configfile config/config.yaml`

Each genome will be analyzed by antiSMASH using a single core, and setting multiple cores allows for parallel analyses (this is way faster in my experience than giving a single antiSMASH run multiple cores). 

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

Example output: [results/example/region_counts.tsv](results/example/region_counts.tsv)

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

Example output: [results/example/all_regions.tsv](results/example/all_regions.tsv)
