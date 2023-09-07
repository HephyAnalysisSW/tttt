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
argParser.add_argument('--noData',         action='store_true', default=False,  help='Do not plot data.')
argParser.add_argument('--plot_directory', action='store', default='4t-postfit-v2')
argParser.add_argument('--selection',      action='store', default='combined')
argParser.add_argument('--backgroundOnly', action='store_true', default=False)
argParser.add_argument('--inputFile',	   action='store', default="dataCards/fitDiagnostics.postFit_combined.root")
#argParser.add_argument('--selections',	   action='store', default="njet4to5-btag2")
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
	{"name": "DY_inclusive", "legendText" : "DY", "color" : color.DY},
	{"name": "DiBoson", "legendText" : "DiBoson", "color" : color.W},
	{"name": "TTTT", "legendText" : "t#bar{t}t#bar{t}", "color" : color.TTTT} ]

selections =["njet4to5_btag2","njet4to5_btag3p","njet6to7_btag2","njet8p_btag2","njet4to5_btag1","njet6to7_btag1","njet8p_btag1"]#,"njet6to7_btag3p","njet8p_btag3p"]
plots =[	
		{"name":"mva",		"texX":"2l_4t",		"binLabels":["0.1","0.2","0.3","0.4","0.5","0.6","0.7","0.8","0.9","1"], "nbins": [0,10]},
		{"name":"nJetGood",	"texX":"N_{Jet}",       "binLabels":["4","5","6","7","8","9","10","11"], "nbins": [0,8]},
		{"name":"nBTag",	"texX":"N_{BJet}",      "binLabels":["0","1","2","3","4","5","6"], "nbins": [0,7]},
		{"name":"ht",       	"texX":"ht",     	"binLabels":None , "nbins": [0,30]},
       ]
for plot in plots:
   for region in selections:
   
      plotName = plot["name"]+"_"+region
   
      if args.backgroundOnly:	plotter = Plotter(plotName+'_bOnly')
      else: 			plotter = Plotter(plotName)
   
      #get the histos
      for process in mc:
      	process["hist"] = getPostFit(process["name"],args.inputFile,plotName,fit)
   	plotter.addSample(process["name"], process["hist"], process["legendText"], process["color"])
   	  
      #get uncertainty
      
      UHist = getUncertainty(args.inputFile,plotName,fit)
      plotter.addPostFitUnc(UHist)
     
      #get data
      if not args.noData:
   	Data = getData(args.inputFile,plotName,fit)
   	plotter.addData(Data)

      #draw the plot
      for log in [False,True]:
         plot_directory_ = os.path.join(plot_directory, 'analysisPlots', args.plot_directory, 'RunII', "all" + ("_log" if log else ""), args.selection )
         plotter.draw(plot_directory_, log, texX = plot["texX"] , ratio = True , binLabels = plot["binLabels"] , nbins=plot["nbins"] )
   
