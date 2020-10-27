#!/usr/bin/env python

import ROOT
print(ROOT.gROOT.GetVersion())

import contourPlotter

import click


@click.command()
@click.option(
    "--group", default="combination", 
	type=click.Choice(["1Lbb", "2L0J", "compressed"]),
)
@click.option("--width", type=int, default=1600, help="Width of canvas")
@click.option("--height", type=int, default=1200, help="Height of canvas")
@click.option(
    "--comEnergy", type=str, default="13 TeV", help="Center-of-mass energy for plot"
)
@click.option(
    "--lumiLabel", type=str, default="#sqrt{{s}} = {comEnergy}, {luminosity} fb^{{-1}}"
)
@click.option("--xlabel", type=str, default="m(#tilde{#chi}^{#pm}_{1})/m(#tilde{#chi}^{0}_{2}) [GeV]")
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
    "--is-internal/--not-internal", default=True, help="Is this ATLAS Internal?"
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
    "--process-label",
    type=str,
    default="pp #rightarrow #tilde{#chi}^{0}_{2} #tilde{#chi}^{#pm}_{1} (Wino) production ; #tilde{#chi}^{0}_{2} #rightarrow h #tilde{#chi}^{0}_{1},#tilde{#chi}^{#pm}_{1} #rightarrow W #tilde{#chi}^{0}_{1} ; ",
    help="Label for the physics process drawn",
)
@click.option("--luminosity", type=float, default=139000)

parser = argparse.ArgumentParser(description='Make simple contour plot from JSON dump')
parser.add_argument('-input_graphs', help='input graphs', default=None)
parser.add_argument('-output_name', help='name of the output', default=None)
parser.add_argument('-model', help='what model do you want to plot?', default='Wh')
parser.add_argument('-version', help='used for printing versioning label', default='Smeared truth v6.0')
parser.add_argument('-comparisonContour', help='Comparison contour', default=None)
parser.add_argument('--gridx', help='calculate x and use it as y variable (mc-mn)/(mg-mn)', action='store_true')
parser.add_argument('--pyhf', help='pyHF comparison', action='store_true')
parser.add_argument('--reco', help='Using reco samples', action='store_true')
parser.add_argument("--closedBands","-b", help = "if contours are closed shapes in this space, this can help with stitching issues if you're seeing weird effects", action="store_true", default=False)

parser.add_argument('--xmin', type=float)
parser.add_argument('--ymin', type=float)
parser.add_argument('--xmax', type=float)
parser.add_argument('--ymax', type=float)
args = parser.parse_args()

def createBandFromContours(contour1,contour2=None):

	if not contour2:
		outputGraph = contour1
	else:
		outputSize = contour1.GetN()+contour2.GetN()+1

		pointOffset = 0
		if args.closedBands:
			outputSize += 2
			pointOffset = 1

		outputGraph = ROOT.TGraph(outputSize)
		tmpx, tmpy = ROOT.Double(), ROOT.Double()
		for iPoint in xrange(contour2.GetN()):
			contour2.GetPoint(iPoint,tmpx,tmpy)
			outputGraph.SetPoint(iPoint,tmpx,tmpy)

		if args.closedBands:
			contour2.GetPoint(0,tmpx,tmpy)
			outputGraph.SetPoint(contour2.GetN()+1, tmpx,tmpy)

		for iPoint in xrange(contour1.GetN()):
			contour1.GetPoint(contour1.GetN()-1-iPoint,tmpx,tmpy)
			outputGraph.SetPoint(contour2.GetN()+pointOffset+iPoint,tmpx,tmpy)

		if args.closedBands:
			contour1.GetPoint(contour1.GetN()-1,tmpx,tmpy)
			outputGraph.SetPoint(contour1.GetN()+contour2.GetN(), tmpx,tmpy)

		contour2.GetPoint(0,tmpx,tmpy)
		outputGraph.SetPoint(contour1.GetN()+contour2.GetN()+pointOffset,tmpx,tmpy)

	outputGraph.SetFillStyle(1001);
	outputGraph.SetLineWidth(1)

	return outputGraph

def cleanContour(contour):
	x,y = ROOT.Double(0),ROOT.Double(0)
	cleanedContour = ROOT.TGraph()
	xmin = 400 if "SS" in args.model else 800
	ymin = 250 if "SS" in args.model else 250
	for p in range(contour.GetN()):
		contour.GetPoint(p,x,y)
		if x < xmin and y < ymin:
			continue
		cleanedContour.SetPoint(p,x,y)
	return cleanedContour


def main(



)
	drawTheorySysts = False

	if args.output_name:
		plotname = args.output_name
	else:
		plotname = 'plot'
		plotname = plotname + '_' + args.model
		plotname = plotname + '_gridx' if args.gridx else plotname + '_x12'

	plot = contourPlotter.contourPlotter(plotname,900,600)

	if args.model == 'Wh':
		plot.processLabel = " #tilde{#chi}^{#pm}_{1}-#tilde{#chi}^{0}_{2}#rightarrowWh#tilde{#chi}^{0}_{1}#tilde{#chi}^{0}_{1}#rightarrowl#nubb#tilde{#chi}^{0}_{1}#tilde{#chi}^{0}_{1}"
		plot.lumiLabel = "#sqrt{s}=13 TeV, 139 fb^{-1}, All limits at 95% CL"
	elif args.model == 'GG_oneStep':
		plot.processLabel = " #tilde{g}-#tilde{g}#rightarrowqqqq#tilde{#chi}^{#pm}_{1}#tilde{#chi}^{#pm}_{1}#rightarrowqqqqWW#tilde{#chi}^{0}_{1}#tilde{#chi}^{0}_{1} ,   x=(m(#tilde{#chi}^{#pm}_{1})-m(#tilde{#chi}^{0}_{1}))/(m(#tilde{g})-m(#tilde{#chi}^{0}_{1})) = 1/2"
		plot.lumiLabel = "#sqrt{s}=13 TeV, 36.1 fb^{-1}, All limits at 95% CL"


	if args.input_graphs is None:
		if args.model == 'GG_oneStep':
			args.input_graphs = 'graphs_gluino_gridx.root' if args.gridx else 'graphs_gluino_x12.root'
		elif args.model == 'SS_oneStep':
			args.input_graphs = 'graphs_squark_gridx.root' if args.gridx else 'graphs_squark_x12.root'
		elif args.model == 'Wh':
			args.input_graphs = 'graphs_1Lbb_Wh_expected.root'
		else:
			args.input_graphs = 'outputGraphs.root'

	f = ROOT.TFile(args.input_graphs)
	f.ls()

	if not args.comparisonContour:
		if args.model == 'GG_oneStep':
			comparisonContour = '../../contours/limit_OneLepton_GGgridx_2J_4Jlowx_4Jhighx_6J_25042017curves.root' if args.gridx else '../contours/limit_OneLepton_GGx12_2J_4Jlowx_4Jhighx_6J_25042017curves.root'
			xmin = 350 if not args.gridx else 1050
			xmax = 2300 if not args.gridx else 2300
			ymin = 25 if not args.gridx else 0
			ymax = 1800 if not args.gridx else 1.5
		elif args.model == 'SS_oneStep':
			comparisonContour = '../../../contours/limit_OneLepton_SSgridx_2J_4Jlowx_4Jhighx_6J_25042017curves.root' if args.gridx else '../contours/limit_OneLepton_SSx12_2J_4Jlowx_4Jhighx_6J_25042017curves.root'
			xmin = 220 if not args.gridx else 650
			xmax = 1450 if not args.gridx else 1600
			ymin = 25 if not args.gridx else 0
			ymax = 1050 if not args.gridx else 1.5
		elif args.model == 'Wh':
			comparisonContour = '../../../contours/outputGraphs_1Lbb_190826.root'
			xmin = 150
			xmax = 1050
			ymin = 0
			ymax = 500
	else:
		comparisonContour = args.comparisonContour
		xmin = 150
		xmax = 1050
		ymin = 0
		ymax = 500

	tfile = ROOT.TFile(comparisonContour, 'read')
	# oldlimitsfile = ROOT.TFile('../contours/gluino_observed_hardlepton_8TeV.root', 'read')
	#
	plot.drawAxes( [xmin,ymin,xmax,ymax] )

	## Main Result

	# plot.drawTextFromTGraph2D( f.Get("CLs_gr")  , angle=30 , title = "Grey Numbers Represent Observed CLs Value")
	plot.processLabel += "                                                                       #bf{First wave 1Lbb}"
	if not args.pyhf:
		label1 = 'arXiv:1909.09226'
		# label2 = 'Full likelihood (bkg)'
		label2 = 'Simplified Fit'
	else:
		label1 = 'arXiv:1909.09226'
		label2 = 'Simplified Fit'


	if 'oneStep' in args.model:
		upSigmaBand = tfile.Get("firstPOneSigmaG")
		downSigmaBand = tfile.Get("firstMOneSigmaG")
		sigmaBand = createBandFromContours(upSigmaBand,downSigmaBand)
		sigmaBand = cleanContour(sigmaBand)

		x,y = ROOT.Double(0),ROOT.Double(0)
		for p in range(sigmaBand.GetN()):
			sigmaBand.GetPoint(p,x,y)
			print (p,x,y)

		cleanedExpected = cleanContour(tfile.Get("firstExpH_graph0"))
		plot.drawOneSigmaBand(sigmaBand, color=ROOT.TColor.GetColor("#ff4d00"),title = 'Full Fit, PhysRevD.96.112010')
		plot.drawExpected(cleanedExpected)
	else:
		plot.drawOneSigmaBand(tfile.Get("Band_1s_0"), color=ROOT.TColor.GetColor("#ff7300"), lineColor=ROOT.TColor.GetColor("#c24c00"), title = label1+' Exp.', legendOrder=0)
		plot.drawExpected(tfile.Get("Exp_0"),color=ROOT.TColor.GetColor("#c24c00"))
		plot.drawObserved(tfile.Get("Obs_0"),color=ROOT.TColor.GetColor("#ff7300"), title = label1+' Obs. (#pm1 #sigma_{theory}^{SUSY})', legendOrder=1)
		plot.drawTheoryUncertaintyCurve(tfile.Get("Obs_0_Up"),color=ROOT.TColor.GetColor("#c24c00"))
		plot.drawTheoryUncertaintyCurve(tfile.Get("Obs_0_Down"),color=ROOT.TColor.GetColor("#c24c00"))
		plot.drawTheoryLegendLines( xyCoord=(0.2305,0.721),color=ROOT.TColor.GetColor("#c24c00"), length=0.045 )


	if args.reco:
		color1=ROOT.TColor.GetColor("#02951a")
		color2=ROOT.TColor.GetColor("#0c8331")
	else:
		color1=ROOT.TColor.GetColor("#07a7ec")
		color2=ROOT.TColor.GetColor("#068ac6")
	# plot.drawOneSigmaBand(f.Get("Band_1s_0"), color=color1,lineColor=color2 ,alpha=0.0,title = label2+' Exp.', legendOrder=2)
	plot.drawExpected(f.Get("Exp_0"),color=color2,title = label2+' Exp.',legendOrder=2)
	plot.drawObserved(f.Get("Obs_0"),color=color1, title = label2+' Obs.', legendOrder=3)


	# plot.drawShadedRegion( oldlimitsfile.Get("Table 32/Graph1D_y1"), title="ATLAS 8 TeV, 20.3 fb^{-1} (observed)" )
	# plot.drawObserved(      f.Get("Obs_0"), title="Observed Limit (#pm1 #sigma_{theory}^{SUSY})" if drawTheorySysts else "Observed Limit")


	## Draw Lines
	if 'oneStep' in args.model:
		if args.gridx:
			plot.drawLine(  coordinates = [xmin,1,xmax,1], label = "", style = 7, angle = 0  )
		else:
			text = "m(#tilde{q}) < m(#tilde{#chi}^{0}_{1})" if "SS" in args.model else "m(#tilde{g}) < m(#tilde{#chi}^{0}_{1})"
			plot.drawLine(  coordinates = [xmin,xmin,ymax,ymax], label = text, style = 7, angle = 40 )
	else:
		text = "m(#tilde{#chi}^{#pm}_{1}/#tilde{#chi}^{0}_{2}) < m(#tilde{#chi}^{0}_{1}) + 125 GeV"
		plot.drawLine(  coordinates = [xmin,xmin-125,ymax+125,ymax], label = text, style = 7, angle = 54 )

	## Axis Labels

	if 'oneStep' in args.model:
		plot.setXAxisLabel("m(#tilde{q}) [GeV]" if "SS" in args.model else "m(#tilde{g}) [GeV]")
		plot.setYAxisLabel("m(#tilde{#chi}^{0}_{1}) [GeV]")
	else:
		plot.setXAxisLabel("m(#tilde{#chi}^{#pm}_{1}/#tilde{#chi}^{0}_{2}) [GeV]")
		plot.setYAxisLabel("m(#tilde{#chi}^{0}_{1}) [GeV]")

	plot.createLegend(shape=(0.22,0.64,0.48,0.79)).Draw()

	if args.version:
		plot.drawLabel(label=args.version)
		# if not args.reco:
			# plot.drawLabel(x = 0.23, y = 0.58, label="m_{bb} smeared")
			# plot.drawLabel(x = 0.23, y = 0.55, label="skew=-5.0, \mu=1.05, \sigma=0.22")

	if args.reco:
		if not args.version:
			plot.drawLabel(label="Reco samples")

	if drawTheorySysts:
		plot.drawTheoryUncertaintyCurve( f.Get("Obs_0_Up") )
		plot.drawTheoryUncertaintyCurve( f.Get("Obs_0_Down") )
		# coordinate in NDC
		plot.drawTheoryLegendLines( xyCoord=(0.234,0.6625), length=0.057 )

	plot.decorateCanvas( )
	plot.writePlot( )


if __name__ == "__main__":
    main()
