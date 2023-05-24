import os, sys
from RootTools.core.Sample import Sample
import ROOT

# Logging
import logging
logger = logging.getLogger(__name__)

from tttt.samples.color import color

import tttt.samples.config as config
directory_ = config.location_mc_UL2018_trilep

# TTHnobb  TTHTobb  TTLep_pow_CP5  TTTT  TTWToLNu  TTWToQQ  TTZToLLNuNu  TTZToLLNuNu_m1to10  TTZToQQ

def make_dirs( dirs ):
    return [ os.path.join( directory_, dir_ ) for dir_ in dirs ]

TTLep = Sample.fromDirectory(name="TTLep", treeName="Events", isData=False, color=color.TT, texName="t#bar{t}", directory=make_dirs( ['TTLep_pow_CP5'] ))
TTLepbb = Sample.fromDirectory(name="TTLepbb", treeName="Events", isData=False, color=color.TT, texName="t#bar{t}", directory=make_dirs( ['TTLep_pow_CP5', 'TTbb'] ))
TTbb  = Sample.fromDirectory(name="TTbb",  treeName="Events", isData=False, color=color.TTbb, texName="t#bar{t}b#bar{b}", directory=make_dirs( ['TTbb'] ))
ST    = Sample.fromDirectory(name="ST",    treeName="Events", isData=False, color=color.T,  texName="t/tW", directory=make_dirs( ['T_tWch', 'T_tch_pow', 'Tbar_tch_pow', 'TBar_tWch'] ))
TTTT  = Sample.fromDirectory(name="TTTT",  treeName="Events", isData=False, color=color.TTTT, texName="t#bar{t}t#bar{t}", directory=make_dirs( ['TTTT'] ))
TTW   = Sample.fromDirectory(name="TTW",   treeName="Events", isData=False, color=color.TTW, texName="t#bar{t}W", directory=make_dirs( ['TTWToLNu', 'TTWToQQ'] ))
TTZ   = Sample.fromDirectory(name="TTZ",   treeName="Events", isData=False, color=color.TTZ, texName="t#bar{t}Z", directory=make_dirs( ['TTZToLLNuNu', 'TTZToLLNuNu_m1to10', 'TTZToQQ'] ))
TTH   = Sample.fromDirectory(name="TTH",   treeName="Events", isData=False, color=color.TTH, texName="t#bar{t}H", directory=make_dirs( ['TTHTobb', 'TTHnobb'] ))

#TTTT_sync = Sample.fromDirectory(name="TTTT_sync",  treeName="Events", isData=False, color=color.TTTT, texName="t#bar{t}t#bar{t}_sync", directory=["/scratch-cbe/users/maryam.shooshtari/tttt/nanoTuples/tttt_v5/UL2018/dilep/TTTT_sync"] )
