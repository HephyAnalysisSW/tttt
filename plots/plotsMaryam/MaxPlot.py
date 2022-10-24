import os
import ROOT
from tttt.Tools.cutInterpreter import cutInterpreter


ev = ROOT.TChain("Events")
ev.Add("/scratch-cbe/users/robert.schoefbeck/tttt/nanoTuples/tttt_v1/UL2018/dilep/TTLep_pow_CP5/*.root")


htemp = ROOT.TH1F("bb", "Max bbTaged jet's pt", 100, 0, 1500)
h1 = ROOT.TH1F("h1","Max bbTaged jet's pt",100,0,1500)
htemp2 = ROOT.TH1F("b", "Max bTaged jet's pt", 100, 0, 1500)
h2 = ROOT.TH1F("h2","Max bTaged jet's pt",100,0,1500)


bbTag_disc_pt = "MaxIf$(JetGood_pt, (JetGood_btagDeepFlavbb/(JetGood_btagDeepFlavb+JetGood_btagDeepFlavlepb))/Max$(JetGood_btagDeepFlavbb/(JetGood_btagDeepFlavb+JetGood_btagDeepFlavlepb))==1)"

# ev.Draw("genTtbarId:JetGood_btagDeepFlavB:JetGood_btagDeepFlavb", cutInterpreter.cutString("dilepL-offZ1-njet4p-btag3p-ht500"))
# ev.Draw("genTtbarId:JetGood_btagDeepFlavB:JetGood_btagDeepFlavbb", cutInterpreter.cutString("dilepL-offZ1-njet4p-btag3p-ht500"), "same")

# :JetGood_btagDeepFlavbb:JetGood_btagDeepFlavlepb
c1 = ROOT.TCanvas()
ev.Draw(bbTag_disc_pt+">>bb", "floor((genTtbarId%100)>=52&&(genTtbarId%100)!=53)&&"+cutInterpreter.cutString("dilepL-offZ1-njet4p-btag3p-ht500"))
ev.Draw(bbTag_disc_pt+">>b", "floor((genTtbarId%100)==51||(genTtbarId%100)==53)&&"+cutInterpreter.cutString("dilepL-offZ1-njet4p-btag3p-ht500"))

c2 = ROOT.TCanvas()
c1.SetLogy()
h1 = htemp
h2 = htemp2
h1.SetLineColor(2)
h2.SetLineColor(8)


h1.Draw("hist")
h2.Draw("same")
