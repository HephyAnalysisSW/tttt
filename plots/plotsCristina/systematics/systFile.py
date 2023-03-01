#!/usr/bin/env python
''' Plots with systematics
'''
################################################################################
# Standard imports and batch mode
import ROOT, os
ROOT.gROOT.SetBatch(True)
c1 = ROOT.TCanvas() #avoid version conflict in png.h with keras import
c1.Draw()
c1.Print('delete.png')
import itertools
import copy
import array
import operator
import numpy as np
from math                                import sqrt, cos, sin, pi, atan2, cosh, exp

# RootTools
from RootTools.core.standard             import *

# tttt
from tttt.Tools.user                import plot_directory
from tttt.Tools.cutInterpreter      import cutInterpreter
from tttt.Tools.helpers             import getCollection, closestOSDLMassToMZ, deltaR, deltaPhi, bestDRMatchInCollection, nonEmptyFile, getSortedZCandidates, cosThetaStar, m3, getMinDLMass
from tttt.Tools.objectSelection     import getMuons, getElectrons, muonSelector, eleSelector, getGoodMuons, getGoodElectrons, isBJet, getGenPartsAll, getJets, genLepFromZ, mvaTopWP, getGenZs, isAnalysisJet, lepString, lepStringNoMVA
from tttt.Tools.triggerEfficiency   import triggerEfficiency

#from tWZ.Tools.helpers                   import getCollection, cosThetaStarNew, getTheta, gettheta, getphi
#from tWZ.Tools.leptonSF_topMVA           import leptonSF_topMVA
#from tWZ.Tools.leptonFakerate            import leptonFakerate

# Analysis
from Analysis.Tools.helpers              import deltaPhi, deltaR
from Analysis.Tools.puProfileCache       import *
from Analysis.Tools.puReweighting        import getReweightingFunction
from Analysis.Tools.leptonJetArbitration import cleanJetsAndLeptons
from Analysis.Tools.WeightInfo           import WeightInfo
from Analysis.Tools.LeptonSF_UL          import LeptonSF

import Analysis.Tools.syncer

################################################################################
# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',       action='store',      default='INFO', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--noData',         action='store_true', default=False, help='also plot data?')
argParser.add_argument('--small',          action='store_true', help='Run only on a small subset of the data?', )
argParser.add_argument('--dataMCScaling',  action='store_true', help='Data MC scaling?', )
argParser.add_argument('--plot_directory', action='store', default='tttt_v5')
argParser.add_argument('--era',            action='store', type=str, default="137. if args.noData else data_sample.lumi/1000.")
argParser.add_argument('--selection',      action='store', default='dilepL-minDLmass20-offZ1-njet4p-btag2p')
argParser.add_argument('--sys',            action='store', default='central')
argParser.add_argument('--nicePlots',      action='store_true', default=False)
argParser.add_argument('--twoD',           action='store_true', default=False)
argParser.add_argument('--triplet',        action='store_true', default=False)
argParser.add_argument('--doTTbarReco',    action='store_true', default=False)
argParser.add_argument('--applyFakerate',  action='store_true', default=False)
argParser.add_argument('--nonpromptOnly',  action='store_true', default=False)
argParser.add_argument('--splitnonprompt', action='store_true', default=False)
argParser.add_argument('--noLooseSel',     action='store_true')
argParser.add_argument('--noLooseWP',      action='store_true')
argParser.add_argument('--useDataSF',      action='store_true')
argParser.add_argument('--mvaTOPv1',       action='store_true')
args = argParser.parse_args()

################################################################################
# Logger
import tttt.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

################################################################################
# Possible SYS variations
variations = [
    "Trigger_UP", "Trigger_DOWN",
    "LepID_UP", "LepID_DOWN",
    "BTag_b_UP", "BTag_b_DOWN",
    "BTag_l_UP", "BTag_l_DOWN",
    "PU_UP", "PU_DOWN",
    "JES_UP", "JES_DOWN",
    "Scale_UPUP", "Scale_UPNONE", "Scale_NONEUP", "Scale_NONEDOWN", "Scale_DOWNNONE", "Scale_DOWNDOWN",
]

jet_variations = {
    "JES_UP": "jesTotalUp",
    "JES_DOWN": "jesTotalDown",
    "JER_UP": "jerUp",
    "JER_DOWN": "jerDown",
}

################################################################################
# Check if we know the variation else don't use data!
if args.sys not in variations:
    if args.sys == "central":
        logger.info( "Running central samples (no sys variation)")
    else:
        raise RuntimeError( "Variation %s not among the known: %s", args.sys, ",".join( variations ) )
else:
    logger.info( "Running sys variation %s, noData is set to 'True'", args.sys)
    args.noData = True


################################################################################
# Some info messages
if args.small:                        args.plot_directory += "_small"
if args.mvaTOPv1:                     args.plot_directory += "_mvaTOPv1"
if args.noData:                       args.plot_directory += "_noData"
if args.nonpromptOnly:                args.plot_directory += "_nonpromptOnly"
if args.splitnonprompt:               args.plot_directory += "_splitnonprompt"
if args.applyFakerate:                args.plot_directory += "_FakeRateSF"
if args.noLooseSel:                   args.plot_directory += "_noLooseSel"
if args.noLooseWP:                    args.plot_directory += "_noLooseWP"
if args.useDataSF:                    args.plot_directory += "_useDataSF"
if args.sys is not 'central':         args.plot_directory += "_%s" %(args.sys)


logger.info( "Working in era %s", args.era)
if args.dataMCScaling:
    logger.info( "Data/MC scaling active")
else:
    logger.info( "Data/MC scaling not active")

if args.nicePlots:
    logger.info( "Only draw the plots")
else:
    logger.info( "Only saving into root file")

# if args.twoD:
#     logger.info( "Create EFT points in 2D")
# else:
#     logger.info( "Create EFT points in 1D")

if args.noData:
    logger.info( "Running without data")
else:
    logger.info( "Data included in analysis cycle")

if args.applyFakerate:
    logger.info( "Apply Fake rate")
else:
    logger.info( "Apply Fake Rate")

################################################################################
# Selection modifier
def jetSelectionModifier( sys, returntype = "func"):
    #Need to make sure all jet variations of the following observables are in the ntuple
    variiedJetObservables = ['nJetGood', 'nBTag', 'met_pt']
    if returntype == "func":
        def changeCut_( string ):
            for s in variiedJetObservables:
                string = string.replace(s, s+'_'+sys)
                if "met_pt" in string:
                    string = string.replace("met_pt", "MET_T1_pt")
            return string
        return changeCut_
    elif returntype == "list":
        list = []
        for v in variiedJetObservables:
            string = v+'_'+sys
            if "met_pt" in string:
                string = string.replace("met_pt", "MET_T1_pt")
            list.append(string)
        return list

def metSelectionModifier( sys, returntype = 'func'):
    #Need to make sure all MET variations of the following observables are in the ntuple
    variiedMetObservables = ['met_pt']
    if returntype == "func":
        def changeCut_( string ):
            for s in variiedMetObservables:
                string = string.replace(s, s+'_'+sys)
                if "met_pt" in string:
                    string = string.replace("met_pt", "MET_T1_pt")
            return string
        return changeCut_
    elif returntype == "list":
        list = []
        for v in variiedMetObservables:
            string = v+'_'+sys
            if "met_pt" in string:
                string = string.replace("met_pt", "MET_T1_pt")
            list.append(string)
        return list

################################################################################
# get scale weight
def getScaleWeight(event, sys):
    # Sometimes the nominal entry [4] is missing, so be careful
    weights_9point = {
        "Scale_DOWNDOWN": 0,
        "Scale_DOWNNONE": 1,
        "Scale_NONEDOWN": 3,
        "Scale_NONEUP"  : 5,
        "Scale_UPNONE"  : 7,
        "Scale_UPUP"    : 8,
    }
    weights_8point = {
        "Scale_DOWNDOWN": 0,
        "Scale_DOWNNONE": 1,
        "Scale_NONEDOWN": 3,
        "Scale_NONEUP"  : 4,
        "Scale_UPNONE"  : 6,
        "Scale_UPUP"    : 7,
    }
    index = -1
    if event.nScale == 9:
        index = weights_9point[sys]
    elif event.nScale == 8:
        index = weights_8point[sys]
    else:
        print "UNEXPECTED NUMBER OF SCALE WEIGHTS:", event.nScale,", not applying any weight"
        return 1.0
    return event.Scale_Weight[index]
################################################################################
# Add a selection selectionModifier

if args.sys in jet_variations.keys():
    selectionModifier = jetSelectionModifier(jet_variations[args.sys])
else:
    selectionModifier = None

################################################################################
# Define the MC samples
from tttt.samples.nano_private_UL20_RunII_postProcessed_dilep import *
#from tWZ.samples.nanoTuples_ULRunII_nanoAODv9_postProcessed import *

if args.era == "UL2016":
    mc = [Summer16.TTLep, Summer16.ST, Summer16.TTTT, Summer16.TTW, Summer16.TTZ,Summer16.TTH]
    #mc = [UL2016.TWZ_NLO_DR, UL2016.TTZ, UL2016.TTX_rare, UL2016.TZQ, UL2016.WZTo3LNu, UL2016.triBoson, UL2016.ZZ, UL2016.nonprompt_3l]
    # if args.applyFakerate or args.nonpromptOnly:
    #     if args.splitnonprompt:
    #         mc = [UL2016.WW, UL2016.Top, UL2016.DY]
    #     else:
    #         mc = [UL2016.nonprompt_3l]
    # samples_eft = []
elif args.era == "UL2016preVFP":
    mc = [Summer16_preVFP.TTLep, Summer16_preVFP.ST, Summer16_preVFP.TTTT, Summer16_preVFP.TTW, Summer16_preVFP.TTZ,Summer16_preVFP.TTH]
    #mc = [UL2016preVFP.TWZ_NLO_DR, UL2016preVFP.TTZ, UL2016preVFP.TTX_rare, UL2016preVFP.TZQ, UL2016preVFP.WZTo3LNu, UL2016preVFP.triBoson, UL2016preVFP.ZZ, UL2016preVFP.nonprompt_3l]
    # if args.applyFakerate or args.nonpromptOnly:
    #     if args.splitnonprompt:
    #         mc = [UL2016preVFP.WW, UL2016preVFP.Top, UL2016preVFP.DY]
    #     else:
    #         mc = [UL2016preVFP.nonprompt_3l]
    # samples_eft = []
elif args.era == "UL2017":
    mc = [Fall17.TTLep, Fall17.ST,Fall17.TTTT, Fall17.TTW, Fall17.TTZ, Fall17.TTH]
    # mc = [UL2017.TWZ_NLO_DR, UL2017.TTZ, UL2017.TTX_rare, UL2017.TZQ, UL2017.WZTo3LNu, UL2017.triBoson, UL2017.ZZ, UL2017.nonprompt_3l]
    # if args.applyFakerate or args.nonpromptOnly:
    #     if args.splitnonprompt:
    #         mc = [UL2017.WW, UL2017.Top, UL2017.DY]
    #     else:
    #         mc = [UL2017.nonprompt_3l]
    # samples_eft = []
elif args.era == "UL2018":
    mc = [Autumn18.TTLep, Autumn18.ST,Autumn18.TTTT, Autumn18.TTW, Autumn18.TTZ, Autumn18.TTH]
    # mc = [UL2018.TWZ_NLO_DR, UL2018.TTZ, UL2018.TTX_rare, UL2018.TZQ, UL2018.WZTo3LNu, UL2018.triBoson, UL2018.ZZ, UL2018.nonprompt_3l]
    # if args.applyFakerate or args.nonpromptOnly:
    #     if args.splitnonprompt:
    #         mc = [UL2018.WW, UL2018.Top, UL2018.DY]
    #     else:
    #         mc = [UL2018.nonprompt_3l]
    # samples_eft = []
# elif args.era == "ULRunII":
#     mc = [TWZ_NLO_DR, TTZ, TTX_rare, TZQ, WZTo3LNu, triBoson, ZZ, nonprompt_3]
#     # if args.applyFakerate or args.nonpromptOnly:
#     #     if args.splitnonprompt:
#     #         mc = [WW, Top, DY]
#     #     else:
#     #         mc = [nonprompt_3l]
#     # samples_eft = []

################################################################################
# EFT reweight

# WeightInfo
# eftweights = []
# for sample in samples_eft:
#     print "Reading weight function for", sample.name
#     w = WeightInfo(sample.reweight_pkl)
#     w.set_order(2)
#     eftweights.append(w)

# define which Wilson coefficients to plot
#cHq1Re11 cHq1Re22 cHq1Re33 cHq3Re11 cHq3Re22 cHq3Re33 cHuRe11 cHuRe22 cHuRe33 cHdRe11 cHdRe22 cHdRe33 cHudRe11 cHudRe22 cHudRe33

# WCs = [
#    # ('cHq3Re11', 1.0, ROOT.kCyan),
#    # ('cHq3Re22', 1.0, ROOT.kMagenta),
#    # ('cHq3Re33', 1.0, ROOT.kBlue),
#    ('cHq1Re11', -2.0, ROOT.kRed),
#     ('cHq1Re11', 2.0, ROOT.kRed),
#     ('cHq1Re22', -2.0, ROOT.kGreen+2),
#     ('cHq1Re22', 2.0, ROOT.kGreen+2),
#     ('cHq1Re33', -2.0, ROOT.kOrange-3),
#     ('cHq1Re33', 2.0, ROOT.kOrange-3),
#     # ('cHuRe11',  2.0, ROOT.kCyan),
#     # ('cHuRe22',  2.0, ROOT.kMagenta),
#     # ('cHuRe33',  2.0, ROOT.kBlue),
#     # ('cHdRe11',  2.0, ROOT.kViolet-9),
#     # ('cHdRe22',  2.0, ROOT.kGray),
#     # ('cHdRe33',  2.0, ROOT.kAzure+10),
# ]

Npoints = 51

if args.nicePlots:
    Npoints = 0

WCs = []
WC_setup = [
    ('cHq1Re11', ROOT.kRed),
    ('cHq1Re22', ROOT.kGreen+2),
    ('cHq1Re33', ROOT.kOrange-3),
    ('cHq3Re11', ROOT.kCyan),
    ('cHq3Re22', ROOT.kMagenta),
    ('cHq3Re33', ROOT.kBlue),
]
for i_wc, (WCname, color) in enumerate(WC_setup):
    for i in range(Npoints):
        minval = -10.
        maxval = 10.
        if 'cHq3Re11' in WCname:
            minval = -0.2
            maxval = 0.2
        value = minval + ((maxval-minval)/(Npoints-1))*i
        WCs.append( (WCname, value, color) )

params =  []
# for i_sample, sample in enumerate(samples_eft):
#     for i_wc, (WC, WCval, color) in enumerate(WCs):
#         params.append({'legendText':'%s=%3.4f'%(WC, WCval), 'color':color,  'WC':{WC:WCval} , 'sample': sample, 'i_sample': i_sample})

#### 2D scan
# if args.twoD:
#     minval1  = -4.0
#     maxval1  = 4.0
#     minval2  = -4.0
#     maxval2  = 4.0
#     Npoints1 = 21
#     Npoints2 = 21
#     WC1  = 'cHq1Re1122'
#     WC1a = 'cHq1Re11'
#     WC1b = 'cHq1Re22'
#     WC2  = 'cHq1Re33'
#     if args.triplet:
#         WC1  = 'cHq3Re1122'
#         WC1a = 'cHq3Re11'
#         WC1b = 'cHq3Re22'
#         WC2  = 'cHq3Re33'
#         minval1 = -0.2
#         maxval1 = 0.2
#     params = []
#     for i in range(Npoints1):
#         value1 = minval1 + ((maxval1-minval1)/(Npoints1-1))*i
#         for j in range(Npoints2):
#             value2 = minval2 + ((maxval2-minval2)/(Npoints2-1))*j
#             for i_sample, sample in enumerate(samples_eft):
#                 params.append({'legendText':'%s=%3.4f, %s=%3.4f'%(WC1,value1,WC2,value2), 'color':ROOT.kRed,  'WC':{WC1a:value1, WC1b:value1, WC2:value2} , 'sample': sample, 'i_sample': i_sample})
####

for i_param, param in enumerate(params):
    param['style']    = styles.lineStyle( param['color'] )

# Creating a list of weights
plotweights = []
# Add MC weights
weight_mc = []
for sample in mc:
    weight_ = lambda event, sample: 1. # Add event.weight and lumi weight to sample.weight later
    weight_mc.append(weight_)
plotweights.append(weight_mc)

# Add data weight
if not args.noData:
    plotweights.append([lambda event, sample: event.weight])
# Add EFT weight
# for param in params:
#     i_sample = param['i_sample']
#     eft_weight = eftweights[i_sample].get_weight_func(**param['WC'])
#     plotweights.append([eft_weight])

################################################################################
# Define the data sample
if   args.era == "UL2016":
    datastring = "Run2016"
    lumistring = "2016"
elif args.era == "UL2016preVFP":
    datastring = "Run2016_preVFP"
    lumistring = "2016_preVFP"
elif args.era == "UL2017":
    datastring = "Run2017"
    lumistring = "2017"
elif args.era == "UL2018":
    datastring = "Run2018"
    lumistring = "2018"
elif args.era == "ULRunII":
    datastring = "RunII"
    lumistring = "RunII"

try:
  data_sample = eval(datastring)
except Exception as e:
  logger.error( "Didn't find %s", datastring )
  raise e

lumi_scale                 = 137. if args.noData else data_sample.lumi/1000.
data_sample.scale          = 1.

# Set up MC sample
for sample in mc:
    sample.scale           = 1

for param in params:
    param['sample'].scale = 1

if args.small:
    for sample in mc + [data_sample]:
        sample.normalization = 1.
        sample.reduceFiles( to = 1 )
        sample.scale /= sample.normalization
    # for param in params[i_sample]:
    #     param['sample'].normalization = 1.
    #     param['sample'].reduceFiles( to = 1 )
    #     param['sample'].scale /= sample.normalization

################################################################################
# Lepton SF
LeptonWP = "tight"
if "trilepVL" in args.selection:
    LeptonWP = "VL"

### TODO: SETUP SF FOR MEDIUM WP
#era, muID = None, elID = None

leptonSF16 = LeptonSF(era = "UL2016", muID="tight", elID="medium")
leptonSF17 = LeptonSF(era = "UL2017", muID="tight", elID="medium")
leptonSF18 = LeptonSF(era = "UL2018", muID="tight", elID="medium")


# FakerateSF
mode = "SF"
dataMC = "MC"

if args.noLooseSel:
    mode = "SF_noLooseSel"
if args.noLooseWP:
    mode = "SF_noLooseWP"

if args.useDataSF:
    dataMC = "DATA"

#leptonFakerate18 = leptonFakerate("UL2018", mode, dataMC)

################################################################################
# Text on the plots
tex = ROOT.TLatex()
tex.SetNDC()
tex.SetTextSize(0.04)
tex.SetTextAlign(11) # align right

################################################################################
# Functions needed specifically for this analysis routine

def drawObjects( plotData, dataMCScale, lumi_scale ):
    lines = [
      (0.15, 0.95, 'CMS Preliminary' if plotData else 'CMS Simulation'),
      (0.45, 0.95, 'L=%3.1f fb{}^{-1} (13 TeV) Scale %3.2f'% ( lumi_scale, dataMCScale ) ) if plotData else (0.45, 0.95, 'L=%3.1f fb{}^{-1} (13 TeV)' % lumi_scale)
    ]
    if "mt2ll100" in args.selection and args.noData: lines += [(0.55, 0.5, 'M_{T2}(ll) > 100 GeV')] # Manually put the mt2ll > 100 GeV label
    return [tex.DrawLatex(*l) for l in lines]

def drawPlots(plots, mode, dataMCScale):
    for log in [False, True]:
        plot_directory_ = os.path.join(plot_directory, 'analysisPlots', args.plot_directory, args.era, mode + ("_log" if log else ""), args.selection)
        for plot in plots:
            if not max(l.GetMaximum() for l in sum(plot.histos,[])): continue # Empty plot
            if not args.noData:
                if mode == "all": plot.histos[1][0].legendText = "Data"
                if mode == "SF":  plot.histos[1][0].legendText = "Data (SF)"

            _drawObjects = []
            n_stacks=len(plot.histos)
            if isinstance( plot, Plot):
                plotting.draw(plot,
                  plot_directory = plot_directory_,
                  ratio = {'histos': [[i+1,0] for i in range(n_stacks-1)], 'yRange':(0.1,1.9)} if not args.noData else None,
                  logX = False, logY = log, sorting = True,
                  yRange = (0.03, "auto") if log else (0.001, "auto"),
                  scaling = {0:1} if args.dataMCScaling else {},
                  legend = ( (0.18,0.88-0.03*sum(map(len, plot.histos)),0.9,0.88), 2),
                  drawObjects = drawObjects( not args.noData, dataMCScale , lumi_scale ) + _drawObjects,
                  copyIndexPHP = True, extensions = ["png", "pdf", "root"],
                )

def getDeepJetsWP(disc,year):
    WP_L = {2016:0.0614, 2017:0.0521, 2018:0.0494}
    WP_M = {2016:0.3093, 2017:0.3033, 2018:0.2770}
    WP_T = {2016:0.7221, 2017:0.7489, 2018:0.7264}
    wp = 0
    if disc > WP_L[year]: wp = 1
    if disc > WP_M[year]: wp = 2
    if disc > WP_T[year]: wp = 3
    return wp

def getClosestBJetindex( event, object, minBtagValue ):
    minDR = 100
    closestjet = ROOT.TLorentzVector()
    for i in range(event.nJetGood):
        btagscore = event.JetGood_btagDeepFlavB[i]
        if btagscore > minBtagValue:
            jet = ROOT.TLorentzVector()
            jetidx = event.JetGood_index[i]
            jet.SetPtEtaPhiM(event.Jet_pt[jetidx], event.Jet_eta[jetidx], event.Jet_phi[jetidx], event.Jet_mass[jetidx])
            if object.DeltaR(jet) < minDR:
                minDR = object.DeltaR(jet)
                closestjet = jet
    return closestjet

def getWlep( event ):
    Wlep = ROOT.TLorentzVector()
    lepton  = ROOT.TLorentzVector()
    met     = ROOT.TLorentzVector()
    lepton.SetPtEtaPhiM(event.lep_pt[event.nonZ1_l1_index], event.lep_eta[event.nonZ1_l1_index], event.lep_phi[event.nonZ1_l1_index], 0)
    met.SetPtEtaPhiM(event.met_pt, 0, event.met_phi, 0)

    lepton_pT = ROOT.TVector3(lepton.Px(), lepton.Py(), 0)
    neutrino_pT = ROOT.TVector3(met.Px(), met.Py(), 0)

    mass_w = 80.399
    mu = mass_w * mass_w / 2 + lepton_pT * neutrino_pT
    A = - (lepton_pT * lepton_pT)
    B = mu * lepton.Pz()
    C = mu * mu - lepton.E() * lepton.E() * (neutrino_pT * neutrino_pT)
    discriminant = B * B - A * C
    neutrinos = []
    if discriminant <= 0:
        # Take only real part of the solution for pz:
        neutrino = ROOT.TLorentzVector()
        neutrino.SetPxPyPzE(met.Px(),met.Py(),-B / A,0)
        neutrino.SetE(neutrino.P())
        neutrinos.append(neutrino)
    else:
        discriminant = sqrt(discriminant)
        neutrino1 = ROOT.TLorentzVector()
        neutrino1.SetPxPyPzE(met.Px(),met.Py(),(-B - discriminant) / A,0)
        neutrino1.SetE(neutrino1.P())
        neutrino2 = ROOT.TLorentzVector()
        neutrino2.SetPxPyPzE(met.Px(),met.Py(),(-B + discriminant) / A,0)
        neutrino2.SetE(neutrino2.P())
        if neutrino1.E() > neutrino2.E():
            neutrinos.append(neutrino1)
            neutrinos.append(neutrino2)
        else:
            neutrinos.append(neutrino2)
            neutrinos.append(neutrino1)

    Wleps = []
    for neu in neutrinos:
        Wlep = lepton + neu
        Wleps.append([Wlep, lepton, neu])
    return Wleps


def looseSelection(lepindex, event):
    if args.noLooseSel:
        return True
    if lepindex < 0:
        return False

    if event.lep_sip3d[lepindex] > 8:
        return False
    if event.lep_pfRelIso03_all[lepindex] > 0.4:
        return False

    # elec
    if abs(event.lep_pdgId[lepindex]) == 11:
        eleindex = event.lep_eleIndex[lepindex]
        if not event.Electron_convVeto[eleindex]:
            return False
        # if event.Electron_tightCharge[eleindex] < 1:
        #     return False
        if ord(event.Electron_lostHits[eleindex]) > 1:
            return False

        passID = False
        # if event.Electron_mvaFall17V2Iso_WP80:
        if event.lep_jetBTag[lepindex] < 0.1:
            jetPtRatio = 1/(event.Electron_jetRelIso[eleindex]+1)
            if (event.year == 2016 and jetPtRatio > 0.5) or (event.year in [2017,2018] and jetPtRatio > 0.4):
                passID = True
        if event.lep_mvaTOPv2WP[lepindex] >= 4:
            passID = True
        if not passID:
            return False

    # muon
    if abs(event.lep_pdgId[lepindex]) == 13:
        muindex = event.lep_muIndex[lepindex]
        passID = False
        if event.lep_jetBTag[lepindex] < 0.025:
            jetPtRatio = 1/(event.Muon_jetRelIso[muindex]+1)
            if jetPtRatio > 0.45:
                passID = True
        if event.lep_mvaTOPv2WP[lepindex] >= 4:
            passID = True
        if not passID:
            return False

    return True
################################################################################
# Define sequences
sequence       = []

# def readWeights(sample,event):
#     if event.year == 2016 and not event.preVFP:
#         yearstring = "2016"
#     elif event.year == 2016 and event.preVFP:
#         yearstring = "2016_preVFP"
#     elif event.year == 2017:
#         yearstring = "2017"
#     elif event.year == 2018:
#         yearstring = "2018"
#     lumi_weight = lumi_year[yearstring]/1000.
#
#     print "-------------------------"
#     print "Weight  =", event.weight
#     print "Lumi    =", lumi_weight
#     return
#
# sequence.append(readWeights)

def getLeptonSF(sample, event):
    if sample.isData:
        return
    SF = 1
    # Search for variation
    sigma = 0
    if args.sys == "LepID_UP":
        sigma = 1
    elif args.sys == "LepID_DOWN":
        sigma = -1
    # Go through the 3 leptons and multiply SF
    idx1 = event.l1_index
    idx2 = event.l2_index
    idx3 = event.l3_index
    for i in [idx1, idx2, idx3]:
        pdgId = event.lep_pdgId[i]
        eta = event.lep_eta[i]
        if abs(pdgId)==11:
            eta+=event.Electron_deltaEtaSC[event.lep_eleIndex[i]]
        pt = event.lep_pt[i]
        if event.year == 2016:
            SF *= leptonSF16.getSF(pdgId, pt, eta, "sys", sigma )
        elif event.year == 2017:
            SF *= leptonSF17.getSF(pdgId, pt, eta, "sys", sigma )
        elif event.year == 2018:
            SF *= leptonSF18.getSF(pdgId, pt, eta, "sys", sigma )
    event.reweightLeptonMVA = SF
sequence.append( getLeptonSF )

def getLeptonFakeRate( sample, event ):
    SF = 1.0
    Nfakes = 0
    if args.applyFakerate:
        idx1 = event.l1_index
        idx2 = event.l2_index
        idx3 = event.l3_index
        for i in [idx1, idx2, idx3]:
            if event.lep_mvaTOPv2WP[i] < 4:
                # Do not use event if loose lepton selection is not satisfied
                if not looseSelection(i, event):
                    event.reweightLeptonFakerate = 0
                    return
                ####
                Nfakes += 1
                pdgId = event.lep_pdgId[i]
                eta = event.lep_eta[i]
                pt = event.lep_ptCone[i]
                sigma = 0
                fakerate = leptonFakerate18.getFactor(pdgId, pt, eta, "sys", sigma )
                if fakerate > 0.9:
                    fakerate = 0.9
                SF *= fakerate/(1-fakerate)
    sign = -1 if (Nfakes > 0 and (Nfakes % 2) == 0) else 1 # for two failing leptons there is a negative sign
    event.reweightLeptonFakerate = sign*SF
    # print Nfakes, event.reweightLeptonFakerate
sequence.append(getLeptonFakeRate)

# def getSYSweight(sample, event):
#     print "-------------------"
#     print sample.files
#     print getScaleWeight(event, "Scale_UPUP")
#     print getScaleWeight(event, "Scale_UPNONE")
#     print getScaleWeight(event, "Scale_NONEUP")
#     print getScaleWeight(event, "Scale_DOWNDOWN")
#     print getScaleWeight(event, "Scale_DOWNNONE")
#     print getScaleWeight(event, "Scale_NONEDOWN")
#
# sequence.append( getSYSweight )

def getMlb(sample, event):
    lepton = ROOT.TLorentzVector()
    if not 'qualep' in args.selection:
        lepton.SetPtEtaPhiM(event.lep_pt[event.nonZ1_l1_index], event.lep_eta[event.nonZ1_l1_index], event.lep_phi[event.nonZ1_l1_index], 0)
    else:
        lepton.SetPtEtaPhiM(0,0,0,0)

    # Get closest tight b:
    minBtagValue = 0.7221
    if   event.year == 2017: minBtagValue = 0.7489
    elif event.year == 2018: minBtagValue = 0.7264
    closestjet = ROOT.TLorentzVector()
    closestjet = getClosestBJetindex( event, lepton, minBtagValue )
    combination = closestjet + lepton
    event.mlb = combination.M()
sequence.append( getMlb )

def getCosThetaStar(sample, event):
    lepton = ROOT.TLorentzVector()
    Z = ROOT.TLorentzVector()
    Z.SetPtEtaPhiM(event.Z1_pt, event.Z1_eta, event.Z1_phi, event.Z1_mass)
    idx_l1 = event.Z1_l1_index
    idx_l2 = event.Z1_l2_index
    if idx_l1 >= 0 and idx_l2 >=0:
        if abs(event.lep_pdgId[idx_l1]) == 11:
            lepmass = 0.0005
        elif abs(event.lep_pdgId[idx_l1]) == 13:
            lepmass = 0.1
        elif abs(event.lep_pdgId[idx_l1]) == 15:
            lepmass = 1.777
        else:
            print "Z does not decay into leptons"
            lepmass = 0

        charge_l1 = event.lep_pdgId[idx_l1]/abs(event.lep_pdgId[idx_l1])
        charge_l2 = event.lep_pdgId[idx_l2]/abs(event.lep_pdgId[idx_l2])
        if charge_l1 < 0 and charge_l2 > 0:
            lepton.SetPtEtaPhiM(event.lep_pt[idx_l1], event.lep_eta[idx_l1], event.lep_phi[idx_l1], lepmass)
        else:
            lepton.SetPtEtaPhiM(event.lep_pt[idx_l2], event.lep_eta[idx_l2], event.lep_phi[idx_l2], lepmass)

        event.cosThetaStar = cosThetaStarNew(lepton, Z)
    else:
        event.cosThetaStar = float('nan')
sequence.append( getCosThetaStar )
#
# def getDiBosonAngles(sample, event):
#     lep1,lep2,boson = ROOT.TLorentzVector(),ROOT.TLorentzVector(),ROOT.TLorentzVector()
#     # Get lep1 and lep2 from Z boson
#     idx_l1 = event.Z1_l1_index
#     idx_l2 = event.Z1_l2_index
#     if idx_l1 >= 0 and idx_l2 >=0:
#         if abs(event.lep_pdgId[idx_l1]) == 11:
#             lepmass = 0.0005
#         elif abs(event.lep_pdgId[idx_l1]) == 13:
#             lepmass = 0.1
#         elif abs(event.lep_pdgId[idx_l1]) == 15:
#             lepmass = 1.777
#         else:
#             print "Z does not decay into leptons"
#             lepmass = 0
#         lep1.SetPtEtaPhiM(event.lep_pt[idx_l1], event.lep_eta[idx_l1], event.lep_phi[idx_l1], lepmass)
#         lep2.SetPtEtaPhiM(event.lep_pt[idx_l2], event.lep_eta[idx_l2], event.lep_phi[idx_l2], lepmass)
#
#     # For 2nd boson distinguish between cases
#     if "qualep" in args.selection:
#         boson.SetPtEtaPhiM(event.Z2_pt, event.Z2_eta, event.Z2_phi, event.Z2_mass)
#     elif "deepjet0" in args.selection:
#         Wleps = getWlep(event)
#         if len(Wleps) == 1:
#             boson = Wleps[0][0]
#         elif len(Wleps) == 2:
#             boson = Wleps[0][0] if Wleps[0][0].Pt()>Wleps[1][0].Pt() else Wleps[1][0]
#         else:
#             print "[ERROR] getWlep should not return more than 2 options"
#     else:
#         boson.SetPtEtaPhiM(0,0,0,0)
#
#     if idx_l1 >= 0 and idx_l2 >=0:
#         event.Theta = getTheta(lep1, lep2, boson)
#         event.theta = gettheta(lep1, lep2, boson)
#         event.phi = getphi(lep1, lep2, boson)
#     else:
#         event.Theta = float('nan')
#         event.theta = float('nan')
#         event.phi = float('nan')
# sequence.append( getDiBosonAngles )

def getbScoresLepton(sample, event):
    fakelepton_btagscores = []
    if event.l1_mvaTOPv2WP < 4:
        fakelepton_btagscores.append(event.lep_jetBTag[event.l1_index])
    if event.l2_mvaTOPv2WP < 4:
        fakelepton_btagscores.append(event.lep_jetBTag[event.l2_index])
    if event.l3_mvaTOPv2WP < 4:
        fakelepton_btagscores.append(event.lep_jetBTag[event.l3_index])
    event.fakelepton_btagscores = fakelepton_btagscores
sequence.append(getbScoresLepton)

# def getZorigin(event, sample):
#     pdgIds = []
#     mothersFound = []
#     productionModeWZ = 0
#     if sample.name != "data":
#         for i in range(event.nGenPart):
#             if i == 2 and abs(event.GenPart_pdgId[i])==24:
#                 productionModeWZ=1
#             if event.GenPart_pdgId[i] == 23:
#                 i_mother = event.GenPart_genPartIdxMother[i]
#                 Id_mother = event.GenPart_pdgId[i_mother]
#                 # If mother is still a Z, go further back until pdgId != 23
#                 if Id_mother == 23:
#                     foundMother = False
#                     while not foundMother:
#                         i_tmp = i_mother
#                         i_mother = event.GenPart_genPartIdxMother[i_tmp]
#                         Id_mother = event.GenPart_pdgId[i_mother]
#                         if Id_mother != 23:
#                             foundMother = True
#                 if i_mother not in mothersFound:
#                     pdgIds.append(Id_mother)
#                     mothersFound.append(i_mother)
#     event.MotherIds = pdgIds
#     event.Nmothers = len(pdgIds)
#     event.productionModeWZ = productionModeWZ
#     MotherList = []
#     # 0 = other
#     # 1,2,3 = 1st, 2nd, 3rd Generation Quarks
#     # 4 = W/Z/Higgs, 5 = Gluon, 6 = Lepton
#     for id in pdgIds:
#         if abs(id)==1 or abs(id)==2: # 1st gen
#             MotherList.append(1)
#         elif abs(id)==3 or abs(id)==4: # 2nd gen
#             MotherList.append(2)
#         elif abs(id)==5 or abs(id)==6: #3rd gen
#             MotherList.append(3)
#         elif abs(id)>=11 and abs(id)<=16: # lepton
#             MotherList.append(6)
#         elif abs(id)==9 or abs(id)==21: # gluon
#             MotherList.append(5)
#         elif abs(id)>=22 and abs(id)<=25: # W/Z/H
#             MotherList.append(4)
#         else:
#             MotherList.append(0)
#     event.MotherIdList = MotherList
#
#     production = -1
#     if sample.name != "data":
#         ID1 = abs(event.GenPart_pdgId[0])
#         ID2 = abs(event.GenPart_pdgId[1])
#         if   ID1 in [1,2] and ID2 in [1,2]: production = 1
#         elif ID1 in [3,4] and ID2 in [3,4]: production = 2
#         elif ID1 in [5,6] and ID2 in [5,6]: production = 3
#         elif (ID1==21 and ID2 in [1,2]) or (ID2==21 and ID1 in [1,2]): production = 4
#         elif (ID1==21 and ID2 in [3,4]) or (ID2==21 and ID1 in [3,4]): production = 5
#         elif (ID1==21 and ID2 in [5,6]) or (ID2==21 and ID1 in [5,6]): production = 6
#         elif ID1==21 and ID2==21: production = 7
#         else: production = 0
#     event.productionMode = production
# sequence.append(getZorigin)

def getM3l( event, sample ):
    l = []
    for i in range(3):
        l.append(ROOT.TLorentzVector())
        l[i].SetPtEtaPhiM(event.lep_pt[i], event.lep_eta[i], event.lep_phi[i],0)
    event.m3l = (l[0] + l[1] + l[2]).M()
sequence.append( getM3l )


def getTTbarReco( event, sample ):
    event.mtophad = float('nan')
    event.mtoplep = float('nan')
    event.minimax = float('nan')
    event.chi2 = float('nan')

    if args.doTTbarReco and event.nJetGood>=4:
        lepton = ROOT.TLorentzVector()
        met    = ROOT.TLorentzVector()
        lepton.SetPtEtaPhiM(event.lep_pt[event.nonZ1_l1_index], event.lep_eta[event.nonZ1_l1_index], event.lep_phi[event.nonZ1_l1_index], 0)
        met.SetPtEtaPhiM(event.met_pt, 0, event.met_phi, 0)
        jets = []
        Njetsmax = 6
        if event.nJetGood < Njetsmax:
            Njetsmax = event.nJetGood
        for i in range(Njetsmax):
            jet = ROOT.TLorentzVector()
            jetidx = event.JetGood_index[i]
            jet.SetPtEtaPhiM(event.Jet_pt[jetidx], event.Jet_eta[jetidx], event.Jet_phi[jetidx], event.Jet_mass[jetidx])
            jets.append(jet)
        reco = ttbarReco(lepton, met, jets)
        reco.reconstruct()
        best_hypothesis = reco.best_hypothesis
        minimax = reco.minimax
        if best_hypothesis:
            event.mtophad = best_hypothesis['toplep'].M()
            event.mtoplep = best_hypothesis['tophad'].M()
            event.chi2 = best_hypothesis['chi2']
        if minimax:
            event.minimax = minimax
sequence.append( getTTbarReco )

def Nlep( event, sample ):
    Nlep_tight = 0
    if event.l1_mvaTOPv2WP >= 4: Nlep_tight+=1
    if event.l2_mvaTOPv2WP >= 4: Nlep_tight+=1
    if event.l3_mvaTOPv2WP >= 4: Nlep_tight+=1
    if event.l4_mvaTOPv2WP >= 4: Nlep_tight+=1
    event.Nlep_tight = Nlep_tight
sequence.append( Nlep )

def getJetId( event, sample ):
    jetIds = []
    for i in range(event.nJetGood):
        jetIds.append(event.JetGood_jetId[i])
    event.jetIds = jetIds
sequence.append(getJetId)

################################################################################
# Read variables

read_variables = [
    "weight/F", "year/I", "preVFP/O", "met_pt/F", "met_phi/F", "nJetGood/I", "PV_npvsGood/I",  "nJet/I", "nBTag/I",
    "l1_pt/F", "l1_eta/F" , "l1_phi/F", "l1_mvaTOP/F", "l1_mvaTOPv2/F", "l1_mvaTOPWP/I", "l1_mvaTOPv2WP/I", "l1_index/I",
    "l2_pt/F", "l2_eta/F" , "l2_phi/F", "l2_mvaTOP/F", "l2_mvaTOPv2/F", "l2_mvaTOPWP/I", "l2_mvaTOPv2WP/I", "l2_index/I",
    "l3_pt/F", "l3_eta/F" , "l3_phi/F", "l3_mvaTOP/F", "l3_mvaTOPv2/F", "l3_mvaTOPWP/I", "l3_mvaTOPv2WP/I", "l3_index/I",
    "l4_pt/F", "l4_eta/F" , "l4_phi/F", "l4_mvaTOP/F", "l4_mvaTOPv2/F", "l4_mvaTOPWP/I", "l4_mvaTOPv2WP/I", "l4_index/I",
    "JetGood[pt/F,eta/F,phi/F,area/F,btagDeepB/F,btagDeepFlavB/F,index/I,jetId/I]",
    "Jet[pt/F,eta/F,phi/F,mass/F,btagDeepFlavB/F,jetId/I]",
    "lep[pt/F,eta/F,phi/F,pdgId/I,muIndex/I,eleIndex/I,mediumId/O,ptCone/F,mvaTOPv2WP/I,jetBTag/F,sip3d/F,pfRelIso03_all/F]",
    "Z1_l1_index/I", "Z1_l2_index/I", "nonZ1_l1_index/I", "nonZ1_l2_index/I",
    "Z1_phi/F", "Z1_pt/F", "Z1_mass/F", "Z1_cosThetaStar/F", "Z1_eta/F", "Z1_lldPhi/F", "Z1_lldR/F",
    "Muon[pt/F,eta/F,phi/F,dxy/F,dz/F,ip3d/F,sip3d/F,jetRelIso/F,miniPFRelIso_all/F,pfRelIso03_all/F,mvaTTH/F,pdgId/I,segmentComp/F,nStations/I,nTrackerLayers/I,mediumId/O,tightId/O,isPFcand/B,isTracker/B,isGlobal/B]",
    "Electron[pt/F,eta/F,phi/F,dxy/F,dz/F,ip3d/F,sip3d/F,jetRelIso/F,miniPFRelIso_all/F,pfRelIso03_all/F,mvaTTH/F,pdgId/I,vidNestedWPBitmap/I,deltaEtaSC/F,convVeto/O,lostHits/b]",
]

if "qualep" in args.selection:
    read_variables.append("Z2_phi/F")
    read_variables.append("Z2_pt/F")
    read_variables.append("Z2_eta/F")
    read_variables.append("Z2_mass/F")

read_variables_MC = [
    "weight/F", 'reweightBTag_SF/F', 'reweightPU/F', 'reweightL1Prefire/F', 'reweightTrigger/F',
    "genZ1_pt/F", "genZ1_eta/F", "genZ1_phi/F",
    "Muon[genPartFlav/I]",
    VectorTreeVariable.fromString( "GenPart[pt/F,mass/F,phi/F,eta/F,pdgId/I,genPartIdxMother/I,status/I,statusFlags/I]", nMax=1000),
    'nGenPart/I',
    'nScale/I', 'Scale[Weight/F]',
    'nPDF/I', VectorTreeVariable.fromString('PDF[Weight/F]',nMax=150),
]

read_variables_eft = [
    "np/I", VectorTreeVariable.fromString("p[C/F]",nMax=200)
]


################################################################################
# MVA

################################################################################
# define 3l selections
if "lepVeto" in args.selection:
    mu_string  = lepString('mu','VL')
else:
    mu_string  = lepString('mu','L') + "&&lep_mediumId"

ele_string = lepString('ele','L')

# print mu_string
# print ele_string
def getLeptonSelection( mode ):
    if   mode=="mumumu":   return "Sum$({mu_string})==3&&Sum$({ele_string})==0".format(mu_string=mu_string,ele_string=ele_string)
    elif mode=="mumue":    return "Sum$({mu_string})==2&&Sum$({ele_string})==1".format(mu_string=mu_string,ele_string=ele_string)
    elif mode=="muee":     return "Sum$({mu_string})==1&&Sum$({ele_string})==2".format(mu_string=mu_string,ele_string=ele_string)
    elif mode=="eee":      return "Sum$({mu_string})==0&&Sum$({ele_string})==3".format(mu_string=mu_string,ele_string=ele_string)
    elif mode=="mumumumu": return "Sum$({mu_string})==4&&Sum$({ele_string})==0".format(mu_string=mu_string,ele_string=ele_string)
    elif mode=="mumuee":   return "Sum$({mu_string})==2&&Sum$({ele_string})==2".format(mu_string=mu_string,ele_string=ele_string)
    elif mode=="eeee":     return "Sum$({mu_string})==0&&Sum$({ele_string})==4".format(mu_string=mu_string,ele_string=ele_string)

################################################################################
# Set up channels and values for plotting
yields     = {}
allPlots   = {}
allPlots_SM= {}
allModes   = ['mumumu', 'mumue', 'muee', 'eee']
if 'qualep' in args.selection:
    allModes = ['mumumumu','mumuee','eeee']

print "Working on channels:", allModes

for i_mode, mode in enumerate(allModes):
    yields[mode] = {}
    if not args.noData:
        data_sample.texName = "data"
        data_sample.setSelectionString([getLeptonSelection(mode)])
        data_sample.name           = "data"
        data_sample.style          = styles.errorStyle(ROOT.kBlack)

    for sample in mc: sample.style = styles.fillStyle(sample.color)

    ###### SYS #################################################################
    if args.sys in jet_variations:
        new_variables = ['%s/F'%v for v in jetSelectionModifier(jet_variations[args.sys],'list')]
        read_variables_MC += new_variables
        read_variables    += new_variables

    weightnames = ['weight', 'reweightBTag_SF', 'reweightPU', 'reweightL1Prefire' , 'reweightTrigger', 'reweightLeptonFakerate'] # 'reweightLeptonMVA'
    # weightnames = ['weight']
    sys_weights = {
        "BTag_b_UP"     : ('reweightBTag_SF','reweightBTag_SF_b_Up'),
        "BTag_b_DOWN"   : ('reweightBTag_SF','reweightBTag_SF_b_Down'),
        "BTag_l_UP"     : ('reweightBTag_SF','reweightBTag_SF_l_Up'),
        "BTag_l_DOWN"   : ('reweightBTag_SF','reweightBTag_SF_l_Down'),
        'Trigger_UP'    : ('reweightTrigger','reweightTriggerUp'),
        'Trigger_DOWN'  : ('reweightTrigger','reweightTriggerDown'),
        'PU_UP'         : ('reweightPU','reweightPUUp'),
        'PU_DOWN'       : ('reweightPU','reweightPUDown'),
        # For lepton SF this is set in the sequence
    }

    if args.sys in sys_weights:
        oldname, newname = sys_weights[args.sys]
        for i, weight in enumerate(weightnames):
            if weight == oldname:
                weightnames[i] = newname
                read_variables_MC += ['%s/F'%(newname)]

    getters = map( operator.attrgetter, weightnames)
    def weight_function( event, sample):
        # Calculate weight, this becomes: w = event.weightnames[0]*event.weightnames[1]*...
        w = reduce(operator.mul, [g(event) for g in getters], 1)
        # Get Lumi weight and multiply to weight
        yearstring = ""
        if event.year == 2016 and not event.preVFP:
            yearstring = "2016"
        elif event.year == 2016 and event.preVFP:
            yearstring = "2016_preVFP"
        elif event.year == 2017:
            yearstring = "2017"
        elif event.year == 2018:
            yearstring = "2018"
        lumi_weight = lumi_year[yearstring]/1000.
        w *= lumi_weight
        # Multiply Scale weight
        if "Scale_" in args.sys:
            scale_weight = getScaleWeight(event, args.sys)
            w *= scale_weight
        return w


    for sample in mc:
        sample.read_variables = read_variables_MC
        sample.setSelectionString([getLeptonSelection(mode)])
        sample.weight = weight_function

    for param in params:
        param['sample'].read_variables = read_variables_MC + read_variables_eft
        param['sample'].setSelectionString([getLeptonSelection(mode)])
        param['sample'].weight = weight_function

    if not args.noData:
        stack = Stack(mc, data_sample, *[ [ param['sample'] ] for param in params ])
        noneftidxs = [0,1]
        if args.nicePlots:
            stack = Stack(mc, data_sample)
    else:
        stack = Stack(mc, *[ [ param['sample'] ] for param in params ])
        noneftidxs = [0]
        if args.nicePlots:
            stack = Stack(mc)

    # Use some defaults
    selection_string = selectionModifier(cutInterpreter.cutString(args.selection)) if selectionModifier is not None else cutInterpreter.cutString(args.selection)
    if args.mvaTOPv1:
        selection_string = selection_string.replace("mvaTOPv2", "mvaTOP")
    Plot.setDefaults(stack = stack, weight = plotweights, selectionString = selection_string)

    ################################################################################
    # Now define the plots

    plots = []

    plots.append(Plot(
      name = 'yield', texX = '', texY = 'Number of Events',
      attribute = lambda event, sample: 0.5 + i_mode,
      binning=[4, 0, 4],
    ))

    plots.append(Plot(
        name = "Z1_pt",
        texX = 'p_{T}(Z_{1}) (GeV)', texY = 'Number of Events / 20 GeV',
        attribute = TreeVariable.fromString( "Z1_pt/F" ),
        binning=[50, 0, 1000],
    ))

    plots.append(Plot(
        name = "M3l",
        texX = 'M(3l) (GeV)', texY = 'Number of Events',
        attribute = lambda event, sample:event.m3l,
        binning=[25,0,500],
    ))

    plots.append(Plot(
        name = "N_LepID",
        texX = 'Number of leptons passing the tight ID', texY = 'Number of Events',
        attribute = lambda event, sample: event.Nlep_tight,
        binning=[5,-0.5,4.5],
    ))

    plots.append(Plot(
        name = "l1_pt",
        texX = 'Leading lepton p_{T} (GeV)', texY = 'Number of Events / 10 GeV',
        addOverFlowBin='both',
        attribute = TreeVariable.fromString( "l1_pt/F" ),
        binning=[40, 0, 400],
    ))

    plots.append(Plot(
        name = "l2_pt",
        texX = 'Subleading lepton p_{T} (GeV)', texY = 'Number of Events / 10 GeV',
        addOverFlowBin='both',
        attribute = TreeVariable.fromString( "l2_pt/F" ),
        binning=[40, 0, 400],
    ))

    plots.append(Plot(
        name = "l3_pt",
        texX = 'Trailing lepton p_{T} (GeV)', texY = 'Number of Events / 10 GeV',
        addOverFlowBin='both',
        attribute = TreeVariable.fromString( "l3_pt/F" ),
        binning=[40, 0, 400],
    ))


    plots.append(Plot(
        name = "fake_bscore_closest",
        texX = 'b tag score closest jet for fake leptons', texY = 'Number of Events',
        attribute = lambda event, sample: event.fakelepton_btagscores,
        binning=[40, 0, 1.0],
    ))


    if args.doTTbarReco:
        plots.append(Plot(
            name = "minimax",
            texX = 'minimax', texY = 'Number of Events',
            attribute = lambda event, sample: event.minimax,
            binning=[40,0,600],
            addOverFlowBin='upper',
        ))

    if args.nicePlots:

        plots.append(Plot(
            name = "Z1_pt_rebin2",
            texX = 'p_{T}(Z_{1}) (GeV)', texY = 'Number of Events / 40 GeV',
            attribute = TreeVariable.fromString( "Z1_pt/F" ),
            binning=[25, 0, 1000],
        ))

        plots.append(Plot(
            name = "Z1_pt_rebin5",
            texX = 'p_{T}(Z_{1}) (GeV)', texY = 'Number of Events / 100 GeV',
            attribute = TreeVariable.fromString( "Z1_pt/F" ),
            binning=[10, 0, 1000],
        ))

        plots.append(Plot(
            name = "M_lb",
            texX = 'm_{lb} (GeV)', texY = 'Number of Events / 20 GeV',
            attribute = lambda event, sample: event.mlb,
            binning=[20, 0, 400],
        ))

        plots.append(Plot(
            name = "N_jets",
            texX = 'Number of jets', texY = 'Number of Events',
            attribute = lambda event, sample: event.nJetGood,
            binning=[16, -0.5, 15.5],
        ))

        plots.append(Plot(
            name = "JetIds",
            texX = 'Jet ID', texY = 'Number of Events',
            attribute = lambda event, sample: event.jetIds,
            binning=[10, -1.5, 8.5],
        ))

        plots.append(Plot(
            name = "N_bjets",
            texX = 'Number of b-tagged jets', texY = 'Number of Events',
            attribute = lambda event, sample: event.nBTag,
            binning=[16, -0.5, 15.5],
        ))


        plots.append(Plot(
            name = "CosThetaStar",
            texX = 'cos #theta*', texY = 'Number of Events',
            attribute = lambda event, sample: event.cosThetaStar,
            binning=[20, -1, 1],
        ))

        plots.append(Plot(
            name = "CosThetaStar_old",
            texX = 'cos #theta*', texY = 'Number of Events',
            attribute = lambda event, sample: event.Z1_cosThetaStar,
            binning=[20, -1, 1],
        ))

        plots.append(Plot(
            name = "theta",
            texX = '#theta', texY = 'Number of Events',
            attribute = lambda event, sample: event.theta,
            binning=[20, 0, pi],
        ))

        plots.append(Plot(
            name = "Theta",
            texX = '#Theta', texY = 'Number of Events',
            attribute = lambda event, sample: event.Theta,
            binning=[20, 0, pi],
        ))

        plots.append(Plot(
            name = "phi",
            texX = '#phi', texY = 'Number of Events',
            attribute = lambda event, sample: event.phi,
            binning=[20, -pi, pi],
        ))

        plots.append(Plot(
            name = "SF_Lepton",
            texX = 'Lepton SF', texY = 'Number of Events',
            attribute = lambda event, sample: event.reweightLeptonMVA if not sample.isData else -1,
            addOverFlowBin='both',
            binning=[50, 0.5, 1.5],
        ))

        plots.append(Plot(
            name = "SF_Fakerate",
            texX = 'Fakerate SF', texY = 'Number of Events',
            attribute = lambda event, sample: event.reweightLeptonFakerate if not sample.isData else -1,
            addOverFlowBin='both',
            binning=[100, -1.0, 1.0],
        ))

        plots.append(Plot(
            name = "SF_Btag",
            texX = 'b tagging SF', texY = 'Number of Events',
            attribute = lambda event, sample: event.reweightBTag_SF if not sample.isData else -1,
            addOverFlowBin='both',
            binning=[50, 0.5, 1.5],
        ))

        plots.append(Plot(
            name = "SF_PU",
            texX = 'PU SF', texY = 'Number of Events',
            attribute = lambda event, sample: event.reweightPU if not sample.isData else -1,
            addOverFlowBin='both',
            binning=[50, 0.5, 1.5],
        ))

        plots.append(Plot(
            name = "SF_L1",
            texX = 'L1 prefire SF', texY = 'Number of Events',
            attribute = lambda event, sample: event.reweightL1Prefire if not sample.isData else -1,
            addOverFlowBin='both',
            binning=[50, 0.5, 1.5],
        ))

        plots.append(Plot(
            name = "SF_Trigger",
            texX = 'Trigger SF', texY = 'Number of Events',
            attribute = lambda event, sample: event.reweightTrigger if not sample.isData else -1,
            addOverFlowBin='both',
            binning=[50, 0.5, 1.5],
        ))

        plots.append(Plot(
            name = "l1_mvaTOPscore",
            texX = 'Leading lepton MVA score', texY = 'Number of Events',
            attribute = lambda event, sample: event.l1_mvaTOP,
            binning=[30, -1.5, 1.5],
        ))

        plots.append(Plot(
            name = "l1_mvaTOPscore_v2",
            texX = 'Leading lepton MVA v2 score', texY = 'Number of Events',
            attribute = lambda event, sample: event.l1_mvaTOPv2,
            binning=[30, -1.5, 1.5],
        ))

        plots.append(Plot(
            name = "l2_mvaTOPscore_v2",
            texX = 'Subleading lepton MVA v2 score', texY = 'Number of Events',
            attribute = lambda event, sample: event.l2_mvaTOPv2,
            binning=[30, -1.5, 1.5],
        ))

        plots.append(Plot(
            name = "l3_mvaTOPscore_v2",
            texX = 'Trailing lepton MVA v2 score', texY = 'Number of Events',
            attribute = lambda event, sample: event.l3_mvaTOPv2,
            binning=[30, -1.5, 1.5],
        ))

        if args.doTTbarReco:
            plots.append(Plot(
                name = "m_toplep",
                texX = 'm_{lep. top}', texY = 'Number of Events',
                attribute = lambda event, sample: event.mtoplep,
                binning=[40,0,400],
                addOverFlowBin='upper',
            ))

            plots.append(Plot(
                name = "m_tophad",
                texX = 'm_{had. top}', texY = 'Number of Events',
                attribute = lambda event, sample: event.mtophad,
                binning=[40,0,400],
                addOverFlowBin='upper',
            ))

            plots.append(Plot(
                name = "chi2",
                texX = '#chi^{2}', texY = 'Number of Events',
                attribute = lambda event, sample: event.chi2,
                binning=[40,0,1000],
                addOverFlowBin='upper',
            ))

    plotting.fill(plots, read_variables = read_variables, sequence = sequence)


    ################################################################################
    # Get normalization yields from yield histogram
    for plot in plots:
        if plot.name == "Z_mother_grouped":
            for i, l in enumerate(plot.histos):
                for j, h in enumerate(l):
                    h.GetXaxis().SetBinLabel(1, "other")
                    h.GetXaxis().SetBinLabel(2, "1st")
                    h.GetXaxis().SetBinLabel(3, "2nd")
                    h.GetXaxis().SetBinLabel(4, "3rd")
                    h.GetXaxis().SetBinLabel(5, "W/Z/H")
                    h.GetXaxis().SetBinLabel(6, "gluon")
                    h.GetXaxis().SetBinLabel(7, "lepton")
        if plot.name == "ProductionMode":
            for i, l in enumerate(plot.histos):
                for j, h in enumerate(l):
                    h.GetXaxis().SetBinLabel(1, "other")
                    h.GetXaxis().SetBinLabel(2, "1st")
                    h.GetXaxis().SetBinLabel(3, "2nd")
                    h.GetXaxis().SetBinLabel(4, "3rd")
                    h.GetXaxis().SetBinLabel(5, "1st+g")
                    h.GetXaxis().SetBinLabel(6, "2nd+g")
                    h.GetXaxis().SetBinLabel(7, "3rd+g")
                    h.GetXaxis().SetBinLabel(8, "g+g")
        if plot.name == "ProductionModeWZ":
            for i, l in enumerate(plot.histos):
                for j, h in enumerate(l):
                    h.GetXaxis().SetBinLabel(1, "t channel")
                    h.GetXaxis().SetBinLabel(2, "s channel")
        if plot.name == "yield":
            for i, l in enumerate(plot.histos):
                for j, h in enumerate(l):
                    yields[mode][plot.stack[i][j].name] = h.GetBinContent(h.FindBin(0.5+i_mode))
                    if 'qualep' in args.selection:
                        h.GetXaxis().SetBinLabel(1, "#mu#mu#mu#mu")
                        h.GetXaxis().SetBinLabel(2, "#mu#muee")
                        h.GetXaxis().SetBinLabel(3, "eeee")
                    else:
                        h.GetXaxis().SetBinLabel(1, "#mu#mu#mu")
                        h.GetXaxis().SetBinLabel(2, "#mu#mue")
                        h.GetXaxis().SetBinLabel(3, "#muee")
                        h.GetXaxis().SetBinLabel(4, "eee")

    if args.noData: yields[mode]["data"] = 0

    yields[mode]["MC"] = sum(yields[mode][s.name] for s in mc)
    dataMCScale        = yields[mode]["data"]/yields[mode]["MC"] if yields[mode]["MC"] != 0 else float('nan')


    if args.nicePlots: drawPlots(plots, mode, dataMCScale)

    allPlots[mode] = plots


################################################################################
# Add all different channels
yields["all"] = {}
for y in yields[allModes[0]]:
    try:    yields["all"][y] = sum(yields[c][y] for c in allModes)
    except: yields["all"][y] = 0
dataMCScale = yields["all"]["data"]/yields["all"]["MC"] if yields["all"]["MC"] != 0 else float('nan')

allPlots["all"] = allPlots[allModes[0]]
for plot in allPlots['all']:
    for i_mode,mode in enumerate(allModes):
        if i_mode == 0:
            continue
        tmp = allPlots[mode]
        for plot2 in (p for p in tmp if p.name == plot.name):
            for i, j in enumerate(list(itertools.chain.from_iterable(plot.histos))):
                for k, l in enumerate(list(itertools.chain.from_iterable(plot2.histos))):
                    if i==k:
                        j.Add(l)


if args.nicePlots:
    drawPlots(allPlots['all'], "all", dataMCScale)

plots_root = ["Z1_pt", "M3l", "l1_pt", "l2_pt", "l3_pt", "N_jets"]

# Write Result Hist in root file
print "Now write results in root file."
plot_dir = os.path.join(plot_directory, 'analysisPlots', args.plot_directory, args.era, "all", args.selection)
if not os.path.exists(plot_dir):
    try:
        os.makedirs(plot_dir)
    except:
        print 'Could not create', plot_dir
outfilename = plot_dir+'/Results.root'
# if args.twoD:
#     outfilename = plot_dir+'/Results_twoD.root'
#     if args.triplet:
#         outfilename = plot_dir+'/Results_twoD_triplet.root'
print "Saving in", outfilename
outfile = ROOT.TFile(outfilename, 'recreate')
outfile.cd()
for plot in allPlots['all']:
    if plot.name in plots_root:
        for idx, histo_list in enumerate(plot.histos):
            for j, h in enumerate(histo_list):
                histname = h.GetName()
                process = "TTLep_bb"
                if "TTLep_bb" in histname: process = "TTLep_bb"
                elif "TTLep_cc" in histname: process = "TTLep_cc"
                elif "TTLep_other" in histname: process = "TTLep_other"
                elif "ST" in histname: process = "ST"
                elif "TTTT" in histname: process = "TTTT"
                elif "TTW" in histname: process = "TTW"
                elif "TTZ" in histname: process = "TTZ"
                elif "TTH" in histname: process = "TTH"
                elif "data" in histname: process = "data"
                # Also add a string for the eft signal samples
                n_noneft = len(noneftidxs)
                if not args.nicePlots and idx not in noneftidxs:
                    h.Write(plot.name+"__"+process+"__"+params[idx-n_noneft]['legendText'])
                else:
                    h.Write(plot.name+"__"+process)

                    # if args.twoD:
                    #     string = params[idx-n_noneft]['legendText']
                    #     if string.count('=0.0000') == 2:
                    #         h_SM = h.Clone()
                    #         h_SM.Write(plot.name+"__"+process)
                    # else:
                    #     if "=0.0000" in params[idx-n_noneft]['legendText']:
                    #         h_SM = h.Clone()
                    #         h_SM.Write(plot.name+"__"+process)

outfile.Close()



logger.info( "Done with prefix %s and selectionString %s", args.selection, selection_string )
