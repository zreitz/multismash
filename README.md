# multiSMASH: A workflow and scripts for large-scale antiSMASH analyses
[![DOI](https://zenodo.org/badge/633863055.svg)](https://zenodo.org/badge/latestdoi/633863055)

multiSMASH is a Snakemake-based [antiSMASH](https://antismash.secondarymetabolites.org/#!/start) 
wrapper that streamlines large-scale analyses of biosynthetic gene clusters (BGCs) 
across multiple genomes.

The pipeline can:
1. Parallelize antiSMASH runs on user-supplied genomes ([OR accept existing results](#tabulating-existing-antismash-results))
2. Summarize and tabulate the antiSMASH results 
   with [information on each region](#tabulate_regionspy) 
   and [per-genome BGC counts](#count_regionspy)
3. Run [BiG-SCAPE](https://github.com/medema-group/BiG-SCAPE/wiki) on the 
   resulting BGCs to visualize gene cluster families (GCFs).

## Installation

### Recommended: Installing multiSMASH inside an antiSMASH conda environment

*For help installing antiSMASH, see my [antiSMASH 7 installation protocol](#antismash-7-installation-protocol) 
below or [the official antiSMASH documentation](https://docs.antismash.secondarymetabolites.org/install/).*

Activate the antiSMASH environment:
```bash
conda activate antismash7
```
Download this repository and enter it, then install the package with pip:
```bash
git clone https://github.com/zreitz/multismash.git
cd multismash
pip install .
```

`multismash` should now be added to your path and ready to use from any directory:
```
$ multismash -h
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

### Other installation notes
* If you are only using the [standalone scripts](#standalone-scripts) for 
  tabulating existing antiSMASH runs, then no dependencies are needed beyond
  `python>=3.7` and the standard library. Simply download the scripts from this repository.
* If you want to install multiSMASH in its own conda environment, you can do so,
  otherwise following installation instructions above. You will have to adjust the
  `antismash_conda_env_name` and `antismash_command` parameters in the config file.
* **BiG-SCAPE** is turned off by default. The first time a BiG-SCAPE job is 
  requested (`run_bigscape: True` in the config file) then multiSMASH will 
  automatically install `bigscape` from Bioconda and reuse the Pfam database from antiSMASH.
  If you want to use your own [BiG-SCAPE installation](https://github.com/medema-group/BiG-SCAPE/wiki/installation), 
  point multiSMASH to the correct locations with the last three parameters
  of the config file.
* **Docker:** Snakemake [supports containerization](https://snakemake.readthedocs.io/en/stable/snakefiles/deployment.html#containerization-of-conda-based-workflows),
  and therefore multiSMASH should be able to. However, I've never used docker/singularity. 
  If you want to help add/test singularity support, then
  please submit an issue with your scenario (or even better, submit a pull request).

## Usage

### An example workflow
Inputs, outputs, and all other flags are set in a job-specific configuration file that is 
used as a required argument for `multismash`.

A working example is provided in [example/config-example.yaml](example/config-example.yaml), 
along with three *E. coli* genomes.

Preview the steps that will be performed with the `-n` (aka `--dry-run`) snakemake flag:
```text
$ multismash example/config-example.yaml -n

Running multiSMASH with 3 cores
3 gbff.gz files found
Building DAG of jobs...
Job stats:
job                 count
----------------  -------
all                     1
count_regions           1
run_antismash           3
tabulate_regions        1
total                   6

<snip>

This was a dry-run (flag -n). The order of jobs does not reflect the order of execution.
```
The three provided genomes were found, yielding three `run_antismash` jobs. Due to
the configuration `cores: 3`, the jobs will run in parallel, each using a single 
core. This scales far more efficiently than multithreading antiSMASH itself. Once 
the antiSMASH runs finish, the results will be summarized with `count_regions` 
and `tabulate_regions` ([see below](#standalone-scripts)). 

Run the analysis by omitting the `-n` flag:
```bash
multismash example/config-example.yaml
```

The results can be found in `multismash/example_output/`, as specified by the 
`out_dir` configuration. 

### Note: default antiSMASH configuration
By default, antiSMASH is run with the `--minimal` flag, as set in the configuration `antismash_flags`. 
A minimal run reduces the run time by skipping many of the features that aren't used in the downstream 
tabulation, **including HTML generation**, as well as optional analysis modules such as NRPS/PKS domain or 
lanthipeptide precursor prediction. I made this the default because the time saving is significant, and
if I'm running hundreds of genomes, I'm not looking at most of the HTML files anyway.

If you want the HTML output for each run, you can add `--enable-html` to the configuration `antismash_flags`. 
To restore the antiSMASH default settings, remove the `--minimal` flag. Alternatively, I usually copy 
BGC region GBKs of interest to a new folder and use them as input for a second round of multiSMASH 
with a richer set of antiSMASH flags.

### Error handling: what happens if individual antiSMASH jobs fail
The logs for each antiSMASH run are stored within the output directory in 
 `log/<timestamp>/antismash`. Any errors are stored in `log/<timestamp>/antismash_errors.log`.

By default, multiSMASH runs snakemake with the `--keep-going (-k)` flag, which means that
if any job fails, non-dependent jobs will continue to be run. After every 
antiSMASH run is attempted, the tabulation jobs will fail (due to missing inputs),
and multiSMASH will exit.

To have multiSMASH exit on the first job failure, remove `--keep-going` 
from the configuration `snakemake_flags`.

To have multiSMASH run tabulation and/or BiG-SCAPE even after job failure(s),
set the configuration `antismash_accept_failure: True`. **Note: An empty 
`<genome>/<genome>.gbk` file will be created.** A record of failed jobs 
will appear in the `antismash_errors.log` file, but those genomes will not appear 
in the tabulated outputs.

### Tabulating existing antiSMASH results
multiSMASH can also work with existing antiSMASH results. 
For a collection of antiSMASH result folders like this:
```
├── antismash_results
│   ├── genome_1
|   │   ├── genome_1.json
|   │   ├── genome_1.gbk
|   │   └── ...
│   ├── genome_2
|   │   ├── genome_2.json
|   │   ├── genome_2.gbk
|   │   └── ...
│   ├── ...
```
Set the `in_dir` configuration to `[path/to/]antismash_results` and leave
the `in_ext` configuration blank. All other configurations can be used normally,
and any antiSMASH-related configurations will be ignored.

### GFF3 gene annotations
multiSMASH can accept paired fasta / GFF3 inputs (the antiSMASH flag `genefinding-gff3`)
as of v0.4.0.  If the `antismash_annotation_ext` configuration is set, each fasta file must be 
accompanied by a GFF3 file with the same directory and stem. For example,
with the following configurations, if multiSMASH finds `path/to/example.fa`, 
it also requires `path/to/example.gff`.
```
in_dir: path/to
in_ext: fa
antismash_annotation_ext: gff
```

## Standalone scripts

The following standalone scripts are available in `workflow/scripts`:

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

Example TSV output: (prettified)
```
|file            |record_id   |region|start   |end     |contig_edge|product                         |KCB_hit        |KCB_acc    |KCB_sim |record_desc                                                             |
|----------------|------------|------|--------|--------|-----------|--------------------------------|---------------|-----------|--------|------------------------------------------------------------------------|
|GCF_000008865.2 |NC_002695   |1     |675813  |730768  |False      |NRP-metallophore / NRPS         |enterobactin   |BGC0002476 |high    |Escherichia coli O157:H7 str. Sakai DNA, complete genome                |
|GCF_000008865.2 |NC_002695   |2     |1069983 |1096276 |False      |thiopeptide                     |               |           |        |Escherichia coli O157:H7 str. Sakai DNA, complete genome                |
|GCF_000008865.2 |NC_002695   |3     |1289425 |1299677 |False      |RiPP-like                       |               |           |        |Escherichia coli O157:H7 str. Sakai DNA, complete genome                |
|GCF_000008865.2 |NC_002695   |4     |1338879 |1381438 |False      |arylpolyene                     |               |           |        |Escherichia coli O157:H7 str. Sakai DNA, complete genome                |
|GCF_000008865.2 |NC_002695   |5     |4324109 |4367697 |False      |arylpolyene                     |APE Ec         |BGC0000836 |high    |Escherichia coli O157:H7 str. Sakai DNA, complete genome                |
|GCF_000407825.1 |NZ_KE136672 |1     |210696  |236988  |False      |thiopeptide                     |               |           |        |Escherichia coli KTE19 acHaZ-supercont1.1, whole genome shotgun sequence|
|GCF_000407825.1 |NZ_KE136672 |2     |378726  |422314  |False      |arylpolyene                     |aryl polyenes  |BGC0002008 |high    |Escherichia coli KTE19 acHaZ-supercont1.1, whole genome shotgun sequence|
|GCF_000407825.1 |NZ_KE136674 |1     |7576    |19112   |True       |RiPP-like                       |microcin L     |BGC0000588 |low     |Escherichia coli KTE19 acHaZ-supercont1.3, whole genome shotgun sequence|
|GCF_000407825.1 |NZ_KE136675 |1     |556378  |619578  |False      |NRP-metallophore / NRPS / T1PKS |yersiniabactin |BGC0001055 |low     |Escherichia coli KTE19 acHaZ-supercont1.4, whole genome shotgun sequence|
|GCF_000407825.1 |NZ_KE136675 |2     |3924573 |3979528 |False      |NRP-metallophore / NRPS         |enterobactin   |BGC0002476 |high    |Escherichia coli KTE19 acHaZ-supercont1.4, whole genome shotgun sequence|
|GCF_000005845.2 |NC_000913   |1     |594156  |649297  |False      |NRP-metallophore / NRPS         |enterobactin   |BGC0002476 |high    |Escherichia coli str. K-12 substr. MG1655, complete genome              |
|GCF_000005845.2 |NC_000913   |2     |940339  |966632  |False      |thiopeptide                     |               |           |        |Escherichia coli str. K-12 substr. MG1655, complete genome              |
```

### count_regions.py
Given a bunch of antismash results, count the BGC regions
```text
usage: count_regions.py [-h] [--contig] [--hybrid] asdir outpath

positional arguments:
  asdir       directory containing antiSMASH directories
  outpath     desired path+name for the output TSV

options:
  -h, --help  show this help message and exit
  --by_contig      count regions per each individual contig rather than per assembly
  --split_hybrids  count each hybrid region multiple times, once for each constituent 
                   BGC class. The total_count column is unaffected.
```

Example TSV output (prettified):

```
|record                  |total_count|RiPP-like|arylpolyene|thiopeptide|hybrid|description                                                                               |
|------------------------|-----------|---------|-----------|-----------|------|------------------------------------------------------------------------------------------|
|GCF_000008865.2.gbff.gz |5          |1        |2          |1          |1     |Escherichia coli O157:H7 str. Sakai DNA, complete genome [3 total records]                |
|GCF_000407825.1.gbff.gz |5          |1        |1          |1          |2     |Escherichia coli KTE19 acHaZ-supercont1.1, whole genome shotgun sequence [5 total records]|
|GCF_000005845.2.gbff.gz |2          |0        |0          |1          |1     |Escherichia coli str. K-12 substr. MG1655, complete genome [1 total record]               |
```

## antiSMASH 7 installation protocol
Here's my recipe for an antiSMASH 7 conda environment that is multiSMASH-compatible.
See [the official antiSMASH documentation](https://docs.antismash.secondarymetabolites.org/install/) 
 for more installation options. 

```bash
# Create the environment. Conda should work too, but mamba is faster
# Python must be v3.9+ (current dev version requires 3.11+)
mamba create -n antismash7 python=3.10
mamba activate antismash7

# Install dependencies
mamba install -c bioconda hmmer2 hmmer diamond fasttree prodigal glimmerhmm

# Download and install antiSMASH v7.1
# Get different versions by changing the branch: https://github.com/antismash/antismash/branches/all
git clone --branch 7-1-stable https://github.com/antismash/antismash.git antismash7   
cd antismash7
pip install .
```
If you encounter the `pip` error `Cargo, the Rust package manager, is not installed or is not on PATH`, use [rustup](https://doc.rust-lang.org/cargo/getting-started/installation.html) to install it:
```
curl https://sh.rustup.rs -sSf | sh
```

**Becoming a MEME queen**

The reason antiSMASH 7 is not one-line conda installable is that it 
requires `meme<=4.11.2`, which doesn't play well with the other dependencies. 
You will have to install the old version of meme suite separately and direct
 antiSMASH to the binaries for `meme` and `fimo`. 

You can create a separate conda environment just for the old meme version,
then tell antiSMASH permanently where to find the binaries using the antiSMASH
config file:
```bash
# Or if you have a working antSMASH v6 environment, just activate that instead
mamba create --name meme_4.11.2 -c bioconda meme=4.11.2
mamba activate meme_4.11.2

# Permanently tell antiSMASH v7 where to find the executables
echo "executable-paths meme=$(which meme),fimo=$(which fimo)" >> ~/.antismash7.cfg

# Return to antismash environment
mamba activate antismash7
```

Finally, download the various databases that antiSMASH requires:
```bash
download-antismash-databases
```
OR if they're already downloaded, tell antiSMASH where to find them:
```bash
echo "databases /path/to/antismash-databases" >> ~/.antismash7.cfg
```

Test your installation:
```bash
# Should return "All prerequisites satisfied"
antismash --check-prereqs
```

## Funding and Acknowledgements
I am currently developing/maintaining multiSMASH in my spare time. 
The workflow was conceived while working with Marnix H. Medema at 
the Wageningen University & Research Bioinformatics Group, 
supported by his European Research Council Starting Grant (948770-DECIPHER).

Thanks to Simon Shaw and Kai Blin for answering many antiSMASH questions.

## Citing multiSMASH
If you find multiSMASH useful, please cite the Zenodo DOI: [10.5281/zenodo.8276143](https://zenodo.org/doi/10.5281/zenodo.8276143)
