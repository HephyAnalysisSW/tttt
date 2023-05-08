import copy, os, sys
from RootTools.core.Sample import Sample
import ROOT

# Logging
import logging
logger = logging.getLogger(__name__)

from tttt.samples.color import color
#dir = "/scratch-cbe/users/robert.schoefbeck/tttt/nanoTuples/gen/v1/"
# dir = "/scratch-cbe/users/lena.wild/tttt/nanoTuples/gen/v1__small/"
dir = "/scratch-cbe/users/lena.wild/tttt/nanoTuples/gen/v6/"

TTTT_MS = Sample.fromDirectory("TTTT_MS", os.path.join( dir, "TTTT_MS" ))
TTTT_MS.reweight_pkl = "/eos/vbc/group/cms/robert.schoefbeck/gridpacks/4top/TTTT_MS_reweight_card.pkl" 
TTTT_MS.color = color.TTTT
TTTT_MS.objects = ['t']
TTTT_MS.xsec     = 11.9e-03
TTTT_MS.total_genWeight = 3.07644844055

TTbb_MS = Sample.fromDirectory("TTbb_MS", os.path.join( dir, "TTbb_MS" ))
TTbb_MS.reweight_pkl = "/eos/vbc/group/cms/robert.schoefbeck/gridpacks/4top/TTbb_MS_reweight_card.pkl" 
TTbb_MS.color = color.TTbb
TTbb_MS.objects = ['t']
TTbb_MS.xsec     = 5.253e-01
TTbb_MS.total_genWeight = 258.110778809

TT_2L = Sample.fromDirectory("TT_2L", os.path.join( dir, "TT_2L" ))
TT_2L.color = color.TT
TT_2L.objects = ['t']
TT_2L.xsec     = 831.762*((3*0.108)**2) # I need this in the plots, is it wrong if I add it here?
TT_2L.total_genWeight = 3465481472.0

TT_2L_full = Sample.fromDirectory("TT_2L_full", os.path.join( dir, "TT_2L_full" ))
TT_2L_full.color = color.TT
TT_2L_full.objects = ['t']
TT_2L_full.xsec     = 831.762*((3*0.108)**2) # I need this in the plots, is it wrong if I add it here?
TT_2L_full.total_genWeight = 10325881856.0


allSamples = [ TTTT_MS, TTbb_MS, TT_2L, TT_2L_full ]

for s in allSamples:
  s.isData  = False
