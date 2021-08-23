#!/usr/bin/env python

# pylint: disable=import-error
import ROOT

print(ROOT.gROOT.GetVersion())

from helpers import contourPlotter
import click
import math


@click.command()
@click.option(
    "--group",
    default="1Lbb",
    type=click.Choice(["1Lbb", "2L0J", "compressed", "3Loffshell", "stop1L"]),
)
@click.option(
    "--contour",
    "-c",
    default=[],
    multiple=True,
    help="Contours to plot",
)
@click.option(
    "--contour-label",
    "-l",
    default=[],
    multiple=True,
    help="Label of the contour",
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
    "--logy/--no-logy",
    default=False,
    help="Draw logarithmic y-axis",
)
@click.option(
    "--draw-CLs/--no-draw-CLs",
    default=False,
    help="Draw CLs numbers on plot",
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
    contour,
    contour_label,
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
    logy,
    process_label,
    draw_cls,
    draw_atlas,
    luminosity,
):

    plot = contourPlotter.contourPlotter(
        "analyses/{group}/plots/exclusion_{group}".format(group=group), width, height
    )

    plot.lumiLabel = ""
    plot.processLabel = ""
    plot.canvas.SetLeftMargin(0.15)
    plot.canvas.SetBottomMargin(0.10)

    plot.drawAxes([xmin, ymin, xmax, ymax])

    color1 = ROOT.TColor.GetColor("#e67e22")
    color2 = ROOT.TColor.GetColor("#07a7ec")
    color3 = ROOT.TColor.GetColor("#8e44ad")
    color4 = ROOT.TColor.GetColor("#e74c3c")

    colors = [color1, color2, color3, color4]
    i = 0
    yoffset = 0
    for idx, (cnt, label, color) in enumerate(zip(contour, contour_label, colors)):
        f = ROOT.TFile("analyses/{group}/graphs/{cnt}".format(group=group, cnt=cnt))
        i += 1
        plot.drawOneSigmaBand(
            f.Get("Band_1s_0"),
            color=color,
            lineColor=color,
            alpha=0.3,
            legendOrder=i,
            title=label + " Exp.",
        )
        plot.drawExpected(f.Get("Exp_0"), color=color, title=None, legendOrder=None)

        i += 1
        plot.drawObserved(
            f.Get("Obs_0"), color=color, title=label + " Obs.", legendOrder=i
        )

        if draw_cls:
            plot.drawTextFromTGraph2D(
                f.Get("CLs_gr"),
                title="",
                color=color,
                alpha=0.6,
                angle=30,
                size=0.015,
                yoffset=yoffset,
                format="%.1g",
                titlesize=0.03,
            )
            yoffset = 0.017 * ymax * (-1) ** idx * math.floor(0.5 * idx + 1)

    if draw_cls:
        plot.drawTextFromTGraph2D(
            f.Get("CLs_gr"),
            title="Coloured numbers represent observed CLs",
            size=0.0,
            alpha=0.4,
        )

    if group == "1Lbb":
        process_label = "pp #rightarrow #tilde{#chi}^{0}_{2} #tilde{#chi}^{#pm}_{1} (Wino) production ; #tilde{#chi}^{0}_{2} #rightarrow h #tilde{#chi}^{0}_{1},#tilde{#chi}^{#pm}_{1} #rightarrow W #tilde{#chi}^{0}_{1} ; "
        text = "m(#tilde{#chi}^{#pm}_{1}/#tilde{#chi}^{0}_{2}) < m(#tilde{#chi}^{0}_{1}) + 125 GeV"
        plot.drawLine(
            coordinates=[125, 0, ymax + 125, ymax], label=text, style=7, angle=57
        )
    elif group == "2L0J":
        process_label = "pp #rightarrow #tilde{#chi}^{#pm}_{1} #tilde{#chi}^{#pm}_{1} (Wino) production ; #tilde{#chi}^{#pm}_{1} #rightarrow W #tilde{#chi}^{0}_{1} ; "
        text = "m(#tilde{#chi}^{#pm}_{1}) < m(#tilde{#chi}^{0}_{1}) + m(W)"
        plot.drawLine(
            coordinates=[xmin, xmin - 80, ymax + 80, ymax],
            label=text,
            style=7,
            angle=54,
        )

    elif group == "stop1L":
        process_label = "pp #rightarrow #tilde{t}_{1} #tilde{t}_{1} ; #tilde{t}_{1} #rightarrow bff #tilde{#chi}^{0}_{1}, #tilde{t}_{1} #rightarrow bW #tilde{#chi}^{0}_{1}, #tilde{t}_{1} #rightarrow t #tilde{#chi}^{0}_{1} ; "
        text = "m(#tilde{t}_{1}) < m(#tilde{#chi}^{0}_{1}) + m(t)"
        plot.drawLine(
            coordinates=[xmin, xmin - 173, ymax + 173, ymax],
            label=text,
            style=7,
            angle=45,
        )

    ## Axis Labels
    plot.setXAxisLabel(xlabel)
    plot.setYAxisLabel(ylabel)
    plot.bottomObject.GetXaxis().SetTitleSize(0.04)
    plot.bottomObject.GetXaxis().SetLabelSize(0.04)
    plot.bottomObject.GetYaxis().SetTitleSize(0.04)
    plot.bottomObject.GetYaxis().SetLabelSize(0.04)

    # Legend
    legend = plot.createLegend(
        shape=(
            labels_left - 0.01,
            labels_top - 0.09,
            labels_left + 0.25,
            labels_top - 0.25,
        )
    )
    legend.SetTextSize(0.035)
    legend.Draw()

    # plot.drawTheoryUncertaintyCurve( f.Get("Obs_0_Up") )
    # plot.drawTheoryUncertaintyCurve( f.Get("Obs_0_Down") )
    # # coordinate in NDC
    # plot.drawTheoryLegendLines( xyCoord=(0.234,0.6625), length=0.057 )

    plot.canvas.cd()
    latexObject = ROOT.TLatex()
    latexObject.SetTextFont(42)
    latexObject.SetTextAlign(11)
    latexObject.SetTextColor(1)

    latexObject.SetTextSize(0.035)
    latexObject.DrawLatexNDC(0.16, 0.95, process_label + group)

    latexObject.SetTextSize(0.037)
    latexObject.DrawLatexNDC(
        labels_left,
        labels_top - 0.04,
        lumi_label.format(comEnergy=comenergy, luminosity=luminosity / 1.0e3),
    )
    latexObject.DrawLatexNDC(labels_left, labels_top - 0.04 * 2, "All limits at 95% CL")

    latexObject.SetTextSize(0.041)
    if is_internal and draw_atlas:
        latexObject.DrawLatexNDC(
            labels_left, labels_top, "#scale[1.2]{#bf{#it{ATLAS}} Internal}"
        )
    elif is_preliminary and draw_atlas:
        latexObject.DrawLatexNDC(
            labels_left, labels_top, "#scale[1.2]{#bf{#it{ATLAS}} Preliminary}"
        )
    elif draw_atlas:
        latexObject.DrawLatexNDC(
            labels_left, labels_top, "#scale[1.2]{#bf{#it{ATLAS}}}"
        )

    if logy:
        ROOT.gPad.RedrawAxis()
        plot.canvas.SetTicks()
        plot.canvas.SetLogy()
        plot.canvas.Update()

    plot.decorateCanvas()
    plot.writePlot()


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    main()
