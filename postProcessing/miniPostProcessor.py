# Standard imports
import os, sys
import ROOT
import itertools
from   Analysis.Tools.helpers import deltaR2, deltaPhi, checkRootFile
from math import pi

#RootTools
from RootTools.core.standard import *

# Tools
import tttt.Tools.user as user
from tttt.Tools.genObjectSelection import *

# argParser
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',    action='store', nargs='?',  choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'],  default='INFO', help="Log level for logging")
argParser.add_argument('--sample',      action='store', default='doubleMuon2018', help="Name of the sample.")
argParser.add_argument('--nJobs',              action='store',      nargs='?', type=int, default=1,  help="Maximum number of simultaneous jobs.")
argParser.add_argument('--job',                action='store',      nargs='?', type=int, default=0,  help="Run only job i")
argParser.add_argument('--targetDir',          action='store',      default='genPlots_temp')
argParser.add_argument('--small',              action='store_true', help='Run only on a small subset of the data?')#, default = True)
argParser.add_argument('--overwrite',          action='store_true', help='Overwrite?')#, default = True)
argParser.add_argument('--copy_input',         action='store_true', help='xrdcp input file?')#, default = True)
#argParser.add_argument('--genVars',            action='store_true', help='Run over TTTT central file for GetJets')
args = argParser.parse_args()


import tttt.Tools.logger as _logger
logger    = _logger.get_logger( args.logLevel, logFile = None )
import RootTools.core.logger as _logger_rt
logger_rt = _logger_rt.get_logger(args.logLevel, logFile = None)


import tttt.samples.miniAOD as samples
sample = getattr( samples, args.sample )

# Define & create output directory
output_directory = os.path.join(user.postprocessing_output_directory, args.targetDir, sample.name)
if not os.path.exists( output_directory ):
    try:
        os.makedirs( output_directory )
    except OSError:
        pass
    logger.info( "Created output directory %s", output_directory )


if args.nJobs>1:
    n_files_before = len(sample.files)
    sample = sample.split(args.nJobs)[args.job]
    n_files_after  = len(sample.files)
    logger.info( "Running job %i/%i over %i files from a total of %i.", args.job, args.nJobs, n_files_after, n_files_before)

# small option
maxEvents = -1
if args.small:
    args.targetDir += "_small"
    maxEvents       = 100
    sample.files=sample.files[:1]


# output file & log files
output_filename =  os.path.join(output_directory, sample.name+ '.root')

# Check whether we have to do anything
if os.path.exists( output_filename ) and checkRootFile( output_filename, checkForObjects=["Events"]) and not args.overwrite:
    logger.info( "File %s found. Quit.", output_filename )
    sys.exit(0)

# relocate original
if args.copy_input:
    sample.copy_files( os.path.join(user.postprocessing_tmp_directory, "input") )

_logger.   add_fileHandler( output_filename.replace('.root', '.log'), args.logLevel )
_logger_rt.add_fileHandler( output_filename.replace('.root', '_rt.log'), args.logLevel )

products = {
    'genJets': {'type':'vector<reco::GenJet>', 'label':( "slimmedGenJets" ) },
    #'genJetsSpecific': {'type':'vector<reco::GenJet::Specific>', 'label':("specific")} 
}


def varnames( vec_vars ):
    return [v.split('/')[0] for v in vec_vars.split(',')]

genVars = 'pt/F,eta/F,phi/F,mass/F,chargedHadronEnergy/F,neutralHadronEnergy/F,chargedEmEnergy/F,neutralEmEnergy/F,muonEnergy/F,chargedHadronMultiplicity/I,neutralHadronMultiplicity/I,neutralEmMultiplicity/I,chargedEmMultiplicity/I,muonMultiplicity/I'
#variables = varnames(genVars)
variables = [ "genJet[%s]"%genVars]
genVarNames = list( map( lambda p:p.split('/')[0], genVars.split(',') ))

fwliteReader = sample.fwliteReader( products = products )

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

def fill_vector( event, collection_name, collection_varnames, obj):
    for var in collection_varnames:
        try:
            setattr(event, collection_name+"_"+var, obj[var] )
        except TypeError as e:
            logger.error( "collection_name %s var %s obj[var] %r", collection_name, var,  obj[var] )
            raise e
        except KeyError as e:
            logger.error( "collection_name %s var %s obj[var] %r", collection_name, var,  obj[var] )
            raise e



def filler( event ):

    event.run, event.lumi, event.evt = fwliteReader.evt
    if fwliteReader.position % 100==0: logger.info("At event %i/%i", fwliteReader.position, min(fwliteReader.nEvents, maxEvents) if maxEvents>0 else fwliteReader.nEvents)

    fwlite_genJets = fwliteReader.products['genJets']
    
    #print(dir(fwlite_genJets))
    allGenJets = map( lambda t:{var: getattr(t, var)() for var in genVarNames}, filter( lambda j:j.pt()>30, fwlite_genJets) )
    genJets = list( filter( lambda j:isGoodGenJet( j, max_jet_abseta = max_jet_abseta), allGenJets ) )
    #genJets = filter (lambda j: abs(j.eta())<2.5, fwliteReader.event.genJets)
    #genJets = filter (lambda j: abs(j.eta())<2.5, allgenJets)
    
    #print(genJets)
    if len(genJets)>0:
        store_jets = [j for j in genJets]

    #    event.nGenJet = len(store_jets)
    fill_vector_collection(event, "genJet", genVarNames, genJets)

    return len(store_jets)>0


# TreeMaker initialisation
tmp_dir     = ROOT.gDirectory
output_file = ROOT.TFile( output_filename, 'recreate')
output_file.cd()
maker = TreeMaker(
    sequence  = [ filler ],
    variables = [ (TreeVariable.fromString(x) if type(x)==str else x) for x in variables ],
    treeName = "Events"
    )
tmp_dir.cd()

maker.start()
fwliteReader.start()

counter = 0
while fwliteReader.run():
    #if not args.genVars:
    #logger.debug( "Evt: %i %i %i Number of Tracks: %i", fwliteReader.event.evt, fwliteReader.event.lumi, fwliteReader.event.run, fwliteReader.event.gt.size() )
    # else:
    logger.debug("Evt: %i %i %i Number of good GenJets: %i", fwliteReader.event.evt, fwliteReader.event.lumi, fwliteReader.event.run, fwliteReader.event.genJets.size())

    #maker.fill()
    success = filler( maker.event )
    if success:
        maker.run()
    counter+=1

    if counter>=maxEvents and maxEvents>0:
        break

output_file.cd()
maker.tree.Write()
output_file.Close()

logger.info( "Done. Output: %s", output_filename )
