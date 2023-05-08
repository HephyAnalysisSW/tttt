import copy, os, sys
from RootTools.core.Sample import Sample
import ROOT

# Logging
import logging
logger = logging.getLogger(__name__)

from tttt.samples.color import color
#dir = "/scratch-cbe/users/robert.schoefbeck/tttt/nanoTuples/gen/v1/"
# dir = "/scratch-cbe/users/lena.wild/tttt/nanoTuples/gen/v1__small/"
dir = "/scratch-cbe/users/lena.wild/tttt/nanoTuples/gen/v7w_weightsum/"

TTTT_MS = Sample.fromDirectory("TTTT_MS", os.path.join( dir, "TTTT_MS" ))


TTbb_MS = Sample.fromDirectory("TTbb_MS", os.path.join( dir, "TTbb_MS" ))


TT_2L   = Sample.fromDirectory("TT_2L", os.path.join( dir, "TT_2L" ))


TT_2L_full = Sample.fromDirectory("TT_2L_full", os.path.join( dir, "TT_2L_full" ))


allSamples = [ TTTT_MS, TTbb_MS, TT_2L, TT_2L_full ]

for s in allSamples:
  s.isData  = False
