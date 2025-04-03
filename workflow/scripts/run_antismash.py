import shlex
import shutil
import subprocess
#from snakemake.script import snakemake

def build_command():
    # build command, starting with always used
    command = [
        snakemake.config["antismash_command"],
        "--output-dir", snakemake.output.out_dir,
        "-c", "1",
        "--logfile", str(snakemake.log)
        ]
    
    # Add inputs
    if snakemake.config["antismash_reuse_results"]:
        command.append("--reuse-results")
    command.append(snakemake.input.genomes)
    if snakemake.input.annotations:
        command.extend(["--genefinding-gff3", input.annotations])

    # Add any additional flags
    if snakemake.config["antismash_flags"]:
        command.extend(shlex.split(snakemake.config["antismash_flags"]))

    return(command)

def run_antismash():
    command = build_command()

    with open(snakemake.log[0], "a") as logf:
        logf.write(f"antiSMASH command:\n\t{" ".join(command)}\n")

    try:
        as_output = subprocess.run(command, capture_output=True)
    except KeyboardInterrupt as e:
        shutil.rmtree(snakemake.output.out_dir)
        raise e

    # On failure
    if as_output.returncode != 0:
        # If failure is ok, touch the output file
        if snakemake.config["antismash_accept_failure"]:
            open(snakemake.output.out_json, 'a').close()

        errorlines = as_output.stderr.decode().splitlines()
        errorlines = [l for l in as_output.stderr.decode().splitlines() 
                      if l.startswith("ERROR")]
        if not errorlines:
            errorlines = as_output.stderr.decode().splitlines() 
        with open(snakemake.params.fail_log, "a") as fail:
            fail.write(f"{snakemake.wildcards.GENOMES}\t{snakemake.input.genomes}\n")
            fail.write("\n".join(errorlines))
            fail.write("\n")
        
        print(f"{snakemake.wildcards.GENOMES}: antiSMASH exited with non-zero exit code")
        print(*errorlines, sep="\n")


run_antismash()