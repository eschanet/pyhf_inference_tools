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


@click.command()
@click.option(
    "--group",
    default="1Lbb",
    type=click.Choice(["1Lbb", "2L0J", "compressed", "3Loffshell"]),
)
@click.option(
    "--dir",
    default="175_135",
)
@click.option(
    "--signal",
    default="MGPy8EG\_A14N23LO\_C1N2\_WZ\_175p0\_135p0\_2L2MET75\_MadSpin",
)
@click.option(
    "--include",
    default="*",
)
def main(group, dir, signal, include):

    yields = {}

    for _f in glob.glob(f"analyses/{group}/tables/{dir}/{include}.tex"):
        print(_f)
        region_name = parse_region_name(_f, group)

        if not region_name in yields.keys():
            yields[region_name] = {}
            yields[region_name]['excl'] = {}
            yields[region_name]['bkgOnly'] = {}
            yields[region_name]['free'] = {}

        if 'excl' in _f:
            fitconfig = 'excl'
        elif 'bkgOnly' in _f:
            fitconfig = 'bkgOnly'
        elif 'free' in _f:
            fitconfig = 'free'

        with open(_f, 'r') as f:
            for l in f:
                if not l.strip().startswith("Fitted"):
                    continue

                entries = l.strip().split('&')

                process = parse_process_name(entries[0])
                (ylds, err_up, err_down) = parse_yields_err(entries[1])

                yields[region_name][fitconfig][process] = (
                    ylds, err_up, err_down
                )

        if (signal in yields[region_name][fitconfig]
            ) and ('bkg' in yields[region_name][fitconfig]):
            bkgyields = yields[region_name][fitconfig]['bkg']
            sigyields = yields[region_name][fitconfig][signal]
            yields[region_name][fitconfig]['bkg'] = (
                bkgyields[0] - sigyields[0], bkgyields[1], bkgyields[2]
            )

    for region in yields.keys():
        samples = yields[region]['bkgOnly'].keys()
        break

    for sample in samples:
        print(sample)

        regions = list(yields.keys())
        regions = np.array(regions)
        _order = np.argsort(regions)
        regions = regions[_order]

        highstat_bkgOnly = []
        highstat_bkgOnly_errs = []
        lowstat_bkgOnly = []
        lowstat_bkgOnly_errs = []
        highstat_excl = []
        highstat_excl_errs = []
        lowstat_excl = []
        lowstat_excl_errs = []
        highstat_free = []
        highstat_free_errs = []
        lowstat_free = []
        lowstat_free_errs = []

        num_lowstat_regions = 0
        for region in regions:
            if region.startswith("CR"):
                highstat_bkgOnly.append(yields[region]['bkgOnly'][sample][0])
                highstat_bkgOnly_errs.append(
                    yields[region]['bkgOnly'][sample][1]
                )
                highstat_excl.append(yields[region]['excl'][sample][0])
                highstat_excl_errs.append(yields[region]['excl'][sample][1])
                highstat_free.append(yields[region]['free'][sample][0])
                highstat_free_errs.append(yields[region]['free'][sample][1])
            else:
                num_lowstat_regions += 1

                lowstat_bkgOnly.append(yields[region]['bkgOnly'][sample][0])
                lowstat_bkgOnly_errs.append(
                    yields[region]['bkgOnly'][sample][1]
                )
                lowstat_excl.append(yields[region]['excl'][sample][0])
                lowstat_excl_errs.append(yields[region]['excl'][sample][1])
                lowstat_free.append(yields[region]['free'][sample][0])
                lowstat_free_errs.append(yields[region]['free'][sample][1])

        highstat_bkgOnly = np.array(highstat_bkgOnly)
        highstat_bkgOnly_errs = np.array(highstat_bkgOnly_errs)
        lowstat_bkgOnly = np.array(lowstat_bkgOnly)
        lowstat_bkgOnly_errs = np.array(lowstat_bkgOnly_errs)
        highstat_excl = np.array(highstat_excl)
        highstat_excl_errs = np.array(highstat_excl_errs)
        lowstat_excl = np.array(lowstat_excl)
        lowstat_excl_errs = np.array(lowstat_excl_errs)
        highstat_free = np.array(highstat_free)
        highstat_free_errs = np.array(highstat_free_errs)
        lowstat_free = np.array(lowstat_free)
        lowstat_free_errs = np.array(lowstat_free_errs)

        num_regions = len(regions)

        y_positions = np.arange(num_regions)[::-1]
        y_pos_lowstat = np.arange(num_lowstat_regions)[::-1]
        y_pos_highstat = np.arange(y_pos_lowstat[0] + 1, num_regions)[::-1]

        fig, (ax_ratio, ax) = plt.subplots(
            1,
            2,
            sharey=True,
            figsize=(6, 1 + num_regions / 4),
            dpi=100,
            gridspec_kw={
                'wspace': 0.03,
                'width_ratios': [1, 2]
            }
        )

        ax2 = ax.twiny()

        ax2.errorbar(
            highstat_free,
            y_pos_highstat + 0.25,
            xerr=highstat_free_errs,
            marker="o",
            markersize=4,
            ls='',
            color="green",
            ecolor='black',
            elinewidth=0.8,
            capsize=1,
            label=r"$\mu_\mathrm{SIG}$ free"
        )

        ax2.errorbar(
            highstat_bkgOnly,
            y_pos_highstat,
            xerr=highstat_bkgOnly_errs,
            marker="o",
            markersize=4,
            ls='',
            color="red",
            ecolor='black',
            elinewidth=0.8,
            capsize=1,
            label=r"$\mu_\mathrm{SIG} = 0$"
        )

        ax2.errorbar(
            highstat_excl,
            y_pos_highstat - 0.25,
            xerr=highstat_excl_errs,
            marker="o",
            markersize=4,
            ls='',
            color="blue",
            ecolor='black',
            elinewidth=0.8,
            capsize=1,
            label=r"$\mu_\mathrm{SIG} = 1$"
        )

        ax.errorbar(
            lowstat_free,
            y_pos_lowstat + 0.25,
            xerr=lowstat_free_errs,
            marker="o",
            markersize=4,
            ls='',
            color="green",
            ecolor='black',
            elinewidth=0.8,
            capsize=1,
            label=r"$\mu_\mathrm{SIG}$ free"
        )

        ax.errorbar(
            lowstat_bkgOnly,
            y_pos_lowstat,
            xerr=lowstat_bkgOnly_errs,
            marker="o",
            ls='',
            markersize=4,
            color="red",
            ecolor='black',
            elinewidth=0.8,
            capsize=1,
            label=r"$\mu_\mathrm{SIG} = 0$"
        )

        ax.errorbar(
            lowstat_excl,
            y_pos_lowstat - 0.25,
            xerr=lowstat_excl_errs,
            marker="o",
            markersize=4,
            ls='',
            color="blue",
            ecolor='black',
            elinewidth=0.8,
            capsize=1,
            label=r"$\mu_\mathrm{SIG} = 1$"
        )

        #
        # Ratios
        #

        ax_ratio.barh(
            y_pos_highstat - 0.25,
            highstat_excl / highstat_bkgOnly - 1,
            height=0.5,
            left=1,
            # xerr=(highstat_excl / highstat_bkgOnly) * (
            #     highstat_excl_errs / highstat_excl +
            #     highstat_bkgOnly_errs / highstat_bkgOnly
            # ),
            color="blue",
            error_kw={
                "ecolor":"gray",
                "elinewidth":0.8,
            },
            linewidth=0.8,
            # label=r"$\mu_\mathrm{SIG} = 1$"
        )

        ax_ratio.barh(
            y_pos_highstat + 0.25,
            highstat_free / highstat_bkgOnly - 1,
            height=0.5,
            left=1,
            # xerr=(highstat_free / highstat_bkgOnly) * (
            #     highstat_free_errs / highstat_free +
            #     highstat_bkgOnly_errs / highstat_bkgOnly
            # ),
            color="green",
            error_kw={
                "ecolor":"gray",
                "elinewidth":0.8,
            },
            # label=r"$\mu_\mathrm{SIG} = 1$"
        )

        ax_ratio.barh(
            y_pos_lowstat - 0.25,
            lowstat_excl / lowstat_bkgOnly - 1,
            height=0.5,
            left=1,
            # xerr=(lowstat_excl / lowstat_bkgOnly) * (
            #     lowstat_excl_errs / lowstat_excl +
            #     lowstat_bkgOnly_errs / lowstat_bkgOnly
            # ),
            color="blue",
            error_kw={
                "ecolor":"gray",
                "elinewidth":0.8,
            },
            linewidth=0.8,
            # label=r"$\mu_\mathrm{SIG} = 1$"
        )

        ax_ratio.barh(
            y_pos_lowstat + 0.25,
            lowstat_free / lowstat_bkgOnly - 1,
            height=0.5,
            left=1,
            # xerr=(lowstat_free / lowstat_bkgOnly) * (
            #     lowstat_free_errs / lowstat_free +
            #     lowstat_bkgOnly_errs / lowstat_bkgOnly
            # ),
            color="green",
            error_kw={
                "ecolor":"gray",
                "elinewidth":0.8,
            },
            # label=r"$\mu_\mathrm{SIG} = 1$"
        )

        # ax.fill_between([-2, 2], -0.5, num_regions - 0.5, color="#fff9ab")
        # ax.fill_between([-1, 1], -0.5, num_regions - 0.5, color="#a4eb9b")
        ax.axhline(
            num_lowstat_regions - 0.5,
            linestyle=(0, (5, 5)),
            linewidth=0.9,
            color="gray"
        )
        ax_ratio.axhline(
            num_lowstat_regions - 0.5,
            linestyle=(0, (5, 5)),
            linewidth=0.9,
            color="gray"
        )

        ax_ratio.set_xlim([0.5, 1.5])
        ax_ratio.axvline(
            1.0, linestyle=(0, (5, 5)), linewidth=0.9, color="gray"
        )
        # ax.hlines(0, -0.5, num_regions - 0.5, linestyles="dotted", color="black")

        sample = sample.replace("\\", "")
        # ax2.set_xlabel(f"Fitted {sample} yields CRs")
        ax2.spines['top'].set_color('black')
        ax2.xaxis.label.set_color('black')
        ax2.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
        ax2.tick_params(direction="in", which="both", axis='x', colors='black')
        ax2.tick_params(axis="both", which="major", pad=8)

        ax.set_xlabel(f"Fitted {sample} yields SRs")
        ax.xaxis.set_minor_locator(
            mpl.ticker.AutoMinorLocator()
        )  # minor ticks
        ax.tick_params(axis="both", which="major", pad=8)
        ax.tick_params(direction="in", top=False, right=True, which="both")

        ax_ratio.set_xlabel(f"Ratio")
        ax_ratio.set_ylim([-0.5, num_regions - 0.5])
        ax_ratio.set_yticks(y_positions)
        ax_ratio.set_yticklabels(regions)
        ax_ratio.xaxis.set_minor_locator(
            mpl.ticker.AutoMinorLocator()
        )  # minor ticks
        ax_ratio.tick_params(axis="both", which="major", pad=8)
        ax_ratio.tick_params(
            direction="in", labeltop=True, top=True, right=True, which="both"
        )

        ax.legend()

        # fig.tight_layout()

        fig.savefig(
            f"analyses/{group}/plots/yields_{dir}_{sample}_{group}.pdf",
            bbox_inches='tight'
        )
        plt.close(fig)


def string_to_float(string):
    return float(string.replace("p", "."))


def parse_region_name(_str, group):
    if group == 'compressed':
        replacements = [
            (".tex", ""),
            ("diboson_fakes_other_Zttjets_top_inRegions_", ""),
            ("_YieldsTable", ""),
            ("MGPy8EG_A14N23LO_C1N2_WZ_175p0_135p0_2L2MET75_MadSpin_", ""),
            ("MGPy8EG_A14N23LO_C1N2_WZ_225p0_215p0_2L2MET75_MadSpin_", ""),
            ("excl_", ""),
            ("bkgOnly_", ""),
            ("free_", ""),
            ("_cuts", ""),
            ("hghmet", "high"),
            ("lowmet_deltaM_low", "medium"),
            ("lowmet_deltaM_high", "low"),
        ]
        basename = os.path.basename(_str.replace(".tex", ""))

        for to_replace, replace_with in replacements:
            basename = basename.replace(to_replace, replace_with)

        # try to map to nice names
        if basename.startswith('SR'):
            if basename.startswith('SRee'):
                basename = basename.replace("SRee_", "SR_") + "_ee"
            elif basename.startswith('SRmm'):
                basename = basename.replace("SRmm_", "SR_") + "_mm"
            basename = basename.replace(f"{basename.split('_')[1]}_", "E_") + basename.split('_')[1].replace("eMLL","_bin_")

        region_name = basename.replace("_", "-")
    else:
        region_name = _str

    return str(region_name)


def parse_process_name(_str):
    process = _str.replace(" ", "").replace("Fitted", "").replace("events", "")
    return process


def parse_yields_err(_str):

    if '\pm' in _str:
        # probably symmetric error
        ylds = float(_str.replace(" ", "").split('\pm')[0].replace("$", ""))

        if len(_str.split('\pm')) > 1:
            err = float(
                _str.replace(" ",
                             "").split('\pm')[1].replace("$",
                                                         "").replace("\\", "")
            )
        else:
            err = 0.0

        return (ylds, err, -err)

    else:
        # asymmetric errors
        ylds = float(_str.replace(" ", "").split('_')[0].replace("$", ""))
        if len(_str.split('_')) > 1:
            err_up = float(
                _str.replace(" ", "").split('_')[1].split('^')
                [0].replace("$", "").replace("{",
                                             "").replace("}",
                                                         "").replace("\\", "")
            )
            err_down = float(
                _str.replace(" ", "").split('_')[1].split('^')
                [1].replace("$", "").replace("{",
                                             "").replace("}",
                                                         "").replace("\\", "")
            )
        else:
            err_up = err_down = 0.0
        return (ylds, err_up, err_down)


if __name__ == "__main__":
    main()
