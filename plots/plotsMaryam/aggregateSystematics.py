import ROOT,os

import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--plot_directory', action='store', default='4t_syst')
argParser.add_argument('--selection',      action='store', default='trg-dilepL-minDLmass20-offZ1-njet4p-btag3p-ht500')
args = argParser.parse_args()

directory = "/groups/hephy/cms/maryam.shooshtari/www/tttt/plots/analysisPlots/"+args.plot_directory+"/RunII/all/"+args.selection

# Open the output file and create a TDirectoryFile
outFile = ROOT.TFile(os.path.join(directory,"tttt__systematics.root"), "RECREATE")
#nJetGood as a bystander for mva or chosen variable
category = outFile.mkdir("tttt__nJetGood")

# Possible Syst variations
variations = ['LeptonSF', 
              'PU',
              'L1Prefire',
              #'Trigger',
              'BTagSFJes', 
              'BTagSFHf',
              'BTagSFLf',
              'BTagSFHfs1',
              'BTagSFLfs1',
              'BTagSFHfs2',
              'BTagSFLfs2',
              #'BTagSFCfe1',
              #'BTagSFCfe2',
              'jesTotal',
              ]

for variation in variations:
  for upOrDown in ["Up","Down"]:
    inFile = ROOT.TFile(os.path.join(directory,"tttt_"+variation+upOrDown+".root"), "READ")
    for key in inFile.GetListOfKeys():
      if "nJetGood" in key.GetName() and variation not in key.GetName():
        obj = key.ReadObj()
        category.cd()
        clonedHist = obj.Clone()
        histname = clonedHist.GetName()
        if "TTLep_bb" in histname: process = "TTLep_bb"
        elif "TTLep_cc" in histname: process = "TTLep_cc"
        elif "TTLep_other" in histname: process = "TTLep_other"
        elif "ST" in histname: process = "ST"
        elif "TTTT" in histname: process = "TTTT"
        elif "TTW" in histname: process = "TTW"
        elif "TTZ" in histname: process = "TTZ"
        elif "TTH" in histname: process = "TTH"
        
        clonedHist.Write(process+"__"+variation+upOrDown)
    inFile.Close()
outFile.Close()
