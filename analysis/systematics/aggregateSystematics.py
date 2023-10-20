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
scaleWeights = ["DYscaleShapeDown","DYscaleShapeUp","TTscaleShapeDown","TTscaleShapeUp"]#, "ScaleDownNone", "ScaleNoneDown", "ScaleNoneUp", "ScaleUpNone"
PSWeights = ["ISRUp", "ISRDown", "FSRUp", "FSRDown"]

variations +=  scaleWeights + PSWeights + PDFWeights

samples = [ "TTLep_bb", "TTLep_cc", "TTLep_other", "ST_tch", "ST_twch", "TTW", "TTH", "TTZ", "TTTT", "DY", "DiBoson", "data"]


#separate the shape and normalization in scale unc.
for look in ["ScaleDownDown","ScaleUpUp"]:
    print "Currently rescaling "+ look

    # Output files
    if look is "ScaleUpUp": newName = "scaleShapeUp"
    elif look is "ScaleDownDown" : newName = "scaleShapeDown"
    modified_scale_tt = ROOT.TFile(os.path.join(directory, "tttt_TT"+newName+".root"), "RECREATE")
    modified_scale_DY = ROOT.TFile(os.path.join(directory, "tttt_DY"+newName+".root"), "RECREATE")
    ratio = open(os.path.join(directory, "scale_ratios_"+newName+".txt"), "w")

    #input files
    scalefile = ROOT.TFile(os.path.join(directory,"tttt_"+look+".root"), "READ")
    centralfile = ROOT.TFile(os.path.join(directory,"tttt_central.root"), "READ")
    
    #for ttbar
    #rescale the histograms and write to new file
    for hKey in scalefile.GetListOfKeys():
    	SMhKey = centralfile.GetKey(hKey.GetName())
    	h = hKey.ReadObj()
    	SMh = SMhKey.ReadObj()
    	modified_scale_tt.cd() 
    	if not h.Integral()==0:
    	  scale_factor = SMh.Integral()/h.Integral() 
    	  if hKey.GetName().startswith("ht_"):
    	  	ratio.write(h.GetName()+": "+str(scale_factor)+"\n")
	  if "DY" in hKey.GetName():
		h = SMh
	  else:	h.Scale(scale_factor)
    	  h.Write(hKey.GetName())
    print "finished the ttbar file"
    
    #for DY
    #rescale the histograms and write to new file
    for hKey in scalefile.GetListOfKeys():
    	SMhKey = centralfile.GetKey(hKey.GetName())
    	h = hKey.ReadObj()
    	SMh = SMhKey.ReadObj()
    	modified_scale_DY.cd() 
    	if not h.Integral()==0:
    	  scale_factor = SMh.Integral()/h.Integral() 
#    	  if hKey.GetName().startswith("ht_"):
#    	  	ratio.write(h.GetName()+": "+str(scale_factor)+"\n")
	  if "DY" in hKey.GetName():
	  	h.Scale(scale_factor)
	  else : h = SMh
    	  h.Write(hKey.GetName())
    print "finished the DY file"
    
    centralfile.Close()
    scalefile.Close()
    modified_scale_tt.Close()
    modified_scale_DY.Close()
    ratio.close()

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
