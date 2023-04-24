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
	self.otherLegend = ROOT.TLegend(0.18,0.88-0.03*10,0.9,0.88)
        self.xTitle = "something"
        self.yTitle = "Number of Events"
        self.ratioTitle = "Data/MC"
        self.ratio = None
        self.stack = None
        self.binning = None
        self.yMax = 0
        self.yMin = 0.9
        self.yFactor = 1.7
	self.yC = 1.05
        self.samples = []
        self.systDeltas = []
        self.systNames = []
        self.data = {}
        self.totalHist = ROOT.TH1F()
        self.totalError = ROOT.TGraphErrors()
        self.stack = ROOT.THStack()
	self.postFitUnc = ROOT.TH1F()
        
        self.log = False
        self.ratio = False
        self.noData = True
        self.noSyst = True
	self.comparisonPlots = False
	self.hasPostFitUnc = False

#---Public funtions ------------------------------------------------------------

    #Add a new sample
    #+ Creat a list of all histograms
    def addSample(self, sampleName, hist, sampleText, color=None):

        sample = {}
        sample["name"] = sampleName
        sample["hist"] = hist
	if not color==None: 
		sample["hist"].SetFillColor(color)
		sample["hist"].SetLineColor(ROOT.kBlack)
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
    def addSystematic(self, sampleName, sysName, upHist, downHist, color):

        for smp in self.samples:
            if smp["name"] == sampleName:
                delta = upHist.Clone()
                delta.Add(downHist, -1)
		for i in range(delta.GetNbinsX()):
		    delta.SetBinContent(i,abs(delta.GetBinContent(i)))
		scaledHist = smp["hist"].Clone()
		scaledHist.Add(delta, 0.5)
		self.systDeltas.append((sampleName, sysName, delta, scaledHist))
                syst= {}
		syst["name"] = sysName
		syst["color"] = color
		if not syst in self.systNames:
			self.systNames.append(syst)

        self.noSyst = False

    def addPostFitUnc(self,hist):
	
	self.postFitUnc = hist
	self.postFitUnc.SetFillColorAlpha(13,0.5)
	self.postFitUnc.SetFillStyle(3245)
	self.legend.AddEntry(hist, "post-fit unc.")

	self.hasPostFitUnc = True
	

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

            Err2 = pow(10, -20)
            for sys in self.systNames:
                shift = 0
                for sampleName, sysName, delta, scaledHist in self.systDeltas:
                    if sys["name"] == sysName:
                        shift   += delta.GetBinContent(binNumber)
                Err2   += pow(shift,2)
            xE  = (binXUp - binXLow)/2
            self.totalError.SetPointError(binNumber, xE, sqrt(Err2)/2)

        self.totalError.SetFillStyle(3245)
        self.totalError.SetFillColor(13)
        self.totalError.SetLineWidth(0)
        self.totalError.SetMarkerStyle(0)

    def getRatio(self,h1,h2):

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
            eX = errorgraph.GetErrorXlow(point)

            if Yval==0:
                eY = 0
            else:
                eY = errorgraph.GetErrorYlow(point)/Yval

            ratio.SetPoint(point, Xval, 1.0)
            ratio.SetPointError(point, eX, eY)

        return ratio

    def getPostFitDataRatio(self,h1,h2):
        ratio = h1.Clone()
        Nbins = ratio.GetN()
        for i in range(Nbins):
            bin=i+1
            if h2.GetBinContent(bin)==0:
                r=-1
                e=0
            else:
   	        d1, d2 = ROOT.Double(0.), ROOT.Double(0.)
   	        h1.GetPoint(bin, d1, d2)
   	        Xval = float(d1)
   	        Yval = float(d2)
   	        eX = h1.GetErrorXlow(bin)
   
                r = Yval/h2.GetBinContent(bin)
   	    #print d2, Yval, h2.GetBinContent(bin), r
                eY = h1.GetErrorYlow(bin)/h2.GetBinContent(bin)
            ratio.SetPoint(bin,Xval,r)
           
	return ratio
   
    def getPostFitRatioUnc(self,h1):
       ratio = h1.Clone()
       Nbins = ratio.GetSize()-2
       for i in range(Nbins):
           bin=i+1
           if h1.GetBinContent(bin)==0:
               e=0
           else:
               e = h1.GetBinError(bin)/h1.GetBinContent(bin)
   	   ratio.SetBinContent(bin,1)
   	   ratio.SetBinError(bin,e)
   
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
	if self.hasPostFitUnc:
        	ratio.GetYaxis().SetRangeUser(0.9,1.1)
	else:   ratio.GetYaxis().SetRangeUser(0,2)
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
        cmsText.SetTextSize(0.05)
        cmsText.SetX(0.50)
        cmsText.SetY(0.98)
        cmsText.Draw()

        infoText = "%s fb^{-1} (13 TeV)" %("137.5")
        lumiText = ROOT.TLatex(3.5, 24, infoText)
        lumiText.SetNDC()
        lumiText.SetTextAlign(33)
        lumiText.SetTextFont(42)
        lumiText.SetX(0.94)
        lumiText.SetTextSize(0.045)
        lumiText.SetY(0.98)
        lumiText.Draw()

        return cmsText, lumiText

    def buildComparisonPlots(self):
	
	for sys in self.systNames:
	    firstHist = True
            for sampleName, sysName, delta, scaledHist in self.systDeltas:
                 if sys["name"] == sysName:
			if firstHist:
				sys["totalScaledHist"] = scaledHist.Clone()
				firstHist = False	
			else:
			 	sys["totalScaledHist"].Add(scaledHist)

	    sys["totalScaledHist"].Divide(self.totalHist)
	    self.otherLegend.AddEntry(sys["totalScaledHist"], sys["name"])
	    if sys["totalScaledHist"].GetMaximum() > self.yC:
            		self.yC = sys["totalScaledHist"].GetMaximum()
	   
    def setComparisonDrawOptions(self):
	
	for sys in self.systNames:
		sys["totalScaledHist"].SetFillColor(0)
		sys["totalScaledHist"].SetLineColor(sys["color"])
		sys["totalScaledHist"].GetXaxis().SetTitle(self.xTitle)
        	sys["totalScaledHist"].GetYaxis().SetTitle("Events/0.01")
        	sys["totalScaledHist"].SetStats(False)
        	sys["totalScaledHist"].SetTitle(self.name+"_syst")
        	# precision 3 fonts. see https://root.cern.ch/root/htmldoc//TAttText.html#T5
        	sys["totalScaledHist"].GetXaxis().SetTitleFont(43)
        	sys["totalScaledHist"].GetYaxis().SetTitleFont(43)
        	sys["totalScaledHist"].GetXaxis().SetLabelFont(43)
        	sys["totalScaledHist"].GetYaxis().SetLabelFont(43)
        	sys["totalScaledHist"].GetXaxis().SetTitleSize(24)
        	sys["totalScaledHist"].GetYaxis().SetTitleSize(24)
        	sys["totalScaledHist"].GetXaxis().SetLabelSize(20)
        	sys["totalScaledHist"].GetYaxis().SetLabelSize(20)
            	sys["totalScaledHist"].GetYaxis().SetTitleOffset( 1.3 )

		


#---Public function ------------------------------------------------------------

    #Draw and store plots
    def draw(self, plot_directory=None, log=False, texX = "" , texY = "Number of Events", extensions = ["pdf", "png", "root"], ratio = False, comparisonPlots = False):

        ROOT.gROOT.LoadMacro("$CMSSW_BASE/src/RootTools/plot/scripts/tdrstyle.C")
        ROOT.setTDRStyle()
	ROOT.gStyle.SetErrorX(0.5)

        if plot_directory is None : plot_directory = self.plot_dir
        self.xTitle = texX
        self.yTitle = texY
        self.ratio = ratio
	self.comparisonPlots = comparisonPlots
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

	if self.hasPostFitUnc : 
	    self.postFitUnc.Draw("E2 same")
	    
        if not self.noData :
            self.data["hist"].Draw("E1 X0 hist p same")

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
	    if not self.noSyst:
            	ratio_uncert = self.getRatioUncert(self.totalError)
		ratio_uncert.Draw("E2")
	    elif self.hasPostFitUnc :
		ratio_uncert = self.getPostFitRatioUnc(self.postFitUnc)
	        ratio_uncert.Draw("E2 same")
            if not self.noData:
		if not self.hasPostFitUnc :
		    ratio_data = self.getRatio(self.data["hist"], self.totalHist)
                    self.setRatioDrawOptions(ratio_data)
                    ratio_data.Draw("P SAME")
		else:
		    ratio_data = self.getPostFitDataRatio(self.data["hist"], self.totalHist)
		    self.setRatioDrawOptions(ratio_data)
		    ratio_data.Draw("X0 E1 P SAME")
            ROOT.gPad.RedrawAxis()

	#Draw Comparison Plots
	if self.comparisonPlots and not log:
	    self.buildComparisonPlots()
	    self.setComparisonDrawOptions()
	    c2 = ROOT.TCanvas("c2","c2",200,10, 500, 500)
            pad = c2
            pad.SetBottomMargin(0.13)
            pad.SetLeftMargin(0.15)
            pad.SetTopMargin(0.07)
            pad.SetRightMargin(0.05)
	    pad.cd()
            pad.SetTitle(self.name+"_syst")
	    
	    isFirstHere = True
	    for sys in self.systNames:
		    if isFirstHere:
			    sys["totalScaledHist"].GetYaxis().SetRangeUser(1, self.yC*1.3)
			    sys["totalScaledHist"].Draw("hist")
			    isFirstHere = False
		    else:
			    sys["totalScaledHist"].Draw("hist same")
 
	    self.otherLegend.SetFillStyle(0)
            self.otherLegend.SetShadowColor(ROOT.kWhite)
            self.otherLegend.SetBorderSize(0)
            self.otherLegend.SetNColumns(2)	    
	    self.otherLegend.Draw()
	    cmsText, subLabel = self.setLabel()
            pad.RedrawAxis()



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
	    if self.comparisonPlots and not log:
	    	compraisonPlotname = os.path.join(plot_directory, self.name+"_syst.%s"%extension)
	    	c2.Print(compraisonPlotname)
