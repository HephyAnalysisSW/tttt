#Standard imports
import ROOT
import os
from math import sqrt, cos, pi

import Analysis.Tools.syncer        as syncer

from tttt.Tools.user                import plot_directory
from tttt.Tools.genObjectSelection  import isGoodGenJet
from tttt.Tools.helpers             import deltaPhi, getCollection

# argParser
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--plot_directory', action='store', nargs='?', default="v0", help="version directory" )
argParser.add_argument('--logLevel', action='store', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], default='INFO', help="Log level for logging" )
argParser.add_argument('--small',                                   action='store_true',     help='Run only on a small subset of the data?')
argParser.add_argument('--plotPath', action='store', nargs='?', default="/groups/hephy/cms/cristina.giordano/www/GenValidation/plots", help="where to write the plots" )
args = argParser.parse_args()


plot_directory_ = os.path.join(args.plotPath, args.plot_directory)


# RootTools
from RootTools.core.standard import *

logger = get_logger(args.logLevel, logFile = None)
selectionString = "ngenJet>0"

#make samples. Samples are statisticall compatible.
s0 = Sample.fromFiles("TTTT_central", "/scratch-cbe/users/cristina.giordano/tttt/nanoTuples/genPlots_v1/TTTT/TTTT.root", selectionString = selectionString)

from tttt.samples.GEN_EFT_postProcessed import *
s1 = TTTT_MS

if args.small:
        #sample.reduceFiles( factor = 30 )
        args.plot_directory += "_small"
        s0.reduceFiles( factor = 1000 )
        s1.reduceFiles( to = 1 )

# styles are functions to be executed on the histogram
s0.style = styles.lineStyle( color = ROOT.kBlue )
s1.style = styles.lineStyle( color = ROOT.kRed )
#print(s0.normalization)
#print(s1.normalization)



# scaling a sample
# Let's scale s2 up by a factor of 2 and compare it to s0+s1


s1.scale = 137
s0.scale = 0.008213
# Define the stack.
# The whole point is that a stack is a stack of samples, not plots. Plots take stacks as arguments.
stack = Stack( [ s0 ],[ s1] )

# Let's use a trivial weight. All functions will
plot_weight   = lambda event, sample : 1

# Two selection strings
#selectionString = "nJetGood>0"
#selectionString_2 = "nJet>1"

# Variables to be read from the tree
read_variables = []
read_variables += [
     #"Pair[%s]"%(",".join(pairVars)),
     #"evt/l", "run/I", "lumi/I",
     "ngenJet/I",#, "Jet_eta/F", "Jet_phi/F",
     "genJet[pt/F,eta/F,phi/F]",# "genJet_eta/F"#, "genJet_phi/F"#, "Z_mass/F", "Z_l_pdgId/I",
    ]

#def ht(event, sample):

#    genJets = isGoodGenJet(event)

#Sequence to be executed
sequence = []

def makeJets(event, sample):

    event.jets = getCollection( event, 'genJet', ['pt', 'eta', 'phi'], 'ngenJet' )
    event.jets = list(filter( lambda j:isGoodGenJet( j ), event.jets))
    event.jets = sorted( event.jets, key=lambda k: -k['pt'] )


sequence.append(makeJets)


#Plot.setDefaults(stack =  stack, weight = plot_weight, addOverFlowBin=None)

plots = []

# plots.append(Plot(\
#     name = "nGenJet", # Name is not needed. If not provided, variable.name is used as filename instead.
#     stack = stack,
#     # met_pt is in the chain
#     attribute = TreeVariable.fromString( "ngenJet/I" ),
#     binning = [20,0,20],
#     selectionString = selectionString,
#     weight = plot_weight
# ))
# plots.append(Plot(\
#     name = "GenJet0_pt", # Name is not needed. If not provided, variable.name is used as filename instead.
#     stack = stack,
#     attribute = lambda event, sample: event.jets[0]['pt'] if len(event.jets)>0 else float('nan'),
#     binning = [20,0,20],
#     selectionString = selectionString,
#     weight = plot_weight
# ))
# plots.append(Plot(\
#     name = "GenJet0_eta", # Name is not needed. If not provided, variable.name is used as filename instead.
#     stack = stack,
#     attribute = lambda event, sample: event.jets[0]['eta'] if len(event.jets)>0 else float('nan'),
#     binning = [30,-2.4,2.4],
#     selectionString = selectionString,
#     weight = plot_weight
# ))
plots.append(Plot(\
   name = "GenJet0_phi", # Name is not needed. If not provided, variable.name is used as filename instead.
   stack = stack,
   attribute = lambda event, sample: event.jets[0]['phi'] if len(event.jets)>0 else float('nan'),
   binning = [30,-pi,pi],
   selectionString = selectionString,
    weight = plot_weight
))
plots.append(Plot(\
   name = "ht", # Name is not needed. If not provided, variable.name is used as filename instead.
   stack = stack,
   attribute = lambda event, sample: sum([j['pt'] for j in event.jets]),
   binning = [40, 0, 2500],
   selectionString = selectionString,
   weight = plot_weight
))




plotting.fill(plots, read_variables = read_variables, sequence = sequence)

if not os.path.exists( plot_directory_ ): os.makedirs( plot_directory_ )
for plot in plots:
    plotting.draw(plot, plot_directory = plot_directory_,
        ratio = {'yRange':(0.1,1.9)}, # Add a default ratio from the first two elements in the stack
        logX = False, logY = True,
# inside each stack member, sort wrt. histo.Integral. Useful when the stack looks like [ [mc1,mc2,mc3,...], [data]]
        sorting = True,
# Adjust y Range such that all bins are within canvas and that nothing is shadowed by the legend. Alternatively (yLow, yHigh)
        yRange = "auto",
# Make legend. Alternatively provide (x0,y0,x1,y1)
        legend = "auto"
        )
# Configuration of the ratio
# ratio = {'num':1, 'den':0, 'logY':False, 'style':None, 'texY': 'Data / MC', 'yRange': (0.5, 1.5)}
