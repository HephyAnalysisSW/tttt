import ROOT,os
from tttt.Tools.user    import plot_directory

import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--plot_directory', action='store', default='4t_syst')
argParser.add_argument('--selection',      action='store', default='trg-dilepL-minDLmass20-offZ1-njet4p-btag3p-ht500')
args = argParser.parse_args()

directory = os.path.join(plot_directory, 'analysisPlots', args.plot_directory, 'RunII', "all", args.selection)

# Open the output file and create a TDirectoryFile
outFile = ROOT.TFile(os.path.join(directory,"tttt__systematics.root"), "RECREATE")
#make a list of possible discriminating variables
theYounglings = ["2l_4t","2l_4t_coarse","ht","nJetGood","nBTag"]

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
              'BTagSFCfe1Up',
	      'BTagSFCfe1Down',
              'BTagSFCfe2Up',
	      'BTagSFCfe2Down',
              'jesTotalUp',
	      'jesTotalDown',
	      'noTopPtReweight',
	      'HDampUp',
	      'HDampDown',
	      'central'
              ]
nPDFs = 101
PDFWeights = ["PDF_%s"%i for i in range(1,nPDFs)]
scaleWeights = ["DYscaleShapeDown","DYscaleShapeUp","TTscaleShapeDown","TTscaleShapeUp","DYrenormalizationShapeUp","DYrenormalizationShapeDown", "DYFactorizationShapeUp","DYFactorizationShapeDown","TTrenormalizationShapeUp","TTrenormalizationShapeDown","TTFactorizationShapeUp","TTFactorizationShapeDown"]
PSWeights = ["DYISRUp", "DYISRDown", "DYFSRUp", "DYFSRDown" , "TTISRUp", "TTISRDown", "TTFSRUp", "TTFSRDown" ]

variations +=  scaleWeights + PSWeights + PDFWeights

samples = [ "TTLep_bb", "TTLep_cc", "TTLep_other", "ST_tch", "ST_twch", "TTW", "TTH", "TTZ", "TTTT", "DY", "DiBoson", "data"]


centralfile = ROOT.TFile(os.path.join(directory,"tttt_central.root"), "READ")

#separate the shape and normalization in scale unc.
scales = {"ScaleDownDown" : "scaleShapeDown",
	  "ScaleUpUp" : "scaleShapeUp",
	  "ScaleUpNone" : "renormalizationShapeUp",
	  "ScaleNoneUp" : "FactorizationShapeUp",
	  "ScaleDownNone" : "renormalizationShapeDown",
	  "ScaleNoneDown" : "FactorizationShapeDown"} 
ratio = open(os.path.join(directory, "scale_ratios.txt"), "w")
for look in scales:
    print "Currently rescaling "+ look
    ratio.write("normalization factor for "+scales[look]+":\n")

    # Output files
    modified_scale_tt = ROOT.TFile(os.path.join(directory, "tttt_TT"+scales[look]+".root"), "RECREATE")
    modified_scale_DY = ROOT.TFile(os.path.join(directory, "tttt_DY"+scales[look]+".root"), "RECREATE")

    #input files
    scalefile = ROOT.TFile(os.path.join(directory,"tttt_"+look+".root"), "READ")
    
    #rescale the histograms and write to new file
    for hKey in scalefile.GetListOfKeys():
    	SMhKey = centralfile.GetKey(hKey.GetName())
    	h = hKey.ReadObj()
    	SMh = SMhKey.ReadObj()
    	if not h.Integral()==0:
    	  scale_factor = SMh.Integral()/h.Integral() 
    	  if hKey.GetName().startswith("ht_"):
    	  	ratio.write("\t"+h.GetName()+": "+str(scale_factor)+"\n")
    	  #ttbar
	  modified_scale_tt.cd() 
	  if "DY" in hKey.GetName(): h = SMh
	  else:	h.Scale(scale_factor)
    	  h.Write(hKey.GetName())
	  #DY
	  modified_scale_DY.cd()
	  h = hKey.ReadObj()
    	  if not "DY" in hKey.GetName(): h = SMh
	  else: h.Scale(scale_factor)
	  h.Write(hKey.GetName())
 
    scalefile.Close()
    modified_scale_tt.Close()
    modified_scale_DY.Close()
ratio.close()


#separate PS weights in ttbar and DY
for PS in ["ISRUp", "ISRDown", "FSRUp", "FSRDown"]:
    jointPS = ROOT.TFile(os.path.join(directory,"tttt_"+PS+".root"), "READ")
    TT_PS = ROOT.TFile(os.path.join(directory, "tttt_TT"+PS+".root"), "RECREATE") 
    DY_PS = ROOT.TFile(os.path.join(directory, "tttt_DY"+PS+".root"), "RECREATE") 
    for hKey in jointPS.GetListOfKeys():
    	SMhKey = centralfile.GetKey(hKey.GetName())
    	SMh = SMhKey.ReadObj()
    	h = hKey.ReadObj()
    	TT_PS.cd() 
	if "DY" in hKey.GetName(): h = SMh
    	h.Write(hKey.GetName())
    	h = hKey.ReadObj()
	DY_PS.cd()
	if not "DY" in hKey.GetName(): h = SMh
	h.Write(hKey.GetName())
    print "finished the {} decorellation".format(PS)
    jointPS.Close()
    TT_PS.Close()
    DY_PS.Close()
		
centralfile.Close()


#Create the root file combine desires
for theChosenOne in theYounglings :
    category = outFile.mkdir("tttt__"+theChosenOne)
    for sample in samples :
	objName = theChosenOne+"__"+sample
	for variation in variations:
	    inFile = ROOT.TFile(os.path.join(directory,"tttt_"+variation+".root"), "READ")
	    for key in inFile.GetListOfKeys():
	      #if key.GetName()=="ht__data": print "found",key.GetName()
	      if objName == key.GetName():
		obj = key.ReadObj()
	        category.cd()
	        clonedHist = obj.Clone()
	        histname = clonedHist.GetName()
		if "data" in histname: 
			clonedHist.Write("data_obs")
			print "found data", theChosenOne,clonedHist.GetTitle()
		else:
			if variation == "central":
				clonedHist.Write(sample)
				clonedHist.Write(sample+"__noTopPtReweightDown")
				for i in range(1,nPDFs):
					clonedHist.Write(sample+"__PDF_%sDown"%i)
			elif variation == "noTopPtReweight" :
				clonedHist.Write(sample+"__noTopPtReweightUp")
			elif "PDF" in variation :
				clonedHist.Write(sample+"__"+variation+"Up")
			else:
	        		clonedHist.Write(sample+"__"+variation)
		
	    inFile.Close()
	
outFile.Close()
