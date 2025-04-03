from __future__ import annotations

import subprocess
from pathlib import Path

import yaml
from snakemake.utils import validate


def build_snakemake_command(
    configfile: Path, snakemake_args: list[str] | None = None
) -> list[str]:
    if snakemake_args:
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

    with Path.open(configfile) as yml:
        configs = yaml.safe_load(yml)

    multismash_dir = Path(__file__).parents[1]

    # Validate the configfile
    schema = multismash_dir.joinpath("workflow", "schema", "config.schema.yaml")
    validate(configs, schema=str(schema))

    # Get Snakefile relative to this file
    snakefile = multismash_dir.joinpath("workflow", "Snakefile")

    args = [
        "snakemake",
        "--snakefile",
        str(snakefile),
        "--cores",
        str(configs["cores"]),
        "--configfile",
        str(configfile),
    ]
    if configs["snakemake_flags"]:
        args.append(configs["snakemake_flags"])

    # TODO: Only require conda if actually required
    # Destination for conda installs
    conda_dir = multismash_dir.joinpath("conda")
    conda_args = [
        "--software-deployment-method conda",
        "--conda-prefix",
        str(conda_dir),
    ]
    args.extend(conda_args)

    # Any other arguments are assumed to be for snakemake
    if snakemake_args:
        args.extend(snakemake_args)

    return args


def main(configfile: Path, snakemake_args: list[str] | None = None):
    command = build_snakemake_command(configfile, snakemake_args)

    subprocess.run(command, check=False)
