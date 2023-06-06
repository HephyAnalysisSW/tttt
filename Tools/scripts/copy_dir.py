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
from tttt.Tools.user                     import *
# Hello
# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',       action='store',      default='INFO', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
#argParser.add_argument('--small',                             action='store_true', help='Run only on a small subset of the data?')
argParser.add_argument('--overwrite',      action='store_true', help='Overwrite?')
argParser.add_argument('--source',         action='store', default='/scratch-cbe/users/maryam.shooshtari/tttt/nanoTuples/tttt_v7/UL2016/dilep/')
argParser.add_argument('--target',         action='store', default='/scratch-cbe/users/$USER/tttt/nanoTuples/tttt_v7/UL2016')
#argParser.add_argument('--version',        action='store', default='tttt_v7', help='which version to copy to?')
argParser.add_argument('--target_subdir',  action='store', default=None, help='If specified, will write to "target/target_subdir" instead if "target/source_subdir-selection".')
argParser.add_argument('--selection',      action='store', default='SS')
argParser.add_argument('--sampleSelection',        action='store',         nargs='*',  type=str, default=[],                  help="List of strings that must appear in samples to be processed (OR-ed)" )
argParser.add_argument('--cores',          action='store',         type=int, default=-1,                  help="How many jobs to parallelize?" )
args = argParser.parse_args()

# Logger
import tttt.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)


if args.target_subdir is not None:
    target = os.path.join( args.target, args.target_subdir)
else:
    target = os.path.join( args.target, os.path.dirname(args.source).split('/')[-1]+'-'+args.selection)
jobs = []
for i_entry, entry in enumerate( os.listdir(args.source) ):
    sample_dir = os.path.join(args.source, entry)
    if os.path.isdir(sample_dir):
        sample = Sample.fromDirectory( "s%i"%i_entry, directory = sample_dir )
        #print(sample.name, len(sample.files))
        #if entry == args.sample:
        found=True
        if len(args.sampleSelection)>0:
            found = False
            for selection in args.sampleSelection:
                if selection in sample_dir:
                    found = True
                    break
        if found:
            jobs.append( {'sample':sample, 'target':os.path.join(os.path.expandvars(target), entry), 'selection':cutInterpreter.cutString(args.selection), 'overwrite':args.overwrite} )

#import time
#def wrapper_function( job ):
#    print (job)
#    time.sleep(5)
def wrapper_function( job ):
    job['sample'].copy_files(target=job['target'], selection=job['selection'], overwrite=job['overwrite'])

if args.cores>0:
    from multiprocessing import Pool
    pool = Pool(processes=args.cores)
    results = pool.map(wrapper_function, jobs)
    pool.close()
else:
    for job in jobs:
        wrapper_function( job ) 
