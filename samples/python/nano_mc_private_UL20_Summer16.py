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

TTLep_pow_CP5 = Sample.nanoAODfromDAS("TTLep_pow_CP5", "/TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8/schoef-crab_RunIISummer20UL16MiniAODv2-106X_mcRun2_asymptotic_v17-v1_nano_mc_UL20_private_v1-987345b702a321dad0facc826a267125/USER", dbFile=dbFile, redirector=redirector, instance="phys03", overwrite=ov, xSection=831.762*((3*0.108)**2))

allSamples = [ TTLep_pow_CP5 ]

for s in allSamples:
    s.isData = False

from Samples.Tools.AutoClass import AutoClass
samples = AutoClass( allSamples )
if __name__=="__main__":
    if options.check_completeness:
        samples.check_completeness( cores=20 )
