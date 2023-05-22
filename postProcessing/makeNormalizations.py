#!/usr/bin/env python

# Standard imports
import ROOT
import os

import tttt.Tools.user as user

def get_parser():
    ''' Argument parser for post-processing module.
    '''
    import argparse
    argParser = argparse.ArgumentParser(description = "Argument parser for cmgPostProcessing")

    argParser.add_argument('--logLevel',    action='store',        nargs='?',  choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'],   default='INFO', help="Log level for logging" )
    argParser.add_argument('--DAS',         action='store',        nargs='?',  type=str, default=None,   help="DAS name" )
    argParser.add_argument('--sampleFile',  action='store',        nargs='?',  type=str, default=None,   help="E.g. Samples.nanoAOD.UL16_nanoAODv9" )
    argParser.add_argument('--small',       action='store_true',                                         help="Run the file on a small sample (for test purpose), bool flag set to True if used" )
    argParser.add_argument('--vector',      action='store',        nargs='?',  type=str, default=None,   help="Which vector shall we add up?" )
    argParser.add_argument('--len',         action='store',        nargs='?',  type=int, default=-1,     help="What is the length?" )
    argParser.add_argument('--overwrite',   action='store_true',   help="Overwrite?" )
    return argParser

args = get_parser().parse_args()

# dirDB
from Analysis.Tools.DirDB import DirDB
dirDB = DirDB(os.path.join( user.cache_dir, 'normalizationCache'))

if args.sampleFile is not None:
    exec( "from %s import allSamples as samples"%args.sampleFile )
    with open( "makeNormalizations.sh", 'w' if not os.path.exists("makeNormalizations.sh") else "a" ) as f:
        for sample in samples:
            f.write("python makeNormalizations.py --DAS %s %s --vector LHEPdfWeight --len 101\n"%(sample.DAS, '--overwrite' if args.overwrite else ''))
            f.write("python makeNormalizations.py --DAS %s %s --vector PSWeight --len 4\n"      %(sample.DAS, '--overwrite' if args.overwrite else ''))
            f.write("python makeNormalizations.py --DAS %s %s --vector LHEScaleWeight --len 9\n"%(sample.DAS, '--overwrite' if args.overwrite else ''))
        f.write("\n")

    print ("Job commands added to makeNormalizations.sh")

# Logging
import tttt.Tools.logger as _logger
logger  = _logger.get_logger(args.logLevel)
import RootTools.core.logger as _logger_rt
logger_rt = _logger_rt.get_logger(args.logLevel)

