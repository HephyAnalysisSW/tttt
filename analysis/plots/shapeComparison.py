''' Analysis script for standard plots
'''

#Standard imports and batch mode

import ROOT
#ROOT.TH1.AddDirectory(False)

import os
import itertools
import copy
import array
import operator
import numpy as np
from math                                import sqrt, cos, sin, pi, atan2, cosh

#Standard imports and batch mode

from RootTools.core.standard             import *

#tttt tools import

import tttt.Tools.user                   as user
from tttt.Tools.cutInterpreter           import cutInterpreter
from tttt.Tools.objectSelection          import lepString, cbEleIdFlagGetter, vidNestedWPBitMapNamingList, isBJet
from tttt.Tools.helpers                  import getObjDict

#Analysis Tools imports

from Analysis.Tools.helpers              import deltaPhi, deltaR
from Analysis.Tools.puProfileCache       import *
from Analysis.Tools.puReweighting        import getReweightingFunction
import Analysis.Tools.syncer

#Argument Parser

import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',       action='store',      default='INFO', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--small',                             action='store_true', help='Run only on a small subset of the data?')
#argParser.add_argument('--sorting',                           action='store', default=None, choices=[None, "forDYMB"],  help='Sort histos?', )
argParser.add_argument('--plot_directory', action='store', default='4t')
argParser.add_argument('--selection',      action='store', default='trg-dilep-OS-minDLmass20-onZ1-lepVeto2-njet4to5-btag1to2-ht500')
argParser.add_argument('--era',           action='store', default='RunII', help= 'Plot year split or inclusively')
argParser.add_argument('--DY',            action='store', default='ht', help= 'what kind of DY do you want?')
args = argParser.parse_args()

# DIrectory naming parser options

if args.small: args.plot_directory += "_small"

plot_directory = os.path.join( user.plot_directory, args.plot_directory, "shapeComparison" )
#Logger
import tttt.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

#Simulated samples

from tttt.samples.nano_private_UL20_RunII_postProcessed_dilep import *

if args.era not in ["Run2016_preVFP", "Run2016", "Run2017", "Run2018", "RunII"]:
    raise Exception("Era %s not known"%args.era)
if args.era == 'Run2016_preVFP':
        from tttt.samples.nano_mc_private_UL20_Summer16_preVFP_postProcessed_dilep import *
if args.era == 'Run2016':
        from tttt.samples.nano_mc_private_UL20_Summer16_postProcessed_dilep import *
if args.era == 'Run2017':
        from tttt.samples.nano_mc_private_UL20_Fall17_postProcessed_dilep import *
if args.era == 'Run2018':
        from tttt.samples.nano_mc_private_UL20_Autumn18_postProcessed_dilep import *
if args.era == 'RunII':
        from tttt.samples.nano_private_UL20_RunII_postProcessed_dilep import *

#Merge simulated background samples

if args.DY == 'ht':
    sample = DY
elif args.DY == 'inclusive':
    sample = DY_inclusive

sample.files = filter( lambda f: "UL2018" in f and "_M50_" in f , sample.files)

if args.small:
    sample.normalization = 1.
    sample.files = filter( lambda f: "600to800" in f and "_M50_" in f , sample.files)
    #sample.files = sample.files[:1] 

#Let's make a function that provides string-based lepton selection
mu_string  = lepString('mu','VL')
ele_string = lepString('ele','VL')
def getLeptonSelection( mode ):
    if   mode=="mumu": return "Sum$({mu_string})==2&&Sum$({ele_string})==0".format(mu_string=mu_string,ele_string=ele_string)
    elif mode=="mue":  return "Sum$({mu_string})==1&&Sum$({ele_string})==1".format(mu_string=mu_string,ele_string=ele_string)
    elif mode=="ee":   return "Sum$({mu_string})==0&&Sum$({ele_string})==2".format(mu_string=mu_string,ele_string=ele_string)
    elif mode=='all':    return "Sum$({mu_string})+Sum$({ele_string})==2".format(mu_string=mu_string,ele_string=ele_string)

selectionString = "("+getLeptonSelection('all')+")&&("+cutInterpreter.cutString(args.selection)+")"

sample.setSelectionString( selectionString )

def ISRJetPtString(pt=40):
    px = "Sum$(JetGood_pt*cos(JetGood_phi)*(JetGood_pt>{thr}))".format(thr=pt)
    py = "Sum$(JetGood_pt*sin(JetGood_phi)*(JetGood_pt>{thr}))".format(thr=pt)
    return "sqrt({px}**2+{py}**2)".format(px=px, py=py)

isrJetPtBins = ( (0, 200), (200,400), (400, 600), (600,800), (800,1000), (1000, -1 ))

isr = ISRJetPtString()
hist_ht = {}
for i_bin, (lower, higher) in enumerate(isrJetPtBins):
    selection = []
    if lower>0:
        selection.append( "{isr}>={lower}".format(isr=isr, lower=lower) )
    if higher>0:
        selection.append( "{isr}<{higher}".format(isr=isr, higher=higher) )

    hist_ht[(lower, higher)] = sample.get1DHistoFromDraw('ht', [40, 500, 2500], selectionString = "&&".join(selection), weightString="weight") 
    hist_ht[(lower, higher)].legendText = str(lower)+"\leq p_{T}(ISR)" + ("<"+str(higher) if higher>0 else "") 
    hist_ht[(lower, higher)].style = styles.lineStyle( ROOT.kMagenta-10+i_bin )

p = Plot.fromHisto( "ht", histos = [[hist_ht[isrJetPtBin]] for isrJetPtBin in isrJetPtBins ], texX = "H_{T} (GeV)") 

plotting.draw( p, plot_directory = plot_directory, legend = ([0.15,0.75, 0.85, 0.90], 2), yRange=(0.02, "auto")) 


htBins = ( (500, 700), (700,900), (1000,1100), (1100, 1500 ), (1500, -1))

hist_isr = {}
for i_bin, (lower, higher) in enumerate(htBins):
    selection = []
    if lower>0:
        selection.append( "ht>={lower}".format(lower=lower) )
    if higher>0:
        selection.append( "ht<{higher}".format(higher=higher) )

    hist_isr[(lower, higher)] = sample.get1DHistoFromDraw(isr, [40, 0, 1500], selectionString = "&&".join(selection), weightString="weight") 
    hist_isr[(lower, higher)].legendText = str(lower)+"\leq H_{T}" + ("<"+str(higher) if higher>0 else "") 
    hist_isr[(lower, higher)].style = styles.lineStyle( ROOT.kMagenta-10+i_bin )

p = Plot.fromHisto( "ISRJetPt", histos = [[hist_isr[htBin]] for htBin in htBins ], texX = "p_{T}(ISR) (GeV)") 

plotting.draw( p, plot_directory = plot_directory, legend = ([0.15,0.75, 0.85, 0.90], 2), yRange=(0.02, "auto")) 
