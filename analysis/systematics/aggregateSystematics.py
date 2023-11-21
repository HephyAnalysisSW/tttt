import ROOT,os
from tttt.Tools.user    import plot_directory

import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--plot_directory', action='store', default='4t_syst')
argParser.add_argument('--out_directory', action='store', default=None)
argParser.add_argument('--user_directory', action = 'store', default = None)
argParser.add_argument('--selection',      action='store', default='trg-dilep-OS-minDLmass20-offZ1-lepVeto2-njet6to7-btag3p-ht500')
argParser.add_argument('--noEFT',	   action='store_true', default=False)
argParser.add_argument('--era',		   action='store', default='RunII', choices=['RunII','2018','2017','2016','2016_preVFP'])
args = argParser.parse_args()

if args.user_directory is not None: plot_directory = os.path.join('/groups/hephy/cms',args.user_directory,'www/tttt/plots')
directory = os.path.join(plot_directory, 'analysisPlots', args.plot_directory, args.era, "all", args.selection)
out_directory = args.plot_directory if args.out_directory is None else args.out_directory

# Open the output file and create a TDirectoryFile
jetSelection = args.selection.split("-")[6]+"_"+args.selection.split("-")[7]
outFile = ROOT.TFile(os.path.join(plot_directory, 'analysisPlots', out_directory, args.era, args.plot_directory+"_"+jetSelection+".root"), "RECREATE")
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
    print(modified_scale_tt)
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
print(ratio)


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
        print "finished the {} decorrellation".format(PS)
        jointPS.Close()
        TT_PS.Close()
        DY_PS.Close()

centralfile.Close()

isEFT = True
wcList = ["cQQ1"]
def getQuadratic(hist_sm, hist_plus, hist_minus):
#create quad term for EFT
# Since the quadratic term does not change sign, we can get it from the
# histograms where c = +1, c = 0, and c = -1
# (1) c = +1 is SM + LIN + QUAD
# (2) c = -1 is SM - LIN + QUAD
# (3) c =  0 is SM
# Thus, we can get the quad from
# (1)+(2) = SM + SM + QUAD + QUAD | -2*(3)
# (1)+(2)-(3) = QUAD + QUAD       | /2
# 0.5*[(1)+(2)-(3)] = QUAD
   hist_quad = hist_plus.Clone(hist_plus.GetName()+"_quad")
   hist_quad.Add(hist_minus)
   hist_quad.Add(hist_sm, -2)
   hist_quad.Scale(0.5)
   return hist_quad



#Create the root file combine desires
for theChosenOne in theYounglings :
    category = outFile.mkdir("tttt__"+theChosenOne)
    for sample in samples :
        objName = theChosenOne+"__"+sample
        # print(objName)
    	for variation in variations:
    	    inFile = ROOT.TFile(os.path.join(directory,"tttt_"+variation+".root"), "READ")
            # print "found syst file in dir %s" %os.path.join(directory, "tttt_"+variation+".root")
            for key in inFile.GetListOfKeys():
                if key.GetName().startswith(objName):
                    obj = key.ReadObj()
                    category.cd()
                    clonedHist = obj.Clone()
                    histname = clonedHist.GetName()
                    if "data" in histname:
                        clonedHist.Write("data_obs")
                        print "found data", theChosenOne,clonedHist.GetTitle()
                    else:
                        # if not args.era == "RunII":
                        #     sample = sample +"_"+args.era
                        if not args.era == "RunII": sample = sample +"_"+args.era
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
                            # if sample != "ST_tch" and variation == "TTFactorizationShapeUp":
                            #     print(sample+"__"+variation)
                            # elif sample == "ST_tch" and variation == "TTFactorizationShapeUp":
                            #     print "OILLOC"
                            # if variation == "TTFactorizationShapeUp" and sample == "ST_tch":
                                # print "OTA (Oh tappost?)"

            inFile.Close()
        if not args.noEFT:
            eftFile = ROOT.TFile(os.path.join(directory,"tttt_EFTs.root"), "READ")
            # print "found eft file in dir %s" %os.path.join(directory, "tttt_EFTs.root")
            histos = {}
            for wc in wcList:
                SMhistName = theChosenOne+"__TTbb_EFT_2018_central"
                plushistName = theChosenOne+"__TTbb_EFT_2018_"+wc+"_+1.000"
                minushistName = theChosenOne+"__TTbb_EFT_2018_"+wc+"_-1.000"
                for key in eftFile.GetListOfKeys():
                    obj = key.ReadObj()
                    # print(obj)
                    clonedHist = obj.Clone()
                    if key.GetName() == SMhistName:
                        histos["SM"] = clonedHist
                        # print "found the sm hist"
                    elif key.GetName() == plushistName :
                        histos["plus"] = clonedHist
                        # print "found the plus hist"
                    elif key.GetName() == minushistName :
                        histos["minus"] = clonedHist
                        # print "found the minus hist"
                # insert here the new histograms
                quadHist = getQuadratic(histos["SM"], histos["plus"], histos["minus"])
                category.cd()
                histos["SM"].Write("sm")
                histos["plus"].Write("sm_lin_quad_"+wc)
                quadHist.Write("quad_"+wc)
                quad_direct_hist = quadHist.Clone()
                # print(quadHist)
                # sm_hist, sm_lin_quad_hist, quad_hist = None, None, None
                # multipliedhistos = {}
                for variation in variations:
                    # Open the file for the current variation
                    inFile = ROOT.TFile(os.path.join(directory, "tttt_" + variation + ".root"), "READ")
                    objName = theChosenOne+"__"+sample
                    # Loop over keys in inFile
                    if sample == "TTLep_bb":
                        for key in inFile.GetListOfKeys():
                            # print("KEYS", key)
                            if key.GetName().startswith(objName):
                                obj = key.ReadObj()
                                clonedHist = obj.Clone()
                                category.cd()
                                for hist_type, hist in histos.items():
                                    multipliedHist = hist.Clone()
                                    if hist_type == "SM":
                                        multipliedHist.Multiply(clonedHist)
                                        # multipliedHist.Write("sm_"+variation)
                                        if variation == "central":
                                            multipliedHist.Write("sm__noTopPtReweightDown")
                                            for i in range(1,nPDFs):
                                                clonedHist.Write("sm__PDF_%sDown"%i)
                                        elif variation == "noTopPtReweight" :
                                            clonedHist.Write("sm__noTopPtReweightUp")
                                        elif "PDF" in variation :
                                            clonedHist.Write("sm__"+variation+"Up")
                                        else:
                                            clonedHist.Write("sm__"+variation)
                                    elif hist_type == "plus":
                                        multipliedHist.Multiply(clonedHist)
                                        if variation == "central":
                                            multipliedHist.Write("sm_lin_quad_"+wc+"__noTopPtReweightDown")
                                            for i in range(1,nPDFs):
                                                multipliedHist.Write("sm_lin_quad_"+wc+"__PDF_%sDown"%i)
                                        elif variation == "noTopPtReweight" :
                                            multipliedHist.Write("sm_lin_quad_"+wc+"__noTopPtReweightUp")
                                        elif "PDF" in variation :
                                            multipliedHist.Write("sm_lin_quad_"+wc+"__"+variation+"Up")
                                        else:
                                            multipliedHist.Write("sm_lin_quad_"+wc+"__"+variation)
                                        # multipliedHist.Write("sm_lin_quad_"+wc+"_"+variation)

                                quad_direct_hist.Multiply(clonedHist)
                                if variation == "central":
                                    quad_direct_hist.Write("quad_"+wc+"__noTopPtReweightDown")
                                    for i in range(1,nPDFs):
                                        quad_direct_hist.Write("quad_"+wc+"__PDF_%sDown"%i)
                                elif variation == "noTopPtReweight" :
                                    quad_direct_hist.Write("quad_"+wc+"__noTopPtReweightUp")
                                elif "PDF" in variation :
                                    quad_direct_hist.Write("quad_"+wc+"__"+variation+"Up")
                                else:
                                    quad_direct_hist.Write("quad_"+wc+"__"+variation)
                                # quad_direct_hist.Write("quad_"+wc+"_"+variation)

                if len(wcList)>=2 :
                    for wc2 in wcList:
                        mixedName = theChosenOne+"__TTbb_EFT_2018_"+wc+"_+1.000_"+wc2+"_+1.000_"
                        for key in eftFile.GetListOfKeys():
                            if key.GetName() == mixedName:
                                obj = key.ReadObj()
                                clonedHist = obj.Clone()
                                category.cd()
                                clonedHist.Write("sm_lin_quad_mixed_"+wc+"_"+wc2)

print("Written output file: %s"%outFile)
outFile.Close()
