#!/usr/bin/env python

import click
import collections
import csv
import json
import re
import math
import pathlib
import jsonpatch
import pprint

import pyhf

pyhf.set_backend("numpy")

from xsecDB import CrossSectionDB

xsecDB = CrossSectionDB()

mass_pattern = re.compile("(\d+(?:p[05]){1})_(\d+(?:p[05]){1})")
dsid_pattern = re.compile("(\d{6}?)")
point_pattern = re.compile("(\d+(?:p[05])_\d+(?:p[05])){1}")


def string_to_float(string):
    return float(string.replace("p", "."))


@click.command()
@click.option(
    "--group",
    default="1Lbb",
    type=click.Choice(["1Lbb", "2L0J", "compressed", "3Loffshell"]),
)
@click.option("--backend", default="pytorch")
@click.option(
    "--prune-channel",
    default=[],
    multiple=True,
    help="Channel to prune",
)
@click.option(
    "--prune-modifier",
    default=[],
    multiple=True,
    help="Modifier to prune",
)
@click.option(
    "--prune-modifier-type",
    default=[],
    multiple=True,
    help="Modifier type to prune",
)
@click.option(
    "--prune-sample",
    default=[],
    multiple=True,
    help="Modifier to prune",
)
@click.option("--simplified/--no-simplified", default=False)
@click.option("--likelihood", default="BkgOnly.json")
@click.option("--optimizer", default="scipy")
@click.option("--patchname", default=None)
@click.option("--lumi", default=139000)
@click.option("--include", default=None)
def main(
    group,
    backend,
    prune_channel,
    prune_modifier,
    prune_modifier_type,
    prune_sample,
    simplified,
    likelihood,
    optimizer,
    patchname,
    lumi,
    include,
):

    pyhf.set_backend(backend, optimizer)
    likelihood = likelihood if not simplified else "simplified_" + likelihood

    spec = json.load(
        open(pathlib.Path(f"./analyses/{group}/likelihoods/{likelihood}"), "r")
    )

    patchDef = {}
    idxCol = 0
    if not patchname:
        patchname = f"{group}.patch"

    with open(f"./analyses/{group}/truth/{patchname}", "r") as f:
        reader = csv.reader(f)
        patchDef = collections.OrderedDict()
        try:
            header = next(reader)
        except StopIteration:
            return {}
        for col in header:
            if header.index(col) == idxCol:
                continue
            patchDef[col] = collections.OrderedDict()
        for row in reader:
            for col in range(0, len(row)):
                if col == idxCol:
                    continue
                try:
                    patchDef[header[col]][row[idxCol]] = row[col]
                except IndexError:
                    print("Exception in %s" % csvName)
                    print("Row: ", row)
                    print("Length: %d - expected: %d" % (len(row), len(header)))
                    raise

    found = False
    wildcard = "*C1*N2*.txt" if not include else include
    filenames = pathlib.Path(f"./analyses/{group}/truth/").glob(wildcard)

    expectedEvents = collections.defaultdict(
        lambda: collections.defaultdict(lambda: None)
    )

    for filename in filenames:
        point_match = point_pattern.search(filename.name)
        assert point_match

        mass_match = mass_pattern.search(filename.name)
        assert mass_match
        masses = string_to_float(mass_match.group(1)), string_to_float(
            mass_match.group(2)
        )

        dsid_match = dsid_pattern.search(filename.name)
        assert dsid_match
        dsid = string_to_float(dsid_match.group(1))
        xsec = xsecDB.xsecTimesEff(dsid)

        # print(filename)

        with open(filename) as file:
            next(file)  # skip header
            for l in file:
                l = l.strip().split(",")
                events = float(lumi) * xsec * float(l[2])
                statError = float(lumi) * xsec * float(l[3])
                # print(expectedEvents[point_match[0]])
                if expectedEvents[point_match[0]][l[0]]:
                    events += expectedEvents[point_match[0]][l[0]][0]
                    statError = math.sqrt(
                        statError ** 2 + expectedEvents[point_match[0]][l[0]][1] ** 2
                    )
                expectedEvents[point_match[0]][l[0]] = (events, statError)

    pprint.pprint(expectedEvents["700p0_150p0"])

    for point, events in expectedEvents.items():
        patches = []
        handled_channels = []
        for srName in patchDef["eff"]:
            path = patchDef["jsonpath"][srName]
            expected = float(events[srName][0])
            # expected *= float(patchDef['eff'][srName])

            patches.append({"op": "replace", "path": path, "value": expected})

        patched_spec = jsonpatch.apply_patch(spec, patches)

        ws = pyhf.Workspace(patched_spec)
        ws = ws.prune(
            modifiers=prune_modifier,
            modifier_types=prune_modifier_type,
            samples=prune_sample,
            channels=prune_channel,
        )

        pdf = ws.model(
            modifier_settings={
                "normsys": {"interpcode": "code4"},
                "histosys": {"interpcode": "code4p"},
            }
        )

        print("Running " + point)

        obsCLs, expCLs = pyhf.infer.hypotest(
            1.0, ws.data(pdf), pdf, qtilde=True, return_expected_set=True
        )
        with open(
            pathlib.Path(
                f"analyses/{group}/results/truth_{'simplified_' if simplified else ''}{group}_{point}.json"
            ),
            "w",
        ) as fp:
            json.dump(
                {
                    "CLs_exp": [float(i.tolist()) for i in expCLs],
                    "CLs_obs": obsCLs.tolist(),
                },
                fp,
            )


if __name__ == "__main__":
    main()
