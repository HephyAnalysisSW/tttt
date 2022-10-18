#!/usr/bin/env python
''' simple analysis script 
'''
#
# Standard imports and batch mode
#
import os
import ROOT
ROOT.gROOT.SetBatch(True)
from math import sqrt, cos, sin, pi, cosh, sinh
from RootTools.core.standard import *
import numpy as np
# StopsDilepton
from tttt.Tools.user            import plot_directory
from tttt.Tools.objectSelection import getGoodMuons

#import Analysis.Tools.syncer as syncer

#
# Arguments
# 
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',       action='store',      default='INFO',      nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--plot_directory', action='store',      default='FourMuonInvariantMass')
argParser.add_argument('--small',       action='store_true',                                                                        help="Run the file on a small sample (for test purpose), bool flag set to True if used" )
args = argParser.parse_args()

#
# Logger
#
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

from tttt.samples.nanoTuples_DATA_UL2016preVFP_nanoAODv9_postProcessed import DoubleMuon_Run2016 as DM_16APVv9
from tttt.samples.nanoTuples_DATA_UL2016_nanoAODv9_postProcessed import DoubleMuon_Run2016 as DM_16
from tttt.samples.nanoTuples_DATA_UL2017_nanoAODv9_postProcessed import DoubleMuon_Run2017 as DM_17
from tttt.samples.nanoTuples_DATA_UL2018_nanoAODv9_postProcessed import DoubleMuon_Run2018 as DM_18

# add all data
DoubleMuon  = Sample.combine( "DoubleMuon", [DM_16,  DM_17,  DM_18] )
#     DoubleElectron  = Sample.combine( "DoubleElectron", [DoubleElectron_Run2016, DoubleElectron_Run2017, DoubleElectron_Run2018] )

data_sample = DoubleMuon

# make small
if args.small:
    #data_sample.reduceFiles( factor = 100 )
    data_sample.reduceFiles( to = 1 )

## 4 muon selection
#preSelection = "Sum$(Muon_pt>20&&Muon_mediumPromptId)>=4"
preSelection = "Sum$(Muon_pt>5&&Muon_mediumPromptId)>=4"

#
# Read variables and sequences
#
read_variables = [#"weight/F" , 
                  #"met_phi/F", 
                  "nMuon/I", "Muon[pt/F,eta/F,phi/F,mediumPromptId/O,pdgId/I,pfRelIso03_all/F]", 
#                  "l1_pt/F",  "l2_pt/F",  "l3_pt/F",  "l4_pt/F",
#                  "l1_eta/F", "l2_eta/F", "l3_eta/F", "l4_eta/F",
#                  "l1_phi/F", "l2_phi/F", "l3_phi/F", "l4_phi/F",

]
muVars = ["pt", "eta", "phi", "mediumPromptId", 'pdgId', "pfRelIso03_all"]


def makeM4l(event, sample):

    # Get muons
    muons      = getGoodMuons(event, collVars = muVars, mu_selector = lambda m:m['pt']>10 and m['mediumPromptId'] and m["pfRelIso03_all"]<0.3 )

    event.m4l = float('nan')
    m4l2 = 0
    if len( muons ) ==4:

        # these lines should be commented when running w/o --small
        #for i_m, m in enumerate(muons):
        #    print i_m, "pt {pt} eta {eta} phi {phi} pdgId {pdgId}".format(**m)
        
        # select 2 positive and 2 negative charges
        pdgIds = [ p['pdgId'] for p in muons ]
        if pdgIds.count(+13) == 2 and pdgIds.count(-13)==2:
            for i in range(1,4):
                for j in range( i ):
                    #print "indices i=%i,j=%i: adding %d to m4l2 => yiels %d" % (i,j,m4l2summand,m4l2)
                    m4l2 += 2.*muons[i]['pt']*muons[j]['pt']*( cosh(muons[i]['eta']-muons[j]['eta']) - cos( muons[i]['phi'] - muons[j]['phi'] ))
                    
    event.m4l = sqrt( m4l2 )
    if event.m4l!=0:
        print("%f = invariant mass of 4 muons (2 pos, 2 neg)" % event.m4l)

sequence = [makeM4l]

#
# Text on the plots
#
def drawObjects( ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    lines = [
      (0.15, 0.95, 'CMS Preliminary'), 
    ]
    return [tex.DrawLatex(*l) for l in lines] 

data_sample.setSelectionString(preSelection)
data_sample.style = styles.errorStyle( ROOT.kBlack )

stack = Stack([data_sample])

# Use some defaults
Plot.setDefaults(stack = stack)

plots = []

plots.append(Plot(name = "m4l",
  texX = 'm(4l)', texY = 'Number of Events / 3 GeV',
  attribute = lambda event, sample: event.m4l,
  #binning=[100,105,135],
  binning=[30,20,320],
))

plotting.fill(plots, read_variables = read_variables, sequence=sequence)

for plot in plots:
  plotting.draw(plot, 
      plot_directory = os.path.join(plot_directory, args.plot_directory),
      ratio = None, 
      logX = False, logY = False, sorting = True, 
      yRange = (0.003, "auto"),
      drawObjects = drawObjects( )
  )
