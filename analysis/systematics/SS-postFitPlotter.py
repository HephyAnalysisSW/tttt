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

def getPostFitUnc(path):
    obj="postfit/TotalProcs"
    hist=getObjFromFile(path,obj)
    return hist

def getPostFitData(path):
	obj="postfit/data_obs"
	hist=getObjFromFile(path,obj)
	# Convert TH1F to TGraphAsymmErrors
	graph = ROOT.TGraphAsymmErrors()	
	for i in range(1, hist.GetNbinsX() + 1):
			x = hist.GetBinCenter(i)
			print x
			y = hist.GetBinContent(i)
			xerr_low = hist.GetBinWidth(i) / 2.0
			xerr_high = hist.GetBinWidth(i) / 2.0
			yerr_low = hist.GetBinErrorLow(i)
			yerr_high = hist.GetBinErrorUp(i)
			graph.SetPoint(i-1, i, y)
			graph.SetPointError(i-1, xerr_low, xerr_high, yerr_low, yerr_high)
	return hist

import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',       action='store',      default='INFO', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--noData',         action='store_true', default=False,  help='Do not plot data.')
argParser.add_argument('--plot_directory', action='store', default='4t-postfit-v2')
argParser.add_argument('--selection',      action='store', default='combined')
argParser.add_argument('--backgroundOnly', action='store_true', default=False)
argParser.add_argument('--inputFile',	   action='store', default="dataCards/fitDiagnostics.postFit_combined.root")
argParser.add_argument('--prefit',         action='store_true', default=False, help='Draw prefit plots with Asimov data')
#argParser.add_argument('--selections',	   action='store', default="njet4to5-btag2")
args = argParser.parse_args()

import tttt.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)


if args.backgroundOnly:
	fit = "shapes_fit_b"
else :  fit = "shapes_fit_s"

if args.prefit: fit = "shapes_prefit"

mc = [ 
	{"name": "total_signal", "legendText" : "t#bar{t}t#bar{t}", "color" : color.TTTT}, 
	{"name": "ttt", "legendText" : "ttt", "color" : color.TTT},
	{"name": "other_t", "legendText" : "other t", "color" : color.Other_t},
	{"name": "Xgamma", "legendText" : "X#gamma", "color" : color.XGamma},
	{"name": "ChargeMisID", "legendText" : "ChargeMisID", "color" : color.Charge_misID},
	{"name": "VVV", "legendText" : "VV(V)", "color" : color.VVV},
	{"name": "nonPromptElectron", "legendText" : "NP e", "color" : color.NPe},
	{"name": "nonPromptMuon", "legendText" : "NP #mu", "color" : color.NPmu},
	{"name": "TTW", "legendText" : "t#bar{t}W", "color" : color.TTW},
	{"name": "TTH", "legendText" : "t#bar{t}H", "color" : color.TTH},
	{"name": "TTZ", "legendText" : "t#bar{t}Z", "color" : color.TTZ},
    ]

#selections =[#"njet4to5_btag3p","njet4to5_btag2","njet4to5_btag1","njet6to7_btag3p","njet6to7_btag2","njet6to7_btag1","njet8p_btag3p","njet8p_btag2","njet8p_btag1"]
plots =[	
    {"name":"SR2L_ttttClass",	"texX":"TTTT score",    "postfit-file":"SR2L_ttttClass_postfit.root",	"binLabels":["0","","1","","1.5","","2","","2.5","","3"], "nbins": [0,11]},
    {"name":"SR2L_ttwClass",	"texX":"TTW score",     "postfit-file":"SR2L_ttwClass_postfit.root",     "binLabels":["0","","1","","1.5","","2","","2.5","","3"], "nbins": [0,11]},
    {"name":"SR2L_NPClass", 	"texX":"NP score",      "postfit-file":"SR2L_NPClass_postfit.root",      "binLabels":["0","","1","","1.5","","2","","2.5","","3"], "nbins": [0,11]},
    {"name":"CR2LNP",       	"texX":"CR2LNP",        "postfit-file":"CR2LNP_postfit.root",        "binLabels":["0","","1","","1.5","","2","","2.5","","3"], "nbins": [0,11]},
    {"name":"CR2LTTW",       	"texX":"CR2LTTW",       "postfit-file":"CR2LTTW_postfit.root",       "binLabels":["0","","1","","1.5","","2","","2.5","","3"], "nbins": [0,11]},
    {"name":"CR3LZ",        	"texX":"CR3LZ",         "postfit-file":"CR3LZ_postfit.root",         "binLabels":["0","","1","","1.5","","2","","2.5","","3"], "nbins": [0,11]},
    {"name":"CR4LZ",         	"texX":"CR4LZ",         "postfit-file":"CR4LZ_postfit.root",         "binLabels":["0","","1","","1.5","","2","","2.5","","3"], "nbins": [0,11]},
    {"name":"CR3LNP",       	"texX":"CR3LNP",        "postfit-file":"CR3LNP_postfit.root",        "binLabels":["0","","1","","1.5","","2","","2.5","","3"], "nbins": [0,11]},
       ]
for plot in plots: 
  for process in mc:
    plot[process["name"]]=ROOT.TH1F()
    #plot["data"]=ROOT.TGraphAsymmErrors()

for plot in plots:
      Bigplotter = Plotter("SS_"+plot["name"])
      for year in ["2016","2017","2018"]:

	      plotName = "SS_"+year+"_"+plot["name"]
	   
	      if args.backgroundOnly:	plotter = Plotter(plotName+'_bOnly')
	      else: 			plotter = Plotter(plotName)
	   
	      #get the histos
	      for process in mc:
			process["hist"] = getPostFit(process["name"],args.inputFile,plotName,fit)
			if process["hist"]: 
				#print process["name"], process["hist"].GetMaximum()
				plotter.addSample(process["name"], process["hist"], process["legendText"], process["color"])
				plot[process["name"]].Add(process["hist"])
				#print plot[process["name"]].GetNbinsX()
			else:
			    pass 
			    #some selections don't have ST_tch. to be investigated
	   	  
	      #get uncertainty
	      
	      UHist = getUncertainty(args.inputFile,plotName,fit)
	      plotter.addPostFitUnc(UHist)
	     
	      #get data
	      if not args.noData:
			Data = getData(args.inputFile,plotName,fit)
			#if args.prefit : Data = getData(args.inputFile,plotName,"shapes_fit_s")
			plotter.addData(Data)
			#plot["data"].Add(Data)
	
	      #draw the plot
	      for log in [False,True]:
	         plot_directory_ = os.path.join(plot_directory, 'analysisPlots', args.plot_directory, 'RunII', "all" + ("_log" if log else ""), args.selection )
	         #plotter.draw(plot_directory_, log, texX = plot["texX"] , ratio = True , binLabels = plot["binLabels"] , nbins=plot["nbins"] )
	  
      for process in mc:
        Bigplotter.addSample(process["name"], plot[process["name"]], process["legendText"], process["color"])
        #print plot[process["name"]].GetNbinsX()
      U2hist = getPostFitUnc(plot["postfit-file"])
      #Bigplotter.addPostFitUnc(U2hist) 
      U2Data = getPostFitData(plot["postfit-file"])
      #Bigplotter.addData(U2Data)
      for log in [False,True]:
			plot_directory_ = os.path.join(plot_directory, 'analysisPlots', args.plot_directory, 'RunII', "all" + ("_log" if log else ""), args.selection )
			Bigplotter.draw(plot_directory_, log, texX = plot["texX"] , ratio = True , binLabels = plot["binLabels"] , nbins=plot["nbins"])

#for plot in plots: print plot[""].GetMaximum()
