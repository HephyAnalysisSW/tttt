import copy, os, sys
from RootTools.core.Sample import Sample
import ROOT

def get_parser():
    import argparse
    argParser = argparse.ArgumentParser(description = "Argument parser for samples file")
    argParser.add_argument('--overwrite',   action='store_true',    help="Overwrite current entry in db?")
    argParser.add_argument('--update',      action='store_true',    help="Update current entry in db?")
    argParser.add_argument('--check_completeness', action='store_true',    help="Check competeness?")
    return argParser

# Logging
if __name__=="__main__":
    import Samples.Tools.logger as logger
    logger = logger.get_logger("INFO", logFile = None )
    import RootTools.core.logger as logger_rt
    logger_rt = logger_rt.get_logger("INFO", logFile = None )
    options = get_parser().parse_args()
    ov = options.overwrite
    if options.update:
        ov = 'update'
else:
    import logging
    logger = logging.getLogger(__name__)
    ov = False

#from Samples.Tools.config import  redirector_clip as redirector
from Samples.Tools.config import redirector_global as redirector

# DB
from Samples.Tools.config import dbDir
#dbFile = dbDir+'/nano_mc_private_UL20.sql'
dbFile = dbDir+'/DB_UL17_nanoAODv9.sql'
logger.info("Using db file: %s", dbFile)

from Samples.nanoAOD.UL17_nanoAODv9 import *
################################################################################
# MadGraph samples
TTTT_MS_EFT = Sample.fromDirectory("TTTT_MS_EFT", "/eos/vbc/group/cms/cristina.giordano/tttt/nanoAOD/Run2SIM_UL2017NANOAOD/TTTT_13TeV_madgraph_pythia8_Run2SIM_UL2017MiniAOD", xSection=0.01197, redirector="root://eos.grid.vbc.ac.at/")
TTTT_MS_EFT.reweight_pkl = '/groups/hephy/cms/robert.schoefbeck/gridpacks/4top/TTTT_MS_reweight_card.pkl'
TTTT_MS_EFT.normalization = 343800.0
TTbb_MS_EFT = Sample.fromDirectory("TTbb_MS_EFT", "/eos/vbc/group/cms/cristina.giordano/tttt/nanoAOD/Run2SIM_UL2017NANOAOD/TTbb_13TeV_madgraph_pythia8_Run2SIM_UL2017MiniAOD", xSection=4.59, redirector = "root://eos.grid.vbc.ac.at/")
TTbb_MS_EFT.reweight_pkl = '/groups/hephy/cms/robert.schoefbeck/gridpacks/4top/TTbb_MS_reweight_card.pkl'
TTbb_MS_EFT.normalization = 149400.0
################################################################################
# Rare processes

TTTT.xSection = 0.01197
TTWW.xSection = 0.007003
TTWZ.xSection = 0.002453
TTZZ.xSection = 0.001386
TTHH.xSection = 0.0006655
TTWH.xSection = 0.001141
TTZH.xSection = 0.00113
TTTJ.xSection = 0.0003974
TTTW.xSection = 0.0007314

################################################################################
# TTbar

TTLep_pow_CP5.xSection = 88.4
TTLep_pow_CP5.topScaleF =  1.03957041204
TTLep_pow_CP5_hDown  = Sample.nanoAODfromDAS("TTLep_pow_CP5_hDown","/TTTo2L2Nu_hdampDOWN_TuneCP5_13TeV-powheg-pythia8/RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v1/NANOAODSIM", dbFile=dbFile, redirector=redirector, instance="global", overwrite=ov, xSection=88.4)
TTLep_pow_CP5_hUp    = Sample.nanoAODfromDAS("TTLep_pow_CP5_hUp","/TTTo2L2Nu_hdampUP_TuneCP5_13TeV-powheg-pythia8/RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v1/NANOAODSIM", dbFile=dbFile, redirector=redirector, instance="global", overwrite=ov, xSection=88.4)
TTSingleLep_pow_CP5.xSection = 365.34
TTHad_pow_CP5.xSection = 377.96
TTbb.xSection = 4.59
TTbb_pow_CP5_hDown   = Sample.nanoAODfromDAS("TTbb_pow_CP5_hDown","/TTbb_4f_TTTo2L2Nu_hdampDOWN_TuneCP5-Powheg-Openloops-Pythia8/RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v1/NANOAODSIM", dbFile=dbFile, redirector=redirector, instance="global", overwrite=ov, xSection=4.59)
TTbb_pow_CP5_hUp     = Sample.nanoAODfromDAS("TTbb_pow_CP5_hUp",  "/TTbb_4f_TTTo2L2Nu_hdampUP_TuneCP5-Powheg-Openloops-Pythia8/RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v1/NANOAODSIM", dbFile=dbFile, redirector=redirector, instance="global", overwrite=ov, xSection=4.59)

################################################################################
# TTX

TTWToLNu.xSection = 0.235
TTWToQQ.xSection = 0.486
TTZToQQ.xSection = 0.5297
TTZToLLNuNu.xSection = 0.258

################################################################################
# Single top

T_tch_pow.xSection = 136.02
TBar_tch_pow.xSection = 35.85*(1.-(1.-0.108*3)*(1.-0.108*3))
T_tWch.xSection = 35.85*(1.-(1.-0.108*3)*(1.-0.108*3))
TBar_tWch.xSection = 35.85*(1.-(1.-0.108*3)*(1.-0.108*3))

WZTo3LNu.xSection = 4.9173
ZZTo4L.xSection = 1.256
WWW_4F.xSection = 0.2086
WWZ_4F.xSection = 0.1651
WZZ.xSection = 0.05565
ZZZ.xSection = 0.01476

################################################################################
#TTLep_pow_CP5 = Sample.nanoAODfromDAS("TTLep_pow_CP5", "/TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8/schoef-crab_RunIISummer20UL17MiniAODv2-106X_mc2017_realistic_v9-v1_nano_mc_UL20_private_v1-cf6bc7eaa3357168d675b8cf13f03a3a/USER", dbFile=dbFile, redirector=redirector, instance="phys03", overwrite=ov, xSection=831.762*((3*0.108)**2))
#TTTT          = Sample.nanoAODfromDAS("TTTT", "/TTTT_TuneCP5_13TeV-amcatnlo-pythia8/schoef-crab_RunIISummer20UL17MiniAODv2-106X_mc2017_realistic_v9-v2_nano_mc_UL20_private_v1-cf6bc7eaa3357168d675b8cf13f03a3a/USER", dbFile=dbFile, redirector=redirector, instance="phys03", overwrite=ov, xSection=0.009103)
# TTTT                = Sample.nanoAODfromDAS("TTTT"               , "/TTTT_TuneCP5_13TeV-amcatnlo-pythia8/schoef-crab_RunIISummer20UL17MiniAODv2-106X_mc2017_realistic_v9-v2_nano_mc_UL20_private_v2-369a15ee052290d76321a570b109af97/USER", dbFile=dbFile, redirector=redirector, instance="phys03", overwrite=ov, xSection=0.01197)
# TTLep_pow_CP5       = Sample.nanoAODfromDAS("TTLep_pow_CP5"      , "/TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8/schoef-crab_RunIISummer20UL17MiniAODv2-106X_mc2017_realistic_v9-v1_nano_mc_UL20_private_v2-369a15ee052290d76321a570b109af97/USER", dbFile=dbFile, redirector=redirector, instance="phys03", overwrite=ov, xSection=88.4)
# TTLep_pow_CP5.topScaleF = 1.03948982468
# T_tch_pow           = Sample.nanoAODfromDAS("T_tch_pow"    ,"/ST_t-channel_top_4f_InclusiveDecays_TuneCP5_13TeV-powheg-madspin-pythia8/schoef-crab_RunIISummer20UL17MiniAODv2-106X_mc2017_realistic_v9-v1_nano_mc_UL20_private_v2-369a15ee052290d76321a570b109af97/USER", dbFile=dbFile, redirector=redirector, instance="phys03", overwrite=ov, xSection= 136.02)
# Tbar_tch_pow        = Sample.nanoAODfromDAS("Tbar_tch_pow" ,"/ST_t-channel_antitop_4f_InclusiveDecays_TuneCP5_13TeV-powheg-madspin-pythia8/schoef-crab_RunIISummer20UL17MiniAODv2-106X_mc2017_realistic_v9-v1_nano_mc_UL20_private_v2-369a15ee052290d76321a570b109af97/USER", dbFile=dbFile, redirector=redirector, instance="phys03", overwrite=ov, xSection= 80.95)
# T_tWch              = Sample.nanoAODfromDAS("T_tWch"       ,"/ST_tW_top_5f_NoFullyHadronicDecays_TuneCP5_13TeV-powheg-pythia8/schoef-crab_RunIISummer20UL17MiniAODv2-106X_mc2017_realistic_v9-v1_nano_mc_UL20_private_v2-369a15ee052290d76321a570b109af97/USER", dbFile=dbFile, redirector=redirector, instance="phys03", overwrite=ov, xSection= 35.85*(1.-(1.-0.108*3)*(1.-0.108*3)))
# TBar_tWch           = Sample.nanoAODfromDAS("TBar_tWch"    ,"/ST_tW_antitop_5f_NoFullyHadronicDecays_TuneCP5_13TeV-powheg-pythia8/schoef-crab_RunIISummer20UL17MiniAODv2-106X_mc2017_realistic_v9-v1_nano_mc_UL20_private_v2-369a15ee052290d76321a570b109af97/USER", dbFile=dbFile, redirector=redirector, instance="phys03", overwrite=ov, xSection= 35.85*(1.-(1.-0.108*3)*(1.-0.108*3)))
# TTWToLNu            = Sample.nanoAODfromDAS("TTWToLNu"           , "/TTWJetsToLNu_TuneCP5_13TeV-amcatnloFXFX-madspin-pythia8/schoef-crab_RunIISummer20UL17MiniAODv2-106X_mc2017_realistic_v9-v1_nano_mc_UL20_private_v2-369a15ee052290d76321a570b109af97/USER", dbFile=dbFile, redirector=redirector, instance="phys03", overwrite=ov, xSection=0.235)
# TTWToQQ             = Sample.nanoAODfromDAS("TTWToQQ"            , "/TTWJetsToQQ_TuneCP5_13TeV-amcatnloFXFX-madspin-pythia8/schoef-crab_RunIISummer20UL17MiniAODv2-106X_mc2017_realistic_v9-v1_nano_mc_UL20_private_v2-369a15ee052290d76321a570b109af97/USER", dbFile=dbFile, redirector=redirector, instance="phys03", overwrite=ov, xSection=0.486)
# TTZToLLNuNu         = Sample.nanoAODfromDAS("TTZToLLNuNu"        , "/TTZToLLNuNu_M-10_TuneCP5_13TeV-amcatnlo-pythia8/schoef-crab_RunIISummer20UL17MiniAODv2-106X_mc2017_realistic_v9-v1_nano_mc_UL20_private_v2-369a15ee052290d76321a570b109af97/USER", dbFile=dbFile, redirector=redirector, instance="phys03", overwrite=ov, xSection=0.258)
# TTZToLLNuNu_m1to10  = Sample.nanoAODfromDAS("TTZToLLNuNu_m1to10" , "/TTZToLL_M-1to10_TuneCP5_13TeV-amcatnlo-pythia8/schoef-crab_RunIISummer20UL17MiniAODv2-106X_mc2017_realistic_v9-v2_nano_mc_UL20_private_v2-369a15ee052290d76321a570b109af97/USER", dbFile=dbFile, redirector=redirector, instance="phys03", overwrite=ov, xSection=0.0532)
# TTZToQQ             = Sample.nanoAODfromDAS("TTZToQQ"            , "/TTZToQQ_TuneCP5_13TeV-amcatnlo-pythia8/schoef-crab_RunIISummer20UL17MiniAODv2-106X_mc2017_realistic_v9-v1_nano_mc_UL20_private_v2-369a15ee052290d76321a570b109af97/USER", dbFile=dbFile, redirector=redirector, instance="phys03", overwrite=ov, xSection=0.5297)
# TTHnobb             = Sample.nanoAODfromDAS("TTHnobb"            , "/ttHToNonbb_M125_TuneCP5_13TeV-powheg-pythia8/schoef-crab_RunIISummer20UL17MiniAODv2-106X_mc2017_realistic_v9-v2_nano_mc_UL20_private_v2-369a15ee052290d76321a570b109af97/USER", dbFile=dbFile, redirector=redirector, instance="phys03", overwrite=ov, xSection=0.5085*(1-0.577))
# TTHTobb             = Sample.nanoAODfromDAS("TTHTobb"            , "/ttHTobb_M125_TuneCP5_13TeV-powheg-pythia8/schoef-crab_RunIISummer20UL17MiniAODv2-106X_mc2017_realistic_v9-v2_nano_mc_UL20_private_v2-369a15ee052290d76321a570b109af97/USER", dbFile=dbFile, redirector=redirector, instance="phys03", overwrite=ov, xSection=0.5085*(0.577))
# TTbb                = Sample.nanoAODfromDAS("TTbb"               , "/TTbb_4f_TTTo2L2Nu_TuneCP5-Powheg-Openloops-Pythia8/schoef-crab_RunIISummer20UL17MiniAODv2-106X_mc2017_realistic_v9-v1_nano_mc_UL20_private_v2-369a15ee052290d76321a570b109af97/USER", dbFile=dbFile, redirector=redirector, instance="phys03", overwrite=ov, xSection=4.59)
# TTbb_pow_CP5_hDown  = Sample.nanoAODfromDAS("TTbb_pow_CP5_hDown","/TTbb_4f_TTTo2L2Nu_hdampDOWN_TuneCP5-Powheg-Openloops-Pythia8/RunIISummer20UL17NanoAODv9-106X_mc2017_realistic_v9-v1/NANOAODSIM", dbFile=dbFile, redirector=redirector, instance="global", overwrite=ov, xSection=4.59)
# TTbb_pow_CP5_hUp    = Sample.nanoAODfromDAS("TTbb_pow_CP5_hUp",  "/TTbb_4f_TTTo2L2Nu_hdampUP_TuneCP5-Powheg-Openloops-Pythia8/RunIISummer20UL17NanoAODv9-106X_mc2017_realistic_v9-v1/NANOAODSIM", dbFile=dbFile, redirector=redirector, instance="global", overwrite=ov, xSection=4.59)
# TTLep_pow_CP5_hDown = Sample.nanoAODfromDAS("TTLep_pow_CP5_hDown","/TTTo2L2Nu_hdampDOWN_TuneCP5_13TeV-powheg-pythia8/RunIISummer20UL17NanoAODv9-106X_mc2017_realistic_v9-v1/NANOAODSIM", dbFile=dbFile, redirector=redirector, instance="global", overwrite=ov, xSection=88.4)
# TTLep_pow_CP5_hUp   = Sample.nanoAODfromDAS("TTLep_pow_CP5_hUp","/TTTo2L2Nu_hdampUP_TuneCP5_13TeV-powheg-pythia8/RunIISummer20UL17NanoAODv9-106X_mc2017_realistic_v9-v1/NANOAODSIM", dbFile=dbFile, redirector=redirector, instance="global", overwrite=ov, xSection=88.4)
# TTSingleLep_pow_CP5 = Sample.nanoAODfromDAS("TTSingleLep_pow_CP5",      "/TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8/RunIISummer20UL17NanoAODv9-106X_mc2017_realistic_v9-v1/NANOAODSIM",      dbFile=dbFile, redirector=redirector, instance="global", overwrite=ov, xSection=365.34)
################################################################################

EFTSamples = [TTTT_MS_EFT, TTbb_MS_EFT]

allSamples = [TTTT, TTWW, TTWZ, TTZZ, TTHH, TTWH, TTZH, TTTJ, TTTW,
              TTLep_pow_CP5, TTLep_pow_CP5_hDown, TTLep_pow_CP5_hUp,
              TTSingleLep_pow_CP5, TTHad_pow_CP5, TTbb,
              TTbb_pow_CP5_hDown, TTbb_pow_CP5_hUp,
              TTHTobb, TTHnobb, TTWToLNu, TTWToQQ, TTZToQQ, TTZToLLNuNu,
              T_tch_pow, TBar_tch_pow, T_tWch, TBar_tWch,
              DYJetsToLL_M50_HT100to200, DYJetsToLL_M50_HT200to400,
              DYJetsToLL_M50_HT400to600, DYJetsToLL_M50_HT600to800,
              DYJetsToLL_M50_HT800to1200, DYJetsToLL_M50_HT1200to2500,
              DYJetsToLL_M50_HT2500toInf, DYJetsToLL_M4to50_HT100to200,
              DYJetsToLL_M4to50_HT200to400, DYJetsToLL_M4to50_HT400to600,
              DYJetsToLL_M4to50_HT600toInf, DYJetsToLL_M10to50, DYJetsToLL_M50,
              WZTo3LNu, ZZTo4L, WWW_4F, WWZ_4F, WZZ, ZZZ, SSWW
    ]

allSamples += EFTSamples

for s in allSamples:
    s.isData = False

from Samples.Tools.AutoClass import AutoClass
samples = AutoClass( allSamples )
if __name__=="__main__":
    if options.check_completeness:
        samples.check_completeness( cores=20 )
