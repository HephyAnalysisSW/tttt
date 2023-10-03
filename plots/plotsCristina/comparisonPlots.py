import os, ROOT, random
from tttt.Tools.user                     import plot_directory
import Analysis.Tools.syncer
import Analysis.Tools.user as user
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--plot_directory', action='store', default='4t-v10.4')
argParser.add_argument('--era', action='store', default="Run2016_preVFP")
argParser.add_argument('--selection', action='store', default='6To7')
argParser.add_argument('--logLevel',       action='store',      default='INFO', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--ISR',            action='store',      default='40')
args = argParser.parse_args()

import tttt.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

ISRdict = { "40":   "ISRJet_pt40",  "60":   "ISRJet_pt60",  "80":   "ISRJet_pt80",
            "100":  "ISRJet_pt100", "150":  "ISRJet_pt150", "200":  "ISRJet_pt200"}

if args.era in ["Run2016_preVFP", "Run2016", "Run2017", "Run2018"]:
    plot_directory_ = os.path.join(plot_directory, 'analysisPlots', args.plot_directory, args.era, args.selection)
elif args.era == "RunII":
    plot_directory_ = os.path.join(plot_directory, 'analysisPlots', args.plot_directory, 'RunII', args.selection)

if not os.path.exists(plot_directory_):
        os.makedirs(plot_directory_)

# selections = ["trg-dilep-OS-minDLmass20-offZ1-lepVeto2-njet6to7-btag2", "trg-dilep-OS-minDLmass20-onZ1-lepVeto2-njet6to7-btag2"]
hist_dir = "/groups/hephy/cms/cristina.giordano/www/tttt/plots/analysisPlots/4t-v10.3/"

if args.selection == '4To5':
    selections = ["trg-dilep-OS-minDLmass20-offZ1-lepVeto2-njet4To5-btag1", "trg-dilep-OS-minDLmass20-offZ1-lepVeto2-njet4To5-btag2", "trg-dilep-OS-minDLmass20-offZ1-lepVeto2-njet4To5-btag3p",
                  "trg-dilep-OS-minDLmass20-onZ1-lepVeto2-njet4To5-btag1", "trg-dilep-OS-minDLmass20-onZ1-lepVeto2-njet4To5-btag2", "trg-dilep-OS-minDLmass20-onZ1-lepVeto2-njet4To5-btag3p"]
elif args.selection == '6To7':
    selections = ["trg-dilep-OS-minDLmass20-offZ1-lepVeto2-njet6To7-btag1", "trg-dilep-OS-minDLmass20-offZ1-lepVeto2-njet6To7-btag2", "trg-dilep-OS-minDLmass20-offZ1-lepVeto2-njet6To7-btag3p",
                  "trg-dilep-OS-minDLmass20-onZ1-lepVeto2-njet6To7-btag1", "trg-dilep-OS-minDLmass20-onZ1-lepVeto2-njet6To7-btag2", "trg-dilep-OS-minDLmass20-onZ1-lepVeto2-njet6To7-btag3p"]
elif args.selection == '8p':
    selections = [ "trg-dilep-OS-minDLmass20-offZ1-lepVeto2-njet8p-btag1", "trg-dilep-OS-minDLmass20-offZ1-lepVeto2-njet8p-btag2", "trg-dilep-OS-minDLmass20-offZ1-lepVeto2-njet8p-btag3p",
                    "trg-dilep-OS-minDLmass20-onZ1-lepVeto2-njet8p-btag1", "trg-dilep-OS-minDLmass20-onZ1-lepVeto2-njet8p-btag2", "trg-dilep-OS-minDLmass20-onZ1-lepVeto2-njet8p-btag3p"]


myfiles = [ROOT.TFile.Open(os.path.join(hist_dir, args.era, "all_log", sel, ISRdict[args.ISR]+".root")) for sel in selections]
hists = []

for myfile, sel in zip(myfiles, selections):
    if not myfile or myfile.IsZombie():
        print("Error: Unable to open the ROOT file for selection: {}".format(sel))
    else:
        keys = myfile.GetListOfKeys()
        for key in keys:
            canvasName = key.ReadObj().GetName()
            canvas = myfile.Get(canvasName)
            pad = canvas.GetListOfPrimitives()[0]
            padContent = pad.GetListOfPrimitives()
            for obj in padContent:
                if obj.IsA().InheritsFrom("TH1") and 'DY' in obj.GetName():
                    hists.append((obj, obj.GetName(), sel))

def normalize_histograms(hist):
    integral = hist.Integral()
    if integral> 0 :
        scaling_factor = 1.0/integral
        hist.Scale(scaling_factor)

def draw_histograms(hists):
    if not hists:
        print("No histograms???")
        return

    colourWheel = [ROOT.kRed, ROOT.kBlue, ROOT.kGreen, ROOT.kOrange, ROOT.kCyan, ROOT.kMagenta, ROOT.kSpring+10, ROOT.kViolet]

    canvas = ROOT.TCanvas("canvas", "Histogram", 900, 600)
    canvas.SetLogy()

    legend = ROOT.TLegend(0.54, 0.64, 0.89, 0.89)
    legend.SetTextSize(0.03)
    legend.SetFillColor(0)
    legend.SetBorderSize(0)
    legend.SetHeader("Legend")
    legend.SetMargin(0.15)

    processed_legend_entries = set()

    for i, (hist, name, directory) in enumerate(hists):
        hist.SetBinContent(0, 0)
        hist.SetTitle("DY")
        normalize_histograms(hist)

        parts = directory.split('-')
        filtered_parts = [part for part in parts if part.startswith(("off", "on", "njet", "btag"))]
        transformed_directory = "-".join(filtered_parts)
        legend_entry = "{}".format( transformed_directory)
        if legend_entry in processed_legend_entries:
            continue

        processed_legend_entries.add(legend_entry)
        if colourWheel:
            colour = random.choice(colourWheel)
            colourWheel.remove(colour)
            hist.SetLineColor(colour)
        else:
            hist.SetLineColor(ROOT.kBlack)

        if i == 0:
            hist.Draw()
        else:
            hist.Draw("same")

        hist.SetStats(0)
        legend.AddEntry(hist, legend_entry, "l")

    legend.Draw()
    canvas.Update()
    canvas.WaitPrimitive()
    files = ["pdf", "png", "root"]
    for f in files:
        canvas.Print(os.path.join(plot_directory_, "ISRJet_pt40."+f))

draw_histograms(hists)
