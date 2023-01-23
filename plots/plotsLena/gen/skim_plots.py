#!/usr/bin/env python
''' Analysis script for standard plots
'''

# Standard imports and batch mode
import ROOT, os, itertools
#ROOT.gROOT.SetBatch(True)
import copy
from math                           import sqrt, cos, sin, pi, isnan, sinh, cosh, log, acos

# Analysis
import Analysis.Tools.syncer        as syncer
from   Analysis.Tools.WeightInfo    import WeightInfo

# RootTools
from RootTools.core.standard        import *

# tttt
from tttt.Tools.user                 import plot_directory
from tttt.Tools.helpers              import deltaPhi, getCollection, deltaR, mZ
from tttt.Tools.genCutInterpreter    import cutInterpreter
from tttt.Tools.genObjectSelection   import isGoodGenJet

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO',          nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--plot_directory',     action='store',      default='gen')
argParser.add_argument('--selection',          action='store',      default=None)
argParser.add_argument('--sample',             action='store',      default='TTTT_MS')
argParser.add_argument('--WC',                 action='store',      nargs = '*',             default=['ctt'], type=str)
argParser.add_argument('--WCval',              action='store',      nargs = '*',             type=float,    default=[1.0],  help='Values of the Wilson coefficient')
argParser.add_argument('--WCval_FI',           action='store',      nargs = '*',             type=float,    default=[],  help='Values of the Wilson coefficient to show FI for.')
argParser.add_argument('--small',                                   action='store_true',     help='Run only on a small subset of the data?')
args = argParser.parse_args()

# Logger
import tttt.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

if args.small: args.plot_directory += "_small"

# Import samples
from tttt.samples.GEN_EFT_postProcessed import *
sample = eval(args.sample) 
# objects to plot
objects = sample.objects if hasattr( sample, "objects") else []

# WeightInfo
w = WeightInfo(sample.reweight_pkl)
w.set_order(2)

colors = [ROOT.kBlue, ROOT.kPink-7, ROOT.kOrange, ROOT.kRed, ROOT.kGreen, ROOT.kCyan, ROOT.kMagenta,ROOT.kOrange-2, ROOT.kPink-9, ROOT.kBlue-2, ROOT.kRed-2, ROOT.kGreen-2, ROOT.kCyan-2, ROOT.kMagenta-2, ROOT.kCyan+3]
# define which Wilson coefficients to plot
FIs = []
params =  [ {'legendText':'SM',  'color':ROOT.kBlack, 'WC':{}} ] 
for i in range (len(args.WC)):
    params += [ {'legendText':'%s %3.2f'%(args.WC[i], wc), 'color':colors[i]+(i_wc),  'WC':{args.WC[i]:wc} } for i_wc, wc in enumerate(args.WCval)]
for i_param, param in enumerate(params):
    params[i_param]['sample'] = sample
    params[i_param]['style']  = styles.lineStyle( params[i_param]['color'] )
params[0]['style']  = styles.lineStyle( params[0]['color'], 2 )
stack = Stack(*[ [ param['sample'] ] for param in params ] )
weight= [ [ w.get_weight_func(**param['WC']) ] for param in params ]
# FIs.append( ( ROOT.kGray+1, "WC@SM",   w.get_fisher_weight_string(args.WC,args.WC, **{args.WC:0})) )
# for i_WCval, WCval in enumerate(args.WCval_FI):
    # FIs.append( ( ROOT.kGray+i_WCval,   "WC@WC=%3.2f"%WCval, w.get_fisher_weight_string(args.WC,args.WC, **{args.WC:WCval})) )

# Read variables and sequences
read_variables = [
    "genMet_pt/F", "genMet_phi/F", 
    "ngenJet/I", "genJet[pt/F,eta/F,phi/F,matchBParton/I]", 
    "ngenLep/I", "genLep[pt/F,eta/F,phi/F,pdgId/I,mother_pdgId/I]", 
    "ngenTop/I", "genTop[pt/F,eta/F,phi/F]",
    "ngenB/I", "genB[pt/F,eta/F,phi/F]",
    "ngenZ/I", "genZ[pt/F,phi/F,eta/F,daughter_pdgId/I,l1_index/I,l2_index/I]",
    "ngenW/I", "genW[pt/F,phi/F,eta/F,daughter_pdgId/I,l1_index/I,l2_index/I]",
    "ngenPhoton/I", "genPhoton[pt/F,phi/F,eta/F]",
]
read_variables.append( VectorTreeVariable.fromString('p[C/F]', nMax=2000) )

preselection = [ 
    #( "SMP-20-005",  "genPhoton_pt[0]>300&&genMet_pt>80&&genLep_pt[genW_l1_index[0]]>80&&sqrt(acos(cos(genLep_phi[genW_l1_index[0]]-genPhoton_phi[0]))**2+(genLep_eta[genW_l1_index[0]]-genPhoton_eta[0])**2)>3.0"),
    #( "SMP-20-005-light",  "genPhoton_pt[0]>80&genMet_pt>30&&genLep_pt[genW_l1_index[0]]>30&&sqrt(acos(cos(genLep_phi[genW_l1_index[0]]-genPhoton_phi[0]))**2+(genLep_eta[genW_l1_index[0]]-genPhoton_eta[0])**2)>3.0"),
    #( "SMP-20-005-ul",  "genPhoton_pt[0]>40&genMet_pt>30&&genLep_pt[genW_l1_index[0]]>30&&sqrt(acos(cos(genLep_phi[genW_l1_index[0]]-genPhoton_phi[0]))**2+(genLep_eta[genW_l1_index[0]]-genPhoton_eta[0])**2)>3.0"),
]

selectionString  = "&&".join( [ c[1] for c in preselection] + ([cutInterpreter.cutString(args.selection)] if args.selection is not None else []))
subDirectory     =  '-'.join( [ c[0] for c in preselection] + ([args.selection] if args.selection is not None else []))
if subDirectory  == '': 
    subDirectory = 'inc'

for sample in stack.samples:
    if selectionString != "":
        sample.addSelectionString( selectionString )
    if args.small:
        #sample.reduceFiles( factor = 30 )
        sample.reduceFiles( to = 2 )

## Helpers
def addTransverseVector( p_dict ):
    ''' add a transverse vector for further calculations
    '''
    p_dict['vec2D'] = ROOT.TVector2( p_dict['pt']*cos(p_dict['phi']), p_dict['pt']*sin(p_dict['phi']) )

def addTLorentzVector( p_dict ):
    ''' add a TLorentz 4D Vector for further calculations
    '''
    p_dict['vec4D'] = ROOT.TLorentzVector( p_dict['pt']*cos(p_dict['phi']), p_dict['pt']*sin(p_dict['phi']),  p_dict['pt']*sinh(p_dict['eta']), 0 )
    
def addTLorentzVectortop( p_dict ):
    ''' add a TLorentz 4D Vector for further calculations
    '''
    p_dict['vec4D'] = ROOT.TLorentzVector( p_dict['pt']*cos(p_dict['phi']), p_dict['pt']*sin(p_dict['phi']),  p_dict['pt']*sinh(p_dict['eta']), p_dict['pt']*cosh(p_dict['eta']) )
    
#sequence functions
sequence = []

def addLorentzTopB ( event, sample ):
    event.tops = getCollection( event, 'genTop', ['pt', 'eta', 'phi'], 'ngenTop' )
    event.bs   = getCollection( event, 'genB', ['pt', 'eta', 'phi'], 'ngenB' )
    event.tops = list(filter( lambda j:isGoodGenJet( j ), event.tops)) ###?
    event.bs   = list(filter( lambda j:isGoodGenJet( j ), event.bs  ))
    # sort
    event.tops = sorted( event.tops, key=lambda k: -k['pt'] )
    event.bs = sorted( event.bs, key=lambda k: -k['pt'] )
    
    for p in event.tops:
        addTLorentzVectortop( p )
    for p in event.bs:
        addTLorentzVectortop( p )
    
    #print (event.tops[0]['vec4D']+event.tops[1]['vec4D']+event.tops[2]['vec4D']+event.tops[3]['vec4D']).M() 
    
sequence.append( addLorentzTopB )


        
def makeJets( event, sample ):
    ''' Add a list of filtered all jets to the event
    '''

    # Retrieve & filter
    event.jets = getCollection( event, 'genJet', ['pt', 'eta', 'phi', 'matchBParton'], 'ngenJet' )
    event.jets = list(filter( lambda j:isGoodGenJet( j ), event.jets))
    # sort
    event.jets = sorted( event.jets, key=lambda k: -k['pt'] )

    # Add extra vectors
    for p in event.jets:
        addTransverseVector( p )
        addTLorentzVector( p )

    # True B's
    event.trueBjets    = list( filter( lambda j: j['matchBParton'], event.jets ) )
    event.trueNonBjets = list( filter( lambda j: not j['matchBParton'], event.jets ) )    
        
sequence.append( makeJets )

def calculatedeltaR (event, sample ):
    if len(list(event.trueBjets))>=2:
        event.min_dR_bjbj = min( [deltaR( comb[0], comb[1] ) for comb in itertools.combinations( event.trueBjets, 2)] )
    else:
        event.min_dR_bjbj = -1 
        
    if len(list(event.jets))>=2:
        event.min_dR_jj = min( [deltaR( comb[0], comb[1] ) for comb in itertools.combinations( event.jets, 2)] )
    else:
        event.min_dR_jj = -1    
        
    if len(list(event.tops))>=2:
        event.min_dR_tt = min( [deltaR( comb[0], comb[1] ) for comb in itertools.combinations( event.tops, 2)] )
    else:
        event.min_dR_tt = -1   

    if len(list(event.bs))>=2:
        event.min_dR_bb = min( [deltaR( comb[0], comb[1] ) for comb in itertools.combinations( event.bs, 2)] )
    else:
        event.min_dR_bb = -1  

sequence.append ( calculatedeltaR ) 

def makeMET( event, sample ):
    ''' Make a MET vector to facilitate further calculations
    '''
    event.MET = {'pt':event.genMet_pt, 'phi':event.genMet_phi}
    addTransverseVector( event.MET )

sequence.append( makeMET )

def makeLeps( event, sample ):

    # Read leptons, do not yet filter
    event.all_leps = getCollection( event, 'genLep', ['pt', 'eta', 'phi', 'pdgId', 'mother_pdgId'], 'ngenLep' )
    # Add extra vectors
    for p in event.all_leps:
        addTransverseVector( p )
        addTLorentzVector( p )

    # Sort
    event.leps = sorted( event.all_leps, key=lambda k: -k['pt'] )

    # Cross-cleaning: remove leptons that overlap with a jet within 0.4
    event.leps = list(filter( lambda l: min( [ deltaR(l, j) for j in event.jets ] + [999] ) > 0.4 , event.leps ))

    # find leptons from Z
    event.lepsFromZ = list( filter( lambda j: j['mother_pdgId'] == 23 , event.leps ) )
    event.foundZ    = len( event.lepsFromZ )==2 and event.lepsFromZ[0]['pdgId'] * event.lepsFromZ[1]['pdgId'] < 0
    event.Z_deltaPhi_ll = deltaPhi( event.lepsFromZ[0]['phi'], event.lepsFromZ[1]['phi']) if event.foundZ else float('nan')
    event.Z_deltaR_ll   = deltaR( *event.lepsFromZ) if event.foundZ else float('nan')
 
    # convinience
    #event.Z_unitVec2D = UnitVectorT2( event.Z_phi )
    #event.Z_vec4D     = ROOT.TLorentzVector()
    #event.Z_vec4D.SetPtEtaPhiM( event.Z_pt, event.Z_eta, event.Z_phi, event.Z_mass )
    #event.Z_unitVec3D = event.Z_vec4D.Vect()
    #event.Z_unitVec3D /= event.Z_unitVec3D.Mag() 

    # find leptons that are NOT from Z 
    event.leptonsNotFromZ = [lepton for lepton in event.leps if lepton not in event.lepsFromZ] 
    
    dR_vals = sorted([deltaR(event.trueBjets[i], event.leps[j]) for i in range(len(list(event.trueBjets))) for j in range(len(list(event.leps)))])
    if len(dR_vals)>=2:
        event.dR_min0 = dR_vals[0]
        event.dR_min1 = dR_vals[1]
    else:
        event.dR_min0 = -1
        event.dR_min1 = -1
        
sequence.append( makeLeps )

# interference resurrection

import re
# make stack and construct weights
def coeff_getter( coeff):
    def getter_( event, sample):
        #print "Filling with", coeff, event.p_C[coeff]
        return event.p_C[coeff]
    return getter_

def add_fisher_plot( plot, fisher_string, color, legendText):

    # the coefficients we need
    required_coefficients = map( lambda s: int(s.replace('[','').replace(']','')), list(set(re.findall(r'\[[0-9][0-9]*\]', fisher_string ) )) )
    # copy the plot
    fisher_plot = copy.deepcopy( plot )
    # modify weights etc
    fisher_plot.name+="_fisher_coeffs"
    fisher_plot.weight = [ [ coeff_getter(coeff) ] for coeff in required_coefficients ]
    fisher_plot.stack  = Stack( *[[sample] for coeff in required_coefficients] )
    # for computing the FI
    fisher_plot.coefficients = required_coefficients
    fisher_plot.formula      = re.sub(r'p_C\[([0-9][0-9]*)\]', r'{lambda_\1}', fisher_string)
    # pass through information for plotting
    fisher_plot.color        = color
    fisher_plot.legendText   = legendText
    # add the fisher_plot to the original plot so we know which is which
    if hasattr( plot, "fisher_plots"):
        plot.fisher_plots.append( fisher_plot )
    else: 
        plot.fisher_plots = [fisher_plot]
    return fisher_plot 
    
# Use some defaults
Plot.setDefaults(stack = stack, weight = weight, addOverFlowBin=None)
  
plots        = []
fisher_plots = []

l = ''.join(args.WC)
if (len(args.WC)>4): l = 'multi'
postfix = '_'+l

if 'g' in objects:
    plots.append(Plot( name = "Photon0_pt"+postfix,
      texX = 'p_{T}(#gamma_{0}) (GeV)', texY = 'Number of Events',
      attribute = lambda event, sample: event.genPhoton_pt[0] if event.ngenPhoton>0 else float('nan'),
      binning=[600/20,0,600],
    ))
    # for color, legendText, fisher_string in FIs:
        # fisher_plots.append( add_fisher_plot( plots[-1], fisher_string, color, legendText ) )

    plots.append(Plot( name = "Photon0_eta"+postfix,
      texX = '#eta(#gamma_{0}) (GeV)', texY = 'Number of Events',
      attribute = lambda event, sample: event.genPhoton_eta[0] if event.ngenPhoton>0 else float('nan'),
      binning=[30,-3,3],
    ))
    # for color, legendText, fisher_string in FIs:
        # fisher_plots.append( add_fisher_plot( plots[-1], fisher_string, color, legendText ) )

if 't' in objects:
    plots.append(Plot( name = "W0_pt"+postfix,
      texX = 'p_{T}(W_{0}) (GeV)', texY = 'Number of Events',
      attribute = lambda event, sample: event.genW_pt[0] if event.ngenW>0 else float('nan'),
      binning=[600/20,0,600],
    ))
    # for color, legendText, fisher_string in FIs:
        # fisher_plots.append( add_fisher_plot( plots[-1], fisher_string, color, legendText ) )

    plots.append(Plot( name = "W0_eta"+postfix,
      texX = '#eta(W_{0}) (GeV)', texY = 'Number of Events',
      attribute = lambda event, sample: event.genW_eta[0] if event.ngenW>0 else float('nan'),
      binning=[30,-3,3],
    ))
    # for color, legendText, fisher_string in FIs:
        # fisher_plots.append( add_fisher_plot( plots[-1], fisher_string, color, legendText ) )

    plots.append(Plot( name = "W1_pt"+postfix,
      texX = 'p_{T}(W_{1}) (GeV)', texY = 'Number of Events',
      attribute = lambda event, sample: event.genW_pt[1] if event.ngenW>1 else float('nan'),
      binning=[600/20,0,600],
    ))

    plots.append(Plot( name = "W1_eta"+postfix,
      texX = '#eta(W_{1}) (GeV)', texY = 'Number of Events',
      attribute = lambda event, sample: event.genW_eta[1] if event.ngenW>1 else float('nan'),
      binning=[30,-3,3],
    ))

if 't' in objects:
    plots.append(Plot( name = "top0_pt"+postfix,
      texX = 'p_{T}(top_{0}) (GeV)', texY = 'Number of Events',
      attribute = lambda event, sample: event.genTop_pt[0] if event.ngenTop>0 else float('nan'),
      binning=[600/20,0,800],
    ))
    # for color, legendText, fisher_string in FIs:
        # fisher_plots.append( add_fisher_plot( plots[-1], fisher_string, color, legendText ) )

    plots.append(Plot( name = "top0_eta"+postfix,
      texX = '#eta(top_{0}) (GeV)', texY = 'Number of Events',
      attribute = lambda event, sample: event.genTop_eta[0] if event.ngenTop>0 else float('nan'),
      binning=[30,-5,5],
    ))
    # for color, legendText, fisher_string in FIs:
        # fisher_plots.append( add_fisher_plot( plots[-1], fisher_string, color, legendText ) )

    plots.append(Plot( name = "top1_pt"+postfix,
      texX = 'p_{T}(top_{1}) (GeV)', texY = 'Number of Events',
      attribute = lambda event, sample: event.genTop_pt[1] if event.ngenTop>1 else float('nan'),
      binning=[600/20,0,800],
    ))

    plots.append(Plot( name = "top1_eta"+postfix,
      texX = '#eta(top_{1}) (GeV)', texY = 'Number of Events',
      attribute = lambda event, sample: event.genTop_eta[1] if event.ngenTop>1 else float('nan'),
      binning=[30,-5,5],
    ))
    
    plots.append(Plot( name = "top2_pt"+postfix,
      texX = 'p_{T}(top_{2}) (GeV)', texY = 'Number of Events',
      attribute = lambda event, sample: event.genTop_pt[2] if event.ngenTop>2 else float('nan'),
      binning=[600/20,0,800],
    ))

    plots.append(Plot( name = "top2_eta"+postfix,
      texX = '#eta(top_{2}) (GeV)', texY = 'Number of Events',
      attribute = lambda event, sample: event.genTop_eta[2] if event.ngenTop>2 else float('nan'),
      binning=[30,-5,5],
    ))
    
    plots.append(Plot( name = "top3_pt"+postfix,
      texX = 'p_{T}(top_{3}) (GeV)', texY = 'Number of Events',
      attribute = lambda event, sample: event.genTop_pt[3] if event.ngenTop>3 else float('nan'),
      binning=[600/20,0,800],
    ))

    plots.append(Plot( name = "top3_eta"+postfix,
      texX = '#eta(top_{3}) (GeV)', texY = 'Number of Events',
      attribute = lambda event, sample: event.genTop_eta[3] if event.ngenTop>3 else float('nan'),
      binning=[30,-5,5],
    ))
    
    plots.append(Plot( name = 'dEtat_12'+postfix,
      texX = '\Delta\eta_{top}', texY = 'Number of Events / 20 GeV',
      attribute = lambda event, sample: abs(event.genTop_eta[0] - event.genTop_eta[1]) if event.ngenTop>=2 else -10,
      binning=[40,0,6],
    ))

    plots.append(Plot( name = 'dPhit_12'+postfix,
      texX = '\Delta\phi_{top}', texY = 'Number of Events / 20 GeV',
      attribute = lambda event, sample: acos(cos(event.genTop_phi[0]-event.genTop_phi[1])) if event.ngenTop>=2 else 0,
      binning=[40,0,3.5],
    ))
    
    plots.append(Plot( name = 'mt_t_12'+postfix,
      texX = 'm_{t, top12}', texY = 'Number of Events / 20 GeV',
      attribute = lambda event, sample: sqrt(2*event.genTop_pt[0]*event.genTop_pt[1]*(cosh(event.genTop_eta[0]-event.genTop_eta[1])-cos(event.genTop_phi[0]-event.genTop_phi[1]))) if len(event.genTop_eta)>=2 else 0,
      binning=[40,0,2500],
    ))
    
    plots.append(Plot( name = 'm_tttt'+postfix,
      texX = 'm_{tttt}', texY = 'Number of Events / 20 GeV',
      attribute = lambda event, sample: abs((event.tops[0]['vec4D']+event.tops[1]['vec4D']+event.tops[2]['vec4D']+event.tops[3]['vec4D']).M()) if len(list(event.tops))>=4 else 0,
      binning=[12,500,5000],
    ))
    
    plots.append(Plot( name = 'm_ttbb'+postfix,
      texX = 'm_{ttbb}', texY = 'Number of Events / 20 GeV',
      attribute = lambda event, sample: abs((event.tops[0]['vec4D']+event.tops[1]['vec4D']+event.bs[0]['vec4D']+event.bs[1]['vec4D']).M()) if (len(list(event.tops))>=2 and len(list(event.bs))>=2) else 0,
      binning=[12,300,5000],
    ))
    
    plots.append(Plot( name = 'min_dR_tt'+postfix,
      texX = '\Delta R_{t,t}', texY = 'Number of Events / 20 GeV',
      attribute = lambda event, sample: event.min_dR_tt,
      binning=[40,0,3.5],
    ))
    
    
#if 'b' in objects:
    plots.append(Plot( name = "b0_pt"+postfix,
      texX = 'p_{T}(b_{0}) (GeV)', texY = 'Number of Events',
      attribute = lambda event, sample: event.genB_pt[0] if event.ngenB>0 else float('nan'),
      binning=[600/20,0,600],
    ))
    # for color, legendText, fisher_string in FIs:
        # fisher_plots.append( add_fisher_plot( plots[-1], fisher_string, color, legendText ) )

    plots.append(Plot( name = "b0_eta"+postfix,
      texX = '#eta(b_{0}) (GeV)', texY = 'Number of Events',
      attribute = lambda event, sample: event.genB_eta[0] if event.ngenB>0 else float('nan'),
      binning=[30,-5,5],
    ))
    # for color, legendText, fisher_string in FIs:
        # fisher_plots.append( add_fisher_plot( plots[-1], fisher_string, color, legendText ) )

    plots.append(Plot( name = "b1_pt"+postfix,
      texX = 'p_{T}(b_{1}) (GeV)', texY = 'Number of Events',
      attribute = lambda event, sample: event.genB_pt[1] if event.ngenB>1 else float('nan'),
      binning=[600/20,0,600],
    ))

    plots.append(Plot( name = "b1_eta"+postfix,
      texX = '#eta(b_{1}) (GeV)', texY = 'Number of Events',
      attribute = lambda event, sample: event.genB_eta[1] if event.ngenB>1 else float('nan'),
      binning=[30,-5,5],
    ))
    
    plots.append(Plot( name = 'dEtab_12'+postfix,
      texX = '\Delta\eta_{b}', texY = 'Number of Events / 20 GeV',
      attribute = lambda event, sample: abs(event.genB_eta[0] - event.genB_eta[1]) if event.ngenB>=2 else -10,
      binning=[40,0,6],
    ))

    plots.append(Plot( name = 'dPhib_12'+postfix,
      texX = '\Delta\phi_{b}', texY = 'Number of Events / 20 GeV',
      attribute = lambda event, sample: acos(cos(event.genB_phi[0]-event.genB_phi[1])) if event.ngenB>=2 else 0,
      binning=[40,0,3.5],
    ))

    plots.append(Plot( name = 'mt_b_12'+postfix,
      texX = 'm_{t, b12}', texY = 'Number of Events / 20 GeV',
      attribute = lambda event, sample: sqrt(2*event.genB_pt[0]*event.genB_pt[1]*(cosh(event.genB_eta[0]-event.genB_eta[1])-cos(event.genB_phi[0]-event.genB_phi[1]))) if len(event.genB_eta)>=2 else 0,
      binning=[40,0,2500],
    ))
    
    plots.append(Plot( name = 'min_dR_bb'+postfix,
      texX = '\Delta R_{b,b}', texY = 'Number of Events / 20 GeV',
      attribute = lambda event, sample: event.min_dR_bb,
      binning=[40,0,3.5],
    ))
    
    
    
plots.append(Plot( name = "j0_pt"+postfix,
  texX = 'p_{T}(j_{0}) (GeV)', texY = 'Number of Events',
  attribute = lambda event, sample: event.jets[0]['pt'] if len(event.jets)>0 else float('nan'),
  binning=[600/20,0,600],
))

plots.append(Plot( name = "j1_pt"+postfix,
  texX = 'p_{T}(j_{1}) (GeV)', texY = 'Number of Events',
  attribute = lambda event, sample: event.jets[1]['pt'] if len(event.jets)>1 else float('nan'),
  binning=[600/20,0,600],
))

plots.append(Plot( name = "j2_pt"+postfix,
  texX = 'p_{T}(j_{2}) (GeV)', texY = 'Number of Events',
  attribute = lambda event, sample: event.jets[2]['pt'] if len(event.jets)>2 else float('nan'),
  binning=[600/20,0,600],
))

plots.append(Plot( name = "j0_eta"+postfix,
  texX = '#eta(j_{0}) (GeV)', texY = 'Number of Events',
  attribute = lambda event, sample: event.jets[0]['eta'] if len(event.jets)>0 else float('nan'),
  binning=[30,-3,3],
))

plots.append(Plot( name = "j1_eta"+postfix,
  texX = '#eta(j_{1}) (GeV)', texY = 'Number of Events',
  attribute = lambda event, sample: event.jets[1]['eta'] if len(event.jets)>1 else float('nan'),
  binning=[30,-3,3],
))

plots.append(Plot( name = "j2_eta"+postfix,
  texX = '#eta(j_{2}) (GeV)', texY = 'Number of Events',
  attribute = lambda event, sample: event.jets[2]['eta'] if len(event.jets)>2 else float('nan'),
  binning=[30,-3,3],
))

plots.append(Plot( name = "bj0_pt"+postfix,
  texX = 'p_{T}(b-jet_{0}) (GeV)', texY = 'Number of Events',
  attribute = lambda event, sample: event.trueBjets[0]['pt'] if len(event.trueBjets)>0 else float('nan'),
  binning=[600/20,0,600],
))

plots.append(Plot( name = "bj1_pt"+postfix,
  texX = 'p_{T}(b-jet_{1}) (GeV)', texY = 'Number of Events',
  attribute = lambda event, sample: event.trueBjets[1]['pt'] if len(event.trueBjets)>1 else float('nan'),
  binning=[600/20,0,600],
))

plots.append(Plot( name = "bj0_eta"+postfix,
  texX = '#eta(b-jet_{0}) (GeV)', texY = 'Number of Events',
  attribute = lambda event, sample: event.trueBjets[0]['eta'] if len(event.trueBjets)>0 else float('nan'),
  binning=[30,-3,3],
))

plots.append(Plot( name = "bj1_eta"+postfix,
  texX = '#eta(b-jet_{1}) (GeV)', texY = 'Number of Events',
  attribute = lambda event, sample: event.trueBjets[1]['eta'] if len(event.trueBjets)>1 else float('nan'),
  binning=[30,-3,3],
))

plots.append(Plot( name = 'Met_pt'+postfix,
  texX = 'E_{T}^{miss} (GeV)', texY = 'Number of Events / 20 GeV',
  attribute = lambda event, sample: event.genMet_pt,
  binning=[400/20,0,400],
))

plots.append(Plot( name = 'nJet'+postfix,
  texX = 'jet multiplicity', texY = 'Number of Events / 20 GeV',
  attribute = lambda event, sample: len(event.jets),
  binning=[8,0,8],
))

plots.append(Plot( name = 'ht'+postfix,
  texX = 'H_{T}', texY = 'Number of Events / 20 GeV',
  attribute = lambda event, sample: sum( [j['pt'] for j in event.jets]),
  binning=[40,0,2500],
))

plots.append(Plot( name = 'htb'+postfix,
  texX = 'H_{T,b-jets}', texY = 'Number of Events / 20 GeV',
  attribute = lambda event, sample: sum( [j['pt'] for j in event.trueBjets]),
  binning=[40,0,2500],
))

plots.append(Plot( name = 'ht_ratio'+postfix,
  texX = '\Delta H_{T}', texY = 'Number of Events / 20 GeV',
  attribute = lambda event, sample: sum( [j['pt'] for j in event.jets[:4]])/ sum( [j['pt'] for j in event.jets ]) if len(event.jets)>=4 else 1,
  binning=[40,0,1],
))

plots.append(Plot( name = 'dEtaj_12'+postfix,
  texX = '\Delta\eta_{j}', texY = 'Number of Events / 20 GeV',
  attribute = lambda event, sample: abs(event.jets[0]['eta'] - event.jets[1]['eta']) if len(event.jets)>=2 else -10,
  binning=[40,0,6],
))

plots.append(Plot( name = 'dPhij_12'+postfix,
  texX = '\Delta\phi_{j}', texY = 'Number of Events / 20 GeV',
  attribute = lambda event, sample: acos(cos(event.jets[0]['phi']-event.jets[1]['phi'])) if len(event.jets)>=2 else 0,
  binning=[40,0,3.5],
))

plots.append(Plot( name = 'min_dR_jj'+postfix,
  texX = '\Delta R_{j,j}', texY = 'Number of Events / 20 GeV',
  attribute = lambda event, sample: event.min_dR_jj,
  binning=[40,0,3.5],
))

plots.append(Plot( name = 'min_dR_bjbj'+postfix,
  texX = '\Delta R_{b-jet,b-jet}', texY = 'Number of Events / 20 GeV',
  attribute = lambda event, sample: event.min_dR_bjbj,
  binning=[40,0,3.5],
))

plots.append(Plot( name = 'mt_j_12'+postfix,
  texX = 'm_{t, j12}', texY = 'Number of Events / 20 GeV',
  attribute = lambda event, sample: sqrt(2*event.jets[0]['pt']*event.jets[1]['pt']*(cosh(event.jets[0]['eta']-event.jets[1]['eta'])-cos(event.jets[0]['phi']-event.jets[1]['phi']))) if len(event.jets)>=2 else 0,
  binning=[40,0,2500],
))

plots.append(Plot( name = 'mt_bj_12'+postfix,
  texX = 'm_{t, b-jet12}', texY = 'Number of Events / 20 GeV',
  attribute = lambda event, sample: sqrt(2*event.trueBjets[0]['pt']*event.trueBjets[1]['pt']*(cosh(event.trueBjets[0]['eta']-event.trueBjets[1]['eta'])-cos(event.trueBjets[0]['phi']-event.trueBjets[1]['phi']))) if len(event.trueBjets)>=2 else 0,
  binning=[40,0,2500],
))


    


# Text on the plots
def drawObjects( hasData = False ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    lines = [
      (0.15, 0.95, 'CMS Preliminary' if hasData else "CMS Simulation"), 
      #(0.45, 0.95, 'L=%3.1f fb{}^{-1} (13 TeV) Scale %3.2f'% ( lumi_scale, dataMCScale ) ) if plotData else (0.45, 0.95, 'L=%3.1f fb{}^{-1} (13 TeV)' % lumi_scale)
    ]
    return [tex.DrawLatex(*l) for l in lines] 

# draw function for plots
def drawPlots(plots, subDirectory=''):
  for log in [False, True]:
    plot_directory_ = os.path.join(plot_directory, args.plot_directory, args.sample, subDirectory)
    plot_directory_ = os.path.join(plot_directory_, "log") if log else os.path.join(plot_directory_, "lin")
    for plot in plots:
      if not max(l[0].GetMaximum() for l in plot.histos): continue # Empty plot

      len_FI = len(plot.fisher_plots) if hasattr(plot, "fisher_plots") else 0
      plotting.draw(plot,
	    plot_directory = plot_directory_,
	    ratio = {'histos':[(i,0) for i in range(1,len(plot.histos)-len_FI)], 'yRange':(0.1,1.9)},
	    logX = False, logY = log, sorting = False,
	    yRange = (1.0e-03,"auto") if log else "auto",
	    scaling = {},
        legend =  ( (0.17,0.9-0.05*sum(map(len, plot.histos))/2,1.,0.9), 2), 
        drawObjects = drawObjects( ),
        copyIndexPHP = True,
      )

plotting.fill(plots+fisher_plots, read_variables = read_variables, sequence = sequence, max_events = -1 if args.small else -1)

for plot in plots:
    for i in range (len(plot.histos)):
        # dress up
        #print i
        plot.histos[i][0].legendText = params[i]['legendText'] 
        #print params[i]['legendText'] 
        plot.histos[i][0].style = params[i]['style']

    # calculate & add FI histo
    if hasattr(plot, "fisher_plots" ):
        for fisher_plot in plot.fisher_plots:

            # make empty histo
            FI = plot.histos[0][0].Clone()
            FI.Reset()

            # calculate FI in each bin
            for i_bin in range(1, FI.GetNbinsX()+1):
                yields = {'lambda_%i'%coeff : fisher_plot.histos[i_coeff][0].GetBinContent(i_bin) for i_coeff, coeff in enumerate(fisher_plot.coefficients)}
                try:
                    FI.SetBinContent( i_bin,  eval(fisher_plot.formula.format(**yields)) )
                except ZeroDivisionError:
                    pass

            # dress up
            FI.legendText = fisher_plot.legendText
            FI.style = styles.lineStyle( fisher_plot.color )

            # scale the FI & indicate log(I) in the plot
            if FI.Integral()>0:
                FI.legendText += "(%3.2f)" % log(FI.Integral(),10)
                FI.Scale(plot.histos[0][0].Integral()/FI.Integral())

            # add the FI histos back to the plot and fake the stack so that the draw command does not get confused
            plot.histos.append( [FI] )
            stack.append( [sample] )

drawPlots(plots, subDirectory = subDirectory)

logger.info( "Done with prefix %s and selectionString %s", args.selection, cutInterpreter.cutString(args.selection) )
