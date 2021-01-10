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

def timing(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        print('func:%r args:[%r, %r] took: %2.4f sec' % (f.__name__, args, kw, te-ts))
        return result
    return wrap

def string_to_float(string):
    return float(string.replace("p", "."))

@timing
def run_fit(filename, prune_channel, prune_modifier, prune_modifier_type, prune_sample):
    ws = pyhf.Workspace(json.load(open(pathlib.Path(str(filename)), "r")))
    ws = ws.prune(modifiers=prune_modifier,modifier_types=prune_modifier_type,samples=prune_sample,channels=prune_channel)

    pdf = ws.model(
        modifier_settings={
            'normsys': {
                'interpcode': 'code4'
            },
            'histosys': {
                'interpcode': 'code4p'
            }
        }
    )

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
def main(group, simplified, backend, prune_channel, prune_modifier, prune_modifier_type, prune_sample, optimizer, skip_to, include):

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
        
        print(filename)
        
        try:
            obsCLs, expCLs = run_fit(filename, prune_channel, prune_modifier, prune_modifier_type, prune_sample)
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

if __name__ == "__main__":
    main()
