from RootTools.core.standard import *
import os
import ROOT
import array

#ROOT.gROOT.LoadMacro("$CMSSW_BASE/src/TMB/Tools/scripts/tdrstyle.C")
#ROOT.setTDRStyle()

dirname = "/groups/hephy/cms/lena.wild/www/tttt/plots/analysisPlots/tttt_small/RunIII/all_log/dilepL-offZ1-njet4p-btag2p-ht500/"
roc = {}


data_root = [
("flat batch=5000", os.path.join(dirname, "lenas_MVA_TTTT_model1.root"),600),
("flat batch=10000", os.path.join(dirname, "lenas_MVA_TTTT_model2.root"),820),
("flat batch=20000", os.path.join(dirname, "lenas_MVA_TTTT_model3.root"),1),
("flat batch=100000", os.path.join(dirname, "lenas_MVA_TTTT_model4.root"),400),
("flat hs1=features*3", os.path.join(dirname, "lenas_MVA_TTTT_model5.root"),840),
("flat hs1=features*4", os.path.join(dirname, "lenas_MVA_TTTT_model6.root"),900),
("flat hs1=features*5", os.path.join(dirname, "lenas_MVA_TTTT_model7.root"),920),
("flat hs1=features+5", os.path.join(dirname, "lenas_MVA_TTTT_model8.root"),616),
("flat hs1=features+10", os.path.join(dirname, "lenas_MVA_TTTT_model9.root"),890),
("flat hs1=features+15", os.path.join(dirname, "lenas_MVA_TTTT_model10.root"),632),
("flat hs1=features+30", os.path.join(dirname, "lenas_MVA_TTTT_model11.root"),432),
#("lstm layers=1", os.path.join(dirname, "lenas_MVA_TTTT_model1_lstm.root"),880),
#("lstm layers=2", os.path.join(dirname, "lenas_MVA_TTTT_model2_lstm.root"),606),
#("lstm layers=3", os.path.join(dirname, "lenas_MVA_TTTT_model3_lstm.root"), 870),
#("lstm layers=4", os.path.join(dirname, "lenas_MVA_TTTT_model4_lstm.root"),882)
]
for name, filename, color in data_root:
    f = ROOT.TFile.Open(filename)
    canvas = f.Get(f.GetListOfKeys().At(0).GetName())
    bkg = canvas.GetListOfPrimitives().At(1)
    sig = canvas.GetListOfPrimitives().At(4)

    print ("sig",sig.GetName())
    print ("bkg",bkg.GetName())

    sig.Scale(1./sig.Integral())
    bkg.Scale(1./bkg.Integral())

    sig_eff = []
    bkg_eff = []
    for i_bin in reversed(range(1,sig.GetNbinsX()+1)):
        sig_eff .append( sig.Integral(i_bin, sig.GetNbinsX()))
        bkg_eff .append( bkg.Integral(i_bin, sig.GetNbinsX()))
        #print i_bin, sig_eff, bkg_eff

    roc[name] = ROOT.TGraph(len(sig_eff), array.array('d',bkg_eff), array.array('d',sig_eff))
    roc[name].SetLineColor(color)
    roc[name].SetLineWidth(2)
    



c1 = ROOT.TCanvas()
i=0
roc["flat batch=20000"].Draw("AL")
for name, filename, color in data_root:
    roc[name].Draw("SAME")
    roc[name].SetTitle("")
    roc[name].GetXaxis().SetTitle("total background efficiency")
    roc[name].GetYaxis().SetTitle("t#bar{t}t#bar{t} signal efficiency")
    d=0.6
    i +=1
    roc[name].GetXaxis().SetRangeUser(0,1-d)
    roc[name].GetYaxis().SetRangeUser(d,1)
    #roc[name].SetMarkerStyle(0)
    #roc[name].SetMarkerColor(int(i))


l = ROOT.TLegend(0.6, 0.5, 0.9, 0.14)
l.SetFillStyle(0)
l.SetShadowColor(0)
l.SetBorderSize(0)

for name, filename, color in data_root:
    l.AddEntry( roc[name], name )
    
 
l.Draw()

ROOT.gStyle.SetOptStat(0)
c1.SetTitle("")
c1.RedrawAxis()
#c1.SetLogy()
#c1.SetLogx()
#c1.SetGridy()
#c1.SetGridx()
c1.Print(os.path.join(dirname, "roc.png"))
c1.Print(os.path.join(dirname, "roc.pdf"))
c1.Print(os.path.join(dirname, "roc.root"))
#Analysis.Tools.syncer.sync()