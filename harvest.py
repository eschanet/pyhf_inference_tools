#!/usr/bin/env python

import json
import re
import click
import pathlib


def string_to_float(string):
    return float(string.replace("p", "."))


pattern = re.compile("(\d+(?:p[05])?)_(\d+(?:p[05])?)")


def filename_to_mass(filename):
    global pattern
    match = pattern.search(filename.name)
    assert match
    return string_to_float(match.group(1)), string_to_float(match.group(2))


def make_harvest_from_result(result, masses):
    return {
        "CLs": result["CLs_obs"],
        "CLsexp": result["CLs_exp"][2],
        "clsd1s": result["CLs_exp"][1],
        "clsd2s": result["CLs_exp"][0],
        "clsu1s": result["CLs_exp"][3],
        "clsu2s": result["CLs_exp"][4],
        "covqual": 3,
        "dodgycov": 0,
        "excludedXsec": -999007,
        "expectedUpperLimit": -1,
        "expectedUpperLimitMinus1Sig": -1,
        "expectedUpperLimitMinus2Sig": -1,
        "expectedUpperLimitPlus1Sig": -1,
        "expectedUpperLimitPlus2Sig": -1,
        "fID": -1,
        "failedcov": 0,
        "failedfit": 0,
        "failedp0": 0,
        "failedstatus": 0,
        "fitstatus": 0,
        "x": masses[0],
        "y": masses[1],
        "dm": masses[0] - masses[1],
        "mode": -1,
        "nexp": -1,
        "nofit": 0,
        "p0": 0,
        "p0d1s": -1,
        "p0d2s": -1,
        "p0exp": -1,
        "p0u1s": -1,
        "p0u2s": -1,
        "p1": 0,
        "seed": 0,
        "sigma0": -1,
        "sigma1": -1,
        "upperLimit": -1,
        "upperLimitEstimatedError": -1,
        "xsec": -999007,
    }


@click.command()
@click.option(
    "--group",
    default="1Lbb",
    type=click.Choice(
        [
            "compressed",
            "1Lbb",
            "2L0J",
        ]
    ),
)
@click.option('--simplified/--no-simplified', default=False)

def main(group, simplified):
    harvest = []
    signal_grid_results = {}

    match_base = group

    filenames = pathlib.Path(f"./analyses/{group}/results/").glob(f"{'simplified_' if simplified else ''}{match_base}_*.json")

    for filename in filenames:
        print(filename)
        result = json.load(filename.open())
        masses = filename_to_mass(filename)
        harvest.append(make_harvest_from_result(result, masses))

    with pathlib.Path(f"./analyses/{group}/harvests/harvest_{'simplified_' if simplified else ''}{group}.json").open("w+") as output_file:
        json.dump(
            harvest, output_file, sort_keys=True, indent=2,
        )


if __name__ == "__main__":
    main()
