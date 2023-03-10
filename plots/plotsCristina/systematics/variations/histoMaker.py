# General imports
import os, sys
import ROOT
from array import array

# tttt imports
from tttt.Tools.cutInterpreter import cutInterpreter
from tttt.Tools.user import variations_directory



scenarios = ["nom", "jerUp", "jerDown"]



def histoMaker(scenario):
    inFileName ="/scratch-cbe/users/cristina.giordano/tttt/nanoTuples/tttt_v5/UL2016/dilep_small/TTLep_pow_CP5/TTLep_pow_CP5_0.root"
    inFile = ROOT.TFile.Open(inFileName, "READ")
    tree = inFile.Get("Events")
    #print(tree)
    pt = array('f', [0.])

    #for i, scen in enumerate(scenarios):

    out_dir = os.path.join(variations_directory)#, options.samples)

    if not os.path.exists(out_dir):
        try:
            os.makedirs(out_dir)
        except:
            print 'Could not create', out_dir
    print(type(out_dir))
    print(type(scenario))
    outFileName = out_dir+"/JetGood_pt_"+str(scenario)+".root"

    outFile = ROOT.TFile.Open(outFileName, "RECREATE")
    tree.SetBranchAddress("JetGood_pt_"+scenario, pt)

    htemp = ROOT.TH1F(scenario, "JetGood_pt_"+scenario, 4, 0, 400)

    for i in range(0, tree.GetEntries()):
        tree.GetEntry(i)
        htemp.Fill(pt[0])

    h = htemp

    outFile.Write()


for s in scenarios:
    histoMaker(s)





#
#
# #scenario = ['jerUp']
#
# variables = ["pt/F"]
#
# input_dir = postprocessing_output_directory
#
# inFileName = "/scratch-cbe/users/cristina.giordano/tttt/nanoTuples/tttt_v5/UL2016/dilep_small/TTLep_pow_CP5/TTLep_pow_CP5_0.root"
# inFile = ROOT.TFile.Open(inFileName, "READ")
# tree = inFile.Get("Events")
#
# pt = array('f', [0.])
#
# output_dir = "./histograms"
#
# jesUncertainties = [
#     "Total",
#     # "AbsoluteMPFBias",
#     # "AbsoluteScale",
#     # "AbsoluteStat",
#     # "RelativeBal",
#     # "RelativeFSR",
#     # "RelativeJEREC1",
#     # "RelativeJEREC2",
#     # "RelativeJERHF",
#     # "RelativePtBB",
#     # "RelativePtEC1",
#     # "RelativePtEC2",
#     # "RelativePtHF",
#     # "RelativeStatEC",
#     # "RelativeStatFSR",
#     # "RelativeStatHF",
#     # "PileUpDataMC",
#     # "PileUpPtBB",
#     # "PileUpPtEC1",
#     # "PileUpPtEC2",
#     # "PileUpPtHF",
#     # "PileUpPtRef",
#     # "FlavorQCD",
#     # "Fragmentation",
#     # "SinglePionECAL",
#     # "SinglePionHCAL",
#     # "TimePtEta",
# ]
# #
# # jesVariations= ["pt_jes%s%s"%(var, upOrDown) for var in jesUncertainties for upOrDown in ["Up","Down"]]
# #
# # for var in jesVariations:
# #     out_dir = "."
# #     outFileName = out_dir+"/Jet_"+var+".root"
# #     outFile = ROOT.TFile.Open(outFileName, "RECREATE")
# #     tree.SetBranchAddress("Jet_"+var, pt)
# #
# #     htemp = ROOT.TH1F(var, "Jet_"+var, 4, 0, 400)
# #
# #     for i in range(0, tree.GetEntries()):
# #         tree.GetEntry(i)
# #         htemp.Fill(pt[0])
# #
# # h = htemp
# #
# # outFile.Write()
#
# out_dir = "."
# outFileNamept = out_dir+"/Jet_pt.root"
# outFilept = ROOT.TFile.Open(outFileNamept, "RECREATE")
# tree.SetBranchAddress("Jet_pt", pt)
#
# htemp = ROOT.TH1F(pt, "Jet_pt", 4, 0, 400)
#
# for i in range(0, tree.GetEntries()):
#     tree.GetEntry(i)
#     htemp.Fill(pt[0])
# #
# h = htemp
# #
# outFile.Write()


# if not os.path.exists(out_dir):
#     try:
#         os.makedirs(out_dir)
#     except:
#         print 'Could not create', out_dir

# def histoMaker(scenario):
#
#     inFileName ="/scratch-cbe/users/cristina.giordano/tttt/nanoTuples/tttt_v5/UL2016/dilep_small/TTLep_pow_CP5/TTLep_pow_CP5_0.root"
#     inFile = ROOT.TFile.Open(inFileName, "READ")
#     tree = inFile.Get("Events")
#     #print(tree)
#     pt = array('f', [0.])
#
#     #for i, scen in enumerate(scenarios):
#
#     out_dir = os.path.join(variations_directory, options.processingEra, options.era, options.skim)#, options.samples)
#
#
#
#     if not os.path.exists(out_dir):
#         try:
#             os.makedirs(out_dir)
#         except:
#             print 'Could not create', out_dir
#     print(type(out_dir))
#     print(type(scenario))
#     outFileName = out_dir+"/JetGood_pt_"+str(scenario)+".root"
#     logger.info( "Saving in %s", outFileName )
#
#     outFile = ROOT.TFile.Open(outFileName, "RECREATE")
#     tree.SetBranchAddress("JetGood_pt_jes"+scenario, pt)
#
#     htemp = ROOT.TH1F(scenario, "JetGood_pt_"+scenario, 4, 0, 400)
#
#     for i in range(0, tree.GetEntries()):
#         tree.GetEntry(i)
#         htemp.Fill(pt[0])
#
#     h = htemp
#
#     outFile.Write()
#
#
# for s in scenarios:
#     histoMaker(s)
