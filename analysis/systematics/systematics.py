#!/usr/bin/env python
''' Analysis script for standard plots
'''

#Standard imports and batch mode

import ROOT, os
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

#Argument Parser

import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',       action='store',      default='INFO', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--small',          action='store_true', default=False,       help='Run only on a small subset of the data?')
argParser.add_argument('--noData',         action='store_true', default=False,       help='Do not plot data.')
argParser.add_argument('--dataMCScaling',  action='store_true',                      help='Data MC scaling?')
argParser.add_argument('--plot_directory', action='store',      default='4t')
argParser.add_argument('--selection',      action='store',      default='trg-dilepL-minDLmass20-offZ1-njet4p-btag2p-ht500')
argParser.add_argument('--sys',            action='store',      default='central')
args = argParser.parse_args()

#Directory naming parser options

if args.noData: args.plot_directory += "_noData"
if args.small: args.plot_directory += "_small"

#Logger

import tttt.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)


# Possible Syst variations
variations = ['LeptonSFDown', 
              'LeptonSFUp',
              'PUDown',
              'PUUp',
              'L1PrefireDown',
              'L1PrefireUp',
              #'TriggerDown',
              #'TriggerUp',
              'BTagSFJesDown', 
              'BTagSFJesUp',
              'BTagSFHfDown',
              'BTagSFHfUp',
              'BTagSFLfDown',
              'BTagSFLfUp',
              'BTagSFHfs1Down',
              'BTagSFHfs1Up',
              'BTagSFLfs1Down',
              'BTagSFLfs1Up',
              'BTagSFHfs2Down',
              'BTagSFHfs2Up',
              'BTagSFLfs2Down',
              'BTagSFLfs2Up',
              'BTagSFCfe1Down',
              'BTagSFCfe1Up',
              'BTagSFCfe2Down',
              'BTagSFCfe2Up',
	      'noTopPtReweight',
	      'HDampUp',
	      'HDampDown',
             ]

jesUncertainties = [
    "Total",
    "AbsoluteMPFBias",
    "AbsoluteScale",
    "AbsoluteStat",
    "RelativeBal",
    "RelativeFSR",
    "RelativeJEREC1",
    "RelativeJEREC2",
    "RelativeJERHF",
    "RelativePtBB",
    "RelativePtEC1",
    "RelativePtEC2",
    "RelativePtHF",
    "RelativeStatEC",
    "RelativeStatFSR",
    "RelativeStatHF",
    "PileUpDataMC",
    "PileUpPtBB",
    "PileUpPtEC1",
    "PileUpPtEC2",
    "PileUpPtHF",
    "PileUpPtRef",
    "FlavorQCD",
    "Fragmentation",
    "SinglePionECAL",
    "SinglePionHCAL",
    "TimePtEta",
]
    
nPDFs = 101
PDFWeights = ["PDF_%s"%i for i in range(1,nPDFs)]

scaleWeights = ["ScaleDownDown", "ScaleDownNone", "ScaleNoneDown", "ScaleNoneUp", "ScaleUpNone", "ScaleUpUp"]

PSWeights = ["ISRUp", "ISRDown", "FSRUp", "FSRDown"]

jetVariations= ["jes%s%s"%(var, upOrDown) for var in jesUncertainties for upOrDown in ["Up","Down"]]

variations = variations + jetVariations + scaleWeights + PSWeights + PDFWeights

# Check if we know the variation if not central don't use data!
if args.sys not in variations:
    if args.sys == "central":
        logger.info( "Running central samples (no sys variation)")
    else:
        raise RuntimeError( "Variation %s not among the known: %s", args.sys, ",".join( variations ) )
else:
    logger.info( "Running sys variation %s, noData is set to 'True'", args.sys)
    args.noData = True

if args.noData:
    logger.info( "Running without data")
else:
    logger.info( "Data included in analysis cycle")



#Simulated samples
from tttt.samples.nano_private_UL20_RunII_postProcessed_dilep import *
# Split dileptonic TTBar into three different contributions
# Use the hdamp samples for this variation
if not args.sys == "HDampUp" or args.sys == "HDampDown" :
    sample_TTLep = TTLep
elif args.sys == "HDampUp":
    sample_TTLep = TTLepHUp
elif args.sys == "HDampDown":
    sample_TTLep = TTLepHDown

if not args.sys == "HDampUp" or args.sys == "HDampDown" :
    TTLep_bb    = copy.deepcopy( TTbb )
elif args.sys == "HDampUp":
    TTLep_bb    = copy.deepcopy( TTbbHUp )
elif args.sys == "HDampDown":
    TTLep_bb    = copy.deepcopy( TTbbHDown )

# genTtbarId classification: https://github.com/cms-top/cmssw/blob/topNanoV6_from-CMSSW_10_2_18/TopQuarkAnalysis/TopTools/plugins/GenTtbarCategorizer.cc
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

#Merge simulated background samples
mc = [ TTLep_bb, TTLep_cc, TTLep_other, ST_tch, ST_twch, TTW, TTH, TTZ, TTTT, DY_inclusive, DiBoson]
#Add the data
if not args.noData:
    from tttt.samples.nano_private_UL20_RunII_postProcessed_dilep import RunII
    data_sample = RunII
    data_sample.name = "data"
    all_samples = mc +  [data_sample]
else:
    all_samples = mc

#Luminosity scaling. Here we compute the scaling of the simulation to the data luminosity (event.weight corresponds to 1/fb for simulation, hence we divide the data lumi in pb^-1 by 1000)

lumi_scale = 137. if args.noData else data_sample.lumi/1000.

for sample in mc:
    sample.scale  = 1

if args.small:
    if not args.noData:
        data_sample.reduceFiles( factor = 100 )
    for sample in mc :
        sample.normalization = 1.
        sample.reduceFiles( to = 1 )
        sample.scale /= sample.normalization


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
                 'neHEF/F' ]

if args.sys in jetVariations:
  jetVars += ["pt_"+args.sys+"/F"]

jetVarNames     = [x.split('/')[0] for x in jetVars]

#Read variables (data & MC)

read_variables += [
    "weight/F", "year/I", "met_pt/F", "met_phi/F", "nBTag/I", "nJetGood/I", "PV_npvsGood/I", #"event/l", "run/I", "luminosityBlock/I",
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
    'reweightBTagSF_central/F', 'reweightPU/F', 'reweightL1Prefire/F', 'reweightLeptonSF/F', 'reweightTrigger/F', 'reweightTopPt/F',
    "PDF[Weight/F]","nPDF/I","PS[Weight/F]","nPS/I","scale[Weight/F]","nscale/I",
    "GenJet[pt/F,eta/F,phi/F,partonFlavour/I,hadronFlavour/i]"
    ]
sequence = []

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
classes = [ts.name for ts in config.training_samples]

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
sequence.append( keras_predict )

#Jet Selection modifier
def jetSelectionModifier( sys, returntype = "func"):
  variiedJetObservables = ['nJetGood', 'nBTag', 'ht']
  if returntype == "func":
    def changeCut_( string ):
      for s in variiedJetObservables:
        string = string.replace(s, s+'_'+sys)
        return changeCut_
  elif returntype == "list":
    list = []
    for v in variiedJetObservables:
      string = v+'_'+sys
      list.append(string)    
    return list

#Add a selection selection Modifier
if args.sys in jetVariations:
    selectionModifier = jetSelectionModifier(args.sys)
    read_variables_MC += ["nJetGood_"+args.sys+"/I","nBTag_"+args.sys+"/I","ht_"+args.sys+"/F"]
else:
    selectionModifier = None


def make_jets( event, sample ):
    event.jets  = [getObjDict(event, 'JetGood_', jetVarNames, i) for i in range(int(event.nJetGood))]
    event.bJets = filter(lambda j:isBJet(j, year=event.year) and abs(j['eta'])<=2.4    , event.jets)

sequence.append( make_jets )

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


#get each theory uncertainty reweight

def getTheorySystematics(event,sample):
    if args.sys in scaleWeights:
	 WhichWay9 = {"ScaleDownDown": 	0, 
		      "ScaleDownNone": 	1, 
		      "ScaleNoneDown": 	3, 
		      "ScaleNoneUp":	5, 
		      "ScaleUpNone":	7, 
		      "ScaleUpUp":	8,
			 }
	 WhichWay8 = {"ScaleDownDown": 	0, 
		      "ScaleDownNone": 	1, 
		      "ScaleNoneDown": 	3, 
		      "ScaleNoneUp":	4, 
		      "ScaleUpNone":	6, 
		      "ScaleUpUp":	7,
			 }
	 if event.nscale == 9 : event.reweightScale = event.scale_Weight[WhichWay9[args.sys]]
	 elif event.nscale == 8 : event.reweightScale = event.scale_Weight[WhichWay8[args.sys]]
 	 else: print "Unexpected number of Scale weights!" 
	 #print "We are at scale weight number:" , WhichWay9[args.sys]
    else:event.reweightScale = 1.0

    if args.sys in PDFWeights:
	 WhichOne = int(args.sys.split("_")[1])
	 #print WhichOne
	 if WhichOne == -1 or WhichOne > event.nPDF-1:
		         print "PDF index out of range!"
	 event.reweightPDF = event.PDF_Weight[WhichOne]
	 #print "we are at PDF weight"
    else:event.reweightPDF = 1.0

    if args.sys in PSWeights:
	 WhichSide = {	"ISRUp": 	0,
			"FSRUp":	1,
			"ISRDown": 	2,
			"FSRDown": 	3,
			}
	 event.reweightPS = event.PS_Weight[WhichSide[args.sys]]
	 print WhichSide[args.sys]
	 #print "We have the PS weight:",event.PS_Weight[WhichSide[args.sys]]
    else:event.reweightPS = 1.0 

sequence.append( getTheorySystematics )

#TTree formulas

if args.sys in jetVariations:
  ttreeFormulas = {"ht_"+args.sys :"Sum$(JetGood_pt_"+args.sys+")"}
else: ttreeFormulas = {} 

##list all the reweights FIXME
weightnames = ['reweightLeptonSF', 'reweightBTagSF_central', 'reweightPU', 'reweightL1Prefire', 'reweightTrigger']
if not args.sys == "noTopPtReweight": weightnames += ['reweightTopPt']
weightnames += ['reweightScale','reweightPS','reweightPDF']


sys_weights = {
        'LeptonSFDown'  : ('reweightLeptonSF','reweightLeptonSFDown'),
        'LeptonSFUp'    : ('reweightLeptonSF','reweightLeptonSFUp'),
        'BTagSFJesUp'   : ('reweightBTagSF_central','reweightBTagSF_up_jes'),
        'BTagSFJesDown' : ('reweightBTagSF_central','reweightBTagSF_down_jes'),
        'BTagSFHfDown'  : ('reweightBTagSF_central','reweightBTagSF_down_hf'),
        'BTagSFHfUp'    : ('reweightBTagSF_central','reweightBTagSF_up_hf'),
        'BTagSFLfdown'  : ('reweightBTagSF_central','reweightBTagSF_down_lf'),
        'BTagSFLfUp'    : ('reweightBTagSF_central','reweightBTagSF_up_lf'),
        'BTagSFHfs1Down': ('reweightBTagSF_central','reweightBTagSF_down_hfstats1'),
        'BTagSFHfs1Up'  : ('reweightBTagSF_central','reweightBTagSF_up_hfstats1'),
        'BTagSFLfs1Down': ('reweightBTagSF_central','reweightBTagSF_down_lfstats1'),
        'BTagSFLfs1Up'  : ('reweightBTagSF_central','reweightBTagSF_up_lfstats1'),
        'BTagSFHfs2Down': ('reweightBTagSF_central','reweightBTagSF_down_hfstats2'),
        'BTagSFHfs2Up'  : ('reweightBTagSF_central','reweightBTagSF_up_hfstats2'),
        'BTagSFLfs2Down': ('reweightBTagSF_central','reweightBTagSF_down_lfstats2'),
        'BTagSFLfs2Up'  : ('reweightBTagSF_central','reweightBTagSF_up_lfstats2'),
        'BTagSFCfe1Down': ('reweightBTagSF_central','reweightBTagSF_Down_cferr1'),
        'BTagSFCfe1Up'  : ('reweightBTagSF_central','reweightBTagSF_up_cferr1'),
        'BTagSFCfe2Down': ('reweightBTagSF_central','reweightBTagSF_Down_cferr2'),
        'BTagSFCfe2Up'  : ('reweightBTagSF_central','reweightBTagSF_up_cferr2'),
        'L1PrefireUp'   : ('reweightL1Prefire','reweightL1PrefireUp'),
        'L1PrefireDown' : ('reweightL1Prefire','reweightL1PrefireDown'),
        'TriggerUp'     : ('reweightTrigger','reweightTriggerUp'),
        'TriggerDown'   : ('reweightTrigger','reweightTriggerDown')
    }

if args.sys in sys_weights:
    oldname, newname = sys_weights[args.sys]
    for i, weight in enumerate(weightnames):
        if weight == oldname:
          weightnames[i] = newname
          read_variables_MC += ['%s/F'%(newname)]


if args.sys in jetVariations:
    if "Up" in args.sys:
      oldname, newname = sys_weights['BTagSFJesUp']
    elif "Down" in args.sys:
      oldname, newname = sys_weights['BTagSFJesDown']
    for i, weight in enumerate(weightnames):
        if weight == oldname:
          weightnames[i] = newname
          read_variables_MC += ['%s/F'%(newname)]


yields     = {}
allPlots   = {}
allModes   = ['mumu','mue', 'ee']
for i_mode, mode in enumerate(allModes):
    yields[mode] = {}

    #Calculate the reweight
    getters = map( operator.attrgetter, weightnames)
    def weight_function( event, sample):
        # Calculate weight, this becomes: w = event.weightnames[0]*event.weightnames[1]*...
        w = reduce(operator.mul, [g(event) for g in getters], 1)
        return w

    # This weight goes to the plot - do not reweight the sample with it
    weight_ = lambda event, sample: event.weight if sample.isData else event.weight

    #Plot styling
    for sample in mc: sample.style = styles.fillStyle(sample.color)
    if not args.noData:
        data_sample.style = styles.errorStyle( ROOT.kBlack )

    #Apply reweighting to MC for specific detector effects
    for sample in mc:
      sample.read_variables = read_variables_MC
      sample.weight = weight_function


    #Stack : Define what we want to see.
    if not args.noData:
        stack = Stack(mc, [data_sample])
    else:
        stack = Stack(mc)

    # Define everything we want to have common to all plots
    selection_string = selectionModifier(cutInterpreter.cutString(args.selection)) if selectionModifier is not None else cutInterpreter.cutString(args.selection) 
    Plot.setDefaults(stack = stack, weight = staticmethod(weight_), selectionString = "("+getLeptonSelection(mode)+")&&("+selection_string+")")

    plots = []

    #Yeld plot
    plots.append(Plot(
      name = 'yield', texX = '', texY = 'Number of Events',
      attribute = lambda event, sample: 0.5 + i_mode,
      binning=[3, 0, 3],
    ))

    for model in models:
        for class_ in model['classes']:
            if "TTTT" in class_ : plot_name = "2l_4t"
            if "TTLep_bb" in class_ : plot_name = "2l_ttbb"
            if "TTLep_cc" in class_: plot_name = "2l_ttcc"
            if "TTLep_other" in class_: plot_name = "2l_ttlight"
            model_name = model['name']+'_'+class_
            plots.append(Plot(
                name = plot_name,
                texX = model_name, texY = 'Number of Events',
                attribute = lambda event, sample, model_name=model_name: getattr(event, model_name),#if event.nJetGood> 5 and event.nJetGood < 7 else float('nan') ,
                binning=[10,0,1],
                addOverFlowBin='upper',
            ))

    for model in models:
        for class_ in model['classes']:
            if "TTTT" in class_ : plot_name = "2l_4t"
            if "TTLep_bb" in class_ : plot_name = "2l_ttbb"
            if "TTLep_cc" in class_: plot_name = "2l_ttcc"
            if "TTLep_other" in class_: plot_name = "2l_ttlight"
            model_name = model['name']+'_'+class_
            plots.append(Plot(
                name = plot_name+"_course",
                texX = model_name, texY = 'Number of Events',
                attribute = lambda event, sample, model_name=model_name: getattr(event, model_name),#if event.nJetGood> 5 and event.nJetGood < 7 else float('nan') ,
                binning=Binning.fromThresholds([0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.82,0.84,0.86,0.88,0.90,0.92,0.94,0.96,0.98,1.0]),
                addOverFlowBin='upper',
            ))

    plots.append(Plot( name = 'Btagging_discriminator_value_l1' , texX = 'DeepB l1' , texY = 'Number of Events',
        attribute = lambda event, sample: event.JetGood_btagDeepFlavB[0],
        binning = [20,0,1],
    ))

    plots.append(Plot(
      name = 'nVtxs', texX = 'vertex multiplicity', texY = 'Number of Events',
      attribute = TreeVariable.fromString( "PV_npvsGood/I" ),
      binning=[50,0,50],
      addOverFlowBin='upper',
    ))

    plots.append(Plot(
        name = 'l1_pt',
        texX = 'p_{T}(l_{1}) (GeV)', texY = 'Number of Events / 20 GeV',
        attribute = lambda event, sample:event.l1_pt,
        binning=[15,0,300],
        addOverFlowBin='upper',
    ))

    plots.append(Plot(
        name = 'l1_eta',
        texX = '#eta(l_{1})', texY = 'Number of Events',
        attribute = lambda event, sample: event.l1_eta,
        binning=[20,-3,3],
    ))

    plots.append(Plot(
        name = 'l1_mvaTOP',
        texX = 'MVA_{TOP}(l_{1})', texY = 'Number of Events',
        attribute = lambda event, sample: event.l1_mvaTOP,
        binning=[20,-1,1],
    ))

    plots.append(Plot(
        name = 'l1_mvaTOPWP',
        texX = 'MVA_{TOP}(l_{1}) WP', texY = 'Number of Events',
        attribute = lambda event, sample: event.l1_mvaTOPWP,
        binning=[5,0,5],
    ))

    plots.append(Plot(
        name = 'l2_pt',
        texX = 'p_{T}(l_{2}) (GeV)', texY = 'Number of Events / 20 GeV',
        attribute = lambda event, sample:event.l2_pt,
        binning=[15,0,300],
        addOverFlowBin='upper',
    ))

    plots.append(Plot(
        name = 'l2_eta',
        texX = '#eta(l_{2})', texY = 'Number of Events',
        attribute = lambda event, sample: event.l2_eta,
        binning=[20,-3,3],
    ))

    plots.append(Plot(
        name = 'l2_mvaTOP',
        texX = 'MVA_{TOP}(l_{2})', texY = 'Number of Events',
        attribute = lambda event, sample: event.l2_mvaTOP,
        binning=[20,-1,1],
    ))

    plots.append(Plot(
        name = 'l2_mvaTOPWP',
        texX = 'MVA_{TOP}(l_{1}) WP', texY = 'Number of Events',
        attribute = lambda event, sample: event.l2_mvaTOPWP,
        binning=[5,0,5],
    ))

    plots.append(Plot(
        texX = 'E_{T}^{miss} (GeV)', texY = 'Number of Events / 20 GeV',
        attribute = TreeVariable.fromString( "met_pt/F" ),
        binning=[400/20,0,400],
        addOverFlowBin='upper',
    ))

    plots.append(Plot(
        texX = '#phi(E_{T}^{miss})', texY = 'Number of Events / 20 GeV',
        attribute = TreeVariable.fromString( "met_phi/F" ),
        binning=[10,-pi,pi],
    ))

    plots.append(Plot(
        name = "Z1_pt",
        texX = 'p_{T}(Z_{1}) (GeV)', texY = 'Number of Events / 20 GeV',
        attribute = TreeVariable.fromString( "Z1_pt/F" ),
        binning=[20,0,400],
        addOverFlowBin='upper',
    ))

    plots.append(Plot(
        name = 'Z1_pt_coarse', texX = 'p_{T}(Z_{1}) (GeV)', texY = 'Number of Events / 50 GeV',
        attribute = TreeVariable.fromString( "Z1_pt/F" ),
        binning=[16,0,800],
        addOverFlowBin='upper',
    ))

    plots.append(Plot(
        name = 'Z1_pt_superCoarse', texX = 'p_{T}(Z_{1}) (GeV)', texY = 'Number of Events',
        attribute = TreeVariable.fromString( "Z1_pt/F" ),
        binning=[3,0,600],
        addOverFlowBin='upper',
    ))

    plots.append(Plot(
      texX = 'p_{T}(leading l) (GeV)', texY = 'Number of Events / 20 GeV',
      name = 'lep1_pt', attribute = lambda event, sample: event.lep_pt[0],
      binning=[400/20,0,400],
    ))

    plots.append(Plot(
      texX = 'p_{T}(subleading l) (GeV)', texY = 'Number of Events / 10 GeV',
      name = 'lep2_pt', attribute = lambda event, sample: event.lep_pt[1],
      binning=[200/10,0,200],
    ))

    plots.append(Plot(
      texX = 'p_{T}(trailing l) (GeV)', texY = 'Number of Events / 10 GeV',
      name = 'lep3_pt', attribute = lambda event, sample: event.lep_pt[2],
      binning=[150/10,0,150],
    ))
    plots.append(Plot(
        texX = 'M(ll) (GeV)', texY = 'Number of Events / 20 GeV',
        attribute = TreeVariable.fromString( "Z1_mass/F" ),
        binning=[10,81,101],
        addOverFlowBin='upper',
    ))

    plots.append(Plot(
        name = "Z1_mass_wide",
        texX = 'M(ll) (GeV)', texY = 'Number of Events / 2 GeV',
        attribute = TreeVariable.fromString( "Z1_mass/F" ),
        binning=[50,20,120],
        addOverFlowBin='upper',
    ))

    plots.append(Plot(
        name = "Z1_cosThetaStar", texX = 'cos#theta(l-)', texY = 'Number of Events / 0.2',
        attribute = lambda event, sample:event.Z1_cosThetaStar,
        binning=[10,-1,1],
    ))

    plots.append(Plot(
        name = "Z2_mass_wide",
        texX = 'M(ll) of 2nd OSDL pair', texY = 'Number of Events / 2 GeV',
        attribute = TreeVariable.fromString( "Z2_mass/F" ),
        binning=[60,0,120],
        addOverFlowBin='upper',
    ))

    plots.append(Plot(
        name = "minDLmass",
        texX = 'min mass of all DL pairs', texY = 'Number of Events / 2 GeV',
        attribute = TreeVariable.fromString( "minDLmass/F" ),
        binning=[60,0,120],
        addOverFlowBin='upper',
    ))

    plots.append(Plot(
        texX = '#Delta#phi(Z_{1}(ll))', texY = 'Number of Events',
        attribute = TreeVariable.fromString( "Z1_lldPhi/F" ),
        binning=[10,0,pi],
    ))

    plots.append(Plot(
        texX = '#Delta R(Z_{1}(ll))', texY = 'Number of Events',
        attribute = TreeVariable.fromString( "Z1_lldR/F" ),
        binning=[10,0,6],
    ))

    plots.append(Plot(
      texX = 'N_{jets}', texY = 'Number of Events',
      attribute = TreeVariable.fromString( "nJetGood/I" ), #nJetSelected
      binning=[8,3.5,11.5],
    ))

    plots.append(Plot(
      texX = 'N_{b-tag}', texY = 'Number of Events',
      attribute = TreeVariable.fromString( "nBTag/I" ), #nJetSelected
      binning=[5, 1.5,6.5],
    ))

    plots.append(Plot(
      texX = 'H_{T} (GeV)', texY = 'Number of Events / 30 GeV',
      name = 'ht', attribute = lambda event, sample: sum( j['pt'] for j in event.jets ),
      binning=[1500/50,0,1500],
    ))

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

    for index in range(2):
        for abs_pdg in [11, 13]:
            lep_name = "mu" if abs_pdg==13 else "ele"
            plots.append(Plot(
              texX = 'p_{T}(%s_{%i}) (GeV)'%(lep_name, index), texY = 'Number of s',
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
            plots.append(Plot(
              texX = 'dxy(%s_{%i}) (GeV)'%(lep_name, index), texY = 'Number of Events',
              name = '%s%i_dxy'%(lep_name, index), attribute = lep_getter("dxy", index, abs_pdg, functor = lambda x: abs(x)),
              binning=[50,0,0.05],
            ))
            plots.append(Plot(
              texX = 'dz(%s_{%i}) (GeV)'%(lep_name, index), texY = 'Number of Events',
              name = '%s%i_dz'%(lep_name, index), attribute = lep_getter("dz", index, abs_pdg, functor = lambda x: abs(x)),
              binning=[50,0,0.05],
            ))
            plots.append(Plot(
              texX = 'IP_{3D}(%s_{%i}) (GeV)'%(lep_name, index), texY = 'Number of Events',
              name = '%s%i_ip3d'%(lep_name, index), attribute = lep_getter("ip3d", index, abs_pdg, functor = lambda x: abs(x)),
              binning=[50,0,0.05],
            ))
            plots.append(Plot(
              texX = '#sigma(IP)_{3D}(%s_{%i}) (GeV)'%(lep_name, index), texY = 'Number of Events',
              name = '%s%i_sip3d'%(lep_name, index), attribute = lep_getter("sip3d", index, abs_pdg, functor = lambda x: abs(x)),
              binning=[40,0,8],
            ))
            plots.append(Plot(
              texX = 'jetRelIso(%s_{%i}) (GeV)'%(lep_name, index), texY = 'Number of Events',
              name = '%s%i_jetRelIso'%(lep_name, index), attribute = lep_getter("jetRelIso", index, abs_pdg),
              binning=[50,-.15,0.5],
            ))
            plots.append(Plot(
              texX = 'miniPFRelIso_all(%s_{%i}) (GeV)'%(lep_name, index), texY = 'Number of Events',
              name = '%s%i_miniPFRelIso_all'%(lep_name, index), attribute = lep_getter("miniPFRelIso_all", index, abs_pdg),
              binning=[50,0,.5],
            ))
            plots.append(Plot(
              texX = 'pfRelIso03_all(%s_{%i}) (GeV)'%(lep_name, index), texY = 'Number of Events',
              name = '%s%i_pfRelIso03_all'%(lep_name, index), attribute = lep_getter("pfRelIso03_all", index, abs_pdg),
              binning=[50,0,.5],
            ))
            # plots.append(Plot(
            #   texX = 'mvaTTH(%s_{%i}) (GeV)'%(lep_name, index), texY = 'Number of Events',
            #   name = '%s%i_mvaTTH'%(lep_name, index), attribute = lep_getter("mvaTTH", index, abs_pdg),
            #   binning=[24,-1.2,1.2],
            # ))
#            plots.append(Plot(
#              texX = 'mvaTOP(%s_{%i}) (GeV)'%(lep_name, index), texY = 'Number of Events',
#              name = '%s%i_mvaTOP'%(lep_name, index), attribute = lep_getter("mvaTOP", index, abs_pdg),
#              binning=[24,-1.2,1.2],
#            ))
            plots.append(Plot(
              texX = 'charge(%s_{%i}) (GeV)'%(lep_name, index), texY = 'Number of Events',
              name = '%s%i_charge'%(lep_name, index), attribute = lep_getter("pdgId", index, abs_pdg, functor = charge),
              binning=[3,-1,2],
            ))
            if lep_name == "mu":
                plots.append(Plot(
                  texX = 'segmentComp(%s_{%i}) (GeV)'%(lep_name, index), texY = 'Number of Events',
                  name = '%s%i_segmentComp'%(lep_name, index), attribute = lep_getter("segmentComp", index, abs_pdg),
                  binning=[50,0,1],
                ))
                plots.append(Plot(
                  texX = 'nStations(%s_{%i}) (GeV)'%(lep_name, index), texY = 'Number of Events',
                  name = '%s%i_nStations'%(lep_name, index), attribute = lep_getter("nStations", index, abs_pdg),
                  binning=[10,0,10],
                ))
                plots.append(Plot(
                  texX = 'nTrackerLayers(%s_{%i}) (GeV)'%(lep_name, index), texY = 'Number of Events',
                  name = '%s%i_nTrackerLayers'%(lep_name, index), attribute = lep_getter("nTrackerLayers", index, abs_pdg),
                  binning=[20,0,20],
                ))
            if lep_name == "ele":
                for cbIdFlag in vidNestedWPBitMapNamingList:
                    plots.append(Plot(
                      texX = '%s(%s_{%i}) (GeV)'%(cbIdFlag, lep_name, index), texY = 'Number of Events',
                      name = '%s%i_%s_Flag'%(lep_name, index, cbIdFlag), attribute = lep_getter("vidNestedWPBitmap", index, abs_pdg, functor = cbEleIdFlagGetter(cbIdFlag)),
                      binning=[5,0,5],
                ))


    if args.sys in jetVariations:

      plots.append(Plot(
        texX = 'N_{jets}_'+args.sys, texY = 'Number of Events',
        attribute = TreeVariable.fromString( "nJetGood_"+args.sys+"/I" ), #nJet varied 
        binning=[8,3.5,11.5],
      )) 

      plots.append(Plot(
        texX = 'N_{b-tag}_'+args.sys, texY = 'Number of Events',
        attribute = TreeVariable.fromString( "nBTag_"+args.sys+"/I" ), #nJetSelected
        binning=[5, 1.5,6.5],
      ))

      plots.append(Plot(
        texX = 'H_{T} (GeV)_'+args.sys, texY = 'Number of Events / 30 GeV',
        name = 'ht_'+args.sys, attribute = TreeVariable.fromString( "ht_"+args.sys+"/F" ),
        binning=[1500/50,0,1500],
      ))

    plotting.fill(plots, read_variables = read_variables, sequence = sequence, ttreeFormulas = ttreeFormulas)

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


# Write Result Hist in root file
logger.info( "Now writing results in root file")
plot_dir = os.path.join(plot_directory, 'analysisPlots', args.plot_directory, 'RunII', 'all', args.selection)
if not os.path.exists(plot_dir):
    try:
        os.makedirs(plot_dir)
    except:
        print 'Could not create', plot_dir
outfilename = plot_dir+'/tttt_'+args.sys+'.root'
logger.info( "Saving in %s", outfilename )
outfile = ROOT.TFile(outfilename, 'recreate')
outfile.cd()
for plot in allPlots[allModes[0]]:
    for idx, histo_list in enumerate(plot.histos):
        for j, h in enumerate(histo_list):
            histname = h.GetName()
            if "TTLep_bb" in histname: process = "TTLep_bb"
            elif "TTLep_cc" in histname: process = "TTLep_cc"
            elif "TTLep_other" in histname: process = "TTLep_other"
            elif "ST_tch" in histname: process = "ST_tch"
	    elif "ST_twch" in histname: process = "ST_twch"
            elif "TTW" in histname: process = "TTW"
            elif "TTZ" in histname: process = "TTZ"
            elif "TTH" in histname: process = "TTH"
   	    elif "DY" in histname: process = "DY"
    	    elif "DiBoson" in histname: process = "DiBoson"
            elif "data" in histname: process = "data"
	    elif "TTTT" in histname: process = "TTTT"
            h.Write(plot.name+"__"+process)
outfile.Close()


logger.info( "Done with prefix %s and selectionString %s", args.selection, cutInterpreter.cutString(args.selection) )
