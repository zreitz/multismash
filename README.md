# multiSMASH: A workflow and scripts for large-scale antiSMASH analyses
[![DOI](https://zenodo.org/badge/633863055.svg)](https://zenodo.org/badge/latestdoi/633863055)

This pipeline runs antiSMASH on a directory of genome files, tabulates the results, and runs BiG-SCAPE clustering. 

## Installation

Download and enter this repository:
```
git clone https://github.com/zreitz/multismash.git
cd multismash
```

If you only want to use the [standalone scripts](#standalone-scripts) to tabulate existing antiSMASH runs, you're probably done! Those scripts have no dependencies outside [Python 3.6+](https://www.python.org/downloads/) and the standard Python library.

The pipeline itself requires `snakemake` or `snakemake-minimal`. See their [documentation](https://snakemake.readthedocs.io/en/stable/getting_started/installation.html) for installation instructions.

If you want to run antiSMASH, then you'll require a local version of antiSMASH. See their [documentation](https://docs.antismash.secondarymetabolites.org/install/) for installation instructions. 
I use antiSMASH in a separate conda environment, and the workflow will need some minor adjustments for other installations such as Docker. If you're interested in those adjustments (and helping me make/test them), please let me know!

Installing BiG-SCAPE for BGC clustering is optional ([their installation instructions](https://github.com/medema-group/BiG-SCAPE/wiki/installation)). Again, the pipeline currently expects a conda installation.


## Snakemake pipeline

After downloading this repo and installing antiSMASH and Snakemake(-minimal), you can test your installation with the provided [example](example) Genbank files. The workflow relies on a configuration file. The example genomes can be run using [config/config.yaml](config/config.yaml).

`snakemake --cores 1 --use-conda --configfile config/config.yaml`

After the pipeline runs, the results will be located in `results/test` (as specificied in the configfile).

Each genome will be analyzed by antiSMASH using a single core. Setting multiple cores allows for parallel analyses (this is way faster in my experience than giving a single antiSMASH run multiple cores). 

`snakemake --cores 4 --use-conda --configfile config/config.yaml     # Divide and conquer`

The tabulation scripts `count_regions.py` and `tabulate_regions.py` (see below) are run by default. If you only want to run antiSMASH, use the `--until` flag:

`snakemake --cores 1 --use-conda --configfile config/config.yaml --until run_antismash`

The BiG-SCAPE analysis is off by default. To enable it, set `run_bigscape: True` in the configfile, or manually set the flag from the command line (which overrides the configfile):

`snakemake --cores 1 --use-conda --configfile config/config.yaml --config run_bigscape=True`


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
