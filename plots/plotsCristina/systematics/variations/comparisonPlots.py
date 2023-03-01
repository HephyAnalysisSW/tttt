import ROOT, os, copy, os
from tttt.Tools.user import variations_directory

nom = variations_directory+"/JetGood_pt_nom.root"
var1 = variations_directory+"/JetGood_pt_jerUp.root"
var2 = variations_directory+"/JetGood_pt_jerDown.root"

c1 = ROOT.TCanvas("c1")
c1.Draw()
c1.cd()


hnom = ROOT.TH1F()
h1=ROOT.TH1F()
h2=ROOT.TH1F()

fnom = ROOT.TFile.Open(nom, "READ")
f1   = ROOT.TFile.Open(var1, "READ")
f2   = ROOT.TFile.Open(var2, "READ")

# nom     = fnom.Get('nom')
# var1    = f1.Get('var1')
# var2    = f2.Get('var2')

hnom=fnom.Get('nom')
h1=f1.Get('jerUp')
h2=f2.Get('jerDown')

#print(h2)

hnom.SetLineColor(ROOT.kBlack)
h1.SetLineColor(ROOT.kRed)
h2.SetLineColor(ROOT.kGreen+2)

maxdiffrel=0.2
for b in range(1,hnom.GetNbinsX()+1):
    hnom.SetBinError(b,0.001*hnom.GetBinContent(b))
    diffrelbin=0
    if(hnom.GetBinContent(b)!=0):
        diffrelbin=max(abs(1-h1.GetBinContent(b)/hnom.GetBinContent(b)),abs(1-h2.GetBinContent(b)/hnom.GetBinContent(b) ) )
    maxdiffrel=max(diffrelbin,maxdiffrel)

hnom.Integral()
c1.SetLogy()
#hnom.SetNameTitle('nom',"JetGood_pt")
hnom.Draw("histo")

for b in range(1,h1.GetNbinsX()+1):
    h1.SetBinError(b,0)
    h2.SetBinError(b,0)

r1 = ROOT.TRatioPlot(h1,hnom,"divsym")
r2 = ROOT.TRatioPlot(h2,hnom,"divsym")

r2.Draw()
g2 = r2.GetLowerRefGraph().Clone("g2")
print(g2.GetN(), h1.GetNbinsX(),hnom.GetNbinsX(),h2.GetNbinsX())

r1.Draw()
print("maxdiffrel is ",maxdiffrel)
r1.GetLowerRefGraph().SetMarkerColorAlpha(ROOT.kRed,0.9)
r1.GetLowerRefGraph().SetLineColorAlpha(ROOT.kRed,0.9)
r1.GetLowerRefGraph().GetYaxis().SetRangeUser(1-maxdiffrel*1.3,1+maxdiffrel*1.3)

u=r1.GetUpperPad()
u.SetLogy()
d=r1.GetLowerPad()

u.cd()
h2.Draw("samehisto")
h1.Draw("samehisto")
h1.SetTitle("JetGood_pt")
d.cd()
g2.SetMarkerStyle(0)
g2.SetMarkerColorAlpha(ROOT.kGreen+2,0.9)
g2.SetLineColorAlpha(ROOT.kGreen+2,0.90)
g2.Draw("P")

c1.Print("nom_vs_syst.pdf")
