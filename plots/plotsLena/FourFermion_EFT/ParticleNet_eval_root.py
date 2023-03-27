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
from array import *
import scipy as scipy



def copyIndexPHP( results_dir ):
    index_php = os.path.join( results_dir, 'index.php' )
    shutil.copyfile( os.path.expandvars( '$CMSSW_BASE/src/RootTools/plot/php/index.php' ), index_php )

ROOT.gROOT.LoadMacro("../4top_multiclass/configs_main/tdrstyle.C")
ROOT.setTDRStyle()

argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',                   default='INFO', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--sample',             action='store',      type=str      )
argParser.add_argument('--lumi',               action='store',      type=int,    default=1     )
argParser.add_argument('--predict_directory',  action='store',      type=str,    default='/scratch-cbe/users/lena.wild/FourFermion/predictions/')
argParser.add_argument('--output_directory',   action='store',      type=str,    default='/groups/hephy/cms/lena.wild/www/tttt/plots/ParticleNet')
#argParser.add_argument('--input_directory',    action='store',      type=str,    default='/eos/vbc/group/cms/lena.wild/tttt/training-ntuples-tttt_v6/MVA-training/ttbb_2l_dilep-bjet_delphes-met30-njet4p-btag2p/')
argParser.add_argument('--model',              action='store',      type=str)
argParser.add_argument('--EFT_coeff',          action='store',      type=str,    default = 'ctt')
argParser.add_argument('--epoch_name',         action='store',      type=str)

args = argParser.parse_args()

import ttbb_2l_python3 as config
logging.basicConfig(filename=None,  format='%(asctime)s %(message)s', level=logging.INFO)
if (args.sample):
    sample           = args.sample
assert sample != None, "Sample not found"

# set hyperparameters
mva_variables    = [ mva_variable[0] for mva_variable in config.mva_variables ]
vector_branches  = ["mva_Jet_%s" % varname for varname in config.lstm_jetVarNames] 
max_target = 2 # lin quad training target

# import training data
logging.info("loading dnn data from %s", os.path.join( args.predict_directory, sample, args.model+".root" )) #HARDCODED
upfile_name = os.path.join( args.predict_directory, sample, args.model+".root") #HARDCODED
xx     = uproot.open( upfile_name ) 
xx     = xx["Events"].arrays( mva_variables )
x      = np.array( [ xx[branch] for branch in list(xx.keys()) ] ).transpose() 

logging.info("loading training from %s", os.path.join( args.predict_directory, sample, args.model+".root" )) #HARDCODED
vec_br_f  = {}
vec_br_y  = {}

with uproot.open( upfile_name ) as upfile:
    if not args.epoch_name:
        ttree = list(upfile.keys())[0]
        inhalt = list(upfile[ttree].keys())
        epoch = list(filter(lambda x: b'epoch' in x, inhalt))[0]
        epoch = str(epoch, 'ascii')
        logging.info("Found epochs {} in file {}".format(epoch, os.path.join( args.predict_directory, sample, args.model+".root" )) )
    else: epoch = "ctt_"+args.epoch_name
    logging.info("Working on epoch {}".format(epoch))    
    for name, branch in upfile["Events"].arrays( epoch ).items(): 
        branch = np.array(branch)
        for i in range ( branch.shape[0] ):
            branch[i]=np.pad( branch[i][:max_target], (0, max_target - len(branch[i][:max_target])) )
        vec_br_f[name] = branch

# put columns side by side and transpose the innermost two axis
z = np.column_stack( [np.stack( vec_br_f[name] ) for name in vec_br_f.keys()] ).reshape( len(x[:,0]), 1, max_target ).transpose((0,2,1))

# load target weight
logging.info("loading truth from %s", os.path.join( args.predict_directory, sample, args.model+".root")) #HARDCODED
with uproot.open(upfile_name) as upfile:
    for name, branch in upfile["Events"].arrays( "ctt").items(): 
        branch = np.array(branch)
        for i in range ( branch.shape[0] ):
            branch[i]=np.pad( branch[i][:max_target+1], (0, max_target +1 - len(branch[i][:max_target+1])) )
        vec_br_y[name] = branch

# put columns side by side and transpose the innermost two axis
y = np.column_stack( [np.stack( vec_br_y[name] ) for name in vec_br_y.keys()] ).reshape( len(x[:,0]), 1, max_target+1).transpose((0,2,1))

assert not np.isnan( np.sum(x) ), logging.info("found NaNs in DNN input!")
assert not np.isnan( np.sum(z) ), logging.info("found NaNs in training!")
assert not np.isnan( np.sum(y) ), logging.info("found NaNs in truth!")


def make_TH1F( val, thr, ignore_binning = False):
    # remove infs from thresholds
    vals = val
    thrs = thr
    if ignore_binning:
        histo = ROOT.TH1F("h","h",len(vals),0,len(vals))
    else:
        histo = ROOT.TH1F("h","h",len(thrs)-1, array('d', thrs))
    for i_v, v in enumerate(vals):
        histo.SetBinContent(i_v+1, v)
    return histo 

def eval_train ( var_evaluation ):
    x_eval = np.array ( xx[bytes(var_evaluation, 'ascii')] )
    hist, bins = np.histogram( x_eval, bins=nbins, range=(config.plot_mva_variables[var_evaluation][0][0], config.plot_mva_variables[var_evaluation][0][1]) )
    train_lin  = np.zeros( (len(bins),1) )
    train_quad = np.zeros( (len(bins),1) )
    for b in range ( 1,len(bins)-1 ):
        for ind in range ( x_eval.shape[0] ):
            val = x_eval[ind]
            if ( val > bins[b-1] and val<= bins[b] ):
                train_lin[b] += y[ind,0]*z[ind,0]
                train_quad[b]+= y[ind,0]*z[ind,1]           
    plots[var_evaluation+'trainlin']  = make_TH1F(train_lin[:,0], bins)
    plots[var_evaluation+'trainquad'] = make_TH1F(train_quad[:,0], bins) 
    plots[var_evaluation+'trainlin'].SetLineColor(ROOT.kRed)
    plots[var_evaluation+'trainquad'].SetLineColor(ROOT.kBlue)
  
def eval_truth ( var_evaluation ):
    x_eval = np.array ( xx[bytes(var_evaluation, 'ascii')] )
    hist, bins  = np.histogram( x_eval, bins=nbins, range=(config.plot_mva_variables[var_evaluation][0][0], config.plot_mva_variables[var_evaluation][0][1]) )
    truth_lin   = np.zeros( (len(bins),1) )
    truth_quad  = np.zeros( (len(bins),1) )
    for b in range ( 1,len(bins)-1 ):
        for ind in range ( x_eval.shape[0] ):
            val = x_eval[ind]
            if ( val > bins[b-1] and val<= bins[b] ):
                truth_lin[b] +=y[ind,1]*y[ind,0]
                truth_quad[b]+=y[ind,2]*y[ind,0]
    i = plotvars.index( var_evaluation )   
    plots[var_evaluation+'truelin']  = make_TH1F(truth_lin[:,0], bins)
    plots[var_evaluation+'truequad'] = make_TH1F(truth_quad[:,0], bins)
    plots[var_evaluation+'truelin'].SetLineColor(ROOT.kRed)
    plots[var_evaluation+'truequad'].SetLineColor(ROOT.kBlue)
    plots[var_evaluation+'truelin'].SetLineStyle(7)
    plots[var_evaluation+'truequad'].SetLineStyle(7)
 
nbins = 20
index = list(itertools.product(list(range(0, 4)), list(range(0, 5))))
plotvars=list(config.plot_mva_variables.keys())
plots = {}   
logging.info("       plotting truth for %i variables ", len(plotvars))
for i in range (len(plotvars)):
    eval_truth(plotvars[i])
logging.info("       plotting train for %i variables ", len(plotvars))        
for i in range (len(plotvars)):
    eval_train(plotvars[i]) 

c1 = ROOT.TCanvas()
c1.SetCanvasSize(2000, 2000);
#c1.SetWindowSize(2,2);  
ROOT.gStyle.SetOptStat(0) 
c1.Divide(4,5)
for idx, var in enumerate(plotvars):
    c1.cd(idx+1)
    plots[var+'truelin'].GetXaxis().SetTitle(config.plot_mva_variables[var][1])
    plots[var+'truelin'].GetYaxis().SetRangeUser(-plots[var+'truequad'].GetMaximum()*0.6,plots[var+'truequad'].GetMaximum()*1.2)
    #print(plots[var+'truelin'].GetMinimum(),plots[var+'truequad'].GetMaximum())
    plots[var+'truelin'].Draw()
    plots[var+'truequad'].Draw("SAME")
    plots[var+'trainlin'].Draw("SAME")
    plots[var+'trainquad'].Draw("SAME")
savename = args.model+"_"+epoch+"_lin_quad" if args.model else args.epoch_name+"_lin_quad"
c1.Print(os.path.join(args.output_directory, savename+".png"))
c1.Print(os.path.join(args.output_directory, savename+".pdf"))
copyIndexPHP(os.path.join(args.output_directory) )

Analysis.Tools.syncer.sync()