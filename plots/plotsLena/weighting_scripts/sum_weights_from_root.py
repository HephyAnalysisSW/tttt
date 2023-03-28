#!/usr/bin/env python

# General
import os, sys
import ROOT

# Analysis
#import Analysis.Tools.syncer
# RootTools
from RootTools.core.standard import *

from tttt.Tools.helpers import getVarValue, getObjDict

# MVA configuration
import tttt.MVA.configs  as configs

import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel', action='store', nargs='?',  choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'],   default='INFO', help="Log level for logging" )
argParser.add_argument('--sample',                    action='store', type=str)
argParser.add_argument('--config',                    action='store', type=str)
argParser.add_argument('--output_directory',          action='store', type=str,   default='.')

args = argParser.parse_args()

#Logger
import tttt.Tools.logger as logger
logger = logger.get_logger(args.logLevel, logFile = None )
import Analysis.Tools.logger as logger_an
logger_an = logger_an.get_logger(args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None )
import numpy as np


#config
config = getattr( configs, args.config)

sample_names = []
found = False
for sample in config.weightsum_samples:
    if args.sample == sample.name:
        found = True
        break # found it
    else:
        sample_names.append( sample.name )
      
if not found:
    logger.error( "Need sample to be one of %s, got %s", ",".join( sample_names ), args.sample )
    sys.exit()

logger.info( "Processing sample weights in %s", sample.name )

count  = int(sample.getYieldFromDraw( weightString="(1)" )["val"])
logger.info( "Found %i weights for sample %s", count, sample.name )

# where the output goes
output_file  = os.path.join( args.output_directory, "MVA-training", sample.name, sample.name + "_weightsum.root" )

#filler
weightsum = []
def filler( event, sample ):
    weightsum.append(event.genWeight_sum)
 
def maker_sum( event, weightsum ):
    event.total_genWeight = np.sum(weightsum)
    logger.info("Sum over all event.genWeights in sample %s is %s", sample.name, event.total_genWeight)

# reader
reader = sample.treeReader( \
    variables =  ['genWeight_sum/F'],
    sequence  = [ filler ],
    )
    
reader.start()

# scalar variable
weight_variable = ["total_genWeight/F"]

tmp_dir     = ROOT.gDirectory

dirname = os.path.dirname(output_file)
if not os.path.exists(dirname):
    os.makedirs(dirname)

outputfile = ROOT.TFile.Open(output_file, 'recreate')
outputfile.cd()

maker = TreeMaker(
    variables = map(lambda v: TreeVariable.fromString(v) if type(v)==type("") else v, weight_variable),
    treeName = "Events"
    )

tmp_dir.cd()

maker.start()

logger.info( "Starting event loop" )
counter=0
while reader.run():
    counter += 1
    if counter%10000 == 0:
        logger.info("Written %i events.", counter)


maker_sum( maker.event, weightsum )
maker.fill()
maker.event.init()
maker.tree.Write()
outputfile.Close()
logger.info( "Written %s", output_file)

maker.clear()
logger.info( "Written sum of all event weights to %s", output_file )
