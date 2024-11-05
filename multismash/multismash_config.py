from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from snakemake.logging import logger


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="multismash-config",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        # usage="%(prog)s [-h] [path]",
        description="Convenience function for generating a new config file.",
        epilog="The copied template config file can be found in the "
        "multiSMASH directory: 'workflow/config/config-template.yaml'",
    )

    parser.add_argument(
        "destination",
        type=Path,
        nargs="?",
        default="config.yaml",
        help="Default path: config.yaml",
    )

    return parser.parse_args()


def main():
    args = parse_args()
    destination_path = args.destination.resolve()

    source_path = (
        Path(__file__).resolve().parent.parent
        / "workflow"
        / "config"
        / "config-template.yaml"
    )

    destination_dir = destination_path.parent
    destination_dir.mkdir(parents=True, exist_ok=True)

    shutil.copyfile(source_path, destination_path)
    logger.info(f"Config file copied to {args.destination}")


if __name__ == "__main__":
    main()
