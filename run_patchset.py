#!/usr/bin/env python
import click
import copy
import pathlib
import subprocess
import re
import json
import jsonpatch
import numpy as np

import pyhf

from time import time
from functools import wraps


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

def recursive_iter(obj):
    if isinstance(obj, dict):
        for item in obj.values():
            yield from recursive_iter(item)
    elif any(isinstance(obj, t) for t in (list, tuple)):
        for item in obj:
            yield from recursive_iter(item)
    else:
        yield obj

def get_only_bin(spec, n):
    channels = copy.deepcopy(spec["channels"])
    measurements = copy.deepcopy(spec["measurements"])
    observations = copy.deepcopy(spec["observations"])

    for channel in channels:
        for sample in channel:
            for data in sample["data"][:-1]:
                del data
            for modifier in sample["modifiers"]:
                for key in modifier["data"].keys():
                    for data in modifier[key][:-1]:
                        del data
    

    for observation in observations:
        for data in observation["data"][:-1]:
            del data

    return {"channels": channels, measurements: "measurements", observations: "observations"}
        

@timeit
def run_single_point(spec, patch):
    patched_spec = jsonpatch.apply_patch(spec, patch)  
    ws = pyhf.Workspace(patched_spec)
    # ws = ws.prune(modifiers=prune_modifier,modifier_types=prune_modifier_type,samples=prune_sample,channels=prune_channel)
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

    return (obsCLs,expCLs)
        


@click.command()
@click.option(
    "--group",
    default="1Lbb",
    type=click.Choice(["1Lbb", "2L0J", "compressed", "3Loffshell", "stop1L", "3LRJR", "directstaus", "samesign", "sbottom"]),
)
@click.option('--simplified/--no-simplified', default=False)
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
@click.option("--likelihood", default="BkgOnly.json")
@click.option("--patchset", default="patchset.json")
@click.option("--backend", default="numpy")
@click.option("--optimizer", default=None)
@click.option("--skip-to", default=None)
@click.option('--benchmark/--no-benchmark', default=False)

def main(group, simplified, prune_channel, prune_modifier, prune_modifier_type, prune_sample, likelihood, patchset, backend, optimizer, skip_to, benchmark):

    pyhf.set_backend(backend, optimizer)

    bkgOnly = likelihood if not simplified else "simplified_" + likelihood
    patchset = patchset if not simplified else "simplified_" + patchset

    spec = json.load(
        open(
            pathlib.Path(f"./analyses/{group}/likelihoods/{bkgOnly}"), "r"
        )
    )
  
  
    patchset = pyhf.PatchSet(
        json.load(
            open(
                pathlib.Path(f"./analyses/{group}/likelihoods/{patchset}"), "r"
            )
        )
    )

    for patch in patchset.patches:
        try:            
            obsCLs, expCLs = run_single_point(spec, patch)
            
            # click.echo({
            #             "CLs_exp": [float(i.tolist()) for i in expCLs],
            #             "CLs_obs": obsCLs.tolist()
            #         })
            with open(
                pathlib.Path(
                    f"analyses/{group}/results/{'simplified_' if simplified else ''}{group}_{patch.name}.json"
                ), "w"
            ) as fp:
                json.dump(
                    {
                        "CLs_exp": [float(i.tolist()) for i in expCLs],
                        "CLs_obs": obsCLs.tolist()
                    }, fp
                )
            

            if benchmark:
                print(*total_time, sep = " ")
            total_time.clear()


        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()
