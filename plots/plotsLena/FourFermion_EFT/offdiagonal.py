# plot script for histograms of (wc1,wc2)

from RootTools.core.standard import *
import ROOT
import  uproot  
import  numpy                   as np
from    matplotlib              import pyplot as plt
import  os, shutil
import  argparse
from    WeightInfo              import WeightInfo #have it in my local folder
import  itertools
import  logging
import Analysis.Tools.syncer
import array
import scipy as scipy

def copyIndexPHP( results_dir ):
    index_php = os.path.join( results_dir, 'index.php' )
    shutil.copyfile( os.path.expandvars( '$CMSSW_BASE/src/RootTools/plot/php/index.php' ), index_php )

ROOT.gROOT.LoadMacro("../4top_multiclass/configs_main/tdrstyle.C")
ROOT.setTDRStyle()

argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',                   default='INFO', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--sample',             action='store',      type=str      )
argParser.add_argument('--output_directory',   action='store',      type=str,    default='/groups/hephy/cms/lena.wild/www/tttt/plots/eft-weights/')
argParser.add_argument('--input_directory',    action='store',      type=str,    default='/eos/vbc/group/cms/lena.wild/tttt/training-ntuples-tttt_v6/MVA-training/ttbb_2l_dilep-bjet_delphes-met30-njet4p-btag2p/')

args = argParser.parse_args()


logging.basicConfig(filename=None,  format='%(asctime)s %(message)s', level=logging.INFO)
if (args.sample):
    sample           = args.sample
if not (args.sample):
    if (str(args.models).find('TTTT')!=-1): 
        sample = 'TTTT_MS'
    if (str(args.models).find('TTbb')!=-1): 
        sample = 'TTbb_MS'
if sample == 'TTTT_MS':  EFTCoefficients = ['ctt', 'cQQ1', 'cQQ8', 'cQt1', 'cQt8', 'ctHRe', 'ctHIm']
if sample == 'TTbb_MS':  EFTCoefficients = ['ctt', 'cQQ1', 'cQQ8', 'cQt1', 'cQt8', 'ctHRe', 'ctHIm','ctb1', 'ctb8', 'cQb1', 'cQb8', 'cQtQb1Re', 'cQtQb8Re', 'cQtQb1Im', 'cQtQb8Im']
assert sample != None, "Sample not found"
assert EFTCoefficients != None, "EFT Coefficient not found"

logging.info("Working on sample %s for EFT Coefficient %s", sample, EFTCoefficients)
# adding hard coded reweight_pkl because of ML-pytorch
if ( sample == "TTTT_MS" ): reweight_pkl = "/eos/vbc/group/cms/robert.schoefbeck/gridpacks/4top/TTTT_MS_reweight_card.pkl" 
if ( sample == "TTbb_MS" ): reweight_pkl = "/eos/vbc/group/cms/robert.schoefbeck/gridpacks/4top/TTbb_MS_reweight_card.pkl" 


import ttbb_2l_python3 as config
   
# set weights 
weightInfo = WeightInfo( reweight_pkl ) 
weightInfo.set_order( 2 ) 

# import training data
logging.info("loading eft data from %s", os.path.join( args.input_directory, sample, sample+".root" ))
upfile_name = os.path.join( args.input_directory, sample, sample+".root" ) 


weigh = {}
with uproot.open(upfile_name) as upfile:
    for name, branch in upfile["Events"].arrays( "p_C").items(): 
        weigh = [ (branch[i]) for i in  range (branch.shape[0]) ]
        # check number of weights
        assert len( weightInfo.combinations ) == branch[0].shape[0] , "got p_C wrong: found %i weights but need %i" %( branch[0].shape[0], len( weightInfo.combinations ) )
    y = np.asarray( weigh )
    

#double check for NaNs:
assert not np.isnan( np.sum(y) ), logging.info("found NaNs in DNN truth values!")

    
def make_TH1F( h, ignore_binning = False):
    # remove infs from thresholds
    vals, thrs = h
    if ignore_binning:
        histo = ROOT.TH1F("h","h",len(vals),0,len(vals))
    else:
        histo = ROOT.TH1F("h","h",len(thrs)-1,array.array('d', thrs))
    for i_v, v in enumerate(vals):
        histo.SetBinContent(i_v+1, v)
    return histo    


limits = {}
exp_nll_ratios = {}
color = [ROOT.kBlue, ROOT.kPink-7, ROOT.kOrange, ROOT.kRed, ROOT.kGreen, ROOT.kCyan, ROOT.kMagenta,ROOT.kOrange-2, ROOT.kPink-9, ROOT.kBlue-2, ROOT.kRed-2, ROOT.kGreen-2, ROOT.kCyan-2, ROOT.kMagenta-2, ROOT.kCyan+3, ROOT.kOrange, ROOT.kRed, ROOT.kGreen, ROOT.kCyan, ROOT.kMagenta]

logging.info("plotting")
exp_nll_ratio = []

for coeff1 in EFTCoefficients:
    histos = []
    k = 0
    for coeff2 in EFTCoefficients:
        nbins=10
        print (coeff1, coeff2)
        binning = np.linspace(-1, 5, 30)
        try: 
            index = weightInfo.combinations.index( (coeff1,coeff2) )
        except:
            index = weightInfo.combinations.index( (coeff2,coeff1) )
        np_histo  = np.histogram(y[:,index]*1e06, bins=binning) 
        
        histo    = make_TH1F(np_histo)
        
        histo.legendText = coeff1+", "+coeff2
        if (coeff1==coeff2):
            histo.style       = styles.lineStyle( ROOT.kBlack, dashed = True)
        else:
            histo.style       = styles.lineStyle( color[k%len(color)])
        k = k+1
        histos.append( histo )

    drawObjects = [ ]
    subdir = sample
    plot = Plot.fromHisto( os.path.join(subdir, "mixed_eft_coeffs_"+coeff1), [[h] for h in histos], texX = "w_{%s, i}"%coeff1, texY = "Entries" )
    plotting.draw( plot,
            plot_directory = args.output_directory,
            #ratio          = {'yRange':(0.6,1.4)} if len(plot.stack)>=2 else None,
            logX = False, logY = True, sorting = False,
            yRange = ('auto', 'auto'),
            legend         = ( (0.15,0.7,0.9,0.92),3),
            drawObjects    = drawObjects,
            copyIndexPHP   = True,
            extensions     = ["png"],
          )
 
Analysis.Tools.syncer.sync()

