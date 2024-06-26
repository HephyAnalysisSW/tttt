#!/usr/bin/env python
''' Analysis script for standard plots
'''

#Standard imports and batch mode

import ROOT, os
ROOT.TH1.AddDirectory(False)
import itertools
import copy
import array
import operator
import numpy as np
from math                                import sqrt, cos, sin, pi, atan2, cosh

#Standard imports and batch mode

from RootTools.core.standard             import *

#tttt tools import

from tttt.Tools.user                     import plot_directory
from tttt.Tools.cutInterpreter           import cutInterpreter
from tttt.Tools.objectSelection          import lepString, cbEleIdFlagGetter, vidNestedWPBitMapNamingList, isBJet
from tttt.Tools.helpers                  import getObjDict


#Analysis Tools imports

from Analysis.Tools.helpers              import deltaPhi, deltaR
from Analysis.Tools.puProfileCache       import *
from Analysis.Tools.puReweighting        import getReweightingFunction
import Analysis.Tools.syncer
from   Analysis.Tools.WeightInfo   	 import WeightInfo


#Argument Parser

import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',       action='store',      default='INFO', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--small',                             action='store_true', help='Run only on a small subset of the data?')
argParser.add_argument('--noData',         action='store_true', default=True,	 help='Do not plot data.')
#argParser.add_argument('--sorting',                           action='store', default=None, choices=[None, "forDYMB"],  help='Sort histos?', )
argParser.add_argument('--dataMCScaling',  action='store_true', help='Data MC scaling?')
argParser.add_argument('--plot_directory', action='store', default='4t')
argParser.add_argument('--selection',      action='store', default='trg-dilepL-OS-minDLmass20-onZ1-njet4p-btag2p-ht500')
argParser.add_argument('--era',            action='store', default='Run2018', help= 'Plot year split or inclusively')
argParser.add_argument('--signal',	   action='store', default='TTTT', help= 'Define the signal sample')
argParser.add_argument('--point',          action='store',  default='1', help="What is the value of the wilson coefficient?")
args = argParser.parse_args()

# DIrectory naming parser options

#if args.noData: args.plot_directory += "_noData"
if args.small: args.plot_directory += "_small"

#Logger

import tttt.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)


#Simulated samples

from tttt.samples.nano_private_UL20_RunII_postProcessed_dilep import *


if args.era not in ["Run2016_preVFP", "Run2016", "Run2017", "Run2018", "RunII"]:
    raise Exception("Era %s not known"%args.era)
if args.era == 'Run2016_preVFP':
        from tttt.samples.nano_mc_private_UL20_Summer16_preVFP_postProcessed_dilep import *
if args.era == 'Run2016':
        from tttt.samples.nano_mc_private_UL20_Summer16_postProcessed_dilep import *
if args.era == 'Run2017':
        from tttt.samples.nano_mc_private_UL20_Fall17_postProcessed_dilep import *
if args.era == 'Run2018':
        from tttt.samples.nano_mc_private_UL20_Autumn18_postProcessed_dilep import TTTT_EFT, TTbb_EFT
if args.era == 'RunII':
        from tttt.samples.nano_private_UL20_RunII_postProcessed_dilep import *

#signal
if args.signal == "TTTT" : signal = TTTT_EFT
elif args.signal == "TTbb" : signal = TTbb_EFT
else : raise Exception("Signal %s is not known!"%args.signal)

# Split dileptonic TTBar into three different contributions
#sample_TTLep = TTLep
## genTtbarId classification: https://github.com/cms-top/cmssw/blob/topNanoV6_from-CMSSW_10_2_18/TopQuarkAnalysis/TopTools/plugins/GenTtbarCategorizer.cc
#TTLep_bb    = copy.deepcopy( TTbb_EFT )
#TTLep_bb.name = "TTLep_bb"
#TTLep_bb.texName = "t#bar{t}b#bar{b}"
#TTLep_bb.color   = ROOT.kRed + 2
#TTLep_bb.setSelectionString( "genTtbarId%100>=50" )
#TTLep_cc    = copy.deepcopy( sample_TTLep )
#TTLep_cc.name = "TTLep_cc"
#TTLep_cc.texName = "t#bar{t}c#bar{c}"
#TTLep_cc.color   = ROOT.kRed - 3
#TTLep_cc.setSelectionString( "genTtbarId%100>=40&&genTtbarId%100<50" )
#TTLep_other = copy.deepcopy( sample_TTLep )
#TTLep_other.name = "TTLep_other"
#TTLep_other.texName = "t#bar{t} + light j."
#TTLep_other.setSelectionString( "genTtbarId%100<40" )

#Merge simulated background samples
mc = [signal]
#Add the data
if not args.noData:
    if args.era == 'Run2016_preVFP':
        from tttt.samples.nano_data_private_UL20_Run2016_preVFP_postProcessed_dilep import Run2016_preVFP as data_sample
    if args.era == 'Run2016':
        from tttt.samples.nano_data_private_UL20_Run2016_postProcessed_dilep import Run2016 as data_sample
    if args.era == 'Run2017':
        from tttt.samples.nano_data_private_UL20_Run2017_postProcessed_dilep import Run2017 as data_sample
    if args.era == 'Run2018':
        from tttt.samples.nano_data_private_UL20_Run2018_postProcessed_dilep import Run2018 as data_sample
    if args.era == 'RunII':
        from tttt.samples.nano_private_UL20_RunII_postProcessed_dilep import RunII as data_sample
    #data_sample = RunII
    data_sample.name = "data"
    all_samples = mc +  [data_sample]
else:
    all_samples = mc

#Luminosity scaling. Here we compute the scaling of the simulation to the data luminosity (event.weight corresponds to 1/fb for simulation, hence we divide the data lumi in pb^-1 by 1000)
#if args.era == 'Run2016_preVFP':
lumi_scale = 137. if args.noData else data_sample.lumi/1000.

#for sample in mc:
#    sample.scale  = 1

if args.small:
    if not args.noData:
        data_sample.reduceFiles( factor = 100 )
    for sample in mc :
        sample.normalization = 1.
        sample.reduceFiles( to = 1 )
#        sample.scale /= sample.normalization

#Helpers for putting text on the plots

tex = ROOT.TLatex()
tex.SetNDC()
tex.SetTextSize(0.04)
tex.SetTextAlign(11) # align right

def drawObjects( dataMCScale, lumi_scale ):
    lines = [
      (0.15, 0.95, 'CMS Simulation'),
      (0.45, 0.95, 'L=%3.1f fb{}^{-1} (13 TeV)' % lumi_scale),
    ]
    return [tex.DrawLatex(*l) for l in lines]

def drawPlots(plots, mode, dataMCScale):
  for log in [False, True]:
    if args.era in ["Run2016_preVFP", "Run2016", "Run2017", "Run2018"]:
        plot_directory_ = os.path.join(plot_directory, 'analysisPlots', args.plot_directory, args.era,"c"+args.point, mode + ("_log" if log else ""), args.selection)
    elif args.era == "RunII":
        plot_directory_ = os.path.join(plot_directory, 'analysisPlots', args.plot_directory, 'RunII',"c"+args.point, mode + ("_log" if log else ""), args.selection)
    for plot in plots:
      if not max(l.GetMaximum() for l in sum(plot.histos,[])): continue # Empty plot

      _drawObjects = []

      if isinstance( plot, Plot):
          plotting.draw(plot,
            plot_directory = plot_directory_,
	    ratio =  {'histos':[(1,0),(2,0),(3,0),(4,0),(5,0),(6,0),(7,0)],'yRange':(0.1,2.0),'texY': 'EFT/SM'}, #if not args.noData else None,
            logX = False, logY = log, sorting = True,
            yRange = (0.9, "auto") if log else (0.001, "auto"),
            scaling = {0:1} if args.dataMCScaling else {},
            legend = ( (0.18,0.88-0.03*sum(map(len, plot.histos)),0.9,0.88), 2),
            drawObjects = drawObjects( dataMCScale , lumi_scale ) + _drawObjects,
            copyIndexPHP = True, extensions = ["png", "pdf", "root"],
          )

read_variables = []

jetVars     =   ['pt/F',
                 'eta/F',
                 'phi/F',
                 'btagDeepFlavB/F',
                 'btagDeepFlavCvB/F',
                 'btagDeepFlavQG/F',
                 #'btagDeepFlavb/F',
                 #'btagDeepFlavbb/F',
                 #'btagDeepFlavlepb/F',
                 #'btagDeepb/F',
                 #'btagDeepbb/F',
                 'chEmEF/F',
                 'chHEF/F',
                 'neEmEF/F',
                 'neHEF/F',
		 'isBJet/O',
		 'isBJet_loose/O',
		 'isBJet_medium/O',
		 'isBJet_tight/O'
 		]

jetVarNames     = [x.split('/')[0] for x in jetVars]

#Read variables (data & MC)

read_variables += [
    "weight/F", "year/I", "met_pt/F", "met_phi/F", "nBTag/I", "nJetGood/I", "PV_npvsGood/I",
    "l1_pt/F", "l1_eta/F" , "l1_phi/F", "l1_mvaTOP/F", "l1_mvaTOPWP/I", "l1_index/I",
    "l2_pt/F", "l2_eta/F" , "l2_phi/F", "l2_mvaTOP/F", "l2_mvaTOPWP/I", "l2_index/I",
    "JetGood[%s]"%(",".join(jetVars)),
    "lep[pt/F,eta/F,phi/F,pdgId/I,muIndex/I,eleIndex/I,mvaTOP/F]",
    "Z1_l1_index/I", "Z1_l2_index/I",
    "Z1_phi/F", "Z1_pt/F", "Z1_mass/F", "Z1_cosThetaStar/F", "Z1_eta/F", "Z1_lldPhi/F", "Z1_lldR/F",
    "Muon[pt/F,eta/F,phi/F,dxy/F,dz/F,ip3d/F,sip3d/F,jetRelIso/F,miniPFRelIso_all/F,pfRelIso03_all/F,mvaTTH/F,pdgId/I,segmentComp/F,nStations/I,nTrackerLayers/I]",
    "Electron[pt/F,eta/F,phi/F,dxy/F,dz/F,ip3d/F,sip3d/F,jetRelIso/F,miniPFRelIso_all/F,pfRelIso03_all/F,mvaTTH/F,pdgId/I,vidNestedWPBitmap/I]",
]

#MC only
read_variables_MC = [
    'reweightBTagSF_central/F', 'reweightPU/F', 'reweightL1Prefire/F', 'reweightLeptonSF/F', 'reweightLeptonSFDown/F', 'reweightLeptonSFUp/F', 'reweightTrigger/F', 'reweightTopPt/F',
    "GenJet[pt/F,eta/F,phi/F,partonFlavour/I,hadronFlavour/i]"
    ]

read_variables_MC += [VectorTreeVariable.fromString( "p[C/F]", nMax=200 )]

sequence       = []

# MVA configuration
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
classes = [ts.name for ts in config.training_samples] if not hasattr( config, "classes") else config.classes

models  = [{'name':'tttt_2l', 'has_lstm':False, 'classes':classes, 'model':load_model("/groups/hephy/cms/cristina.giordano/www/tttt/plots/tttt_2l/tttt_2l/regression_model.h5")}]

def keras_predict( event, sample ):
    flat_variables, lstm_jets = config.predict_inputs( event, sample, jet_lstm = True)
    for model in models:
        if model['has_lstm']:
            prediction = model['model'].predict( [flat_variables ])#, lstm_jets] )
        else:
            prediction = model['model'].predict( [flat_variables] )
        for i_class_, class_ in enumerate(model['classes']):
            setattr( event, model['name']+'_'+class_, prediction[0][i_class_] )
	    #print model['name']+'_'+class_
sequence.append( keras_predict )

def cut_MVA(event,sample):
	this = getattr(event, "tttt_2l_2l_4t")
	setattr(event,"cut_tttt_MVA",1 if this>=0.9 else 0)
sequence.append(cut_MVA)

#WeightInfo
signal.weightInfo = WeightInfo(signal.reweight_pkl)
signal.weightInfo.set_order(2)

#EFT config
if args.signal == "TTTT":
   eft_configs= [{'param':{}, 'text':"SM",		'color':ROOT.kBlack},
		{'param':{'cQQ8':args.point}, 'text':"cQQ8="+args.point,	'color':ROOT.kOrange},
		{'param':{'cQQ1':args.point}, 'text':"cQQ1="+args.point,     'color':ROOT.kGreen},
		{'param':{'cQt1':args.point}, 'text':"cQt1="+args.point,     'color':ROOT.kGreen+2},
		{'param':{'ctt':args.point}, 'text':"ctt="+args.point,     'color':ROOT.kOrange+10},
		{'param':{'cQt8':args.point}, 'text':"cQt8="+args.point,     'color':ROOT.kOrange-9},
		{'param':{'ctHRe':args.point}, 'text':"ctHRe="+args.point,     'color':ROOT.kGreen-5},
		{'param':{'ctHIm':args.point}, 'text':"ctHIm="+args.point,     'color':ROOT.kOrange+5},
	      ]
if args.signal == "TTbb":
   eft_configs= [{'param':{}, 'text':"SM",		'color':ROOT.kBlack},
		{'param':{'cQQ8':args.point}, 'text':"cQQ8="+args.point,	'color':ROOT.kOrange},
		{'param':{'cQQ1':args.point}, 'text':"cQQ1="+args.point,     'color':ROOT.kGreen},
		{'param':{'cQt1':args.point}, 'text':"cQt1="+args.point,     'color':ROOT.kGreen+2},
		{'param':{'ctt':args.point}, 'text':"ctt="+args.point,     'color':ROOT.kOrange+10},
		{'param':{'cQt8':args.point}, 'text':"cQt8="+args.point,     'color':ROOT.kOrange-9},
		{'param':{'ctHRe':args.point}, 'text':"ctHRe="+args.point,     'color':ROOT.kGreen-5},
		{'param':{'ctHIm':args.point}, 'text':"ctHIm="+args.point,     'color':ROOT.kOrange+5},
		{'param':{'ctb1':args.point}, 'text':"ctb1="+args.point,     'color':ROOT.kCyan},
   		{'param':{'ctb8':args.point}, 'text':"ctb8="+args.point,     'color':ROOT.kCyan+2},
   		{'param':{'cQb1':args.point}, 'text':"cQb1="+args.point,     'color':ROOT.kCyan-8},
   		{'param':{'cQb8':args.point}, 'text':"cQb8="+args.point,     'color':ROOT.kBlue},
   		{'param':{'cQtQb1Re':args.point}, 'text':"cQtQb1Re="+args.point,     'color':ROOT.kBlue-3},
   		{'param':{'cQtQb8Re':args.point}, 'text':"cQtQb8Re="+args.point,     'color':ROOT.kBlue-7},
   		{'param':{'cQtQb1Im':args.point}, 'text':"cQtQb1Im="+args.point,     'color':ROOT.kViolet},
   		{'param':{'cQtQb8Im':args.point}, 'text':"cQtQb8Im="+args.point,     'color':ROOT.kViolet-1},
	      ]

for eft in eft_configs:
	eft['weight_func'] = signal.weightInfo.get_weight_func(**eft['param']) 
	eft['name'] = "_".join( ["signal"] + ( ["SM"] if len(eft['param'])==0 else [ "_".join([key, str(val)]) for key, val in sorted(eft['param'].iteritems())] ) )

def make_eft_weights( event, sample):
    if sample.name!=signal.name:
	    return
    event.eft_weights = [1] + [eft['weight_func'](event, sample) for eft in eft_configs[1:]]
    #if event.event == 2393412 or event.event == 1882425: 
    #print "FOUND IT!! eft weight is : "+ event.eft_weights

sequence.append( make_eft_weights )

def make_manyJets(event, sample):
    thresholds = [30, 40, 80, 200]
    for threshold in thresholds:
        postfix = 'Pt{}'.format(threshold)

        filtered_jets = [j for j in event.jets if j['pt'] > threshold]
        setattr(event, 'nJetGood'+postfix, len(filtered_jets))
        setattr(event, 'ht'+postfix, sum(jet['pt'] for jet in filtered_jets))

        cos_pt, sin_pt = 0., 0.
        for j in filtered_jets:
            cos_pt += j['pt'] * cos(j['phi'])
            sin_pt += j['pt'] * sin(j['phi'])

        setattr(event, 'ISRJet'+postfix, sqrt(cos_pt**2 + sin_pt**2))

sequence.append(make_manyJets)

stack = Stack()
eft_weights = []

for i_eft, eft in enumerate(eft_configs):
    signal.style = styles.errorStyle(eft['color'])
    stack.append( [signal] )
    eft_weights.append( [lambda event, sample, i_eft=i_eft: event.eft_weights[i_eft]*event.weight] )


#Let's make a function that provides string-based lepton selection
mu_string  = lepString('mu','VL')
ele_string = lepString('ele','VL')
def getLeptonSelection( mode ):
    if   mode=="mumu": return "Sum$({mu_string})==2&&Sum$({ele_string})==0".format(mu_string=mu_string,ele_string=ele_string)
    elif mode=="mue":  return "Sum$({mu_string})==1&&Sum$({ele_string})==1".format(mu_string=mu_string,ele_string=ele_string)
    elif mode=="ee":   return "Sum$({mu_string})==0&&Sum$({ele_string})==2".format(mu_string=mu_string,ele_string=ele_string)
    elif mode=='all':    return "Sum$({mu_string})+Sum$({ele_string})==2".format(mu_string=mu_string,ele_string=ele_string)

def charge(pdgId):
    return -pdgId/abs(pdgId)

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

# TTreeFormulas are faster than if we compute things in the event loop.
ttreeFormulas = { #"bbTag_max_value" : "Max$(JetGood_btagDeepFlavbb/(JetGood_btagDeepFlavb+JetGood_btagDeepFlavlepb))",
#		  "nJetGood_pt30" : "Sum$(JetGood_pt>30)",
#                  "nJetGood_pt40" : "Sum$(JetGood_pt>40)",
#                  "nJetGood_pt50" : "Sum$(JetGood_pt>50)",
#                  "nJetGood_pt80" : "Sum$(JetGood_pt>80)",
#                  "nJetGood_pt100" : "Sum$(JetGood_pt>100)",
#                  "nJetGood_pt150" : "Sum$(JetGood_pt>150)",
#                  "nJetGood_pt200" : "Sum$(JetGood_pt>200)",
#                  "nBTag_loose"   : "Sum$(JetGood_isBJet_loose)",
#                  "nBTag_medium"  : "Sum$(JetGood_isBJet_medium)" ,
#                  "nBTag_tight"   : "Sum$(JetGood_isBJet_tight)" ,
#                  "nBTag_loose_pt30"   : "Sum$(JetGood_isBJet_loose&&JetGood_pt>30)",
#                  "nBTag_medium_pt30"  : "Sum$(JetGood_isBJet_medium&&JetGood_pt>30)" ,
#                  "nBTag_tight_pt30"   : "Sum$(JetGood_isBJet_tight&&JetGood_pt>30)"  ,
#                  "nBTag_loose_pt40"   : "Sum$(JetGood_isBJet_loose&&JetGood_pt>40)",
#                  "nBTag_medium_pt40"  : "Sum$(JetGood_isBJet_medium&&JetGood_pt>40)" ,
#                  "nBTag_tight_pt40"   : "Sum$(JetGood_isBJet_tight&&JetGood_pt>40)"  ,
#                  "nBTag_loose_pt50"   : "Sum$(JetGood_isBJet_loose&&JetGood_pt>50)",
#                  "nBTag_medium_pt50"  : "Sum$(JetGood_isBJet_medium&&JetGood_pt>50)" ,
#                  "nBTag_tight_pt50"   : "Sum$(JetGood_isBJet_tight&&JetGood_pt>50)",
		 }

yields     = {}
allPlots   = {}
allModes   = ['mumu','mue', 'ee']
for i_mode, mode in enumerate(allModes):
    yields[mode] = {}

    # "event.weight" is 0/1 for data, depending on whether it is from a certified lumi section. For MC, it corresponds to the 1/fb*cross-section/Nsimulated. So we multiply with the lumi in /fb.

# This weight goes to the plot. DO NOT apply it again to the samples
    #weight_ = lambda event, sample: event.weight if sample.isData else event.weight
    #weight_ = lambda event, sample: event.cut_tttt_MVA*(event.weight if sample.isData else event.weight)

    #Plot styling
    #for sample in mc: sample.style = styles.fillStyle(sample.color)
    if not args.noData:
        data_sample.style = styles.errorStyle( ROOT.kBlack )

    #Apply reweighting to MC for specific detector effects
    for sample in mc:
      sample.read_variables = read_variables_MC
      sample.weight = lambda event, sample: event.reweightBTagSF_central*event.reweightPU*event.reweightL1Prefire*event.reweightTrigger*event.reweightLeptonSF*event.reweightTopPt

    #Stack : Define what we want to see.
    #if not args.noData:
    #   stack = Stack(mc, [data_sample])
    #else:
    #   stack = Stack(mc)

    # Define everything we want to have common to all plots
    Plot.setDefaults(stack = stack, weight = eft_weights, selectionString = "("+getLeptonSelection(mode)+")&&("+cutInterpreter.cutString(args.selection)+")")

    plots = []

    #Yeld plot
    plots.append(Plot(
      name = 'yield', texX = '', texY = 'Number of Events',
      attribute = lambda event, sample: 0.5 + i_mode,
      binning=[3, 0, 3],
    ))

    for model in models:
        for class_ in model['classes']:
            model_name = model['name']+'_'+class_
            plots.append(Plot(
                name = class_,
                texX = model_name, texY = 'Number of Events',
                attribute = lambda event, sample, model_name=model_name: getattr(event, model_name),#if event.nJetGood> 5 and event.nJetGood < 7 else float('nan') ,
                binning=[10,0,1],
                addOverFlowBin='upper',
            ))

    for model in models:
        for class_ in model['classes']:
	    model_name = model['name']+'_'+class_
            plots.append(Plot(
                name = class_+"_course",
                texX = model_name, texY = 'Number of Events',
                attribute = lambda event, sample, model_name=model_name: getattr(event, model_name),#if event.nJetGood> 5 and event.nJetGood < 7 else float('nan') ,
                binning=Binning.fromThresholds([0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.82,0.84,0.86,0.88,0.90,0.92,0.94,0.96,0.98,1.0]),
                addOverFlowBin='upper',
            ))

##    plots.append(Plot( name = 'bbtag_discriminator' , texX = 'max(bb_over_blepb)' , texY = 'Number of Events',
##        attribute = lambda event, sample: event.bbTag_max_value,
##        binning = [30,0,3],
##    ))
##
##    plots.append(Plot( name = 'bbTag_value_leadingJet' , texX = 'DeepFlavbb-jet0' , texY = 'Number of Events',
##        attribute = lambda event, sample: event.JetGood_btagDeepFlavbb[0],
##        binning = [20,0,1],
##    ))
##
##    plots.append(Plot( name = 'bbTag_value_subleadingJet' , texX = 'DeepFlavbb-jet1' , texY = 'Number of Events',
##        attribute = lambda event, sample: event.JetGood_btagDeepFlavbb[1],
##        binning = [20,0,1],
##    ))
#
#    plots.append(Plot( name = 'Btagging_discriminator_value_Jet0' , texX = 'DeepB J0' , texY = 'Number of Events',
#        attribute = lambda event, sample: event.JetGood_btagDeepFlavB[0],
#        binning = [20,0,1],
#    ))
#
#    plots.append(Plot( name = 'Btagging_discriminator_value_Jet1' , texX = 'DeepB J1' , texY = 'Number of Events',
#        attribute = lambda event, sample: event.JetGood_btagDeepFlavB[1],
#        binning = [20,0,1],
#    ))
#
#    # for model in models:
#    #     for class_ in model['classes']:
#    #         model_name = model['name']+'_'+class_
#    #         plots.append(Plot(
#    #             name = model_name,
#    #             texX = model_name, texY = 'Number of Events',
#    #             attribute = lambda event, sample, model_name=model_name: getattr(event, model_name),
#    #             binning=[50,0,1],
#    #             addOverFlowBin='upper',
#    #         ))
#
#    plots.append(Plot(
#      name = 'nVtxs', texX = 'vertex multiplicity', texY = 'Number of Events',
#      attribute = TreeVariable.fromString( "PV_npvsGood/I" ),
#      binning=[50,0,50],
#      addOverFlowBin='upper',
#    ))
#
#    plots.append(Plot(
#        name = 'l1_pt',
#        texX = 'p_{T}(l_{1}) (GeV)', texY = 'Number of Events / 20 GeV',
#        attribute = lambda event, sample:event.l1_pt,
#        binning=[15,0,300],
#        addOverFlowBin='upper',
#    ))
#
#    plots.append(Plot(
#        name = 'l1_eta',
#        texX = '#eta(l_{1})', texY = 'Number of Events',
#        attribute = lambda event, sample: event.l1_eta,
#        binning=[20,-3,3],
#    ))
#
#    plots.append(Plot(
#        name = 'l1_mvaTOP',
#        texX = 'MVA_{TOP}(l_{1})', texY = 'Number of Events',
#        attribute = lambda event, sample: event.l1_mvaTOP,
#        binning=[20,-1,1],
#    ))
#
#    plots.append(Plot(
#        name = 'l1_mvaTOPWP',
#        texX = 'MVA_{TOP}(l_{1}) WP', texY = 'Number of Events',
#        attribute = lambda event, sample: event.l1_mvaTOPWP,
#        binning=[5,0,5],
#    ))
#
#    plots.append(Plot(
#        name = 'l2_pt',
#        texX = 'p_{T}(l_{2}) (GeV)', texY = 'Number of Events / 20 GeV',
#        attribute = lambda event, sample:event.l2_pt,
#        binning=[15,0,300],
#        addOverFlowBin='upper',
#    ))
#
#    plots.append(Plot(
#        name = 'l2_eta',
#        texX = '#eta(l_{2})', texY = 'Number of Events',
#        attribute = lambda event, sample: event.l2_eta,
#        binning=[20,-3,3],
#    ))
#
#    plots.append(Plot(
#        name = 'l2_mvaTOP',
#        texX = 'MVA_{TOP}(l_{2})', texY = 'Number of Events',
#        attribute = lambda event, sample: event.l2_mvaTOP,
#        binning=[20,-1,1],
#    ))
#
#    plots.append(Plot(
#        name = 'l2_mvaTOPWP',
#        texX = 'MVA_{TOP}(l_{1}) WP', texY = 'Number of Events',
#        attribute = lambda event, sample: event.l2_mvaTOPWP,
#        binning=[5,0,5],
#    ))
#
#    plots.append(Plot(
#        texX = 'E_{T}^{miss} (GeV)', texY = 'Number of Events / 20 GeV',
#        attribute = TreeVariable.fromString( "met_pt/F" ),
#        binning=[400/20,0,400],
#        addOverFlowBin='upper',
#    ))
#
#    plots.append(Plot(
#        texX = '#phi(E_{T}^{miss})', texY = 'Number of Events / 20 GeV',
#        attribute = TreeVariable.fromString( "met_phi/F" ),
#        binning=[10,-pi,pi],
#    ))
#
#    plots.append(Plot(
#        name = "Z1_pt",
#        texX = 'p_{T}(Z_{1}) (GeV)', texY = 'Number of Events / 20 GeV',
#        attribute = TreeVariable.fromString( "Z1_pt/F" ),
#        binning=[20,0,400],
#        addOverFlowBin='upper',
#    ))
#
#    plots.append(Plot(
#        name = 'Z1_pt_coarse', texX = 'p_{T}(Z_{1}) (GeV)', texY = 'Number of Events / 50 GeV',
#        attribute = TreeVariable.fromString( "Z1_pt/F" ),
#        binning=[16,0,800],
#        addOverFlowBin='upper',
#    ))
#
#    plots.append(Plot(
#        name = 'Z1_pt_superCoarse', texX = 'p_{T}(Z_{1}) (GeV)', texY = 'Number of Events',
#        attribute = TreeVariable.fromString( "Z1_pt/F" ),
#        binning=[3,0,600],
#        addOverFlowBin='upper',
#    ))
#
#    plots.append(Plot(
#        name = 'Z1_pt_coarse', texX = 'p_{T}(Z_{1}) (GeV)', texY = 'Number of Events / 50 GeV',
#        attribute = TreeVariable.fromString( "Z1_pt/F" ),
#        binning=[16,0,800],
#    ))
#
#    plots.append(Plot(
#        name = 'Z1_pt_superCoarse', texX = 'p_{T}(Z_{1}) (GeV)', texY = 'Number of Events',
#        attribute = TreeVariable.fromString( "Z1_pt/F" ),
#        binning=[3,0,600],
#    ))
#
#    plots.append(Plot(
#      texX = 'p_{T}(leading l) (GeV)', texY = 'Number of Events / 20 GeV',
#      name = 'lep1_pt', attribute = lambda event, sample: event.lep_pt[0],
#      binning=[400/20,0,400],
#    ))
#
#    plots.append(Plot(
#      texX = 'p_{T}(subleading l) (GeV)', texY = 'Number of Events / 10 GeV',
#      name = 'lep2_pt', attribute = lambda event, sample: event.lep_pt[1],
#      binning=[200/10,0,200],
#    ))
#
#    plots.append(Plot(
#      texX = 'p_{T}(trailing l) (GeV)', texY = 'Number of Events / 10 GeV',
#      name = 'lep3_pt', attribute = lambda event, sample: event.lep_pt[2],
#      binning=[150/10,0,150],
#    ))
#    plots.append(Plot(
#        texX = 'M(ll) (GeV)', texY = 'Number of Events / 20 GeV',
#        attribute = TreeVariable.fromString( "Z1_mass/F" ),
#        binning=[10,81,101],
#        addOverFlowBin='upper',
#    ))
#
#    plots.append(Plot(
#        name = "Z1_mass_wide",
#        texX = 'M(ll) (GeV)', texY = 'Number of Events / 2 GeV',
#        attribute = TreeVariable.fromString( "Z1_mass/F" ),
#        binning=[50,20,120],
#        addOverFlowBin='upper',
#    ))
#
#    plots.append(Plot(
#        name = "Z1_cosThetaStar", texX = 'cos#theta(l-)', texY = 'Number of Events / 0.2',
#        attribute = lambda event, sample:event.Z1_cosThetaStar,
#        binning=[10,-1,1],
#    ))
#
#    plots.append(Plot(
#        name = "Z2_mass_wide",
#        texX = 'M(ll) of 2nd OSDL pair', texY = 'Number of Events / 2 GeV',
#        attribute = TreeVariable.fromString( "Z2_mass/F" ),
#        binning=[60,0,120],
#        addOverFlowBin='upper',
#    ))
#
#    plots.append(Plot(
#        name = "minDLmass",
#        texX = 'min mass of all DL pairs', texY = 'Number of Events / 2 GeV',
#        attribute = TreeVariable.fromString( "minDLmass/F" ),
#        binning=[60,0,120],
#        addOverFlowBin='upper',
#    ))
#
#    plots.append(Plot(
#        texX = '#Delta#phi(Z_{1}(ll))', texY = 'Number of Events',
#        attribute = TreeVariable.fromString( "Z1_lldPhi/F" ),
#        binning=[10,0,pi],
#    ))
#
#    plots.append(Plot(
#        texX = '#Delta R(Z_{1}(ll))', texY = 'Number of Events',
#        attribute = TreeVariable.fromString( "Z1_lldR/F" ),
#        binning=[10,0,6],
#    ))

    plots.append(Plot(
      texX = 'N_{jets}', texY = 'Number of Events',
      attribute = TreeVariable.fromString( "nJetGood/I" ), #nJetSelected
      binning=[8,3.5,11.5],
    ))

#    plots.append(Plot(
#      name = "nJetGood_pt30",
#      texX = 'N_{jets}', texY = 'Number of Events',
#      attribute = lambda event, sample:event.nJetGood_pt30, #nJetSelected_pt>30
#      binning=[8,3.5,11.5],
#    ))
#
#    plots.append(Plot(
#      name = "nJetGood_pt40",
#      texX = 'N_{jets}', texY = 'Number of Events',
#      attribute = lambda event, sample:event.nJetGood_pt40, #nJetSelected_pt>40
#      binning=[8,3.5,11.5],
#    ))
#
#    plots.append(Plot(
#      name = "nJetGood_pt50",
#      texX = 'N_{jets}', texY = 'Number of Events',
#      attribute = lambda event, sample:event.nJetGood_pt50, #nJetSelected_pt>50
#      binning=[8,3.5,11.5],
#    ))
#
#    plots.append(Plot(
#      name = "nJetGood_pt80",
#      texX = 'N_{jets}', texY = 'Number of Events',
#      attribute = lambda event, sample:event.nJetGood_pt80, #nJetSelected_pt>80
#      binning=[8,3.5,11.5],
#    ))
#
#    plots.append(Plot(
#      name = "nJetGood_pt100",
#      texX = 'N_{jets}', texY = 'Number of Events',
#      attribute = lambda event, sample:event.nJetGood_pt100, #nJetSelected_pt>100
#      binning=[8,3.5,11.5],
#    ))
#
#    plots.append(Plot(
#      name = "nJetGood_pt150",
#      texX = 'N_{jets}', texY = 'Number of Events',
#      attribute = lambda event, sample:event.nJetGood_pt150, #nJetSelected_pt>150
#      binning=[8,3.5,11.5],
#    ))
#
#    plots.append(Plot(
#      name = "nJetGood_pt200",
#      texX = 'N_{jets}', texY = 'Number of Events',
#      attribute = lambda event, sample:event.nJetGood_pt200, #nJetSelected_pt>200
#      binning=[8,3.5,11.5],
#    ))
#
#    plots.append(Plot(
#      name = "nBTag_loose_pt30",
#      texX = 'N_{jets}', texY = 'Number of Events',
#      attribute = lambda event, sample:event.nBTag_loose_pt30, #nJetSelected_pt>30
#      binning=[7,-0.5,6.5],
#    ))
#
#    plots.append(Plot(
#      name = "nBTag_loose_pt40",
#      texX = 'N_{jets}', texY = 'Number of Events',
#      attribute = lambda event, sample:event.nBTag_loose_pt40, #nJetSelected_pt>40
#      binning=[7,-0.5,6.5],
#    ))
#
#    plots.append(Plot(
#      name = "nBTag_loose_pt50",
#      texX = 'N_{jets}', texY = 'Number of Events',
#      attribute = lambda event, sample:event.nBTag_loose_pt50, #nJetSelected_pt>50
#      binning=[7,-0.5,6.5],
#    ))
#
#    plots.append(Plot(
#      name = "nBTag_medium_pt30",
#      texX = 'N_{jets}', texY = 'Number of Events',
#      attribute = lambda event, sample:event.nBTag_medium_pt30, #nJetSelected_pt>30
#      binning=[7,-0.5,6.5],
#    ))
#
#    plots.append(Plot(
#      name = "nBTag_medium_pt40",
#      texX = 'N_{jets}', texY = 'Number of Events',
#      attribute = lambda event, sample:event.nBTag_medium_pt40, #nJetSelected_pt>40
#      binning=[7,-0.5,6.5],
#    ))
#
#    plots.append(Plot(
#      name = "nBTag_medium_pt50",
#      texX = 'N_{jets}', texY = 'Number of Events',
#      attribute = lambda event, sample:event.nBTag_medium_pt50, #nJetSelected_pt>50
#      binning=[7,-0.5,6.5],
#    ))
#
#    plots.append(Plot(
#      name = "nBTag_tight_pt30",
#      texX = 'N_{jets}', texY = 'Number of Events',
#      attribute = lambda event, sample:event.nBTag_tight_pt30, #nJetSelected_pt>30
#      binning=[7,-0.5,6.5],
#    ))
#
#    plots.append(Plot(
#      name = "nBTag_tight",
#      texX = 'N_{jets}', texY = 'Number of Events',
#      attribute = lambda event, sample:event.nBTag_tight, #nBJetTight
#      binning=[7, -0.5,6.5],
#    ))
#
#    plots.append(Plot(
#      name = "nBTag_medium",
#      texX = 'N_{jets}', texY = 'Number of Events',
#      attribute = lambda event, sample:event.nBTag_medium, #nBJetMedium
#      binning=[7, -0.5,6.5],
#    ))
#
#    plots.append(Plot(
#      name = "nBTag_loose",
#      texX = 'N_{jets}', texY = 'Number of Events',
#      attribute = lambda event, sample:event.nBTag_loose, #nBJetLoose
#      binning=[7, -0.5,6.5],
#    ))

    plots.append(Plot(
      texX = 'N_{b-tag}', texY = 'Number of Events',
      attribute = TreeVariable.fromString( "nBTag/I" ), #nJetSelected
      binning=[7, -0.5,6.5],
    ))

    plots.append(Plot(
      texX = 'H_{T} (GeV)', texY = 'Number of Events / 100 GeV',
      name = 'ht', attribute = lambda event, sample: sum( j['pt'] for j in event.jets ),
      binning=[2000/200,500,2500],#[1500/50,0,1500],
    ))

    plots.append(Plot(
      texX = 'H_{T} from p_{T}(j)>30 ', texY = 'Number of Events / 100 GeV',
      name = 'htPt30', attribute = lambda event, sample: event.htPt30,
      binning=[2000/200,500,2500],
    ))

    plots.append(Plot(
      texX = 'H_{T} from p_{T}(j)>40 ', texY = 'Number of Events / 100 GeV',
      name = 'htPt40', attribute = lambda event, sample: event.htPt40,
      binning=[2000/200,500,2500],
    ))

    plots.append(Plot(
      texX = 'H_{T} from p_{T}(j)>80 ', texY = 'Number of Events / 100 GeV',
      name = 'htPt80', attribute = lambda event, sample: event.htPt80,
      binning=[2000/200,500,2500],
    ))

    plots.append(Plot(
      texX = 'H_{T} from p_{T}(j)>200 ', texY = 'Number of Events / 100 GeV',
      name = 'htPt200', attribute = lambda event, sample: event.htPt200,
      binning=[2500/100,0,2500],
    ))

    plots.append(Plot(
      texX = 'H_{T}b (GeV)', texY = 'Number of Events / 30 GeV',
      name = 'htb', attribute = lambda event, sample: sum( j['pt'] for j in event.bJets ),
      binning=[1500/50,0,1500],
    ))

#    plots.append(Plot(
#      texX = '#eta(leading jet) (GeV)', texY = 'Number of Events / 30 GeV',
#      name = 'jet0_eta', attribute = lambda event, sample: event.JetGood_eta[0],
#      binning=[20,-3,3],
#    ))
#
#    plots.append(Plot(
#      texX = '#eta(subleading jet) (GeV)', texY = 'Number of Events / 30 GeV',
#      name = 'jet1_eta', attribute = lambda event, sample: event.JetGood_eta[1],
#      binning=[20,-3,3],
#    ))
#
#    plots.append(Plot(
#      texX = '#phi(leading jet) (GeV)', texY = 'Number of Events / 30 GeV',
#      name = 'jet0_phi', attribute = lambda event, sample: event.JetGood_phi[0],
#      binning=[10,-pi,pi],
#    ))
#
#    plots.append(Plot(
#      texX = '#phi(subleading jet) (GeV)', texY = 'Number of Events / 30 GeV',
#      name = 'jet1_phi', attribute = lambda event, sample: event.JetGood_phi[1],
#      binning=[10,-pi,pi],
#    ))
#
#
#
    plots.append(Plot(
      texX = 'p_{T}(leading jet) (GeV)', texY = 'Number of Events / 30 GeV',
      name = 'jet0_pt', attribute = lambda event, sample: event.JetGood_pt[0],
      binning=[600/30,0,600],
    ))

    plots.append(Plot(
      texX = 'p_{T}(subleading jet) (GeV)', texY = 'Number of Events / 30 GeV',
      name = 'jet1_pt', attribute = lambda event, sample: event.JetGood_pt[1],
      binning=[600/30,0,600],
    ))

    plots.append(Plot(
      texX = 'p_{T}(jet2) (GeV)', texY = 'Number of Events / 30 GeV',
      name = 'jet2_pt', attribute = lambda event, sample: event.JetGood_pt[2] if event.nJetGood >= 3 else float('nan'),
      binning=[600/30,0,600],
      addOverFlowBin='upper',
    ))

    plots.append(Plot(
      texX = 'p_{T}(jet3) (GeV)', texY = 'Number of Events / 30 GeV',
      name = 'jet3_pt', attribute = lambda event, sample: event.JetGood_pt[3] if event.nJetGood >= 4 else float('nan'),
      binning=[600/30,0,600],
      addOverFlowBin='upper',
    ))

    plots.append(Plot(
      texX = 'p_{T}(jet4) (GeV)', texY = 'Number of Events / 30 GeV',
      name = 'jet4_pt', attribute = lambda event, sample: event.JetGood_pt[4] if event.nJetGood >= 5 else float('nan'),
      binning=[600/30,0,600],
      addOverFlowBin='upper',
    ))

    plots.append(Plot(
      texX = 'p_{T}(jet5) (GeV)', texY = 'Number of Events / 30 GeV',
      name = 'jet5_pt', attribute = lambda event, sample: event.JetGood_pt[5] if event.nJetGood >= 6 else float('nan'),
      binning=[600/30,0,600],
      addOverFlowBin='upper',
    ))

    plots.append(Plot(
      texX = 'p_{T}(jet6) (GeV)', texY = 'Number of Events / 30 GeV',
      name = 'jet6_pt', attribute = lambda event, sample: event.JetGood_pt[6] if event.nJetGood >= 7 else float('nan'),
      binning=[600/30,0,600],
      addOverFlowBin='upper',
    ))

    plots.append(Plot(
      texX = 'p_{T}(jet7) (GeV)', texY = 'Number of Events / 30 GeV',
      name = 'jet7_pt', attribute = lambda event, sample: event.JetGood_pt[7] if event.nJetGood >= 8 else float('nan'),
      binning=[600/30,0,600],
      addOverFlowBin='upper',
    ))


    # plots.append(Plot(
    #   texX = 'p_{T}(subleading jet) most bb (GeV)', texY = 'Number of Events / 30 GeV',
    #   name = 'jet1_ptbb', attribute = lambda event, sample: event.JetGood_pt[1] if (event.JetGood_btagDeepFlavbb[1]=>0.002),
    #   binning=[600/30,0,600],
    # ))

##    for index in range(2):
##        for abs_pdg in [11, 13]:
##            lep_name = "mu" if abs_pdg==13 else "ele"
##            plots.append(Plot(
##              texX = 'p_{T}(%s_{%i}) (GeV)'%(lep_name, index), texY = 'Number of s',
##              name = '%s%i_pt'%(lep_name, index), attribute = lep_getter("pt", index, abs_pdg),
##              binning=[400/20,0,400],
##            ))
##	    plots.append(Plot(
##              texX = '#eta(%s_{%i}) (GeV)'%(lep_name, index), texY = 'Number of Events',
##              name = '%s%i_eta'%(lep_name, index), attribute = lep_getter("eta", index, abs_pdg),
##              binning=[30,-3,3],
##            ))
##            plots.append(Plot(
##              texX = '#phi(%s_{%i}) (GeV)'%(lep_name, index), texY = 'Number of Events',
##              name = '%s%i_phi'%(lep_name, index), attribute = lep_getter("phi", index, abs_pdg),
##              binning=[30,-pi,pi],
##            ))
##            plots.append(Plot(
##              texX = 'dxy(%s_{%i}) (GeV)'%(lep_name, index), texY = 'Number of Events',
##              name = '%s%i_dxy'%(lep_name, index), attribute = lep_getter("dxy", index, abs_pdg, functor = lambda x: abs(x)),
##              binning=[50,0,0.05],
##            ))
##            plots.append(Plot(
##              texX = 'dz(%s_{%i}) (GeV)'%(lep_name, index), texY = 'Number of Events',
##              name = '%s%i_dz'%(lep_name, index), attribute = lep_getter("dz", index, abs_pdg, functor = lambda x: abs(x)),
##              binning=[50,0,0.05],
##            ))
##            plots.append(Plot(
##              texX = 'IP_{3D}(%s_{%i}) (GeV)'%(lep_name, index), texY = 'Number of Events',
##              name = '%s%i_ip3d'%(lep_name, index), attribute = lep_getter("ip3d", index, abs_pdg, functor = lambda x: abs(x)),
##              binning=[50,0,0.05],
##            ))
##            plots.append(Plot(
##              texX = '#sigma(IP)_{3D}(%s_{%i}) (GeV)'%(lep_name, index), texY = 'Number of Events',
##              name = '%s%i_sip3d'%(lep_name, index), attribute = lep_getter("sip3d", index, abs_pdg, functor = lambda x: abs(x)),
##              binning=[40,0,8],
##            ))
##            plots.append(Plot(
##              texX = 'jetRelIso(%s_{%i}) (GeV)'%(lep_name, index), texY = 'Number of Events',
##              name = '%s%i_jetRelIso'%(lep_name, index), attribute = lep_getter("jetRelIso", index, abs_pdg),
##              binning=[50,-.15,0.5],
##            ))
##            plots.append(Plot(
##              texX = 'miniPFRelIso_all(%s_{%i}) (GeV)'%(lep_name, index), texY = 'Number of Events',
##              name = '%s%i_miniPFRelIso_all'%(lep_name, index), attribute = lep_getter("miniPFRelIso_all", index, abs_pdg),
##              binning=[50,0,.5],
##            ))
##            plots.append(Plot(
##              texX = 'pfRelIso03_all(%s_{%i}) (GeV)'%(lep_name, index), texY = 'Number of Events',
##              name = '%s%i_pfRelIso03_all'%(lep_name, index), attribute = lep_getter("pfRelIso03_all", index, abs_pdg),
##              binning=[50,0,.5],
##            ))
##            # plots.append(Plot(
##            #   texX = 'mvaTTH(%s_{%i}) (GeV)'%(lep_name, index), texY = 'Number of Events',
##            #   name = '%s%i_mvaTTH'%(lep_name, index), attribute = lep_getter("mvaTTH", index, abs_pdg),
##            #   binning=[24,-1.2,1.2],
##            # ))


    plotting.fill(plots, read_variables = read_variables, sequence = sequence, ttreeFormulas = ttreeFormulas)

    #set colors and text to samples
    for plot in plots:
	for i_eft, eft in enumerate(eft_configs):
				plot.histos[i_eft][0].legendText = eft['text']
				#plot.histos[i_eft][0].style      = styles.lineStyle(eft['color'],width=2)
				plot.histos[i_eft][0].style      = styles.errorStyle(eft['color'])
				plot.histos[i_eft][0].SetName(eft['name'])

    #Get normalization yields from yield histogram
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

    #yields[mode]["data"] = 0
    yields[mode]["MC"] = sum(yields[mode][s.name] for s in mc)
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
