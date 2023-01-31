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
argParser.add_argument('--sample',             action='store', type=str)
argParser.add_argument('--config',             action='store', type=str)
argParser.add_argument('--selection',          action='store', type=str, default=None,  help="Additional training selection?")
argParser.add_argument('--output_directory',   action='store', type=str,   default='.')
argParser.add_argument('--small',              action='store_true')

args = argParser.parse_args()

#Logger
import tttt.Tools.logger as logger
logger = logger.get_logger(args.logLevel, logFile = None )
import Analysis.Tools.logger as logger_an
logger_an = logger_an.get_logger(args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None )

subDir = args.config

#config
config = getattr(configs, args.config)

sample_names = []
found = False
for sample in config.training_samples:
    if args.sample == sample.name:
        found = True
        break # found it
    else:
        sample_names.append( sample.name )

if not found:
    logger.error( "Need sample to be one of %s, got %s", ",".join( sample_names ), args.sample )
    sys.exit()

logger.info( "Processing sample %s", sample.name )

count  = int(sample.getYieldFromDraw( weightString="(1)" )["val"])
logger.info( "Found %i events for sample %s", count, sample.name )

if args.small:
    sample.reduceFiles(to=1)
    subDir += '_small'

if args.selection is not None:
    from tttt.Tools.delphesCutInterpreter import cutInterpreter
    custom_sel = cutInterpreter.cutString( args.selection)
    sample.addSelectionString( custom_sel )
    logger.info( "Add selectionstring %s", custom_sel )
    subDir += "_"+args.selection
elif hasattr( config, "selectionString"):
    sample.addSelectionString( config.selectionString )
    logger.info( "Add selectionstring %s", config.selectionString )
    subDir += "_"+config.selection
else:
    logger.info( "Do not use selectionstring" )

# where the output goes
output_file  = os.path.join( args.output_directory, "MVA-training", subDir, sample.name, sample.name + ".root" )

# reader
reader = sample.treeReader( \
    #variables = map( TreeVariable.fromString, config.read_variables),
    variables =  config.read_variables,
    sequence  = config.sequence,
    )
reader.start()

def fill_vector_collection( event, collection_name, collection_varnames, objects, maxN = 100):
    setattr( event, "n"+collection_name, len(objects) )
    for i_obj, obj in enumerate(objects[:maxN]):
        for var in collection_varnames:
            if var in obj.keys():
                if type(obj[var]) == type("string"):
                    obj[var] = int(ord(obj[var]))
                if type(obj[var]) == type(True):
                    obj[var] = int(obj[var])
                getattr(event, collection_name+"_"+var)[i_obj] = obj[var]

#filler
def filler( event ):

    r = reader.event

    # copy scalar variables
    for name, func in config.all_mva_variables.iteritems():
        setattr( event, name, func(r, sample=None) )

    # copy vector variables
    for name, vector_var in config.mva_vector_variables.iteritems():
        objs = vector_var["func"]( r, sample=None )

        fill_vector_collection( event, name, vector_var['varnames'], objs )

    # fill FIs
    if hasattr(config, "FIs"):
        for FI_name, FI in config.FIs.iteritems():
            #print( event, 'mva_'+FI_name, FI['func']( [r.p_C[i] for i in range(r.np) ] ) )
            setattr( event, 'FI_'+FI_name, FI['func']( [r.p_C[i] for i in range(r.np) ] )[1][0][0] )

# Create a maker. Maker class will be compiled.

# scalar variables
mva_variables = ["%s/F"%var for var in config.all_mva_variables.keys()]

# vector variables, if any
for name, vector_var in config.mva_vector_variables.iteritems():
    #mva_variables.append( VectorTreeVariable.fromString(name+'['+','.join(vector_var['vars'])+']') )
    mva_variables.append( name+'['+','.join(vector_var['vars'])+']' )
# FIs
if hasattr( config, "FIs"):
    FI_variables = ["FI_%s/F"%var for var in config.FIs.keys() ]
else:
    FI_variables = []

tmp_dir     = ROOT.gDirectory

dirname = os.path.dirname(output_file)
if not os.path.exists(dirname):
    os.makedirs(dirname)

outputfile = ROOT.TFile.Open(output_file, 'recreate')

outputfile.cd()
maker = TreeMaker(
    sequence  = [ filler ],
    variables = map(TreeVariable.fromString,
          mva_variables+FI_variables,
        ),
    treeName = "Events"
    )

tmp_dir.cd()

maker.start()

logger.info( "Starting event loop" )
counter=0
while reader.run():

    maker.run()
    counter += 1
    if counter%10000 == 0:
        logger.info("Written %i events.", counter)

nEventsTotal = maker.tree.GetEntries()

maker.tree.Write()
outputfile.Close()
logger.info( "Written %s", output_file)
#
#      # Destroy the TTree
maker.clear()
logger.info( "Written %i events to %s",  nEventsTotal, output_file )
