#!/usr/bin/env python

import click
import collections
import glob
import csv
import json
import re
import pathlib
import jsonpatch

import pyhf
pyhf.set_backend("numpy")

from xsecDB import CrossSectionDB
xsecDB = CrossSectionDB()

mass_pattern = re.compile("(\d+(?:p[05]){1})_(\d+(?:p[05]){1})")
dsid_pattern = re.compile("(\d{6}?)")

def string_to_float(string):
    return float(string.replace("p", "."))

@click.command()
@click.option(
    "--group",
    default="1Lbb",
    type=click.Choice(["1Lbb", "2L0J", "compressed", "3Loffshell"]),
)
@click.option("--backend", default="pytorch")
# @click.option(
#     '--prune-channel',
#     default=[],
#     multiple=True,
#     help="Channel to prune",
# )
# @click.option(
#     '--prune-modifier',
#     default=[],
#     multiple=True,
#     help="Modifier to prune",
# )
# @click.option(
#     '--prune-modifier-type',
#     default=[],
#     multiple=True,
#     help="Modifier type to prune",
# )
# @click.option(
#     '--prune-sample',
#     default=[],
#     multiple=True,
#     help="Modifier to prune",
# )   
@click.option("--likelihood", default="BkgOnly.json")
@click.option("--optimizer", default="scipy")
@click.option("--lumi", default=139000)
@click.option("--include", default=None)
def main(group, backend, likelihood, optimizer, lumi, include):

    pyhf.set_backend(backend, optimizer)
    spec = json.load(
        open(
            pathlib.Path(f"./analyses/{group}/likelihoods/{likelihood}"), "r"
        )
    )

    patchDef = {}
    idxCol=0
    with open(f"./analyses/{group}/truth/{group}.patch", 'r') as f:
        reader = csv.reader(f)
        patchDef = collections.OrderedDict()
        try:
            header=next(reader)
        except StopIteration:
            return {}
        for col in header: 
            if header.index(col) == idxCol: continue
            patchDef[col] = collections.OrderedDict()
        for row in reader:
            for col in range(0,len(row)):
                if col==idxCol: continue
                try:
                    patchDef[header[col]][row[idxCol]]=row[col]
                except IndexError:
                    print("Exception in %s" % csvName)
                    print("Row: ", row)
                    print("Length: %d - expected: %d" % (len(row),len(header)))
                    raise


    found = False
    wildcard = "*C1pN2*.txt" if not include else include
    filenames = pathlib.Path(f"./analyses/{group}/truth/").glob(wildcard)

    for filename in filenames:
        mass_match = mass_pattern.search(filename.name)
        assert mass_match
        masses = string_to_float(mass_match.group(1)), string_to_float(mass_match.group(2))

        dsid_match = dsid_pattern.search(filename.name)
        assert dsid_match
        dsid = string_to_float(dsid_match.group(1))
        xsec = xsecDB.xsecTimesEffTimeskFac(dsid)

        print(filename)

        expectedEvents = {}
        with open(filename) as file:
            expectedEvents = {}
            next(file) # skip header
            for l in file:
                l = l.strip().split(",")
                events = float(lumi)*xsec*float(l[2])
                statError = float(lumi)*xsec*float(l[3])
                expectedEvents[l[0]] = (events,statError)

        patches = []
        handled_channels = []
        for srName in patchDef['eff']:
            path = patchDef['jsonpath'][srName]
            expected = float(expectedEvents[srName][0])
            expected *= float(patchDef['eff'][srName])

            # channel = path.split("/data")[0]
            # if channel in handled_channels:
            #     handled_channels.append(channel)

            # else:
            #     handled_channels.append(channel)


            
            patches.append({
                "op": "add",
                "path": path.replace("/data/0",""),
                "value": {
                    "data": [
                        expected
                    ],
                    "modifiers": [
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
                    ],
                    "name": filename.stem
                },
            })

        patched_spec = jsonpatch.apply_patch(spec, patches)            
        ws = pyhf.Workspace(patched_spec)
        pdf=ws.model(modifier_settings={'normsys': {'interpcode': 'code4'},'histosys': {'interpcode': 'code4p'}})

        obsCLs, expCLs = pyhf.infer.hypotest(
            1.0, ws.data(pdf), pdf, qtilde=True, return_expected_set=True
        )
        with open(
            pathlib.Path(
                f"analyses/{group}/results/truth_{group}_{str(masses[0]).replace('.','p')}_{str(masses[1]).replace('.','p')}.json"
            ), "w"
        ) as fp:
            json.dump(
                {
                    "CLs_exp": [float(i.tolist()) for i in expCLs],
                    "CLs_obs": obsCLs.tolist()
                }, fp
            )


if __name__ == "__main__":
    main()

def getExpectedEvents(inputname):
    expectedEvents = {}
   
        # Have SimpleAnalysis output text file, so do the usual thing.
    with open(f) as file:
        expectedEvents = {}
        next(file) # skip header
        xsection = xsecDB.xsecTimesEffTimeskFac(dsid=getDSID(inputname))
        for l in file:
            l = l.strip().split(",")
            events = float(args.lumi)*xsection*float(l[2])
            statError = float(args.lumi)*xsection*float(l[3])
            expectedEvents[l[0]] = (events,statError)

    # print(expectedEvents)
    return expectedEvents
