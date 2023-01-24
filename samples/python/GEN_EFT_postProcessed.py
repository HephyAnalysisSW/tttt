import copy, os, sys
from RootTools.core.Sample import Sample
import ROOT

# Logging
import logging
logger = logging.getLogger(__name__)

from tttt.samples.color import color
#dir = "/scratch-cbe/users/robert.schoefbeck/tttt/nanoTuples/gen/v1/"
dir = "/scratch-cbe/users/lena.wild/tttt/nanoTuples/gen/v2/"

TTTT_MS = Sample.fromDirectory("TTTT_MS", os.path.join( dir, "TTTT_MS" ))
TTTT_MS.reweight_pkl = "/eos/vbc/group/cms/robert.schoefbeck/gridpacks/4top/TTTT_MS_reweight_card.pkl" 
TTTT_MS.color = color.TTTT
TTTT_MS.objects = ['t']

TTbb_MS = Sample.fromDirectory("TTbb_MS", os.path.join( dir, "TTbb_MS" ))
TTbb_MS.reweight_pkl = "/eos/vbc/group/cms/robert.schoefbeck/gridpacks/4top/TTbb_MS_reweight_card.pkl" 
TTbb_MS.color = color.TTbb
TTbb_MS.objects = ['t']

allSamples = [ TTTT_MS, TTbb_MS ]

for s in allSamples:
  s.isData  = False
