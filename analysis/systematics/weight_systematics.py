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

#tttt

from tttt.Tools.user                     import plot_directory
from tttt.Tools.cutInterpreter           import cutInterpreter
from tttt.Tools.objectSelection          import lepString, cbEleIdFlagGetter, vidNestedWPBitMapNamingList, isBJet
from tttt.Tools.helpers                  import getObjDict

#Analysis Tools
from Analysis.Tools.helpers              import deltaPhi, deltaR
import Analysis.Tools.syncer

#Argument Parser
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',       action='store',      default='INFO', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--small',          action='store_true', default=False,       help='Run only on a small subset of the data?')
argParser.add_argument('--plot_directory', action='store',      default='4t')
argParser.add_argument('--selection',      action='store',      default='trg-dilepL-minDLmass20-offZ1-njet4p-btag2p-ht500')
argParser.add_argument('--era',            action='store',      default='RunII', type=str,                help="Which era?" )
args = argParser.parse_args()

#Directory naming parser options

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

nPDFs = 101
PDFWeights = ["PDF_%s"%i for i in range(1,nPDFs)]

scaleWeights = ["ScaleDownDown", "ScaleDownNone", "ScaleNoneDown", "ScaleNoneUp", "ScaleUpNone", "ScaleUpUp"]

PSWeights = ["ISRUp", "ISRDown", "FSRUp", "FSRDown"]

variations += scaleWeights + PSWeights + PDFWeights

if args.era == '2016_preVFP':
        from tttt.samples.nano_mc_private_UL20_Summer16_preVFP_postProcessed_dilep import *
elif args.era == '2016':
        from tttt.samples.nano_mc_private_UL20_Summer16_postProcessed_dilep import *
elif args.era == '2017':
        from tttt.samples.nano_mc_private_UL20_Fall17_postProcessed_dilep import *
elif args.era == '2018':
        from tttt.samples.nano_mc_private_UL20_Autumn18_postProcessed_dilep import *
elif args.era == 'RunII':
        from tttt.samples.nano_private_UL20_RunII_postProcessed_dilep import *
else:
    raise Exception("Era %s not known"%args.era)

# genTtbarId classification: https://github.com/cms-top/cmssw/blob/topNanoV6_from-CMSSW_10_2_18/TopQuarkAnalysis/TopTools/plugins/GenTtbarCategorizer.cc
TTLep_bb    = copy.deepcopy(TTbb)
TTLep_bb.name = "TTLep_bb"
TTLep_bb.texName = "t#bar{t}b#bar{b}"
TTLep_bb.color   = ROOT.kRed + 2
TTLep_bb.setSelectionString( "genTtbarId%100>=50" )
TTLep_cc    = copy.deepcopy( TTLep )
TTLep_cc.name = "TTLep_cc"
TTLep_cc.texName = "t#bar{t}c#bar{c}"
TTLep_cc.color   = ROOT.kRed - 3
TTLep_cc.setSelectionString( "genTtbarId%100>=40&&genTtbarId%100<50" )
TTLep_other = copy.deepcopy( TTLep )
TTLep_other.name = "TTLep_other"
TTLep_other.texName = "t#bar{t} + light j."
TTLep_other.setSelectionString( "genTtbarId%100<40" )

#Merge simulated background samples
all_samples = [ TTLep_bb, TTLep_cc, TTLep_other, ST_tch, ST_twch, TTW, TTH, TTZ, TTTT, DY_inclusive, DiBoson]

if args.small:
    for sample in all_samples:
        sample.normalization = 1.
        sample.reduceFiles( to = 1 )
        sample.scale /= sample.normalization

read_variables = []

jetVars     = ['pt/F', 'eta/F', 'phi/F', 'btagDeepFlavB/F', 'btagDeepFlavCvB/F', 'btagDeepFlavQG/F', 'chEmEF/F', 'chHEF/F', 'neEmEF/F', 'neHEF/F', 'index/I']
jetVarNames = [x.split('/')[0] for x in jetVars]

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
    VectorTreeVariable.fromString( "PDF[Weight/F]", nMax=120) , "nPDF/I","PS[Weight/F]","nPS/I","scale[Weight/F]","nscale/I",
    "GenJet[pt/F,eta/F,phi/F,partonFlavour/I,hadronFlavour/i]",
    'reweightLeptonSFDown/F', 'reweightLeptonSFUp/F', 'reweightBTagSF_up_jes/F', 'reweightBTagSF_down_jes/F', 'reweightBTagSF_down_hf/F', 
    'reweightBTagSF_up_hf/F', 'reweightBTagSF_down_lf/F', 'reweightBTagSF_up_lf/F', 'reweightBTagSF_down_hfstats1/F', 
    'reweightBTagSF_up_hfstats1/F', 'reweightBTagSF_down_lfstats1/F', 'reweightBTagSF_up_lfstats1/F', 'reweightBTagSF_down_hfstats2/F', 
    'reweightBTagSF_up_hfstats2/F', 'reweightBTagSF_down_lfstats2/F', 'reweightBTagSF_up_lfstats2/F', 'reweightBTagSF_down_cferr1/F', 
    'reweightBTagSF_up_cferr1/F', 'reweightBTagSF_down_cferr2/F', 'reweightBTagSF_up_cferr2/F', 'reweightL1PrefireUp/F', 'reweightL1PrefireDown/F', 
    'reweightTriggerUp/F', 'reweightTriggerDown/F',
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
sequence.append( keras_predict )

#Let's make a function that provides string-based lepton selection
mu_string  = lepString('mu','VL')
ele_string = lepString('ele','VL')
def getLeptonSelection( mode ):
    if   mode=="mumu": return "Sum$({mu_string})==2&&Sum$({ele_string})==0".format(mu_string=mu_string,ele_string=ele_string)
    elif mode=="mue":  return "Sum$({mu_string})==1&&Sum$({ele_string})==1".format(mu_string=mu_string,ele_string=ele_string)
    elif mode=="ee":   return "Sum$({mu_string})==0&&Sum$({ele_string})==2".format(mu_string=mu_string,ele_string=ele_string)
    elif mode=='all':    return "Sum$({mu_string})+Sum$({ele_string})==2".format(mu_string=mu_string,ele_string=ele_string)

nominal_weights = ['reweightLeptonSF', 'reweightBTagSF_central', 'reweightPU', 'reweightL1Prefire', 'reweightTrigger', 'reweightTopPt']

scaleMap = { 
    9: {
    "ScaleDownDown": 0,
    "ScaleDownNone": 1,
    "ScaleNoneDown": 3,
    "ScaleNoneUp":   5,
    "ScaleUpNone":   7,
    "ScaleUpUp":     8,}, 
    8: {
    "ScaleDownDown": 0,
    "ScaleDownNone": 1,
    "ScaleNoneDown": 3,
    "ScaleNoneUp":   4,
    "ScaleUpNone":   6,
    "ScaleUpUp":     7,}
}

systematics = {
        'LeptonSFDown'  : {'remove':'reweightLeptonSF',      'add':'reweightLeptonSFDown'},
        'LeptonSFUp'    : {'remove':'reweightLeptonSF',      'add':'reweightLeptonSFUp'},
        'BTagSFJesUp'   : {'remove':'reweightBTagSF_central','add':'reweightBTagSF_up_jes'},
        'BTagSFJesDown' : {'remove':'reweightBTagSF_central','add':'reweightBTagSF_down_jes'},
        'BTagSFHfDown'  : {'remove':'reweightBTagSF_central','add':'reweightBTagSF_down_hf'},
        'BTagSFHfUp'    : {'remove':'reweightBTagSF_central','add':'reweightBTagSF_up_hf'},
        'BTagSFLfdown'  : {'remove':'reweightBTagSF_central','add':'reweightBTagSF_down_lf'},
        'BTagSFLfUp'    : {'remove':'reweightBTagSF_central','add':'reweightBTagSF_up_lf'},
        'BTagSFHfs1Down': {'remove':'reweightBTagSF_central','add':'reweightBTagSF_down_hfstats1'},
        'BTagSFHfs1Up'  : {'remove':'reweightBTagSF_central','add':'reweightBTagSF_up_hfstats1'},
        'BTagSFLfs1Down': {'remove':'reweightBTagSF_central','add':'reweightBTagSF_down_lfstats1'},
        'BTagSFLfs1Up'  : {'remove':'reweightBTagSF_central','add':'reweightBTagSF_up_lfstats1'},
        'BTagSFHfs2Down': {'remove':'reweightBTagSF_central','add':'reweightBTagSF_down_hfstats2'},
        'BTagSFHfs2Up'  : {'remove':'reweightBTagSF_central','add':'reweightBTagSF_up_hfstats2'},
        'BTagSFLfs2Down': {'remove':'reweightBTagSF_central','add':'reweightBTagSF_down_lfstats2'},
        'BTagSFLfs2Up'  : {'remove':'reweightBTagSF_central','add':'reweightBTagSF_up_lfstats2'},
        'BTagSFCfe1Down': {'remove':'reweightBTagSF_central','add':'reweightBTagSF_down_cferr1'},
        'BTagSFCfe1Up'  : {'remove':'reweightBTagSF_central','add':'reweightBTagSF_up_cferr1'},
        'BTagSFCfe2Down': {'remove':'reweightBTagSF_central','add':'reweightBTagSF_down_cferr2'},
        'BTagSFCfe2Up'  : {'remove':'reweightBTagSF_central','add':'reweightBTagSF_up_cferr2'},
        'L1PrefireUp'   : {'remove':'reweightL1Prefire',     'add':'reweightL1PrefireUp'},
        'L1PrefireDown' : {'remove':'reweightL1Prefire',     'add':'reweightL1PrefireDown'},
        'TriggerUp'     : {'remove':'reweightTrigger',       'add':'reweightTriggerUp'},
        'TriggerDown'   : {'remove':'reweightTrigger',       'add':'reweightTriggerDown'},
        "noReweightTopPt":{'remove':'reweightTopPt'},
        "ScaleDownDown" : {'add': lambda event, sample: event.scale_Weight[scaleMap[event.nscale]["ScaleDownDown"]]},
        "ScaleDownNone" : {'add': lambda event, sample: event.scale_Weight[scaleMap[event.nscale]["ScaleDownNone"]]},
        "ScaleNoneDown" : {'add': lambda event, sample: event.scale_Weight[scaleMap[event.nscale]["ScaleNoneDown"]]},
        "ScaleNoneUp"   : {'add': lambda event, sample: event.scale_Weight[scaleMap[event.nscale]["ScaleNoneUp"  ]]},
        "ScaleUpNone"   : {'add': lambda event, sample: event.scale_Weight[scaleMap[event.nscale]["ScaleUpNone"  ]]},
        "ScaleUpUp"     : {'add': lambda event, sample: event.scale_Weight[scaleMap[event.nscale]["ScaleUpUp"    ]]},
        "ISRUp"         : {'add': lambda event, sample: event.PS_Weight[0]},
        "FSRUp"         : {'add': lambda event, sample: event.PS_Weight[1]},
        "ISRDown"       : {'add': lambda event, sample: event.PS_Weight[2]},
        "FSRDown"       : {'add': lambda event, sample: event.PS_Weight[3]},
    }

# produces a function that retrieves event.vector[i] if it is not 'nan' else 1.
def getter(i, vector):
    def func( event, sample):
        val = operator.itemgetter(i)(getattr(event, vector))
        if val<float('inf'):
            return val
        else:
            return 1
    return func

# add pdf systematics
for i_pdf in range(1, 100):
    systematics["PDF_%i"%i_pdf] = {'add': getter(i_pdf, "PDF_Weight")}

def evaluate_systematic_weights(event, sample):
    # sanity
    if event.nPDF<101:
        raise RuntimeError
    if event.nscale not in [8,9]:
        raise RuntimeError

    # precompute all the weights we're going to need
    nominal_weight_dict = {weight:operator.attrgetter(weight)(event) for weight in nominal_weights}
    event.sys_weights   = {sys:1.0 for sys in systematics.keys()} 
    for name, sys in systematics.iteritems():

        # Let's make sure you're not trying to remove what isn't there in the first place
        if sys.has_key("remove") and sys["remove"] not in nominal_weights:
            raise RuntimeError( "Can't remove weight %s because it is not in the nominal list" % sys["remove"] )

        # multiply all nominal weights unless they are in 'remove'
        for weight in nominal_weights:
            if not ( sys.has_key('remove') and sys['remove']==weight):
                event.sys_weights[name] *= nominal_weight_dict[weight]
        if sys.has_key('add') and type(sys['add'])==type(""):
            # we have a string
            event.sys_weights[name] *= operator.attrgetter(sys["add"])(event)
        elif sys.has_key('add'):
            # we have a function
            event.sys_weights[name] *= sys["add"](event, sample)

    #print event.sys_weights

sequence.append( evaluate_systematic_weights )

allPlots   = {}
allModes   = ['mumu','mue', 'ee']
for i_mode, mode in enumerate(allModes):
    allPlots[mode] = {}

    for sys in systematics.keys():

        plots = []
        # This weight goes to the plot - do not reweight the sample with it
        weight_ = lambda event, sample, sys=sys: event.weight*event.sys_weights[sys] 

        #Plot styling
        for sample in all_samples: sample.style = styles.fillStyle(sample.color)

        #Apply reweighting to MC for specific detector effects
        for sample in all_samples:
          sample.read_variables = read_variables_MC
          #sample.weight = weight_function

        #Stack : Define what we want to see.
        stack = Stack(all_samples)

        # Define everything we want to have common to all plots
        selection_string = cutInterpreter.cutString(args.selection) 
        Plot.setDefaults(stack = stack, weight = staticmethod(weight_), selectionString = "("+getLeptonSelection(mode)+")&&("+selection_string+")")

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
                    name = class_+'_coarse',
                    texX = model_name, texY = 'Number of Events',
                    attribute = lambda event, sample, model_name=model_name: getattr(event, model_name),#if event.nJetGood> 5 and event.nJetGood < 7 else float('nan') ,
                    binning=Binning.fromThresholds([0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.82,0.84,0.86,0.88,0.90,0.92,0.94,0.96,0.98,1.0]),
                    addOverFlowBin='upper',
                ))

#        plots.append(Plot( name = 'Btagging_discriminator_value_Jet0' , texX = 'DeepB J0' , texY = 'Number of Events',
#            attribute = lambda event, sample: event.JetGood_btagDeepFlavB[0],
#            binning = [20,0,1],
#        ))
#
#        plots.append(Plot( name = 'Btagging_discriminator_value_Jet1' , texX = 'DeepB J1' , texY = 'Number of Events',
#            attribute = lambda event, sample: event.JetGood_btagDeepFlavB[1],
#            binning = [20,0,1],
#        ))
#
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

#        plots.append(Plot(
#            name = 'l1_mvaTOP',
#            texX = 'MVA_{TOP}(l_{1})', texY = 'Number of Events',
#            attribute = lambda event, sample: event.l1_mvaTOP,
#            binning=[20,-1,1],
#        ))
#
#        plots.append(Plot(
#            name = 'l1_mvaTOPWP',
#            texX = 'MVA_{TOP}(l_{1}) WP', texY = 'Number of Events',
#            attribute = lambda event, sample: event.l1_mvaTOPWP,
#            binning=[5,0,5],
#        ))
#
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

#        plots.append(Plot(
#            name = 'l2_mvaTOP',
#            texX = 'MVA_{TOP}(l_{2})', texY = 'Number of Events',
#            attribute = lambda event, sample: event.l2_mvaTOP,
#            binning=[20,-1,1],
#        ))
#
#        plots.append(Plot(
#            name = 'l2_mvaTOPWP',
#            texX = 'MVA_{TOP}(l_{1}) WP', texY = 'Number of Events',
#            attribute = lambda event, sample: event.l2_mvaTOPWP,
#            binning=[5,0,5],
#        ))
#
#        plots.append(Plot(
#            texX = 'E_{T}^{miss} (GeV)', texY = 'Number of Events / 20 GeV',
#            attribute = TreeVariable.fromString( "met_pt/F" ),
#            binning=[400/20,0,400],
#            addOverFlowBin='upper',
#        ))
#
#        plots.append(Plot(
#            texX = '#phi(E_{T}^{miss})', texY = 'Number of Events / 20 GeV',
#            attribute = TreeVariable.fromString( "met_phi/F" ),
#            binning=[10,-pi,pi],
#        ))
#
#        plots.append(Plot(
#            name = "minDLmass",
#            texX = 'min mass of all DL pairs', texY = 'Number of Events / 2 GeV',
#            attribute = TreeVariable.fromString( "minDLmass/F" ),
#            binning=[60,0,120],
#            addOverFlowBin='upper',
#        ))
#
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
          texX = 'H_{T}b (GeV)', texY = 'Number of Events / 30 GeV',
          name = 'htb', attribute = lambda event, sample: sum( j['pt'] for j in event.bJets ),
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
        
#        plots.append(Plot(
#          texX = '#eta(leading jet) (GeV)', texY = 'Number of Events / 30 GeV',
#          name = 'jet0_eta', attribute = lambda event, sample: event.JetGood_eta[0],
#          binning=[20,-3,3],
#        ))
#
#        plots.append(Plot(
#          texX = '#eta(subleading jet) (GeV)', texY = 'Number of Events / 30 GeV',
#          name = 'jet1_eta', attribute = lambda event, sample: event.JetGood_eta[1],
#          binning=[20,-3,3],
#        ))
#
#        plots.append(Plot(
#          texX = '#phi(leading jet) (GeV)', texY = 'Number of Events / 30 GeV',
#          name = 'jet0_phi', attribute = lambda event, sample: event.JetGood_phi[0],
#          binning=[10,-pi,pi],
#        ))
#
#        plots.append(Plot(
#          texX = '#phi(subleading jet) (GeV)', texY = 'Number of Events / 30 GeV',
#          name = 'jet1_phi', attribute = lambda event, sample: event.JetGood_phi[1],
#          binning=[10,-pi,pi],
#        ))
#
        allPlots[mode][sys] = plots
        
    plotting.fill(sum(allPlots[mode].values(), []), read_variables = read_variables, sequence = sequence, ttreeFormulas = {})


# Add the different channels into SF and all
for mode in ["SF","all"]:
    for sys in allPlots['mumu'].keys():
        for plot in allPlots['mumu'][sys]:
            for plot2 in (p for p in (allPlots['ee'][sys] if mode=="SF" else allPlots["mue"][sys]) if p.name == plot.name):  #For SF add EE, second round add EMu for all
                for i, j in enumerate(list(itertools.chain.from_iterable(plot.histos))):
                    for k, l in enumerate(list(itertools.chain.from_iterable(plot2.histos))):
                        if i==k: j.Add(l)

# Write Result Hist in root file
logger.info( "Now writing results in root file")
plot_dir = os.path.join(plot_directory, 'analysisPlots', args.plot_directory, args.era, 'all', args.selection)
if not os.path.exists(plot_dir):
    try:
        os.makedirs(plot_dir)
    except:
        # different jobs may start at the same time creating race conditions.
        pass 

for sys in systematics.keys():
    outfilename = plot_dir+'/tttt_'+sys+'.root'
    logger.info( "Saving in %s", outfilename )
    outfile = ROOT.TFile(outfilename, 'recreate')
    outfile.cd()
    for plot in allPlots[allModes[0]][sys]:
        for idx, histo_list in enumerate(plot.histos):
            for j, h in enumerate(histo_list):
                h.Write( plot.name + "__" + stack[idx][j].name + ('_'+args.era if args.era != 'RunII' else '') )

    logger.info( "Written %s", outfilename)
    outfile.Close()

logger.info( "Done with prefix %s and selectionString %s", args.selection, cutInterpreter.cutString(args.selection) )
