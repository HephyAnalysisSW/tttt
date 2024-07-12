import os, sys, shutil
import ROOT
#import Analysis.Tools.syncer
from tttt.Tools.helpers                           import getObjFromFile
#from tttt.Tools.user                              import plot_directory
#import RootTools.plot.helpers as plot_helpers
from tttt.samples.color import color
from tttt.Tools.Plotter import Plotter		


def getPostFit(process,process_dir,path):
	obj = "/"+process_dir+"/"+process
	hist = getObjFromFile(path,obj)
	return hist

def getUncertainty(path,region,fit):
	obj = fit+"/"+region+"/total"
	hist = getObjFromFile(path,obj)
	return hist

def getData(process_dir,path):
	obj = "/"+process_dir+"/data_obs"
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
argParser.add_argument('--input_directory',action='store', default="dataCards/fitDiagnostics.postFit_combined.root")
argParser.add_argument('--prefit',         action='store_true', default=False, help='Draw prefit plots with Asimov data')
#argParser.add_argument('--selections',	   action='store', default="njet4to5-btag2")
args = argParser.parse_args()

#import tttt.Tools.logger as logger
#import RootTools.core.logger as logger_rt
#logger    = logger.get_logger(   args.logLevel, logFile = None)
#logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

plot_directory = "/user/mshoosht/public_html/Interpretations/Plots/"

if args.backgroundOnly:
	fit = "shapes_fit_b"
else :  fit = "shapes_fit_s"

if args.prefit: fit = "shapes_prefit"

mc = [ 
	{"name": "TotalSig", "legendText" : "t#bar{t}t#bar{t}", "color" : color.TTTT}, 
	{"name": "TTT", "legendText" : "ttt", "color" : color.TTT},
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
    {"name":"SR2L_Sig",		"texX":"TTTT score",    "postfit-file":"SR2L_Sig_combined_postFitPlots.root",	"binLabels":["0","","1","","1.5","","2","","2.5","","3"], "nbins": [0,11]},
    {"name":"SR2L_ttw",		"texX":"TTW score",     "postfit-file":"SR2L_ttw_combined_postFitPlots.root",     "binLabels":["0","","1","","1.5","","2","","2.5","","3"], "nbins": [0,11]},
    {"name":"SR2L_NP",	 	"texX":"NP score",      "postfit-file":"SR2L_NP_combined_postFitPlots.root",      "binLabels":["0","","1","","1.5","","2","","2.5","","3"], "nbins": [0,11]},
    {"name":"CR2LNP",       	"texX":"CR2LNP",        "postfit-file":"CR2LNP_combined_postFitPlots.root",        "binLabels":["0","","1","","1.5","","2","","2.5","","3"], "nbins": [0,11]},
    {"name":"CR2LTTW",       	"texX":"CR2LTTW",       "postfit-file":"CR2LTTW_combined_postFitPlots.root",       "binLabels":["0","","1","","1.5","","2","","2.5","","3"], "nbins": [0,11]},
    {"name":"CR3LZ",        	"texX":"CR3LZ",         "postfit-file":"CR3LZ_combined_postFitPlots.root",         "binLabels":["0","","1","","1.5","","2","","2.5","","3"], "nbins": [0,11]},
    {"name":"CR4LZ",         	"texX":"CR4LZ",         "postfit-file":"CR4LZ_combined_postFitPlots.root",         "binLabels":["0","","1","","1.5","","2","","2.5","","3"], "nbins": [0,11]},
    {"name":"CR3LNP",       	"texX":"CR3LNP",        "postfit-file":"CR3LNP_combined_postFitPlots.root",        "binLabels":["0","","1","","1.5","","2","","2.5","","3"], "nbins": [0,11]},
       ]
for plot in plots: 
  for process in mc:
    plot[process["name"]]=ROOT.TH1F()
    plot["data"]=ROOT.TH1F()

for plot in plots:
      plotter = Plotter("SS_"+plot["name"])
      inputFile = args.input_directory + plot["postfit-file"]
      for process in mc:
             for year in ["2016","2017","2018"]:

                histDirName = "SS_"+year+"_"+plot["name"]+"_postfit"
                
                #get the histos
                processHist = getPostFit(process["name"],histDirName,inputFile)
		#print histDirName, process["name"]
		#print processHist.GetMaximum()
                plot[process["name"]].Add(processHist,1)
                
                #get data
                if not args.noData:
                  	Data = getData(histDirName,inputFile)
                  	#plotter.addData(Data)
                  	plot["data"].Add(Data,1)
                
                    
             #get uncertainty 
             UHist = getPostFitUnc(inputFile)
             
             plotter.addPostFitUnc(UHist)
             plotter.addSample(process["name"], plot[process["name"]], process["legendText"], process["color"])
	     if not args.noData: plotter.addData(plot["data"])
      #draw the plot
      for log in [False]:
         plot_directory_ = os.path.join(plot_directory, args.plot_directory, args.selection )
         plotter.draw(plot_directory_, log, texX = plot["texX"] , ratio = True )

#      if plot["hist"]: 
#      	#print process["name"], process["hist"].GetMaximum()
#      	Bigplotter.addSample(process["name"], process["hist"], process["legendText"], process["color"])
#      	plot[process["name"]].Add(process["hist"])
#      	#print plot[process["name"]].GetNbinsX()
#      else:
#          pass 
#          #some selections don't have ST_tch. to be investigated
#
#      for process in mc:
#        Bigplotter.addSample(process["name"], plot[process["name"]], process["legendText"], process["color"])
#        #print plot[process["name"]].GetNbinsX()
#      U2hist = getPostFitUnc(plot["postfit-file"])
#      #Bigplotter.addPostFitUnc(U2hist) 
#      U2Data = getPostFitData(plot["postfit-file"])
#      #Bigplotter.addData(U2Data)
#      for log in [False]:
#			plot_directory_ = os.path.join(plot_directory, args.plot_directory, args.selection )
#			Bigplotter.draw(plot_directory_, log, texX = plot["texX"] , ratio = True , binLabels = plot["binLabels"] , nbins=plot["nbins"])
#
##for plot in plots: print plot[""].GetMaximum()
