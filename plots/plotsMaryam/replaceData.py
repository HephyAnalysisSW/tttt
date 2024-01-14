import ROOT
from tttt.Tools.user                              import plot_directory
from tttt.Tools.helpers                           import getObjFromFile

def getData(path,region,fit):
	obj = fit+"/"+region+"/data"
	hist = getObjFromFile(path,obj)
	return hist

def graph_to_hist(graph):
    hist = ROOT.TH1D("hist", "Graph to Histogram", graph.GetN(), 0, graph.GetN())

    for i in range(graph.GetN()):
        x = graph.GetX()[i]
        y = graph.GetY()[i]
        error_low = graph.GetErrorYlow(i)
        error_high = graph.GetErrorYhigh(i)

        hist.SetBinContent(i + 1, y)
        hist.SetBinError(i + 1, max(error_low, error_high))  # Assuming symmetric errors

    return hist

import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--plot_directory', action='store', default='4t-v15-syst/')
argParser.add_argument('--combine_file',      action='store', default="../../analysis/systematics/dataCards/v17/ht_combined_asimov/fitDiagnostics.postFit_combined.root")
args = argParser.parse_args()

combine_file = ROOT.TFile("../../analysis/systematics/dataCards/v17/ht_combined_asimov/fitDiagnostics.postFit_combined.root", "READ")
selections =[
"njet4to5_btag2","njet6to7_btag2","njet4to5_btag1","njet6to7_btag1","njet8p_btag2","njet8p_btag1","njet8p_btag3p"]
#"mvaCut2p_njet4to5_btag3p"]
#"mvaCut2m_njet4to5_btag3p"]
#"mvaCut1p_njet6to7_btag3p"]
#"mvaCut1m_njet6to7_btag3p"]
for region in selections:
	# Open the ROOT file
	input_file = ROOT.TFile("/groups/hephy/cms/maryam.shooshtari/www/tttt/plots/analysisPlots/"+args.plot_directory+"/RunII/4t-v12-syst_"+region+".root", "update")
	
	# Loop over all directories in the file
	for key in input_file.GetListOfKeys():
		directory = key.ReadObj()
		print "\n",key.GetName()
		dir_name = key.GetName()
		if key.GetName()=="tttt__ht":
			directory.cd()
			old_data = directory.FindKey("data_obs")
			if old_data: 
				print "Found the old data, going to delete it"
				old_data.Delete()
			else: print "can't find old data"
			plot_name = dir_name.split("__")[1]+"_"+region
			#print plot_name
			graph = getData(args.combine_file,plot_name,"shapes_fit_s") 
			new_data_hist = graph_to_hist(graph)
			#print new_data_hist.IsA().InheritsFrom("TH1")
			#print new_data_hist.GetMaximum()
			directory.cd()
			new_data_hist.Write("data_obs")

	# Close the input file
	input_file.Close()


