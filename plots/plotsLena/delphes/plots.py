#!/usr/bin/env python
''' Analysis script for standard plots
'''

# Standard imports and batch mode
import ROOT, os, itertools
#ROOT.gROOT.SetBatch(True)
ROOT.gROOT.SetBatch(True)
c1 = ROOT.TCanvas() # do this to avoid version conflict in png.h with keras import ...
c1.Draw()
c1.Print('/tmp/delete.png')

import copy
import operator
import random
from math                           import sqrt, cos, sin, pi, isnan, sinh, cosh, log, copysign

# Analysis
import Analysis.Tools.syncer        as syncer
from   Analysis.Tools.WeightInfo    import WeightInfo
from   Analysis.Tools.helpers       import deltaPhi, deltaR, getObjDict

# RootTools
from RootTools.core.standard        import *

# tttt
from tttt.Tools.user                 import plot_directory
from tttt.Tools.helpers              import deltaPhi, getCollection, deltaR, mZ
from tttt.Tools.delphesCutInterpreter import cutInterpreter

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO',          nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--plot_directory',     action='store',      default='delphes')
argParser.add_argument('--selection',          action='store',      default=None)
argParser.add_argument('--signal',             action='store',      default='TTTT_MS')
argParser.add_argument('--small',                                   action='store_true',     help='Run only on a small subset of the data?')
argParser.add_argument('--scaling',                                 action='store_true',     help='Scale the eft to SM?')
argParser.add_argument('--show_derivatives',                        action='store_true',     help='Show also the derivatives?')

args = argParser.parse_args()

# Logger'singlelep-WHJet' if sample.name=='WH' else 'dilep-ZHJet-onZ'
import tttt.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

plot_directory = os.path.join(plot_directory, args.plot_directory,  args.signal )
if args.small: plot_directory += "_small"

# Import samples
import tttt.samples.GEN_EFT_postProcessed as samples
    
signal = getattr( samples, args.signal)
 
# WeightInfo
signal.weightInfo = WeightInfo(signal.reweight_pkl)
signal.weightInfo.set_order(2)
signal.read_variables = [VectorTreeVariable.fromString( "p[C/F]", nMax=200 )]

if (args.signal =='TTTT_MS'):
    eft_configs = [
        {'color':ROOT.kBlack,       'param':{},              'tex':"SM"},
        {'color':ROOT.kBlue,      'param':{'ctt': 1},      'tex':"c_{tt}=1",        'binning':[20,0,1.5]},
        {'color':ROOT.kPink-7,    'param':{'cQQ1': 1},     'tex':"c_{QQ1}=1",       'binning':[20,0,1.5]},
        {'color':ROOT.kOrange,    'param':{'cQQ8': 1},     'tex':"c_{QQ8}=1",       'binning':[20,0,1.5]},
        {'color':ROOT.kRed,       'param':{'cQt1': 1},     'tex':"c_{Qt1}=1",       'binning':[20,0,1.5]},
        {'color':ROOT.kGreen,     'param':{'cQt8': 1},     'tex':"c_{Qt8}=1",       'binning':[20,0,1.5]},
        {'color':ROOT.kCyan,      'param':{'ctHRe': 1},    'tex':"c_{tHRe}=1",      'binning':[20,0,1.5]},
        {'color':ROOT.kMagenta,   'param':{'ctHIm': 1},    'tex':"c_{tHIm}=1",      'binning':[20,0,1.5]},
        # {'color':ROOT.kBlue-4,      'param':{'ctt':-1},      'tex':"c_{tt}=-1",       'binning':[20,0,1.5]},
        # {'color':ROOT.kPink-7-4,    'param':{'cQQ1':-1},     'tex':"c_{QQ1}=-1",      'binning':[20,0,1.5]},
        # {'color':ROOT.kOrange-4,    'param':{'cQQ8':-1},     'tex':"c_{QQ8}=-1",      'binning':[20,0,1.5]},
        # {'color':ROOT.kRed-4,       'param':{'cQt1':-1},     'tex':"c_{Qt1}=-1",      'binning':[20,0,1.5]},
        # {'color':ROOT.kGreen-4,     'param':{'cQt8':-1},     'tex':"c_{Qt8}=-1",      'binning':[20,0,1.5]},
        # {'color':ROOT.kCyan-4,      'param':{'ctHRe':-1},    'tex':"c_{tHRe}=-1",     'binning':[20,0,1.5]},
        # {'color':ROOT.kMagenta-4,   'param':{'ctHIm':-1},    'tex':"c_{tHIm}=-1",     'binning':[20,0,1.5]},
    ]
    
    if args.show_derivatives:
        eft_derivatives = [   
            {'der':('ctt',),                  'color':ROOT.kBlue-4,         'tex':"c_{tt}"},     
            {'der':('ctt','ctt'),             'color':ROOT.kBlue+2,         'tex':"c_{tt}^2"},      
            {'der':('cQQ1',),                 'color':ROOT.kPink-7-4,       'tex':"c_{QQ1}"},    
            {'der':('cQQ1','cQQ1'),           'color':ROOT.kPink-7+2,       'tex':"c_{QQ1}^2"},     
            {'der':('cQQ8',),                 'color':ROOT.kOrange-4,       'tex':"c_{QQ8}"},    
            {'der':('cQQ8','cQQ8'),           'color':ROOT.kOrange+2,       'tex':"c_{QQ8}^2"},     
            {'der':('cQt1',),                 'color':ROOT.kRed-4,          'tex':"c_{Qt1}"},    
            {'der':('cQt1','cQt1'),           'color':ROOT.kRed+2,          'tex':"c_{Qt1}^2"},     
            {'der':('cQt8',),                 'color':ROOT.kGreen-4,        'tex':"c_{Qt8}"},    
            {'der':('cQt8','cQt8'),           'color':ROOT.kGreen+2,        'tex':"c_{Qt8}^2"},     
            {'der':('ctHRe',),                'color':ROOT.kCyan-4,         'tex':"c_{tHRe}"},   
            {'der':('ctHRe','ctHRe'),         'color':ROOT.kCyan+2,         'tex':"c_{tHRe}^2"},    
            {'der':('ctHIm',),                'color':ROOT.kMagenta-4,      'tex':"c_{tHIm}"},   
            {'der':('ctHIm','ctHIm'),         'color':ROOT.kMagenta+2,      'tex':"c_{tHIm}^2"}, 
        ]    
    
if (args.signal=='TTbb_MS'):  
    eft_configs = [
        {'color':ROOT.kBlack,       'param':{},              'tex':"SM"},
        {'color':ROOT.kBlue,      'param':{'ctt': 10},      'tex':"c_{tt}=10",        'binning':[20,0,1.5]},
        {'color':ROOT.kPink-7,    'param':{'cQQ1': 10},     'tex':"c_{QQ1}=10",       'binning':[20,0,1.5]},
        #{'color':ROOT.kOrange,    'param':{'cQQ1': 20},     'tex':"c_{QQ1}=20",       'binning':[20,0,1.5]},
        {'color':ROOT.kOrange,    'param':{'cQQ8': 10},     'tex':"c_{QQ8}=10",       'binning':[20,0,1.5]},
        {'color':ROOT.kRed,       'param':{'cQt1': 10},     'tex':"c_{Qt1}=10",       'binning':[20,0,1.5]},
        {'color':ROOT.kGreen,     'param':{'cQt8': 10},     'tex':"c_{Qt8}=10",       'binning':[20,0,1.5]},
        {'color':ROOT.kCyan,      'param':{'ctHRe': 10},    'tex':"c_{tHRe}=10",      'binning':[20,0,1.5]},
        {'color':ROOT.kMagenta,   'param':{'ctHIm': 10},    'tex':"c_{tHIm}=10",      'binning':[20,0,1.5]},
        {'color':ROOT.kOrange-2,  'param':{'ctb1': 10},     'tex':"c_{tb1}=10",       'binning':[20,0,1.5]},
        {'color':ROOT.kPink-9,    'param':{'ctb8': 10},     'tex':"c_{tb8}=10",       'binning':[20,0,1.5]},
        {'color':ROOT.kBlue-2,    'param':{'cQb1': 10},     'tex':"c_{Qb1}=10",       'binning':[20,0,1.5]},
        #{'color':ROOT.kRed-2,     'param':{'cQb1': 20},     'tex':"c_{Qb1}=20",       'binning':[20,0,1.5]},
        {'color':ROOT.kRed-2,     'param':{'cQb8': 10},     'tex':"c_{Qb8}=10",       'binning':[20,0,1.5]},
        {'color':ROOT.kGreen-2,   'param':{'cQtQb1Re': 10}, 'tex':"c_{QtQb1Re}=10",   'binning':[20,0,1.5]},
        {'color':ROOT.kCyan-2,    'param':{'cQtQb8Re': 10}, 'tex':"c_{QtQb8Re}=10",   'binning':[20,0,1.5]},
        {'color':ROOT.kMagenta-2, 'param':{'cQtQb1Im': 10}, 'tex':"c_{QtQb1Im}=10",   'binning':[20,0,1.5]},
        {'color':ROOT.kCyan+3,    'param':{'cQtQb8Im': 10}, 'tex':"c_{QtQb8Im}=10",   'binning':[20,0,1.5]},
        # {'color':ROOT.kBlue-4,      'param':{'ctt':-10},      'tex':"c_{tt}=-1",       'binning':[20,0,1.5]},
        # {'color':ROOT.kPink-7-4,    'param':{'cQQ1':-10},     'tex':"c_{QQ1}=-1",      'binning':[20,0,1.5]},
        # {'color':ROOT.kOrange-4,    'param':{'cQQ8':-10},     'tex':"c_{QQ8}=-1",      'binning':[20,0,1.5]},
        # {'color':ROOT.kRed-4,       'param':{'cQt1':-10},     'tex':"c_{Qt1}=-1",      'binning':[20,0,1.5]},
        # {'color':ROOT.kGreen-4,     'param':{'cQt8':-10},     'tex':"c_{Qt8}=-1",      'binning':[20,0,1.5]},
        # {'color':ROOT.kCyan-4,      'param':{'ctHRe':-10},    'tex':"c_{tHRe}=-1",     'binning':[20,0,1.5]},
        # {'color':ROOT.kMagenta-4,   'param':{'ctHIm':-10},    'tex':"c_{tHIm}=-1",     'binning':[20,0,1.5]},
        # {'color':ROOT.kOrange-2-4,  'param':{'ctb1':-10},     'tex':"c_{tb1}=-1",      'binning':[20,0,1.5]},
        # {'color':ROOT.kPink-9-4,    'param':{'ctb8':-10},     'tex':"c_{tb8}=-1",      'binning':[20,0,1.5]},
        # {'color':ROOT.kBlue-2-4,    'param':{'cQb1':-10},     'tex':"c_{Qb1}=-1",      'binning':[20,0,1.5]},
        # {'color':ROOT.kRed-2-4,     'param':{'cQb8':-10},     'tex':"c_{Qb8}=-1",      'binning':[20,0,1.5]},
        # {'color':ROOT.kGreen-2-4,   'param':{'cQtQb1Re':-10}, 'tex':"c_{QtQb1Re}=-1",  'binning':[20,0,1.5]},
        # {'color':ROOT.kCyan-2-4,    'param':{'cQtQb8Re':-10}, 'tex':"c_{QtQb8Re}=-1",  'binning':[20,0,1.5]},
        # {'color':ROOT.kMagenta-2-4, 'param':{'cQtQb1Im':-10}, 'tex':"c_{QtQb1Im}=-1",  'binning':[20,0,1.5]},
        # {'color':ROOT.kCyan+3-4,    'param':{'cQtQb8Im':-10}, 'tex':"c_{QtQb8Im}=-1",  'binning':[20,0,1.5]},
    ]



    if args.show_derivatives:
        eft_derivatives = [   
            {'der':('ctt',),                  'color':ROOT.kBlue-4,         'tex':"c_{tt}"},     
            {'der':('ctt','ctt'),             'color':ROOT.kBlue+2,         'tex':"c_{tt}^2"},      
            {'der':('cQQ1',),                 'color':ROOT.kPink-7-4,       'tex':"c_{QQ1}"},    
            {'der':('cQQ1','cQQ1'),           'color':ROOT.kPink-7+2,       'tex':"c_{QQ1}^2"},     
            {'der':('cQQ8',),                 'color':ROOT.kOrange-4,       'tex':"c_{QQ8}"},    
            {'der':('cQQ8','cQQ8'),           'color':ROOT.kOrange+2,       'tex':"c_{QQ8}^2"},     
            {'der':('cQt1',),                 'color':ROOT.kRed-4,          'tex':"c_{Qt1}"},    
            {'der':('cQt1','cQt1'),           'color':ROOT.kRed+2,          'tex':"c_{Qt1}^2"},     
            {'der':('cQt8',),                 'color':ROOT.kGreen-4,        'tex':"c_{Qt8}"},    
            {'der':('cQt8','cQt8'),           'color':ROOT.kGreen+2,        'tex':"c_{Qt8}^2"},     
            {'der':('ctHRe',),                'color':ROOT.kCyan-4,         'tex':"c_{tHRe}"},   
            {'der':('ctHRe','ctHRe'),         'color':ROOT.kCyan+2,         'tex':"c_{tHRe}^2"},    
            {'der':('ctHIm',),                'color':ROOT.kMagenta-4,      'tex':"c_{tHIm}"},   
            {'der':('ctHIm','ctHIm'),         'color':ROOT.kMagenta+2,      'tex':"c_{tHIm}^2"},    
            {'der':('ctb1',),                 'color':ROOT.kOrange-2-4,     'tex':"c_{tb1}"},    
            {'der':('ctb1','ctb1'),           'color':ROOT.kOrange-2+2,     'tex':"c_{tb1}^2"},     
            {'der':('ctb8',),                 'color':ROOT.kPink-9-4,       'tex':"c_{tb8}"},    
            {'der':('ctb8','ctb8'),           'color':ROOT.kPink-9+2,       'tex':"c_{tb8}^2"},     
            {'der':('cQb1',),                 'color':ROOT.kBlue-2-4,       'tex':"c_{Qb1}"},    
            {'der':('cQb1','cQb1'),           'color':ROOT.kBlue-2+2,       'tex':"c_{Qb1}^2"},     
            {'der':('cQb8',),                 'color':ROOT.kRed-2-4,        'tex':"c_{Qb8}"},    
            {'der':('cQb8','cQb8'),           'color':ROOT.kRed-2+2,        'tex':"c_{Qb8}^2"},     
            {'der':('cQtQb1Re',),             'color':ROOT.kGreen-2-4,      'tex':"c_{QtQb1Re}"},
            {'der':('cQtQb1Re','cQtQb1Re'),   'color':ROOT.kGreen-2+2,      'tex':"c_{QtQb1Re}^2"}, 
            {'der':('cQtQb8Re',),             'color':ROOT.kCyan-2-4,       'tex':"c_{QtQb8Re}"},
            {'der':('cQtQb8Re','cQtQb8Re'),   'color':ROOT.kCyan-2+2,       'tex':"c_{QtQb8Re}^2"}, 
            {'der':('cQtQb1Im',),             'color':ROOT.kMagenta-2-4,    'tex':"c_{QtQb1Im}"},
            {'der':('cQtQb1Im','cQtQb1Im'),   'color':ROOT.kMagenta-2+2,    'tex':"c_{QtQb1Im}^2"}, 
            {'der':('cQtQb8Im',),             'color':ROOT.kCyan+3-4,       'tex':"c_{QtQb8Im}"},
            {'der':('cQtQb8Im','cQtQb8Im'),   'color':ROOT.kCyan+3+2,       'tex':"c_{QtQb8Im}^2"}, 
        ]    
 
for eft in eft_configs:
    eft['func'] = signal.weightInfo.get_weight_func(**eft['param']) 
    eft['name'] = "_".join( ["signal"] + ( ["SM"] if len(eft['param'])==0 else [ "_".join([key, str(val)]) for key, val in sorted(eft['param'].iteritems())] ) ) 
    
    
if not args.show_derivatives:
    eft_derivatives = []
    
for der in eft_derivatives:
    der['func'] = signal.weightInfo.get_diff_weight_func(der['der'])
    der['name'] = "_".join( ["derivative"] + list(der['der']) )

lumi  = 300

sequence = []
def make_eft_weights( event, sample):
    if sample.name!=signal.name:
        return
    SM_ref_weight         = event.lumiweight1fb*lumi
    # SM_ref_weight         = eft_configs[0]['func'](event, sample)*lumi
    #print SM_ref_weight, event.lumiweight1fb*300
    event.eft_weights     = [eft['func'](event, sample)/SM_ref_weight for eft in eft_configs]
    #event.eft_weights     = [1] + [eft['func'](event, sample)/SM_ref_weight for eft in eft_configs[1:]]
    event.eft_derivatives = [der['func'](event, sample)/SM_ref_weight for der in eft_derivatives]

stack = Stack( )

sequence.append( make_eft_weights )

eft_weights = [] 

for i_eft, eft in enumerate(eft_configs):
    stack.append( [signal] )
    #eft_weights.append( [get_eft_reweight(eft, signal.weightInfo)] )
    eft_weights.append( [lambda event, sample, i_eft=i_eft: event.eft_weights[i_eft]] )

for i_eft, eft in enumerate(eft_derivatives):
    stack.append( [signal] )
    #eft_weights.append( [get_eft_reweight(eft, signal.weightInfo)] )
    eft_weights.append( [lambda event, sample, i_eft=i_eft: event.eft_derivatives[i_eft]] )

weight_branches = ["lumiweight1fb"]



def weight_getter( branches ):
    getters = [ operator.attrgetter(branch) for branch in branches ]
    def getter( event, sample ):
        return reduce( operator.mul , [ g(event) for g in getters ], lumi ) 
    return getter



import delphes_config as config 
read_variables = []
read_variables+=config.read_variables

preselection = [ 
    #("debug", "(evt==25857178)") 
]

selectionString  = "&&".join( [ c[1] for c in preselection] + ([cutInterpreter.cutString(args.selection)] if args.selection is not None else []))
subDirectory     =  '-'.join( [ c[0] for c in preselection] + ([args.selection] if args.selection is not None else []))
print subDirectory, selectionString
if subDirectory  == '': 
    subDirectory = 'inc'

for sample in stack.samples:
    if selectionString != "":
        sample.addSelectionString( selectionString )
    if args.small:
        #sample.reduceFiles( factor = 30 )
        sample.reduceFiles( to = 10 )

bits = []

keras_models = []



### Helpers
def addTransverseVector( p_dict ):
    ''' add a transverse vector for further calculations
    '''
    p_dict['vec2D'] = ROOT.TVector2( p_dict['pt']*cos(p_dict['phi']), p_dict['pt']*sin(p_dict['phi']) )

# def addTLorentzVector( p_dict ):
    # ''' add a TLorentz 4D Vector for further calculations
    # '''
    # p_dict['vecP4'] = ROOT.TLorentzVector( p_dict['pt']*cos(p_dict['phi']), p_dict['pt']*sin(p_dict['phi']),  p_dict['pt']*sinh(p_dict['eta']), p_dict['pt']*cosh(p_dict['eta']) )



sequence+=config.sequence
def make_mva_inputs( event, sample ):
   for mva_variable, func in config.mva_variables:
       setattr( event, mva_variable, func(event, sample) )

sequence.append( make_mva_inputs ) 


# Use some defaults
Plot.setDefaults(stack = stack, weight = eft_weights, addOverFlowBin="upper")
 
plots        = []
plots2D      = []

postfix = "_scaled" if args.scaling else ""



plots.append(Plot( name = "b0_pt",
  texX = 'p_{T}(b_{0}) (GeV)', texY = 'Number of Events',
  attribute = lambda event, sample: event.recoBj0_pt,
  binning=[600/20,0,600],
))

plots.append(Plot( name = "b1_pt",
  texX = 'p_{T}(b_{1}) (GeV)', texY = 'Number of Events',
  attribute = lambda event, sample: event.recoBj1_pt,
  binning=[600/20,0,600],
))

plots.append(Plot( name = 'l1_pt',
  texX = 'p_{T}(l_{1}) (GeV)', texY = 'Number of Events' ,
  attribute = lambda event, sample:event.l1_pt,
  binning=[15,0,300],
))

plots.append(Plot( name = 'l2_pt',
  texX = 'p_{T}(l_{2}) (GeV)', texY = 'Number of Events' ,
  attribute = lambda event, sample:event.l2_pt,
  binning=[15,0,300],
))

plots.append(Plot( name = 'l1_eta',
  texX = '#eta(l_{1})', texY = 'Number of Events',
  attribute = lambda event, sample: event.l1_eta,
  binning=[20,-3,3],
))

plots.append(Plot( name = 'l2_eta',
  texX = '#eta(l_{2})', texY = 'Number of Events',
  attribute = lambda event, sample: event.l2_eta,
  binning=[20,-3,3],
))

plots.append(Plot( name = 'mT_l1',
  texX = 'm_{T}(l_{1})', texY = 'Number of Events',
  attribute = lambda event, sample: event.mT_l1,
  binning=[40,0,800],
))

plots.append(Plot( name = 'mT_l2',
  texX = 'm_{T}(l_{2})', texY = 'Number of Events',
  attribute = lambda event, sample: event.mT_l2,
  binning=[40,0,800],
))

plots.append(Plot( name = 'ml_l2',
  texX = 'm_{2l}', texY = 'Number of Events',
  attribute = lambda event, sample: event.ml_12,
  binning=[40,0,1500],
))

plots.append(Plot( name = "j0_pt"+postfix,
  texX = 'p_{T}(j_{0}) (GeV)', texY = 'Number of Events',
  attribute = lambda event, sample: event.jet0_pt,
  binning=[600/20,0,600],
))

plots.append(Plot( name = "j1_pt"+postfix,
  texX = 'p_{T}(j_{1}) (GeV)', texY = 'Number of Events',
  attribute = lambda event, sample: event.jet1_pt,
  binning=[600/20,0,600],
))

plots.append(Plot( name = "j2_pt"+postfix,
  texX = 'p_{T}(j_{2}) (GeV)', texY = 'Number of Events',
  attribute = lambda event, sample: event.jet2_pt,
  binning=[600/20,0,600],
))

plots.append(Plot( name = "j3_pt"+postfix,
  texX = 'p_{T}(j_{3}) (GeV)', texY = 'Number of Events',
  attribute = lambda event, sample: event.jet3_pt,
  binning=[600/20,0,600],
))
plots.append(Plot( name = "j4_pt"+postfix,
  texX = 'p_{T}(j_{4}) (GeV)', texY = 'Number of Events',
  attribute = lambda event, sample: event.jet4_pt,
  binning=[600/20,0,600],
))
plots.append(Plot( name = "j5_pt"+postfix,
  texX = 'p_{T}(j_{5}) (GeV)', texY = 'Number of Events',
  attribute = lambda event, sample: event.jet5_pt,
  binning=[600/20,0,600],
))
plots.append(Plot( name = "j6_pt"+postfix,
  texX = 'p_{T}(j_{6}) (GeV)', texY = 'Number of Events',
  attribute = lambda event, sample: event.jet6_pt,
  binning=[600/20,0,600],
))
plots.append(Plot( name = "j7_pt"+postfix,
  texX = 'p_{T}(j_{7}) (GeV)', texY = 'Number of Events',
  attribute = lambda event, sample: event.jet7_pt,
  binning=[600/20,0,600],
))


plots.append(Plot( name = "j0_eta"+postfix,
  texX = '#eta(j_{0}) (GeV)', texY = 'Number of Events',
  attribute = lambda event, sample: event.jet0_eta,
  binning=[30,-3,3],
))

plots.append(Plot( name = "j1_eta"+postfix,
  texX = '#eta(j_{1}) (GeV)', texY = 'Number of Events',
  attribute = lambda event, sample: event.jet1_eta,
  binning=[30,-3,3],
))

plots.append(Plot( name = "j2_eta"+postfix,
  texX = '#eta(j_{2}) (GeV)', texY = 'Number of Events',
  attribute = lambda event, sample: event.jet2_eta,
  binning=[30,-3,3],
))

plots.append(Plot( name = 'Met_pt'+postfix,
  texX = 'E_{T}^{miss} (GeV)', texY = 'Number of Events',
  attribute = lambda event, sample: event.met_pt,
  binning=[400/20,0,400],
))

plots.append(Plot( name = 'nJet'+postfix,
  texX = 'jet multiplicity', texY = 'Number of Events',
  attribute = lambda event, sample: event.nrecoJet,
  binning=[8,0,8],
))

plots.append(Plot( name = 'ht'+postfix,
  texX = 'H_{T}', texY = 'Number of Events',
  attribute = lambda event, sample: event.ht,
  binning=[30,0,3000],
))

plots.append(Plot( name = "m_4b",
  texX = 'm_{4b} (GeV)', texY = 'Number of Events',
  attribute = lambda event, sample: event.m_4b,
  binning=[25,0,2500],
))

plots.append(Plot( name = 'htb'+postfix,
  texX = 'H_{T,b-jets}', texY = 'Number of Events',
  attribute = lambda event, sample: event.htb,
  binning=[40,0,2500],
))

plots.append(Plot( name = 'ht_ratio'+postfix,
  texX = '#Delta H_{T}', texY = 'Number of Events',
  attribute = lambda event, sample: event.ht_ratio,
  binning=[40,0,1],
))

plots.append(Plot( name = 'dEta_jj'+postfix,
  texX = '#Delta#eta_{jj}', texY = 'Number of Events',
  attribute = lambda event, sample: event.dEtaj_12,
  binning=[40,0,6],
))

plots.append(Plot( name = 'dEta_ll'+postfix,
  texX = '#Delta#eta_{ll}', texY = 'Number of Events',
  attribute = lambda event, sample: event.dEtal_12,
  binning=[40,0,6],
))

plots.append(Plot( name = 'dPhi_jj'+postfix,
  texX = '#Delta#phi_{jj}', texY = 'Number of Events',
  attribute = lambda event, sample: event.dPhij_12,
  binning=[40,0,3.5],
))

plots.append(Plot( name = 'dPhi_l'+postfix,
  texX = '#Delta#phi_{ll}', texY = 'Number of Events',
  attribute = lambda event, sample: event.dPhil_12,
  binning=[40,0,3.5],
))

plots.append(Plot( name = 'min_dR_0'+postfix,
  texX = '#Delta R_{0}', texY = 'Number of Events',
  attribute = lambda event, sample: event.dR_min0,
  binning=[40,0,3.5],
))

plots.append(Plot( name = 'min_dR_1'+postfix,
  texX = '#Delta R_{1}', texY = 'Number of Events',
  attribute = lambda event, sample: event.dR_min1,
  binning=[40,0,3.5],
))

plots.append(Plot( name = 'min_dR_bb'+postfix,
  texX = '#Delta R_{b-jet,b-jet}', texY = 'Number of Events',
  attribute = lambda event, sample: event.min_dR_bb,
  binning=[40,0,3.5],
))

plots.append(Plot( name = 'min_dR_2l'+postfix,
  texX = '#Delta R_{2l}', texY = 'Number of Events',
  attribute = lambda event, sample: event.dR_2l,
  binning=[40,0,3.5],
))


plots.append(Plot( name = 'mj_12'+postfix,
  texX = 'm_{2j}', texY = 'Number of Events',
  attribute = lambda event, sample: event.mj_12,
  binning=[40,0,2500],
))

plots.append(Plot( name = 'mlj_l1'+postfix,
  texX = 'm_{l1, j1}', texY = 'Number of Events',
  attribute = lambda event, sample: event.mlj_11,
  binning=[40,0,2500],
))

plots.append(Plot( name = 'mlj_l2'+postfix,
  texX = 'm_{l1, j2}', texY = 'Number of Events',
  attribute = lambda event, sample: event.mlj_12,
  binning=[40,0,2500],
))

plots.append(Plot( name = 'mt2ll'+postfix,
  texX = 'm2_{T,ll}', texY = 'Number of Events',
  attribute = lambda event, sample: event.mt2ll,
  binning=[40,0,1200],
))

plots.append(Plot( name = 'mt2bb'+postfix,
  texX = 'm2_{T,bb}', texY = 'Number of Events',
  attribute = lambda event, sample: event.mt2bb,
  binning=[40,0,1200],
))

plots.append(Plot( name = 'mt2blbl'+postfix,
  texX = 'm2_{T,blbl}', texY = 'Number of Events',
  attribute = lambda event, sample: event.mt2blbl,
  binning=[40,0,1200],
))

# Text on the plots
def drawObjects( hasData = False ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    lines = [
      (0.15, 0.95, 'CMS Preliminary' if hasData else "Delphes Simulation"), 
      #(0.45, 0.95, 'L=%3.1f fb{}^{-1} (13 TeV) Scale %3.2f'% ( lumi_scale, dataMCScale ) ) if plotData else (0.45, 0.95, 'L=%3.1f fb{}^{-1} (13 TeV)' % lumi_scale)
    ]
    return [tex.DrawLatex(*l) for l in lines] 

# draw function for plots
def drawPlots(plots, subDirectory=''):
  for log in [False, True]:
    plot_directory_ = os.path.join(plot_directory, subDirectory)
    plot_directory_ = os.path.join(plot_directory_, "log") if log else os.path.join(plot_directory_, "lin")
    for plot in plots:
        if  type(plot)==Plot2D:
            plotting.draw2D( plot,
                       plot_directory = plot_directory_,
                       logX = False, logY = False, logZ = log,
                       drawObjects = drawObjects(),
                       copyIndexPHP = True,
#                       oldColors = True,
                       ) 
        else:
            if not max(l[0].GetMaximum() for l in plot.histos): continue # Empty plot
            subtr = 0 #if args.show_derivatives else len(eft_configs)
            
            scale = {}
            if (args.scaling):
              for i in range(1,len(plot.histos)):
                  scale.update({i: 0})
            plotting.draw(plot,
              plot_directory = plot_directory_,
              #ratio =  None,
              ratio = {'histos':[(i,0) for i in range(1,len(plot.histos))], 'yRange':(0.1,1.9)},
              logX = False, logY = log, sorting = False,
              yRange = (0.03, "auto") if log else "auto",
              scaling = scale,
              legend =  ( (0.17,0.9-0.05*sum(map(len, plot.histos))/2,1.,0.9), 2), 
              drawObjects = drawObjects( ),
              copyIndexPHP = True,
            )

plotting.fill(plots+plots2D, read_variables = read_variables, sequence = sequence, max_events = -1 if args.small else -1)



#color EFT
offset = 0 
for plot in plots:
    for i_eft, eft in enumerate(eft_configs):
        plot.histos[i_eft+offset][0].legendText = eft['tex']
        plot.histos[i_eft+offset][0].style      = styles.lineStyle(eft['color'],width=1)
        plot.histos[i_eft+offset][0].SetName(eft['name'])
    for i_eft, eft in enumerate(eft_derivatives):
        if args.show_derivatives:
            plot.histos[i_eft+offset+len(eft_configs)][0].legendText = eft['tex']
            plot.histos[i_eft+offset+len(eft_configs)][0].style = styles.lineStyle(eft['color'],width=1,dashed=True)
        else:
            plot.histos[i_eft+offset+len(eft_configs)][0].legendText = None
            plot.histos[i_eft+offset+len(eft_configs)][0].style = styles.invisibleStyle()
        plot.histos[i_eft+offset+len(eft_configs)][0].SetName(eft['name'])

#plot_phi_subtr.histos = plot_phi_subtr.histos[1:]

drawPlots(plots+plots2D, subDirectory = subDirectory)

logger.info( "Done with prefix %s and selectionString %s", args.selection, cutInterpreter.cutString(args.selection) )

syncer.sync()

