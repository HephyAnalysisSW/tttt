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

SingleMuon_Run2018A = Sample.nanoAODfromDAS("SingleMuon_Run2018A", "/SingleMuon/schoef-crab_Run2018A-UL2018_MiniAODv2-v3_nano_data_UL20_private_v1-0bf6294e252c33eca4e4a21d6858e8c4/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
SingleMuon_Run2018B = Sample.nanoAODfromDAS("SingleMuon_Run2018B", "/SingleMuon/schoef-crab_Run2018B-UL2018_MiniAODv2-v2_nano_data_UL20_private_v1-0bf6294e252c33eca4e4a21d6858e8c4/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
SingleMuon_Run2018C = Sample.nanoAODfromDAS("SingleMuon_Run2018C", "/SingleMuon/schoef-crab_Run2018C-UL2018_MiniAODv2-v2_nano_data_UL20_private_v1-0bf6294e252c33eca4e4a21d6858e8c4/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
SingleMuon_Run2018D = Sample.nanoAODfromDAS("SingleMuon_Run2018D", "/SingleMuon/schoef-crab_Run2018D-UL2018_MiniAODv2-v3_nano_data_UL20_private_v1-0bf6294e252c33eca4e4a21d6858e8c4/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
SingleMuon_Run2018 = [SingleMuon_Run2018A, SingleMuon_Run2018B, SingleMuon_Run2018C, SingleMuon_Run2018D]

EGamma_Run2018A = Sample.nanoAODfromDAS("EGamma_Run2018A", "/EGamma/schoef-crab_Run2018A-UL2018_MiniAODv2-v1_nano_data_UL20_private_v1-0bf6294e252c33eca4e4a21d6858e8c4/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
EGamma_Run2018B = Sample.nanoAODfromDAS("EGamma_Run2018B", "/EGamma/schoef-crab_Run2018B-UL2018_MiniAODv2-v1_nano_data_UL20_private_v1-0bf6294e252c33eca4e4a21d6858e8c4/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
EGamma_Run2018C = Sample.nanoAODfromDAS("EGamma_Run2018C", "/EGamma/schoef-crab_Run2018C-UL2018_MiniAODv2-v1_nano_data_UL20_private_v1-0bf6294e252c33eca4e4a21d6858e8c4/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
EGamma_Run2018D = Sample.nanoAODfromDAS("EGamma_Run2018D", "/EGamma/schoef-crab_Run2018D-UL2018_MiniAODv2-v2_nano_data_UL20_private_v1-0bf6294e252c33eca4e4a21d6858e8c4/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
EGamma_Run2018 = [EGamma_Run2018A, EGamma_Run2018B, EGamma_Run2018C, EGamma_Run2018D]

DoubleMuon_Run2018A = Sample.nanoAODfromDAS("DoubleMuon_Run2018A", "/DoubleMuon/schoef-crab_Run2018A-UL2018_MiniAODv2-v1_nano_data_UL20_private_v1-0bf6294e252c33eca4e4a21d6858e8c4/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
DoubleMuon_Run2018B = Sample.nanoAODfromDAS("DoubleMuon_Run2018B", "/DoubleMuon/schoef-crab_Run2018B-UL2018_MiniAODv2-v1_nano_data_UL20_private_v1-0bf6294e252c33eca4e4a21d6858e8c4/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
DoubleMuon_Run2018C = Sample.nanoAODfromDAS("DoubleMuon_Run2018C", "/DoubleMuon/schoef-crab_Run2018C-UL2018_MiniAODv2-v1_nano_data_UL20_private_v1-0bf6294e252c33eca4e4a21d6858e8c4/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
DoubleMuon_Run2018D = Sample.nanoAODfromDAS("DoubleMuon_Run2018D", "/DoubleMuon/schoef-crab_Run2018D-UL2018_MiniAODv2-v1_nano_data_UL20_private_v1-0bf6294e252c33eca4e4a21d6858e8c4/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
DoubleMuon_Run2018 = [DoubleMuon_Run2018A, DoubleMuon_Run2018B, DoubleMuon_Run2018C, DoubleMuon_Run2018D]

MuonEG_Run2018A = Sample.nanoAODfromDAS("MuonEG_Run2018A", "/MuonEG/schoef-crab_Run2018A-UL2018_MiniAODv2-v1_nano_data_UL20_private_v1-0bf6294e252c33eca4e4a21d6858e8c4/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
MuonEG_Run2018B = Sample.nanoAODfromDAS("MuonEG_Run2018B", "/MuonEG/schoef-crab_Run2018B-UL2018_MiniAODv2-v1_nano_data_UL20_private_v1-0bf6294e252c33eca4e4a21d6858e8c4/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
MuonEG_Run2018C = Sample.nanoAODfromDAS("MuonEG_Run2018C", "/MuonEG/schoef-crab_Run2018C-UL2018_MiniAODv2-v1_nano_data_UL20_private_v1-0bf6294e252c33eca4e4a21d6858e8c4/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
MuonEG_Run2018D = Sample.nanoAODfromDAS("MuonEG_Run2018D", "/MuonEG/schoef-crab_Run2018D-UL2018_MiniAODv2-v1_nano_data_UL20_private_v1-0bf6294e252c33eca4e4a21d6858e8c4/USER", instance="phys03", dbFile=dbFile, overwrite=ov, redirector=redirector)
MuonEG_Run2018 = [MuonEG_Run2018A, MuonEG_Run2018B, MuonEG_Run2018C, MuonEG_Run2018D]

allSamples = SingleMuon_Run2018 + EGamma_Run2018 + DoubleMuon_Run2018 + MuonEG_Run2018

for s in allSamples:
    s.isData = True
    s.json = os.path.expandvars("$CMSSW_BASE/src/Samples/Tools/data/json/Cert_314472-325175_13TeV_Legacy2018_Collisions18_JSON.txt")

from Samples.Tools.AutoClass import AutoClass
samples = AutoClass( allSamples )
if __name__=="__main__":
    if options.check_completeness:
        samples.check_completeness( cores=20 )
