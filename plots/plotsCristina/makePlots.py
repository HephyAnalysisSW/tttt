#!/usr/bin/env python
''' Analysis script for Stacked Plots
'''

#----------------- Standard imports and batch mode

import ROOT, os
import itertools
import copy
import array
import operator
from   math                              import sqrt, cos, sin, pi, atan2, cosh

#----------------- RootTools import

from RootTools.core.standard             import *

#----------------- tttt tools import

from tttt.Tools.user                     import plot_directory
from tttt.Tools.cutInterpreter           import cutInterpreter
from tttt.Tools.objectSelection          import lepString, isBJet
#   Attenzione che ho cambiato la dependency da TMB a tttt per isBJet,
#   dovrebbe essere lo stesso ma e da controllare meglio

#----------------- TMB tools
#ACHTUNG dependencies need to be changed
from TMB.Tools.helpers import getObjDict

#---------------- Analysis

from Analysis.Tools.helpers              import deltaPhi, deltaR
from Analysis.Tools.puProfileCache       import *
from Analysis.Tools.puReweighting        import getReweightingFunction
import Analysis.Tools.syncer
import numpy as np


#---------------- Slimming attempt n.1
#from var_config import fetch_variables_jets

#---------------- Parser (customizable)

import argparse
parser = argparse.ArgumentParser(description = "Argument parser")
parser.add_argument('--logLevel',       action='store',      default='INFO', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
parser.add_argument('--small',                             action='store_true', help='Run only on a small subset of the data?', )
parser.add_argument('--sorting',                           action='store', default=None, choices=[None, "forDYMB"],  help='Sort histos?', )
parser.add_argument('--dataMCScaling',  action='store_true', help='Data MC scaling?', )
parser.add_argument('--plot_directory', action='store', default='TMB_4t')
parser.add_argument('--selection',      action='store', default='dilepL-offZ1-njet4p-btag2p-ht500')
#parser.add_argument('--lepton',     action='store', default= 'None', type=str, choices=['2mu', '2e', '1mu1e', 'SF', 'all'], help='plot lepton categories')
args = parser.parse_args()


#---------------- Logger
#ACHTUNG add logger in tttt BUT before check for dependencies
import tttt.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

if args.small:args.plot_directory += "_small"

#---------------- Import Samples
#ACHTUNG dependencies to be changes
from TMB.Samples.nanoTuples_RunII_nanoAODv6_dilep_pp_Attempt import *

# sample_TTLep = TTLep
# # ttbar gen classification: https://github.com/cms-top/cmssw/blob/topNanoV6_from-CMSSW_10_2_18/TopQuarkAnalysis/TopTools/plugins/GenTtbarCategorizer.cc
# TTLep_bb    = copy.deepcopy( sample_TTLep )
# TTLep_bb.name = "TTLep_bb"
# TTLep_bb.texName = "t#bar{t}b#bar{b}"
# TTLep_bb.color   = ROOT.kRed + 2
# TTLep_bb.setSelectionString( "genTtbarId%100>=50" )
# TTLep_cc    = copy.deepcopy( sample_TTLep )
# TTLep_cc.name = "TTLep_cc"
# TTLep_cc.texName = "t#bar{t}c#bar{c}"
# TTLep_cc.color   = ROOT.kRed - 3
# TTLep_cc.setSelectionString( "genTtbarId%100>=40&&genTtbarId%100<50" )
# TTLep_other = copy.deepcopy( sample_TTLep )
# TTLep_other.name = "TTLep_other"
# TTLep_other.texName = "t#bar{t} + light j."
# TTLep_other.setSelectionString( "genTtbarId%100<40" )




mc = [ TTLep_bb,TTLep_cc,TTLep_other, TTW, TTH, TTZ]

all = mc + [TTTT]


#---------------- Luminosity factor

lumi_scale = 350#sum(lumi_year.values())/1000.


#---------------- Normalizations

for sample in all:
    sample.scale           = 1

if args.small:
    for sample in all:
        sample.normalization = 1.
        sample.reduceFiles( to = 1 )
        sample.scale /= sample.normalization

#--------------- Text on the plots

#tex = ROOT.TLatex()
#tex.SetNDC()
#tex.SetTextSize(0.04)
#tex.SetTextAlign(11) # align right

def drawObjects( dataMCScale, lumi_scale ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11)
    lines = [
      (0.15, 0.95, 'CMS Simulation'),
      (0.45, 0.95, 'L=%3.1f fb{}^{-1} (13 TeV)' % lumi_scale),
    ]
    return [tex.DrawLatex(*l) for l in lines]

def drawPlots(plots, mode, dataMCScale):
  for log in [False, True]:
    plot_directory_ = os.path.join(plot_directory, 'analysisPlots', args.plot_directory, 'RunIII', mode + ("_log" if log else ""), args.selection)
    for plot in plots:
      if not max(l.GetMaximum() for l in sum(plot.histos,[])): continue # Empty plot

      _drawObjects = []

      if isinstance( plot, Plot):
          plotting.draw(plot,
            plot_directory = plot_directory_,
            ratio = None,
            logX = False, logY = log, sorting = True,
            yRange = (0.9, "auto") if log else (0.001, "auto"),
            scaling = {0:1} if args.dataMCScaling else {},
            legend = ( (0.18,0.88-0.03*sum(map(len, plot.histos)),0.9,0.88), 2),
            drawObjects = drawObjects( dataMCScale , lumi_scale ) + _drawObjects,
            copyIndexPHP = True, extensions = ["png", "pdf", "root"],
          )

#---------------- Read variables and sequences

sequence       = []

jetVars          = ['pt/F',
                    'eta/F',
                    'phi/F',
                    'btagDeepB/F'
                    ]
jetVarNames      = [x.split('/')[0] for x in jetVars]
print(jetVarNames)
def make_jets( event, sample ):
    event.jets     = [getObjDict(event, 'JetGood_', jetVarNames, i) for i in range(int(event.nJetGood))]
    event.bJets    = filter(lambda j:isBJet(j, year=event.year) and abs(j['eta'])<=2.4    , event.jets)
sequence.append( make_jets )

#MVA
import TMB.MVA.configs as configs
config = configs.tttt_2l
read_variables = config.read_variables

# Add sequence that computes the MVA inputs
def make_mva_inputs( event, sample ):
    for mva_variable, func in config.mva_variables:
        setattr( event, mva_variable, func(event, sample) )
sequence.append( make_mva_inputs )

def getM3l( event, sample ):
    # get the invariant mass of the 3l system
    l = []
    for i in range(3):
        l.append(ROOT.TLorentzVector())
        l[i].SetPtEtaPhiM(event.lep_pt[i], event.lep_eta[i], event.lep_phi[i],0)
    event.M3l = (l[0] + l[1] + l[2]).M()

sequence.append( getM3l )

read_variables += [
    "weight/F", "year/I", "met_pt/F", "met_phi/F", "nBTag/I", "nJetGood/I", "PV_npvsGood/I",
    "l1_pt/F", "l1_eta/F" , "l1_phi/F", "l1_mvaTOP/F", "l1_mvaTOPWP/I", "l1_index/I",
    "l2_pt/F", "l2_eta/F" , "l2_phi/F", "l2_mvaTOP/F", "l2_mvaTOPWP/I", "l2_index/I",
    "JetGood[%s]"%(",".join(jetVars)),
    "lep[pt/F,eta/F,phi/F,pdgId/I,muIndex/I,eleIndex/I]",
    "Z1_l1_index/I", "Z1_l2_index/I", #"nonZ1_l1_index/I", "nonZ1_l2_index/I",
    "Z1_phi/F", "Z1_pt/F", "Z1_mass/F", "Z1_cosThetaStar/F", "Z1_eta/F", "Z1_lldPhi/F", "Z1_lldR/F",
    "Muon[pt/F,eta/F,phi/F,dxy/F,dz/F,ip3d/F,sip3d/F,jetRelIso/F,miniPFRelIso_all/F,pfRelIso03_all/F,mvaTOP/F,mvaTTH/F,pdgId/I,segmentComp/F,nStations/I,nTrackerLayers/I]",
    "Electron[pt/F,eta/F,phi/F,dxy/F,dz/F,ip3d/F,sip3d/F,jetRelIso/F,miniPFRelIso_all/F,pfRelIso03_all/F,mvaTOP/F,mvaTTH/F,pdgId/I,vidNestedWPBitmap/I]",
    "GenJet[pt/F,eta/F,phi/F,partonFlavour/I,hadronFlavour/i,nBHadFromT/I,nBHadFromTbar/I,nBHadFromW/I,nBHadOther/I,nCHadFromW/I,nCHadOther/I]"
]

read_variables_MC = ['reweightBTag_SF/F', 'reweightPU/F', 'reweightL1Prefire/F', 'reweightLeptonSF/F', 'reweightTrigger/F']
# define 3l selections

mu_string  = lepString('mu','VL')
ele_string = lepString('ele','VL')
def getLeptonSelection( mode ):
    if   mode=="mumu": return "Sum$({mu_string})==2&&Sum$({ele_string})==0".format(mu_string=mu_string,ele_string=ele_string)
    elif mode=="mue":  return "Sum$({mu_string})==1&&Sum$({ele_string})==1".format(mu_string=mu_string,ele_string=ele_string)
    elif mode=="ee":   return "Sum$({mu_string})==0&&Sum$({ele_string})==2".format(mu_string=mu_string,ele_string=ele_string)
    elif mode=='all':    return "Sum$({mu_string})+Sum$({ele_string})==2".format(mu_string=mu_string,ele_string=ele_string)

# Getter functor for lepton quantities
def lep_getter( branch, index, abs_pdg = None, functor = None, debug=False):
    if functor is not None:
        if abs_pdg == 13:
            def func_( event, sample ):
                if debug:
                    print "Returning", "Muon_%s"%branch, index, abs_pdg, "functor", functor, "result",
                    print functor(getattr( event, "Muon_%s"%branch )[event.lep_muIndex[index]]) if abs(event.lep_pdgId[index])==abs_pdg else float('nan')
                return functor(getattr( event, "Muon_%s"%branch )[event.lep_muIndex[index]]) if abs(event.lep_pdgId[index])==abs_pdg else float('nan')
        else:
            def func_( event, sample ):
                return functor(getattr( event, "Electron_%s"%branch )[event.lep_eleIndex[index]]) if abs(event.lep_pdgId[index])==abs_pdg else float('nan')
    else:
        if abs_pdg == 13:
            def func_( event, sample ):
                if debug:
                    print "Returning", "Muon_%s"%branch, index, abs_pdg, "functor", functor, "result",
                    print getattr( event, "Muon_%s"%branch )[event.lep_muIndex[index]] if abs(event.lep_pdgId[index])==abs_pdg else float('nan')
                return getattr( event, "Muon_%s"%branch )[event.lep_muIndex[index]] if abs(event.lep_pdgId[index])==abs_pdg else float('nan')
        else:
            def func_( event, sample ):
                return getattr( event, "Electron_%s"%branch )[event.lep_eleIndex[index]] if abs(event.lep_pdgId[index])==abs_pdg else float('nan')
    return func_
genJetSelection = "GenJet_pt>30&&abs(GenJet_eta)<2.4"

ttreeFormulas = {   "nGenJet_absHF5":"Sum$(abs(GenJet_hadronFlavour)==5&&{genJetSelection})".format(genJetSelection=genJetSelection),
                    "nGenJet_absPF5":"Sum$(abs(GenJet_partonFlavour)==5&&{genJetSelection})".format(genJetSelection=genJetSelection),
                    "nGenJet_min1BHadFromTorTbar":"Sum$(GenJet_nBHadFromT+GenJet_nBHadFromTbar>=1&&{genJetSelection})".format(genJetSelection=genJetSelection),
                    "nGenJet_min1BHadFromW":"Sum$(GenJet_nBHadFromW>=1&&{genJetSelection})".format(genJetSelection=genJetSelection),
                    "nGenJet_min1BHadOther":"Sum$(GenJet_nBHadOther>=1&&{genJetSelection})".format(genJetSelection=genJetSelection),
                    "nGenJet_min1CHadFromW":"Sum$(GenJet_nCHadFromW>=1&&{genJetSelection})".format(genJetSelection=genJetSelection),
                    "nGenJet_min1CHadOther":"Sum$(GenJet_nCHadOther>=1&&{genJetSelection})".format(genJetSelection=genJetSelection),
    }

yields     = {}
allPlots   = {}
allModes   = ['mumu','mue', 'ee']
for i_mode, mode in enumerate(allModes):
    yields[mode] = {}

    weight_ = lambda event, sample: event.weight if sample.isData else event.weight*lumi_scale

    for sample in mc: sample.style = styles.fillStyle(sample.color)
    TTTT.style = styles.lineStyle( ROOT.kBlack, width=2)

    for sample in all:
      sample.read_variables = read_variables_MC
      sample.weight = lambda event, sample: event.reweightBTag_SF*event.reweightPU*event.reweightL1Prefire*event.reweightTrigger#*event.reweightLeptonSF

    #yt_TWZ_filter.scale = lumi_scale * 1.07314

    stack = Stack(all, TTTT)

    # Use some defaults
    Plot.setDefaults(stack = stack, weight = staticmethod(weight_), selectionString = "("+getLeptonSelection(mode)+")&&("+cutInterpreter.cutString(args.selection)+")")

    plots = []


    # plots.append(Plot(
    #     name = 'nVtxs', texX = 'Vertex Multiplicity', texY = 'Number of Events',
    #     attribute = TreeVariable.fromString( "PV_npvsGood/I" ),
    #     binning=[50,0,50],
    #     addOverFlowBin='upper',
    # ))
    plots.append(Plot(
        name = 'yield', texX = '', texY = 'Number of Events',
        attribute = lambda event, sample: 0.5 + i_mode,
        binning=[3, 0, 3],
    ))

    plots.append(Plot(
        name = 'B_tag_discriminator', texX = '', texY = 'Number of Events',
        attribute = lambda event, sample: event.JetGood_btagDeepB[0],
        #attribute = TreeVariable.fromString( "JetGood_btagDeepB/F" ),
        binning=[10, 0, 1],
    ))


    #Plots for lepton eff
    for index in range(2):
        for abs_pdg in [11, 13]:
            lep_name = "mu" if abs_pdg==13 else "ele"
            plots.append(Plot(
              texX = 'p_{T}(%s_{%i}) (GeV)'%(lep_name, index), texY = 'Number of Events',
              name = '%s%i_pt'%(lep_name, index), attribute = lep_getter("pt", index, abs_pdg),
              binning=[400/20,0,400],
            ))
            plots.append(Plot(
             texX = '#eta(%s_{%i}) (GeV)'%(lep_name, index), texY = 'Number of Events',
             name = '%s%i_eta'%(lep_name, index), attribute = lep_getter("eta", index, abs_pdg),
             binning=[30,-3,3],
            ))
            plots.append(Plot(
             texX = '#phi(%s_{%i}) (GeV)'%(lep_name, index), texY = 'Number of Events',
             name = '%s%i_phi'%(lep_name, index), attribute = lep_getter("phi", index, abs_pdg),
             binning=[30,-pi,pi],
            ))



    plotting.fill(plots, read_variables = read_variables, sequence = sequence, ttreeFormulas = ttreeFormulas)

    # Get normalization yields from yield histogram
    for plot in plots:
        if plot.name == "yield":
            for i, l in enumerate(plot.histos):
                for j, h in enumerate(l):
                    yields[mode][plot.stack[i][j].name] = h.GetBinContent(h.FindBin(0.5+i_mode))
                    h.GetXaxis().SetBinLabel(1, "#mu#mu")
                    h.GetXaxis().SetBinLabel(2, "#mue")
                    h.GetXaxis().SetBinLabel(3, "ee")
        if plot.name.endswith("_Flag"):
            for i, l in enumerate(plot.histos):
                for j, h in enumerate(l):
                    h.GetXaxis().SetBinLabel(1, "fail")
                    h.GetXaxis().SetBinLabel(2, "veto")
                    h.GetXaxis().SetBinLabel(3, "loose")
                    h.GetXaxis().SetBinLabel(4, "medium")
                    h.GetXaxis().SetBinLabel(5, "tight")

    yields[mode]["data"] = 0

    yields[mode]["MC"] = sum(yields[mode][s.name] for s in mc)
    dataMCScale        = yields[mode]["data"]/yields[mode]["MC"] if yields[mode]["MC"] != 0 else float('nan')

    drawPlots(plots, mode, dataMCScale)
    allPlots[mode] = plots

# Add the different channels into SF and all
for mode in ["SF","all"]:
  yields[mode] = {}
  for y in yields[allModes[0]]:
    try:    yields[mode][y] = sum(yields[c][y] for c in (['ee','mumu'] if mode=="SF" else ['ee','mumu','mue']))
    except: yields[mode][y] = 0
  dataMCScale = yields[mode]["data"]/yields[mode]["MC"] if yields[mode]["MC"] != 0 else float('nan')

  for plot in allPlots['mumu']:
    for plot2 in (p for p in (allPlots['ee'] if mode=="SF" else allPlots["mue"]) if p.name == plot.name):  #For SF add EE, second round add EMu for all
      for i, j in enumerate(list(itertools.chain.from_iterable(plot.histos))):
        for k, l in enumerate(list(itertools.chain.from_iterable(plot2.histos))):
          if i==k:
            j.Add(l)

  drawPlots(allPlots['mumu'], mode, dataMCScale)

logger.info( "Done with prefix %s and selectionString %s", args.selection, cutInterpreter.cutString(args.selection) )
