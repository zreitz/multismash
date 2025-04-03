from __future__ import annotations

import subprocess
from pathlib import Path

import yaml
from snakemake.logging import logger
from snakemake.utils import validate


def main(configfile: Path, snakemake_args: list[str]):
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

    # Only set conda flags if it's needed
    if any((configs["run_bigscape"], configs["antismash_conda_env_name"])):
        # Destination for conda installs
        conda_dir = multismash_dir.joinpath("conda")
        conda_args = [
            "--use-conda",
            "--conda-prefix",
            str(conda_dir),
        ]
        args.extend(conda_args)

    # Any other arguments are assumed to be for snakemake
    args.extend(snakemake_args)

    logger.info(f"Running multiSMASH with {configs['cores']} cores")
    subprocess.run(args, check=False)
