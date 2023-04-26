import os, sys
import ROOT
import Analysis.Tools.syncer
from tttt.Tools.helpers                           import getObjFromFile
from tttt.Tools.user                              import plot_directory
import RootTools.plot.helpers as plot_helpers
from tttt.samples.color import color
from tttt.Tools.Plotter import Plotter		


def getPostFit(process,path,region,fit):
	obj = "/"+fit+"/"+region+"/"+process
	hist = getObjFromFile(path,obj)
	return hist

def getUncertainty(path,region,fit):
	obj = fit+"/"+region+"/total"
	hist = getObjFromFile(path,obj)
	return hist

def getData(path,region,fit):
	obj = fit+"/"+region+"/data"
	hist = getObjFromFile(path,obj)
	return hist


import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',       action='store',      default='INFO', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--noData',         action='store_true', default=True,  help='Do not plot data.')
argParser.add_argument('--plot_directory', action='store', default='4t_postfit')
argParser.add_argument('--backgroundOnly', action='store_true', default=False)
argParser.add_argument('--inputFile',	   action='store', default="dataCards/fitDiagnostics.postFit_combined.root")
args = argParser.parse_args()

import tttt.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)


if args.backgroundOnly:
	fit = "shapes_fit_b"
else :  fit = "shapes_fit_s"


mc = [ 	{"name": "TTLep_bb", "legendText" : "t#bar{t}b#bar{b}", "color" : ROOT.kRed + 2},
	{"name": "TTLep_cc", "legendText" : "t#bar{t}c#bar{c}", "color" : ROOT.kRed - 3},
	{"name": "TTLep_other", "legendText" : "t#bar{t} + light j.", "color" : color.TT},
#       {"name": "ST", "legendText" : "t/tW", "color" : color.T},
	{"name": "ST_tch", "legendText" : "t", "color" : color.T},
	{"name": "ST_twch", "legendText" : "tW", "color" : color.tW},
	{"name": "TTW", "legendText" : "t#bar{t}W", "color" : color.TTW},
	{"name": "TTH", "legendText" : "t#bar{t}H", "color" : color.TTH},
	{"name": "TTZ", "legendText" : "t#bar{t}Z", "color" : color.TTZ},
	{"name": "TTTT", "legendText" : "t#bar{t}t#bar{t}", "color" : color.TTTT} ]

selections =["SR","CR1","CR2","CR3","CR4","CR5"]

for region in selections:

   plotName = region
   if region=="SR": plotName="nJet6to7_bTag3"
   elif region=="CR1": plotName="nJet4to5_bTag3"
   elif region=="CR2": plotName="nJet8p_bTag3"
   elif region=="CR3": plotName="nJet4to5_bTag2"
   elif region=="CR4": plotName="nJet6to7_bTag2"
   elif region=="CR5": plotName="nJet8p_bTag2"
   if args.backgroundOnly: plotName += '_bOnly'

   plotter = Plotter(plotName)

   #get the histos
   for process in mc:
   	process["hist"] = getPostFit(process["name"],args.inputFile,region,fit)
	plotter.addSample(process["name"], process["hist"], process["legendText"], process["color"])
	  
   #get uncertainty
   
   UHist = getUncertainty(args.inputFile,region,fit)
   plotter.addPostFitUnc(UHist)
  
   #get data
   if not args.noData:
	Data = getData(args.inputFile,region,fit)
	plotter.addData(Data)
   
   #draw the plot
   for log in [False,True]:
      plot_directory_ = os.path.join(plot_directory, 'analysisPlots', '4t_postFit', 'RunII', "all" + ("_log" if log else "") )
      plotter.draw(plot_directory_, log, texX = "2l_4t" , ratio = True )

