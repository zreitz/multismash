# multiSMASH: A workflow and scripts for large-scale antiSMASH analyses
[![DOI](https://zenodo.org/badge/633863055.svg)](https://zenodo.org/badge/latestdoi/633863055)

multiSMASH is a Snakemake-based [antiSMASH](https://antismash.secondarymetabolites.org/#!/start) 
wrapper that streamlines large-scale analyses of biosynthetic gene clusters (BGCs) 
across multiple genomes.

The pipeline can:
1. Parallelize antiSMASH runs on user-supplied genomes (OR accept existing results)
2. Summarize and tabulate the antiSMASH results 
   with [information on each region](#tabulateregionspy) 
   and [per-genome BGC counts](#countregionspy)
3. Run [BiG-SCAPE](https://github.com/medema-group/BiG-SCAPE/wiki) on the 
   resulting BGCs to visualize gene cluster families (GCFs).

## Installation

### Recommended: Installing multiSMASH inside an antiSMASH conda environment

*For help installing antiSMASH, see my [antiSMASH 7 installation protocol](#antiSMASH-7-installation-protocol) 
below or [the official antiSMASH documentation](https://docs.antismash.secondarymetabolites.org/install/).*

Activate the antiSMASH environment:
```bash
conda activate antismash7
```
Download this repository and enter it, then install the package with pip:
```bash
git clone https://github.com/zreitz/multismash.git
cd multismash
pip install -e .
```

multiSMASH should now be added to your path and ready to use from any directory.
```bash
multismash -h
```

### Other installation notes
* If you are only using the [standalone scripts](#standalone-scripts) for 
  tabulating existing antiSMASH runs, then no dependencies are needed beyond
  `Python>=3.7` and the standard library. Simply download this repository.
* If you want to install multiSMASH in a separate conda environment, create one,
  then follow the installation instructions above. Finally, adjust the
  `antismash_conda_env_name` and `antismash_command` parameters in the config file.
* **BiG-SCAPE** is turned off by default. The first time a BiG-SCAPE job is 
  requested (`run_bigscape: True` in the config file) then multiSMASH will 
  automatically install `bigscape=1.1.5` and download the latest Pfam database.
  If you want to use your own [BiG-SCAPE conda installation](https://github.com/medema-group/BiG-SCAPE/wiki/installation), 
  point multiSMASH to the correct locations with the last three parameters
  of the config file.
* **Docker:** While Snakemake [supports containerization](https://snakemake.readthedocs.io/en/stable/snakefiles/deployment.html#containerization-of-conda-based-workflows),
  I've only used conda. If you want to help add/test support for other setups, then
  please submit an issue with your scenario (or even better, submit a pull request).

## Usage
Inputs, outputs, and all other flags are set in a job-specific configuration file. 
A working example is provided in [example/config-example.yaml](example/config-example.yaml), 
along with three *E. coli* genomes.

Preview the steps that will be performed with the `-n` (aka `--dry-run`) snakemake flag:

```bash
multismash example/config-example.yaml -n
```

```bash
multismash example/config-example.yaml
```

#######  old ###


After the pipeline runs, the results will be located in `results/test` (as specified in the configfile).

Each genome will be analyzed by antiSMASH using a single core. Setting multiple cores allows for parallel analyses (this is way faster in my experience than giving a single antiSMASH run multiple cores). 

`snakemake --cores 4 --use-conda --configfile config/config.yaml     # Divide and conquer`

The tabulation scripts `count_regions.py` and `tabulate_regions.py` (see below) are run by default. If you only want to run antiSMASH, use the `--until` flag:

`snakemake --cores 1 --use-conda --configfile config/config.yaml --until run_antismash`

The BiG-SCAPE analysis is off by default. To enable it, set `run_bigscape: True` in the configfile, or manually set the flag from the command line (which overrides the configfile):

`snakemake --cores 1 --use-conda --configfile config/config.yaml --config run_bigscape=True`


* The minimal flag 

**multismash --help output**
```text
usage: multismash [-h] configfile [--cores CORES] [...]

multiSMASH is a Snakemake-based antiSMASH wrapper that streamlines 
large-scale analyses of BGCs across multiple genomes.

positional arguments:
  configfile  path to the YAML file with job configurations

options:
  -h, --help  show this help message and exit

Any additional arguments will be passed to Snakemake. Use `snakemake -h`
to see all available parameters. Flags you may find useful:
  --dry-run, -n   Do not execute anything, and display what would be done
  --quiet, -q     Do not output any progress or rule information
  --forceall, -F  Force the (re-)execution of all rules 
```

## Standalone scripts

The following standalone scripts are available in `workflow/scripts`:

### count_regions.py
Given a bunch of antismash results, count the BGC regions
```text
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

```text
usage: tabulate_regions.py [-h] asdir outpath

positional arguments:
  asdir       directory containing antiSMASH directories
  outpath     desired path+name for the output TSV

options:
  -h, --help  show this help message and exit
```

Example output: [results/example/all_regions.tsv](results/example/all_regions.tsv)



## antiSMASH 7 installation protocol
Here's my secret recipe for an antiSMASH 7.0 conda environment that is multiSMASH-compatible.
See [the official antiSMASH documentation](https://docs.antismash.secondarymetabolites.org/install/) 
 for more installation options. 

```bash
# Create the environment. Conda should work too, but mamba is faster
mamba create -n antismash7 python=3.10
mamba activate antismash7

# Install dependencies
mamba install hmmer2 hmmer diamond fasttree prodigal glimmerhmm   # Not meme!

# Download and install antiSMASH
git clone --branch 7-0-stable https://github.com/antismash/antismash.git antismash7
cd antismash7
pip install .
```

Note that Python must be 3.9+.


The reason antiSMASH 7 is not one-line conda installable is that it 
requires `meme<=4.11.2`, which doesn't play well with others. 

You will have to install the old version of meme suite separately and direct
 antiSMASH to the binaries for `meme` and `fimo`. Options include:
- Use the binaries from a working antiSMASH 6 conda environment
- Create a separate conda environment just for the old meme version with   
`mamba create --name meme_4.11.2 meme=4.11.2`

Get the path to the binaries themselves (try `which meme; which fimo` 
from inside the meme-containing environment). You'll get something like:   
`/Users/zach/mambaforge/envs/meme_4.11.2/bin/meme`

Permanently tell antiSMASH where to find them with a config file:
```bash
echo "executable-paths meme=/path/to/meme,fimo=/path/to/fimo" >> ~/.antismash7.cfg
```


Finally, download the various databases that antiSMASH requires:
```bash
download-antismash-databases
```

Test your installation:
```bash
antismash --check-prereqs
```