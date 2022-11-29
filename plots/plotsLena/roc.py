from RootTools.core.standard import *
import os
import ROOT
import array
import config_roc as config
import Analysis.Tools.syncer

import os, shutil
def copyIndexPHP( results_dir ):
    index_php = os.path.join( results_dir, 'index.php' )
    shutil.copyfile( os.path.expandvars( '$CMSSW_BASE/src/RootTools/plot/php/index.php' ), index_php )


dirname = config.dirname
results_dir = "/groups/hephy/cms/lena.wild/www/tttt/plots/analysisPlots/TMB_4t_p3/RunII/roc/"+config.njetsel[0]
if not os.path.exists( results_dir ): 
    os.makedirs( results_dir )
data_root = config.data_root
roc = {}
for selection, Title, Name in data_root:
    for name, filename, color in selection:
        print(name)
        f = ROOT.TFile.Open(filename)
        canvas = f.Get(f.GetListOfKeys().At(0).GetName())
        bkg1 = canvas.GetListOfPrimitives().At(0).GetListOfPrimitives().At(1)
        bkg2 = canvas.GetListOfPrimitives().At(0).GetListOfPrimitives().At(2)
        bkg3 = canvas.GetListOfPrimitives().At(0).GetListOfPrimitives().At(3)
        sig = canvas.GetListOfPrimitives().At(0).GetListOfPrimitives().At(4)
        a=bkg1.Integral()
        b=bkg2.Integral()
        c=bkg3.Integral()
        print ("sig",sig.GetName())
        print ("bkg1",bkg1.GetName())
        print ("bkg2",bkg2.GetName())
        print ("bkg3",bkg3.GetName())
        sig.Scale(1./sig.Integral())
        bkg1.Scale(1./(a+b+c))
        bkg2.Scale(1./(a+b+c))
        bkg3.Scale(1./(a+b+c))
        sig_eff = []
        bkg_eff = []
        for i_bin in reversed(range(1,sig.GetNbinsX()+1)):
            sig_eff .append( sig.Integral(i_bin, sig.GetNbinsX()))
            bkg_eff .append( bkg1.Integral(i_bin, sig.GetNbinsX())+bkg2.Integral(i_bin, sig.GetNbinsX())+bkg3.Integral(i_bin, sig.GetNbinsX()))
            #print (sig_eff[-1],bkg_eff[-1])
        roc[name] = ROOT.TGraph(len(sig_eff), array.array('d',bkg_eff), array.array('d',sig_eff))
        roc[name].SetLineColor(color)
        roc[name].SetLineWidth(2)
        



    c1 = ROOT.TCanvas()
    roc[selection[0][0]].Draw("AL")
    for name, filename, color in selection:
        roc[name].Draw("SAME")
        roc[name].SetTitle(Title)
        roc[name].GetXaxis().SetTitle("total background efficiency")
        roc[name].GetYaxis().SetTitle("t#bar{t}t#bar{t} signal efficiency")
        d=0.4
        roc[name].GetXaxis().SetRangeUser(0,1-d)
        roc[name].GetYaxis().SetRangeUser(d,1)


    l = ROOT.TLegend(0.5, 0.3, 0.9, 0.14)
    l.SetFillStyle(0)
    l.SetShadowColor(0)
    l.SetBorderSize(0)
    for name, filename, color in selection:
        l.AddEntry( roc[name], name )
    l.Draw()

    ROOT.gStyle.SetOptStat(0)
    c1.SetTitle("")
    c1.RedrawAxis()
    copyIndexPHP( results_dir )
    c1.Print(os.path.join(results_dir,Name+".png"))
    #c1.Print(os.path.join(results_dir,Name+".pdf"))
    #c1.Print(os.path.join(results_dir,Name+".root"))
Analysis.Tools.syncer.sync()