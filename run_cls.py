#!/usr/bin/env python
import click
import pathlib
import subprocess
import re
import pyhf
import json

from functools import wraps
from time import time

pattern = re.compile("(\d+(?:p[05])?)_(\d+(?:p[05])?)")

total_time = []

def timeit(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        start = time()
        result = f(*args, **kwargs)
        end = time()
        total_time.append((end - start))
        return result
    return wrapper

def string_to_float(string):
    return float(string.replace("p", "."))

@timeit
def create_ws(filename, prune_channel, prune_modifier, prune_modifier_type, prune_sample):
    ws = pyhf.Workspace(json.load(open(pathlib.Path(str(filename)), "r")))
    ws = ws.prune(modifiers=prune_modifier,modifier_types=prune_modifier_type,samples=prune_sample,channels=prune_channel)
    return ws

@timeit
def create_pdf(ws):
    return ws.model(
        modifier_settings={
            'normsys': {
                'interpcode': 'code4'
            },
            'histosys': {
                'interpcode': 'code4p'
            }
        }
    )

@timeit
def run_fit(ws, pdf):
    obsCLs, expCLs = pyhf.infer.hypotest(
        1.0, ws.data(pdf), pdf, qtilde=True, return_expected_set=True
    )
    return (obsCLs, expCLs)
    

@click.command()
@click.option(
    "--group",
    default="1Lbb",
    type=click.Choice(["1Lbb", "2L0J", "compressed", "3Loffshell"]),
)
@click.option('--simplified/--no-simplified', default=False)
@click.option('--benchmark/--no-benchmark', default=False)
@click.option("--backend", default="pytorch")
@click.option(
    '--prune-channel',
    default=[],
    multiple=True,
    help="Channel to prune",
)
@click.option(
    '--prune-modifier',
    default=[],
    multiple=True,
    help="Modifier to prune",
)
@click.option(
    '--prune-modifier-type',
    default=[],
    multiple=True,
    help="Modifier type to prune",
)
@click.option(
    '--prune-sample',
    default=[],
    multiple=True,
    help="Modifier to prune",
) 
@click.option("--optimizer", default="scipy")
@click.option("--skip-to", default=None)
@click.option("--include", default=None)
def main(group, simplified, benchmark, backend, prune_channel, prune_modifier, prune_modifier_type, prune_sample, optimizer, skip_to, include):

    pyhf.set_backend(backend, optimizer)

    found = False
    wildcard = "*.json" if not include else include
    filenames = pathlib.Path(f"./analyses/{group}/workspaces/").glob(wildcard)

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
        
        if not benchmark:
            click.echo(filename)
        
        try:
            ws = create_ws(filename, prune_channel, prune_modifier, prune_modifier_type, prune_sample)
            pdf = create_pdf(ws)
            obsCLs, expCLs = run_fit(ws, pdf)
            with open(
                pathlib.Path(
                    f"analyses/{group}/results/{'simplified_' if simplified else ''}{group}_{match.group(1)}_{match.group(2)}.json"
                ), "w"
            ) as fp:
                json.dump(
                    {
                        "CLs_exp": [float(i.tolist()) for i in expCLs],
                        "CLs_obs": obsCLs.tolist()
                    }, fp
                )
        except Exception as e:
            print(e)
        
        total_time.insert(0,sum(total_time))
        if benchmark:
            print(*total_time, sep = " ")
        total_time.clear()

if __name__ == "__main__":
    main()
