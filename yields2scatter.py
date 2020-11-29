#!/usr/bin/env python
import click
import pathlib
import subprocess
import re
import json
import os
import glob

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

import uncertainties

import pyhf

pattern = re.compile("(\d+(?:p[05])?)_(\d+(?:p[05])?)")


def string_to_float(string):
    return float(string.replace("p", "."))

def parse_region_name(_str):
    basename = os.path.basename(_str.replace(".tex",""))
    basename = basename.replace("diboson_fakes_other_Zttjets_top_inRegions_","").replace("_YieldsTable","")
    region_name = basename.replace("excl_","").replace("bkgOnly_","")
    return region_name

def parse_process_name(_str):
    process = _str.replace(" ", "").replace("Fitted","").replace("events","")
    return process

def parse_yields_err(_str):

    if '\pm' in _str:
        # probably symmetric error
        ylds = float(_str.replace(" ", "").split('\pm')[0].replace("$",""))

        if len(_str.split('\pm')) > 1:
            err = float(_str.replace(" ", "").split('\pm')[1].replace("$","").replace("\\",""))
        else:
            err = 0.0

        return (ylds, err, -err)

    else:
        # asymmetric errors
        ylds = float(_str.replace(" ", "").split('_')[0].replace("$",""))
        if len(_str.split('_')) > 1:
            err_up = float(_str.replace(" ", "").split('_')[1].split('^')[0].replace("$","").replace("{","").replace("}","").replace("\\",""))
            err_down = float(_str.replace(" ", "").split('_')[1].split('^')[1].replace("$","").replace("{","").replace("}","").replace("\\",""))
        else:
            err_up = err_down = 0.0
        return (ylds, err_up, err_down) 

@click.command()
@click.option(
    "--group",
    default="1Lbb",
    type=click.Choice(["1Lbb", "2L0J", "compressed", "3Loffshell"]),
)
def main(group):

    yields = {}

    for _f in glob.glob(f"analyses/{group}/tables/*.tex"):
        print(_f)
        region_name = parse_region_name(_f)

        if not region_name in yields.keys():
            yields[region_name] = {}
            yields[region_name]['excl'] = {}
            yields[region_name]['bkgOnly'] = {}

        fitconfig = "excl" if "excl" in _f else "bkgOnly"

        with open(_f, 'r') as f:
            for l in f:
                if not l.strip().startswith("Fitted"):
                    continue

                entries = l.strip().split('&')

                process = parse_process_name(entries[0])
                (ylds,err_up,err_down) = parse_yields_err(entries[1])
                
                yields[region_name][fitconfig][process] = (ylds, err_up,err_down)

    print(yields)

    for region in yields.keys():
        samples = yields[region]['bkgOnly'].keys()
        break
    
    for sample in samples:
        print(sample) 
        
        bkgOnly = []
        bkgOnly_errs = []
        for region in yields.keys():
            bkgOnly.append(yields[region]['bkgOnly'][sample][0])
            bkgOnly_errs.append(yields[region]['bkgOnly'][sample][1])

        num_regions = len(yields.keys())

        y_positions = np.arange(num_regions)[::-1]
        fig, ax = plt.subplots(figsize=(6, 1 + num_regions / 4), dpi=100)

        ax.errorbar(
            bkgOnly,
            y_positions,
            # xerr=uncertainty_constrained,
            fmt="o",
            color="black",
        )

        # ax.fill_between([-2, 2], -0.5, num_regions - 0.5, color="#fff9ab")
        # ax.fill_between([-1, 1], -0.5, num_regions - 0.5, color="#a4eb9b")
        # ax.vlines(0, -0.5, num_regions - 0.5, linestyles="dotted", color="black")
        # ax.hlines(0, -0.5, len(num_regions) - 0.5, linestyles="dotted", color="black")

        ax.set_xlim([0, 2])
        ax.set_xlabel(r"$\left(\hat{\theta} - \theta_0\right) / \Delta \theta$")
        ax.set_ylim([-0.5, num_regions - 0.5])
        ax.set_yticks(y_positions)
        ax.set_yticklabels(np.append(yields.keys(), axis=0))
        ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())  # minor ticks
        ax.tick_params(axis="both", which="major", pad=8)
        ax.tick_params(direction="in", top=True, right=True, which="both")

        fig.tight_layout()

        fig.savefig(f"analyses/{group}/plots/yields_{sample}_{group}.pdf")
        plt.close(fig)



if __name__ == "__main__":
    main()
