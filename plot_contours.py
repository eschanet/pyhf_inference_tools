#!/usr/bin/env python

# pylint: disable=import-error
import ROOT
print(ROOT.gROOT.GetVersion())
# pylint: enable=import-error

import contourPlotter
import click


@click.command()
@click.option(
    "--group",
    default="1Lbb",
    type=click.Choice(["1Lbb", "2L0J", "compressed", "3Loffshell"]),
)
@click.option(
    "--is-simplified/--not-simplified",
    default=False,
    help="Results from simplified LH?",
)
@click.option("--width", type=int, default=1600, help="Width of canvas")
@click.option("--height", type=int, default=1200, help="Height of canvas")
@click.option(
    "--comEnergy",
    type=str,
    default="13 TeV",
    help="Center-of-mass energy for plot"
)
@click.option(
    "--lumi-Label",
    type=str,
    default="#sqrt{{s}} = {comEnergy}, {luminosity} fb^{{-1}}"
)
@click.option(
    "--xlabel",
    type=str,
    default="m(#tilde{#chi}^{#pm}_{1})/m(#tilde{#chi}^{0}_{2}) [GeV]"
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
    "--is-internal/--not-internal",
    default=True,
    help="Is this ATLAS Internal?"
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
    "--process-label",
    type=str,
    default=
    "pp #rightarrow #tilde{#chi}^{0}_{2} #tilde{#chi}^{#pm}_{1} (Wino) production ; #tilde{#chi}^{0}_{2} #rightarrow Z #tilde{#chi}^{0}_{1},#tilde{#chi}^{#pm}_{1} #rightarrow W #tilde{#chi}^{0}_{1} ; ",
    help="Label for the physics process drawn",
)
@click.option("--luminosity", type=float, default=139000)
def main(
    group,
    is_simplified,
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
    luminosity,
):

    plot = contourPlotter.contourPlotter(
        "analyses/{group}/plots/exclusion_{group}".format(group=group), width,
        height
    )

    plot.lumiLabel = ""
    plot.processLabel = ""
    plot.canvas.SetLeftMargin(0.15)
    plot.canvas.SetBottomMargin(0.10)

    fullLH_file = ROOT.TFile(
        "analyses/{group}/graphs/pyhf_{group}_fullLH.root".format(group=group)
    )
    simplLH_file = ROOT.TFile(
        "analyses/{group}/graphs/pyhf_{group}_simplifiedLH.root".format(group=group)
    )

    plot.drawAxes([xmin, ymin, xmax, ymax])

    # plot.drawOneSigmaBand(tfile.Get("Band_1s_0"), color=ROOT.TColor.GetColor("#ff7300"), lineColor=ROOT.TColor.GetColor("#c24c00"), title = label1+' Exp.', legendOrder=0)
    # plot.drawExpected(tfile.Get("Exp_0"),color=ROOT.TColor.GetColor("#c24c00"))
    # plot.drawObserved(tfile.Get("Obs_0"),color=ROOT.TColor.GetColor("#ff7300"), title = label1+' Obs. (#pm1 #sigma_{theory}^{SUSY})', legendOrder=1)
    # plot.drawTheoryUncertaintyCurve(tfile.Get("Obs_0_Up"),color=ROOT.TColor.GetColor("#c24c00"))
    # plot.drawTheoryUncertaintyCurve(tfile.Get("Obs_0_Down"),color=ROOT.TColor.GetColor("#c24c00"))
    # plot.drawTheoryLegendLines( xyCoord=(0.2305,0.721),color=ROOT.TColor.GetColor("#c24c00"), length=0.045 )

    color1 = ROOT.TColor.GetColor("#e67e22")
    color2 = ROOT.TColor.GetColor("#b2590c")
    color3 = ROOT.TColor.GetColor("#07a7ec")
    color4 = ROOT.TColor.GetColor("#0475a5")

    if draw_cls:

        plot.drawTextFromTGraph2D(
            simplLH_file.Get("CLs_gr"),
            title="Coloured numbers represent observed CLs",
            size=0.0,
            alpha=0.4,
        )

        plot.drawTextFromTGraph2D(
            fullLH_file.Get("CLs_gr"),
            title="",
            color=color2,
            alpha=0.6,
            angle=30,
            size=0.015,
            yoffset=0.013*ymax,
            format="%.1g",
            titlesize=0.03
        )

        plot.drawTextFromTGraph2D(
            simplLH_file.Get("CLs_gr"),
            title="",
            color=color4,
            alpha=0.6,
            angle=30,
            size=0.015,
            yoffset=-0.013 * ymax,
            format="%.1g",
            titlesize=0.03
        )

    plot.drawOneSigmaBand(
        fullLH_file.Get("Band_1s_0"),
        color=color1,
        lineColor=color1,
        alpha=0.3,
        legendOrder=2,
        title='Full LH Exp.'
    )
    plot.drawExpected(
        fullLH_file.Get("Exp_0"), color=color1, title=None, legendOrder=None
    )
    plot.drawObserved(
        fullLH_file.Get("Obs_0"),
        color=color1,
        title='Full LH Obs.',
        legendOrder=3
    )

    plot.drawOneSigmaBand(
        simplLH_file.Get("Band_1s_0"),
        color=color3,
        lineColor=color3,
        alpha=0.3,
        legendOrder=4,
        title='Simplified LH Exp.'
    )
    plot.drawExpected(
        simplLH_file.Get("Exp_0"), color=color3, title=None, legendOrder=None
    )
    plot.drawObserved(
        simplLH_file.Get("Obs_0"),
        color=color3,
        title='Simplified LH Obs.',
        legendOrder=5
    )

    if group == '1Lbb':
        process_label = "pp #rightarrow #tilde{#chi}^{0}_{2} #tilde{#chi}^{#pm}_{1} (Wino) production ; #tilde{#chi}^{0}_{2} #rightarrow h #tilde{#chi}^{0}_{1},#tilde{#chi}^{#pm}_{1} #rightarrow W #tilde{#chi}^{0}_{1} ; "
        text = "m(#tilde{#chi}^{#pm}_{1}/#tilde{#chi}^{0}_{2}) < m(#tilde{#chi}^{0}_{1}) + 125 GeV"
        plot.drawLine(
            coordinates=[xmin, xmin - 125, ymax + 125, ymax],
            label=text,
            style=7,
            angle=54
        )
    elif group == '2L0J':
        process_label = "pp #rightarrow #tilde{#chi}^{#pm}_{1} #tilde{#chi}^{#pm}_{1} (Wino) production ; #tilde{#chi}^{#pm}_{1} #rightarrow W #tilde{#chi}^{0}_{1} ; "
        text = "m(#tilde{#chi}^{#pm}_{1}) < m(#tilde{#chi}^{0}_{1}) + m(W)"
        plot.drawLine(
            coordinates=[xmin, xmin - 80, ymax + 80, ymax],
            label=text,
            style=7,
            angle=54
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

    # plot.drawLabel(label="v1.0.0")

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
    latexObject.DrawLatexNDC(
        labels_left, labels_top - 0.04 * 2, "All limits at 95% CL"
    )

    latexObject.SetTextSize(0.041)
    if is_internal:
        latexObject.DrawLatexNDC(
            labels_left, labels_top, "#scale[1.2]{#bf{#it{ATLAS}} Internal}"
        )
    elif is_preliminary:
        latexObject.DrawLatexNDC(
            labels_left, labels_top, "#scale[1.2]{#bf{#it{ATLAS}} Preliminary}"
        )
    else:
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
