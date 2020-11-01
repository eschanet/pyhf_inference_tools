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
    type=click.Choice(["1Lbb", "2L0J", "compressed", "3Loffshell"]),
)
@click.option(
    "--output-file",
    help="The location of the output json file. If not specified, prints to screen.",
    default=None,
)
def main(group, output_file):

    pattern = re.compile("^/channels/[0-9]+/samples/[0-9]+$")

    ws = pyhf.Workspace(json.load(open(pathlib.Path(f"./analyses/{group}/likelihoods/BkgOnly.json"), "r")))
    patchset = pyhf.PatchSet(json.load(open(pathlib.Path(f"./analyses/{group}/likelihoods/patchset.json"), "r")))

    simplified_patchset = {}
    simplified_patchset['metadata'] = patchset.metadata
    simplified_patchset['version'] = patchset.version
    simplified_patchset['patches'] = []
    for patch in patchset:

        simplified_patch = {}
        simplified_patch['metadata'] = patch.metadata
        simplified_patch['patch'] = []
        
        print(patch.name)
        
        for p in patch.patch:
            # we only need to grab patches that add signal yields
            if not pattern.match(p['path']) or not p['op'] == 'add':
                continue
            p['value']['modifiers'] = [
                {
                    "data": None,
                    "name": "lumi",
                    "type": "lumi"
                },
                {
                    "data": None,
                    "name": "mu_Sig",
                    "type": "normfactor"
                }
            ]
            p['path'] = p['path'].split('samples/')[0]+'samples/1'
            simplified_patch['patch'].append(
                p
            )
        simplified_patchset['patches'].append(simplified_patch)

    if output_file is None:
        click.echo(json.dumps(simplified_patchset, indent=4, sort_keys=True))
    else:
        with open(output_file, "w+") as out_file:
            json.dump(simplified_patchset, out_file, indent=4, sort_keys=True)
        click.echo("Written to {0:s}".format(output_file))



if __name__ == "__main__":
    main()
