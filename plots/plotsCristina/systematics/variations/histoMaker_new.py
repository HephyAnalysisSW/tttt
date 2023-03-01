# General imports
import os
import ROOT
from array import array

# tttt imports
from tttt.Tools.cutInterpreter import cutInterpreter
import tttt.Tools.user as user



def get_parser():
    ''' Argument parser for post-processing module.
    '''
    import argparse
    argParser = argparse.ArgumentParser(description = "Argument parser for cmgPostProcessing")
    argParser.add_argument('--small',                             action='store_true', help='Run only on a small subset of the data?')
    argParser.add_argument('--targetDir',   action='store',         nargs='?',  type=str, default=user.postprocessing_output_directory, help="Name of the directory the post-processed files will be saved" )
    argParser.add_argument('--era',        action='store',                      type=str,                                               help="Which era?" )
    #argParser.add_argument('--getJEC',      action='store',                     type=str, default=True,                                 help="Get the JEC for plotting")
    # argParser.add_argument('--getJER',      action='store',                     type=str, default=True,                                 help="Get the JER for plotting")
    # argParser.add_argument('--getJES',      action='store',                     type=str, default=True,                                 help="Get the JES for plotting")

    return argParser

options = get_parser().parse_args()


from tttt.samples.nano_private_UL20_RunII_postProcessed_dilep import *

samples = [TTLep, TTLepbb, TTbb, ST, TTTT, TTW, TTZ, TTH]

if options.small:
    for sample in samples :
        sample.normalization = 1.
        sample.reduceFiles( to = 1 )
        sample.scale /= sample.normalization

input_directory = "/scratch-cbe/users/cristina.giordano/tttt/nanoTuples/tttt_v6"

if options.era not in [ 'UL2016', 'UL2016_preVFP', 'UL2017', 'UL2018' ]:
    raise Exception("Era %s not known"%options.era)
if "UL2016" == options.era:
    year = 2016
elif "UL2016_preVFP" == options.era:
    year = 2016
elif "UL2017" == options.era:
    year = 2017
elif "UL2018" == options.era:
    year = 2018
