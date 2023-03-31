#!/usr/bin/env python
''' Make flat ntuple from GEN data tier 
'''
#
# Standard imports and batch mode
#
import ROOT
import os, sys
ROOT.gROOT.SetBatch(True)
import itertools
from math                                import sqrt, cos, sin, pi, acos, cosh, sinh
import imp

#RootTools
from RootTools.core.standard             import *

#Analysis
from Analysis.Tools.WeightInfo              import WeightInfo
from Analysis.Tools.leptonJetArbitration    import cleanJetsAndLeptons
from Analysis.Tools.GenSearch               import GenSearch
from Analysis.Tools.HyperPoly               import HyperPoly

# tttt
from tttt.Tools.user                    import postprocessing_output_directory
from tttt.Tools.helpers                 import deltaPhi, deltaR, deltaR2, cosThetaStar, closestOSDLMassToMZ, checkRootFile
from tttt.Tools.DelphesProducer         import DelphesProducer
from tttt.Tools.genObjectSelection      import isGoodGenJet, isGoodGenLepton, isGoodGenPhoton, genJetId
from tttt.Tools.DelphesObjectSelection  import isGoodRecoMuon, isGoodRecoElectron, isGoodRecoLepton, isGoodRecoJet, isGoodRecoPhoton

#
# Arguments
# 
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO',          nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--small',              action='store_true', help='Run only on a small subset of the data?')#, default = True)
argParser.add_argument('--reduce',             action='store_true', help='Reduce data to 1/10?')#, default = True)
argParser.add_argument('--miniAOD',            action='store_true', help='Run on miniAOD?')#, default = True)
argParser.add_argument('--overwrite',          action='store',      nargs='?', choices = ['none', 'all', 'target'], default = 'none', help='Overwrite?')#, default = True)
argParser.add_argument('--targetDir',          action='store',      default='v1')
argParser.add_argument('--sample',             action='store',      default='TTbb_MS', help="Name of the sample loaded from fwlite_benchmarks. Only if no inputFiles are specified")
argParser.add_argument('--inputFiles',         action='store',      nargs = '*', default=[])
argParser.add_argument('--delphesEra',         action='store',      default = None, choices = ["RunII", "RunIICentral", "RunIInoDelphesIso", "RunIIPileUp", "PhaseII"], help="specify delphes era")
argParser.add_argument('--targetSampleName',   action='store',      default=None, help="Name of the sample in case inputFile are specified. Otherwise ignored")
argParser.add_argument('--nJobs',              action='store',      nargs='?', type=int, default=1,  help="Maximum number of simultaneous jobs.")
argParser.add_argument('--job',                action='store',      nargs='?', type=int, default=0,  help="Run only job i")
argParser.add_argument('--addReweights',       action='store_true',   help="Add reweights?")
argParser.add_argument('--combinatoricalBTags', action='store_true',   help="BTags combinatorical?")
argParser.add_argument('--removeDelphesFiles', action='store_true',   help="remove Delphes file after postprocessing?")
argParser.add_argument('--interpolationOrder', action='store',      nargs='?', type=int, default=3,  help="Interpolation order for EFT weights.")
argParser.add_argument('--add_training_vars',  action='store_true',   default = False, help="add training variables for particle net?")
argParser.add_argument('--trainingCoefficients', action='store',    nargs='*', default=['ctt', 'cQQ1', 'cQQ8', 'cQt1', 'cQt8', 'ctHRe', 'ctHIm','ctb1', 'ctb8', 'cQb1', 'cQb8', 'cQtQb1Re', 'cQtQb8Re', 'cQtQb1Im', 'cQtQb8Im'], type = str,  help="Training vectors for particle net")
argParser.add_argument('--config',             action='store', type=str)
args = argParser.parse_args()

#
# Logger
#
import tttt.Tools.logger as _logger
import RootTools.core.logger as _logger_rt
logger    = _logger.get_logger(   args.logLevel, logFile = None)
logger_rt = _logger_rt.get_logger(args.logLevel, logFile = None)

# Load sample either from 
if len(args.inputFiles)>0:
    logger.info( "Input files found. Ignoring 'sample' argument. Files: %r", args.inputFiles)
    sample = FWLiteSample( args.targetSampleName, args.inputFiles)
else:
    sample_file = "$CMSSW_BASE/python/tttt/samples/GEN_EFT.py"
    samples = imp.load_source( "samples", os.path.expandvars( sample_file ) )
    sample = getattr( samples, args.sample )
    logger.debug( 'Loaded sample %s with %i files.', sample.name, len(sample.files) )

maxEvents = -1
if args.small: 
    args.targetDir += "_small"
    maxEvents       = 50 
    sample.files=sample.files[:1]
    
if (args.reduce):
    sample.reduceFiles( factor = 10 )

xsec = sample.xsec if hasattr( sample, "xsec" ) else sample.xSection 
nEvents = sample.nEvents

test = 0
    
# output directory
output_directory = os.path.join(postprocessing_output_directory, 'gen', args.targetDir+'_weightsum', sample.name) 

if not os.path.exists( output_directory ): 
    try:
        os.makedirs( output_directory )
    except OSError:
        pass
    logger.info( "Created output directory %s", output_directory )

# Load reweight pickle file if supposed to keep weights. 
extra_variables = []
if args.addReweights:
    weightInfo = WeightInfo( sample.reweight_pkl )
    weightInfo.set_order( args.interpolationOrder ) 
    
    weight_base      = TreeVariable.fromString( "weight[base/F]")
    weight_base.nMax = weightInfo.nid
   
    param_vector      = TreeVariable.fromString( "p[C/F]" )
    param_vector.nMax = HyperPoly.get_ndof(weightInfo.nvar, args.interpolationOrder)
    hyperPoly         = HyperPoly( args.interpolationOrder )
   
    def interpret_weight(weight_id):
        str_s = weight_id.rstrip('_nlo').split('_')
        res={}
        for i in range(len(str_s)/2):
            res[str_s[2*i]] = float(str_s[2*i+1].replace('m','-').replace('p','.'))
        return res

   
    weightInfo_data_lower = {k.lower():val for k, val in weightInfo.data.iteritems()}
    weightInfo_data_lower.update(weightInfo.data)


# Run only job number "args.job" from total of "args.nJobs"
if args.nJobs>1:
    n_files_before = len(sample.files)
    sample = sample.split(args.nJobs)[args.job]
    n_files_after  = len(sample.files)
    logger.info( "Running job %i/%i over %i files from a total of %i.", args.job, args.nJobs, n_files_after, n_files_before)

#max_jet_abseta = 5.2

if args.miniAOD:
    products = {
        'lhe':{'type':'LHEEventProduct', 'label':("externalLHEProducer")},
        'gen':{'type':'GenEventInfoProduct', 'label':'generator'},
        'gp':{'type':'vector<reco::GenParticle>', 'label':("prunedGenParticles")},
        #'gpPacked':{'type':'vector<pat::PackedGenParticle>', 'label':("packedGenParticles")},
        #'gp':{'type':'vector<pat::PackedGenParticle>', 'label':("packedGenParticles")},
        'genJets':{'type':'vector<reco::GenJet>', 'label':("slimmedGenJets")},
        'genMET':{'type':'vector<reco::GenMET>',  'label':("genMetTrue")},
    }
else:
    products = {
        'lhe':{'type':'LHEEventProduct', 'label':("externalLHEProducer")},
        'gen':{'type':'GenEventInfoProduct', 'label':'generator'},
        'gp':{'type':'vector<reco::GenParticle>', 'label':("genParticles")},
        'genJets':{'type':'vector<reco::GenJet>', 'label':("ak4GenJets")},
        'genMET':{'type':'vector<reco::GenMET>',  'label':("genMetTrue")},
    }

def varnames( vec_vars ):
    return [v.split('/')[0] for v in vec_vars.split(',')]

def vecSumPt(*args):
    return sqrt( sum([o['pt']*cos(o['phi']) for o in args],0.)**2 + sum([o['pt']*sin(o['phi']) for o in args],0.)**2 )

def addIndex( collection ):
    for i  in range(len(collection)):
        collection[i]['index'] = i


# variables
variables = []
# EDM standard variables
variables  += ["genWeight_sum/F"]
     


logger.info( "Running over files: %s", ", ".join(sample.files ) )

if args.delphesEra is not None:
    if args.delphesEra == 'RunII':
        from tttt.Tools.DelphesReader          import DelphesReader
        delphesCard = 'delphes_card_CMS'
    elif args.delphesEra == 'RunIICentral':
        from tttt.Tools.DelphesReader          import DelphesReader
        delphesCard = 'delphes_card_CMS_Central'
    elif args.delphesEra == 'RunIInoDelphesIso':
        from tttt.Tools.DelphesReader          import DelphesReader
        delphesCard = 'delphes_card_CMS_noLepIso'
    elif args.delphesEra == 'RunIIPileUp':
        from tttt.Tools.DelphesReader          import DelphesReader
        delphesCard = 'delphes_card_CMS_PileUp'
    elif args.delphesEra == 'PhaseII':
        from tttt.Tools.DelphesReaderCMSHLLHC  import DelphesReader
        delphesCard = 'CMS_PhaseII/CMS_PhaseII_200PU_v03'
readers = []

# FWLite reader if this is an EDM file
fwliteReader = sample.fwliteReader( products = products )
readers.append( fwliteReader )

# Delphes reader if we read Delphes
if args.delphesEra is not None:
    delphes_file = os.path.join( output_directory, 'delphes', sample.name+'.root' )
    if      ( not os.path.exists( delphes_file )) or \
            ( os.path.exists( delphes_file ) and not checkRootFile( delphes_file, checkForObjects=["Delphes"])) or \
            args.overwrite in ['all']:
        logger.debug( "Reproducing delphes file %s", delphes_file)
        delphesProducer = DelphesProducer( card = delphesCard )
        delphesProducer.produce( sample.files, delphes_file)
    delphesReader = DelphesReader( Sample.fromFiles( delphes_file, delphes_file, treeName = "Delphes" ) ) # RootTools version
    readers.append( delphesReader )

def addTLorentzVector( p_dict ):
    ''' add a TLorentz 4D Vector for further calculations
    '''
    p_dict['vecP4'] = ROOT.TLorentzVector( p_dict['pt']*cos(p_dict['phi']), p_dict['pt']*sin(p_dict['phi']),  p_dict['pt']*sinh(p_dict['eta']), p_dict['pt']*cosh(p_dict['eta']) )

tmp_dir     = ROOT.gDirectory
#post_fix = '_%i'%args.job if args.nJobs > 1 else ''
output_filename =  os.path.join(output_directory, sample.name + '.root')

_logger.   add_fileHandler( output_filename.replace('.root', '.log'), args.logLevel )
_logger_rt.add_fileHandler( output_filename.replace('.root', '_rt.log'), args.logLevel )

if os.path.exists( output_filename ) and checkRootFile( output_filename, checkForObjects=["Events"]) and args.overwrite =='none' :
    logger.info( "File %s found. Quit.", output_filename )
    sys.exit(0)

output_file = ROOT.TFile( output_filename, 'recreate')
output_file.cd()
maker = TreeMaker(
    #sequence  = config.sequence,
    variables = [ (TreeVariable.fromString(x) if type(x)==str else x) for x in variables ] + extra_variables,
    treeName = "Events"
    )

tmp_dir.cd()

gRandom = ROOT.TRandom3()
def eft_weight0():

    if fwliteReader.position % 1000==0: logger.info("At event %i/%i", fwliteReader.position, fwliteReader.nEvents)
    
    lhe_weights = fwliteReader.products['lhe'].weights()
    weights      = []
    param_points = []
    for weight in lhe_weights:
        
        weight_id = weight.id.rstrip('_nlo')
        
        if not weight_id.lower() in weightInfo_data_lower.keys(): 
            continue
        pos = weightInfo_data_lower[weight_id]
        weights.append( weight.wgt )
        interpreted_weight = interpret_weight(weight_id.lower()) 
        if not hyperPoly.initialized: param_points.append( tuple(interpreted_weight[var.lower()] for var in weightInfo.variables) )

    # get list of values of ref point in specific order
    ref_point_coordinates = [weightInfo.ref_point_coordinates[var] for var in weightInfo.variables]

    # Initialize with Reference Point
    if not hyperPoly.initialized: 
        hyperPoly.initialize( param_points, ref_point_coordinates )
    coeff = hyperPoly.get_parametrization( weights )
    
    return coeff[0]
    
    
                
def filler_sum( event, test ):
    event.genWeight_sum = test


counter = 0
for reader in readers:
    reader.start()
maker.start()
import numpy as np
while readers[0].run( ):
    for reader in readers[1:]:
        reader.run()
    
    if args.miniAOD: new_weight = fwliteReader.products['gen'].weight()
    if args.addReweights: new_weight = eft_weight0()
    test = test + new_weight
    
    
    counter += 1
    if counter == maxEvents:  
        break
filler_sum( maker.event, test )
maker.fill()
maker.event.init()
logger.info( "Done with running over %i events.", readers[0].nEvents )

output_file.cd()
maker.tree.Write()
output_file.Close()

logger.info( "Written output file %s", output_filename )
logger.info( "The sum of all event weights is %s", test)
##cleanup delphes file:
if os.path.exists( output_filename ) and args.delphesEra is not None and args.removeDelphesFiles:
    os.remove( delphes_file )
    logger.info( "Removing Delphes file %s", delphes_file )
