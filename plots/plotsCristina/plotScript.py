#Import modules
import ROOT
from array import array
from tttt.Tools.cutInterpreter import cutInterpreter
from RootTools.core.standard import *
print("Imports Ok")

#File and specifics
filedir = "/scratch-cbe/users/robert.schoefbeck/tttt/nanoTuples/tttt_v1/UL2018/dilep/TTLep_pow_CP5/*.root"
selection = "MaxIf$(JetGood_pt,(JetGood_btagDeepFlavbb/(JetGood_btagDeepFlavb+JetGood_btagDeepFlavlepb))/Max$(JetGood_btagDeepFlavbb/(JetGood_btagDeepFlavb+JetGood_btagDeepFlavlepb))==1)"
cut = "floor((genTtbarId%100)/10)==5&&(genTtbarId%2==1)&&"+cutInterpreter.cutString("dilepL-offZ1-njet4p-btag3p-ht500")


c = ROOT.TChain("Events")
c.Add(filedir)
print("Chain created")

ht1 = ROOT.TH1F("ht1", "ht1", 100, 0,500)
h1 = ROOT.TH1F("h1", "h1", 100, 0,500)
c1 = ROOT.TCanvas("c1", "pt")

c.Draw(selection+">>ht1", cut)
c1.SetLogy()
h1 = ht1
h1.Draw()
h1.SaveAs("attempt.png")
print("Close")
