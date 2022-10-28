import os
import ROOT
from tttt.Tools.cutInterpreter           import cutInterpreter
from tttt.Tools.user                     import plot_directory
from RootTools.core.standard             import *
import Analysis.Tools.syncer

import tttt.samples.nano_private_UL20_RunII_postProcessed_dilep as samples
sample = samples.TTLep

import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',       action='store',      default='INFO',      nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--plot_directory', action='store',      default='bb')
argParser.add_argument('--small',       action='store_true',                                                                        help="Run the file on a small sample (for test purpose), bool flag set to True if used" )
argParser.add_argument('--selection',      action='store', default='dilepL-offZ1-njet4p-btag2p-ht500')
args = argParser.parse_args()

import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

if args.small:
    sample.reduceFiles( to = 1 )

if args.small:args.plot_directory += "_small"


plot_directory_ = os.path.join(plot_directory, 'analysisPlots', args.plot_directory, args.selection)


# ev = ROOT.TChain("Events")
# ev.Add("/scratch-cbe/users/robert.schoefbeck/tttt/nanoTuples/tttt_v1/UL2018/dilep/TTLep_pow_CP5/*.root")

bbTag_max_pt   = "MaxIf$(JetGood_pt, (JetGood_btagDeepFlavbb/(JetGood_btagDeepFlavb+JetGood_btagDeepFlavlepb))/Max$(JetGood_btagDeepFlavbb/(JetGood_btagDeepFlavb+JetGood_btagDeepFlavlepb))==1)"
bTag_max_pt    = "MaxIf$(JetGood_pt, (JetGood_btagDeepFlavb/(JetGood_btagDeepFlavbb+JetGood_btagDeepFlavlepb))/Max$(JetGood_btagDeepFlavb/(JetGood_btagDeepFlavbb+JetGood_btagDeepFlavlepb))==1)"
bbTag_max_value   = "Max$(JetGood_btagDeepFlavbb/(JetGood_btagDeepFlavb+JetGood_btagDeepFlavlepb))"
# this will not work: You're giving the mean of ALL jets IF the second condition is true for ANY jet, otherwise zero. -> Try Sum$ always with a TChain::Scan :-)
bbTag_mean_pt  = "MaxIf$(Sum$(JetGood_pt)/Length$(JetGood_pt), (JetGood_btagDeepFlavbb/(JetGood_btagDeepFlavb+JetGood_btagDeepFlavlepb))/Max$(JetGood_btagDeepFlavbb/(JetGood_btagDeepFlavb+JetGood_btagDeepFlavlepb))!=1)"

# it is better to use ROOT.kBlue etc. instead of the numerical value. We'd like to look at the plot and the code at the same time.
plot_cfgs = [
    {'name':'max_bb_pt', 'histos': [
        {'legendText':'max(p_{T}) Gen bb',  'var':bbTag_max_pt,   'color':2,     'binning':[100,0,1500], 'selection':"(genTtbarId%100)>=52&&(genTtbarId%100)!=53"},
        {'legendText':'max(p_{T}) Gen b',   'var':bbTag_max_pt,   'color':8,     'binning':[100,0,1500], 'selection':"((genTtbarId%100)==51||(genTtbarId%100)==53)"},
    # this is likely meaningless (see above)
        {'legendText':'mean(p_{T}) Gen bb', 'var':bbTag_mean_pt,  'color':632+2, 'binning':[100,0,1500], 'selection':"(genTtbarId%100)>=52&&(genTtbarId%100)!=53"},
        {'legendText':'mean(p_{T}) Gen b',  'var':bbTag_mean_pt,  'color':416-1, 'binning':[100,0,1500], 'selection':"((genTtbarId%100)==51||(genTtbarId%100)==53)"},
    ]},
    # this seems redundant: 
    {'name': 'max_b_pt', 'histos': [
        {'legendText':'max(p_{T}) Gen bb', 'var':bbTag_max_pt,    'color':2,      'binning':[100,0,1500], 'selection':"(genTtbarId%100)>=52&&(genTtbarId%100)!=53"},
        {'legendText':'max(p_{T}) Gen b',  'var':bbTag_max_pt,    'color':8,      'binning':[100,0,1500], 'selection':"((genTtbarId%100)==51||(genTtbarId%100)==53)"},
    ]},
    # the ratio can be any positive number, not just between [0,1]
    {'name':'bb_over_blepb', 'histos': [
        {'legendText':'bbTag_value Gen bb','var':bbTag_max_value, 'color':2,     'binning':[20,0,2], 'selection':"(genTtbarId%100)>=52&&(genTtbarId%100)!=53"},
        {'legendText':'bbTag_value Gen b', 'var':bbTag_max_value, 'color':8,     'binning':[20,0,2], 'selection':"((genTtbarId%100)==51||(genTtbarId%100)==53)"},
    ]},
]

plots = []
for plot_cfg in plot_cfgs:

    for histo in plot_cfg['histos']:
        histo['h'] = sample.get1DHistoFromDraw(histo['var'], histo['binning'], weightString = "weight*137*({sel})&&".format(sel=histo['selection'])+cutInterpreter.cutString(args.selection), addOverFlowBin = 'upper')
        histo['h'].SetLineColor(histo['color'])
        histo['h'].legendText = histo['legendText'] 

    plots.append(Plot.fromHisto(name=plot_cfg['name'], histos=[[histo['h']] for h in plot_cfg['histos']], texX="pt", texY="Number of Events"))


for plot in plots:
  if not max(l.GetMaximum() for l in sum(plot.histos,[])): continue # Empty plot

  if isinstance( plot, Plot):
      plotting.draw(plot,
        plot_directory = plot_directory_,
        ratio = None ,
        logX = False, logY = True, sorting = True,
        yRange = (0.9, "auto"),
        legend = ( (0.18,0.88-0.03*sum(map(len, plot.histos)),0.9,0.88), 2),
        copyIndexPHP = True, extensions = ["png", "pdf", "root"],
      )

Analysis.Tools.syncer.sync()
