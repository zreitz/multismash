from __future__ import annotations

import shutil
from pathlib import Path

from snakemake.logging import logger


def get_template():
    return (
        Path(__file__).resolve().parent.parent
        / "workflow"
        / "config"
        / "config-template.yaml"
    )


def main(destination: Path):
    source_path = get_template()

    destination_dir = destination.parent
    destination_dir.mkdir(parents=True, exist_ok=True)

    shutil.copyfile(source_path, destination)
    logger.info(f"Config file copied to {destination}")


if __name__ == "__main__":
    main()
