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

SingleMuon_Run2017B = Sample.nanoAODfromDAS("SingleMuon_Run2017B", "/SingleMuon/schoef-crab_Run2017B-UL2017_MiniAODv2-v1_nano_data_UL20_private_v1-fae10e0fddc662898f8c13128282e7e7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
SingleMuon_Run2017C = Sample.nanoAODfromDAS("SingleMuon_Run2017C", "/SingleMuon/schoef-crab_Run2017C-UL2017_MiniAODv2-v1_nano_data_UL20_private_v1-fae10e0fddc662898f8c13128282e7e7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
SingleMuon_Run2017D = Sample.nanoAODfromDAS("SingleMuon_Run2017D", "/SingleMuon/schoef-crab_Run2017D-UL2017_MiniAODv2-v1_nano_data_UL20_private_v1-fae10e0fddc662898f8c13128282e7e7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
SingleMuon_Run2017E = Sample.nanoAODfromDAS("SingleMuon_Run2017E", "/SingleMuon/schoef-crab_Run2017E-UL2017_MiniAODv2-v1_nano_data_UL20_private_v1-fae10e0fddc662898f8c13128282e7e7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
SingleMuon_Run2017F = Sample.nanoAODfromDAS("SingleMuon_Run2017F", "/SingleMuon/schoef-crab_Run2017F-UL2017_MiniAODv2-v1_nano_data_UL20_private_v1-fae10e0fddc662898f8c13128282e7e7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)

SingleMuon_Run2017 = [SingleMuon_Run2017B, SingleMuon_Run2017C, SingleMuon_Run2017D, SingleMuon_Run2017E, SingleMuon_Run2017F]

SingleElectron_Run2017B = Sample.nanoAODfromDAS("SingleElectron_Run2017B", "/SingleElectron/schoef-crab_Run2017B-UL2017_MiniAODv2-v1_nano_data_UL20_private_v1-fae10e0fddc662898f8c13128282e7e7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
SingleElectron_Run2017C = Sample.nanoAODfromDAS("SingleElectron_Run2017C", "/SingleElectron/schoef-crab_Run2017C-UL2017_MiniAODv2-v1_nano_data_UL20_private_v1-fae10e0fddc662898f8c13128282e7e7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
SingleElectron_Run2017D = Sample.nanoAODfromDAS("SingleElectron_Run2017D", "/SingleElectron/schoef-crab_Run2017D-UL2017_MiniAODv2-v1_nano_data_UL20_private_v1-fae10e0fddc662898f8c13128282e7e7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
SingleElectron_Run2017E = Sample.nanoAODfromDAS("SingleElectron_Run2017E", "/SingleElectron/schoef-crab_Run2017E-UL2017_MiniAODv2-v1_nano_data_UL20_private_v1-fae10e0fddc662898f8c13128282e7e7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
SingleElectron_Run2017F = Sample.nanoAODfromDAS("SingleElectron_Run2017F", "/SingleElectron/schoef-crab_Run2017F-UL2017_MiniAODv2-v1_nano_data_UL20_private_v1-fae10e0fddc662898f8c13128282e7e7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
SingleElectron_Run2017 = [SingleElectron_Run2017B, SingleElectron_Run2017C, SingleElectron_Run2017D, SingleElectron_Run2017E, SingleElectron_Run2017F]

DoubleMuon_Run2017B = Sample.nanoAODfromDAS("DoubleMuon_Run2017B", "/DoubleMuon/schoef-crab_Run2017B-UL2017_MiniAODv2-v1_nano_data_UL20_private_v1-fae10e0fddc662898f8c13128282e7e7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
DoubleMuon_Run2017C = Sample.nanoAODfromDAS("DoubleMuon_Run2017C", "/DoubleMuon/schoef-crab_Run2017C-UL2017_MiniAODv2-v1_nano_data_UL20_private_v1-fae10e0fddc662898f8c13128282e7e7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
DoubleMuon_Run2017D = Sample.nanoAODfromDAS("DoubleMuon_Run2017D", "/DoubleMuon/schoef-crab_Run2017D-UL2017_MiniAODv2-v1_nano_data_UL20_private_v1-fae10e0fddc662898f8c13128282e7e7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
DoubleMuon_Run2017E = Sample.nanoAODfromDAS("DoubleMuon_Run2017E", "/DoubleMuon/schoef-crab_Run2017E-UL2017_MiniAODv2-v2_nano_data_UL20_private_v1-fae10e0fddc662898f8c13128282e7e7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
DoubleMuon_Run2017F = Sample.nanoAODfromDAS("DoubleMuon_Run2017F", "/DoubleMuon/schoef-crab_Run2017F-UL2017_MiniAODv2-v1_nano_data_UL20_private_v1-fae10e0fddc662898f8c13128282e7e7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
DoubleMuon_Run2017 = [DoubleMuon_Run2017B, DoubleMuon_Run2017C, DoubleMuon_Run2017D, DoubleMuon_Run2017E, DoubleMuon_Run2017F]

DoubleEG_Run2017B = Sample.nanoAODfromDAS("DoubleEG_Run2017B", "/DoubleEG/schoef-crab_Run2017B-UL2017_MiniAODv2-v1_nano_data_UL20_private_v1-fae10e0fddc662898f8c13128282e7e7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
DoubleEG_Run2017C = Sample.nanoAODfromDAS("DoubleEG_Run2017C", "/DoubleEG/schoef-crab_Run2017C-UL2017_MiniAODv2-v2_nano_data_UL20_private_v1-fae10e0fddc662898f8c13128282e7e7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
DoubleEG_Run2017D = Sample.nanoAODfromDAS("DoubleEG_Run2017D", "/DoubleEG/schoef-crab_Run2017D-UL2017_MiniAODv2-v1_nano_data_UL20_private_v1-fae10e0fddc662898f8c13128282e7e7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
DoubleEG_Run2017E = Sample.nanoAODfromDAS("DoubleEG_Run2017E", "/DoubleEG/schoef-crab_Run2017E-UL2017_MiniAODv2-v1_nano_data_UL20_private_v1-fae10e0fddc662898f8c13128282e7e7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
DoubleEG_Run2017F = Sample.nanoAODfromDAS("DoubleEG_Run2017F", "/DoubleEG/schoef-crab_Run2017F-UL2017_MiniAODv2-v2_nano_data_UL20_private_v1-fae10e0fddc662898f8c13128282e7e7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
DoubleEG_Run2017 = [DoubleEG_Run2017B, DoubleEG_Run2017C, DoubleEG_Run2017D, DoubleEG_Run2017E, DoubleEG_Run2017F]

MuonEG_Run2017B = Sample.nanoAODfromDAS("MuonEG_Run2017B", "/MuonEG/schoef-crab_Run2017B-UL2017_MiniAODv2-v1_nano_data_UL20_private_v1-fae10e0fddc662898f8c13128282e7e7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
MuonEG_Run2017C = Sample.nanoAODfromDAS("MuonEG_Run2017C", "/MuonEG/schoef-crab_Run2017C-UL2017_MiniAODv2-v1_nano_data_UL20_private_v1-fae10e0fddc662898f8c13128282e7e7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
MuonEG_Run2017D = Sample.nanoAODfromDAS("MuonEG_Run2017D", "/MuonEG/schoef-crab_Run2017D-UL2017_MiniAODv2-v1_nano_data_UL20_private_v1-fae10e0fddc662898f8c13128282e7e7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
MuonEG_Run2017E = Sample.nanoAODfromDAS("MuonEG_Run2017E", "/MuonEG/schoef-crab_Run2017E-UL2017_MiniAODv2-v1_nano_data_UL20_private_v1-fae10e0fddc662898f8c13128282e7e7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
MuonEG_Run2017F = Sample.nanoAODfromDAS("MuonEG_Run2017F", "/MuonEG/schoef-crab_Run2017F-UL2017_MiniAODv2-v1_nano_data_UL20_private_v1-fae10e0fddc662898f8c13128282e7e7/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
MuonEG_Run2017 = [MuonEG_Run2017B, MuonEG_Run2017C, MuonEG_Run2017D, MuonEG_Run2017E, MuonEG_Run2017F]

allSamples = SingleMuon_Run2017 + SingleElectron_Run2017 + DoubleMuon_Run2017 + DoubleEG_Run2017 + MuonEG_Run2017

for s in allSamples:
    s.isData = True
    s.json = os.path.expandvars("$CMSSW_BASE/src/Samples/Tools/data/json/Cert_294927-306462_13TeV_UL2017_Collisions17_GoldenJSON.txt")

from Samples.Tools.AutoClass import AutoClass
samples = AutoClass( allSamples )
if __name__=="__main__":
    if options.check_completeness:
        samples.check_completeness( cores=20 )
