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
#argParser.add_argument('--sorting',                           action='store', default=None, choices=[None, "forDYMB"],  help='Sort histos?', )
argParser.add_argument('--dataMCScaling',  action='store_true', help='Data MC scaling?')
argParser.add_argument('--plot_directory', action='store', default='TMB_4t_p3_bin50')
argParser.add_argument('--selection',      action='store', default='dilepL-offZ1-njet4p-btag2p-ht500')
argParser.add_argument('--mva',      action='store', default='dilepL-offZ1-njet4p-btag2p-ht500')
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
    # plot_directory_cut_ = os.path.join(plot_directory,'analysisPlots', args.plot_directory, 'RunII', mode + ("_log" if log else ""), '_cut_y', args.selection)
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
      # if isinstance( plot, Plot):
          # plotting.draw(plot,
            # plot_directory = plot_directory_cut_,
            # ratio =  {'yRange':(0.1,1.9)} if not args.noData else None,
            # logX = False, logY = log, sorting = True,
            # yRange = (0.001, 6) if log else (0.001, "auto"),
            # scaling = {0:1} if args.dataMCScaling else {},
            # legend = ( (0.18,0.88-0.03*sum(map(len, plot.histos)),0.9,0.88), 2),
            # drawObjects = drawObjects( dataMCScale , lumi_scale ) + _drawObjects,
            # copyIndexPHP = True, extensions = ["png", "pdf", "root"],
          # )           

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
import tttt_2l_lena as config
import onnxruntime as ort
read_variables += config.read_variables
test = []

# Add sequence that computes the MVA inputs

# Add sequence that computes the MVA inputs
def make_mva_inputs( event, sample ):
   for mva_variable, func in config.mva_variables:
       setattr( event, mva_variable, func(event, sample) )
sequence.append( make_mva_inputs ) 

allModels = []
allModels.append(config.Models[int(args.mva)])
options = ort.SessionOptions()
options.intra_op_num_threads = 1
options.inter_op_num_threads = 1

def torch_predict( event, sample ):
    flat_variables, lstm_jets_nodb = config.predict_inputs( event, sample, db = False, jet_lstm = True)
    _, lstm_jets_db = config.predict_inputs( event, sample, db = True, jet_lstm = True)
    lstm_jets_nodb = np.nan_to_num(lstm_jets_nodb)
    lstm_jets_db = np.nan_to_num(lstm_jets_db)
    #print(lstm_jets_db[:, 1, 6],lstm_jets_nodb[:, 1, 6])
    #print(np.sum(lstm_jets_db[:, :, :])-np.sum(lstm_jets_nodb[:, :, :]))
    # print(lstm_jets_nodb[:, 0])
    #assert False
    #print('\n',flat_variables.shape, '\n',lstm_jets_db.shape, '\n',lstm_jets_nodb.shape, '\n')
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

    # for model in allModels:
        # plots.append(Plot(
          # name = 'MVA_TTTT_'+str(model),
          # texX = 'prob for TTTT', texY = 'Number of Events / 20 GeV',
          # attribute = lambda event, sample, model_name=model: getattr(event, model_name+"_TTTT"),
          ##binning=Binning.fromThresholds([0, 0.5, 1, 2,3,4,10]),
          # binning=[500,0,1],
          # addOverFlowBin='upper',
        # ))
        # plots.append(Plot(
          # name = 'MVA_TTLepbb_'+str(model),
          # texX = 'prob for TTlepbb', texY = 'Number of Events / 20 GeV',
          # attribute = lambda event, sample, model_name=model: getattr(event, model_name+"_TTB"),
          ##binning=Binning.fromThresholds([0, 0.5, 1, 2,3,4,10]),
          # binning=[500,0,1],
          # addOverFlowBin='upper',
        # ))
        # plots.append(Plot(
          # name = 'MVA_TTLepcc_'+str(model),
          # texX = 'prob for TTlepcc', texY = 'Number of Events / 20 GeV',
          # attribute = lambda event, sample, model_name=model: getattr(event, model_name+"_TTC"),
          ##binning=Binning.fromThresholds([0, 0.5, 1, 2,3,4,10]),
          # binning=[500,0,1],
          # addOverFlowBin='upper',
        # ))
        # plots.append(Plot(
          # name = 'MVA_TTLepOther_'+str(model),
          # texX = 'prob for TTlepother', texY = 'Number of Events / 20 GeV',
          # attribute = lambda event, sample, model_name=model: getattr(event, model_name+"_TTO"),
          ##binning=Binning.fromThresholds([0, 0.5, 1, 2,3,4,10]),
          # binning=[500,0,1],
          # addOverFlowBin='upper',
        # ))
        

    plots.append(Plot(
      name = 'nVtxs', 
      texX = 'vertex multiplicity', texY = 'Number of Events',
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
        # name = "2mva_nBTag",
        # texX = 'N_{b}', texY = 'Number of Events / 20 GeV',
        # attribute = config.all_mva_variables["mva_nBTag"],
        # binning=[2,3,5],
        # addOverFlowBin='upper',
    # ))

    # plots.append(Plot(
        # name = "1mva_nJetGood",
        # texX = 'N_{jet}', texY = 'Number of Events / 20 GeV',
        # attribute = config.all_mva_variables["mva_nJetGood"],
        # binning=[6,4,10],
        # addOverFlowBin='upper',
    # ))
    
    # plots.append(Plot(
        # name = "3mva_nlep",
        # texX = 'N_{\ell}', texY = 'Number of Events / 20 GeV',
        # attribute = config.all_mva_variables["mva_nlep"],
        # binning=[30,2,3],
        # addOverFlowBin='upper',
    # ))
    
    plots.append(Plot(
        name = "4mva_mT_l1",
        texX = 'm_{T, \ell 1}', texY = 'Number of Events / 20 GeV',
        attribute = config.all_mva_variables["mva_mT_l1"],
        binning=[15,-20,300],
        addOverFlowBin='upper',
    ))
    
    plots.append(Plot(
        name = "5mva_mT_l2",
        texX = 'm_{T, \ell 2}', texY = 'Number of Events / 20 GeV',
        attribute = config.all_mva_variables["mva_mT_l2"],
        binning=[20,-20,300],
        addOverFlowBin='upper',
    ))
      
    # plots.append(Plot(
        # name = "35mva_ml_12",
        # texX = 'm_{T, 12}', texY = 'Number of Events / 20 GeV',
        # attribute = config.all_mva_variables["mva_ml_12"],
        # binning=[15,0,300],
        # addOverFlowBin='upper',
    # ))

    # plots.append(Plot(
        # name = "6mva_met_pt"  ,
        # texX = 'E_{t}^{miss}', texY = 'Number of Events / 20 GeV',
        # attribute = config.all_mva_variables["mva_met_pt"],
        # binning=[15,0,300],
        # addOverFlowBin='upper',
    # ))  

    # plots.append(Plot(
        # name = "7mva_l1_pt"   ,
        # texX = 'p_{T,\ell 1} (GeV)', texY = 'Number of Events / 20 GeV',
        # attribute = config.all_mva_variables["mva_l1_pt"],
        # binning=[15,0,300],
        # addOverFlowBin='upper',
    # ))    
    
    # plots.append(Plot(
        # name = "8mva_l1_eta" ,
        # texX = '\eta_{\ell 1}', texY = 'Number of Events / 20 GeV',
        # attribute = config.all_mva_variables["mva_l1_eta"],
        # binning=[15,0,300],
        # addOverFlowBin='upper',
    # ))    
    
    # plots.append(Plot(
        # name = "9mva_l2_pt"  ,
        # texX = 'p_{T,\ell 2}', texY = 'Number of Events / 20 GeV',
        # attribute = config.all_mva_variables["mva_l2_pt"],
        # binning=[15,0,300],
        # addOverFlowBin='upper',
    # ))   

    # plots.append(Plot(
        # name = "10mva_l2_eta"  ,
        # texX = '\eta_{\ell 2}', texY = 'Number of Events / 20 GeV',
        # attribute = config.all_mva_variables["mva_l2_eta"],
        # binning=[15,0,300],
        # addOverFlowBin='upper',
    # ))   
    
    # plots.append(Plot(
        # name = "11mva_mj_12"  ,
        # texX = 'm_{jet, 12}', texY = 'Number of Events / 20 GeV',
        # attribute = config.all_mva_variables["mva_mj_12"],
        # binning=[15,0,300],
        # addOverFlowBin='upper',
    # )) 

    # plots.append(Plot(
        # name = "12mva_mlj_11"  ,
        # texX = 'm_{T, jet 1}', texY = 'Number of Events / 20 GeV',
        # attribute = config.all_mva_variables["mva_mlj_11"],
        # binning=[15,0,300],
        # addOverFlowBin='upper',
    # )) 
       
    # plots.append(Plot(
        # name = "13mva_mlj_12"  ,
        # texX = 'm_{T, jet 2}', texY = 'Number of Events / 20 GeV',
        # attribute = config.all_mva_variables["mva_mlj_12"],
        # binning=[15,0,300],
        # addOverFlowBin='upper',
    # ))   
    
    # plots.append(Plot(
        # name = "14mva_dPhil_12"  ,
        # texX = '\Delta\phi_{\ell}', texY = 'Number of Events / 20 GeV',
        # attribute = config.all_mva_variables["mva_dPhil_12"],
        # binning=[15,0,300],
        # addOverFlowBin='upper',
    # )) 

    # plots.append(Plot(
        # name = "15mva_dPhij_12"  ,
        # texX = '\Delta\phi_{jet}', texY = 'Number of Events / 20 GeV',
        # attribute = config.all_mva_variables["mva_dPhij_12"],
        # binning=[15,0,300],
        # addOverFlowBin='upper',
    # )) 

    # plots.append(Plot(
        # name = "16mva_dEtal_12"  ,
        # texX = '\Delta\eta_{\ell}', texY = 'Number of Events / 20 GeV',
        # attribute = config.all_mva_variables["mva_dEtal_12"],
        # binning=[15,0,300],
        # addOverFlowBin='upper',
    # )) 

    # plots.append(Plot(
        # name = "17mva_dEtaj_12"  ,
        # texX = '\Delta\eta_{jet}', texY = 'Number of Events / 20 GeV',
        # attribute = config.all_mva_variables["mva_dEtaj_12"],
        # binning=[15,0,300],
        # addOverFlowBin='upper',
    # )) 
    
    # plots.append(Plot(
        # name = "18mva_ht"  ,
        # texX = 'H_{T}', texY = 'Number of Events / 20 GeV',
        # attribute = config.all_mva_variables["mva_ht"],
        # binning=[15,0,300],
        # addOverFlowBin='upper',
    # )) 

    # plots.append(Plot(
        # name = "19mva_htb"  ,
        # texX = 'H_{T,b}', texY = 'Number of Events / 20 GeV',
        # attribute = config.all_mva_variables["mva_htb"],
        # binning=[15,0,300],
        # addOverFlowBin='upper',
    # )) 
    
    # plots.append(Plot(
        # name = "20mva_ht_ratio"  ,
        # texX = '\Delta H_{T}', texY = 'Number of Events / 20 GeV',
        # attribute = config.all_mva_variables["mva_ht_ratio"],
        # binning=[15,0,300],
        # addOverFlowBin='upper',
    # )) 

    # plots.append(Plot(
        # name = "21mva_jet0_pt"  ,
        # texX = 'p_{T}(j_{0}) (GeV)', texY = 'Number of Events / 20 GeV',
        # attribute = config.all_mva_variables["mva_jet0_pt"],
        # binning=[15,0,300],
        # addOverFlowBin='upper',
    # )) 
    
    # plots.append(Plot(
        # name = "22mva_jet0_eta"  ,
        # texX = 'p_{T}(l_{1}) (GeV)', texY = 'Number of Events / 20 GeV',
        # attribute = config.all_mva_variables["mva_jet0_eta"],
        # binning=[15,0,300],
        # addOverFlowBin='upper',
    # )) 
       
    # plots.append(Plot(
        # name = "23mva_jet0_btagDeepFlavB"  ,
        # texX = 'p_{T}(l_{1}) (GeV)', texY = 'Number of Events / 20 GeV',
        # attribute = config.all_mva_variables["mva_jet0_btagDeepFlavB"],
        # binning=[15,0,300],
        # addOverFlowBin='upper',
    # ))   
    
    # plots.append(Plot(
        # name = "24mva_jet1_pt"  ,
        # texX = 'p_{T}(j_{1}) (GeV)', texY = 'Number of Events / 20 GeV',
        # attribute = config.all_mva_variables["mva_jet1_pt"],
        # binning=[15,0,300],
        # addOverFlowBin='upper',
    # )) 

    # plots.append(Plot(
        # name = "25mva_jet1_eta"  ,
        # texX = 'p_{T}(l_{1}) (GeV)', texY = 'Number of Events / 20 GeV',
        # attribute = config.all_mva_variables["mva_jet1_eta"],
        # binning=[15,0,300],
        # addOverFlowBin='upper',
    # )) 

    # plots.append(Plot(
        # name = "26mva_jet1_btagDeepFlavB"  ,
        # texX = 'p_{T}(l_{1}) (GeV)', texY = 'Number of Events / 20 GeV',
        # attribute = config.all_mva_variables["mva_jet1_btagDeepFlavB"],
        # binning=[15,0,300],
        # addOverFlowBin='upper',
    # )) 

    # plots.append(Plot(
        # name = "27mva_jet2_pt"  ,
        # texX = 'p_{T}(j_{2}) (GeV) (GeV)', texY = 'Number of Events / 20 GeV',
        # attribute = config.all_mva_variables["mva_jet2_pt"],
        # binning=[15,0,300],
        # addOverFlowBin='upper',
    # )) 
    
    # plots.append(Plot(
        # name = "28mva_jet2_eta"  ,
        # texX = 'p_{T}(l_{1}) (GeV)', texY = 'Number of Events / 20 GeV',
        # attribute = config.all_mva_variables["mva_jet2_eta"],
        # binning=[15,0,300],
        # addOverFlowBin='upper',
    # )) 

    # plots.append(Plot(
        # name = "29mva_jet2_btagDeepFlavB"  ,
        # texX = 'p_{T}(l_{1}) (GeV)', texY = 'Number of Events / 20 GeV',
        # attribute = config.all_mva_variables["mva_jet2_btagDeepFlavB"],
        # binning=[15,0,300],
        # addOverFlowBin='upper',
    # )) 
    
    # plots.append(Plot(
        # name = "30mva_jet3_pt"  ,
        # texX = 'p_{T}(j_{3}) (GeV) (GeV)', texY = 'Number of Events / 20 GeV',
        # attribute = config.all_mva_variables["mva_jet3_pt"],
        # binning=[15,0,300],
        # addOverFlowBin='upper',
    # )) 

    # plots.append(Plot(
        # name = "31mva_jet4_pt"  ,
        # texX = 'p_{T}(j_{4}) (GeV) (GeV)', texY = 'Number of Events / 20 GeV',
        # attribute = config.all_mva_variables["mva_jet4_pt"],
        # binning=[15,0,300],
        # addOverFlowBin='upper',
    # )) 
    
    # plots.append(Plot(
        # name = "32mva_jet5_pt"  ,
        # texX = 'p_{T}(j_{5}) (GeV)', texY = 'Number of Events / 20 GeV',
        # attribute = config.all_mva_variables["mva_jet5_pt"],
        # binning=[15,0,300],
        # addOverFlowBin='upper',
    # ))
    
    # plots.append(Plot(
        # name = "33mva_jet6_pt"  ,
        # texX = 'p_{T}(j_{6}) (GeV) (GeV)', texY = 'Number of Events / 20 GeV',
        # attribute = config.all_mva_variables["mva_jet6_pt"],
        # binning=[15,0,300],
        # addOverFlowBin='upper',
    # ))
    
    # plots.append(Plot(
        # name = "34mva_jet7_pt"  ,
        # texX = 'p_{T}(j_{7}) (GeV) (GeV)', texY = 'Number of Events / 20 GeV',
        # attribute = config.all_mva_variables["mva_jet7_pt"],
        # binning=[15,0,300],
        # addOverFlowBin='upper',
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
