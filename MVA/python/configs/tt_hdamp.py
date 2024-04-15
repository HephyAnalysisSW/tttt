#!/usr/bin/env python

#Standard imports
from operator                   import attrgetter
from math                       import pi, sqrt, cosh, cos, acos, sin
import ROOT, os
import copy
import itertools
import numpy as np

#From RootTools
from RootTools.core.standard     import *

#From Tools
from tttt.Tools.helpers          import deltaPhi, deltaR2, deltaR, getCollection, getObjDict
from tttt.Tools.objectSelection import isBJet, isAnalysisJet

from Analysis.Tools.WeightInfo       import WeightInfo

import logging
logger = logging.getLogger(__name__)

from tttt.Tools.cutInterpreter import cutInterpreter
selection = 'trg-dilepVL-minDLmass20-offZ1'
selectionString = cutInterpreter.cutString( selection )

TTLep_hUp = Sample.fromDirectory( "TTLep_hUp", directory = [
        "/scratch-cbe/users/maryam.shooshtari/tttt/nanoTuples/tttt_v8/UL2016/dilep-dilep-nlepFO2p-ht500/TTLep_pow_CP5_hUp/",
        "/scratch-cbe/users/maryam.shooshtari/tttt/nanoTuples/tttt_v8/UL2016_preVFP/dilep-dilep-nlepFO2p-ht500/TTLep_pow_CP5_hUp/",
        "/scratch-cbe/users/maryam.shooshtari/tttt/nanoTuples/tttt_v8/UL2017/dilep-dilep-nlepFO2p-ht500/TTLep_pow_CP5_hUp/",
        "/scratch-cbe/users/maryam.shooshtari/tttt/nanoTuples/tttt_v8/UL2018/dilep-dilep-nlepFO2p-ht500/TTLep_pow_CP5_hUp/",
        ])
TTLep_hUp.texName = "t#bar{t} hdamp Up"
TTLep_hUp.color   = ROOT.kBlue + 1

TTLep_hDown = Sample.fromDirectory( "TTLep_hDown", directory = [
        "/scratch-cbe/users/maryam.shooshtari/tttt/nanoTuples/tttt_v8/UL2016/dilep-dilep-nlepFO2p-ht500/TTLep_pow_CP5_hDown/",
        "/scratch-cbe/users/maryam.shooshtari/tttt/nanoTuples/tttt_v8/UL2016_preVFP/dilep-dilep-nlepFO2p-ht500/TTLep_pow_CP5_hDown/",
        "/scratch-cbe/users/maryam.shooshtari/tttt/nanoTuples/tttt_v8/UL2017/dilep-dilep-nlepFO2p-ht500/TTLep_pow_CP5_hDown/",
        "/scratch-cbe/users/maryam.shooshtari/tttt/nanoTuples/tttt_v8/UL2018/dilep-dilep-nlepFO2p-ht500/TTLep_pow_CP5_hDown/",
        ])
TTLep_hDown.texName = "t#bar{t} hDamp down"
TTLep_hDown.color   = ROOT.kBlue + 3 

TTLep = Sample.fromDirectory( "TTLep", directory = [
        "/scratch-cbe/users/maryam.shooshtari/tttt/nanoTuples/tttt_v8/UL2016/dilep-dilep-nlepFO2p-ht500/TTLep_pow_CP5/",
        "/scratch-cbe/users/maryam.shooshtari/tttt/nanoTuples/tttt_v8/UL2016_preVFP/dilep-dilep-nlepFO2p-ht500/TTLep_pow_CP5/",
        "/scratch-cbe/users/maryam.shooshtari/tttt/nanoTuples/tttt_v8/UL2017/dilep-dilep-nlepFO2p-ht500/TTLep_pow_CP5/",
        "/scratch-cbe/users/maryam.shooshtari/tttt/nanoTuples/tttt_v8/UL2018/dilep-dilep-nlepFO2p-ht500/TTLep_pow_CP5/",
        ])
TTLep.texName = "t#bar{t}"
TTLep.color   = ROOT.kBlue 

# Training variables
jetVars          = ['pt/F', 'eta/F', 'phi/F', 'btagDeepFlavB/F', 'btagDeepFlavCvB/F', 'btagDeepFlavQG/F','index/I']
read_variables = [\
                    "nJet/I",
                    "nBTag/I",
                    "nlep/I",
                    "JetGood[%s]"%(",".join(jetVars)),
                    "met_pt/F", "met_phi/F",
                    "year/I",
                    "MET_T1_pt/F", "ht/F", "nJetGood/I", "weight/F",
                    ]

sequence = []

all_mva_variables = {
     "weight"                :(lambda event, sample: event.weight),

     "nJetGood"              :(lambda event, sample: event.nJetGood),
     "nBTag"                 :(lambda event, sample: event.nBTag),
     "met"                   :(lambda event, sample: event.MET_T1_pt),
     "ht"                    :(lambda event, sample: event.ht),

     "jet0_pt"               :(lambda event, sample: event.JetGood_pt[0]          if event.nJetGood >=1 else 0),
     "jet0_eta"              :(lambda event, sample: event.JetGood_eta[0]         if event.nJetGood >=1 else -10),
     "jet1_pt"               :(lambda event, sample: event.JetGood_pt[1]          if event.nJetGood >=2 else 0),
     "jet1_eta"              :(lambda event, sample: event.JetGood_eta[1]         if event.nJetGood >=2 else -10),
     "jet2_pt"               :(lambda event, sample: event.JetGood_pt[2]          if event.nJetGood >=3 else 0),
     "jet2_eta"              :(lambda event, sample: event.JetGood_eta[2]         if event.nJetGood >=3 else -10),
     "jet3_pt"               :(lambda event, sample: event.JetGood_pt[2]          if event.nJetGood >=4 else 0),
     "jet3_eta"              :(lambda event, sample: event.JetGood_eta[2]         if event.nJetGood >=4 else -10),
     "jet4_pt"               :(lambda event, sample: event.JetGood_pt[2]          if event.nJetGood >=5 else 0),
     "jet4_eta"              :(lambda event, sample: event.JetGood_eta[2]         if event.nJetGood >=5 else -10),

}

# for the filler
mva_vector_variables    =   {
    #"Jet":  {"name":"Jet", "vars":['pt'], "varnames":['pt'], "selector": (lambda jet: True), 'maxN':10}
}

## Using all variables
mva_variables_ = all_mva_variables.keys()
mva_variables_.sort()
mva_variables  = [ (key, value) for key, value in all_mva_variables.iteritems() if key in mva_variables_ and not "reweightBTagSF" in key ]

import numpy as np
import operator

training_samples = [ TTLep_hUp, TTLep_hDown, TTLep ]

assert len(training_samples)==len(set([s.name for s in training_samples])), "training_samples names are not unique!"

# training selection

selectionString = cutInterpreter.cutString( selection )
