#!/usr/bin/env python
''' Stacked plots (2l) 2D
'''

#       Standard imports

import ROOT
ROOT.gROOT.SetBatch(True)
c1 = ROOT.TCanvas() # do this to avoid version conflict in png.h with keras import
c1.Draw()
c1.Print('/tmp/delete.png')
h = ROOT.TH2F("x","x",100,0,1,100,0,1)
h.Draw("COLZ")
c1.Print('/tmp/delete.png')
import os, itertools, copy, array, operator
import numpy as np
from math                                import sqrt, cos, sin, pi, atan2, cosh

#       RootTools

from RootTools.core.standard             import *

#       tttt

from tttt.Tools.user                      import plot_directory
from tttt.Tools.cutInterpreter            import cutInterpreter
from tttt.Tools.objectSelection           import lepString
from tttt.Tools.helpers                   import getObjDict

#       Analysis Tools

from Analysis.Tools.helpers              import deltaPhi, deltaR
from Analysis.Tools.puProfileCache       import *
from Analysis.Tools.puReweighting        import getReweightingFunction
import Analysis.Tools.syncer

#       Arguments

import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',       action='store',      default='INFO', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--noData',         action='store_true', default=True, help='also plot data?')
argParser.add_argument('--small',                             action='store_true', help='Run only on a small subset of the data?', )
#argParser.add_argument('--sorting',                           action='store', default=None, choices=[None, "forDYMB"],  help='Sort histos?', )
argParser.add_argument('--dataMCScaling',  action='store_true', help='Data MC scaling?', )
argParser.add_argument('--plot_directory', action='store', default='tttt')
argParser.add_argument('--era',            action='store', type=str, default="RunII")
argParser.add_argument('--selection',      action='store', default='dilepL-offZ1-njet4p-btag2p-ht500')
args = argParser.parse_args()

if args.small:                        args.plot_directory += "_small"
if args.noData:                       args.plot_directory += "_noData"

#       Logger

import tttt.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)



#       Samples

from tttt.samples.nano_private_UL20_RunII_postProcessed_dilep import *

if args.era not in ["Run2016_preVFP", "Run2016", "Run2017", "Run2018", "RunII"]:
    raise Exception("Era %s not known"%args.era)

logger.info( "Working in era %s", args.era)

if args.era == "Run2016_preVFP":
    mc = [Summer16_preVFP.TTTT]
    sample_TTLep = Summer16_preVFP.TTLep
    lumi_scale = lumi_era['Run2016_preVFP']/1000.
if args.era == "Run2016":
    mc = [Summer16.TTTT]
    sample_TTLep = Summer16.TTLep
    lumi_scale = lumi_era['Run2016']/1000.
elif args.era == "Run2017":
    mc = [Fall17.TTTT]
    sample_TTLep = Fall17.TTLep
    lumi_scale = lumi_era['Run2017']/1000.
elif args.era == "Run2018":
    sample_TTLep = Autumn18.TTLep
    mc = [Autumn18.TTTT]
    lumi_scale = lumi_era['Run2018']/1000.
elif args.era == "RunII":
    sample_TTLep = TTLep
    mc = [DYJetsToLL, TTTT]
    lumi_scale = sum(lumi_year.values())/1000.

# ttbar gen classification: https://github.com/cms-top/cmssw/blob/topNanoV6_from-CMSSW_10_2_18/TopQuarkAnalysis/TopTools/plugins/GenTtbarCategorizer.cc
TTLep_bb    = copy.deepcopy( sample_TTLep )
TTLep_bb.name = "TTLep_bb"
TTLep_bb.texName = sample_TTLep.name+" (b#bar{b})"
TTLep_bb.color   = ROOT.kRed + 2
TTLep_bb.setSelectionString( "genTtbarId%100>=50" )
TTLep_cc    = copy.deepcopy( sample_TTLep )
TTLep_cc.name = "TTLep_cc"
TTLep_cc.texName = sample_TTLep.name+" (c#bar{c})"
TTLep_cc.color   = ROOT.kRed - 3
TTLep_cc.setSelectionString( "genTtbarId%100>=40&&genTtbarId%100<50" )
TTLep_other = copy.deepcopy( sample_TTLep )
TTLep_other.name = "TTLep_other"
TTLep_other.texName = sample_TTLep.name+" (other)"
TTLep_other.setSelectionString( "genTtbarId%100<40" )

mc = [ TTLep_bb,TTLep_cc,TTLep_other ] + mc

if args.small:
    for sample in mc:
        sample.normalization = 1.
        sample.reduceFiles( to = 1 )
        sample.scale /= sample.normalization

for sample in mc:
    sample.scale           = 1

#       Text on the plots

tex = ROOT.TLatex()
tex.SetNDC()
tex.SetTextSize(0.04)
tex.SetTextAlign(11) # align right

def charge(pdgId):
    return -pdgId/abs(pdgId)

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

      if isinstance( plot, Plot):
          ROOT.setTDRStyle()
          ROOT.gStyle.SetPalette()
          plotting.draw(plot,
            plot_directory = plot_directory_,
            ratio = {'yRange':(0.1,1.9)} if not args.noData else None,
            logX = False, logY = log, sorting = True,
            yRange = (0.03, "auto") if log else (0.001, "auto"),
            scaling = {0:1} if args.dataMCScaling else {},
            legend = ( (0.18,0.88-0.03*sum(map(len, plot.histos)),0.9,0.88), 2),
            drawObjects = drawObjects( not args.noData, dataMCScale , lumi_scale ) + _drawObjects,
            copyIndexPHP = True, extensions = ["png", "pdf", "root"],
          )
      if isinstance( plot, Plot2D):
          #print plot, plot.histos, plot.histos_added[0][0].Integral()
          ROOT.setTDRStyle()
          ROOT.gStyle.SetPalette()
          plotting.draw2D(plot,
            plot_directory = plot_directory_,
            logX = False, logY=False, logZ = log,
            drawObjects = drawObjects( not args.noData, dataMCScale , lumi_scale ) + _drawObjects,
            copyIndexPHP = True, extensions = ["png", "pdf", "root"],
          )

# Read variables and sequences
sequence       = []
#
# from tttt.Tools.objectSelection import isBJet

jetVars          = ['pt/F', 'eta/F', 'phi/F', 'btagDeepFlavB/F']
jetVarNames      = [x.split('/')[0] for x in jetVars]
# def make_jets( event, sample ):
#     event.jets     = [getObjDict(event, 'JetGood_', jetVarNames, i) for i in range(int(event.nJetGood))]
#     event.bJets    = filter(lambda j:isBJet(j, year=event.year) and abs(j['eta'])<=2.4    , event.jets)
# sequence.append( make_jets )

#MVA
import tttt.MVA.configs as configs
config = configs.tttt_2l
read_variables = config.read_variables


sequence += config.sequence
# Add sequence that computes the MVA inputs
def make_mva_inputs( event, sample ):
    for mva_variable, func in config.mva_variables:
        setattr( event, mva_variable, func(event, sample) )
sequence.append( make_mva_inputs )

# load models

#----------------- MVA configuration
import tttt.MVA.configs as configs
config = configs.tttt_2l
read_variables += config.read_variables

sequence += config.sequence

# Add sequence that computes the MVA inputs
def make_mva_inputs( event, sample ):
    for mva_variable, func in config.mva_variables:
        setattr( event, mva_variable, func(event, sample) )
sequence.append( make_mva_inputs )

from keras.models import load_model
classes = [ts.name for ts in config.training_samples]
print(classes)

models  = []#]{'name':'tttt_2l', 'has_lstm':False, 'classes':classes, 'model':load_model("/groups/hephy/cms/cristina.giordano/www/tttt/plots/tttt_2l/tttt_2l_v2/regression_model.h5")}]

def keras_predict( event, sample ):
    flat_variables, lstm_jets = config.predict_inputs( event, sample, jet_lstm = True)
    for model in models:
        if model['has_lstm']:
            prediction = model['model'].predict( [flat_variables ])#, lstm_jets] )
        else:
            prediction = model['model'].predict( [flat_variables] )
        for i_class_, class_ in enumerate(model['classes']):
            setattr( event, model['name']+'_'+class_, prediction[0][i_class_] )
sequence.append( keras_predict )

read_variables += [
    "weight/F", "year/I", "met_pt/F", "met_phi/F", "nBTag/I", "nJetGood/I", "PV_npvsGood/I",
    "l1_pt/F", "l1_eta/F" , "l1_phi/F", "l1_mvaTOP/F", "l1_mvaTOPWP/I", "l1_index/I",
    "l2_pt/F", "l2_eta/F" , "l2_phi/F", "l2_mvaTOP/F", "l2_mvaTOPWP/I", "l2_index/I",
    "JetGood[%s]"%(",".join(jetVars)),
    "lep[pt/F,eta/F,phi/F,pdgId/I,muIndex/I,eleIndex/I]",
    "Z1_l1_index/I", "Z1_l2_index/I", "nonZ1_l1_index/I", "nonZ1_l2_index/I",
    "Z1_phi/F", "Z1_pt/F", "Z1_mass/F", "Z1_cosThetaStar/F", "Z1_eta/F", "Z1_lldPhi/F", "Z1_lldR/F",
    "Muon[pt/F,eta/F,phi/F,dxy/F,dz/F,ip3d/F,sip3d/F,jetRelIso/F,miniPFRelIso_all/F,pfRelIso03_all/F,mvaTOP/F,mvaTTH/F,pdgId/I,segmentComp/F,nStations/I,nTrackerLayers/I]",
    "Electron[pt/F,eta/F,phi/F,dxy/F,dz/F,ip3d/F,sip3d/F,jetRelIso/F,miniPFRelIso_all/F,pfRelIso03_all/F,mvaTTH/F,pdgId/I,vidNestedWPBitmap/I,mvaTOP/F]",
    #"GenJet[pt/F,eta/F,phi/F,partonFlavour/I,hadronFlavour/i,nBHadFromT/I,nBHadFromTbar/I,nBHadFromW/I,nBHadOther/I,nCHadFromW/I,nCHadOther/I]"
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

#genJetSelection = "GenJet_pt>30&&abs(GenJet_eta)<2.4"

ttreeFormulas = {   #"nGenJet_absHF5":"Sum$(abs(GenJet_hadronFlavour)==5&&{genJetSelection})".format(genJetSelection=genJetSelection),
                    #"nGenJet_absPF5":"Sum$(abs(GenJet_partonFlavour)==5&&{genJetSelection})".format(genJetSelection=genJetSelection),
                    #"nGenJet_min1BHadFromTorTbar":"Sum$(GenJet_nBHadFromT+GenJet_nBHadFromTbar>=1&&{genJetSelection})".format(genJetSelection=genJetSelection),
                    #"nGenJet_min1BHadFromW":"Sum$(GenJet_nBHadFromW>=1&&{genJetSelection})".format(genJetSelection=genJetSelection),
                    #"nGenJet_min1BHadOther":"Sum$(GenJet_nBHadOther>=1&&{genJetSelection})".format(genJetSelection=genJetSelection),
                    #"nGenJet_min1CHadFromW":"Sum$(GenJet_nCHadFromW>=1&&{genJetSelection})".format(genJetSelection=genJetSelection),
                    #"nGenJet_min1CHadOther":"Sum$(GenJet_nCHadOther>=1&&{genJetSelection})".format(genJetSelection=genJetSelection),
    }

def getter( attr, s_name ):
    def getter_( event, sample):
        #print "Need %s get %s" %( s_name, sample.name )
        if sample.name==s_name:
            return getattr( event, attr)
        else:
            float('nan')
    return getter_

ROOT.setTDRStyle()
ROOT.gStyle.SetPalette()
yields     = {}
allPlots   = {}
allModes   = ['mumu','mue', 'ee']
for i_mode, mode in enumerate(allModes):
    yields[mode] = {}
    if not args.noData:
        data_sample.texName = "data"
        data_sample.name           = "data"
        data_sample.style          = styles.errorStyle(ROOT.kBlack)
        lumi_scale                 = data_sample.lumi/1000

    weight_ = lambda event, sample: event.weight if sample.isData else event.weight*lumi_era[args.era]/1000.

    for sample in mc: sample.style = styles.fillStyle(sample.color)

    for sample in mc:
      sample.read_variables = read_variables_MC
      sample.weight = lambda event, sample: event.reweightBTag_SF*event.reweightPU*event.reweightL1Prefire*event.reweightTrigger#*event.reweightLeptonSF

    #yt_TWZ_filter.scale = lumi_scale * 1.07314

    if not args.noData:
      stack = Stack(mc, data_sample)
    else:
      stack = Stack(mc)

    # Use some defaults
    Plot.setDefaults  (stack = stack, weight = staticmethod(weight_), selectionString = "("+getLeptonSelection(mode)+")&&("+cutInterpreter.cutString(args.selection)+")")
    Plot2D.setDefaults(               weight = staticmethod(weight_), selectionString = "("+getLeptonSelection(mode)+")&&("+cutInterpreter.cutString(args.selection)+")")

    plots   = []
    plots.append(Plot(
      name = 'yield', texX = '', texY = 'Number of Events',
      attribute = lambda event, sample: 0.5 + i_mode,
      binning=[3, 0, 3],
    ))

    plots2D = []
    for name, classes, has_lstm, model, in models:
        for i_tr_s, tr_s in enumerate( config.training_samples ):
            #disc_name = name+'_'+config.training_samples[i_tr_s].name
            disc_name = config.training_samples[i_tr_s].name

            print(disc_name)
            plots.append(Plot(
                texX = disc_name, texY = 'Number of Events',
                name = disc_name,
                attribute = lambda event, sample, disc_name=disc_name: getattr( event, disc_name ),
                binning=[50, 0, 1],
            ))

            for sample_ in mc:
                sample_name = sample_.name
                if "DY" in sample_name:# small background, large weights
                    continue
                for i_tr_s2, tr_s2 in enumerate( config.training_samples ):
                    if i_tr_s2<=i_tr_s: continue
                    disc2_name = name+'_'+config.training_samples[i_tr_s2].name
                    plot2D_name= name+'_'+sample_name+'_'+config.training_samples[i_tr_s].name+'_vs_'+config.training_samples[i_tr_s2].name
                    print(plot2D_name)
                    plots2D.append(Plot2D(
                        stack = Stack([sample_]),
                        texX = disc_name,
                        texY = disc2_name,
                        name = plot2D_name,
                        attribute = (
                            #getter( disc_name, sample_name),
                            #getter( disc2_name, sample_name),
                            lambda event, sample, disc_name=disc_name, s_name=sample_name: getattr( event, disc_name ) if sample.name==s_name else float('nan'),
                            lambda event, sample, disc2_name=disc2_name, s_name=sample_name: getattr( event, disc2_name )if sample.name==s_name else float('nan'),
                            ),
                        binning=[10, 0, 1, 10, 0, 1],
                    ))

    plotting.fill(plots+plots2D, read_variables = read_variables, sequence = sequence, ttreeFormulas = ttreeFormulas)

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

    if args.noData: yields[mode]["data"] = 0

    yields[mode]["MC"] = sum(yields[mode][s.name] for s in mc)
    dataMCScale        = yields[mode]["data"]/yields[mode]["MC"] if yields[mode]["MC"] != 0 else float('nan')

    drawPlots(plots+plots2D, mode, dataMCScale)
    allPlots[mode] = plots+plots2D

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

import pickle
pickle.dump( {p.name: p.histos for p in allPlots['mumu'] if isinstance(p, Plot2D)}, file( os.path.join(plot_directory, 'analysisPlots', args.plot_directory, args.era, args.selection+'.pkl'), 'w' ))

logger.info( "Done with prefix %s and selectionString %s", args.selection, cutInterpreter.cutString(args.selection) )
