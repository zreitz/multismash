import shlex
import subprocess

def check_antismash():
    print("Checking antiSMASH installation... ", end = "")
    # build command
    command = [
        snakemake.config["antismash_command"],
        "--check-prereqs"
        ]
    # Add any additional flags in case they're needed for the check
    # E.g. --databases, --executable-paths
    if snakemake.config["antismash_flags"]:
        command.extend(shlex.split(snakemake.config["antismash_flags"]))

    output = subprocess.run(command, capture_output=True)
    if output.returncode != 0:
        print(f"FAIL\n{output.stderr.decode()}")
        exit(1)

    print("OK")
    # Touch the ok file
    open(snakemake.output[0], 'a').close()

check_antismash()