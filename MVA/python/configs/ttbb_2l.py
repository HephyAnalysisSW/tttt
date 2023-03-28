#!/usr/bin/env python

#Standard imports
from operator                   import attrgetter
from math                       import pi, sqrt, cosh, cos, acos, sin, sinh
import ROOT, os
import copy
import itertools

#From RootTools
from RootTools.core.standard     import *

#From Tools
from tttt.Tools.helpers          import deltaPhi, deltaR2, deltaR, getCollection, getObjDict
from Analysis.Tools.WeightInfo       import WeightInfo

import logging
logger = logging.getLogger(__name__)


from Analysis.Tools.mt2Calculator import mt2Calculator
mt2Calculator = mt2Calculator()

# Read variables and sequences
jetVars          = ['pt/F', 'eta/F', 'phi/F', 'bTag/F', 'bTagPhys/I']
jetVarNames      = [x.split('/')[0] for x in jetVars]

lepVars          = ['pt/F','eta/F','phi/F','pdgId/I','isolationVar/F', 'isolationVarRhoCorr/F']
lepVarNames      = [x.split('/')[0] for x in lepVars]

lstm_jets_maxN   = 10
lstm_jetVars     = ['pt/F', 'eta/F', 'phi/F', 'bTag/F']
lstm_jetVarNames = [x.split('/')[0] for x in lstm_jetVars]

eft_coeff        = ['coeff/F']
eft_VarNames     = [x.split('/')[0] for x in eft_coeff]

WC = {}
WC['TTTT_MS']    = ['ctt', 'cQQ1', 'cQQ8', 'cQt1', 'cQt8', 'ctHRe', 'ctHIm']
WC['TTbb_MS']    = ['ctt', 'cQQ1', 'cQQ8', 'cQt1', 'cQt8', 'ctHRe', 'ctHIm','ctb1', 'ctb8', 'cQb1', 'cQb8', 'cQtQb1Re', 'cQtQb8Re', 'cQtQb1Im', 'cQtQb8Im']

# Training variables
read_variables = [\
    "nBTag/I", 
    "recoMet_pt/F", "recoMet_phi/F",
    "genMet_pt/F", "genMet_phi/F",
    "nrecoJet/I",
    "nrecoBJet/I",
    "recoJet[%s]"%(",".join(jetVars)),
    "recoBJet[%s]"%(",".join(jetVars)),
    "nrecoLep/I",
    "recoLep[%s]"%(",".join(lepVars)),
    "ngenLep/I", "genLep[pt/F,eta/F,phi/F,pdgId/I,mother_pdgId/I]", 
    "lumiweight1fb/F",
    "evt/l", "run/I", "lumi/I",
    "recoBj0_pt/F",
    "recoBj1_pt/F",
    "np/I", VectorTreeVariable.fromString("p[C/F]", nMax=200),
    
]

all_mva_variables = {

     #Global Event Properties
     "nrecoJet"              :(lambda event, sample: event.nrecoJet),

     #Lep Vars
     "mT_l1"                 :(lambda event, sample: sqrt(2*event.recoLep_pt[0]*event.recoMet_pt*(1-cos(event.recoLep_phi[0]-event.recoMet_phi)))),
     "mT_l2"                 :(lambda event, sample: sqrt(2*event.recoLep_pt[1]*event.recoMet_pt*(1-cos(event.recoLep_phi[1]-event.recoMet_phi)))),
     "ml_12"                 :(lambda event, sample: sqrt(2*event.recoLep_pt[0]*event.recoLep_pt[1]*(cosh(event.recoLep_eta[0]-event.recoLep_eta[1])-cos(event.recoLep_phi[0]-event.recoLep_phi[1])))),
     "l1_pt"                 :(lambda event, sample: event.recoLep_pt[0]),
     "l1_eta"                :(lambda event, sample: event.recoLep_eta[0]),
     "l2_pt"                 :(lambda event, sample: event.recoLep_pt[1]),
     "l2_eta"                :(lambda event, sample: event.recoLep_eta[1]),

     #MET
     "met_pt"                :(lambda event, sample: event.recoMet_pt),
     
     #leptons/jets
     "mj_12"                 :(lambda event, sample: sqrt(2*event.recoJet_pt[0]*event.recoJet_pt[1]*(cosh(event.recoJet_eta[0]-event.recoJet_eta[1])-cos(event.recoJet_phi[0]-event.recoJet_phi[1]))) if event.nrecoJet >=2 else 0),
     "mlj_11"                :(lambda event, sample: sqrt(2*event.recoLep_pt[0]*event.recoJet_pt[0]*(cosh(event.recoLep_eta[0]-event.recoJet_eta[0])-cos(event.recoLep_phi[0]-event.recoJet_phi[0]))) if event.nrecoJet >=1 else 0),
     "mlj_12"                :(lambda event, sample: sqrt(2*event.recoLep_pt[0]*event.recoJet_pt[1]*(cosh(event.recoLep_eta[0]-event.recoJet_eta[1])-cos(event.recoLep_phi[0]-event.recoJet_phi[1]))) if event.nrecoJet >=2 else 0),
     
     "dPhil_12"              :(lambda event, sample: deltaPhi(event.recoLep_phi[0], event.recoLep_phi[1])),
     "dPhij_12"              :(lambda event, sample: deltaPhi(event.recoJet_phi[0], event.recoJet_phi[1]) if event.nrecoJet >=2 else 0),
     
     "dEtal_12"              :(lambda event, sample: abs(event.recoLep_eta[0]-event.recoLep_eta[1])),
     "dEtaj_12"              :(lambda event, sample: abs(event.recoJet_eta[0]-event.recoJet_eta[1]) if event.nrecoJet >=2 else -10),

     "ht"                    :(lambda event, sample: sum( [event.recoJet_pt[i] for i in range (event.nrecoJet)] ) ),
     "htb"                   :(lambda event, sample: sum( [event.recoBJet_pt[i] for i in range (event.nrecoBJet)] ) ),
     "ht_ratio"              :(lambda event, sample: sum( [event.recoJet_pt[i] for i in range (4)])/ sum( [event.recoJet_pt[i] for i in range (event.nrecoJet) ]) if event.nrecoJet>=4 else 1 ),

     "jet0_pt"               :(lambda event, sample: event.recoJet_pt[0]          if event.nrecoJet >=1 else 0),
     "jet0_eta"              :(lambda event, sample: event.recoJet_eta[0]         if event.nrecoJet >=1 else -10),
     "jet1_pt"               :(lambda event, sample: event.recoJet_pt[1]          if event.nrecoJet >=2 else 0),
     "jet1_eta"              :(lambda event, sample: event.recoJet_eta[1]         if event.nrecoJet >=2 else -10),
     "jet2_pt"               :(lambda event, sample: event.recoJet_pt[2]          if event.nrecoJet >=3 else 0),
     "jet2_eta"              :(lambda event, sample: event.recoJet_eta[2]         if event.nrecoJet >=3 else -10),
     "jet3_pt"               :(lambda event, sample: event.recoJet_pt[3]          if event.nrecoJet >=4 else 0),
     "jet4_pt"               :(lambda event, sample: event.recoJet_pt[4]          if event.nrecoJet >=5 else 0),
     "jet5_pt"               :(lambda event, sample: event.recoJet_pt[5]          if event.nrecoJet >=6 else 0),
     "jet6_pt"               :(lambda event, sample: event.recoJet_pt[6]          if event.nrecoJet >=7 else 0),
     "jet7_pt"               :(lambda event, sample: event.recoJet_pt[7]          if event.nrecoJet >=8 else 0),
     "bjet0_pt"              :(lambda event, sample: event.recoBJet_pt[0]),
     "bjet1_pt"              :(lambda event, sample: event.recoBJet_pt[1]),
     "m_4b"                  :(lambda event, sample: event.m_4b),
     "dR_min0"               :(lambda event, sample: event.dR_min0),
     "dR_min1"               :(lambda event, sample: event.dR_min1),
     #Smallest dR between two b-tagged jets
     "min_dR_bb"             :(lambda event, sample: event.min_dR_bb),
     #dR between leading/subleading lepton
     "dR_2l"                 :(lambda event, sample: sqrt(deltaPhi(event.recoLep_phi[0], event.recoLep_phi[1])**2 + (event.recoLep_eta[0] - event.recoLep_eta[1])**2)),
     #Mt2 mass lepton + b-jet
     "mt2ll"                 :(lambda event, sample : event.mt2ll),
     "mt2bb"                 :(lambda event, sample : event.mt2bb),
     "mt2blbl"               :(lambda event, sample : event.mt2blbl),
     }

## Using all variables
mva_variables_ = all_mva_variables.keys()
mva_variables_.sort()
mva_variables  = [ (key, value) for key, value in all_mva_variables.iteritems() if key in mva_variables_ ]

def lstm_jets(event, sample):
    #print event.recoJet_bTagPhys[0]
    jets = [ getObjDict( event, 'recoJet_', lstm_jetVarNames, i) for i in range(int(event.nrecoJet)) ]
    #jets = filter( jet_vector_var['selector'], jets )
    return jets

def copy_p(event, sample):
    p_C = [ getObjDict( event, 'p_', "C", i) for i in range(int(event.np)) ]
    return p_C
    
# for the filler 
mva_vector_variables    =   {
    "mva_Jet":  {"func":lstm_jets,  "name":"Jet", "vars":lstm_jetVars, "varnames":lstm_jetVarNames},
    #"p":        {"func":copy_p,     "name":"p", "vars":["C/F"], "varnames":"C", "nMax":200},
    #"ctt":      {"func":copy_coeff, "name":"ctt", "vars":eft_coeff, "varnames":eft_VarNames, "nMax":3}
}

# separate p_C from mva_vector_variables because not every sample has EFT weight vector
mva_target_variables = {
    "p":        {"func":copy_p,     "name":"p", "vars":["C/F"], "varnames":"C", "nMax":200}
}    

sequence = []

def addTLorentzVector( p_dict , name ):
    ''' add a TLorentz 4D Vector for further calculations
    '''
    #v = ROOT.TLorentzVector(0,0,0,0)
    p_dict[name] = ROOT.TLorentzVector( p_dict['pt']*cos(p_dict['phi']), p_dict['pt']*sin(p_dict['phi']),  p_dict['pt']*sinh(p_dict['eta']), p_dict['pt']*cosh(p_dict['eta']) )


def make_bjets ( event, sample ):
    event.recoJets = getCollection( event, 'recoJet', jetVarNames, 'nrecoJet' )
    event.recoBJets = getCollection( event, 'recoBJet', jetVarNames, 'nrecoBJet' )
    event.recoNonBJets = []
    for b in event.recoJets:
        addTLorentzVector( b, 'vec4D' ) 
        # if b not in event.recoBJets:
            # event.recoNonBJets.append(b)
    for b in event.recoBJets:
        addTLorentzVector( b, 'vec4D' )      
        
    if (event.nrecoBJet >= 4):        
        event.m_4b  = abs((event.recoBJets[0]['vec4D']+event.recoBJets[1]['vec4D']+event.recoBJets[2]['vec4D']+event.recoBJets[3]['vec4D']).M())  
    else:
        event.m_4b  = 0
        
    # minDR of all btag combinations
    if len(event.recoBJets)>=2:
        event.min_dR_bb = min( [deltaR( comb[0], comb[1] ) for comb in itertools.combinations( event.recoBJets, 2)] )
    else:
        event.min_dR_bb = -1
        
sequence.append ( make_bjets )


def make_leptons(event, sample):
    event.leptons   = getCollection(event, 'recoLep', lepVarNames, 'nrecoLep') 
    
     #(Second) smallest dR between any lepton and medium b-tagged jet
    dR_vals = sorted([deltaR(event.recoBJets[i], event.leptons[j]) for i in range(len(event.recoBJets)) for j in range(len(event.leptons))])
    if len(dR_vals)>=2:
        event.dR_min0 = dR_vals[0]
        event.dR_min1 = dR_vals[1]
    else:
        event.dR_min0 = -1
        event.dR_min1 = -1

sequence.append(make_leptons)




def MT2(event, sample):

    # we must always have two leptons and two jets, hence no default needed?
    mt2Calculator.reset()    
    
    mt2Calculator.setMet(event.recoMet_pt, event.recoMet_phi)
    if (len(event.leptons)>=2):
        mt2Calculator.setLeptons(event.recoLep_pt[0], event.recoLep_eta[0], event.recoLep_phi[0],event.recoLep_pt[1], event.recoLep_eta[1], event.recoLep_phi[1])
        event.mt2ll = mt2Calculator.mt2ll()
    else: 
        event.mt2ll = float('nan')
        
    b = event.recoBJets
    if (len(b)>=2) and (len(event.leptons)>=2):   
        b1, b2 = b[0], b[1]
        mt2Calculator.setBJets(b1['pt'], b1['eta'], b1['phi'], b2['pt'], b2['eta'], b2['phi'])
        event.mt2bb = mt2Calculator.mt2bb()  
        event.mt2blbl = mt2Calculator.mt2blbl()
    else: 
        event.mt2blbl = float('nan')  
        event.mt2bb   = float('nan')
        
sequence.append( MT2 )


import tttt.samples.GEN_EFT_postProcessed as samples
training_samples = [samples.TTTT_MS, samples.TTbb_MS, samples.TT_2L]

import tttt.samples.GEN_EFT_postProcessed_weights as samples_weights
weightsum_samples = [samples_weights.TTTT_MS, samples_weights.TTbb_MS, samples_weights.TT_2L]

