import os
from RootTools.core.Sample import Sample
import ROOT

# Logging
import logging
logger = logging.getLogger(__name__)

from tttt.samples.color import color

directory_ = "/scratch-cbe/users/robert.schoefbeck/tttt/nanoTuples/tttt_v1/UL2018/dilep/"

def make_dirs( dirs ):
    return [ os.path.join( directory_, dir_ ) for dir_ in dirs ]

dirs = {}

dirs['TTLep']  = ["TTLep_pow_CP5"]
TTLep = Sample.fromDirectory(name="TTLep", treeName="Events", isData=False, color=color.TT, texName="t#bar{t}", directory=make_dirs( dirs['TTLep'] ))
TTTT  = Sample.fromDirectory(name="TTTT",  treeName="Events", isData=False, color=color.TTTT, texName="t#bar{t}t#bar{t}", directory=make_dirs( ['TTTT'] ))
