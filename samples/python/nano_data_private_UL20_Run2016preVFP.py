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
dbFile = dbDir+'/nano_data_private_UL20.sql'

logger.info("Using db file: %s", dbFile)

SingleMuon_Run2016Bver1_preVFP     = Sample.nanoAODfromDAS("SingleMuon_Run2016Bver1_preVFP", "/SingleMuon/schoef-crab_Run2016B-ver1_HIPM_UL2016_MiniAODv2-v2_nano_data_UL20_private_v1-db7e530214851c2df75d13ca5dc648d7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
SingleMuon_Run2016Bver2_preVFP     = Sample.nanoAODfromDAS("SingleMuon_Run2016Bver2_preVFP", "/SingleMuon/schoef-crab_Run2016B-ver2_HIPM_UL2016_MiniAODv2-v2_nano_data_UL20_private_v1-db7e530214851c2df75d13ca5dc648d7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
SingleMuon_Run2016C_preVFP         = Sample.nanoAODfromDAS("SingleMuon_Run2016C_preVFP"    , "/SingleMuon/schoef-crab_Run2016C-HIPM_UL2016_MiniAODv2-v2_nano_data_UL20_private_v1-db7e530214851c2df75d13ca5dc648d7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
SingleMuon_Run2016D_preVFP         = Sample.nanoAODfromDAS("SingleMuon_Run2016D_preVFP"    , "/SingleMuon/schoef-crab_Run2016D-HIPM_UL2016_MiniAODv2-v2_nano_data_UL20_private_v1-db7e530214851c2df75d13ca5dc648d7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
SingleMuon_Run2016E_preVFP         = Sample.nanoAODfromDAS("SingleMuon_Run2016E_preVFP"    , "/SingleMuon/schoef-crab_Run2016E-HIPM_UL2016_MiniAODv2-v2_nano_data_UL20_private_v1-db7e530214851c2df75d13ca5dc648d7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
SingleMuon_Run2016F_preVFP         = Sample.nanoAODfromDAS("SingleMuon_Run2016F_preVFP"    , "/SingleMuon/schoef-crab_Run2016F-HIPM_UL2016_MiniAODv2-v2_nano_data_UL20_private_v1-db7e530214851c2df75d13ca5dc648d7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
SingleMuon_Run2016_preVFP = [SingleMuon_Run2016Bver1_preVFP, SingleMuon_Run2016Bver2_preVFP, SingleMuon_Run2016C_preVFP, SingleMuon_Run2016D_preVFP, SingleMuon_Run2016E_preVFP, SingleMuon_Run2016F_preVFP]

SingleElectron_Run2016Bver1_preVFP = Sample.nanoAODfromDAS("SingleElectron_Run2016Bver1_preVFP", "/SingleElectron/schoef-crab_Run2016B-ver1_HIPM_UL2016_MiniAODv2-v2_nano_data_UL20_private_v1-db7e530214851c2df75d13ca5dc648d7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
SingleElectron_Run2016Bver2_preVFP = Sample.nanoAODfromDAS("SingleElectron_Run2016Bver2_preVFP", "/SingleElectron/schoef-crab_Run2016B-ver2_HIPM_UL2016_MiniAODv2-v2_nano_data_UL20_private_v1-db7e530214851c2df75d13ca5dc648d7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
SingleElectron_Run2016C_preVFP     = Sample.nanoAODfromDAS("SingleElectron_Run2016C_preVFP"    , "/SingleElectron/schoef-crab_Run2016C-HIPM_UL2016_MiniAODv2-v2_nano_data_UL20_private_v1-db7e530214851c2df75d13ca5dc648d7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
SingleElectron_Run2016D_preVFP     = Sample.nanoAODfromDAS("SingleElectron_Run2016D_preVFP"    , "/SingleElectron/schoef-crab_Run2016D-HIPM_UL2016_MiniAODv2-v2_nano_data_UL20_private_v1-db7e530214851c2df75d13ca5dc648d7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
SingleElectron_Run2016E_preVFP     = Sample.nanoAODfromDAS("SingleElectron_Run2016E_preVFP"    , "/SingleElectron/schoef-crab_Run2016E-HIPM_UL2016_MiniAODv2-v5_nano_data_UL20_private_v1-db7e530214851c2df75d13ca5dc648d7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
SingleElectron_Run2016F_preVFP     = Sample.nanoAODfromDAS("SingleElectron_Run2016F_preVFP"    , "/SingleElectron/schoef-crab_Run2016F-HIPM_UL2016_MiniAODv2-v2_nano_data_UL20_private_v1-db7e530214851c2df75d13ca5dc648d7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
SingleElectron_Run2016_preVFP = [SingleElectron_Run2016Bver1_preVFP, SingleElectron_Run2016Bver2_preVFP, SingleElectron_Run2016C_preVFP, SingleElectron_Run2016D_preVFP, SingleElectron_Run2016E_preVFP, SingleElectron_Run2016F_preVFP]

DoubleMuon_Run2016Bver1_preVFP     = Sample.nanoAODfromDAS("DoubleMuon_Run2016Bver1_preVFP", "/DoubleMuon/schoef-crab_Run2016B-ver1_HIPM_UL2016_MiniAODv2-v1_nano_data_UL20_private_v1-db7e530214851c2df75d13ca5dc648d7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
DoubleMuon_Run2016Bver2_preVFP     = Sample.nanoAODfromDAS("DoubleMuon_Run2016Bver2_preVFP", "/DoubleMuon/schoef-crab_Run2016B-ver2_HIPM_UL2016_MiniAODv2-v1_nano_data_UL20_private_v1-db7e530214851c2df75d13ca5dc648d7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
DoubleMuon_Run2016C_preVFP         = Sample.nanoAODfromDAS("DoubleMuon_Run2016C_preVFP"    , "/DoubleMuon/schoef-crab_Run2016C-HIPM_UL2016_MiniAODv2-v1_nano_data_UL20_private_v1-db7e530214851c2df75d13ca5dc648d7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
DoubleMuon_Run2016D_preVFP         = Sample.nanoAODfromDAS("DoubleMuon_Run2016D_preVFP"    , "/DoubleMuon/schoef-crab_Run2016D-HIPM_UL2016_MiniAODv2-v1_nano_data_UL20_private_v1-db7e530214851c2df75d13ca5dc648d7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
DoubleMuon_Run2016E_preVFP         = Sample.nanoAODfromDAS("DoubleMuon_Run2016E_preVFP"    , "/DoubleMuon/schoef-crab_Run2016E-HIPM_UL2016_MiniAODv2-v1_nano_data_UL20_private_v1-db7e530214851c2df75d13ca5dc648d7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
DoubleMuon_Run2016F_preVFP         = Sample.nanoAODfromDAS("DoubleMuon_Run2016F_preVFP"    , "/DoubleMuon/schoef-crab_Run2016F-HIPM_UL2016_MiniAODv2-v1_nano_data_UL20_private_v1-db7e530214851c2df75d13ca5dc648d7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
DoubleMuon_Run2016_preVFP = [DoubleMuon_Run2016Bver1_preVFP, DoubleMuon_Run2016Bver2_preVFP, DoubleMuon_Run2016C_preVFP, DoubleMuon_Run2016D_preVFP, DoubleMuon_Run2016E_preVFP, DoubleMuon_Run2016F_preVFP]

DoubleEG_Run2016Bver1_preVFP       = Sample.nanoAODfromDAS("DoubleEG_Run2016Bver1_preVFP", "/DoubleEG/schoef-crab_Run2016B-ver1_HIPM_UL2016_MiniAODv2-v1_nano_data_UL20_private_v1-db7e530214851c2df75d13ca5dc648d7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
DoubleEG_Run2016Bver2_preVFP       = Sample.nanoAODfromDAS("DoubleEG_Run2016Bver2_preVFP", "/DoubleEG/schoef-crab_Run2016B-ver2_HIPM_UL2016_MiniAODv2-v3_nano_data_UL20_private_v1-db7e530214851c2df75d13ca5dc648d7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
DoubleEG_Run2016C_preVFP           = Sample.nanoAODfromDAS("DoubleEG_Run2016C_preVFP"    , "/DoubleEG/schoef-crab_Run2016C-HIPM_UL2016_MiniAODv2-v1_nano_data_UL20_private_v1-db7e530214851c2df75d13ca5dc648d7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
DoubleEG_Run2016D_preVFP           = Sample.nanoAODfromDAS("DoubleEG_Run2016D_preVFP"    , "/DoubleEG/schoef-crab_Run2016D-HIPM_UL2016_MiniAODv2-v1_nano_data_UL20_private_v1-db7e530214851c2df75d13ca5dc648d7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
DoubleEG_Run2016E_preVFP           = Sample.nanoAODfromDAS("DoubleEG_Run2016E_preVFP"    , "/DoubleEG/schoef-crab_Run2016E-HIPM_UL2016_MiniAODv2-v1_nano_data_UL20_private_v1-db7e530214851c2df75d13ca5dc648d7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
DoubleEG_Run2016F_preVFP           = Sample.nanoAODfromDAS("DoubleEG_Run2016F_preVFP"    , "/DoubleEG/schoef-crab_Run2016F-HIPM_UL2016_MiniAODv2-v1_nano_data_UL20_private_v1-db7e530214851c2df75d13ca5dc648d7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
DoubleEG_Run2016_preVFP = [DoubleEG_Run2016Bver1_preVFP, DoubleEG_Run2016Bver2_preVFP, DoubleEG_Run2016C_preVFP, DoubleEG_Run2016D_preVFP, DoubleEG_Run2016E_preVFP, DoubleEG_Run2016F_preVFP]

MuonEG_Run2016Bver1_preVFP         = Sample.nanoAODfromDAS("MuonEG_Run2016Bver1_preVFP", "/MuonEG/schoef-crab_Run2016B-ver1_HIPM_UL2016_MiniAODv2-v2_nano_data_UL20_private_v1-db7e530214851c2df75d13ca5dc648d7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
MuonEG_Run2016Bver2_preVFP         = Sample.nanoAODfromDAS("MuonEG_Run2016Bver2_preVFP", "/MuonEG/schoef-crab_Run2016B-ver2_HIPM_UL2016_MiniAODv2-v2_nano_data_UL20_private_v1-db7e530214851c2df75d13ca5dc648d7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
MuonEG_Run2016C_preVFP             = Sample.nanoAODfromDAS("MuonEG_Run2016C_preVFP"    , "/MuonEG/schoef-crab_Run2016C-HIPM_UL2016_MiniAODv2-v2_nano_data_UL20_private_v1-db7e530214851c2df75d13ca5dc648d7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
MuonEG_Run2016D_preVFP             = Sample.nanoAODfromDAS("MuonEG_Run2016D_preVFP"    , "/MuonEG/schoef-crab_Run2016D-HIPM_UL2016_MiniAODv2-v2_nano_data_UL20_private_v1-db7e530214851c2df75d13ca5dc648d7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
MuonEG_Run2016E_preVFP             = Sample.nanoAODfromDAS("MuonEG_Run2016E_preVFP"    , "/MuonEG/schoef-crab_Run2016E-HIPM_UL2016_MiniAODv2-v2_nano_data_UL20_private_v1-db7e530214851c2df75d13ca5dc648d7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
MuonEG_Run2016F_preVFP             = Sample.nanoAODfromDAS("MuonEG_Run2016F_preVFP"    , "/MuonEG/schoef-crab_Run2016F-HIPM_UL2016_MiniAODv2-v2_nano_data_UL20_private_v1-db7e530214851c2df75d13ca5dc648d7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
MuonEG_Run2016_preVFP = [MuonEG_Run2016Bver1_preVFP, MuonEG_Run2016Bver2_preVFP, MuonEG_Run2016C_preVFP, MuonEG_Run2016D_preVFP, MuonEG_Run2016E_preVFP, MuonEG_Run2016F_preVFP]

allSamples = SingleMuon_Run2016_preVFP + SingleElectron_Run2016_preVFP + DoubleMuon_Run2016_preVFP + DoubleEG_Run2016_preVFP + MuonEG_Run2016_preVFP

for s in allSamples:
    s.isData = False

from Samples.Tools.AutoClass import AutoClass
samples = AutoClass( allSamples )
if __name__=="__main__":
    if options.check_completeness:
        samples.check_completeness( cores=20 )
