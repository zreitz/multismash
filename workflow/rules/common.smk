from pathlib import Path
from datetime import datetime

def build_paths():
    paths = {}
    # Convert to pure paths, expand home directory (~/), and make relative to config
    # For absolute paths, config_dir is ignored
    config_dir = Path(workflow.configfiles[0]).parent
    paths["IN_DIR"] = Path.resolve(config_dir / Path(config["in_dir"]).expanduser())
    paths["OUT_DIR"] = Path.resolve(config_dir / Path(config["out_dir"]).expanduser())

    # Antismash in/out
    if not config["in_ext"]:
        paths["AS_DIR"] = paths["IN_DIR"]
    else:
        paths["AS_DIR"]  = paths["OUT_DIR"] / "antismash"

    # Tabulation
    paths["COUNT"] = Path(workflow.basedir) / "scripts" / "count_regions.py"
    paths["TABULATE"] = Path(workflow.basedir) / "scripts" / "tabulate_regions.py"

    # Out directory for bigscape
    paths["BIG_DIR"] = paths["OUT_DIR"] / "bigscape"
    # Pfam directory for bigscape
    pfam = config["pfam_dir"]
    if pfam:
        paths["PFAM_DIR"] = Path.resolve(config_dir / Path(pfam).expanduser())
    else:
        paths["PFAM_DIR"] = Path(workflow.basedir).parent / "pfam"

    # Timestamped directory for logging
    paths["LOG_DIR"] = paths["OUT_DIR"] / "log" / datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    return paths


## Get wildcards

def get_samples(paths):
    in_dir = paths["IN_DIR"]
    IN_EXT = config["in_ext"]
    # antismash results as input
    if not IN_EXT:
        GENOMES, trash = glob_wildcards(f"{in_dir}/{{genome}}/{{trash}}.json")
        print(f"{len(GENOMES)} antiSMASH results found")

    # genome files as input
    else:
        GENOMES, = glob_wildcards(f"{in_dir}/{{genome}}.{IN_EXT}")
        print(f"{len(GENOMES)} {IN_EXT} files found")
        gff = config["antismash_annotation_ext"]
        if gff:
            expected = expand(f"{paths['IN_DIR']}/{{genomes}}.{gff}", genomes = GENOMES)
            missing = [p for p in expected if not Path.exists(Path(p))]
            if missing:
                raise OSError(f"Error! Unable to find {len(missing)} expected annotation files "
                          f"with the extension '{gff}'.\n\tFirst missing file: {missing[1]}")

    if not GENOMES:
        raise OSError(f"Error! Unable to find files in '{in_dir}' "
                      f"with extension '{IN_EXT}'.")

    return GENOMES


def get_bigscape_env():
    env = config["bigscape_conda_env_name"]
    # An environment was created
    if not env:
        env = "envs/bigscape.yaml"

    command = config["bigscape_command"]
    if not command:
        command = Path(workflow.basedir).parent / "conda" / "BiG-SCAPE-1.1.5" / "bigscape.py"
        command = f"python {command}"

    pfam = config["pfam_dir"]
    # Use antismash functions to find and validate the Pfam directory
    if not pfam:
        exit_message = "Unable to locate Pfam-A.hmm. Please set the 'pfam_dir' " \
                       "flag in the configuration file."
        try:
            from antismash.config import build_config
            from antismash.common.pfamdb import get_latest_db_path, ensure_database_pressed
        except ImportError:
            raise SystemExit(exit_message)
        try:
            pfam = get_latest_db_path(build_config([]).database_dir)
        except ValueError:
            raise SystemExit(exit_message)

        pfam = pfam.replace("Pfam-A.hmm", "")   # We want the directory

    return env, command, pfam


def get_inputs_for_all(paths):
    out_dir = paths["OUT_DIR"]
    inputs = []
    if config["run_tabulation"]:
        inputs.extend((
            # tabulate_regions
            f"{out_dir}/all_regions.tsv",
            # count_regions
            f"{out_dir}/region_counts.tsv"
        ))
    # bigscape
    if config["run_bigscape"]:
        big_dir = paths["BIG_DIR"]
        if config["zip_bigscape"]:
            inputs.append(f"{big_dir}.tar.gz")
        else:
            inputs.append(f"{big_dir}/index.html")
    return inputs