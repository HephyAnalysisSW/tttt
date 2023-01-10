#!/usr/bin/env python
''' Analysis script for standard plots
'''
#
# Standard imports and batch mode
#
import ROOT, os
import itertools
import copy
import array
import operator
from   math                              import sqrt, cos, sin, pi, atan2, cosh

# RootTools
from RootTools.core.standard             import *

# tttt
from tttt.Tools.user                     import plot_directory
from tttt.Tools.cutInterpreter           import cutInterpreter
from tttt.Tools.objectSelection          import lepString, cbEleIdFlagGetter, vidNestedWPBitMapNamingList

# Analysis
from Analysis.Tools.helpers              import deltaPhi, deltaR
from Analysis.Tools.puProfileCache       import *
from Analysis.Tools.puReweighting        import getReweightingFunction
import Analysis.Tools.syncer
import numpy as np

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',       action='store',      default='INFO', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--small',                             action='store_true', help='Run only on a small subset of the data?')
argParser.add_argument('--noData',         action='store_true', help='Do not plot data.')
argParser.add_argument('--sorting',                           action='store', default=None, choices=[None, "forDYMB"],  help='Sort histos?', )
argParser.add_argument('--dataMCScaling',  action='store_true', help='Data MC scaling?')
argParser.add_argument('--plot_directory', action='store', default='TMB_4t_p3_bin50')
argParser.add_argument('--selection',      action='store', default='dilepL-offZ1-njet4p-btag2p-ht500')
argParser.add_argument('--mva',            action='store', default='no MVA')
args = argParser.parse_args()

# Logger
import tttt.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

if args.small: args.plot_directory += "_small"
if args.noData:args.plot_directory += "_noData"

# Simulated samples
from tttt.samples.nano_private_UL20_RunII_postProcessed_dilep import *
#from TMB.Samples.nanoTuples_RunII_nanoAODv6_dilep_pp import *


# Split dileptonic TTBar into three different contributions
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

# group all the simulated backgroundsamples 
mc = [ TTLep_bb, TTLep_cc, TTLep_other,TTTT] 
#mc = [  TTTT] 
# Now we add the data
if not args.noData:
    from tttt.samples.nano_private_UL20_RunII_postProcessed_dilep import RunII
    data_sample = RunII
    data_sample.name = "data"
    all_samples = mc +  [data_sample]
else:
    all_samples = mc 

# Here we compute the scaling of the simulation to the data luminosity (event.weight corresponds to 1/fb for simulation, hence we divide the data lumi in pb^-1 by 1000) 
lumi_scale = 137. if args.noData else data_sample.lumi/1000.

# We're going to "scale" the simulation if "small" is true. So let's define a "scale" which will correct this
for sample in mc:
    sample.scale  = 1 

# For R&D we just use a fraction of the data
if args.small:
    if not args.noData:
        data_sample.reduceFiles( factor = 100 )
    for sample in mc :
        sample.normalization = 1.
        sample.reduceFiles( to = 1 )
        #sample.reduceFiles( to=1)
        sample.scale /= sample.normalization

# Helpers for putting text on the plots
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
    plot_directory_ = os.path.join(plot_directory, 'analysisPlots', args.plot_directory, 'RunII', mode + ("_log" if log else ""), args.selection)
    plot_directory_cut_ = os.path.join(plot_directory,'analysisPlots', args.plot_directory, 'RunII', mode + ("_log" if log else ""), '_cut_y', args.selection)
    plot_directory_cut__ = os.path.join(plot_directory,'analysisPlots', args.plot_directory, 'RunII', mode + ("_log" if log else ""), '_cut_yy', args.selection)
    for plot in plots:
      if not max(l.GetMaximum() for l in sum(plot.histos,[])): continue # Empty plot

      _drawObjects = []

      if isinstance( plot, Plot):
          plotting.draw(plot,
            plot_directory = plot_directory_,
            ratio =  {'yRange':(0.1,1.9)} if not args.noData else None,
            logX = False, logY = log, sorting = True,
            yRange = (0.9, "auto") if log else (0.001, "auto"),
            scaling = {0:1} if args.dataMCScaling else {},
            legend = ( (0.18,0.88-0.03*sum(map(len, plot.histos)),0.9,0.88), 2),
            drawObjects = drawObjects( dataMCScale , lumi_scale ) + _drawObjects,
            copyIndexPHP = True, extensions = ["png", "pdf", "root"],
          )
      if isinstance( plot, Plot):
          plotting.draw(plot,
            plot_directory = plot_directory_cut_,
            ratio =  {'yRange':(0.1,1.9)} if not args.noData else None,
            logX = False, logY = log, sorting = True,
            yRange = (0.1, "auto") if log else (0.001, "auto"),
            scaling = {0:1} if args.dataMCScaling else {},
            legend = ( (0.18,0.88-0.03*sum(map(len, plot.histos)),0.9,0.88), 2),
            drawObjects = drawObjects( dataMCScale , lumi_scale ) + _drawObjects,
            copyIndexPHP = True, extensions = ["png", "pdf", "root"],
          ) 

    if isinstance( plot, Plot):
          plotting.draw(plot,
            plot_directory = plot_directory_cut__,
            ratio =  {'yRange':(0.1,1.9)} if not args.noData else None,
            logX = False, logY = log, sorting = True,
            yRange = (0.01, "auto") if log else (0.001, "auto"),
            scaling = {0:1} if args.dataMCScaling else {},
            legend = ( (0.18,0.88-0.03*sum(map(len, plot.histos)),0.9,0.88), 2),
            drawObjects = drawObjects( dataMCScale , lumi_scale ) + _drawObjects,
            copyIndexPHP = True, extensions = ["png", "pdf", "root"],
          )           

read_variables = []

#jetVars         = ['pt/F', 'eta/F', 'phi/F', 'btagDeepFlavB/F']#, 'btagDeepFlavCvB/F', 'btagDeepFlavCvL/F']
#jetVars          = ['pt/F', 'eta/F', 'phi/F', 'btagDeepFlavB/F', 'btagDeepFlavCvB/F', 'btagDeepFlavQG/F','index/I']
jetVars     = ['pt/F', 'eta/F', 'phi/F', 'btagDeepFlavB/F', 'btagDeepFlavCvB/F', 'btagDeepFlavQG/F', 'btagDeepFlavb/F', 'btagDeepFlavbb/F', 'btagDeepFlavlepb/F', 'btagDeepb/F', 'btagDeepbb/F', 'chEmEF/F', 'chHEF/F', 'neEmEF/F', 'neHEF/F' ]

jetVarNames     = [x.split('/')[0] for x in jetVars]
#    jetVars     += ['btagDeepFlavb/F', 'btagDeepFlavbb/F', 'btagDeepFlavlepb/F', 'btagDeepb/F', 'btagDeepbb/F']

# the following we read for both, data and simulation 
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

# the following we read only in simulation
read_variables_MC = [
    'reweightBTag_SF/F', 'reweightPU/F', 'reweightL1Prefire/F', 'reweightLeptonSF/F', 'reweightTrigger/F',
    "GenJet[pt/F,eta/F,phi/F,partonFlavour/I,hadronFlavour/i]"
    ]
            
# Read variables and sequences
sequence       = []

from tttt.Tools.objectSelection import isBJet
from tttt.Tools.helpers import getObjDict


def make_jets( event, sample ):
    event.jets  = [getObjDict(event, 'JetGood_', jetVarNames, i) for i in range(int(event.nJetGood))] 
    event.bJets = [j for j in event.jets if isBJet(j, year=event.year) and abs(j['eta'])<=2.4]

sequence.append( make_jets )

#MVA
import tttt_2l2p as config
assert False
import onnxruntime as ort
read_variables += config.read_variables
test = []

# Add sequence that computes the MVA inputs

# Add sequence that computes the MVA inputs
def make_mva_inputs( event, sample ):
   for mva_variable, func in config.mva_variables:
       setattr( event, mva_variable, func(event, sample) )
sequence.append( make_mva_inputs ) 

Models = [
"btag2p_b-100000_e-500_hs1-96_hs2-53",
"btag2p_b-10000_e-500_hs1-96_hs2-53",
"btag2p_b-20000_e-2000_hs1-96_hs2-53_lstm-4_hs-lstm-25",
"btag2p_b-20000_e-2000_hs1-96_hs2-53_lstm-4_hs-lstm-25_DoubleB",
"btag2p_b-20000_e-500_hs1-144_hs2-53",
"btag2p_b-20000_e-500_hs1-192_hs2-53",
"btag2p_b-20000_e-500_hs1-48_hs2-53",
"btag2p_b-20000_e-500_hs1-96_hs2-33",
"btag2p_b-20000_e-500_hs1-96_hs2-43",
"btag2p_b-20000_e-500_hs1-96_hs2-48",
"btag2p_b-20000_e-500_hs1-96_hs2-53",
"btag2p_b-20000_e-500_hs1-96_hs2-53_lstm-1_hs-lstm-10",
"btag2p_b-20000_e-500_hs1-96_hs2-53_lstm-1_hs-lstm-10_DoubleB",
"btag2p_b-20000_e-500_hs1-96_hs2-53_lstm-2_hs-lstm-10",
"btag2p_b-20000_e-500_hs1-96_hs2-53_lstm-2_hs-lstm-10_DoubleB",
"btag2p_b-20000_e-500_hs1-96_hs2-53_lstm-4_hs-lstm-10",
"btag2p_b-20000_e-500_hs1-96_hs2-53_lstm-4_hs-lstm-15",
"btag2p_b-20000_e-500_hs1-96_hs2-53_lstm-4_hs-lstm-15_DoubleB",
"btag2p_b-20000_e-500_hs1-96_hs2-53_lstm-4_hs-lstm-25",
"btag2p_b-20000_e-500_hs1-96_hs2-53_lstm-4_hs-lstm-25_DoubleB",
"btag2p_b-20000_e-500_hs1-96_hs2-53_lstm-4_hs-lstm-5",
"btag2p_b-20000_e-500_hs1-96_hs2-53_lstm-4_hs-lstm-5_DoubleB",
"btag2p_b-20000_e-500_hs1-96_hs2-53_lstm-6_hs-lstm-10",
"btag2p_b-20000_e-500_hs1-96_hs2-53_lstm-6_hs-lstm-10_DoubleB",
"btag2p_b-20000_e-500_hs1-96_hs2-53_lstm-8_hs-lstm-10",
"btag2p_b-20000_e-500_hs1-96_hs2-53_lstm-8_hs-lstm-10_DoubleB",
"btag2p_b-20000_e-500_hs1-96_hs2-63",
"btag2p_b-20000_e-750_hs1-96_hs2-53_lstm-4_hs-lstm-25",
"btag2p_b-20000_e-750_hs1-96_hs2-53_lstm-4_hs-lstm-25_DoubleB",
"btag2p_b-50000_e-500_hs1-96_hs2-53",
"btag2p_b-5000_e-500_hs1-96_hs2-53"
]

if (args.mva == "no MVA"):
    allModels = []
else:
    allModels = []
    allModels.append(Models[int(args.mva)])
options = ort.SessionOptions()
options.intra_op_num_threads = 1
options.inter_op_num_threads = 1

def torch_predict( event, sample ):
    flat_variables, lstm_jets_db = config.predict_inputs( event, sample, jet_lstm = True)    
    lstm_jets_nodb = np.delete(lstm_jets_db, obj = [6,7,8], axis = 2) #remove doubleB info
    lstm_jets_db = np.nan_to_num(lstm_jets_db)
    for model in allModels:
        ort_sess = ort.InferenceSession("models/"+model+".onnx", providers = ['CPUExecutionProvider'],sess_options=options)
        LSTM = False
        db = False
        if (str(model).find('lstm')!=-1): LSTM = True
        if (str(model).find('db')!=-1 or str(model).find('DoubleB')!=-1): db = True
        if (LSTM):
            if (db):
                lis = ort_sess.run(["output1"], {"input1": flat_variables.astype(np.float32),"input2": lstm_jets_db.astype(np.float32)})[0][0]     
            else:
                lis = ort_sess.run(["output1"], {"input1": flat_variables.astype(np.float32),"input2": lstm_jets_nodb.astype(np.float32)})[0][0] 
        else:
            lis = ort_sess.run(["output1"], {"input1": flat_variables.astype(np.float32)})[0][0]           
        if lis.any()<0 or lis.any()>1:
            raise RuntimeError("Found NAN prediction?")
        setattr( event, model+"_TTTT", lis[0] )
        setattr( event, model+"_TTB", lis[1] )
        setattr( event, model+"_TTC", lis[2] )
        setattr( event, model+"_TTO", lis[3] )
        
        #test.append(lis[0])
sequence.append( torch_predict )

# Let's make a function that provides string-based lepton selection
mu_string  = lepString('mu','VL')
ele_string = lepString('ele','VL')
def getLeptonSelection( mode ):
    if   mode=="mumu": return "Sum$({mu_string})==2&&Sum$({ele_string})==0".format(mu_string=mu_string,ele_string=ele_string)
    elif mode=="mue":  return "Sum$({mu_string})==1&&Sum$({ele_string})==1".format(mu_string=mu_string,ele_string=ele_string)
    elif mode=="ee":   return "Sum$({mu_string})==0&&Sum$({ele_string})==2".format(mu_string=mu_string,ele_string=ele_string)
    elif mode=='all':    return "Sum$({mu_string})+Sum$({ele_string})==2".format(mu_string=mu_string,ele_string=ele_string)

def charge(pdgId):
    return -pdgId/abs(pdgId)

# Getter functor for lepton quantities
def lep_getter( branch, index, abs_pdg = None, functor = None, debug=False):
    if functor is not None:
        if abs_pdg == 13:
            def func_( event, sample ):
                if debug:
                    print("Returning", "Muon_%s"%branch, index, abs_pdg, "functor", functor, "result", end=' ')
                    print(functor(getattr( event, "Muon_%s"%branch )[event.lep_muIndex[index]]) if abs(event.lep_pdgId[index])==abs_pdg else float('nan'))
                return functor(getattr( event, "Muon_%s"%branch )[event.lep_muIndex[index]]) if abs(event.lep_pdgId[index])==abs_pdg else float('nan')
        else:
            def func_( event, sample ):
                return functor(getattr( event, "Electron_%s"%branch )[event.lep_eleIndex[index]]) if abs(event.lep_pdgId[index])==abs_pdg else float('nan')
    else:
        if abs_pdg == 13:
            def func_( event, sample ):
                if debug:
                    print("Returning", "Muon_%s"%branch, index, abs_pdg, "functor", functor, "result", end=' ')
                    print(getattr( event, "Muon_%s"%branch )[event.lep_muIndex[index]] if abs(event.lep_pdgId[index])==abs_pdg else float('nan'))
                return getattr( event, "Muon_%s"%branch )[event.lep_muIndex[index]] if abs(event.lep_pdgId[index])==abs_pdg else float('nan')
        else:
            def func_( event, sample ):
                return getattr( event, "Electron_%s"%branch )[event.lep_eleIndex[index]] if abs(event.lep_pdgId[index])==abs_pdg else float('nan')
    return func_

# We don't use tree formulas, but I leave them so you understand the syntax. TTreeFormulas are faster than if we compute things in the event loop.
ttreeFormulas = {   
#                    "nGenJet_absHF5":"Sum$(abs(GenJet_hadronFlavour)==5&&{genJetSelection})".format(genJetSelection=genJetSelection), 
    }

yields     = {}
allPlots   = {}
allModes   = ['mumu','mue', 'ee']
for i_mode, mode in enumerate(allModes):
    yields[mode] = {}

    # "event.weight" is 0/1 for data, depending on whether it is from a certified lumi section. For MC, it corresponds to the 1/fb*cross-section/Nsimulated. So we multiply with the lumi in /fb.
    # This weight goes to the plot.
    weight_ = lambda event, sample: event.weight if sample.isData else event.weight

    # coloring
    for sample in mc: sample.style = styles.fillStyle(sample.color)
    #TTTT.style = styles.lineStyle( ROOT.kBlack, width=2)
    if not args.noData:
        data_sample.style = styles.errorStyle( ROOT.kBlack ) 

    # read the MC variables only in MC; apply reweighting to simulation for specific detector effects
    for sample in mc:
      sample.read_variables = read_variables_MC 
      sample.weight = lambda event, sample: event.reweightBTag_SF*event.reweightPU*event.reweightL1Prefire*event.reweightTrigger#*event.reweightLeptonSF

    # Define what we want to see.
    stack = Stack(mc, [data_sample]) if not args.noData else Stack(mc)

    # Define everything we want to have common to all plots
    Plot.setDefaults(stack = stack, weight = staticmethod(weight_), selectionString = "("+getLeptonSelection(mode)+")&&("+cutInterpreter.cutString(args.selection)+")")
    
    plots = []

    # A special plot that holds the yields of all modes
    plots.append(Plot(
      name = 'yield', texX = '', texY = 'Number of Events',
      attribute = lambda event, sample: 0.5 + i_mode,
      binning=[3, 0, 3],
    ))

    for model in allModels:
        plots.append(Plot(
          name = 'MVA_TTTT_'+str(model),
          texX = 'prob for TTTT', texY = 'Number of Events / 20 GeV',
          attribute = lambda event, sample, model_name=model: getattr(event, model_name+"_TTTT"),
          #binning=Binning.fromThresholds([0, 0.5, 1, 2,3,4,10]),
          binning=[500,0,1],
          addOverFlowBin='upper',
        ))
        plots.append(Plot(
          name = 'MVA_TTLepbb_'+str(model),
          texX = 'prob for TTlepbb', texY = 'Number of Events / 20 GeV',
          attribute = lambda event, sample, model_name=model: getattr(event, model_name+"_TTB"),
          #binning=Binning.fromThresholds([0, 0.5, 1, 2,3,4,10]),
          binning=[500,0,1],
          addOverFlowBin='upper',
        ))
        plots.append(Plot(
          name = 'MVA_TTLepcc_'+str(model),
          texX = 'prob for TTlepcc', texY = 'Number of Events / 20 GeV',
          attribute = lambda event, sample, model_name=model: getattr(event, model_name+"_TTC"),
          #binning=Binning.fromThresholds([0, 0.5, 1, 2,3,4,10]),
          binning=[500,0,1],
          addOverFlowBin='upper',
        ))
        plots.append(Plot(
          name = 'MVA_TTLepOther_'+str(model),
          texX = 'prob for TTlepother', texY = 'Number of Events / 20 GeV',
          attribute = lambda event, sample, model_name=model: getattr(event, model_name+"_TTO"),
          #binning=Binning.fromThresholds([0, 0.5, 1, 2,3,4,10]),
          binning=[500,0,1],
          addOverFlowBin='upper',
        ))
# "mva_mT_l1"                  
# "mva_mT_l2"              
# "mva_ml_12"               
             
            
             
                
    
# "mva_mj_12"                  
# "mva_mlj_11"                 
# "mva_mlj_12"                 
    
# "mva_dPhil_12"               
# "mva_dPhij_12"               
    
# "mva_dEtal_12"               
# "mva_dEtaj_12"               
    
                    
# "mva_htb"                    
# "mva_ht_ratio"               
    
            
# "mva_jet0_eta"               
# "mva_jet0_btagDeepFlavB"     
                
# "mva_jet1_eta"               
# "mva_jet1_btagDeepFlavB"     
    
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

    # plots.append(Plot(
      # name = 'l1_eta',
      # texX = '#eta(l_{1})', texY = 'Number of Events',
      # attribute = lambda event, sample: event.l1_eta,
      # binning=[20,-3,3],
    # ))

    # plots.append(Plot(
      # name = 'l2_pt',
      # texX = 'p_{T}(l_{2}) (GeV)', texY = 'Number of Events / 20 GeV',
      # attribute = lambda event, sample:event.l2_pt,
      # binning=[15,0,300],
      # addOverFlowBin='upper',
    # ))

    # plots.append(Plot(
      # name = 'l2_eta',
      # texX = '#eta(l_{2})', texY = 'Number of Events',
      # attribute = lambda event, sample: event.l2_eta,
      # binning=[20,-3,3],
    # ))
  
    # plots.append(Plot(
      # texX = 'E_{T}^{miss} (GeV)', texY = 'Number of Events / 20 GeV',
      # attribute = TreeVariable.fromString( "met_pt/F" ),
      # binning=[20,0,400],
      # addOverFlowBin='upper',
    # ))


    # plots.append(Plot(
      # texX = 'p_{T}(leading l) (GeV)', texY = 'Number of Events / 20 GeV',
      # name = 'lep1_pt', attribute = lambda event, sample: event.lep_pt[0],
      # binning=[20,0,400],
    # ))

    # plots.append(Plot(
      # texX = 'p_{T}(subleading l) (GeV)', texY = 'Number of Events / 10 GeV',
      # name = 'lep2_pt', attribute = lambda event, sample: event.lep_pt[1],
      # binning=[20,0,200],
    # ))

    # plots.append(Plot(
      # texX = 'p_{T}(trailing l) (GeV)', texY = 'Number of Events / 10 GeV',
      # name = 'lep3_pt', attribute = lambda event, sample: event.lep_pt[2],
      # binning=[150,0,150],
    # ))

    # plots.append(Plot(
      # texX = 'N_{jets}', texY = 'Number of Events',
      # attribute = TreeVariable.fromString( "nJetGood/I" ), #nJetSelected
      # binning=[8,3.5,11.5],
    # ))

    # plots.append(Plot(
      # texX = 'N_{b-tag}', texY = 'Number of Events',
      # attribute = TreeVariable.fromString( "nBTag/I" ), #nJetSelected
      # binning=[5, 1.5,6.5],
    # ))

    # plots.append(Plot(
      # texX = 'H_{T} (GeV)', texY = 'Number of Events / 30 GeV',
      # name = 'ht', attribute = lambda event, sample: sum( j['pt'] for j in event.jets ),
      # binning=[30,0,1500],
    # ))

    # plots.append(Plot(
      # texX = 'p_{T}(leading jet) (GeV)', texY = 'Number of Events / 30 GeV',
      # name = 'jet0_pt', attribute = lambda event, sample: event.JetGood_pt[0],
      # binning=[20,0,600],
    # ))

    # plots.append(Plot(
      # texX = 'p_{T}(subleading jet) (GeV)', texY = 'Number of Events / 30 GeV',
      # name = 'jet1_pt', attribute = lambda event, sample: event.JetGood_pt[1],
      # binning=[20,0,600],
    # ))

    
    
    
    plotting.fill(plots, read_variables = read_variables, sequence = sequence, ttreeFormulas = ttreeFormulas, max_events=100 if args.small else -1)

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
        
    #yields[mode]["data"] = 0

    yields[mode]["MC"] = sum(yields[mode][s.name] for s in mc)
    if args.noData:
        dataMCScale = 1.
    else:
        dataMCScale        = yields[mode]["data"]/yields[mode]["MC"] if yields[mode]["MC"] != 0 else float('nan')

    drawPlots(plots, mode, dataMCScale)
    allPlots[mode] = plots

#Add the different channels into SF and all
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
