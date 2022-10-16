
#/scratch-cbe/users/robert.schoefbeck/tWZ/nanoTuples/tWZ_nAODv6_private_v3/2016/dilep:
#DYJetsToLL_M10to50             DYJetsToLL_M50_HT100to200_ext   DYJetsToLL_M50_HT400to600_comb  DYJetsToLL_M50_LO_ext1_comb          DYJetsToLL_M5to50_HT400to600_comb  TTTT
#DYJetsToLL_M10to50_LO          DYJetsToLL_M50_HT1200to2500     DYJetsToLL_M50_HT600to800       DYJetsToLL_M50_LO_ext1_comb_lheHT70  DYJetsToLL_M5to50_HT600toInf       TTWW
#DYJetsToLL_M10to50_LO_lheHT70  DYJetsToLL_M50_HT200to400_comb  DYJetsToLL_M50_HT70to100        DYJetsToLL_M5to50_HT100to200_comb    DYJetsToLL_M5to50_HT70to100        TTWZ
#DYJetsToLL_M50_ext2            DYJetsToLL_M50_HT2500toInf      DYJetsToLL_M50_HT800to1200      DYJetsToLL_M5to50_HT200to400_comb    TTLep_pow                          TTZZ
#
#/scratch-cbe/users/robert.schoefbeck/tWZ/nanoTuples/tWZ_nAODv6_private_v3/2017/dilep:
#DYJetsToLL_M10to50_LO           DYJetsToLL_M4to50_HT200to400_comb  DYJetsToLL_M50_HT100to200       DYJetsToLL_M50_HT2500toInf  DYJetsToLL_M50_HT70to100    DYJetsToLL_M50_LO_comb_lheHT70  TTWW
#DYJetsToLL_M10to50_LO_lheHT100  DYJetsToLL_M4to50_HT400to600_comb  DYJetsToLL_M50_HT1200to2500     DYJetsToLL_M50_HT400to600   DYJetsToLL_M50_HT800to1200  TTLep_pow                       TTWZ
#DYJetsToLL_M4to50_HT100to200    DYJetsToLL_M4to50_HT600toInf_comb  DYJetsToLL_M50_HT200to400_comb  DYJetsToLL_M50_HT600to800   DYJetsToLL_M50_LO_comb      TTTT                            TTZZ



#DYJetsToLL_M10to50_LO
#DYJetsToLL_M50_HT1200to2500
#DYJetsToLL_M50_HT2500toInf
#DYJetsToLL_M50_HT600to800
#DYJetsToLL_M50_HT800to1200
#DYJetsToLL_M50_HT100to200
#DYJetsToLL_M50_HT200to400
#DYJetsToLL_M50_HT400to600
#DYJetsToLL_M50_HT70to100
#DYJetsToLL_M50_LO_lheHT70

import os
from RootTools.core.Sample import Sample
import ROOT

# Logging
import logging
logger = logging.getLogger(__name__)

from tttt.samples.color import color

directory_ = "/scratch-cbe/users/robert.schoefbeck/tttt/nanoTuples/tttt_v1/UL2016_preVFP/dilep/"

def make_dirs( dirs ):
    return [ os.path.join( directory_, dir_ ) for dir_ in dirs ]

dirs = {}

dirs['TTLep']  = ["TTLep_pow_CP5"]
TTLep = Sample.fromDirectory(name="TTLep", treeName="Events", isData=False, color=color.TT, texName="t#bar{t}", directory=make_dirs( dirs['TTLep'] ))
