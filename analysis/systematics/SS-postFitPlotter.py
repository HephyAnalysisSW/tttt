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

#def getData(path):
#	obj = "/postfit/data_obs"
#	hist = getObjFromFile(path,obj)
#	return hist

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
			#print x
			y = hist.GetBinContent(i)
			#print y
			xerr_low = hist.GetBinWidth(i) / 2.0
			xerr_high = hist.GetBinWidth(i) / 2.0
			yerr_low = hist.GetBinErrorLow(i)
			yerr_high = hist.GetBinErrorUp(i)
			graph.SetPoint(i-1, x, y)
			graph.SetPointError(i-1, xerr_low, xerr_high, yerr_low, yerr_high)
			#print "data : ", graph.GetMaximum()
	return graph

import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',       action='store',      default='INFO', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--noData',         action='store_true', default=False,  help='Do not plot data.')
argParser.add_argument('--plot_directory', action='store', default='4t-postfit-v2')
argParser.add_argument('--selection',      action='store', default='combined')
argParser.add_argument('--backgroundOnly', action='store_true', default=False)
argParser.add_argument('--input_directory',action='store', default="dataCards/fitDiagnostics.postFit_combined.root")
argParser.add_argument('--prefit',         action='store_true', default=False, help='Draw prefit plots with Asimov data')
args = argParser.parse_args()


plot_directory = "/user/mshoosht/public_html/Interpretations/Plots/"

if args.backgroundOnly:
	fit = "shapes_fit_b"
else :  fit = "shapes_fit_s"

if args.prefit: fit = "shapes_prefit"

mc = [ 
	{"name": "TTT", "legendText" : "ttt", "color" : color.TTT},
	{"name": "other_t", "legendText" : "other t", "color" : color.Other_t},
	{"name": "Xgamma", "legendText" : "X#gamma", "color" : color.XGamma},
	{"name": "ChargeMisID", "legendText" : "ChargeMisID", "color" : color.Charge_misID},
	{"name": "VVV", "legendText" : "VV(V)", "color" : color.VVV},
	{"name": "WZ", "legendText" : "WZ", "color" : color.VVV},
	{"name": "nonPromptElectron", "legendText" : "NP e", "color" : color.NPe},
	{"name": "nonPromptMuon", "legendText" : "NP #mu", "color" : color.NPmu},
	{"name": "TTW", "legendText" : "t#bar{t}W", "color" : color.TTW},
	{"name": "TTH", "legendText" : "t#bar{t}H", "color" : color.TTH},
	{"name": "TTZ", "legendText" : "t#bar{t}Z", "color" : color.TTZ},
	{"name": "TotalSig", "legendText" : "t#bar{t}t#bar{t}", "color" : color.TTTT}, 
    ]

plots =[	
    {"name":"SR2L_Sig",		"texX":"H_{T}",    	"postfit-file":"SR2L_Sig_combined_postFitPlots.root",	 },
    {"name":"SR2L_ttw",		"texX":"TTX score",     "postfit-file":"SR2L_ttw_combined_postFitPlots.root",    },
    {"name":"SR2L_NP",	 	"texX":"TT score",      "postfit-file":"SR2L_NP_combined_postFitPlots.root",     },
    {"name":"SR3L_Sig",		"texX":"H_{T}",	    	"postfit-file":"SR3L_Sig_combined_postFitPlots.root",	 },
    {"name":"SR3L_ttw",		"texX":"TTX score",     "postfit-file":"SR3L_ttw_combined_postFitPlots.root",    },
    {"name":"SR3L_NP",	 	"texX":"TT score",      "postfit-file":"SR3L_NP_combined_postFitPlots.root",     },
    {"name":"CR2LNP",       	"texX":"TT score",        "postfit-file":"CR2LNP_combined_postFitPlots.root",      },
    {"name":"CR2LTTW",       	"texX":"TT score",       "postfit-file":"CR2LTTW_combined_postFitPlots.root",     },
    {"name":"CR3LZ",        	"texX":"N_{jet}",         "postfit-file":"CR3LZ_combined_postFitPlots.root",       },
    {"name":"CR4LZ",         	"texX":"N_{jet}",         "postfit-file":"CR4LZ_combined_postFitPlots.root",       },
    {"name":"CR3LNP",       	"texX":"N_{jet}",        "postfit-file":"CR3LNP_combined_postFitPlots.root",      },
       ]
for plot in plots: 
  for process in mc:
    plot[process["name"]]=ROOT.TH1F()
    plot["data"]=ROOT.TH1F()

for plot in plots:
      plotter = Plotter(plot["name"])
      inputFile = args.input_directory + plot["postfit-file"]
      #print plot["name"]
      for process in mc:
	     First = True
             for year in ["2016","2017","2018"]:

                histDirName = "SS_"+year+"_"+plot["name"]+"_postfit"
                
                #get the histos
                processHist = getPostFit(process["name"],histDirName,inputFile)
		#print histDirName, process["name"], year
		if processHist : 
		    #print processHist.GetMaximum()
		    if First :
			plot[process["name"]] = processHist.Clone()
			First = False
		    else:
			plot[process["name"]].Add(processHist,1)
                    
	     if plot[process["name"]].GetMaximum()!=0:
	         plotter.addSample(process["name"], plot[process["name"]], process["legendText"], process["color"])
	         #print plot[process["name"]].GetMaximum()
             else: print "This process was not found in this channel :", process["name"],plot["name"]
                
      #get data
      if not args.noData:
	      Data = getPostFitData(inputFile)
              plotter.addData(Data)
      
      
      #get uncertainty 
      UHist = getPostFitUnc(inputFile)
      #print "uhist : ",UHist.GetMaximum()
      
      plotter.addPostFitUnc(UHist)
      #draw the plot
      for log in [False]:
         plot_directory_ = os.path.join(plot_directory, args.plot_directory, args.selection )
         plotter.draw(plot_directory_, log, texX = plot["texX"] , ratio = True )

