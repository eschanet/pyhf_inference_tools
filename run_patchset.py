#!/usr/bin/env python
import click
import pathlib
import subprocess
import re
import json
import numpy as np

import pyhf

pattern = re.compile("(\d+(?:p[05])?)_(\d+(?:p[05])?)")

def string_to_float(string):
    return float(string.replace("p", "."))

@click.command()
@click.option(
    "--group",
    default="1Lbb",
    type=click.Choice(["1Lbb", "2L0J", "compressed"]),
)
@click.option("--backend", default=None)
@click.option("--optimizer", default=None)
@click.option("--skip-to", default=None)
def main(group, backend, optimizer, skip_to):
    ws = pyhf.Workspace(json.load(open(pathlib.Path(f"./analyses/{group}/likelihoods/BkgOnly.json"), "r")))
    patchset = pyhf.PatchSet(json.load(open(pathlib.Path(f"./analyses/{group}/likelihoods/patchset.json"), "r")))

    for patch in patchset:
        print(patch.name)
        pdf = ws.model(
            patches = [patch], 
            modifier_settings = {'normsys': {'interpcode': 'code4'},'histosys': {'interpcode': 'code4p'}}
        )

        CLs_obs, CLs_exp_band = pyhf.infer.hypotest(
            1.0, ws.data(pdf), pdf, qtilde=True, return_expected_set=True
        )

        obsCLs, expCLs = pyhf.infer.hypotest(1.0,ws.data(pdf), pdf, qtilde=True, return_expected_set=True)
        print(obsCLs,expCLs)

        with open(pathlib.Path(f"results/{group}_{patch.name}.json"), "w") as fp:
            json.dump({"CLs_exp":[float(i.tolist()) for i in expCLs], "CLs_obs":obsCLs.tolist()}, fp)
 
if __name__ == "__main__":
    main()
