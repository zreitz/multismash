from __future__ import annotations

import argparse
import subprocess
import textwrap
from pathlib import Path

import yaml
from snakemake.logging import logger
from snakemake.utils import validate


def parse_args() -> tuple[argparse.Namespace, list[str]]:
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
            """),
    )

    parser.add_argument(
        "configfile", type=Path, help="path to the YAML file with job configurations"
    )

    return parser.parse_known_args()


def main():
    args, snakemake_args = parse_args()

    # Catch problematic flags
    forbidden = {
        "--snakefile",
        "--cores",
        "--use-conda",
        "--configfile",
        "--conda-prefix",
    }
    forbidden = forbidden.intersection(set(snakemake_args))
    if forbidden:
        msg = (
            f"Error: multiSMASH automatically sets the following flag"
            f"{'s' if len(forbidden) > 1 else ''}: {' '.join(forbidden)}"
        )
        raise SystemExit(msg)
    if "--reuse-results" in snakemake_args:
        msg = (
            "Error: instead of using --reuse-results, set the "
            "antismash_reuse_results flag to be True"
        )
        raise SystemExit(msg)

    with Path.open(args.configfile) as yml:
        configs = yaml.safe_load(yml)

    multismash_dir = Path(__file__).parents[1]

    # Validate the configfile
    schema = multismash_dir.joinpath("workflow", "schema", "config.schema.yaml")
    validate(configs, schema=str(schema))

    # Get Snakefile relative to this file
    snakefile = multismash_dir.joinpath("workflow", "Snakefile")

    # Always install conda envs in the same location
    conda_dir = multismash_dir.joinpath("conda")

    args = [
        "snakemake",
        "--snakefile",
        snakefile,
        "--cores",
        str(configs["cores"]),
        "--use-conda",
        "--configfile",
        args.configfile,
        "--conda-prefix",
        conda_dir,
    ]
    if configs["snakemake_flags"]:
        args.append(configs["snakemake_flags"])
    args.extend(snakemake_args)

    logger.info(f"Running multiSMASH with {configs['cores']} cores")
    subprocess.run(args, check=False)


if __name__ == "__main__":
    main()
