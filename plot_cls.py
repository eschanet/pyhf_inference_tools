#!/usr/bin python3

import click

import uproot
import pandas
import numpy as np
import json

import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

plt.rcParams["font.sans-serif"] = ["Arial", "sans-serif"]
plt.rcParams.update({"font.size": 12})


@click.command()
@click.option(
    "--group",
    default="1Lbb",
    type=click.Choice(
        [
            "1Lbb",
            "2L0J",
            "compressed",
            "3Loffshell",
            "stop1L",
            "3LRJR",
            "directstaus",
            "samesign",
            "sbottom",
        ]
    ),
)
@click.option(
    "--harvest",
    "-h",
    default=[],
    multiple=True,
    help="Harvest to plot",
)
@click.option(
    "--harvest-label",
    "-l",
    default=[],
    multiple=True,
    help="Label of the harvest",
)
@click.option("--width", type=int, default=1600, help="Width of canvas")
@click.option("--height", type=int, default=1200, help="Height of canvas")
@click.option(
    "--comEnergy", type=str, default="13 TeV", help="Center-of-mass energy for plot"
)
@click.option(
    "--lumi-Label", type=str, default="#sqrt{{s}} = {comEnergy}, {luminosity} fb^{{-1}}"
)
@click.option(
    "--xlabel",
    type=str,
    default="m(#tilde{#chi}^{#pm}_{1})/m(#tilde{#chi}^{0}_{2}) [GeV]",
)
@click.option(
    "--ylabel",
    type=str,
    default="m(#tilde{#chi}^{0}_{1}) [GeV]",
)
@click.option("--xmin", type=float, default=20, help="x-axis minimum")
@click.option("--xmax", type=float, default=1000, help="x-axis maximum")
@click.option("--ymin", type=float, default=20, help="y-axis minimum")
@click.option("--ymax", type=float, default=700, help="y-axis maximum")
@click.option(
    "--is-internal/--not-internal", default=False, help="Is this ATLAS Internal?"
)
@click.option(
    "--is-preliminary/--not-preliminary",
    default=False,
    help="Is this ATLAS Preliminary?",
)
@click.option(
    "--labels-left",
    type=float,
    default=0.2,
    help="x-position of labels drawn on the left side of the plot",
)
@click.option(
    "--labels-top",
    type=float,
    default=0.86,
    help="y-position of labels drawn on the top-left of the plot",
)
@click.option(
    "--log/--no-log",
    default=False,
    help="Draw logarithmic axes",
)
@click.option(
    "--draw-ATLAS/--no-ATLAS",
    default=False,
    help="Draw ATLAS label",
)
@click.option(
    "--process-label",
    type=str,
    default="pp #rightarrow #tilde{#chi}^{0}_{2} #tilde{#chi}^{#pm}_{1} (Wino) production ; #tilde{#chi}^{0}_{2} #rightarrow Z #tilde{#chi}^{0}_{1},#tilde{#chi}^{#pm}_{1} #rightarrow W #tilde{#chi}^{0}_{1} ; ",
    help="Label for the physics process drawn",
)
@click.option("--luminosity", type=float, default=139000)
def main(
    group,
    harvest,
    harvest_label,
    width,
    height,
    comenergy,
    lumi_label,
    xlabel,
    ylabel,
    xmin,
    xmax,
    ymin,
    ymax,
    is_internal,
    is_preliminary,
    labels_left,
    labels_top,
    log,
    process_label,
    draw_atlas,
    luminosity,
):

    colors = ["#e67e22", "#07a7ec", "#16a085", "#8e44ad", "#e74c3c"]
    i, yoffset = 0, 0

    g = {}

    for h in harvest:
        with open(f"analyses/{group}/harvests/{h}") as f:
            ds = json.load(f)

            for d in ds:
                if not (d["m1"], d["m2"]) in g.keys():
                    g[(d["m1"], d["m2"])] = [(d["CLsexp"], d["CLs"])]
                else:
                    g[(d["m1"], d["m2"])].append((d["CLsexp"], d["CLs"]))

    signal_grid = {}
    for k, i in g.items():
        if len(i) > 1:
            signal_grid[k] = i

    exp_x = np.array([i[0][0] for k, i in signal_grid.items()])
    exp_y = np.array([i[1][0] for k, i in signal_grid.items()])

    obs_x = np.array([i[0][1] for k, i in signal_grid.items()])
    obs_y = np.array([i[1][1] for k, i in signal_grid.items()])

    fig, ax = plt.subplots()
    fig.set_size_inches(5, 4)

    plt.locator_params(axis="x", nbins=8)

    ax.scatter(
        exp_x,
        exp_y,
        s=20,
        facecolors="none",
        label="Expected CLs",
        edgecolors="#686de0",
    )
    ax.scatter(
        obs_x,
        obs_y,
        s=20,
        facecolors="none",
        label="Observed CLs",
        edgecolors="#10ac84",
    )

    ax.plot((0, 1), linestyle="--", linewidth=1.2, c="#444444")

    ax.legend(
        loc="upper left", bbox_to_anchor=(-0.01, 0.90), frameon=False, fontsize=12
    )

    if log:
        tag = "log"
        ax.set_ylim([0.0000000001, 1])
        ax.set_xlim([0.0000000001, 1])
        ax.set_xscale("log")
        ax.set_yscale("log")
    else:
        tag = "lin"
        ax.set_ylim([0, 1])
        ax.set_xlim([0, 1])

    plt.ylabel("Full LH CLs", ha="right", y=1.0, fontsize=12)
    plt.xlabel("Simplified LH CLs", ha="right", x=1.0, fontsize=12)
    fig.tight_layout()

    ax.minorticks_on()
    plt.tick_params(direction="in", which="both", length=4)

    plt.text(
        0.04,
        0.92,
        r"$\sqrt{s}$=13 TeV, 139 fb$^{-1}$",
        transform=plt.gca().transAxes,
        alpha=1.0,
        fontsize=12,
    )
    plt.text(0.04, 0.86, f"", transform=plt.gca().transAxes, alpha=1.0, fontsize=12)

    plt.savefig(f"analyses/{group}/plots/cls_scatter_{tag}.pdf")


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    main()
