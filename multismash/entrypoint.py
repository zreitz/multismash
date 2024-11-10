from __future__ import annotations

import importlib.metadata
from pathlib import Path
from typing import Annotated

import typer
from snakemake import logging
from typer.core import TyperGroup

import multismash.copy_config
import multismash.count
import multismash.overview
import multismash.workflow


class OrderCommands(TyperGroup):
    def list_commands(self, _):
        return list(self.commands)


app = typer.Typer(
    help="multiSMASH: an antiSMASH wrapper that streamlines large-scale analyses",
    context_settings={"help_option_names": ["-h", "--help"]},
    add_completion=False,
    pretty_exceptions_enable=False,
    no_args_is_help=True,
    cls=OrderCommands,
)

typer.rich_utils.STYLE_REQUIRED_LONG = "red"
typer.rich_utils.STYLE_OPTIONS_PANEL_BORDER = ""
typer.rich_utils.STYLE_COMMANDS_PANEL_BORDER = ""
typer.rich_utils.STYLE_ERRORS_SUGGESTION = ""
typer.rich_utils.STYLE_HELPTEXT = ""


def version_callback(version: bool):
    if version:
        logging.logger(importlib.metadata.version("multiSMASH"))
        raise typer.Exit()


@app.callback(epilog="See `multismash [command] -h` for more details")
def common(
    version: bool = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Print the installed version and exit.",
    ),
):
    pass


# appeasing ruff while avoiding the metavar bug in typer
unknown_default = typer.Option(None)


@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
    epilog="""\
        Any additional flags will be passed to Snakemake. Use `snakemake -h`\n
        to see all available parameters. Some flags you may find useful:\n
            --dry-run, -n   Do not execute anything, and display what would be done\n
            --quiet, -q     Do not output any progress or rule information\n
            --forceall, -F  Force the (re-)execution of all rules""",
)
def run(
    config: Annotated[
        Path,
        typer.Argument(
            show_default=False,
            help="YAML file with job configurations",
            exists=True,
            readable=True,
        ),
    ],
    unknown_args: typer.Context = unknown_default,
):
    """
    Run a Snakemake-based workflow according to a configuration file

    A template config file can be created with `multismash init`
    """
    multismash.workflow.main(config, unknown_args.args)


# init: make a config file
def where_callback(where: bool):
    if where:
        logging.logger(multismash.copy_config.get_template())
        raise typer.Exit()


# appeasing ruff while avoiding the metavar bug in typer
dest_default = typer.Argument("config.yaml", metavar="DESTINATION", help="")


@app.command()
def init(
    destination: Annotated[Path | None, None] = dest_default,
    _where: Annotated[
        bool | None,
        typer.Option(
            "--where",
            help="Show the path to the template YAML and exit.",
            callback=where_callback,
            is_eager=True,
        ),
    ] = None,
):
    """
    Generate a new YAML config file from a template
    """
    multismash.copy_config.main(destination)


@app.command()
def overview(
    asdir: Annotated[
        Path,
        typer.Argument(show_default=False, help="Directory containing aS directories"),
    ],
    outpath: Annotated[
        Path,
        typer.Argument(show_default=False, help="Location to write the output TSV"),
    ],
):
    """
    Generate a table of BGCs from a directory of aS results
    """
    multismash.overview.main(asdir, outpath)


@app.command()
def count(
    asdir: Annotated[
        Path,
        typer.Argument(show_default=False, help="Directory containing aS directories"),
    ],
    outpath: Annotated[
        Path,
        typer.Argument(show_default=False, help="Location to write the output TSV"),
    ],
    by_contig: Annotated[
        bool,
        typer.Option(
            "--by-contig",
            help="count regions per each individual contig rather than per aS run",
        ),
    ] = False,
    split_hybrid: Annotated[
        bool,
        typer.Option(
            "--split-hybrids",
            help="Count each hybrid region multiple times, once for each constituent BGC class. The total_count column is unaffected",
        ),
    ] = False,
):
    """
    Generate a summary table of per-genome BGC counts from aS results
    """
    multismash.count.main(asdir, outpath, by_contig, split_hybrid)


if __name__ == "__main__":
    app()
