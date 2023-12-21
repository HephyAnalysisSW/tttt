import ROOT,os
from tttt.Tools.user    import plot_directory
import RootTools.plot.helpers as plot_helpers
from shutil import copyfile

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

# cristina.giordano/www/tttt/plots/analysisPlots/
directory = os.path.join(plot_directory, 'analysisPlots', args.plot_directory, args.era, "all", args.selection)
out_directory = args.plot_directory if args.out_directory is None else args.out_directory
outFile_dir = os.path.join(plot_directory, 'analysisPlots', out_directory, args.era)
if not os.path.exists(os.path.join(outFile_dir, "all", args.selection)):
    try:
        os.makedirs(os.path.join(outFile_dir, "all", args.selection))
        print "making a new directory"
    except:
        # different jobs may start at the same time creating race conditions.
        pass 
#plot_helpers.copyIndexPHP(out_Filedir)

# Open the output file and create a TDirectoryFile
jetSelection = args.selection.split("-")[6]+"_"+args.selection.split("-")[7]
outFile = ROOT.TFile(os.path.join(outFile_dir, args.plot_directory+"_"+jetSelection+".root"), "RECREATE")
#make a list of possible discriminating variables
theYounglings = ["2l_4t","ht","nJetGood","nBTag"]
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
scaleWeights = ["DYscaleShapeDown","DYscaleShapeUp",
                "TTscaleShapeDown","TTscaleShapeUp",
                "DYrenormalizationShapeUp","DYrenormalizationShapeDown", "DYFactorizationShapeUp","DYFactorizationShapeDown",
                #"TTrenormalizationShapeUp","TTrenormalizationShapeDown","TTFactorizationShapeUp","TTFactorizationShapeDown", 
                "TTbbrenormalizationShapeUp","TTbbrenormalizationShapeDown","TTbbFactorizationShapeUp","TTbbFactorizationShapeDown",
                "TTccrenormalizationShapeUp","TTccrenormalizationShapeDown","TTccFactorizationShapeUp","TTccFactorizationShapeDown",
                "TTlightrenormalizationShapeUp","TTlightrenormalizationShapeDown","TTlightFactorizationShapeUp","TTlightFactorizationShapeDown",
                "TTTTrenormalizationShapeUp","TTTTrenormalizationShapeDown","TTTTFactorizationShapeUp","TTTTFactorizationShapeDown",
                ]
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
    print "\n Currently rescaling "+ look
    ratio.write("normalization factor for "+scales[look]+":\n")

    # Output files
    modified_scale_tt = ROOT.TFile(os.path.join(directory, "tttt_TT"+scales[look]+".root"), "RECREATE")
    modified_scale_ttbb = ROOT.TFile(os.path.join(directory, "tttt_TTbb"+scales[look]+".root"), "RECREATE")
    modified_scale_ttcc = ROOT.TFile(os.path.join(directory, "tttt_TTcc"+scales[look]+".root"), "RECREATE")
    modified_scale_ttother = ROOT.TFile(os.path.join(directory, "tttt_TTlight"+scales[look]+".root"), "RECREATE")
    modified_scale_tttt = ROOT.TFile(os.path.join(directory, "tttt_TTTT"+scales[look]+".root"), "RECREATE")
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
            #tt
            modified_scale_tt.cd()
            h = hKey.ReadObj()
            #if "DY" in hKey.GetName(): h = SMh
            if not (("TTLep_bb" in hKey.GetName()) or ("TTLep_cc" in hKey.GetName()) or ("TTLep_other" in hKey.GetName())): h = SMh
            else: 
                h.Scale(scale_factor)
                #print "\n in ttbar: ", hKey.GetName(), "8th bin: ", h.GetBinContent(8), "SM value: ", SMh.GetBinContent(8)
            h.Write(hKey.GetName())
            
            #ttbb
            modified_scale_ttbb.cd()
            h = hKey.ReadObj()
            if not "TTLep_bb" in hKey.GetName(): h = SMh
            else:	
                h.Scale(scale_factor)
                #print "found ttbb scale",hKey.GetName(), "8th bin: ", h.GetBinContent(8)
            h.Write(hKey.GetName())
            
            #ttother
            modified_scale_ttcc.cd()
            h = hKey.ReadObj()
            if not "TTLep_cc" in hKey.GetName(): h = SMh
            else:	
                h.Scale(scale_factor)
                #print "found ttcc scale",hKey.GetName(), "8th bin: ", h.GetBinContent(8)
            h.Write(hKey.GetName())
            
            # ttother
            modified_scale_ttother.cd()
            h = hKey.ReadObj()
            if not "TTLep_other" in hKey.GetName(): h = SMh
            else:	
                h.Scale(scale_factor)
                #print "found ttlight scale", hKey.GetName(), "8th bin: ", h.GetBinContent(8)
            h.Write(hKey.GetName())
            
            # tttt
            modified_scale_tttt.cd()
            h = hKey.ReadObj()
            if not "TTTT" in hKey.GetName(): h = SMh
            else:	
                h.Scale(scale_factor)
                #print "found tttt scale", hKey.GetName(), "8th bin: ", h.GetBinContent(8)
            h.Write(hKey.GetName())
            # DY
            modified_scale_DY.cd()
            h = hKey.ReadObj()
            if not "DY" in hKey.GetName(): h = SMh
            else: 
                h.Scale(scale_factor)
                #print "found DY scale", hKey.GetName(), "8th bin: ", h.GetBinContent(8)
            h.Write(hKey.GetName())

    scalefile.Close()
    modified_scale_tt.Close()
    modified_scale_ttbb.Close()
    modified_scale_ttcc.Close()
    modified_scale_ttother.Close()
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
        for variation in variations:
            inFile = ROOT.TFile(os.path.join(directory,"tttt_"+variation+".root"), "READ")
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
						    # if not args.era == "RunII": sample = sample +"_"+args.era
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

            if not args.noEFT and sample== "TTLep_bb":
                eftFile = ROOT.TFile(os.path.join(directory,"tttt_EFTs.root"), "READ")
                #print "found eft file"
                histos = {}
                for wc in wcList:
                    #Get the histos in the form combine wants
                    SMhistName = theChosenOne+"__TTbb_EFT_central"
                    plushistName = theChosenOne+"__TTbb_EFT_"+wc+"_+1.000"
                    minushistName = theChosenOne+"__TTbb_EFT_"+wc+"_-1.000"
                    for key in eftFile.GetListOfKeys():
                        obj = key.ReadObj()
                        clonedHist = obj.Clone()
                        if key.GetName() == SMhistName:
                            histos["SM"] = clonedHist
                            #print "found the sm hist"
                        elif key.GetName() == plushistName :
                            histos["plus"] = clonedHist
                            #print "found the plus hist"
                        elif key.GetName() == minushistName : histos["minus"] = clonedHist
                    histos["quad"] = getQuadratic(histos["SM"], histos["plus"], histos["minus"])

                    #scale the histos to Pow/MG
                    for key in inFile.GetListOfKeys():
                        if key.GetName().startswith(objName):
                            obj = key.ReadObj()
                            clonedHist = obj.Clone()
                            histos["ratio"] = clonedHist.Clone()
                            histos["ratio"].Divide(histos["SM"])
                            #print objName, sample, variation
                            #check for zeros
                            for bin in range(1, histos["SM"].GetNbinsX() + 1):
                                if histos["SM"].GetBinContent(bin) == 0:
                                    histos["ratio"].SetBinContent(bin, 0)
                                #print "TTLep_bb bin:",clonedHist.GetBinContent(bin),"EFT at sm bin:",histos["SM"].GetBinContent(bin),"EFT lin bin:",histos["plus"].GetBinContent(bin), "EFT quad bin:",histos["quad"].GetBinContent(bin)
                            histos["SM"].Multiply(histos["ratio"])
                            histos["plus"].Multiply(histos["ratio"])
                            histos["quad"].Multiply(histos["ratio"])
                            # for bin in range(1, histos["SM"].GetNbinsX() + 1):


                    category.cd()
                    if variation == "central":
                        histos["SM"].Write("sm")
                        histos["plus"].Write("sm_lin_quad_"+wc)
                        histos["quad"].Write("quad_"+wc)
                        histos["SM"].Write("sm__noTopPtReweightDown")
                        histos["plus"].Write("sm_lin_quad_"+wc+"__noTopPtReweightDown")
                        histos["quad"].Write("quad_"+wc+"__noTopPtReweightDown")
                        for i in range(1,nPDFs):
                            histos["SM"].Write("sm__PDF_%sDown"%i)
                            histos["plus"].Write("sm_lin_quad_"+wc+"__PDF_%sDown"%i)
                            histos["quad"].Write("quad_"+wc+"__PDF_%sDown"%i)
                    elif variation == "noTopPtReweight" :
                        histos["SM"].Write("sm__noTopPtReweightUp")
                        histos["plus"].Write("sm_lin_quad_"+wc+"__noTopPtReweightUp")
                        histos["quad"].Write("quad_"+wc+"__noTopPtReweightUp")
                    elif "PDF" in variation :
                        histos["SM"].Write("sm__"+variation+"Up")
                        histos["plus"].Write("sm_lin_quad_"+wc+"__"+variation+"Up")
                        histos["quad"].Write("quad_"+wc+"__"+variation+"Up")
                    else:
                        histos["SM"].Write("sm__"+variation)
                        histos["plus"].Write("sm_lin_quad_"+wc+"__"+variation)
                        histos["quad"].Write("quad_"+wc+"__"+variation)



                    #TBC
                    if len(wcList)>=2 :
                        for wc2 in wcList:
                            mixedName = theChosenOne+"__TTbb_EFT_"+wc+"_+1.000_"+wc2+"_+1.000_"
                            for key in eftFile.GetListOfKeys():
                                if key.GetName() == mixedName:
                                    obj = key.ReadObj()
                                    clonedHist = obj.Clone()
                                    category.cd()
                                    clonedHist.Write("sm_lin_quad_mixed_"+wc+"_"+wc2)
                    eftFile.Close()
                    #print "done creating EFT histos"
            inFile.Close()
#            copyfile(os.path.join(directory,"tttt_"+variation+".root"),os.path.join(outFile_dir, "all", args.selection,"tttt_"+variation+".root"))


print("Written to output file: %s"%outFile)
outFile.Close()
