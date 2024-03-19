import os, sys
from RootTools.core.Sample import Sample
import ROOT

# Logging
import logging
logger = logging.getLogger(__name__)

from tttt.samples.color import color

import tttt.samples.config as config
directory_ = config.location_mc_UL2018

# TTHnobb  TTHTobb  TTLep_pow_CP5  TTTT  TTWToLNu  TTWToQQ  TTZToLLNuNu  TTZToLLNuNu_m1to10  TTZToQQ

def make_dirs( dirs ):
    return [ os.path.join( directory_, dir_ ) for dir_ in dirs ]

TTLep = Sample.fromDirectory(name="TTLep", treeName="Events", isData=False, color=color.TT, texName="t#bar{t}", directory=make_dirs( ['TTLep_pow_CP5'] ))
TTLepbb = Sample.fromDirectory(name="TTLepbb", treeName="Events", isData=False, color=color.TT, texName="t#bar{t}", directory=make_dirs( ['TTLep_pow_CP5', 'TTbb'] ))
TTbb  = Sample.fromDirectory(name="TTbb",  treeName="Events", isData=False, color=color.TTbb, texName="t#bar{t}b#bar{b}", directory=make_dirs( ['TTbb'] ))
ST    = Sample.fromDirectory(name="ST",    treeName="Events", isData=False, color=color.T,  texName="t/tW", directory=make_dirs( ['T_tWch', 'T_tch_pow', 'Tbar_tch_pow', 'TBar_tWch'] ))
ST_tch     = Sample.fromDirectory(name="ST_tch",     treeName="Events", isData=False, color=color.T,   texName="t" , directory=make_dirs( ['T_tch_pow', 'Tbar_tch_pow'] ))
ST_twch    = Sample.fromDirectory(name="ST_twch",    treeName="Events", isData=False, color=color.tW,  texName="tW", directory=make_dirs( ['T_tWch', 'TBar_tWch'] ))
TTTT  = Sample.fromDirectory(name="TTTT",  treeName="Events", isData=False, color=color.TTTT, texName="t#bar{t}t#bar{t}", directory=make_dirs( ['TTTT'] ))
TTW   = Sample.fromDirectory(name="TTW",   treeName="Events", isData=False, color=color.TTW, texName="t#bar{t}W", directory=make_dirs( ['TTWToLNu', 'TTWToQQ'] ))
TTZ   = Sample.fromDirectory(name="TTZ",   treeName="Events", isData=False, color=color.TTZ, texName="t#bar{t}Z", directory=make_dirs( ['TTZToLLNuNu', 'TTZToLLNuNu_m1to10', 'TTZToQQ'] ))
TTH   = Sample.fromDirectory(name="TTH",   treeName="Events", isData=False, color=color.TTH, texName="t#bar{t}H", directory=make_dirs( ['TTHTobb', 'TTHnobb'] ))
DY    = Sample.fromDirectory(name="DY",    treeName="Events", isData=False, color=color.DY, texName="DY", directory=make_dirs( ['DYJetsToLL_M50_HT100to200', 'DYJetsToLL_M50_HT200to400','DYJetsToLL_M50_HT400to600','DYJetsToLL_M50_HT600to800','DYJetsToLL_M50_HT800to1200','DYJetsToLL_M50_HT1200to2500','DYJetsToLL_M50_HT2500toInf','DYJetsToLL_M4to50_HT100to200', 'DYJetsToLL_M-4to50_HT200to400','DYJetsToLL_M-4to50_HT400to600','DYJetsToLL_M4to50_HT600toInf'] ))
DY_inclusive = Sample.fromDirectory(name="DY_inclusive",    treeName="Events", isData=False, color=color.DY, texName="DY", directory=make_dirs(['DYJetsToLL_M10to50_LO','DYJetsToLL_M50']))
DiBoson = Sample.fromDirectory(name="DiBoson",    treeName="Events", isData=False, color=color.W, texName="DiBoson", directory=make_dirs( ['WZTo3LNu','WZTo1L3Nu','WZTo2L2Q','WWTo2L2Nu','WWDoubleTo2L','WWTo1L1Nu2Q','WWTo4Q','ZZTo2L2Nu','ZZTo2L2Q','ZZTo2Q2Nu','ZZTo4L']))
TTbbHUp		= Sample.fromDirectory(name="TTbbHUp",  treeName="Events", isData=False, color=color.TTbb, texName="t#bar{t}b#bar{b}", directory=make_dirs( ['TTbb_pow_CP5_hUp'] ))
TTbbHDown	= Sample.fromDirectory(name="TTbbHDown",  treeName="Events", isData=False, color=color.TTbb, texName="t#bar{t}b#bar{b}", directory=make_dirs( ['TTbb_pow_CP5_hDown'] ))
TTLepHUp	= Sample.fromDirectory(name="TTLepHUp", treeName="Events", isData=False, color=color.TT, texName="t#bar{t}", directory=make_dirs( ['TTLep_pow_CP5_hUp'] ))
TTLepHDown      = Sample.fromDirectory(name="TTLepHDown", treeName="Events", isData=False, color=color.TT, texName="t#bar{t}", directory=make_dirs( ['TTLep_pow_CP5_hDown'] ))

TTbb_EFT	= Sample.fromDirectory(name="TTbb_EFT", treeName="Events", isData=False, color=color.TTbb, texName="t#bar{t}b#bar{b}", directory=['/scratch-cbe/users/cristina.giordano/tttt/nanoTuples/tttt_v9/UL2018/dilep/TTbb_MS_EFT'])
TTbb_EFT.reweight_pkl = '/groups/hephy/cms/robert.schoefbeck/gridpacks/4top/TTbb_MS_reweight_card.pkl'
TTTT_EFT    = Sample.fromDirectory(name="TTTT_EFT", treeName="Events", isData=False, color=color.TTTT, texName="t#bar{t}t#bar{t}", directory=['/scratch-cbe/users/cristina.giordano/tttt/nanoTuples/tttt_v9/UL2018/dilep/TTTT_MS_EFT'])
TTTT_EFT.reweight_pkl = '/eos/vbc/group/cms/robert.schoefbeck/gridpacks/4top/TTTT_MS_reweight_card.pkl'

TTbb_cQQ1_quad = Sample.fromDirectory(name="TTbb_cQQ1_quad", treeName="Events", isData=False, color=ROOT.kBlue, texName="t#bar{t}b#bar{b}_cQQ1_quad", directory=['/scratch-cbe/users/maryam.shooshtari/tttt/nanoTuples/tttt_v10/UL2018/dilep-nlepFO2p-ht500/TTbb_cQQ1_quad'])
TTbb_cQQ1_lin = Sample.fromDirectory(name="TTbb_cQQ1_lin", treeName="Events", isData=False, color=ROOT.kCyan, texName="t#bar{t}b#bar{b}_cQQ1_lin", directory=['/scratch-cbe/users/maryam.shooshtari/tttt/nanoTuples/tttt_v10/UL2018/dilep-nlepFO2p-ht500/TTbb_cQQ1_lin'])

TTbb_SMonly = Sample.fromDirectory(name="TTbb_SMonly", treeName="Events", isData=False, color=ROOT.kCyan+3, texName="t#bar{t}b#bar{b}_LO", directory=['/scratch-cbe/users/maryam.shooshtari/tttt/nanoTuples/tttt_v10/UL2018/dilep-nlepFO2p-ht500/TTbb_SMonly'])

##samples w/ extra jets

TTbb01j_cQQ1_quad = Sample.fromDirectory(name="TTbb01j_cQQ1_quad", treeName="Events", isData=False, color=ROOT.kBlue, texName="t#bar{t}b#bar{b}_cQQ1_quad", directory=['/scratch-cbe/users/maryam.shooshtari/tttt/nanoTuples/tttt_v10/UL2018/dilep-nlepFO2p-ht500/TTbb01j_cQQ1_quad'])

TTbb01j_cQQ1_lin = Sample.fromDirectory(name="TTbb01j_cQQ1_lin", treeName="Events", isData=False, color=ROOT.kCyan, texName="t#bar{t}b#bar{b}_cQQ1_lin", directory=['/scratch-cbe/users/maryam.shooshtari/tttt/nanoTuples/tttt_v10/UL2018/dilep-nlepFO2p-ht500/TTbb01j_cQQ1_lin'])

TTbb01j_SMonly = Sample.fromDirectory(name="TTbb01j_SMonly", treeName="Events", isData=False, color=ROOT.kCyan+3, texName="t#bar{t}b#bar{b}_LO", directory=['/scratch-cbe/users/maryam.shooshtari/tttt/nanoTuples/tttt_v10/UL2018/dilep-nlepFO2p-ht500/TTbb01j_SMonly'])
TTbb01j_SMonly.scale = 8.55 
