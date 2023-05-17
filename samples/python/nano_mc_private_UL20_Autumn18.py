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
dbFile = dbDir+'/nano_mc_private_UL20_Run2018.sql'

logger.info("Using db file: %s", dbFile)

#TTLep_pow_CP5 = Sample.nanoAODfromDAS("TTLep_pow_CP5", "/TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8/schoef-crab_RunIISummer20UL18MiniAODv2-106X_upgrade2018_realistic_v16_L1v1-v1_nano_mc_UL20_private_v1-be97bb1179c64af1e45e5c6521726198/USER", dbFile=dbFile, redirector=redirector, instance="phys03", overwrite=ov, xSection=831.762*((3*0.108)**2))
#TTTT          = Sample.nanoAODfromDAS("TTTT", "/TTTT_TuneCP5_13TeV-amcatnlo-pythia8/schoef-crab_RunIISummer20UL18MiniAODv2-106X_upgrade2018_realistic_v16_L1v1-v2_nano_mc_UL20_private_v1-be97bb1179c64af1e45e5c6521726198/USER", dbFile=dbFile, redirector=redirector, instance="phys03", overwrite=ov, xSection=0.009103)

TTTT                 = Sample.nanoAODfromDAS("TTTT"              , "/TTTT_TuneCP5_13TeV-amcatnlo-pythia8/schoef-crab_RunIISummer20UL18MiniAODv2-106X_upgrade2018_realistic_v16_L1v1-v2_nano_mc_UL20_private_v2-f7efd77530810e0d3aa782b723e6d6d7/USER", dbFile=dbFile, redirector=redirector, instance="phys03", overwrite=ov, xSection=0.01197)
TTLep_pow_CP5        = Sample.nanoAODfromDAS("TTLep_pow_CP5"     , "/TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8/schoef-crab_RunIISummer20UL18MiniAODv2-106X_upgrade2018_realistic_v16_L1v1-v1_nano_mc_UL20_private_v2-f7efd77530810e0d3aa782b723e6d6d7/USER", dbFile=dbFile, redirector=redirector, instance="phys03", overwrite=ov, xSection=88.4)
TTLep_pow_CP5.topScaleF =  1.03957041204
T_tch_pow            = Sample.nanoAODfromDAS("T_tch_pow"         , "/ST_t-channel_top_4f_InclusiveDecays_TuneCP5_13TeV-powheg-madspin-pythia8/schoef-crab_RunIISummer20UL18MiniAODv2-106X_upgrade2018_realistic_v16_L1v1-v1_nano_mc_UL20_private_v2-f7efd77530810e0d3aa782b723e6d6d7/USER", dbFile=dbFile, redirector=redirector, instance="phys03", overwrite=ov, xSection= 136.02)
Tbar_tch_pow         = Sample.nanoAODfromDAS("Tbar_tch_pow"      , "/ST_t-channel_antitop_4f_InclusiveDecays_TuneCP5_13TeV-powheg-madspin-pythia8/schoef-crab_RunIISummer20UL18MiniAODv2-106X_upgrade2018_realistic_v16_L1v1-v1_nano_mc_UL20_private_v2-f7efd77530810e0d3aa782b723e6d6d7/USER", dbFile=dbFile, redirector=redirector, instance="phys03", overwrite=ov, xSection= 80.95)
T_tWch               = Sample.nanoAODfromDAS("T_tWch"            , "/ST_tW_top_5f_NoFullyHadronicDecays_TuneCP5_13TeV-powheg-pythia8/schoef-crab_RunIISummer20UL18MiniAODv2-106X_upgrade2018_realistic_v16_L1v1-v1_nano_mc_UL20_private_v2-f7efd77530810e0d3aa782b723e6d6d7/USER", dbFile=dbFile, redirector=redirector, instance="phys03", overwrite=ov, xSection= 35.85*(1.-(1.-0.108*3)*(1.-0.108*3)))
TBar_tWch            = Sample.nanoAODfromDAS("TBar_tWch"         , "/ST_tW_antitop_5f_NoFullyHadronicDecays_TuneCP5_13TeV-powheg-pythia8/schoef-crab_RunIISummer20UL18MiniAODv2-106X_upgrade2018_realistic_v16_L1v1-v1_nano_mc_UL20_private_v2-f7efd77530810e0d3aa782b723e6d6d7/USER", dbFile=dbFile, redirector=redirector, instance="phys03", overwrite=ov, xSection= 35.85*(1.-(1.-0.108*3)*(1.-0.108*3)))
TTWToLNu             = Sample.nanoAODfromDAS("TTWToLNu"          , "/TTWJetsToLNu_TuneCP5_13TeV-amcatnloFXFX-madspin-pythia8/schoef-crab_RunIISummer20UL18MiniAODv2-106X_upgrade2018_realistic_v16_L1v1-v1_nano_mc_UL20_private_v2-f7efd77530810e0d3aa782b723e6d6d7/USER", dbFile=dbFile, redirector=redirector, instance="phys03", overwrite=ov, xSection=0.235)
TTWToQQ              = Sample.nanoAODfromDAS("TTWToQQ"           , "/TTWJetsToQQ_TuneCP5_13TeV-amcatnloFXFX-madspin-pythia8/schoef-crab_RunIISummer20UL18MiniAODv2-106X_upgrade2018_realistic_v16_L1v1-v1_nano_mc_UL20_private_v2-f7efd77530810e0d3aa782b723e6d6d7/USER", dbFile=dbFile, redirector=redirector, instance="phys03", overwrite=ov, xSection=0.486)
TTZToLLNuNu          = Sample.nanoAODfromDAS("TTZToLLNuNu"       , "/TTZToLLNuNu_M-10_TuneCP5_13TeV-amcatnlo-pythia8/schoef-crab_RunIISummer20UL18MiniAODv2-106X_upgrade2018_realistic_v16_L1v1-v2_nano_mc_UL20_private_v2-f7efd77530810e0d3aa782b723e6d6d7/USER", dbFile=dbFile, redirector=redirector, instance="phys03", overwrite=ov, xSection=0.258)
TTZToLLNuNu_m1to10   = Sample.nanoAODfromDAS("TTZToLLNuNu_m1to10", "/TTZToLL_M-1to10_TuneCP5_13TeV-amcatnlo-pythia8/schoef-crab_RunIISummer20UL18MiniAODv2-106X_upgrade2018_realistic_v16_L1v1-v2_nano_mc_UL20_private_v2-f7efd77530810e0d3aa782b723e6d6d7/USER", dbFile=dbFile, redirector=redirector, instance="phys03", overwrite=ov, xSection=0.0532)
TTZToQQ              = Sample.nanoAODfromDAS("TTZToQQ"           , "/TTZToQQ_TuneCP5_13TeV-amcatnlo-pythia8/schoef-crab_RunIISummer20UL18MiniAODv2-106X_upgrade2018_realistic_v16_L1v1-v1_nano_mc_UL20_private_v2-f7efd77530810e0d3aa782b723e6d6d7/USER", dbFile=dbFile, redirector=redirector, instance="phys03", overwrite=ov, xSection=0.5297)
TTHnobb              = Sample.nanoAODfromDAS("TTHnobb"           , "/ttHToNonbb_M125_TuneCP5_13TeV-powheg-pythia8/schoef-crab_RunIISummer20UL18MiniAODv2-106X_upgrade2018_realistic_v16_L1v1-v2_nano_mc_UL20_private_v2-f7efd77530810e0d3aa782b723e6d6d7/USER", dbFile=dbFile, redirector=redirector, instance="phys03", overwrite=ov, xSection=0.5085*(1-0.577))
TTHTobb              = Sample.nanoAODfromDAS("TTHTobb"           , "/ttHTobb_M125_TuneCP5_13TeV-powheg-pythia8/schoef-crab_RunIISummer20UL18MiniAODv2-106X_upgrade2018_realistic_v16_L1v1-v2_nano_mc_UL20_private_v2-f7efd77530810e0d3aa782b723e6d6d7/USER", dbFile=dbFile, redirector=redirector, instance="phys03", overwrite=ov, xSection=0.5085*(0.577))
TTbb                 = Sample.nanoAODfromDAS( "TTbb"             , "/TTbb_4f_TTTo2L2Nu_TuneCP5-Powheg-Openloops-Pythia8/schoef-crab_RunIISummer20UL18MiniAODv2-106X_upgrade2018_realistic_v16_L1v1-v1_nano_mc_UL20_private_v2-f7efd77530810e0d3aa782b723e6d6d7/USER", dbFile=dbFile, redirector=redirector, instance="phys03", overwrite=ov, xSection=4.59)
#TTbb_ToLep_pow_CP5_hDown           = Sample.nanoAODfromDAS("TTbb_ToLep_pow_CP5_hDown","/TTbb_4f_TTTo2L2Nu_hdampDOWN_TuneCP5-Powheg-Openloops-Pythia8/RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v1/NANOAODSIM", dbFile=dbFile, redirector=redirector, instance="global", overwrite=ov, xSection=4.59)
#TTbb_ToLep_pow_CP5_hUp             = Sample.nanoAODfromDAS("TTbb_ToLep_pow_CP5_hUp",  "/TTbb_4f_TTTo2L2Nu_hdampUP_TuneCP5-Powheg-Openloops-Pythia8/RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v1/NANOAODSIM", dbFile=dbFIle, redirector=redirector, instance="global", overwrite=ov, xSection=4.59)
#TTbb_ToHad_pow_CP5_hDown           = Sample.nanoAODfromDAS("TTbb_ToHad_pow_CP5_hDown", /TTbb_4f_TTToHadronic_hdampDOWN_TuneCP5-Powheg-Openloops-Pythia8/RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v1/NANOAODSIM", dbFile=dbFile, redirector=redirector, instance="global", overwrite=ov, xSection=4.59)
#TTbb_ToHad_pow_CP5_hUp             = Sample.nanoAODfromDAS("TTbb_ToHad_pow_CP5_hUp", "/TTbb_4f_TTToHadronic_hdampUP_TuneCP5-Powheg-Openloops-Pythia8/RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v1/NANOAODSIM", dbFile=dbFile, redirector=redirector, instance="global", overwrite=ov, xSection=4.59)
#TTbb_SemiLeptonic_pow_CP5_hDown    = Sample.nanoAODfromDAS("TTbb_SemiLeptonic_pow_CP5_hDown", "/TTbb_4f_TTToSemiLeptonic_hdampDOWN_TuneCP5-Powheg-Openloops-Pythia8/RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v1/NANOAODSIM", dbFile=dbFile, redirector=redirector, instance="global", overwrite=ov, xSection=4.59)
#TTbb_SemiLeptonic_pow_CP5_hUp      = Sample.nanoAODfromDAS("TTbb_SemiLeptonic_pow_CP5_hUp", "/TTbb_4f_TTToSemiLeptonic_hdampUP_TuneCP5-Powheg-Openloops-Pythia8/RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v1/NANOAODSIM", dbFile=dbFile, redirector=redirector, instance="global", overwrite=ov, xSection=4.59)



#TTTT_sync miniAOD : https://cmsweb.cern.ch/das/request?instance=prod/global&input=dataset+file%3D%2Fstore%2Fmc%2FRunIISummer20UL18MiniAODv2%2FTTTT_TuneCP5_13TeV-amcatnlo-pythia8%2FMINIAODSIM%2F106X_upgrade2018_realistic_v16_L1v1-v2%2F2520000%2F01CC7B01-9F49-A44F-8B48-D8B913E73DB0.root
TTTT_sync            = Sample.fromFiles("TTTT_sync", ["/groups/hephy/cms/robert.schoefbeck/tttt/sync/nanoAOD.root"], xSection=1, normalization = 1)

allSamples = [ TTTT, TTLep_pow_CP5, T_tch_pow, Tbar_tch_pow, T_tWch, TBar_tWch, TTWToLNu, TTWToQQ, TTZToLLNuNu, TTZToLLNuNu_m1to10, TTZToQQ, TTHnobb, TTHTobb, TTTT_sync, TTbb]#, TTbb_ToLep_pow_CP5_hDown, TTbb_ToLep_pow_CP5_hUp, TTbb_ToHad_pow_CP5_hDown, #TTbb_ToHad_pow_CP5_hUp, TTbb_SemiLeptonic_pow_CP5_hDown, TTbb_SemiLeptonic_pow_CP5_hUp]

for s in allSamples:
    s.isData = False

from Samples.Tools.AutoClass import AutoClass
samples = AutoClass( allSamples )
if __name__=="__main__":
    if options.check_completeness:
        samples.check_completeness( cores=20 )
