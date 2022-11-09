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

from Samples.Tools.config import  redirector_global
redirector = redirector_global

# DB
from Samples.Tools.config import dbDir
dbFile = dbDir+'/nano_mc_private_UL20.sql'

logger.info("Using db file: %s", dbFile)

#TTLep_pow_CP5 = Sample.nanoAODfromDAS("TTLep_pow_CP5", "/TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8/schoef-crab_RunIISummer20UL17MiniAODv2-106X_mc2017_realistic_v9-v1_nano_mc_UL20_private_v1-cf6bc7eaa3357168d675b8cf13f03a3a/USER", dbFile=dbFile, redirector=redirector, instance="phys03", overwrite=ov, xSection=831.762*((3*0.108)**2))
#TTTT          = Sample.nanoAODfromDAS("TTTT", "/TTTT_TuneCP5_13TeV-amcatnlo-pythia8/schoef-crab_RunIISummer20UL17MiniAODv2-106X_mc2017_realistic_v9-v2_nano_mc_UL20_private_v1-cf6bc7eaa3357168d675b8cf13f03a3a/USER", dbFile=dbFile, redirector=redirector, instance="phys03", overwrite=ov, xSection=0.009103)

TTTT                = Sample.nanoAODfromDAS("TTTT"               , "/TTTT_TuneCP5_13TeV-amcatnlo-pythia8/schoef-crab_RunIISummer20UL17MiniAODv2-106X_mc2017_realistic_v9-v2_nano_mc_UL20_private_v2-369a15ee052290d76321a570b109af97/USER", dbFile=dbFile, redirector=redirector, instance="phys03", overwrite=ov, xSection=0.009103)
TTLep_pow_CP5       = Sample.nanoAODfromDAS("TTLep_pow_CP5"      , "/TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8/schoef-crab_RunIISummer20UL17MiniAODv2-106X_mc2017_realistic_v9-v1_nano_mc_UL20_private_v2-369a15ee052290d76321a570b109af97/USER", dbFile=dbFile, redirector=redirector, instance="phys03", overwrite=ov, xSection=831.762*((3*0.108)**2))
T_tch_pow           = Sample.nanoAODfromDAS("T_tch_pow"    ,"/ST_t-channel_top_4f_InclusiveDecays_TuneCP5_13TeV-powheg-madspin-pythia8/schoef-crab_RunIISummer20UL17MiniAODv2-106X_mc2017_realistic_v9-v1_nano_mc_UL20_private_v2-369a15ee052290d76321a570b109af97/USER", dbFile=dbFile, redirector=redirector, instance="phys03", overwrite=ov, xSection= 136.02)
Tbar_tch_pow        = Sample.nanoAODfromDAS("Tbar_tch_pow" ,"/ST_t-channel_antitop_4f_InclusiveDecays_TuneCP5_13TeV-powheg-madspin-pythia8/schoef-crab_RunIISummer20UL17MiniAODv2-106X_mc2017_realistic_v9-v1_nano_mc_UL20_private_v2-369a15ee052290d76321a570b109af97/USER", dbFile=dbFile, redirector=redirector, instance="phys03", overwrite=ov, xSection= 80.95)
T_tWch              = Sample.nanoAODfromDAS("T_tWch"       ,"/ST_tW_top_5f_NoFullyHadronicDecays_TuneCP5_13TeV-powheg-pythia8/schoef-crab_RunIISummer20UL17MiniAODv2-106X_mc2017_realistic_v9-v1_nano_mc_UL20_private_v2-369a15ee052290d76321a570b109af97/USER", dbFile=dbFile, redirector=redirector, instance="phys03", overwrite=ov, xSection= 35.85*(1.-(1.-0.108*3)*(1.-0.108*3)))
TBar_tWch           = Sample.nanoAODfromDAS("TBar_tWch"    ,"/ST_tW_antitop_5f_NoFullyHadronicDecays_TuneCP5_13TeV-powheg-pythia8/schoef-crab_RunIISummer20UL17MiniAODv2-106X_mc2017_realistic_v9-v1_nano_mc_UL20_private_v2-369a15ee052290d76321a570b109af97/USER", dbFile=dbFile, redirector=redirector, instance="phys03", overwrite=ov, xSection= 35.85*(1.-(1.-0.108*3)*(1.-0.108*3)))
TTWToLNu            = Sample.nanoAODfromDAS("TTWToLNu"           , "/TTWJetsToLNu_TuneCP5_13TeV-amcatnloFXFX-madspin-pythia8/schoef-crab_RunIISummer20UL17MiniAODv2-106X_mc2017_realistic_v9-v1_nano_mc_UL20_private_v2-369a15ee052290d76321a570b109af97/USER", dbFile=dbFile, redirector=redirector, instance="phys03", overwrite=ov, xSection=0.2043)
TTWToQQ             = Sample.nanoAODfromDAS("TTWToQQ"            , "/TTWJetsToQQ_TuneCP5_13TeV-amcatnloFXFX-madspin-pythia8/schoef-crab_RunIISummer20UL17MiniAODv2-106X_mc2017_realistic_v9-v1_nano_mc_UL20_private_v2-369a15ee052290d76321a570b109af97/USER", dbFile=dbFile, redirector=redirector, instance="phys03", overwrite=ov, xSection=0.40620)
TTZToLLNuNu         = Sample.nanoAODfromDAS("TTZToLLNuNu"        , "/TTZToLLNuNu_M-10_TuneCP5_13TeV-amcatnlo-pythia8/schoef-crab_RunIISummer20UL17MiniAODv2-106X_mc2017_realistic_v9-v1_nano_mc_UL20_private_v2-369a15ee052290d76321a570b109af97/USER", dbFile=dbFile, redirector=redirector, instance="phys03", overwrite=ov, xSection=0.2728)
TTZToLLNuNu_m1to10  = Sample.nanoAODfromDAS("TTZToLLNuNu_m1to10" , "/TTZToLL_M-1to10_TuneCP5_13TeV-amcatnlo-pythia8/schoef-crab_RunIISummer20UL17MiniAODv2-106X_mc2017_realistic_v9-v2_nano_mc_UL20_private_v2-369a15ee052290d76321a570b109af97/USER", dbFile=dbFile, redirector=redirector, instance="phys03", overwrite=ov, xSection=0.0493)
TTZToQQ             = Sample.nanoAODfromDAS("TTZToQQ"            , "/TTZToQQ_TuneCP5_13TeV-amcatnlo-pythia8/schoef-crab_RunIISummer20UL17MiniAODv2-106X_mc2017_realistic_v9-v1_nano_mc_UL20_private_v2-369a15ee052290d76321a570b109af97/USER", dbFile=dbFile, redirector=redirector, instance="phys03", overwrite=ov, xSection=0.5297)
TTHnobb             = Sample.nanoAODfromDAS("TTHnobb"            , "/ttHToNonbb_M125_TuneCP5_13TeV-powheg-pythia8/schoef-crab_RunIISummer20UL17MiniAODv2-106X_mc2017_realistic_v9-v2_nano_mc_UL20_private_v2-369a15ee052290d76321a570b109af97/USER", dbFile=dbFile, redirector=redirector, instance="phys03", overwrite=ov, xSection=0.5085*(1-0.577))
TTHTobb             = Sample.nanoAODfromDAS("TTHTobb"            , "/ttHTobb_M125_TuneCP5_13TeV-powheg-pythia8/schoef-crab_RunIISummer20UL17MiniAODv2-106X_mc2017_realistic_v9-v2_nano_mc_UL20_private_v2-369a15ee052290d76321a570b109af97/USER", dbFile=dbFile, redirector=redirector, instance="phys03", overwrite=ov, xSection=0.5085*(0.577))

allSamples = [ TTTT, TTLep_pow_CP5, T_tch_pow, Tbar_tch_pow, T_tWch, TBar_tWch, TTWToLNu, TTWToQQ, TTZToLLNuNu, TTZToLLNuNu_m1to10, TTZToQQ, TTHnobb, TTHTobb]

for s in allSamples:
    s.isData = False

from Samples.Tools.AutoClass import AutoClass
samples = AutoClass( allSamples )
if __name__=="__main__":
    if options.check_completeness:
        samples.check_completeness( cores=20 )
