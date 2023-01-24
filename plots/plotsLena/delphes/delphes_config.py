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

# Training variables
read_variables = [\
    "nBTag/I", 
    "recoMet_pt/F", "recoMet_phi/F",
    "genMet_pt/F", "genMet_phi/F",
    "nrecoJet/I",
    "recoJet[%s]"%(",".join(jetVars)),
    "nrecoLep/I",
    "recoLep[%s]"%(",".join(lepVars)),
    "ngenLep/I", "genLep[pt/F,eta/F,phi/F,pdgId/I,mother_pdgId/I]", 
    "lumiweight1fb/F",
    "evt/l", "run/I", "lumi/I",
    "recoBj0_pt/F",
    "recoBj1_pt/F",
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
     "htb"                   :(lambda event, sample: sum( [j['pt'] for j in event.recoBJets] ) ),
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
     "bjet0_pt"              :(lambda event, sample: event.recoBj0_pt),
     "bjet1_pt"              :(lambda event, sample: event.recoBj1_pt),
    
     "dR_min0"               :(lambda event, sample: event.dR_min0),
     "dR_min1"               :(lambda event, sample: event.dR_min1),
     #Smallest dR between two b-tagged jets
     "min_dR_bb"             :(lambda event, sample: event.min_dR_bb),
     #dR between leading/subleading lepton
     "dR_2l"                 :(lambda event, sample: sqrt(deltaPhi(event.recoLep_phi[0], event.recoLep_phi[1])**2 + (event.recoLep_eta[0] - event.recoLep_eta[1])**2)),
     #Mt2 mass lepton + b-jet
     #"mt2ll"                 :(lambda event, sample : event.mt2ll),
     #"mt2bb"                 :(lambda event, sample : event.mt2bb),
     #"mt2blbl"               :(lambda event, sample : event.mt2blbl),
     }


## Using all variables
mva_variables_ = all_mva_variables.keys()
mva_variables_.sort()
mva_variables  = [ (key, value) for key, value in all_mva_variables.iteritems() if key in mva_variables_ ]

sequence = []

def make_bjets ( event, sample ):

    event.recoJets = getCollection( event, 'recoJet', ['pt', 'eta', 'phi', 'bTag_loose'], 'nrecoJet' )
    event.recoBJets    = filter( lambda j:     j['bTag_loose'] and abs(j['eta'])<2.4 , event.recoJets )
    event.recoNonBJets = []
    for b in event.recoJets:
        if b not in event.recoBJets:
            event.recoNonBJets.append(b)
    
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

    # we must always have two leptons and two jets, hence no default needed.
    mt2Calculator.reset()    
    mt2Calculator.setLeptons(event.recoLep_pt[0], event.recoLep_eta[0], event.recoLep_phi[0],event.recoLep_pt[1], event.recoLep_eta[1], event.recoLep_phi[1])
    mt2Calculator.setMet(event.recoMet_pt, event.recoMet_phi)
    #event.mt2ll = mt2Calculator.mt2ll()
    
    
    b = (event.recoBJets + event.recoNonBJets )[:2]
    b1, b2 = b[0], b[1]
    mt2Calculator.setBJets(b1['pt'], b1['eta'], b1['phi'], b2['pt'], b2['eta'], b2['phi'])
    #event.mt2bb = mt2Calculator.mt2bb()
    #event.mt2blbl = mt2Calculator.mt2blbl()

#sequence.append( MT2 )