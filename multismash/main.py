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
            input(f"BiG-SCAPE will be downloaded and installed to {bigscape_dir}/. Press Enter to continue.")
            url = "https://github.com/medema-group/BiG-SCAPE/archive/refs/tags/v1.1.5.tar.gz"
            try:
                subprocess.run(["curl", url, "-L", "-o", tar], check=True)
            except (KeyboardInterrupt, Exception) as e:
                print(f"\n\n{type(e).__name__} detected: removing partial file")
                subprocess.run(["rm", "-f", tar])
                raise e
        subprocess.run(["tar", "-xzf", tar, "-C", conda_dir], check=True)
        assert(bigscape_dir.exists())
        tar.unlink()    # Delete


def main():
    args, snakemake_args = parse_args()

    # Catch problematic flags
    forbidden = {"--snakefile", "--cores", "--use-conda", "--configfile", "--conda-prefix"}
    forbidden = forbidden.intersection(set(snakemake_args))
    if forbidden:
        raise SystemExit(f"Error: multiSMASH automatically sets the following flag"
                         f"{'s' if len(forbidden) > 1 else ''}: {' '.join(forbidden)}")
    if "--reuse-results" in snakemake_args:
        raise SystemExit(f"Error: instead of using --reuse-results, set the "
                         "antismash_reuse_results flag to be True")

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

    print(f"Running multiSMASH with {configs['cores']} cores")
    subprocess.run(args)


if __name__ == "__main__":
    main()
