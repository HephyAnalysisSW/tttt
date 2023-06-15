#!/usr/bin/env python

#Standard imports
from operator                   import attrgetter
from math                       import pi, sqrt, cosh, cos, acos
import ROOT, os
import copy
import itertools

#From RootTools
from RootTools.core.standard     import *

#From Tools
from tttt.Tools.helpers          import deltaPhi, deltaR2, deltaR, getCollection, getObjDict
from tttt.Tools.objectSelection import isBJet, isAnalysisJet

from Analysis.Tools.WeightInfo       import WeightInfo

import logging
logger = logging.getLogger(__name__)

from Analysis.Tools.leptonJetArbitration     import cleanJetsAndLeptons

jetVars          = ['pt/F', 'eta/F', 'phi/F', 'btagDeepFlavB/F', 'btagDeepFlavCvB/F', 'btagDeepFlavQG/F','index/I']

jetVarNames      = [x.split('/')[0] for x in jetVars]

lstm_jets_maxN   = 10
lstm_jetVars     = ['pt/F', 'eta/F', 'phi/F', 'btagDeepFlavB/F', 'btagDeepFlavCvB/F', 'btagDeepFlavQG/F', 'puId/F', 'qgl/F']
lstm_jetVarNames = [x.split('/')[0] for x in lstm_jetVars]

lepVars          = ['pt/F','eta/F','phi/F','pdgId/I','cutBased/I','miniPFRelIso_all/F','pfRelIso03_all/F','mvaFall17V2Iso_WP90/O', 'mvaTOP/F', 'sip3d/F','lostHits/I','convVeto/I','dxy/F','dz/F','charge/I','deltaEtaSC/F','mediumId/I','eleIndex/I','muIndex/I']
lepVarNames      = [x.split('/')[0] for x in lepVars]

# Training variables
read_variables = [\
                    "nJet/I",
                    "nBTag/I",
                    "nJetGood/I",
                    "nlep/I",
                    "m3/F",
                    "JetGood[%s]"%(",".join(jetVars)),
                    "Jet[%s]"%(",".join(lstm_jetVars + ['mass/F'])),
                    "lep[%s]"%(",".join(lepVars)),
                    "met_pt/F", "met_phi/F",
                    "l1_pt/F",
                    "l1_eta/F",
                    "l1_phi/F",
                    "l2_pt/F",
                    "l2_eta/F",
                    "l2_phi/F",
                    "year/I",
                    ]
# sequence
sequence = []

# Fisher informations
FIs = {
}

from tttt.Tools.objectSelection import isBJet
def make_jets( event, sample ):
    event.jets     = [getObjDict(event, 'JetGood_', jetVarNames, i) for i in range(int(event.nJetGood))]
    event.bJets    = filter(lambda j:isBJet(j, year=event.year) and abs(j['eta'])<=2.4    , event.jets)
    event.nonbJets = []
    for b in event.jets:
        if b not in event.bJets:
            event.nonbJets.append(b)

    # store all btag flavors in a list
    event.btagDeepFlavB_scores = sorted([jet['btagDeepFlavB'] for jet in event.jets], reverse=True)

    # minDR of all btag combinations
    if len(event.bJets)>=2:
        event.min_dR_bb = min( [deltaR( comb[0], comb[1] ) for comb in itertools.combinations( event.bJets, 2)] )
    else:
        event.min_dR_bb = -1


sequence.append( make_jets )

def make_leptons(event, sample):
    event.leptons   = [getObjDict(event, 'lep_', lepVarNames, i) for i in range(int(event.nlep))]

     #(Second) smallest dR between any lepton and medium b-tagged jet
    dR_vals = sorted([deltaR(event.bJets[i], event.leptons[j]) for i in range(len(event.bJets)) for j in range(len(event.leptons))])
    if len(dR_vals)>=2:
        event.dR_min0 = dR_vals[0]
        event.dR_min1 = dR_vals[1]
    else:
        event.dR_min0 = -1
        event.dR_min1 = -1

sequence.append(make_leptons)

from Analysis.Tools.mt2Calculator import mt2Calculator
mt2Calculator = mt2Calculator()

def MT2(event, sample):
    # we must always have two leptons and two jets, hence no default needed.
    mt2Calculator.reset()
    mt2Calculator.setLeptons(event.l1_pt, event.l1_eta, event.l1_phi, event.l2_pt, event.l2_eta, event.l2_phi)
    mt2Calculator.setMet(event.met_pt, event.met_phi)
    event.mt2ll = mt2Calculator.mt2ll()

    b = (event.bJets + event.nonbJets)[:2]
    b1, b2 = b[0], b[1]

    mt2Calculator.setBJets(b1['pt'], b1['eta'], b1['phi'], b2['pt'], b2['eta'], b2['phi'])
    event.mt2bb = mt2Calculator.mt2bb()
    event.mt2blbl = mt2Calculator.mt2blbl()

sequence.append( MT2 )

all_mva_variables = {

     #Global Event Properties
     "mva_nJetGood"              :(lambda event, sample: event.nJetGood),

     #Lep Vars
     "mva_mT_l1"                 :(lambda event, sample: sqrt(2*event.l1_pt*event.met_pt*(1-cos(event.l1_phi-event.met_phi)))),
     "mva_mT_l2"                 :(lambda event, sample: sqrt(2*event.l2_pt*event.met_pt*(1-cos(event.l2_phi-event.met_phi)))),
     "mva_ml_12"                 :(lambda event, sample: sqrt(2*event.l1_pt*event.l2_pt*(cosh(event.l1_eta-event.l2_eta)-cos(event.l1_phi-event.l2_phi)))),
     "mva_l1_pt"                 :(lambda event, sample: event.l1_pt),
     "mva_l1_eta"                :(lambda event, sample: event.l1_eta),
     "mva_l2_pt"                 :(lambda event, sample: event.l2_pt),
     "mva_l2_eta"                :(lambda event, sample: event.l2_eta),

     #MET
     "mva_met_pt"                :(lambda event, sample: event.met_pt),

     "mva_mj_12"                 :(lambda event, sample: sqrt(2*event.jets[0]['pt']*event.jets[1]['pt']*(cosh(event.jets[0]['eta']-event.jets[1]['eta'])-cos(event.jets[0]['phi']-event.jets[1]['phi']))) if event.nJetGood >=2 else 0),
     "mva_mlj_11"                :(lambda event, sample: sqrt(2*event.l1_pt*event.jets[0]['pt']*(cosh(event.l1_eta-event.jets[0]['eta'])-cos(event.l1_phi-event.jets[0]['phi']))) if event.nJetGood >=1 else 0),
     "mva_mlj_12"                :(lambda event, sample: sqrt(2*event.l1_pt*event.jets[1]['pt']*(cosh(event.l1_eta-event.jets[1]['eta'])-cos(event.l1_phi-event.jets[1]['phi']))) if event.nJetGood >=2 else 0),

     # Use these when retraining:
     #"mva_dPhil_12"              :(lambda event, sample: deltaPhi(event.l1_phi, event.l2_phi)),
     #"mva_dPhij_12"              :(lambda event, sample: deltaPhi(event.JetGood_phi[0], event.JetGood_phi[1]) if event.nJetGood >=2 else 0),
     # Keep old version vor consistently evaluating:
     "mva_dPhil_12"              :(lambda event, sample: acos(cos(event.l1_phi-event.l2_phi))),
     "mva_dPhij_12"              :(lambda event, sample: acos(cos(event.JetGood_phi[0]-event.JetGood_phi[1])) if event.nJetGood >=2 else 0),

     "mva_dEtal_12"              :(lambda event, sample: abs(event.l1_eta-event.l2_eta)),
     "mva_dEtaj_12"              :(lambda event, sample: abs(event.JetGood_eta[0] - event.JetGood_eta[1]) if event.nJetGood >=2 else -10),

     "mva_ht"                    :(lambda event, sample: sum( [j['pt'] for j in event.jets] ) ),
     "mva_htb"                   :(lambda event, sample: sum( [j['pt'] for j in event.bJets] ) ),
     "mva_ht_ratio"              :(lambda event, sample: sum( [j['pt'] for j in event.jets[:4]])/ sum( [j['pt'] for j in event.jets ]) if event.nJetGood>=4 else 1 ),

     "mva_jet0_pt"               :(lambda event, sample: event.JetGood_pt[0]          if event.nJetGood >=1 else 0),
     "mva_jet0_eta"              :(lambda event, sample: event.JetGood_eta[0]         if event.nJetGood >=1 else -10),
     "mva_jet0_btagDeepFlavB"    :(lambda event, sample: event.JetGood_btagDeepFlavB[0]   if (event.nJetGood >=1 and event.JetGood_btagDeepFlavB[0]>-10) else -10),
     "mva_jet1_pt"               :(lambda event, sample: event.JetGood_pt[1]          if event.nJetGood >=2 else 0),
     "mva_jet1_eta"              :(lambda event, sample: event.JetGood_eta[1]         if event.nJetGood >=2 else -10),
     "mva_jet1_btagDeepFlavB"    :(lambda event, sample: event.JetGood_btagDeepFlavB[1]   if (event.nJetGood >=2 and event.JetGood_btagDeepFlavB[1]>-10) else -10),
     "mva_jet2_pt"               :(lambda event, sample: event.JetGood_pt[2]          if event.nJetGood >=3 else 0),
     "mva_jet2_eta"              :(lambda event, sample: event.JetGood_eta[2]         if event.nJetGood >=3 else -10),
     "mva_jet2_btagDeepFlavB"    :(lambda event, sample: event.JetGood_btagDeepFlavB[2]   if (event.nJetGood >=3 and event.JetGood_btagDeepFlavB[2]>-10) else -10),

     "mva_jet3_pt"               :(lambda event, sample: event.JetGood_pt[3]          if event.nJetGood >=4 else 0),
     "mva_jet4_pt"               :(lambda event, sample: event.JetGood_pt[4]          if event.nJetGood >=5 else 0),
     "mva_jet5_pt"               :(lambda event, sample: event.JetGood_pt[5]          if event.nJetGood >=6 else 0),
     "mva_jet6_pt"               :(lambda event, sample: event.JetGood_pt[6]          if event.nJetGood >=7 else 0),
     "mva_jet7_pt"               :(lambda event, sample: event.JetGood_pt[7]          if event.nJetGood >=8 else 0),

    # there is no other way to obtain a jet counting observale than to actually count the jets. "nJetGood" will always refer to the jet collection it was computed with.
    # the working points are already implemented in isBJet
     "mva_nBTagJetL"             :(lambda event, sample: len(filter( lambda j:isBJet(j, WP="loose"),  event.jets ))),
     "mva_nBTagJetM"             :(lambda event, sample: len(filter( lambda j:isBJet(j, WP="medium"), event.jets ))),
     "mva_nBTagJetT"             :(lambda event, sample: len(filter( lambda j:isBJet(j, WP="tight"),  event.jets ))),
     "mva_dR_min0"               :(lambda event, sample: event.dR_min0),
     "mva_dR_min1"               :(lambda event, sample: event.dR_min1),
     #Smallest dR between two b-tagged jets
     "mva_min_dR_bb"             :(lambda event, sample: event.min_dR_bb),
     #dR between leading/subleading lepton
     "mva_dR_2l"                 :(lambda event, sample: sqrt(deltaPhi(event.l1_phi, event.l2_phi)**2 + (event.l1_eta - event.l2_eta)**2)),
     #Highest mass to pT ratio of any selected jet
     "mva_mpt_ratio"             :(lambda event, sample: max([(event.Jet_mass[event.JetGood_index[i]]/event.JetGood_pt[i]) for i in range(event.nJetGood)]) if event.nJetGood>=1 else 0),
     #Mt2 mass lepton + b-jet
     "mva_mt2ll"                 :(lambda event, sample : event.mt2ll),
     "mva_mt2bb"                 :(lambda event, sample : event.mt2bb),
     "mva_mt2blbl"               :(lambda event, sample : event.mt2blbl),
     "mva_bTagScore_max0"        :(lambda event, sample: event.btagDeepFlavB_scores[0] if len(event.btagDeepFlavB_scores)>0 else -1),
     "mva_bTagScore_max1"        :(lambda event, sample: event.btagDeepFlavB_scores[1] if len(event.btagDeepFlavB_scores)>1 else -1),
     "mva_bTagScore_max2"        :(lambda event, sample: event.btagDeepFlavB_scores[2] if len(event.btagDeepFlavB_scores)>2 else -1),
     "mva_bTagScore_max3"        :(lambda event, sample: event.btagDeepFlavB_scores[3] if len(event.btagDeepFlavB_scores)>3 else -1),
}

def lstm_jets(event, sample):
    jets = [ getObjDict( event, 'Jet_', lstm_jetVarNames, event.JetGood_index[i] ) for i in range(int(event.nJetGood)) ]
    #jets = filter( jet_vector_var['selector'], jets )
    return jets

# for the filler
mva_vector_variables    =   {
    #"mva_Jet":  {"name":"Jet", "vars":lstm_jetVars, "varnames":lstm_jetVarNames, "selector": (lambda jet: True), 'maxN':10}
    "mva_Jet":  {"func":lstm_jets, "name":"Jet", "vars":lstm_jetVars, "varnames":lstm_jetVarNames}
}

## Using all variables
mva_variables_ = all_mva_variables.keys()
mva_variables_.sort()
mva_variables  = [ (key, value) for key, value in all_mva_variables.iteritems() if key in mva_variables_ ]

import numpy as np
import operator

def predict_inputs( event, sample, jet_lstm = False):
    flat_variables = np.array([[getattr( event, mva_variable) for mva_variable, _ in mva_variables]])
    if jet_lstm:
        lstm_jets_maxN = 10 #remove after retraining
        jet_vector_var = mva_vector_variables["mva_Jet"]
        jets = mva_vector_variables["mva_Jet"]["func"](event,sample=None)
        jets =  [ [ operator.itemgetter(varname)(jet) for varname in lstm_jetVarNames] for jet in jets[:lstm_jets_maxN] ]
        # zero padding
        jets += [ [0.]*len(lstm_jetVarNames)]*(max(0, lstm_jets_maxN-len(jets)))
        jets = np.array([jets])

        return  flat_variables, jets
    else:
        return  flat_variables

#define training samples for multiclassification
import tttt.samples.nano_private_UL20_RunII_postProcessed_dilep as samples

# ttbar gen classification: https://github.com/cms-top/cmssw/blob/topNanoV6_from-CMSSW_10_2_18/TopQuarkAnalysis/TopTools/plugins/GenTtbarCategorizer.cc
sample_TTLep = samples.TTLepbb
# ttbar gen classification: https://github.com/cms-top/cmssw/blob/topNanoV6_from-CMSSW_10_2_18/TopQuarkAnalysis/TopTools/plugins/GenTtbarCategorizer.cc

TTLep_bb    = copy.deepcopy( sample_TTLep )
TTLep_bb.name = "TTLep_bb"
TTLep_bb.texName = "t#bar{t}b#bar{b}"
TTLep_bb.color   = ROOT.kRed + 2
TTLep_bb.setSelectionString( "genTtbarId%100>=50&&overlapRemoval" )
TTLep_cc    = copy.deepcopy( sample_TTLep )
TTLep_cc.name = "TTLep_cc"
TTLep_cc.texName = "t#bar{t}c#bar{c}"
TTLep_cc.color   = ROOT.kRed - 3
TTLep_cc.setSelectionString( "genTtbarId%100>=40&&genTtbarId%100<50&&overlapRemoval" )
TTLep_other = copy.deepcopy( sample_TTLep )
TTLep_other.name = "TTLep_other"
TTLep_other.texName = "t#bar{t} + light j."
TTLep_other.setSelectionString( "genTtbarId%100<40&&overlapRemoval" )

training_samples = [ samples.TTTT, TTLep_bb, TTLep_cc, TTLep_other]#, samples.ST, samples.TTW, samples.TTH, samples.TTZ]
classes          = [ "2l_4t",      "2l_ttbb","2l_ttcc","2l_ttlight"]

assert len(training_samples)==len(set([s.name for s in training_samples])), "training_samples names are not unique!"

# training selection

selection = 'trg-dilepVL-minDLmass20-offZ1-njet4p-btag3p-ht500'
from tttt.Tools.cutInterpreter import cutInterpreter
selectionString = cutInterpreter.cutString( selection )
