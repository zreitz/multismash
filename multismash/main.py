import argparse
import subprocess
import textwrap
import yaml

from pathlib import Path
from snakemake.utils import validate
from typing import List, Tuple


def parse_args() -> Tuple[argparse.Namespace, List[str]]:
    parser = argparse.ArgumentParser(
        prog="multismash",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        usage="%(prog)s [-h] configfile [--cores CORES] [...]",
        description=textwrap.dedent("""\
            multiSMASH is a Snakemake-based antiSMASH wrapper that streamlines 
            large-scale analyses of BGCs across multiple genomes."""),
        epilog=textwrap.dedent("""\
            Any additional arguments will be passed to Snakemake. Use `snakemake -h`
            to see all available parameters. Flags you may find useful:
              --dry-run, -n   Do not execute anything, and display what would be done
              --quiet, -q     Do not output any progress or rule information
              --forceall, -F  Force the (re-)execution of all rules 
            """)
    )

    parser.add_argument("configfile", type=str,
                        help="path to the YAML file with job configurations")

    return parser.parse_known_args()


def install_bigscape(configs):
    # If a bigscape environment isn't defined then download the repository
    conda_dir = Path(__file__).parents[1] / "conda"
    bigscape_dir = conda_dir / "BiG-SCAPE-1.1.5"
    if not configs["bigscape_conda_env_name"] and not bigscape_dir.exists():
        conda_dir.mkdir(exist_ok=True)
        tar = Path(str(bigscape_dir) + ".tar.gz")
        if not tar.exists():
            input(f"BiG-SCAPE will be downloaded to {bigscape_dir}/. Press Enter to continue.")
            url = "https://github.com/medema-group/BiG-SCAPE/archive/refs/tags/v1.1.5.tar.gz"
            subprocess.run(["curl", url, "-L", "-o", tar], check=True)
        subprocess.run(["tar", "-xzf", tar, "-C", conda_dir], check=True)
        assert(bigscape_dir.exists())
        tar.unlink()    # Delete

    # check if the Pfam files exist, and if not, download them
    pfam_dir = configs["pfam_dir"]
    if pfam_dir:
        pfam = Path(args.configfile).parents[0] / Path(pfam_dir)
        pfam = pfam.expanduser().resolve()
    else:
        pfam = Path(__file__).parents[1] / "pfam"
    files = [pfam / ("Pfam-A.hmm" + ext) for ext in ["", ".gz", ".h3f", ".h3i", ".h3m", ".h3p"]]

    # Only download if needed and after prompt
    if not files[0].exists():  # Pfam-A.hmm
        if not files[1].exists():  # Pfam-A.hmm.gz
            Path.mkdir(pfam, exist_ok=True)
            print("Downloading the Pfam database from EBI...")
            url = "https://ftp.ebi.ac.uk/pub/databases/Pfam/current_release/Pfam-A.hmm.gz"
            subprocess.run(["curl", "-o", files[1], url], check=True)
        subprocess.run(["gunzip", files[1]], check=True)

    if not all((file.exists() for file in files[2:])):
        print("Pressing the Pfam database...")
        subprocess.run(["hmmpress", files[0]], check=True)
        print("Done")


def main():
    args, snakemake_args = parse_args()

    forbidden = {"--snakefile", "--cores", "--use-conda", "--configfile", "--conda-prefix"}
    forbidden = forbidden.intersection(set(snakemake_args))
    if forbidden:
        raise SystemExit(f"Error: multiSMASH automatically sets the following flag"
                         f"{'s' if len(forbidden) > 1 else ''}: {' '.join(forbidden)}")

    with open(args.configfile) as yml:
        configs = yaml.safe_load(yml)

    multismash_dir = Path(__file__).parents[1]

    # Validate the configfile
    schema = multismash_dir.joinpath("workflow", "schema", "config.schema.yaml")
    validate(configs, schema=str(schema))

    if configs["run_bigscape"]:
        install_bigscape(configs)

    # Get Snakefile relative to this file
    snakefile = multismash_dir.joinpath("workflow", "Snakefile")

    # Always install conda envs in the same location
    conda_dir = multismash_dir.joinpath("conda")

    args = ["snakemake",
            "--snakefile", snakefile,
            "--cores", str(configs["cores"]),
            "--use-conda",
            "--configfile", args.configfile,
            "--conda-prefix", conda_dir
            ]
    if configs["snakemake_flags"]:
        args.append(configs["snakemake_flags"])
    args.extend(snakemake_args)
    subprocess.run(args)


if __name__ == "__main__":
    main()
