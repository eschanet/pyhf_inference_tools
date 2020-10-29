#!/usr/bin/env python
import click
import pathlib
import subprocess
import re

pattern = re.compile("(\d+(?:p[05])?)_(\d+(?:p[05])?)")

def string_to_float(string):
    return float(string.replace("p", "."))

@click.command()
@click.option(
    "--group",
    default="1Lbb",
    type=click.Choice(["1Lbb", "2L0J", "compressed"]),
)
@click.option('--simplified/--no-simplified', default=False)
@click.option("--backend", default=None)
@click.option("--optimizer", default=None)
@click.option("--skip-to", default=None)
def main(group, simplified, backend, optimizer, skip_to):
    found = False
    filenames = pathlib.Path(f"./analyses/{group}/workspaces/").glob("*.json")
    for filename in filenames:
        if not skip_to:
            found = True
        else:
            if skip_to in filename.name:
                found = True
                continue
            if not found:
                continue
        match = pattern.search(filename.name)
        assert match
        masses = string_to_float(match.group(1)), string_to_float(match.group(2))
        cmd = [
            "time", "pyhf", "cls",
            str(filename), *(["--backend", backend] if backend else []),
            *(["--optimizer", optimizer] if optimizer else []),
            "--output-file",
            f"analyses/{group}/results/{'simplified_' if simplified else ''}{group}_{masses[0]}_{masses[1]}".replace(".", "p") + ".json"
        ]
        print(" ".join(cmd))
        print(subprocess.check_output(cmd))


if __name__ == "__main__":
    main()


