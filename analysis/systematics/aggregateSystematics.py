import ROOT,os

import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--plot_directory', action='store', default='4t_syst')
argParser.add_argument('--selection',      action='store', default='trg-dilepL-minDLmass20-offZ1-njet4p-btag3p-ht500')
args = argParser.parse_args()

directory = "/groups/hephy/cms/maryam.shooshtari/www/tttt/plots/analysisPlots/"+args.plot_directory+"/RunII/all/"+args.selection

# Open the output file and create a TDirectoryFile
outFile = ROOT.TFile(os.path.join(directory,"tttt__systematics.root"), "RECREATE")
#make a list of possible discriminating variables
theYounglings = ["nJetGood","2l_4t"]

for theChosenOne in theYounglings :
	category = outFile.mkdir("tttt__"+theChosenOne)
	
	# Possible Syst variations
	variations = ['LeptonSFUp', 
	              'LeptonSFDown',
		      'PUUp',
		      'PUDown',
	              'L1PrefireUp',
		      'L1PrefireDown',
		      #'TriggerUp',
	              #'TriggerDown',
	              'BTagSFJesUp',
		      'BTagSFJesDown',
		      'BTagSFHfUp',
	              'BTagSFHfDown',
	              'BTagSFLfUp',
		      'BTagSFLfDown',
	              'BTagSFHfs1Up',
		      'BTagSFHfs1Down',
		      'BTagSFLfs1Up',
	              'BTagSFLfs1Down',
	              'BTagSFHfs2Up',
		      'BTagSFHfs2Down',
	              'BTagSFLfs2Up',
		      'BTagSFLfs2Down',
	              #'BTagSFCfe1Up',
		      #'BTagSFCfe1Down',
	              #'BTagSFCfe2Up',
		      #'BTagSFCfe2Down',
	              'jesTotalUp',
		      'jesTotalDown',
		      'central'
	              ]
	
	for variation in variations:
	    inFile = ROOT.TFile(os.path.join(directory,"tttt_"+variation+".root"), "READ")
	    for key in inFile.GetListOfKeys():
	      if theChosenOne in key.GetName() and variation not in key.GetName():
	        obj = key.ReadObj()
	        category.cd()
	        clonedHist = obj.Clone()
	        histname = clonedHist.GetName()
		if "TTLep_bb" in histname: process = "TTLep_bb"
	        elif "TTLep_cc" in histname: process = "TTLep_cc"
	        elif "TTLep_other" in histname: process = "TTLep_other"
	        #elif "ST" in histname: process = "ST"
		elif "ST_tch" in histname: process = "ST_tch"
		elif "ST_twch" in histname: process = "ST_twch"
		elif "TTTT" in histname : process = "TTTT"
	        elif "TTW" in histname: process = "TTW"
	        elif "TTZ" in histname: process = "TTZ"
	        elif "TTH" in histname: process = "TTH"
		if "data" not in clonedHist.GetTitle(): 
			if variation == "central":
				clonedHist.Write(process)
			else:
	        		clonedHist.Write(process+"__"+variation)
		if "data" in histname: clonedHist.Write("data_obs")
		
	    inFile.Close()
	
outFile.Close()
