#vector<reco::GenJet>                  "slimmedGenJets"            ""                "PAT"
#vector<reco::GenJet>                  "slimmedGenJetsAK8"         ""                "PAT"
#vector<reco::GenJet>                  "slimmedGenJetsAK8SoftDropSubJets"   ""                "PAT"
#These are all the GenJet collections in the miniAOD
import copy, os, sys
from RootTools.core.standard import *
import ROOT

def get_parser():
    import argparse
    argParser = argparse.ArgumentParser(description = "Argument parser for samples file")
    argParser.add_argument('--logLevel',    action='store', nargs='?',  choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'],  default='INFO', help="Log level for logging")
    argParser.add_argument('--overwrite',   action='store_true',    help="Overwrite current entry in db?")
    argParser.add_argument('--update',      action='store_true',    help="Update current entry in db?")
    argParser.add_argument('--check_completeness', action='store_true',    help="Check competeness?")
    return argParser

# Logging
if __name__=="__main__":
    args = get_parser().parse_args()
    ov = args.overwrite
    if args.update:
        ov = 'update'
    import Samples.Tools.logger as logger
    logger = logger.get_logger(args.logLevel, logFile = None )
    import RootTools.core.logger as logger_rt
    logger_rt = logger_rt.get_logger(args.logLevel, logFile = None )
else:
    import logging
    logger = logging.getLogger(__name__)
    ov = False

from Samples.Tools.config import  redirector_global
redirector = redirector_global

## DB
from Samples.Tools.config import dbDir
dbFile = dbDir+'/genValidation_AOD.sql'
logger.info("Using db file: %s", dbFile)

#TTTT  = FWLiteSample.fromFiles("TTTT", ["root://cms-xrd-global.cern.ch//store/mc/RunIIAutumn18MiniAOD/TTTT_TuneCP5_13TeV-amcatnlo-pythia8/MINIAODSIM/102X_upgrade2018_realistic_v15_ext1-v2/00000/06ACB6E4-D278-F04F-ABB7-DDF6415C6831.root"])


TTTT = FWLiteSample.fromDAS("TTTT", "/TTTT_TuneCP5_13TeV-amcatnlo-pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15_ext1-v2/MINIAODSIM", prefix=redirector, dbFile=dbFile, overwrite=ov, skipCheck=True)
