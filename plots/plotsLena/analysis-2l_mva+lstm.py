#!/usr/bin/env python
''' Analysis script for standard plots
'''

# Standard imports and batch mode
import ROOT, os
import itertools
import copy
import array
import operator
from   math                              import sqrt, cos, sin, pi, atan2, cosh

# RootTools
from RootTools.core.standard             import *
from ROOT                                import TGraph, TCanvas

# tttt
from tttt.Tools.user                     import plot_directory
from tttt.Tools.cutInterpreter           import cutInterpreter
from tttt.Tools.objectSelection          import lepString 

# Analysis
from Analysis.Tools.helpers              import deltaPhi, deltaR
from Analysis.Tools.puProfileCache       import *
from Analysis.Tools.puReweighting        import getReweightingFunction
#import Analysis.Tools.syncer
import numpy as np
import matplotlib.pyplot as plt

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',       action='store',      default='INFO', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--small',                             action='store_true', help='Run only on a small subset of the data?', )
#argParser.add_argument('--sorting',                           action='store', default=None, choices=[None, "forDYMB"],  help='Sort histos?', )
argParser.add_argument('--dataMCScaling',  action='store_true', help='Data MC scaling?', )
argParser.add_argument('--plot_directory', action='store', default='TMB_4t')
argParser.add_argument('--selection',      action='store', default='dilepL-offZ1-njet4p-btag2p-ht500')
args = argParser.parse_args()

# Logger
import tttt.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

if args.small:args.plot_directory += "_small"

from tttt.samples.nano_private_UL20_RunII_postProcessed_dilep import *

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

mc = [ TTLep_bb,TTLep_cc,TTLep_other] #, TTW, TTH, TTZ] 

all_mc = mc + [TTTT]
lumi_scale = 137

for sample in all_mc:
    sample.scale           = 1 

if args.small:
    for sample in all_mc:
        sample.normalization = 1.
        sample.reduceFiles( to = 1 )
        #sample.reduceFiles( to=1)
        sample.scale /= sample.normalization

# Text on the plots
tex = ROOT.TLatex()
tex.SetNDC()
tex.SetTextSize(0.04)
tex.SetTextAlign(11) # align right

def charge(pdgId):
    return -pdgId//abs(pdgId)

def drawObjects( dataMCScale, lumi_scale ):
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
      if isinstance( plot, TGraph):
          plotting.draw(plot,
            plot_directory = plot_directory_,
            #ratio = None,
            logX = False, logY = False, sorting = True,
            #yRange = (0.9, "auto") if log else (0.001, "auto"),
            #scaling = {0:1} if args.dataMCScaling else {},
            #legend = ( (0.18,0.88-0.03*sum(map(len, plot.histos)),0.9,0.88), 2),
            #drawObjects = drawObjects( dataMCScale , lumi_scale ) + _drawObjects,
            copyIndexPHP = True, extensions = ["png", "pdf"],
          )
      
# Read variables and sequences
sequence       = []

from tttt.Tools.objectSelection import isBJet
from tttt.Tools.helpers import getObjDict
jetVars          = ['pt/F', 'eta/F', 'phi/F', 'btagDeepB/F', 'btagDeepFlavB/F', 'index/F']
#jetVars          = ['pt/F', 'eta/F', 'phi/F', 'btagDeepFlavB/F', 'btagDeepFlavCvB/F', 'btagDeepFlavQG/F','index/I']
jetVarNames      = [x.split('/')[0] for x in jetVars]
def make_jets( event, sample ):
    event.jets     = [getObjDict(event, 'JetGood_', jetVarNames, i) for i in range(int(event.nJetGood))] 
    event.bJets    = [j for j in event.jets if isBJet(j, year=event.year) and abs(j['eta'])<=2.4]
sequence.append( make_jets )

#MVA
import tttt_2l_lena as config
import onnxruntime as ort
read_variables = config.read_variables


# Add sequence that computes the MVA inputs

def mva_eval (event, sample):
    for mva_variable, func in config.mva_variables:
        val = func(event, sample)
        setattr( event, mva_variable, val )
    flat_variables, lstm_jets = config.predict_inputs( event, sample, jet_lstm = True)
    lstm_jets = np.nan_to_num(lstm_jets)
    if (LSTM):
        lis = ort_sess.run(["output1"], {"input1": flat_variables.astype(np.float32),"input2": lstm_jets.astype(np.float32)})[0][0] 
    else:
        lis = ort_sess.run(["output1"], {"input1": flat_variables.astype(np.float32)})[0][0] 
    setattr( event, model, lis[0] )
    es.append(lis[0])
    eb.append(lis[1])
    eb.append(lis[2])
    eb.append(lis[3])

sequence.append(mva_eval)


read_variables = []

# the following we read for both, data and simulation 
lepVars          = ['pt/F','eta/F','phi/F','pdgId/I','cutBased/I','miniPFRelIso_all/F','pfRelIso03_all/F','mvaFall17V2Iso_WP90/O', 'mvaTOP/F', 'sip3d/F','lostHits/I','convVeto/I','dxy/F','dz/F','charge/I','deltaEtaSC/F','mediumId/I','eleIndex/I','muIndex/I']

read_variables += [
    "weight/F", "year/I", "met_pt/F", "met_phi/F", "nBTag/I", "nJetGood/I", "PV_npvsGood/I",
    "l1_pt/F", "l1_eta/F" , "l1_phi/F", "l1_mvaTOP/F", "l1_mvaTOPWP/I", "l1_index/I", 
    "l2_pt/F", "l2_eta/F" , "l2_phi/F", "l2_mvaTOP/F", "l2_mvaTOPWP/I", "l2_index/I",
    "JetGood[%s]"%(",".join(jetVars)),
    "lep[pt/F,eta/F,phi/F,pdgId/I,muIndex/I,eleIndex/I]",
    "Z1_l1_index/I", "Z1_l2_index/I", #"nonZ1_l1_index/I", "nonZ1_l2_index/I", 
    "Z1_phi/F", "Z1_pt/F", "Z1_mass/F", "Z1_cosThetaStar/F", "Z1_eta/F", "Z1_lldPhi/F", "Z1_lldR/F",
    "Muon[pt/F,eta/F,phi/F,dxy/F,dz/F,ip3d/F,sip3d/F,jetRelIso/F,miniPFRelIso_all/F,pfRelIso03_all/F,mvaTTH/F,pdgId/I,segmentComp/F,nStations/I,nTrackerLayers/I]",
    "Electron[pt/F,eta/F,phi/F,dxy/F,dz/F,ip3d/F,sip3d/F,jetRelIso/F,miniPFRelIso_all/F,pfRelIso03_all/F,mvaTTH/F,pdgId/I,vidNestedWPBitmap/I]",
    "nlep/I", "m3/F",
    "lep[%s]"%(",".join(lepVars)),
]

# define 3l selections
# the following we read only in simulation
read_variables_MC = [
    'reweightBTag_SF/F', 'reweightPU/F', 'reweightL1Prefire/F', 'reweightLeptonSF/F', 'reweightTrigger/F',
    "GenJet[pt/F,eta/F,phi/F,partonFlavour/I,hadronFlavour/i]"
    ]

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


genJetSelection = "GenJet_pt>30&&abs(GenJet_eta)<2.4"

ttreeFormulas = {   
                    "nGenJet_absHF5":"Sum$(abs(GenJet_hadronFlavour)==5&&{genJetSelection})".format(genJetSelection=genJetSelection), 
                    "nGenJet_absPF5":"Sum$(abs(GenJet_partonFlavour)==5&&{genJetSelection})".format(genJetSelection=genJetSelection),
    }


yields     = {}
allPlots   = {}
allModes   = ['mumu','mue', 'ee']
allModels  = [ "model1","model2","model3","model4","model5","model6","model7","model8","model9","model10","model11","model1_lstm","model2_lstm","model4_lstm","model6_lstm", "model8_lstm", "model1_db_lstm","model2_db_lstm","model4_db_lstm","model6_db_lstm","model8_db_lstm" ]
weight_ = lambda event, sample: event.weight if sample.isData else event.weight
for sample in mc: sample.style = styles.fillStyle(sample.color)
TTTT.style = styles.lineStyle( ROOT.kBlack, width=2)

for sample in all_mc:
    sample.read_variables = read_variables_MC 
    sample.weight = lambda event, sample: event.reweightBTag_SF*event.reweightPU*event.reweightL1Prefire*event.reweightTrigger#*event.reweightLeptonSF
    
    #yt_TWZ_filter.scale = lumi_scale * 1.07314
    stack = Stack(mc, TTTT)

fig, ax = plt.subplots(figsize=(15,10))
for j, model in enumerate (allModels):
    # ONNX load
    es = []
    eb = []
    options = ort.SessionOptions()
    options.intra_op_num_threads = 1
    options.inter_op_num_threads = 1
    ort_sess = ort.InferenceSession(model+".onnx", providers = ['CPUExecutionProvider'],sess_options=options)
    LSTM = False
    if (str(model).find('lstm')!=-1): LSTM = True
    model=model+str("_v4")
    for i_mode, mode in enumerate(allModes):
        yields[mode] = {}
    
        
    
        # Use some defaults
        Plot.setDefaults(stack = stack, weight = staticmethod(weight_), selectionString = "("+getLeptonSelection(mode)+")&&("+cutInterpreter.cutString(args.selection)+")")
    
        plots = []
    
        plots.append(Plot(
            name = 'yield', texX = '', texY = 'Number of Events',
            attribute = lambda event, sample: 0.5 + i_mode,
            binning=[3, 0, 3],
        ))
    
        plots.append(Plot(
            name = 'lenas_MVA_TTTT_'+str(model),
            texX = 'prob acc to lena for TTTT', texY = 'Number of Events / 20 GeV',
            #attribute = lambda event, sample:event.(str(model)),
            attribute = lambda event, sample, model_name=model: getattr(event, model_name),
            binning=[50,0,1],
            addOverFlowBin='upper',
        ))
        
        
        
        for index in range(2):
            for abs_pdg in [11, 13]:
                lep_name = "mu" if abs_pdg==13 else "ele"
               
                if lep_name == "mu":
                    pass
                   
    
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
    
    for i in range(1,51): print (plots[-1].histos[0][0].GetBinContent(i))  
    #hist1, _ = np.histogram(es, 50, range=(0, 1))
    #hist2, _ = np.histogram(eb, 50, range=(0, 1))
    #f1 = np.sum(hist1)
    #f2 = np.sum(hist2)
    #ef1 = []
    #ef2 = []
    #x1 = 0
    #x2 = 0
    #for i in range (50):
     #   x1 += hist1[50-1-i]
     #   ef1.append(x1/f1)
     #   x2 += hist2[50-1-i]
     #   ef2.append(x2/f2)


    #results_dir = './'
    #sample_file_name = "Efficiency.png"
    #ax.scatter(ef1,ef2, label = str(model))
    #plt.legend()
    #plt.xlabel("sample efficiency")
    #plt.ylabel("background efficiency")
    #plt.savefig(results_dir + sample_file_name)
      
      

#plot_directory_ = os.path.join(plot_directory, 'analysisPlots', args.plot_directory, 'RunIII', mode + "_log", args.selection)




logger.info( "Done with prefix %s and selectionString %s", args.selection, cutInterpreter.cutString(args.selection) )
