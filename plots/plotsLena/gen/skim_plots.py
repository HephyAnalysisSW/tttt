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

params =  [ {'legendText':'SM',  'color':ROOT.kBlack, 'WC':{}} ] 
for i in range (len(args.WC)):
    params += [ {'legendText':'%s %3.2f'%(args.WC[i], wc), 'color':colors[i]+(i_wc*10),  'WC':{args.WC[i]:wc} } for i_wc, wc in enumerate(args.WCval)]
for i_param, param in enumerate(params):
    params[i_param]['sample'] = sample
    params[i_param]['style']  = styles.lineStyle( params[i_param]['color'] )
params[0]['style']  = styles.lineStyle( params[0]['color'], 2 )
stack = Stack(*[ [ param['sample'] ] for param in params ] )
weight= [ [ w.get_weight_func(**param['WC']) ] for param in params ]

# Read variables and sequences
read_variables = [
    "genMet_pt/F", "genMet_phi/F", 
    "ngenJet/I", "genJet[pt/F,eta/F,phi/F,matchBParton/I]", 
    "ngenLep/I", "genLep[pt/F,eta/F,phi/F,pdgId/I,mother_pdgId/I]", 
    "ngenTop/I", "genTop[pt/F,eta/F,phi/F,mass/F]",
    "ngenB/I", "genB[pt/F,eta/F,phi/F,mass/F,fromTop/I]",
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
        sample.reduceFiles( to = 1 )


def addTLorentzVector( p_dict , name ):
    ''' add a TLorentz 4D Vector for further calculations
    '''
    v = ROOT.TLorentzVector(0,0,0,0)
    v.SetPtEtaPhiM( p_dict['pt'], p_dict['eta'],p_dict['phi'],p_dict['mass'] )
    p_dict[name] = v
    
    
    
#sequence functions
sequence = []

def addInvariantMass ( event, sample ):
    event.tops = getCollection( event, 'genTop', ['pt', 'eta', 'phi','mass'], 'ngenTop' )
    event.bs   = getCollection( event, 'genB', ['pt', 'eta', 'phi', 'mass', 'fromTop'], 'ngenB' )
    #sort
    event.tops = sorted( event.tops, key=lambda k: -k['pt'] )
    event.bs   = sorted( event.bs, key=lambda k: -k['pt'] )
    
    for p in event.tops:
        addTLorentzVector( p, 'vec4D' )
     
    for p in event.bs:
        addTLorentzVector( p, 'vec4D' ) 
    
    if (args.sample == 'TTbb_MS'):
        event.extrabs   = list( filter( lambda j: not j['fromTop'], event.bs ) ) 
        event.bsfromt   = list( filter( lambda j: j['fromTop'], event.bs ) ) 
        
    if (args.sample=='TTTT_MS'):
        event.m_tttt       = abs((event.tops[0]['vec4D'] + event.tops[1]['vec4D'] + event.tops[2]['vec4D'] + event.tops[3]['vec4D']).M())    
        event.m_ttbb       = abs((event.tops[0]['vec4D'] + event.tops[1]['vec4D'] + event.bs[0]['vec4D'] + event.bs[1]['vec4D']).M())    
        event.m_tt         = abs((event.tops[0]['vec4D']+event.tops[1]['vec4D']).M())   
       
    if (args.sample=='TTbb_MS'):
        event.m_bbbb       = abs((event.extrabs[0]['vec4D']+event.extrabs[1]['vec4D']+event.bsfromt[0]['vec4D']+event.bsfromt[1]['vec4D']).M())    
        event.m_bb_extra   = abs((event.extrabs[0]['vec4D']+event.extrabs[1]['vec4D']).M())  
        event.m_bb_fromt   = abs((event.bsfromt[0]['vec4D']+event.bsfromt[1]['vec4D']).M())  
        event.m_tt         = abs((event.tops[0]['vec4D']+event.tops[1]['vec4D']).M())  
        event.m_ttbb       = abs((event.extrabs[0]['vec4D']+event.extrabs[1]['vec4D']+event.tops[0]['vec4D']+event.tops[1]['vec4D']).M())  
    
sequence.append( addInvariantMass )


        
def makeJets( event, sample ):
    ''' Add a list of filtered all jets to the event
    '''
    # Retrieve & filter
    event.jets = getCollection( event, 'genJet', ['pt', 'eta', 'phi', 'matchBParton'], 'ngenJet' )
    event.jets = list(filter( lambda j:isGoodGenJet( j ), event.jets))
    # sort
    event.jets = sorted( event.jets, key=lambda k: -k['pt'] )

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
    
    if event.ngenTop>=2:
        event.min_dR_tt = min( [deltaR( comb[0], comb[1] ) for comb in itertools.combinations( event.tops, 2)] )
    else:
        event.min_dR_tt = -1   

    if (args.sample == 'TTbb_MS'):
        if len(event.extrabs)>=2:
            event.min_dR_bb_extra = min( [deltaR( comb[0], comb[1] ) for comb in itertools.combinations( event.extrabs[0:2], 2)] )
        else:
            event.min_dR_bb_extra = -1  

sequence.append ( calculatedeltaR ) 

def makeMET( event, sample ):
    ''' Make a MET vector to facilitate further calculations
    '''
    event.MET = {'pt':event.genMet_pt, 'phi':event.genMet_phi}
    #addTransverseVector( event.MET )

sequence.append( makeMET )

def makeLeps( event, sample ):

    # Read leptons, do not yet filter
    event.all_leps = getCollection( event, 'genLep', ['pt', 'eta', 'phi', 'pdgId', 'mother_pdgId'], 'ngenLep' )
    # Add extra vectors
    # for p in event.all_leps:
        # addTransverseVector( p )
        # addTLorentzVector( p )

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


    
# Use some defaults
Plot.setDefaults(stack = stack, weight = weight, addOverFlowBin=None)
  
plots        = []


l = ''.join(args.WC)
if (len(args.WC)>4): l = 'multi'
postfix = '_'+l



# plots.append(Plot( name = "W0_pt"+postfix,
  # texX = 'p_{T}(W_{0}) (GeV)', texY = 'Number of Events',
  # attribute = lambda event, sample: event.genW_pt[0] if event.ngenW>0 else float('nan'),
  # binning=[600/20,0,600],
# ))
 
# plots.append(Plot( name = "W0_eta"+postfix,
  # texX = '#eta(W_{0}) (GeV)', texY = 'Number of Events',
  # attribute = lambda event, sample: event.genW_eta[0] if event.ngenW>0 else float('nan'),
  # binning=[30,-3,3],
# ))

# plots.append(Plot( name = "W1_pt"+postfix,
  # texX = 'p_{T}(W_{1}) (GeV)', texY = 'Number of Events',
  # attribute = lambda event, sample: event.genW_pt[1] if event.ngenW>1 else float('nan'),
  # binning=[600/20,0,600],
# ))

# plots.append(Plot( name = "W1_eta"+postfix,
  # texX = '#eta(W_{1}) (GeV)', texY = 'Number of Events',
  # attribute = lambda event, sample: event.genW_eta[1] if event.ngenW>1 else float('nan'),
  # binning=[30,-3,3],
# ))


# plots.append(Plot( name = "top0_pt"+postfix,
  # texX = 'p_{T}(top_{0}) (GeV)', texY = 'Number of Events',
  # attribute = lambda event, sample: event.genTop_pt[0] if event.ngenTop>0 else float('nan'),
  # binning=[600/20,0,800],
# ))

# plots.append(Plot( name = "top0_eta"+postfix,
  # texX = '#eta(top_{0}) (GeV)', texY = 'Number of Events',
  # attribute = lambda event, sample: event.genTop_eta[0] if event.ngenTop>0 else float('nan'),
  # binning=[30,-5,5],
# ))

# plots.append(Plot( name = "top1_pt"+postfix,
  # texX = 'p_{T}(top_{1}) (GeV)', texY = 'Number of Events',
  # attribute = lambda event, sample: event.genTop_pt[1] if event.ngenTop>1 else float('nan'),
  # binning=[600/20,0,800],
# ))

# plots.append(Plot( name = "top1_eta"+postfix,
  # texX = '#eta(top_{1}) (GeV)', texY = 'Number of Events',
  # attribute = lambda event, sample: event.genTop_eta[1] if event.ngenTop>1 else float('nan'),
  # binning=[30,-5,5],
# ))

# plots.append(Plot( name = "top2_pt"+postfix,
  # texX = 'p_{T}(top_{2}) (GeV)', texY = 'Number of Events',
  # attribute = lambda event, sample: event.genTop_pt[2] if event.ngenTop>2 else float('nan'),
  # binning=[600/20,0,800],
# ))

# plots.append(Plot( name = "top2_eta"+postfix,
  # texX = '#eta(top_{2}) (GeV)', texY = 'Number of Events',
  # attribute = lambda event, sample: event.genTop_eta[2] if event.ngenTop>2 else float('nan'),
  # binning=[30,-5,5],
# ))

# plots.append(Plot( name = "top3_pt"+postfix,
  # texX = 'p_{T}(top_{3}) (GeV)', texY = 'Number of Events',
  # attribute = lambda event, sample: event.genTop_pt[3] if event.ngenTop>3 else float('nan'),
  # binning=[600/20,0,800],
# ))

# plots.append(Plot( name = "top3_eta"+postfix,
  # texX = '#eta(top_{3}) (GeV)', texY = 'Number of Events',
  # attribute = lambda event, sample: event.genTop_eta[3] if event.ngenTop>3 else float('nan'),
  # binning=[30,-5,5],
# ))

# plots.append(Plot( name = "pt_tt"+postfix,
  # texX = 'p_{T}(tt) (GeV)', texY = 'Number of Events',
  # attribute = lambda event, sample: (event.tops[0]['vec4D']+event.tops[1]['vec4D']).Pt() if len(event.tops)>=2 else float('nan'),
  # binning=[600/20,0,1600],
# ))

# plots.append(Plot( name = "eta_tt"+postfix,
  # texX = '\eta(tt) (GeV)', texY = 'Number of Events',
  # attribute = lambda event, sample: (event.tops[0]['vec4D']+event.tops[1]['vec4D']).Eta() if len(event.tops)>=2 else float('nan'),
  # binning=[30,-7,7],
# ))

# plots.append(Plot( name = 'dEta_tt'+postfix,
  # texX = '\Delta\eta_{top}', texY = 'Number of Events / 20 GeV',
  # attribute = lambda event, sample: abs(event.genTop_eta[0] - event.genTop_eta[1]) if event.ngenTop>=2 else float('nan'),
  # binning=[40,0,6],
# ))

# plots.append(Plot( name = 'dPhi_tt'+postfix,
  # texX = '\Delta\phi_{top}', texY = 'Number of Events / 20 GeV',
  # attribute = lambda event, sample: acos(cos(event.genTop_phi[0]-event.genTop_phi[1])) if event.ngenTop>=2 else float('nan'),
  # binning=[40,0,3.5],
# ))

# if (args.sample == 'TTTT_MS'):
    # plots.append(Plot( name = 'm_tt'+postfix,
      # texX = 'm_{tt}', texY = 'Number of Events / 20 GeV',
      # attribute = lambda event, sample: event.m_tt, 
      # binning=[40,0,2500],
    # ))
    
    # plots.append(Plot( name = 'm_tttt'+postfix,
      # texX = 'm_{tttt}', texY = 'Number of Events / 20 GeV',
      # attribute = lambda event, sample: event.m_tttt,
      # binning=[12,500,5000],
    # ))
    
    # plots.append(Plot( name = 'm_ttbb'+postfix,
      # texX = 'm_{ttbb}', texY = 'Number of Events / 20 GeV',
      # attribute = lambda event, sample: event.m_ttbb,
      # binning=[12,300,5000],
    # ))
    
    # plots.append(Plot( name = 'dEta_bb'+postfix,
      # texX = '\Delta\eta_{b}', texY = 'Number of Events / 20 GeV',
      # attribute = lambda event, sample: abs(event.genB_eta[0] - event.genB_eta[1]) if event.ngenB>=2 else float('nan'),
      # binning=[40,0,6],
    # ))

    # plots.append(Plot( name = 'dPhi_bb'+postfix,
      # texX = '\Delta\phi_{b}', texY = 'Number of Events / 20 GeV',
      # attribute = lambda event, sample: acos(cos(event.genB_phi[0]-event.genB_phi[1])) if event.ngenB>=2 else 0,
      # binning=[40,0,3.5],
    # ))

    
if (args.sample == 'TTbb_MS'):      
    # plots.append(Plot( name = 'm_tt'+postfix,
      # texX = 'm_{tt}', texY = 'Number of Events / 20 GeV',
      # attribute = lambda event, sample: event.m_tt, 
      # binning=[40,0,2500],
    # ))
    
    # plots.append(Plot( name = 'm_bb_from_t'+postfix,
      # texX = 'm_{bb from t}', texY = 'Number of Events / 20 GeV',
      # attribute = lambda event, sample: event.m_bb_fromt, 
      # binning=[40,0,2500],
    # ))
    
    # plots.append(Plot( name = 'm_bb_extra'+postfix,
      # texX = 'm_{bb extra}', texY = 'Number of Events / 20 GeV',
      # attribute = lambda event, sample: event.m_bb_extra, 
      # binning=[40,0,2500],
    # ))
    
    plots.append(Plot( name = 'm_bbbb'+postfix,
      texX = 'm_{bbbb}', texY = 'Number of Events / 20 GeV',
      attribute = lambda event, sample: event.m_bbbb,
      binning=[30,0,2500],
    ))
    
    # plots.append(Plot( name = 'm_ttbb'+postfix,
      # texX = 'm_{ttbb}', texY = 'Number of Events / 20 GeV',
      # attribute = lambda event, sample: event.m_ttbb,
      # binning=[12,300,5000],
    # ))
    
    # plots.append(Plot( name = 'min_dR_bb_extra'+postfix,
      # texX = '\Delta R_{bb extra}', texY = 'Number of Events / 20 GeV',
      # attribute = lambda event, sample: event.min_dR_bb_extra,
      # binning=[40,0,3.5],
    # ))
    
    # plots.append(Plot( name = 'dEta_bb_extra'+postfix,
      # texX = '\Delta\eta_{bb extra}', texY = 'Number of Events / 20 GeV',
      # attribute = lambda event, sample: abs(event.extrabs[0]['eta'] - event.extrabs[1]['eta']) if len(event.extrabs)>=2 else float('nan'),
      # binning=[40,0,6],
    # ))
    
    # plots.append(Plot( name = 'dPhi_bb_extra'+postfix,
      # texX = '\Delta\phi_{b extra}', texY = 'Number of Events / 20 GeV',
      # attribute = lambda event, sample: acos(cos(event.extrabs[0]['phi']-event.extrabs[1]['phi'])) if len(event.extrabs)>=2  else float('nan'),
      # binning=[40,0,3.5],
    # ))
    
    # plots.append(Plot( name = "pt_bb_extra"+postfix,
      # texX = 'p_{T}(bb extra) (GeV)', texY = 'Number of Events',
      # attribute = lambda event, sample: (event.extrabs[0]['vec4D']+event.extrabs[1]['vec4D']).Pt() if len(event.extrabs)>=2 else float('nan'),
      # binning=[600/20,0,1600],
    # ))

    # plots.append(Plot( name = "eta_bb_extra"+postfix,
      # texX = '\eta(bb extra) (GeV)', texY = 'Number of Events',
      # attribute = lambda event, sample: (event.extrabs[0]['vec4D']+event.extrabs[1]['vec4D']).Eta() if len(event.extrabs)>=2 else float('nan'),
      # binning=[30,-7,7],
    # ))

    
    
# plots.append(Plot( name = 'min_dR_tt'+postfix,
  # texX = '\Delta R_{t,t}', texY = 'Number of Events / 20 GeV',
  # attribute = lambda event, sample: event.min_dR_tt,
  # binning=[40,0,3.5],
# ))

# plots.append(Plot( name = "b0_pt"+postfix,
  # texX = 'p_{T}(b_{0}) (GeV)', texY = 'Number of Events',
  # attribute = lambda event, sample: event.genB_pt[0] if event.ngenB>0 else float('nan'),
  # binning=[600/20,0,600],
# ))

# plots.append(Plot( name = "b0_eta"+postfix,
  # texX = '#eta(b_{0}) (GeV)', texY = 'Number of Events',
  # attribute = lambda event, sample: event.genB_eta[0] if event.ngenB>0 else float('nan'),
  # binning=[30,-5,5],
# ))

# plots.append(Plot( name = "b1_pt"+postfix,
  # texX = 'p_{T}(b_{1}) (GeV)', texY = 'Number of Events',
  # attribute = lambda event, sample: event.genB_pt[1] if event.ngenB>1 else float('nan'),
  # binning=[600/20,0,600],
# ))

# plots.append(Plot( name = "b1_eta"+postfix,
  # texX = '#eta(b_{1}) (GeV)', texY = 'Number of Events',
  # attribute = lambda event, sample: event.genB_eta[1] if event.ngenB>1 else float('nan'),
  # binning=[30,-5,5],
# ))

# plots.append(Plot( name = "j0_pt"+postfix,
  # texX = 'p_{T}(j_{0}) (GeV)', texY = 'Number of Events',
  # attribute = lambda event, sample: event.jets[0]['pt'] if len(event.jets)>0 else float('nan'),
  # binning=[600/20,0,600],
# ))

# plots.append(Plot( name = "j1_pt"+postfix,
  # texX = 'p_{T}(j_{1}) (GeV)', texY = 'Number of Events',
  # attribute = lambda event, sample: event.jets[1]['pt'] if len(event.jets)>1 else float('nan'),
  # binning=[600/20,0,600],
# ))

# plots.append(Plot( name = "j2_pt"+postfix,
  # texX = 'p_{T}(j_{2}) (GeV)', texY = 'Number of Events',
  # attribute = lambda event, sample: event.jets[2]['pt'] if len(event.jets)>2 else float('nan'),
  # binning=[600/20,0,600],
# ))

# plots.append(Plot( name = "j0_eta"+postfix,
  # texX = '#eta(j_{0}) (GeV)', texY = 'Number of Events',
  # attribute = lambda event, sample: event.jets[0]['eta'] if len(event.jets)>0 else float('nan'),
  # binning=[30,-3,3],
# ))

# plots.append(Plot( name = "j1_eta"+postfix,
  # texX = '#eta(j_{1}) (GeV)', texY = 'Number of Events',
  # attribute = lambda event, sample: event.jets[1]['eta'] if len(event.jets)>1 else float('nan'),
  # binning=[30,-3,3],
# ))

# plots.append(Plot( name = "j2_eta"+postfix,
  # texX = '#eta(j_{2}) (GeV)', texY = 'Number of Events',
  # attribute = lambda event, sample: event.jets[2]['eta'] if len(event.jets)>2 else float('nan'),
  # binning=[30,-3,3],
# ))

# plots.append(Plot( name = "bj0_pt"+postfix,
  # texX = 'p_{T}(b-jet_{0}) (GeV)', texY = 'Number of Events',
  # attribute = lambda event, sample: event.trueBjets[0]['pt'] if len(event.trueBjets)>0 else float('nan'),
  # binning=[600/20,0,600],
# ))

# plots.append(Plot( name = "bj1_pt"+postfix,
  # texX = 'p_{T}(b-jet_{1}) (GeV)', texY = 'Number of Events',
  # attribute = lambda event, sample: event.trueBjets[1]['pt'] if len(event.trueBjets)>1 else float('nan'),
  # binning=[600/20,0,600],
# ))

# plots.append(Plot( name = "bj0_eta"+postfix,
  # texX = '#eta(b-jet_{0}) (GeV)', texY = 'Number of Events',
  # attribute = lambda event, sample: event.trueBjets[0]['eta'] if len(event.trueBjets)>0 else float('nan'),
  # binning=[30,-3,3],
# ))

# plots.append(Plot( name = "bj1_eta"+postfix,
  # texX = '#eta(b-jet_{1}) (GeV)', texY = 'Number of Events',
  # attribute = lambda event, sample: event.trueBjets[1]['eta'] if len(event.trueBjets)>1 else float('nan'),
  # binning=[30,-3,3],
# ))

# plots.append(Plot( name = 'Met_pt'+postfix,
  # texX = 'E_{T}^{miss} (GeV)', texY = 'Number of Events / 20 GeV',
  # attribute = lambda event, sample: event.genMet_pt,
  # binning=[400/20,0,400],
# ))

# plots.append(Plot( name = 'nJet'+postfix,
  # texX = 'jet multiplicity', texY = 'Number of Events / 20 GeV',
  # attribute = lambda event, sample: len(event.jets),
  # binning=[8,0,8],
# ))

plots.append(Plot( name = 'ht'+postfix,
  texX = 'H_{T}', texY = 'Number of Events / 20 GeV',
  attribute = lambda event, sample: sum( [j['pt'] for j in event.jets]),
  binning=[30,0,2500],
))

# plots.append(Plot( name = 'htb'+postfix,
  # texX = 'H_{T,b-jets}', texY = 'Number of Events / 20 GeV',
  # attribute = lambda event, sample: sum( [j['pt'] for j in event.trueBjets]),
  # binning=[40,0,2500],
# ))

# plots.append(Plot( name = 'ht_ratio'+postfix,
  # texX = '\Delta H_{T}', texY = 'Number of Events / 20 GeV',
  # attribute = lambda event, sample: sum( [j['pt'] for j in event.jets[:4]])/ sum( [j['pt'] for j in event.jets ]) if len(event.jets)>=4 else float('nan'),
  # binning=[40,0,1],
# ))

# plots.append(Plot( name = 'dEta_jj'+postfix,
  # texX = '\Delta\eta_{j}', texY = 'Number of Events / 20 GeV',
  # attribute = lambda event, sample: abs(event.jets[0]['eta'] - event.jets[1]['eta']) if len(event.jets)>=2 else float('nan'),
  # binning=[40,0,6],
# ))

# plots.append(Plot( name = 'dPhi_jj'+postfix,
  # texX = '\Delta\phi_{j}', texY = 'Number of Events / 20 GeV',
  # attribute = lambda event, sample: acos(cos(event.jets[0]['phi']-event.jets[1]['phi'])) if len(event.jets)>=2 else float('nan'),
  # binning=[40,0,3.5],
# ))

# plots.append(Plot( name = 'min_dR_jj'+postfix,
  # texX = '\Delta R_{jj}', texY = 'Number of Events / 20 GeV',
  # attribute = lambda event, sample: event.min_dR_jj,
  # binning=[40,0,3.5],
# ))

# plots.append(Plot( name = 'min_dR_bjbj'+postfix,
  # texX = '\Delta R_{b-jet,b-jet}', texY = 'Number of Events / 20 GeV',
  # attribute = lambda event, sample: event.min_dR_bjbj,
  # binning=[40,0,3.5],
# ))

# plots.append(Plot( name = 'm_jj'+postfix,
  # texX = 'm_{jj}', texY = 'Number of Events / 20 GeV',
  # attribute = lambda event, sample: sqrt(2*event.jets[0]['pt']*event.jets[1]['pt']*(cosh(event.jets[0]['eta']-event.jets[1]['eta'])-cos(event.jets[0]['phi']-event.jets[1]['phi']))) if len(event.jets)>=2 else float('nan'),
  # binning=[40,0,2500],
# ))

# plots.append(Plot( name = 'm_bjbj'+postfix,
  # texX = 'm_{b-jet b-jet}', texY = 'Number of Events / 20 GeV',
  # attribute = lambda event, sample: sqrt(2*event.trueBjets[0]['pt']*event.trueBjets[1]['pt']*(cosh(event.trueBjets[0]['eta']-event.trueBjets[1]['eta'])-cos(event.trueBjets[0]['phi']-event.trueBjets[1]['phi']))) if len(event.trueBjets)>=2 else float('nan'),
  # binning=[40,0,2500],
# ))


    


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
	    yRange = (1.0e-03,"auto") if log else (0,"auto"),
	    scaling = {1:0, 2:0},
        legend =  ( (0.17,0.9-0.05*sum(map(len, plot.histos))/2,1.,0.9), 2), 
        drawObjects = drawObjects( ),
        copyIndexPHP = True,
      )

plotting.fill(plots, read_variables = read_variables, sequence = sequence, max_events = -1 if args.small else -1)

for plot in plots:
    for i in range (len(plot.histos)):
        # dress up
        plot.histos[i][0].legendText = params[i]['legendText']  
        plot.histos[i][0].style = params[i]['style']

   

drawPlots(plots, subDirectory = subDirectory)

logger.info( "Done with prefix %s and selectionString %s", args.selection, cutInterpreter.cutString(args.selection) )
