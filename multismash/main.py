import argparse
import textwrap
import subprocess
from pathlib import Path
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


def main():
    args, snakemake_args = parse_args()

    if "--configfile" in snakemake_args:
        raise SystemExit("Error: do not use the --configfile flag with multiSMASH")

    # Get Snakefile relative to this file
    snakefile = Path(__file__).parents[1].joinpath("workflow", "Snakefile").resolve()

    # We need cores from the config file for snakemake
    with open(args.configfile) as f:
        line = next((l for l in f if l.startswith("cores:")), None)
    try:
        cores = str(int(line.strip().split(":")[1]))    # Ensure int
    except (IndexError, AttributeError, ValueError) as e:
        raise SystemExit(
            textwrap.dedent("Error: specify the maximum number of CPU cores to "
                            "be used at the same time in the config file, with "
                            "a line such as `cores: 1`")) from e


    args = ["snakemake",
            "--snakefile", snakefile,
            "--cores", cores,
            "--use-conda",
            "--configfile", args.configfile]

    args.extend(snakemake_args)
    subprocess.run(args)


if __name__ == "__main__":
    main()
