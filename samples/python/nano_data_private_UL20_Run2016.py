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

SingleMuon_Run2016F         = Sample.nanoAODfromDAS("SingleMuon_Run2016F"    , "/SingleMuon/schoef-crab_Run2016F-UL2016_MiniAODv2-v2_nano_data_UL20_private_v1-a8784177d661a0be9ee687bb7d14546f/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
SingleMuon_Run2016G         = Sample.nanoAODfromDAS("SingleMuon_Run2016G"    , "/SingleMuon/schoef-crab_Run2016G-UL2016_MiniAODv2-v2_nano_data_UL20_private_v1-a8784177d661a0be9ee687bb7d14546f/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
SingleMuon_Run2016H         = Sample.nanoAODfromDAS("SingleMuon_Run2016H"    , "/SingleMuon/schoef-crab_Run2016H-UL2016_MiniAODv2-v2_nano_data_UL20_private_v1-a8784177d661a0be9ee687bb7d14546f/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
SingleMuon_Run2016 = [SingleMuon_Run2016F, SingleMuon_Run2016G, SingleMuon_Run2016H]

SingleElectron_Run2016F     = Sample.nanoAODfromDAS("SingleElectron_Run2016F", "/SingleElectron/schoef-crab_Run2016F-UL2016_MiniAODv2-v2_nano_data_UL20_private_v1-a8784177d661a0be9ee687bb7d14546f/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
SingleElectron_Run2016G     = Sample.nanoAODfromDAS("SingleElectron_Run2016G", "/SingleElectron/schoef-crab_Run2016G-UL2016_MiniAODv2-v2_nano_data_UL20_private_v1-a8784177d661a0be9ee687bb7d14546f/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
SingleElectron_Run2016H     = Sample.nanoAODfromDAS("SingleElectron_Run2016H", "/SingleElectron/schoef-crab_Run2016H-UL2016_MiniAODv2-v2_nano_data_UL20_private_v1-a8784177d661a0be9ee687bb7d14546f/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
SingleElectron_Run2016 = [ SingleElectron_Run2016F, SingleElectron_Run2016G, SingleElectron_Run2016H] 

DoubleMuon_Run2016F         = Sample.nanoAODfromDAS("DoubleMuon_Run2016F"    , "/DoubleMuon/schoef-crab_Run2016F-UL2016_MiniAODv2-v1_nano_data_UL20_private_v1-a8784177d661a0be9ee687bb7d14546f/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
DoubleMuon_Run2016G         = Sample.nanoAODfromDAS("DoubleMuon_Run2016G"    , "/DoubleMuon/schoef-crab_Run2016G-UL2016_MiniAODv2-v1_nano_data_UL20_private_v1-a8784177d661a0be9ee687bb7d14546f/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
DoubleMuon_Run2016H         = Sample.nanoAODfromDAS("DoubleMuon_Run2016H"    , "/DoubleMuon/schoef-crab_Run2016H-UL2016_MiniAODv2-v2_nano_data_UL20_private_v1-a8784177d661a0be9ee687bb7d14546f/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
DoubleMuon_Run2016 = [DoubleMuon_Run2016F, DoubleMuon_Run2016G, DoubleMuon_Run2016H]

DoubleEG_Run2016F           = Sample.nanoAODfromDAS("DoubleEG_Run2016F"      , "/DoubleEG/schoef-crab_Run2016F-UL2016_MiniAODv2-v1_nano_data_UL20_private_v1-a8784177d661a0be9ee687bb7d14546f/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
DoubleEG_Run2016G           = Sample.nanoAODfromDAS("DoubleEG_Run2016G"      , "/DoubleEG/schoef-crab_Run2016G-UL2016_MiniAODv2-v1_nano_data_UL20_private_v1-a8784177d661a0be9ee687bb7d14546f/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
DoubleEG_Run2016H           = Sample.nanoAODfromDAS("DoubleEG_Run2016H"      , "/DoubleEG/schoef-crab_Run2016H-UL2016_MiniAODv2-v1_nano_data_UL20_private_v1-a8784177d661a0be9ee687bb7d14546f/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
DoubleEG_Run2016 = [DoubleEG_Run2016F, DoubleEG_Run2016G, DoubleEG_Run2016H]

MuonEG_Run2016F             = Sample.nanoAODfromDAS("MuonEG_Run2016F"        , "/MuonEG/schoef-crab_Run2016F-UL2016_MiniAODv2-v2_nano_data_UL20_private_v1-a8784177d661a0be9ee687bb7d14546f/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
MuonEG_Run2016G             = Sample.nanoAODfromDAS("MuonEG_Run2016G"        , "/MuonEG/schoef-crab_Run2016G-UL2016_MiniAODv2-v2_nano_data_UL20_private_v1-a8784177d661a0be9ee687bb7d14546f/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
MuonEG_Run2016H             = Sample.nanoAODfromDAS("MuonEG_Run2016H"        , "/MuonEG/schoef-crab_Run2016H-UL2016_MiniAODv2-v2_nano_data_UL20_private_v1-a8784177d661a0be9ee687bb7d14546f/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
MuonEG_Run2016 = [MuonEG_Run2016F, MuonEG_Run2016G, MuonEG_Run2016H]

allSamples = SingleMuon_Run2016 + SingleElectron_Run2016 + DoubleMuon_Run2016 + DoubleEG_Run2016 + MuonEG_Run2016

for s in allSamples:
    s.isData = False

from Samples.Tools.AutoClass import AutoClass
samples = AutoClass( allSamples )
if __name__=="__main__":
    if options.check_completeness:
        samples.check_completeness( cores=20 )
