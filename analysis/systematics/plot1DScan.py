#!/usr/bin/env python
from __future__ import absolute_import
from __future__ import print_function
import ROOT
import math
from functools import partial
import CombineHarvester.CombineTools.plotting as plot
import json
import argparse
import os.path
from six.moves import range

import Analysis.Tools.syncer
from tttt.Tools.user                     import plot_directory
import RootTools.plot.helpers as plot_helpers


ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(ROOT.kTRUE)

plot.ModTDRStyle(width=700, l=0.13)
ROOT.gStyle.SetNdivisions(510, "XYZ")
ROOT.gStyle.SetMarkerSize(0.7)

argParser = argparse.ArgumentParser()

argParser.add_argument('main', help='Main input file for the scan')
argParser.add_argument('--y-cut', type=float, default=8., help='Remove points with y > y-cut')
argParser.add_argument('--y-max', type=float, default=8., help='y-axis maximum')
argParser.add_argument('--output', '-o', help='output name without file extension', default='limitPlot')
argParser.add_argument('--POI', help='use this parameter of interest', default='r')
argParser.add_argument('--translate', default=None, help='json file with POI name translation')
#argParser.add_argument('--main-label', default='Observed', type=str, help='legend label for the main scan')
argParser.add_argument('--main-color', default=1, type=int, help='line and marker color for main scan')
argParser.add_argument('--others', nargs='*', help='add secondary scans processed as main: FILE:LABEL:COLOR')
argParser.add_argument('--breakdown', help='do quadratic error subtraction using --others')
argParser.add_argument('--logo', default='CMS')
argParser.add_argument('--logo-sub', default='Internal')
argParser.add_argument('--plot_directory', action='store', default='4t-limits')
argParser.add_argument('--selection',      action='store', default='combined')
argParser.add_argument('--logLevel',       action='store',      default='INFO', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")

args = argParser.parse_args()

#Logger

import tttt.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)



NAMECOUNTER = 0

def read(scan, param, files, ycut):
    goodfiles = [f for f in files if plot.TFileIsGood(f)]
    limit = plot.MakeTChain(goodfiles, 'limit')
    graph = plot.TGraphFromTree(limit, param, '2*deltaNLL', 'quantileExpected > -1.5')
    graph.SetName(scan)
    graph.Sort()
    plot.RemoveGraphXDuplicates(graph)
    plot.RemoveGraphYAbove(graph, ycut)
    # graph.Print()
    return graph


def Eval(obj, x, params):
    return obj.Eval(x[0])


def BuildScan(scan, param, files, color, yvals, ycut):
    graph = read(scan, param, files, ycut)
    if graph.GetN() <= 1:
        graph.Print()
        raise RuntimeError('Attempting to build %s scan from TGraph with zero or one point (see above)' % files)
    bestfit = None
    for i in range(graph.GetN()):
        if graph.GetY()[i] == 0.:
            bestfit = graph.GetX()[i]
    graph.SetMarkerColor(color)
    spline = ROOT.TSpline3("spline3", graph)
    global NAMECOUNTER
    func_method = partial(Eval, spline)
    func = ROOT.TF1('splinefn'+str(NAMECOUNTER), func_method, graph.GetX()[0], graph.GetX()[graph.GetN() - 1], 1)
    func._method = func_method
    NAMECOUNTER += 1
    func.SetLineColor(color)
    func.SetLineWidth(3)
    assert(bestfit is not None)
    crossings = {}
    cross_1sig = None
    cross_2sig = None
    other_1sig = []
    other_2sig = []
    val = None
    val_2sig = None
    for yval in yvals:
        crossings[yval] = plot.FindCrossingsWithSpline(graph, func, yval)
        for cr in crossings[yval]:
            cr["contains_bf"] = cr["lo"] <= bestfit and cr["hi"] >= bestfit
    for cr in crossings[yvals[0]]:
        if cr['contains_bf']:
            val = (bestfit, cr['hi'] - bestfit, cr['lo'] - bestfit)
            cross_1sig = cr
        else:
            other_1sig.append(cr)
    if len(yvals) > 1:
        for cr in crossings[yvals[1]]:
            if cr['contains_bf']:
                val_2sig = (bestfit, cr['hi'] - bestfit, cr['lo'] - bestfit)
                cross_2sig = cr
            else:
                other_2sig.append(cr)
    else:
        val_2sig = (0., 0., 0.)
        cross_2sig = cross_1sig
    return {
        "graph"     : graph,
        "spline"    : spline,
        "func"      : func,
        "crossings" : crossings,
        "val"       : val,
        "val_2sig": val_2sig,
        "cross_1sig" : cross_1sig,
        "cross_2sig" : cross_2sig,
        "other_1sig" : other_1sig,
        "other_2sig" : other_2sig
    }

#plot_directory_ = os.path.join(plot_directory, 'test/limit-plots')
plot_directory_ = os.path.join(plot_directory, 'analysisPlots', args.plot_directory, 'RunII', args.selection)
plotName = plot_directory_ +"/"+ args.output


fixed_name = args.POI
if args.translate is not None:
    with open(args.translate) as jsonfile:
        name_translate = json.load(jsonfile)
    if args.POI in name_translate:
        fixed_name = name_translate[args.POI]

yvals = [1., 4.]


main_scan = BuildScan(plotName, args.POI, [args.main], args.main_color, yvals, args.y_cut)

other_scans = [ ]
other_scans_opts = [ ]
if args.others is not None:
    for oargs in args.others:
        splitargs = oargs.split(':')
        other_scans_opts.append(splitargs)
        other_scans.append(BuildScan(plotName, args.POI, [splitargs[0]], int(splitargs[2]), yvals, args.y_cut))


canv = ROOT.TCanvas(plotName, args.output)
pads = plot.OnePad()
main_scan['graph'].SetMarkerColor(ROOT.kBlue+2)
main_scan['graph'].Draw('AP')

axishist = plot.GetAxisHist(pads[0])

axishist.SetMinimum(min(main_scan['graph'].GetY()))
axishist.SetMaximum(args.y_max)
axishist.GetYaxis().SetTitle("- 2 #Delta ln L")
axishist.GetXaxis().SetTitle("%s" % fixed_name)

new_min = axishist.GetXaxis().GetXmin()
new_max = axishist.GetXaxis().GetXmax()
mins = []
maxs = []
for other in other_scans:
    mins.append(other['graph'].GetX()[0])
    maxs.append(other['graph'].GetX()[other['graph'].GetN()-1])

if len(other_scans) > 0:
    if min(mins) < main_scan['graph'].GetX()[0]:
        new_min = min(mins) - (main_scan['graph'].GetX()[0] - new_min)
    if max(maxs) > main_scan['graph'].GetX()[main_scan['graph'].GetN()-1]:
        new_max = max(maxs) + (new_max - main_scan['graph'].GetX()[main_scan['graph'].GetN()-1])
    axishist.GetXaxis().SetLimits(new_min, new_max)

for other in other_scans:
    if args.breakdown is not None:
        other['graph'].SetMarkerSize(0.4)
    other['graph'].Draw('PSAME')

line = ROOT.TLine()
line.SetLineColor(16)
line.SetLineStyle(7)
for yval in yvals:
    plot.DrawHorizontalLine(pads[0], line, yval)
    if (len(other_scans) == 0):
        for cr in main_scan['crossings'][yval]:
            if cr['valid_lo']: 
		    line.DrawLine(cr['lo'], 0, cr['lo'], yval)
	    if cr['valid_hi']: 
		    line.DrawLine(cr['hi'], 0, cr['hi'], yval)
x1 = main_scan['crossings'][1][0]['lo']
x2 = main_scan['crossings'][1][0]['hi']
x3 = main_scan['crossings'][4][0]['lo']
x4 = main_scan['crossings'][4][0]['hi']
box1 = ROOT.TBox(x1, 0, x2, args.y_max)            		
box1.SetFillColorAlpha(ROOT.kCyan-2, 0.5)
box1.Draw()
box2 = ROOT.TBox(x3, 0, x4, args.y_max)
box2.SetFillColorAlpha(ROOT.kCyan-7, 0.5)
box2.Draw()

main_scan['func'].Draw('same')
for other in other_scans:
    if args.breakdown is not None:
        other['func'].SetLineStyle(2)
        other['func'].SetLineWidth(2)
    other['func'].Draw('SAME')



box = ROOT.TBox(axishist.GetXaxis().GetXmin(), 0.625*args.y_max, axishist.GetXaxis().GetXmax(), args.y_max)
#box.Draw()
pads[0].GetFrame().Draw()
pads[0].RedrawAxis()

crossings = main_scan['crossings']
val_nom = main_scan['val']
val_2sig = main_scan['val_2sig']

textfit = '%s = %.3f{}^{#plus %.3f}_{#minus %.3f}' % (fixed_name, val_nom[0], val_nom[1], abs(val_nom[2]))


pt = ROOT.TPaveText(0.59, 0.82 - len(other_scans)*0.08, 0.95, 0.91, 'NDCNB')
pt.AddText(textfit)

if args.breakdown is None:
    for i, other in enumerate(other_scans):
        textfit = '#color[%s]{%s = %.3f{}^{#plus %.3f}_{#minus %.3f}}' % (other_scans_opts[i][2], fixed_name, other['val'][0], other['val'][1], abs(other['val'][2]))
        pt.AddText(textfit)


if args.breakdown is not None:
    pt.SetX1(0.50)
    if len(other_scans) >= 3:
        pt.SetX1(0.19)
        pt.SetX2(0.88)
        pt.SetY1(0.66)
        pt.SetY2(0.82)
    breakdown = args.breakdown.split(',')
    v_hi = [val_nom[1]]
    v_lo = [val_nom[2]]
    for other in other_scans:
        v_hi.append(other['val'][1])
        v_lo.append(other['val'][2])
    assert(len(v_hi) == len(breakdown))
    textfit = '%s = %.3f' % (fixed_name, val_nom[0])
    for i, br in enumerate(breakdown):
        if i < (len(breakdown) - 1):
            if (abs(v_hi[i+1]) > abs(v_hi[i])):
                print('ERROR SUBTRACTION IS NEGATIVE FOR %s HI' % br)
                hi = 0.
            else:
                hi = math.sqrt(v_hi[i]*v_hi[i] - v_hi[i+1]*v_hi[i+1])
            if (abs(v_lo[i+1]) > abs(v_lo[i])):
                print('ERROR SUBTRACTION IS NEGATIVE FOR %s LO' % br)
                lo = 0.
            else:
                lo = math.sqrt(v_lo[i]*v_lo[i] - v_lo[i+1]*v_lo[i+1])
        else:
            hi = v_hi[i]
            lo = v_lo[i]
        textfit += '{}^{#plus %.3f}_{#minus %.3f}(%s)' % (hi, abs(lo), br)
    pt.AddText(textfit)


pt.SetTextAlign(11)
pt.SetTextFont(42)
#pt.Draw()

#plot.DrawCMSLogo(pads[0], args.logo, args.logo_sub, 11, 0.045, 0.035, 1.2,  cmsTextSize = 1.)

legend_l = 0.69
if len(other_scans) > 0:
    legend_l = legend_l - len(other_scans) * 0.04
legend = ROOT.TLegend(0.15, legend_l, 0.45, 0.78, '')#, 'NBNDC')
if len(other_scans) >= 3:
    legend = ROOT.TLegend(0.46, 0.83, 0.95, 0.93, '', 'NBNDC')
    legend.SetNColumns(2)

legend.AddEntry(main_scan['func'], args.output, 'L')
for i, other in enumerate(other_scans):
    legend.AddEntry(other['func'], other_scans_opts[i][1], 'L')
#legend.Draw()

#save the plot
if not os.path.exists(plot_directory_):
	try:
		os.makedirs(plot_directory_)
	except OSError: # Resolve rare race condition
		pass

plot_helpers.copyIndexPHP(plot_directory_)

save_graph = main_scan['graph'].Clone()
save_graph.GetXaxis().SetTitle('%s = %.3f %+.3f/%+.3f' % (fixed_name, val_nom[0], val_nom[2], val_nom[1]))
outfile = ROOT.TFile(plotName+'.root', 'RECREATE')
outfile.WriteTObject(save_graph)
outfile.Close()
canv.Print(plotName+'.pdf')
canv.Print(plotName+'.png')

