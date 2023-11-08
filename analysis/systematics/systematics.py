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
from math                                import sqrt, cos, sin, pi, atan2, cosh, isnan
ROOT.TH1.AddDirectory(False)

#Standard imports and batch mode

from RootTools.core.standard             import *

#tttt

from tttt.Tools.user                     import plot_directory
from tttt.Tools.cutInterpreter           import cutInterpreter
from tttt.Tools.objectSelection          import lepString, cbEleIdFlagGetter, vidNestedWPBitMapNamingList, isBJet
from tttt.Tools.helpers                  import getObjDict
from tttt.Tools.ISRCorrector             import ISRCorrector
from tttt.Tools.HTCorrector              import HTCorrector

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
argParser.add_argument('--sys',            action='store',      default='central')
argParser.add_argument('--era',            action='store',      default='RunII', type=str,                help="Which era?" )
argParser.add_argument('--mva_cut',        action='store',      default=None, help= 'Do you want to apply a cut on mva? which one?', choices=["tttt_2l_2l_4t","tttt_2l_2l_ttbb","tttt_2l_2l_ttcc","tttt_2l_2l_ttlight"])
argParser.add_argument('--cut_point',      action='store',      default=None,                            help= 'Where do you want the cut?')
argParser.add_argument('--DY',             action='store', default='ht', help= 'what kind of DY do you want?')
argParser.add_argument('--wc',             action='store', nargs = '*', default=[], help= 'Which wilson coefficients?')
args = argParser.parse_args()

#Directory naming parser options

if args.small: args.plot_directory += "_small"
isEFT = len(args.wc)>0
if isEFT:
    args.sys='central'
    print "Will produce templates for EFT coefficients:", args.wc
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
              'noDYISRReweight',
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

variations += jetVariations + scaleWeights + PSWeights + PDFWeights

# Check if we know the variation if not central don't use data!
if args.sys not in variations:
    if args.sys == "central":
        logger.info( "Running central samples (no sys variation)")
        noData = isEFT
    else:
        raise RuntimeError( "Variation %s not among the known: %s", args.sys, ",".join( variations ) )
else:
    logger.info( "Running sys variation %s, noData is set to 'True'", args.sys)
    noData = True

if noData:
    logger.info( "Running without data")
else:
    logger.info( "Data included in analysis cycle")

if not args.mva_cut is None:
    logger.info("Applying a cut on events based on {} with threshold {}".format(args.mva_cut, args.cut_point))
    args.plot_directory += "_mvaCut"+args.cut_point

if args.era == '2016_preVFP':
        from tttt.samples.nano_mc_private_UL20_Summer16_preVFP_postProcessed_dilep import *
        from tttt.samples.nano_data_private_UL20_Run2016_preVFP_postProcessed_dilep import Run2016_preVFP as data_sample
elif args.era == '2016':
        from tttt.samples.nano_mc_private_UL20_Summer16_postProcessed_dilep import *
        from tttt.samples.nano_data_private_UL20_Run2016_postProcessed_dilep import Run2016 as data_sample
elif args.era == '2017':
        from tttt.samples.nano_mc_private_UL20_Fall17_postProcessed_dilep import *
        from tttt.samples.nano_data_private_UL20_Run2017_postProcessed_dilep import Run2017 as data_sample
elif args.era == '2018':
        from tttt.samples.nano_mc_private_UL20_Autumn18_postProcessed_dilep import *
        from tttt.samples.nano_data_private_UL20_Run2018_postProcessed_dilep import Run2018 as data_sample
elif args.era == 'RunII':
        from tttt.samples.nano_private_UL20_RunII_postProcessed_dilep import *
        data_sample = RunII
else:
    raise Exception("Era %s not known"%args.era)

if not (args.sys == "HDampUp" or args.sys == "HDampDown") :
    sample_TTLep = copy.deepcopy(TTLep)
    TTLep_bb     = copy.deepcopy(TTbb)
elif args.sys == "HDampUp":
    sample_TTLep = TTLepHUp
    TTLep_bb     = TTbbHUp 
    print "switching to HDampUp samples" 
elif args.sys == "HDampDown":
    sample_TTLep = TTLepHDown
    TTLep_bb     = TTbbHDown 
    print "switching to HDampDown samples"

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

mc = [ TTLep_bb, TTLep_cc, TTLep_other, ST_tch, ST_twch, TTW, TTH, TTZ, TTTT, DiBoson]
if args.DY == 'ht': mc += [DY]
elif args.DY == 'inclusive': mc += [DY_inclusive]

#Add the data
if not noData:
    data_sample.name = "data"
    all_samples = mc +  [data_sample]
else:
    all_samples = mc

if isEFT:
    noData      = True
    sample      = TTbb_EFT
    from Analysis.Tools.WeightInfo import WeightInfo
    sample.weightInfo  = WeightInfo( sample.reweight_pkl )
    sample.weightInfo.set_order(2)

    mc          = [ sample for _ in range(sample.weightInfo.get_ndof(len(args.wc), 2)) ]

    coefficient = np.zeros( len(sample.weightInfo.combinations) )
    coefficient[0]=1
    eft_w_points= [coefficient]
    eft_w_names = ["central"]
    for wc in args.wc:
        index_lin  = sample.weightInfo.combinations.index((wc,))
        index_quad = sample.weightInfo.combinations.index((wc,wc))
       
        # +/-1 values 
        for val in [+1, -1]:
            coefficient = np.zeros( len(sample.weightInfo.combinations) )
            coefficient[0] = 1
            coefficient[index_lin] =val
            coefficient[index_quad]=val**2
            eft_w_names.append(wc+"_%+3.3f"%val)
            eft_w_points.append( coefficient )

    # mixed terms
    for wc in args.wc:
        index_lin  = sample.weightInfo.combinations.index((wc,))
        index_quad = sample.weightInfo.combinations.index((wc,wc))
        for wc2 in args.wc:
            index_lin2  = sample.weightInfo.combinations.index((wc2,))
            index_quad2 = sample.weightInfo.combinations.index((wc2,wc2))
            if not index_lin2>index_lin: continue
            index_mixed = sample.weightInfo.combinations.index((wc,wc2))
            coefficient = np.zeros( len(sample.weightInfo.combinations) )
            coefficient[0] = 1
            coefficient[index_lin] =1 
            coefficient[index_quad]=1
            coefficient[index_lin2] =1 
            coefficient[index_quad2]=1
            coefficient[index_mixed]=1
            eft_w_names.append(wc+"_%+3.3f"%1+"_"+wc2+"_%+3.3f"%1)
            eft_w_points.append( coefficient )

    # Multiply this matrix with p_C to get a vector of weights according to what is in base_points_names
    sample.eft_base_point_matrix = np.vstack( eft_w_points)
    #print sample.base_point_matrix.shape, sample.base_point_matrix
    #print sample.eft_w_names

if args.small:
    if not noData:
        data_sample.reduceFiles( factor = 100 )
    for sample in mc :
        sample.normalization = 1.
        sample.reduceFiles( to = 1 )
        #sample.scale /= sample.normalization

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
                 'index/I',
                 'isBJet/O',
                 'isBJet_loose/O',
                 'isBJet_medium/O',
                 'isBJet_tight/O'

                 ]

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
    VectorTreeVariable.fromString( "PDF[Weight/F]", nMax=120) , "nPDF/I","PS[Weight/F]","nPS/I","scale[Weight/F]","nscale/I",
    "GenJet[pt/F,eta/F,phi/F,partonFlavour/I,hadronFlavour/i]"
    ]
sequence = []

def debug(event, sample):
    try:
        event.jets = [getObjDict(event, 'JetGood_', jetVarNames, i) for i in range(int(event.nJetGood))]
        mass = sqrt(2*event.jets[0]['pt']*event.jets[1]['pt']*(cosh(event.jets[0]['eta']-event.jets[1]['eta'])-cos(event.jets[0]['phi']-event.jets[1]['phi']))) if event.nJetGood >=2 else 0
        #print event.jets[0]['phi'], event.jets[0]['pt'], event.jets[1]['phi'], event.jets[1]['pt'], event.jets[0]['eta'], event.jets[1]['eta']
        if mass <0:
            raise RuntimeError
    except:
        print event.jets[0]['phi'], event.jets[0]['pt'], event.jets[1]['phi'], event.jets[1]['pt'], event.jets[0]['eta'], event.jets[1]['eta']
        raise RuntimeError

#sequence.append(debug)

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

# def make_jets( event, sample ):
#     event.jets  = [getObjDict(event, 'JetGood_', jetVarNames, i) for i in range(int(event.nJetGood))]
#     event.bJets = filter(lambda j:isBJet(j, year=event.year) and abs(j['eta'])<=2.4    , event.jets)

#sequence.append( make_jets )

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
#WhichWay9 = {
#    "ScaleDownDown": 0,
#    "ScaleDownNone": 1,
#    "ScaleNoneDown": 3,
#    "ScaleNoneUp": 5,
#    "ScaleUpNone": 7,
#    "ScaleUpUp" 8,}
#WhichWay8 = {
#    "ScaleDownDown": 0,
#    "ScaleDownNone": 1,
#    "ScaleNoneDown": 3,
#    "ScaleNoneUp": 4,
#    "ScaleUpNone": 6,
#    "ScaleUpUp": 7,}
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

def getTheorySystematics(event,sample):
    #if event.nscale<8 : print event.nscale
    if args.sys in scaleWeights and event.nscale>=8 :
    #if event.nscale == 9 : event.reweightScale = event.scale_Weight[WhichWay9[args.sys]]
    #elif event.nscale == 8 : event.reweightScale = event.scale_Weight[WhichWay8[args.sys]]
    #else: print "Unexpected number of Scale weights!"
    #print "We are at scale weight number:" , WhichWay9[args.sys
        event.reweightScale = event.scale_Weight[scaleMap[event.nscale][args.sys]]
    else:
        event.reweightScale = 1.0

    if args.sys in PDFWeights:# and event.nPDF > 0:
        WhichOne = int(args.sys.split("_")[1])
        #print WhichOne
        if WhichOne == -1 or WhichOne > event.nPDF-1:
            print "PDF index out of range!"
        if not isnan(event.PDF_Weight[WhichOne]): 
            event.reweightPDF = event.PDF_Weight[WhichOne]
        else :
            event.reweightPDF = 1.0
        #print "we are at PDF weight"
    else:event.reweightPDF = 1.0

    if args.sys in PSWeights:
        WhichSide = {
            "ISRUp":    0,
            "FSRUp":    1,
            "ISRDown":  2,
            "FSRDown":  3,
            }
        event.reweightPS = event.PS_Weight[WhichSide[args.sys]]
        #print WhichSide[args.sys]
        #print "We have the PS weight:",event.PS_Weight[WhichSide[args.sys]]
    else:event.reweightPS = 1.0

sequence.append( getTheorySystematics )

def cut_MVA(event,sample):
    if not args.mva_cut is None:
        this = getattr(event, args.mva_cut)
    if args.cut_point == "0.1m":
        setattr(event,"cut_tttt_MVA",1 if this<0.1 else 0)
    elif args.cut_point == "0.1p":
        setattr(event,"cut_tttt_MVA",1 if this>=0.1 else 0)
    elif args.cut_point == "0.2m":
        setattr(event,"cut_tttt_MVA",1 if this<0.2 else 0)
    elif args.cut_point == "0.2p":
        setattr(event,"cut_tttt_MVA",1 if this>=0.2 else 0)
    else: setattr(event,"cut_tttt_MVA",1)

sequence.append(cut_MVA)

def make_manyJets(event, sample):
    thresholds = [30, 40, 50, 80, 100, 150, 200]
    # threshold_jets = {}
    for threshold in thresholds:
        # jet_name = 'jet{}'.format(threshold)
        filtered_jets = [j for j in event.jets if j['pt'] > threshold]
        # threshold_jets[jet_name] = filtered_jets
        ht_threshold = sum(jet['pt'] for jet in filtered_jets)#event.jets if jet['pt'] > threshold)
        setattr(event, 'nJetGood_pt{}'.format(threshold), len(filtered_jets))
        #setattr(event, 'nBTag_pt{}'.format(threshold), len(filtered_jets))
        setattr(event, 'htPt{}'.format(threshold), ht_threshold)
        cos_pt, sin_pt = 0., 0.
        for j in filtered_jets:
            cos_pt += j['pt'] * cos(j['phi'])
            sin_pt += j['pt'] * sin(j['phi'])

        setattr(event, 'ISRJet_pt{}'.format(threshold), sqrt(cos_pt**2 + sin_pt**2))

sequence.append(make_manyJets)

# ISR jets and corrector
isrCorrector = ISRCorrector()
htCorrector = HTCorrector()

#def make_ISRJet(event, sample):
#    event.jet40 = filter(lambda j: j['pt']>40 , event.jets)
#    cos_pt, sin_pt = 0., 0.
#    for j in event.jet40:
#        cos_pt += j['pt']*cos(j['phi'])
#        sin_pt += j['pt']*sin(j['phi'])
#    event.ISRJet_pt40 = sqrt(cos_pt**2 + sin_pt**2)
#
#sequence.append(make_ISRJet)

def makeISRSF( event, sample ):
    event.reweightDY = 1
    if not args.sys == "noDYISRReweight" and args.DY=='ht':
        if sample.name.startswith("DY"):
            event.reweightDY = isrCorrector.getSF( event.nJetGood, event.ISRJet_pt40 ) 

#sequence.append( makeISRSF )

def makeHTSF( event, sample ):
    event.reweightDY = 1
    if not args.sys == "noDYISRReweight" and args.DY=='ht':
        if sample.name.startswith("DY"):
            event.reweightDY = htCorrector.getSF( event.nJetGood, event.htPt30 )

sequence.append( makeHTSF )

def makeEFTWeights( event, sample):
    if not hasattr( sample, "reweight_pkl" ):
        return
    # we're here if the sample has a reweight_pkl

    np.eft_base_point_weights = np.dot( sample.eft_base_point_matrix, np.array( [event.p_C[i] for i in range(len(sample.weightInfo.combinations))] ) )
    for name, val in zip( eft_w_names, np.eft_base_point_weights):
        setattr( event, name, val/event.p_C[0])

sequence.append( makeEFTWeights )

#TTree formulas
ttreeFormulas = {}

if args.sys in jetVariations:
  ttreeFormulas.update({"ht_"+args.sys :"Sum$(JetGood_pt_"+args.sys+")"})


##list all the reweights
weightnames = ['reweightLeptonSF', 'reweightBTagSF_central', 'reweightPU', 'reweightL1Prefire', 'reweightTrigger','reweightScale','reweightPS','reweightPDF']
if not args.sys == "noTopPtReweight": weightnames += ['reweightTopPt']
if not args.sys == "noDYISRReweight": weightnames += ['reweightDY']

sys_weights = {
        'LeptonSFDown'  : ('reweightLeptonSF','reweightLeptonSFDown'),
        'LeptonSFUp'    : ('reweightLeptonSF','reweightLeptonSFUp'),
        'PUUp'          : ('reweightPU','reweightPUUp'),
        'PUDown'        : ('reweightPU','reweightPUDown'),
        'BTagSFJesUp'   : ('reweightBTagSF_central','reweightBTagSF_up_jes'),
        'BTagSFJesDown' : ('reweightBTagSF_central','reweightBTagSF_down_jes'),
        'BTagSFHfDown'  : ('reweightBTagSF_central','reweightBTagSF_down_hf'),
        'BTagSFHfUp'    : ('reweightBTagSF_central','reweightBTagSF_up_hf'),
        'BTagSFLfDown'  : ('reweightBTagSF_central','reweightBTagSF_down_lf'),
        'BTagSFLfUp'    : ('reweightBTagSF_central','reweightBTagSF_up_lf'),
        'BTagSFHfs1Down': ('reweightBTagSF_central','reweightBTagSF_down_hfstats1'),
        'BTagSFHfs1Up'  : ('reweightBTagSF_central','reweightBTagSF_up_hfstats1'),
        'BTagSFLfs1Down': ('reweightBTagSF_central','reweightBTagSF_down_lfstats1'),
        'BTagSFLfs1Up'  : ('reweightBTagSF_central','reweightBTagSF_up_lfstats1'),
        'BTagSFHfs2Down': ('reweightBTagSF_central','reweightBTagSF_down_hfstats2'),
        'BTagSFHfs2Up'  : ('reweightBTagSF_central','reweightBTagSF_up_hfstats2'),
        'BTagSFLfs2Down': ('reweightBTagSF_central','reweightBTagSF_down_lfstats2'),
        'BTagSFLfs2Up'  : ('reweightBTagSF_central','reweightBTagSF_up_lfstats2'),
        'BTagSFCfe1Down': ('reweightBTagSF_central','reweightBTagSF_down_cferr1'),
        'BTagSFCfe1Up'  : ('reweightBTagSF_central','reweightBTagSF_up_cferr1'),
        'BTagSFCfe2Down': ('reweightBTagSF_central','reweightBTagSF_down_cferr2'),
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

if "jesTotal" in args.sys:
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

    #def make_weight_function( weightnames=weightnames):
    def weight_function( event, sample, weightnames=weightnames):
            # Calculate weight, this becomes: w = event.weightnames[0]*event.weightnames[1]*...
            weights = [g(event) for g in map( operator.attrgetter, weightnames)]
            # Check if any weight is nan
            if any(not isinstance(w, (int, float)) or isnan(w) for w in weights):
                weights = [1 if (not isinstance(w, (int, float)) or isnan(w) )else w for w in weights]
                for w in weights : print "We really should not have NANs. There is something to fix for:", w
            w = reduce(operator.mul, weights, 1)
            return w
    #    return weight_function

    #Plot styling
    for sample in mc: sample.style = styles.fillStyle(sample.color)
    if not noData:
        data_sample.style = styles.errorStyle( ROOT.kBlack )

    #Apply reweighting to MC for specific detector effects
    for sample in mc:
      sample.read_variables = read_variables_MC
      sample.weight = weight_function
      if hasattr( sample, "reweight_pkl" ):
          sample.read_variables += [VectorTreeVariable.fromString("p[C/F]", nMax=200)]
        
    #Stack : Define what we want to see.
    weight_ = lambda event, sample: event.cut_tttt_MVA*event.weight
    if not noData:
        stack = Stack(mc, [data_sample])
    elif isEFT:
        stack = Stack(*list([s] for s in mc))
        weight_ = [ [lambda event, sample, eft_w=eft_w: event.cut_tttt_MVA*event.weight*getattr( event, eft_w)] for eft_w in eft_w_names]
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
                name = class_+"_coarse",
                texX = model_name, texY = 'Number of Events',
                attribute = lambda event, sample, model_name=model_name: getattr(event, model_name),#if event.nJetGood> 5 and event.nJetGood < 7 else float('nan') ,
                binning=Binning.fromThresholds([0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.82,0.84,0.86,0.88,0.90,0.92,0.94,0.96,0.98,1.0]),
                addOverFlowBin='upper',
            ))

    plots.append(Plot( name = 'Btagging_discriminator_value_Jet0' , texX = 'DeepB J0' , texY = 'Number of Events',
        attribute = lambda event, sample: event.JetGood_btagDeepFlavB[0],
        binning = [20,0,1],
    ))

    plots.append(Plot( name = 'Btagging_discriminator_value_Jet1' , texX = 'DeepB J1' , texY = 'Number of Events',
        attribute = lambda event, sample: event.JetGood_btagDeepFlavB[1],
        binning = [20,0,1],
    ))

#    plots.append(Plot(
#      name = 'nVtxs', texX = 'vertex multiplicity', texY = 'Number of Events',
#      attribute = TreeVariable.fromString( "PV_npvsGood/I" ),
#      binning=[50,0,50],
#      addOverFlowBin='upper',
#    ))

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
    plots.append(Plot(
        name = "minDLmass",
        texX = 'min mass of all DL pairs', texY = 'Number of Events / 2 GeV',
        attribute = TreeVariable.fromString( "minDLmass/F" ),
        binning=[60,0,120],
        addOverFlowBin='upper',
    ))

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
#
    plots.append(Plot(
      texX = 'N_{jets}', texY = 'Number of Events',
      attribute = TreeVariable.fromString( "nJetGood/I" ), #nJetSelected
      binning=[8,3.5,11.5],
    ))

    plots.append(Plot(
      name = "nJetGood_pt30",
      texX = 'N_{jets}', texY = 'Number of Events',
      attribute = lambda event, sample:event.nJetGood_pt30, #nJetSelected_pt>30
      binning=[8,3.5,11.5],
    ))

    plots.append(Plot(
      name = "nJetGood_pt40",
      texX = 'N_{jets}', texY = 'Number of Events',
      attribute = lambda event, sample:event.nJetGood_pt40, #nJetSelected_pt>40
      binning=[8,3.5,11.5],
    ))

    plots.append(Plot(
      name = "nJetGood_pt50",
      texX = 'N_{jets}', texY = 'Number of Events',
      attribute = lambda event, sample:event.nJetGood_pt50, #nJetSelected_pt>50
      binning=[8,3.5,11.5],
    ))

    plots.append(Plot(
      name = "nJetGood_pt80",
      texX = 'N_{jets}', texY = 'Number of Events',
      attribute = lambda event, sample:event.nJetGood_pt80, #nJetSelected_pt>80
      binning=[8,3.5,11.5],
    ))

    plots.append(Plot(
      name = "nJetGood_pt100",
      texX = 'N_{jets}', texY = 'Number of Events',
      attribute = lambda event, sample:event.nJetGood_pt100, #nJetSelected_pt>100
      binning=[8,3.5,11.5],
    ))

    plots.append(Plot(
      name = "nJetGood_pt150",
      texX = 'N_{jets}', texY = 'Number of Events',
      attribute = lambda event, sample:event.nJetGood_pt150, #nJetSelected_pt>150
      binning=[8,3.5,11.5],
    ))

    plots.append(Plot(
      name = "nJetGood_pt200",
      texX = 'N_{jets}', texY = 'Number of Events',
      attribute = lambda event, sample:event.nJetGood_pt200, #nJetSelected_pt>200
      binning=[8,3.5,11.5],
    ))

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
      texX = 'H_{T} (GeV)', texY = 'Number of Events / 40 Gev',
      name = 'ht_fineBinning', attribute = lambda event, sample: sum( j['pt'] for j in event.jets ),
      binning=[2000/50,500,2500],
    ))

    plots.append(Plot(
      texX = 'H_{T} (GeV)', texY = 'Number of Events',
      name = 'ht', attribute = lambda event, sample: sum( j['pt'] for j in event.jets ),
      binning=[2000/200,500,2500],
    ))

    plots.append(Plot(
      texX = 'H_{T}b (GeV)', texY = 'Number of Events / 30 GeV',
      name = 'htb', attribute = lambda event, sample: sum( j['pt'] for j in event.bJets ),
      binning=[1500/50,0,1500],
    ))
    
    plots.append(Plot(
      texX = 'H_{T} from p_{T}(j)>30 ', texY = 'Number of Events / 100 GeV',
      name = 'htPt30', attribute = lambda event, sample: event.htPt30,
      binning=[2500/200,500,2500],
    ))

    plots.append(Plot(
      texX = 'H_{T} from p_{T}(j)>40 ', texY = 'Number of Events / 100 GeV',
      name = 'htPt40', attribute = lambda event, sample: event.htPt40,
      binning=[2500/200,500,2500],
    ))

    plots.append(Plot(
      texX = 'H_{T} from p_{T}(j)>50 ', texY = 'Number of Events / 100 GeV',
      name = 'htPt50', attribute = lambda event, sample: event.htPt50,
      binning=[2500/200,500,2500],
    ))

    plots.append(Plot(
      texX = 'H_{T} from p_{T}(j)>80 ', texY = 'Number of Events / 100 GeV',
      name = 'htPt80', attribute = lambda event, sample: event.htPt80,
      binning=[2500/200,500,2500],
    ))
 
    plots.append(Plot(
      texX = ' p_{T}(ISR j)>30 ', texY = 'Number of Events / 100 GeV',
      name = 'ISRJet_pt30', attribute = lambda event, sample: event.ISRJet_pt30,
      binning=[600/30,0,600],
    ))

    plots.append(Plot(
      texX = ' p_{T}(ISR j)>50 ', texY = 'Number of Events / 100 GeV',
      name = 'ISRJet_pt50', attribute = lambda event, sample: event.ISRJet_pt50,
      binning=[600/30,0,600],
    ))
    
    plots.append(Plot(
      texX = ' p_{T}(ISR j)>80 ', texY = 'Number of Events / 100 GeV',
      name = 'ISRJet_pt80', attribute = lambda event, sample: event.ISRJet_pt80,
      binning=[600/30,0,600],
    ))
    
    plots.append(Plot(
      name = "ISRJet_pt40",
      texX = 'p_{T}(ISR)>40', texY = 'Number of Events',
      attribute = lambda event, sample: event.ISRJet_pt40,
      binning=Binning.fromThresholds([0,20,40,60,80,100,120,140,160,180,200,220,240,260,280,300,320,340,360,380,400,450,500,600,800,1000,2000]),
      #binning=[600/30,0,600],
    ))
    
    plots.append(Plot(
      name = "ISRJet_pt40_course",
      texX = 'p_{T}(ISR)>40', texY = 'Number of Events',
      attribute = lambda event, sample: event.ISRJet_pt40,
      binning=Binning.fromThresholds([0,50,100,150,200,250,300,350,400,450,500,600,800,1000,2000]),
      #binning=[600/30,0,600],
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

    
    plots.append(Plot(
      texX = '#eta(leading jet) (GeV)', texY = 'Number of Events / 30 GeV',
      name = 'jet0_eta', attribute = lambda event, sample: event.JetGood_eta[0],
      binning=[20,-3,3],
    ))

    plots.append(Plot(
      texX = '#eta(subleading jet) (GeV)', texY = 'Number of Events / 30 GeV',
      name = 'jet1_eta', attribute = lambda event, sample: event.JetGood_eta[1],
      binning=[20,-3,3],
    ))

    plots.append(Plot(
      texX = '#phi(leading jet) (GeV)', texY = 'Number of Events / 30 GeV',
      name = 'jet0_phi', attribute = lambda event, sample: event.JetGood_phi[0],
      binning=[10,-pi,pi],
    ))

    plots.append(Plot(
      texX = '#phi(subleading jet) (GeV)', texY = 'Number of Events / 30 GeV',
      name = 'jet1_phi', attribute = lambda event, sample: event.JetGood_phi[1],
      binning=[10,-pi,pi],
    ))


#    for index in range(2):
#        for abs_pdg in [11, 13]:
#            lep_name = "mu" if abs_pdg==13 else "ele"
#            plots.append(Plot(
#              texX = 'p_{T}(%s_{%i}) (GeV)'%(lep_name, index), texY = 'Number of s',
#              name = '%s%i_pt'%(lep_name, index), attribute = lep_getter("pt", index, abs_pdg),
#              binning=[400/20,0,400],
#            ))
#            plots.append(Plot(
#              texX = '#eta(%s_{%i}) (GeV)'%(lep_name, index), texY = 'Number of Events',
#              name = '%s%i_eta'%(lep_name, index), attribute = lep_getter("eta", index, abs_pdg),
#              binning=[30,-3,3],
#            ))
#            plots.append(Plot(
#              texX = '#phi(%s_{%i}) (GeV)'%(lep_name, index), texY = 'Number of Events',
#              name = '%s%i_phi'%(lep_name, index), attribute = lep_getter("phi", index, abs_pdg),
#              binning=[30,-pi,pi],
#            ))
#            plots.append(Plot(
#              texX = 'dxy(%s_{%i}) (GeV)'%(lep_name, index), texY = 'Number of Events',
#              name = '%s%i_dxy'%(lep_name, index), attribute = lep_getter("dxy", index, abs_pdg, functor = lambda x: abs(x)),
#              binning=[50,0,0.05],
#            ))
#            plots.append(Plot(
#              texX = 'dz(%s_{%i}) (GeV)'%(lep_name, index), texY = 'Number of Events',
#              name = '%s%i_dz'%(lep_name, index), attribute = lep_getter("dz", index, abs_pdg, functor = lambda x: abs(x)),
#              binning=[50,0,0.05],
#            ))
#            plots.append(Plot(
#              texX = 'IP_{3D}(%s_{%i}) (GeV)'%(lep_name, index), texY = 'Number of Events',
#              name = '%s%i_ip3d'%(lep_name, index), attribute = lep_getter("ip3d", index, abs_pdg, functor = lambda x: abs(x)),
#              binning=[50,0,0.05],
#            ))
#            plots.append(Plot(
#              texX = '#sigma(IP)_{3D}(%s_{%i}) (GeV)'%(lep_name, index), texY = 'Number of Events',
#              name = '%s%i_sip3d'%(lep_name, index), attribute = lep_getter("sip3d", index, abs_pdg, functor = lambda x: abs(x)),
#              binning=[40,0,8],
#            ))
#            plots.append(Plot(
#              texX = 'jetRelIso(%s_{%i}) (GeV)'%(lep_name, index), texY = 'Number of Events',
#              name = '%s%i_jetRelIso'%(lep_name, index), attribute = lep_getter("jetRelIso", index, abs_pdg),
#              binning=[50,-.15,0.5],
#            ))
#            plots.append(Plot(
#              texX = 'miniPFRelIso_all(%s_{%i}) (GeV)'%(lep_name, index), texY = 'Number of Events',
#              name = '%s%i_miniPFRelIso_all'%(lep_name, index), attribute = lep_getter("miniPFRelIso_all", index, abs_pdg),
#              binning=[50,0,.5],
#            ))
#            plots.append(Plot(
#              texX = 'pfRelIso03_all(%s_{%i}) (GeV)'%(lep_name, index), texY = 'Number of Events',
#              name = '%s%i_pfRelIso03_all'%(lep_name, index), attribute = lep_getter("pfRelIso03_all", index, abs_pdg),
#              binning=[50,0,.5],
#            ))
#            # plots.append(Plot(
#            #   texX = 'mvaTTH(%s_{%i}) (GeV)'%(lep_name, index), texY = 'Number of Events',
#            #   name = '%s%i_mvaTTH'%(lep_name, index), attribute = lep_getter("mvaTTH", index, abs_pdg),
#            #   binning=[24,-1.2,1.2],
#            # ))
##            plots.append(Plot(
##              texX = 'mvaTOP(%s_{%i}) (GeV)'%(lep_name, index), texY = 'Number of Events',
##              name = '%s%i_mvaTOP'%(lep_name, index), attribute = lep_getter("mvaTOP", index, abs_pdg),
##              binning=[24,-1.2,1.2],
##            ))
#            plots.append(Plot(
#              texX = 'charge(%s_{%i}) (GeV)'%(lep_name, index), texY = 'Number of Events',
#              name = '%s%i_charge'%(lep_name, index), attribute = lep_getter("pdgId", index, abs_pdg, functor = charge),
#              binning=[3,-1,2],
#            ))
#            if lep_name == "mu":
#                plots.append(Plot(
#                  texX = 'segmentComp(%s_{%i}) (GeV)'%(lep_name, index), texY = 'Number of Events',
#                  name = '%s%i_segmentComp'%(lep_name, index), attribute = lep_getter("segmentComp", index, abs_pdg),
#                  binning=[50,0,1],
#                ))
#                plots.append(Plot(
#                  texX = 'nStations(%s_{%i}) (GeV)'%(lep_name, index), texY = 'Number of Events',
#                  name = '%s%i_nStations'%(lep_name, index), attribute = lep_getter("nStations", index, abs_pdg),
#                  binning=[10,0,10],
#                ))
#                plots.append(Plot(
#                  texX = 'nTrackerLayers(%s_{%i}) (GeV)'%(lep_name, index), texY = 'Number of Events',
#                  name = '%s%i_nTrackerLayers'%(lep_name, index), attribute = lep_getter("nTrackerLayers", index, abs_pdg),
#                  binning=[20,0,20],
#                ))
#            if lep_name == "ele":
#                for cbIdFlag in vidNestedWPBitMapNamingList:
#                    plots.append(Plot(
#                      texX = '%s(%s_{%i}) (GeV)'%(cbIdFlag, lep_name, index), texY = 'Number of Events',
#                      name = '%s%i_%s_Flag'%(lep_name, index, cbIdFlag), attribute = lep_getter("vidNestedWPBitmap", index, abs_pdg, functor = cbEleIdFlagGetter(cbIdFlag)),
#                      binning=[5,0,5],
#                ))
#

    if args.sys in jetVariations:

      plots.append(Plot(
        texX = 'N_{jets}_'+args.sys, texY = 'Number of Events',
        attribute = TreeVariable.fromString( "nJetGood_"+args.sys+"/I" ), #nJet varied
        binning=[8,3.5,11.5],
      ))
      
      plots.append(Plot(
        texX = 'N_{b-tag}_'+args.sys, texY = 'Number of Events',
        attribute = TreeVariable.fromString( "nBTag_"+args.sys+"/I" ), #nJetSelected
        binning=[7, -0.5,6.5],
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

    allPlots[mode] = plots

# Add the different channels into SF and all
for mode in ["SF","all"]:
    yields[mode] = {}
    for y in yields[allModes[0]]:
        try:    yields[mode][y] = sum(yields[c][y] for c in (['ee','mumu'] if mode=="SF" else ['ee','mumu','mue']))
        except: yields[mode][y] = 0

    for plot in allPlots['mumu']:
        for plot2 in (p for p in (allPlots['ee'] if mode=="SF" else allPlots["mue"]) if p.name == plot.name):  #For SF add EE, second round add EMu for all
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

outfilename = plot_dir+'/tttt_'+args.sys+'.root'
if isEFT: outfilename = plot_dir+'/tttt_EFTs.root'
logger.info( "Saving in %s", outfilename )
outfile = ROOT.TFile(outfilename, 'recreate')#'update'
outfile.cd()
for plot in allPlots[allModes[0]]:
    for idx, histo_list in enumerate(plot.histos):
        for j, h in enumerate(histo_list):
            h.Write( plot.name + "__" + stack[idx][j].name + ('_'+args.era if args.era != 'RunII' else '') + (('_'+eft_w_names[idx]) if isEFT else '') )
outfile.Close()

logger.info( "Done with prefix %s and selectionString %s", args.selection, cutInterpreter.cutString(args.selection) )
