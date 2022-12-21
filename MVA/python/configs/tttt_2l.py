#!/usr/bin/env python

#Standard imports
from operator                   import attrgetter
from math                       import pi, sqrt, cosh, cos, acos
import ROOT, os
import copy

#From RootTools
from RootTools.core.standard     import *

#From Tools
from tttt.Tools.helpers          import deltaPhi, deltaR2, deltaR, getCollection, getObjDict, MT2
from tttt.Tools.objectSelection import isBJet, isAnalysisJet

from Analysis.Tools.WeightInfo       import WeightInfo

import logging
logger = logging.getLogger(__name__)

from Analysis.Tools.leptonJetArbitration     import cleanJetsAndLeptons

jetVars          = ['pt/F', 'eta/F', 'phi/F', 'btagDeepFlavB/F', 'btagDeepFlavCvB/F', 'btagDeepFlavQG/F','index/I']

jetVarNames      = [x.split('/')[0] for x in jetVars]

lstm_jets_maxN   = 10
lstm_jetVars     = ['pt/F', 'eta/F', 'phi/F', 'btagDeepFlavB/F', 'btagDeepFlavCvB/F', 'btagDeepFlavQG/F', 'btagDeepFlavb/F', 'btagDeepFlavbb/F', 'btagDeepFlavlepb/F', 'btagDeepb/F', 'btagDeepbb/F', 'chEmEF/F', 'chHEF/F', 'neEmEF/F', 'neHEF/F', 'muEF/F', 'puId/F', 'qgl/F','mass/F']
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
                    "Jet[%s]"%(",".join(lstm_jetVars)),
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
sequence.append( make_jets )

def make_leptons(event, sample):
    event.leptons   = [getObjDict(event, 'lep_', lepVarNames, i) for i in range(int(event.nlep))]
sequence.append(make_leptons)


from Analysis.Tools.mt2Calculator import mt2Calculator
mt2Calculator = mt2Calculator()

all_mva_variables = {

# global event properties
     "mva_nJetGood"              :(lambda event, sample: event.nJetGood),
     "mva_nJet"              :(lambda event, sample: event.nJet),

     "mva_nBTag"                 :(lambda event, sample: event.nBTag),
     "mva_nlep"                  :(lambda event, sample: event.nlep),
     "mva_nJet"                  :(lambda event, sample: event.nJet),

     "mva_mT_l1"                 :(lambda event, sample: sqrt(2*event.l1_pt*event.met_pt*(1-cos(event.l1_phi-event.met_phi)))),
     "mva_mT_l2"                 :(lambda event, sample: sqrt(2*event.l2_pt*event.met_pt*(1-cos(event.l2_phi-event.met_phi)))),
     "mva_ml_12"                 :(lambda event, sample: sqrt(2*event.l1_pt*event.l2_pt*(cosh(event.l1_eta-event.l2_eta)-cos(event.l1_phi-event.l2_phi)))),
     "mva_met_pt"                :(lambda event, sample: event.met_pt),
     "mva_l1_pt"                 :(lambda event, sample: event.l1_pt),
     "mva_l1_eta"                :(lambda event, sample: event.l1_eta),
     "mva_l2_pt"                 :(lambda event, sample: event.l2_pt),
     "mva_l2_eta"                :(lambda event, sample: event.l2_eta),

     "mva_mj_12"                 :(lambda event, sample: sqrt(event.jets[0]['pt']*event.jets[1]['pt']*cosh(event.jets[0]['eta']-event.jets[1]['eta'])-cos(event.jets[0]['phi']-event.jets[1]['phi']))  if event.nJetGood >=2 else 0),
     "mva_mlj_11"                :(lambda event, sample: sqrt(event.l1_pt*event.jets[0]['pt']*cosh(event.l1_eta-event.jets[0]['eta'])-cos(event.l1_phi-event.jets[0]['phi'])) if event.nJetGood >=1 else 0),
     "mva_mlj_12"                :(lambda event, sample: sqrt(event.l1_pt*event.jets[1]['pt']*cosh(event.l1_eta-event.jets[1]['eta'])-cos(event.l1_phi-event.jets[1]['phi'])) if event.nJetGood >=2 else 0),

     # Use these when retraining:
     #"mva_dPhil_12"              :(lambda event, sample: deltaPhi(event.l1_phi, event.l2_phi)),
     #"mva_dPhij_12"              :(lambda event, sample: deltaPhi(event.JetGood_phi[0], event.JetGood_phi[1]) if event.nJetGood >=2 else 0),
     # Keep old version vor consistently evaluating:
     "mva_dPhil_12"              :(lambda event, sample: acos(cos(event.l1_phi-event.l2_phi))),
     "mva_dPhij_12"              :(lambda event, sample: acos(cos(event.JetGood_phi[0]-event.JetGood_phi[1])) if event.nJetGood >=2 else 0),

     "mva_dEtal_12"              :(lambda event, sample: event.l1_eta-event.l2_eta),
     "mva_dEtaj_12"              :(lambda event, sample: event.JetGood_eta[0] - event.JetGood_eta[1] if event.nJetGood >=2 else -10),

     "mva_ht"                    :(lambda event, sample: sum( [j['pt'] for j in event.jets] ) ),
     "mva_htb"                   :(lambda event, sample: sum( [j['pt'] for j in event.bJets] ) ),
     "mva_ht_ratio"              :(lambda event, sample: sum( [j['pt'] for j in event.jets[:4]])/ sum( [j['pt'] for j in event.jets ]) if event.nJetGood>=4 else 1 ),

     "mva_jet0_pt"               :(lambda event, sample: event.JetGood_pt[0]          if event.nJetGood >=1 else 0),
     "mva_jet0_eta"              :(lambda event, sample: event.JetGood_eta[0]         if event.nJetGood >=1 else -10),
     "mva_jet0_btagDeepFlavB"        :(lambda event, sample: event.JetGood_btagDeepFlavB[0]   if (event.nJetGood >=1 and event.JetGood_btagDeepFlavB[0]>-10) else -10),
     "mva_jet1_pt"               :(lambda event, sample: event.JetGood_pt[1]          if event.nJetGood >=2 else 0),
     "mva_jet1_eta"              :(lambda event, sample: event.JetGood_eta[1]         if event.nJetGood >=2 else -10),
     "mva_jet1_btagDeepFlavB"        :(lambda event, sample: event.JetGood_btagDeepFlavB[1]   if (event.nJetGood >=2 and event.JetGood_btagDeepFlavB[1]>-10) else -10),
     "mva_jet2_pt"               :(lambda event, sample: event.JetGood_pt[2]          if event.nJetGood >=3 else 0),
     "mva_jet2_eta"              :(lambda event, sample: event.JetGood_eta[2]         if event.nJetGood >=3 else -10),
     "mva_jet2_btagDeepFlavB"        :(lambda event, sample: event.JetGood_btagDeepFlavB[2]   if (event.nJetGood >=3 and event.JetGood_btagDeepFlavB[2]>-10) else -10),

     "mva_jet3_pt"               :(lambda event, sample: event.JetGood_pt[3]          if event.nJetGood >=4 else 0),
     "mva_jet4_pt"               :(lambda event, sample: event.JetGood_pt[4]          if event.nJetGood >=5 else 0),
     "mva_jet5_pt"               :(lambda event, sample: event.JetGood_pt[5]          if event.nJetGood >=6 else 0),
     "mva_jet6_pt"               :(lambda event, sample: event.JetGood_pt[6]          if event.nJetGood >=7 else 0),
     "mva_jet7_pt"               :(lambda event, sample: event.JetGood_pt[7]          if event.nJetGood >=8 else 0),

     #New variables from the 3 lep file
     "mva_nBTagJetL"             :(lambda event, sample: event.nJetGood if (event.JetGood_btagDeepFlavB>=.0494) else -10),
     "mva_nBTagJetM"             :(lambda event, sample: event.nJetGood if (event.JetGood_btagDeepFlavB>=.2770) else -10),
     "mva_nBTagJetT"             :(lambda event, sample: event.nJetGood if (event.JetGood_btagDeepFlavB>=.7264) else -10),
     #Smallest dR between two b-tagged jets
     "mva_dR_bb"                 :(lambda event, sample: min([deltaR(event.bJets[i],event.bJets[j])if i!=j else 10000 for i in range(len(event.bJets)) for j in range(len(event.bJets))]) if len(event.bJets)>=2 else 10000),
     #dR between leading/subleading lepton
     "mva_dR_2l"                 :(lambda event, sample: sqrt(deltaPhi(event.l1_phi, event.l2_phi)**2 + (event.l1_eta - event.l2_eta)**2)),
     #Highest mass to pT ratio of any selected jet
     "mva_mpt_ratio"             :(lambda event, sample: max([(event.Jet_mass[event.JetGood_index[i]]/event.Jet_pt[event.JetGood_index[i]]) for i in range(event.nJetGood)]) if event.nJetGood>=1 else 0),
     #(Second) smallest dR between any lepton and medium b-tagged jet
     "mva_dR_min0"               :(lambda event, sample: sorted([deltaR(event.bJets[i], event.leptons[j]) for i in range(len(event.bJets)) for j in range(len(event.leptons))])[0] if len(event.bJets)>=1 else 10000),
     "mva_dR_min1"               :(lambda event, sample: sorted([deltaR(event.bJets[i], event.leptons[j]) for i in range(len(event.bJets)) for j in range(len(event.leptons))])[1] if len(event.bJets)>=1 else 10000),
     #Mt2 mass lepton + b-jet
     "mva_mt2_bb"                :(lambda event, sample: MT2(event.l1_pt, event.l1_eta, event.l1_phi, event.l2_pt, event.l2_eta, event.l2_phi, event.met_pt, event.met_phi, event.bJets, event.nonbJets, mt2Calculator)[0] if len(event.jets)>=2 else 0),
     "mva_mt2_blbl"              :(lambda event, sample : MT2(event.l1_pt, event.l1_eta, event.l1_phi, event.l2_pt, event.l2_eta, event.l2_phi, event.met_pt, event.met_phi, event.bJets, event.nonbJets, mt2Calculator)[1] if len(event.jets)>=2 else 0),
     "mva_mt2_blbl"              :(lambda event, sample : MT2(event.l1_pt, event.l1_eta, event.l1_phi, event.l2_pt, event.l2_eta, event.l2_phi, event.met_pt, event.met_phi, event.bJets, event.nonbJets, mt2Calculator)[2] if len(event.jets)>=2 else 0),
     "mva_bTagScore_max0"        :(lambda event, sample: sorted([event.JetGood_btagDeepFlavB[i] for i in range(int(event.nJet))], reverse=True)[0]),
     "mva_bTagScore_max1"        :(lambda event, sample: sorted([event.JetGood_btagDeepFlavB[i] for i in range(int(event.nJet))], reverse=True)[1]),
     "mva_bTagScore_max2"        :(lambda event, sample: sorted([event.JetGood_btagDeepFlavB[i] for i in range(int(event.nJet))], reverse=True)[2]),
     "mva_bTagScore_max3"        :(lambda event, sample: sorted([event.JetGood_btagDeepFlavB[i] for i in range(int(event.nJet))], reverse=True)[3]),


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
TTLep_bb    = copy.deepcopy( samples.TTLep )
TTLep_bb.name = "TTLep_bb"
TTLep_bb.texName = samples.TTLep.name+" (b#overline{b})"
TTLep_bb.setSelectionString( "genTtbarId%100>=50" )
TTLep_cc    = copy.deepcopy( samples.TTLep )
TTLep_cc.name = "TTLep_cc"
TTLep_cc.texName = samples.TTLep.name+" (c#overline{c})"
TTLep_cc.setSelectionString( "genTtbarId%100>=40&&genTtbarId%100<50" )
TTLep_other = copy.deepcopy( samples.TTLep )
TTLep_other.name = "TTLep_other"
TTLep_other.texName = samples.TTLep.name+" (other)"
TTLep_other.setSelectionString( "genTtbarId%100<40" )

training_samples = [ samples.TTTT, TTLep_bb, TTLep_cc, samples.TTLepbb, samples.TTbb ]


assert len(training_samples)==len(set([s.name for s in training_samples])), "training_samples names are not unique!"

# training selection

selection = 'trg-dilepVL-minDLmass20-offZ1-njet4p-btag2p'
from tttt.Tools.cutInterpreter import cutInterpreter
selectionString = cutInterpreter.cutString( selection )
