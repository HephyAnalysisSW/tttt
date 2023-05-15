#!/usr/bin/env python
''' Copy a directory and apply extra selection 
'''
#
# Standard imports and batch mode
#
import ROOT
import glob
import os

# RootTools
from RootTools.core.standard             import *

from tttt.Tools.cutInterpreter           import cutInterpreter

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',       action='store',      default='INFO', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
#argParser.add_argument('--small',                             action='store_true', help='Run only on a small subset of the data?')
argParser.add_argument('--overwrite',      action='store_true', help='Overwrite?')
argParser.add_argument('--source',         action='store', default='/scratch-cbe/users/maryam.shooshtari/tttt/nanoTuples/tttt_v7/UL2016/dilep-ht500/')
argParser.add_argument('--target',         action='store', default='/scratch-cbe/users/robert.schoefbeck/tttt/nanoTuples/tttt_v7/UL2016/')
argParser.add_argument('--target_subdir',  action='store', default=None, help='If specified, will write to "target/target_subdir" instead if "target/source_subdir-selection".')
argParser.add_argument('--selection',      action='store', default='ht1000')
argParser.add_argument('--sample',         action='store', default=None, help='Specify sample subdir after args.target_subdir')
args = argParser.parse_args()

# Logger
import TMB.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)


if args.target_subdir is not None:
    target = os.path.join( args.target, args.target_subdir, args.sample )
else:
    target = os.path.join( args.target, os.path.dirname(args.source).split('/')[-1]+'-'+args.selection, args.sample) 

for i_entry, entry in enumerate( os.listdir(args.source) ):
    sample_dir = os.path.join(args.source, entry)
    if os.path.isdir(sample_dir):
        sample = Sample.fromDirectory( "s%i"%i_entry, directory = sample_dir )
        #print(sample.name, len(sample.files))
        if entry == args.sample:
            sample.copy_files( target, selection=cutInterpreter.cutString(args.selection))#, overwrite=args.overwrite)

