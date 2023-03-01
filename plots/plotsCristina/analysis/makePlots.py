#!/usr/bin/env python
''' Analysis script for Stacked Plots
'''

#----------------- Standard imports and batch mode

import ROOT, os
import itertools
import copy
import array
import operator
from   math import sqrt, cos, sin, pi, atan2, cosh
import numpy as np

#----------------- RootTools import

from RootTools.core.standard import *
from RootTools.core.Sample import Sample
#import RootTools.core.logger             as logger_rt

#----------------- tttt tools import

from tttt.Tools.user import plot_directory
from tttt.Tools.cutInterpreter import cutInterpreter
from tttt.Tools.objectSelection import lepString, isBJet
from tttt.Tools.helpers import getObjDict

#import tttt.samples.UL_nanoAODv9_locations as locations

#---------------- Analysis Tools imports

from Analysis.Tools.helpers import deltaPhi, deltaR
from Analysis.Tools.puProfileCache import *
from Analysis.Tools.puReweighting import getReweightingFunction
import Analysis.Tools.syncer

print("All imports OK")

#---------------- Parser (customizable)

import argparse
parser = argparse.ArgumentParser(description = "Argument parser")
parser.add_argument('--logLevel', action='store', default='INFO', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
parser.add_argument('--small', action='store_true', help='Run only on a small subset of the data?', )
parser.add_argument('--noData', action='store_true', help='Do not plot data?')
#parser.add_argument('--sorting', action='store', default=None, choices=[None, "forDYMB"],  help='Sort histos?', )
parser.add_argument('--normalize', action='store_true', default=False, help="Normalize yields")
parser.add_argument('--dataMCScaling', action='store_true', help='Data MC scaling?', )
parser.add_argument('--plot_directory', action='store', default='tttt')
parser.add_argument('--selection', action='store', default='dilepL-offZ1-njet4p-btag2p-ht500')
parser.add_argument('--year', action='store', default='RunII', choices=['2016', '2016preVFP', '2017', '2018', 'RunII'])
args = parser.parse_args()

#---------------- Logger

import tttt.Tools.logger as logger
import RootTools.core.logger as logger_rt
import logging
#ACHTUNG ->   Changed the dependencies for logger and helpers (from TMB to tttt)

logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

#---------------- Add Samples

if args.year == '2016':
    from tttt.samples.nano_mc_private_UL20_Summer16_postProcessed_dilep import TTTT, TTLep
    args.plot_directory += "2016"
    if args.noData:
        from tttt.samples.nano_data_private_UL20_Run2016_postProcessed_dilep import Run2016
        data_sample = Run2016
        data_sample.name = "data"
    else:
        from tttt.samples.nano_private_UL20_RunII_postProcessed_dilep import RunII
        data_sample = RunII
        data_sample.name = "data"

if args.year == '2016preVFP':
    from tttt.samples.nano_mc_private_UL20_Summer16_preVFP_postProcessed_dilep import TTTT, TTLep
    args.plot_directory += "2016preVFP"
    if args.noData:
        from tttt.samples.nano_data_private_UL20_Run2016_preVFP_postProcessed_dilep import Run2016_preVFP
        data_sample = Run2016_preVFP
        data_sample.name = "data"
    else:
        from tttt.samples.nano_private_UL20_RunII_postProcessed_dilep import RunII
        data_sample = RunII
        data_sample.name = "data"

if args.year == '2017':
    from tttt.samples.nano_mc_private_UL20_Fall17_postProcessed_dilep import TTTT, TTLep
    args.plot_directory += "2017"
    if args.noData:
        from tttt.samples.nano_data_private_UL20_Run2017_postProcessed_dilep import Run2017
        data_sample = Run2017
        data_sample.name = "data"
    else:
        from tttt.samples.nano_private_UL20_RunII_postProcessed_dilep import RunII
        data_sample = RunII
        data_sample.name = "data"

if args.year == '2018':
    from tttt.samples.nano_mc_private_UL20_Autumn18_postProcessed_dilep import TTTT, TTLep
    args.plot_directory += "2018"
    if args.noData:
        from tttt.samples.nano_data_private_UL20_Run2018_postProcessed_dilep import Run2018
        data_sample = Run2018
        data_sample.name = "data"
    else:
        from tttt.samples.nano_private_UL20_RunII_postProcessed_dilep import RunII
        data_sample = RunII
        data_sample.name = "data"

if args.year == 'RunII':
    from tttt.samples.nano_private_UL20_RunII_postProcessed_dilep import TTLep, TTTT, TTW, TTZ, TTH, RunII
    args.plot_directory += "2018"
    if args.noData:
        from tttt.samples.nano_data_private_UL20_Run2018_postProcessed_dilep import Run2018
        data_sample = Run2018
        data_sample.name = "data"
    else:
        from tttt.samples.nano_private_UL20_RunII_postProcessed_dilep import RunII
        data_sample = RunII
        data_sample.name = "data"


#NOTE->move this bit to sample files?
sample_TTLep = TTLep
# ttbar gen classification: https://github.com/cms-top/cmssw/blob/topNanoV6_from-CMSSW_10_2_18/TopQuarkAnalysis/TopTools/plugins/GenTtbarCategorizer.cc
TTLep_bb    = copy.deepcopy( sample_TTLep )
TTLep_bb.name = "TTLep_bb"
TTLep_bb.texName = "t#bar{t}b#bar{b}"
TTLep_bb.color   = ROOT.kRed + 2
TTLep_bb.setSelectionString( "genTtbarId%100>=50" )
TTLep_cc    = copy.deepcopy( sample_TTLep )
TTLep_cc.name = "TTLep_cc"
TTLep_cc.texName = "t#bar{t}c#bar{c}"
TTLep_cc.color   = ROOT.kRed - 3
TTLep_cc.setSelectionString( "genTtbarId%100>=40&&genTtbarId%100<50" )
TTLep_other = copy.deepcopy( sample_TTLep )
TTLep_other.name = "TTLep_other"
TTLep_other.texName = "t#bar{t} + light j."
TTLep_other.setSelectionString( "genTtbarId%100<40" )

bkg = [TTLep_bb, TTLep_cc,TTLep_other]
all = [TTTT] + bkg

#--------------- Luminosity scale factor
lumi_scale =137. if args.noData else data_sample.lumi/1000.

#----------- Define scale factor for "small" option
for sample in all + [data_sample]:
    sample.scale           = 1

if args.small:
    args.plot_directory += "_small"
    if not args.noData:
        data_sample.reduceFiles( factor = 100 )
    for sample in all:
        sample.normalization = 1.
        sample.reduceFiles( to = 1 )
        sample.scale /= sample.normalization
        #NOTE --> For R&D we just use a fraction of the data




#--------------- Text on the plots

def drawObjects(plotData, dataMCScale, lumi_scale ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11)
    lines = [
        (0.15, 0.95, 'CMS Preliminary' if plotData else 'CMS Simulation'),
        (0.48, 0.95, 'L=%3.1f fb{}^{-1} (13 TeV) Scale %3.2f' % (lumi_scale, dataMCScale)) if plotData else (0.48, 0.95, '%3.1f fb^{-1} (13 TeV)' % lumi_scale)
    ]
    return [tex.DrawLatex(*l) for l in lines]

def drawPlots(plots, mode, dataMCScale):
  for log in [False, True]:
    plot_directory_ = os.path.join(plot_directory, 'analysisPlots', args.plot_directory, 'RunII', mode + ("_log" if log else ""), args.selection)
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
            drawObjects = drawObjects( not args.noData, dataMCScale , lumi_scale ) if not args.normalize else drawObjects(not args.noData, 1.0, lumi_scale),
            copyIndexPHP = True, extensions = ["png", "pdf", "root"],
          )

#---------------- Read variables and sequences


import tttt.MVA.configs as configs
config = configs.tttt_2l
read_variables = config.read_variables


sequence       = []

jetVars          = ['pt/F', 'eta/F', 'phi/F',
                    'btagDeepB/F',
                    'btagDeepFlavB/F',
                    'btagDeepFlavb/F',
                    'btagDeepFlavbb/F',
                    'btagDeepFlavlepb/F',
                    'btagDeepb/F',
                    'btagDeepbb/F',
                    'chEmEF/F', 'chHEF/F', 'neEmEF/F',
                    'neHEF/F', 'muEF/F',
                    'puId/F', 'qgl/F'
                    ]

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

read_variables_MC = [
    'reweightBTag_SF/F', 'reweightPU/F', 'reweightL1Prefire/F', 'reweightLeptonSF/F', 'reweightTrigger/F',
    "GenJet[pt/F,eta/F,phi/F,partonFlavour/I,hadronFlavour/i,nBHadFromT/I,nBHadFromTbar/I,nBHadFromW/I,nBHadOther/I,nCHadFromW/I,nCHadOther/I]"
    ]
# define 3l selections

jetVarNames      = [x.split('/')[0] for x in jetVars]

def make_jets( event, sample ):
    event.jets     = [getObjDict(event, 'JetGood_', jetVarNames, i) for i in range(int(event.nJetGood))]
    event.bJets    = filter(lambda j:isBJet(j, year=event.year) and abs(j['eta'])<=2.4    , event.jets)
sequence.append( make_jets )


def make_mva_inputs( event, sample ):
    for mva_variable, func in config.mva_variables:
        setattr( event, mva_variable, func(event, sample) )
sequence.append( make_mva_inputs )



from keras.models import load_model

models = [("tttt_3b_2l", False, load_model("/groups/hephy/cms/robert.schoefbeck/tttt/models/tttt_2l/tttt_2l/multiclass_model.h5"))]

def keras_predict( event, sample ):
    # get model inputs assuming lstm
    flat_variables, lstm_jets = config.predict_inputs( event, sample, jet_lstm = True)
    for name, has_lstm, model in models:
        print has_lstm, flat_variables, lstm_jets
        prediction = model.predict( flat_variables if not has_lstm else [flat_variables, lstm_jets] )
        setattr( event, name, prediction )
        if not prediction>-float('inf'):
            print name, prediction, [[getattr( event, mva_variable) for mva_variable, _ in config.mva_variables]]
            print event.nJetGood
            raise RuntimeError("Found NAN prediction?")
sequence.append( keras_predict )


#----------------- String base selections
mu_string  = lepString('mu','VL')
ele_string = lepString('ele','VL')
def getLeptonSelection( mode ):
    if   mode=="mumu": return "Sum$({mu_string})==2&&Sum$({ele_string})==0".format(mu_string=mu_string,ele_string=ele_string)
    elif mode=="mue":  return "Sum$({mu_string})==1&&Sum$({ele_string})==1".format(mu_string=mu_string,ele_string=ele_string)
    elif mode=="ee":   return "Sum$({mu_string})==0&&Sum$({ele_string})==2".format(mu_string=mu_string,ele_string=ele_string)
    elif mode=='all':    return "Sum$({mu_string})+Sum$({ele_string})==2".format(mu_string=mu_string,ele_string=ele_string)


yields     = {}
allPlots   = {}
allModes   = ['mumu','mue', 'ee']
for i_mode, mode in enumerate(allModes):
    yields[mode] = {}

    # "event.weight" is 0/1 for data, depending on whether it is from a certified lumi section. For MC, it corresponds to the 1/fb*cross-section/Nsimulated. So we multiply with the lumi in /fb.
    # This weight goes to the plot.
    weight_ = lambda event, sample: event.weight if sample.isData else event.weight*lumi_scale

    for sample in bkg: sample.style = styles.fillStyle(sample.color)
    TTTT.style = styles.lineStyle( ROOT.kBlack, width=2)
    if not args.noData:
        data_sample.style = styles.errorStyle( ROOT.kBlack )

    for sample in all:
      sample.read_variables = read_variables_MC
      sample.weight = lambda event, sample: event.reweightBTag_SF*event.reweightPU*event.reweightL1Prefire*event.reweightTrigger#*event.reweightLeptonSF

    #yt_TWZ_filter.scale = lumi_scale * 1.07314

    stack = Stack(all, [data_sample])

    # Use some defaults
    Plot.setDefaults(stack = stack, weight = staticmethod(weight_), selectionString = "("+getLeptonSelection(mode)+")&&("+cutInterpreter.cutString(args.selection)+")")

    plots = []


    plots.append(Plot(
        name = 'nVtxs', texX = 'Vertex Multiplicity', texY = 'Number of Events',
        attribute = TreeVariable.fromString( "PV_npvsGood/I" ),
        binning=[50,0,50],
        addOverFlowBin='upper',
    ))
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

    plots.append(Plot(
        name = 'btag_Ratio',
        texX = 'Btag_ratio', texY = 'Number of Events',
        attribute = lambda event, sample: (event.JetGood_btagDeepFlavbb[0]/(event.JetGood_btagDeepFlavb[0]+event.JetGood_btagDeepFlavlepb[0])),
        binning=[20,0,1],
    ))

    for model_name, _, binning in models:
        plots.append(Plot(
            name = model_name,
            texX = model_name, texY = 'Number of Events / 10 GeV',
            attribute = lambda event, sample, model_name=model_name: getattr(event, model_name),
            #binning=Binning.fromThresholds([0, 0.5, 1, 2,3,4,10]),
            binning=[50,0,1],
            addOverFlowBin='upper',
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

    yields[mode]["MC"] = sum(yields[mode][s.name] for s in bkg)
    if args.noData:
        dataMCScale = 1.
    else:
        dataMCScale        = yields[mode]["data"]/yields[mode]["MC"] if yields[mode]["MC"] != 0 else float('nan')

    drawPlots(plots, mode, dataMCScale)
    allPlots[mode] = plots

# Add the different channels into SF and all
for mode in ["SF","all"]:
    yields[mode] = {}
    for y in yields[allModes[0]]:
        try:    yields[mode][y] = sum(yields[c][y] for c in (['ee','mumu'] if mode=="SF" else ['ee','mumu','mue']))
        except: yields[mode][y] = 0
    if args.noData:
        dataMCScale = 1.
    else:
        dataMCScale = yields[mode]["data"]/yields[mode]["MC"] if yields[mode]["MC"] != 0 else float('nan')
    for plot in allPlots['mumu']:
        for plot2 in (p for p in (allPlots['ee'] if mode=="SF" else allPlots["mue"]) if p.name == plot.name):  #For SF add EE, second round add EMu for all
            for i, j in enumerate(list(itertools.chain.from_iterable(plot.histos))):
                for k, l in enumerate(list(itertools.chain.from_iterable(plot2.histos))):
                    if i==k: j.Add(l)

    drawPlots(allPlots['mumu'], mode, dataMCScale)

logger.info( "Done with prefix %s and selectionString %s", args.selection, cutInterpreter.cutString(args.selection) )
