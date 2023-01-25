"""
Plotting class including systematics
"""

import os
import ROOT
from math                                import sqrt

from tttt.Tools.user                     import plot_directory
import RootTools.plot.helpers as plot_helpers


class Plotter:

    def __init__(self, name = None):

        self.name = name
        self.plot_dir = plot_directory
        self.legend = ROOT.TLegend(0.18,0.88-0.03*10,0.9,0.88)
        self.xTitle = "something"
        self.yTitle = "Number of Events"
        self.ratioTitle = "Data/MC"
        self.ratio = None
        self.stack = None
        self.binning = None
        self.yMax = 0
        self.yMin = 0.9
        self.yFactor = 1.7
        self.samples = []
        self.systDeltas = []
        self.systNames = []
        self.data = {}
        self.totalHist = ROOT.TH1F()
        self.totalError = ROOT.TGraphAsymmErrors()
        self.stack = ROOT.THStack()
        self.padSize = {"yWidth" : 500 , "xWidth": 500}

        self.log = False
        self.ratio = False
        self.noData = True
        self.noSyst = True

#---Public funtions ------------------------------------------------------------

    #Add a new sample
    #+ Creat a list of all histograms
    def addSample(self, sampleName, hist, sampleText):

        sample = {}
        sample["name"] = sampleName
        sample["hist"] = hist
        sample["text"] = sampleText
        sample["integral"] = sample["hist"].Integral()
        self.samples.append(sample)

    def addData(self, hist):

        self.data["name"] = "data"
        self.data["hist"] = hist
        self.data["hist"].SetLineColor(ROOT.kBlack)
        self.data["hist"].SetMarkerColor(ROOT.kBlack)
        self.data["hist"].SetMarkerStyle(8)
        self.data["hist"].SetMarkerSize(1)

        self.legend.AddEntry(self.data["hist"], "Data (RUN II)", "pel")

        self.noData = False

        if hist.GetMaximum() > self.yMax:
            self.yMax = hist.GetMaximum()

    #Add each systematic error for each sample
    #+Creat a list of systematics names
    def addSystematic(self, sampleName, sysName, upHist, downHist):

        for smp in self.samples:
            if smp["name"] == sampleName:
                deltaUp = upHist.Clone()
                deltaUp.Add(smp["hist"], -1)
                deltaDown = downHist.Clone()
                deltaDown.Add(smp["hist"], -1)
                self.systDeltas.append((sampleName, sysName, deltaUp, deltaDown))
                self.systNames.append(sysName)

        self.noSyst = False


#---Private functions-----------------------------------------------------------

    def buildStack(self):

        sampleList = []
        isFirst = True
        for smp in self.samples:
            if isFirst:
                self.totalHist = smp["hist"].Clone()
                isFirst = False
            else:
                self.totalHist.Add(smp["hist"])
            sampleList.append((smp["name"], smp["integral"], smp["hist"], smp["text"]))
        # Sort by integral
        def takeSecond(elem):
            return elem[1]
        sampleList.sort(key=takeSecond)
        #build the stack
        for name, integral, hist, text in sampleList:
            self.stack.Add(hist)
        #build legend
        for name, integral, hist, text in reversed(sampleList):
            self.legend.AddEntry(hist, text)

        if self.totalHist.GetMaximum() > self.yMax:
            self.yMax = self.totalHist.GetMaximum()

    def buildUncertainty(self):

        nBins = self.totalHist.GetNbinsX()
        for i in range(nBins):
            binNumber = i+1
            binCenter = self.totalHist.GetXaxis().GetBinCenter(binNumber)
            binXUp = self.totalHist.GetXaxis().GetBinUpEdge(binNumber)
            binXLow = self.totalHist.GetXaxis().GetBinLowEdge(binNumber)
            binContent = self.totalHist.GetBinContent(binNumber)
            self.totalError.SetPoint(binNumber, binCenter, binContent)

            upErr2 = pow(10, -20)
            downErr2 = pow(10, -20)
            for sys in self.systNames:
                shiftUp = 0
                shiftDown = 0
                for sampleName, sysName, deltaUp, deltaDown in self.systDeltas:
                    if sys == sysName:
                        shiftUp   += deltaUp.GetBinContent(binNumber)
                        shiftDown += deltaDown.GetBinContent(binNumber)
                upErr2   += pow(shiftUp,2)
                downErr2 += pow(shiftDown,2)
            xELow  = binCenter - binXLow
            xEHigh = binXUp - binCenter
            self.totalError.SetPointError(binNumber, xELow, xEHigh, sqrt(downErr2), sqrt(upErr2))

        self.totalError.SetFillStyle(3245)
        self.totalError.SetFillColor(13)
        self.totalError.SetLineWidth(0)
        self.totalError.SetMarkerStyle(0)

    def getRatio(self,h1,h2):

        self.padSize["yWidth"] += 200

        ratio = h1.Clone()
        Nbins = ratio.GetSize()-2
        for i in range(Nbins):
            bin=i+1
            if h2.GetBinContent(bin)==0:
                r=-1
                e=0
            else:
                r = h1.GetBinContent(bin)/h2.GetBinContent(bin)
                e = h1.GetBinError(bin)/h2.GetBinContent(bin)
            ratio.SetBinContent(bin,r)
            ratio.SetBinError(bin,e)

        return ratio

    def getRatioUncert(self, errorgraph):

        ratio = errorgraph.Clone()
        Npoints = errorgraph.GetN()
        for i in range(Npoints):
            point=i+1
            d1, d2 = ROOT.Double(0.), ROOT.Double(0.)
            errorgraph.GetPoint(point, d1, d2)
            Xval = float(d1)
            Yval = float(d2)
            eX_hi = errorgraph.GetErrorXhigh(point)
            eX_lo = errorgraph.GetErrorXlow(point)

            if Yval==0:
                eY_hi = 0
                eY_lo = 0
            else:
                eY_hi = errorgraph.GetErrorYhigh(point)/Yval
                eY_lo = errorgraph.GetErrorYlow(point)/Yval

            ratio.SetPoint(point, Xval, 1.0)
            ratio.SetPointError(point, eX_lo, eX_hi, eY_lo, eY_hi)

        return ratio

    def getRatioLine(self, h1):
        line = h1.Clone()
        Nbins = line.GetSize()-2
        for i in range(Nbins):
            bin=i+1
            line.SetBinContent(bin,1.0)
            line.SetBinError(bin,0.0)
        return line

    def setDrawOptions(self,hist):

        hist.GetYaxis().SetRangeUser(self.yMin, self.yMax*self.yFactor)
        hist.GetXaxis().SetTitle(self.xTitle)
        hist.GetYaxis().SetTitle(self.yTitle)
        hist.SetStats(False)
        hist.SetTitle(self.name)
        # precision 3 fonts. see https://root.cern.ch/root/htmldoc//TAttText.html#T5
        hist.GetXaxis().SetTitleFont(43)
        hist.GetYaxis().SetTitleFont(43)
        hist.GetXaxis().SetLabelFont(43)
        hist.GetYaxis().SetLabelFont(43)
        hist.GetXaxis().SetTitleSize(24)
        hist.GetYaxis().SetTitleSize(24)
        hist.GetXaxis().SetLabelSize(20)
        hist.GetYaxis().SetLabelSize(20)

        if not self.ratio:
            hist.GetYaxis().SetTitleOffset( 1.3 )
        else:
            hist.GetYaxis().SetTitleOffset( 1.6 )

    def setRatioDrawOptions(self, ratio):

        ratio.SetTitle('')
        ratio.GetYaxis().SetTitle(self.ratioTitle)
        ratio.GetYaxis().SetRangeUser(0,2)
        ratio.GetYaxis().SetNdivisions(505)
        ratio.GetYaxis().CenterTitle()
        ratio.GetYaxis().SetTitleSize(22)
        ratio.GetYaxis().SetTitleFont(43)
        ratio.GetYaxis().SetTitleOffset(2.2)
        ratio.GetYaxis().SetLabelFont(43)
        ratio.GetYaxis().SetLabelSize(19)
        ratio.GetYaxis().SetLabelOffset(0.009)
        ratio.GetXaxis().SetTitle(self.xTitle)
        ratio.GetXaxis().SetTickLength(0.07)
        ratio.GetXaxis().SetTitleSize(25)
        ratio.GetXaxis().SetTitleFont(43)
        ratio.GetXaxis().SetTitleOffset(4.0)
        ratio.GetXaxis().SetLabelFont(43)
        ratio.GetXaxis().SetLabelSize(21)
        ratio.GetXaxis().SetLabelOffset(0.035)
        ratio.GetXaxis().SetNdivisions(505)

    def setLabel(self):

        cmsText = ROOT.TLatex(3.5, 24, "CMS Simulation")
        cmsText.SetNDC()
        cmsText.SetTextAlign(33)
        cmsText.SetTextFont(42)
        if self.ratio: cmsText.SetTextSize(0.05)
        else:          cmsText.SetTextSize(0.036)
        cmsText.SetX(0.50)
        cmsText.SetY(0.98)
        cmsText.Draw()

        infoText = "%s fb^{-1} (13 TeV)" %("137.5")
        lumiText = ROOT.TLatex(3.5, 24, infoText)
        lumiText.SetNDC()
        lumiText.SetTextAlign(33)
        lumiText.SetTextFont(42)
        lumiText.SetX(0.94)
        if self.ratio:
            lumiText.SetTextSize(0.045)
            lumiText.SetY(0.98)
        else:
            lumiText.SetTextSize(0.0367)
            lumiText.SetY(0.951)
        lumiText.Draw()

        return cmsText, lumiText

#---Public function ------------------------------------------------------------

    #Draw and store plots
    def draw(self, plot_directory=None, log=False, texX = "" , texY = "Number of Events", extensions = ["pdf", "png", "root"], ratio = False):

        ROOT.gROOT.LoadMacro("$CMSSW_BASE/src/RootTools/plot/scripts/tdrstyle.C")
        ROOT.setTDRStyle()

        if plot_directory is None : plot_directory = self.plot_dir
        self.xTitle = texX
        self.yTitle = texY
        self.ratio = ratio
        c1 = ROOT.TCanvas("c1","c1",200,10, 500, 500)

        if self.ratio:
            c1.SetCanvasSize(500,700)
            yRatio = 0.31
            c1.Divide(1,2,0,0)
            topPad = c1.cd(1)
            topPad.SetBottomMargin(0)
            topPad.SetLeftMargin(0.15)
            topPad.SetTopMargin(0.07)
            topPad.SetRightMargin(0.05)
            topPad.SetPad(topPad.GetX1(), yRatio , topPad.GetX2(), topPad.GetY2())

            bottomPad = c1.cd(2)
            bottomPad.SetPad(bottomPad.GetX1(), bottomPad.GetY1(), bottomPad.GetX2(), yRatio)
            bottomPad.SetTopMargin(0)
            bottomPad.SetRightMargin(0.05)
            bottomPad.SetLeftMargin(0.15)
            bottomPad.SetBottomMargin(0.13*3.5)
        else:
            topPad = c1
            topPad.SetBottomMargin(0.13)
            topPad.SetLeftMargin(0.15)
            topPad.SetTopMargin(0.07)
            topPad.SetRightMargin(0.05)

        topPad.cd()
        if log: self.yFactor = 10000*1.7
        else: self.yFactor = 1.7
        topPad.SetLogy(log)
        topPad.SetTitle(self.name)

        if self.totalHist.GetMaximum()==0:
            self.buildStack()
            if not self.noSyst:
                self.legend.AddEntry(self.totalError, "Systematic Uncertainty")
                self.buildUncertainty()

        self.setDrawOptions(self.totalHist)
        self.totalHist.Draw("hist")
        self.stack.Draw("hist same")
        self.totalError.Draw("E2 hist same")

        if not self.noData :
            self.data["hist"].Draw("p hist same")

        self.legend.SetFillStyle(0)
        self.legend.SetShadowColor(ROOT.kWhite)
        self.legend.SetBorderSize(0)
        self.legend.SetNColumns(2)
        self.legend.Draw()
        cmsText, subLabel = self.setLabel()

        topPad.RedrawAxis()

        #Draw ratio
        if self.ratio:
            bottomPad.cd()
            topPad.SetTitle(self.name+"_ratio")
            ratioline = self.getRatioLine(self.totalHist)
            self.setRatioDrawOptions(ratioline)
            ratioline.SetFillColor(0)
            ratioline.SetLineColor(13)
            ratioline.SetLineWidth(2)
            ratioline.Draw("hist")
            ratio_uncert = self.getRatioUncert(self.totalError)
            ratio_uncert.Draw("E2")
            if not self.noData:
                ratio_data = self.getRatio(self.data["hist"], self.totalHist)
                self.setRatioDrawOptions(ratio_data)
                ratio_data.Draw("P SAME")
            ROOT.gPad.RedrawAxis()


        #save the plot
        if not os.path.exists(plot_directory):
            try:
                os.makedirs(plot_directory)
            except OSError: # Resolve rare race condition
                pass
        
        plot_helpers.copyIndexPHP(plot_directory)

        for extension in extensions:
            plotname = os.path.join(plot_directory, self.name+".%s"%extension)
            c1.Print(plotname)
