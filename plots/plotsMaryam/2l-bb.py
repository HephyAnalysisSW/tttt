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
bbTag_mean_pt = "MaxIf$(Sum$(JetGood_pt)/Length$(JetGood_pt), (JetGood_btagDeepFlavbb/(JetGood_btagDeepFlavb+JetGood_btagDeepFlavlepb))/Max$(JetGood_btagDeepFlavbb/(JetGood_btagDeepFlavb+JetGood_btagDeepFlavlepb))!=1)"
bTag_max_pt    = "MaxIf$(JetGood_pt, (JetGood_btagDeepFlavb/(JetGood_btagDeepFlavbb+JetGood_btagDeepFlavlepb))/Max$(JetGood_btagDeepFlavb/(JetGood_btagDeepFlavbb+JetGood_btagDeepFlavlepb))==1)"
bbTag_max_value   = "Max$(JetGood_btagDeepFlavbb/(JetGood_btagDeepFlavb+JetGood_btagDeepFlavlepb))"

plots = []

h1 = sample.get1DHistoFromDraw(bbTag_max_pt, [100,0,1500], weightString = "weight*137*((genTtbarId%100)>=52&&(genTtbarId%100)!=53&&"+cutInterpreter.cutString(args.selection)+")", addOverFlowBin = 'upper')
h2 = sample.get1DHistoFromDraw(bbTag_max_pt, [100,0,1500], weightString = "weight*137*((genTtbarId%100)==51||(genTtbarId%100)==53&&"+cutInterpreter.cutString(args.selection)+")", addOverFlowBin = 'upper')
h7 = sample.get1DHistoFromDraw(bbTag_mean_pt, [100,0,1500], weightString = "weight*137*((genTtbarId%100)>=52&&(genTtbarId%100)!=53&&"+cutInterpreter.cutString(args.selection)+")", addOverFlowBin = 'upper')
h8 = sample.get1DHistoFromDraw(bbTag_mean_pt, [100,0,1500], weightString = "weight*137*((genTtbarId%100)==51||(genTtbarId%100)==53&&"+cutInterpreter.cutString(args.selection)+")", addOverFlowBin = 'upper')
h1.SetLineColor(2)
h2.SetLineColor(8)
h7.SetLineColor(632+2)
h8.SetLineColor(416-1)
h1.legendText = "max_pt Gen bb"
h2.legendText = "max_pt Gen b"
h7.legendText = "mean_pt Gen bb"
h8.legendText = "mean_pt Gen b"
plots.append(Plot.fromHisto(name="max bbTaged jet's pt", histos=[[h1],[h2],[h7],[h8]], texX="pt", texY="Number of Events"))

h3 = sample.get1DHistoFromDraw(bTag_max_pt, [100,0,1500], weightString =  "weight*137*((genTtbarId%100)>=52&&(genTtbarId%100)!=53&&"+cutInterpreter.cutString(args.selection)+")")
h4 = sample.get1DHistoFromDraw(bTag_max_pt, [100,0,1500], weightString =  "weight*137*((genTtbarId%100)==51||(genTtbarId%100)==53&&"+cutInterpreter.cutString(args.selection)+")")
h3.SetLineColor(2)
h4.SetLineColor(8)
h3.legendText = "max_pt Gen bb"
h4.legendText = "max_pt Gen b"
plots.append(Plot.fromHisto(name="max bTaged jet's pt", histos=[[h3],[h4]], texX="pt", texY="Number of Events"))

h51 = sample.get1DHistoFromDraw(bbTag_max_pt , [100,0,1500], weightString =  "weight*137*((genTtbarId%100)==51&&"+cutInterpreter.cutString(args.selection)+")")
h52 = sample.get1DHistoFromDraw(bbTag_max_pt , [100,0,1500], weightString =  "weight*137*((genTtbarId%100)==52&&"+cutInterpreter.cutString(args.selection)+")")
h53 = sample.get1DHistoFromDraw(bbTag_max_pt , [100,0,1500], weightString =  "weight*137*((genTtbarId%100)==53&&"+cutInterpreter.cutString(args.selection)+")")
h54 = sample.get1DHistoFromDraw(bbTag_max_pt , [100,0,1500], weightString =  "weight*137*((genTtbarId%100)==54&&"+cutInterpreter.cutString(args.selection)+")")
h55 = sample.get1DHistoFromDraw(bbTag_max_pt , [100,0,1500], weightString =  "weight*137*((genTtbarId%100)==55&&"+cutInterpreter.cutString(args.selection)+")")
h52.SetLineColor(632+1)
h54.SetLineColor(632+2)
h55.SetLineColor(632-7)
h53.SetLineColor(416+3)
h51.SetLineColor(416-9)
h51.legendText = "1bjet 1Bhadron"
h52.legendText = "1bjet 2pBhadrons"
h53.legendText = "2bjet 1Bhadron"
h54.legendText = "2bjet with 2pBhadrons and 1Bhadron"
h55.legendText = "2bjet both with 2pBhadrons"
plots.append(Plot.fromHisto(name="max bbTaged jet's pt _ separated", histos=[[h51],[h52],[h53],[h54],[h55]], texX="pt", texY="Number of Events"))

h5 = sample.get1DHistoFromDraw(bbTag_max_value, [20,0,1], weightString = "weight*137*((genTtbarId%100)>=52&&(genTtbarId%100)!=53&&"+cutInterpreter.cutString(args.selection)+")")
h6 = sample.get1DHistoFromDraw(bbTag_max_value, [20,0,1], weightString = "weight*137*((genTtbarId%100)==51||(genTtbarId%100)==53&&"+cutInterpreter.cutString(args.selection)+")")
h5.SetLineColor(2)
h6.SetLineColor(8)
h5.legendText = "bbTag_value Gen bb"
h6.legendText = "bbTag_value Gen b"
plots.append(Plot.fromHisto(name="max bbTaged discriminator value", histos=[[h5],[h6]], texX="bb/(b+lepb)", texY="Number of Events"))

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
