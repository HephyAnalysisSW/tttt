#!/usr/bin/env python
import os
import ROOT
import argparse
import Analysis.Tools.helpers as helpers

#Logger
import tttt.Tools.logger as logger
logger = logger.get_logger("INFO", logFile = None )

argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel', action='store', nargs='?',  choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'],   default='INFO', help="Log level for logging" )
argParser.add_argument('--files',                     action='store', nargs='*')
argParser.add_argument('--rebin',                     action='store', type=int, required=True)
argParser.add_argument('--outdir',                    action='store', type=str,   default=None)

args = argParser.parse_args()

for filename in args.files:
    if not filename.endswith('.root'):
        logger.warning( "Not a root file: %s"%filename)

    logger.info( "At file %s"%filename )

    gDir = ROOT.gDirectory.GetName()
    f = ROOT.TFile.Open( filename )
    keys   = f.GetListOfKeys()
    names = [keys.At(i_key).GetName() for i_key in range(keys.GetSize())]
    f.Close()
    ROOT.gDirectory.cd(gDir+':/')
 
    if args.outdir == None:
        outdir = os.path.dirname(filename)+'_rebin%i'%args.rebin
    else:
        outdir = args.outdir

    outfile = os.path.join( outdir, os.path.basename( filename ))

    if not os.path.exists(outdir):
        os.makedirs( outdir )

    for t in names:
        h = helpers.getObjFromFile( filename, t)
        try:
            h.Rebin(args.rebin)
        except AssertionError:
            continue
        helpers.writeObjToFile( outfile, h, update=True)

    logger.info ("Done with file %s", outfile)
