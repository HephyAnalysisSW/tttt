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
argParser.add_argument('--lumi',               action='store',      type=int,    default=300     )
argParser.add_argument('--predict_directory',  action='store',      type=str,    default='/groups/hephy/cms/lena.wild/tttt/models_LSTM/')
argParser.add_argument('--output_directory',   action='store',      type=str,    default='/groups/hephy/cms/lena.wild/www/tttt/plots/limits_testing/')
argParser.add_argument('--input_directory',    action='store',      type=str,    default='/eos/vbc/group/cms/lena.wild/tttt/training-ntuples-tttt_v7/MVA-training/ttbb_2l_dilep2-bjet_delphes-ht500-njet6p-btag1p/')
argParser.add_argument('--model',             action='store',      type=str)


args = argParser.parse_args()

import ttbb_2l_python3 as config
logging.basicConfig(filename=None,  format='%(asctime)s %(message)s', level=logging.INFO)
if (args.sample):
    sample           = args.sample
assert sample != None, "Sample not found"
bkg = "TT_2L"

# adding hard coded reweight_pkl because of ML-pytorch
if ( sample == "TTTT_MS" ): reweight_pkl = "/eos/vbc/group/cms/robert.schoefbeck/gridpacks/4top/TTTT_MS_reweight_card.pkl" 
if ( sample == "TTbb_MS" ): reweight_pkl = "/eos/vbc/group/cms/robert.schoefbeck/gridpacks/4top/TTbb_MS_reweight_card.pkl" 


model = args.model
EFTCoefficients = {}
for coeff in config.WC[sample]:
    if(model.find(coeff)!=-1):
        EFTCoefficients[model] = coeff

# set hyperparameters
mva_variables    = [ mva_variable[0] for mva_variable in config.mva_variables ]
vector_branches  = ["mva_Jet_%s" % varname for varname in config.lstm_jetVarNames] 
max_timestep     = config.lstm_jets_maxN

# import training data
logging.info("loading dnn data from %s", os.path.join( args.input_directory, sample, sample+".root" ))
upfile_name = os.path.join( args.input_directory, sample, sample+".root" )
xx     = uproot.open( upfile_name ) 
xx     = xx["Events"].arrays( mva_variables )
x      = np.array( [ xx[branch] for branch in list(xx.keys()) ] ).transpose() 

# add lstm if needed
logging.info("loading gNN/LSTM data from %s", os.path.join( args.input_directory, sample, sample+".root" ))
vec_br_f  = {}
vec_br_c  = {}

with uproot.open( upfile_name ) as upfile:
    for name, branch in upfile["Events"].arrays( vector_branches ).items():
        branch = np.array(branch)
        for i in range ( branch.shape[0] ):
            branch[i]=np.pad( branch[i][:max_timestep], (0, max_timestep - len(branch[i][:max_timestep])) )
        vec_br_f[name] = branch
    
# put columns side by side and transpose the innermost two axis
v = np.column_stack( [np.stack( vec_br_f[name] ) for name in vec_br_f.keys()] ).reshape( len(x[:,0]), len(vector_branches), max_timestep ).transpose((0,2,1))

# set weights 
weightInfo = WeightInfo( reweight_pkl ) 
weightInfo.set_order( 2 ) 
index_lin = weightInfo.combinations.index( (EFTCoefficients[model],) ) 
index_quad = weightInfo.combinations.index( (EFTCoefficients[model],EFTCoefficients[model]) )

weigh = {}
with uproot.open(upfile_name) as upfile:
    for name, branch in upfile["Events"].arrays( "p_C" ).items(): 
        weigh = [ (branch[i][0], branch[i][index_lin], branch[i][index_quad]) for i in  range (branch.shape[0]) ]
        # check number of weights
        assert len( weightInfo.combinations ) == branch[0].shape[0] , "got p_C wrong: found %i weights but need %i" %( branch[0].shape[0], len( weightInfo.combinations ) )
    y = np.asarray( weigh )
    
assert not np.isnan( np.sum(x) ), logging.info("found NaNs in DNN input!")
assert not np.isnan( np.sum(y) ), logging.info("found NaNs in DNN truth values!")
assert not np.isnan( np.sum(v) ), logging.info("found NaNs in LSTM input!")

# import bkg training data 
logging.info("import training data for bkg %s", bkg)
upfile_name = os.path.join( args.input_directory, bkg, bkg+".root" )
xx_bkg = uproot.open( upfile_name ) 
xx_bkg = xx_bkg["Events"].arrays( mva_variables )
x_bkg  = np.array( [ xx_bkg[branch] for branch in list(xx_bkg.keys()) ] ).transpose() 

yy_bkg = uproot.open( upfile_name )
yy_bkg = yy_bkg["Events"].arrays( "genWeight" )
yy_bkg = np.array( [ yy_bkg[branch] for branch in [b'genWeight'] ] ).transpose() 
y_bkg  = np.zeros((len(x_bkg[:,0]), 3))
y_bkg[:,0] = np.reshape(yy_bkg, (len(yy_bkg), ))

# add lstm if needed
logging.info("loading gNN/LSTM data from %s", os.path.join( args.input_directory, bkg, bkg+".root" ))
vec_br_f  = {}
with uproot.open( upfile_name ) as upfile:
    for name, branch in upfile["Events"].arrays( vector_branches ).items():
        branch = np.array(branch)
        for i in range ( branch.shape[0] ):
            branch[i]=np.pad( branch[i][:max_timestep], (0, max_timestep - len(branch[i][:max_timestep])) )
        vec_br_f[name] = branch
v_bkg = np.column_stack( [np.stack( vec_br_f[name] ) for name in vec_br_f.keys()] ).reshape( len(y_bkg[:,0]), len(vector_branches), max_timestep ).transpose((0,2,1))

# normalizing to integrated luminosity
logging.info("calculating new weights, reweighting to integrated luminosity")
w     = args.lumi * config.xsec[sample] * 1000 * y/ config.total_genWeight[sample]
w_bkg = args.lumi * config.xsec[bkg] * 1000 * y_bkg/ config.total_genWeight[bkg]

w_bkg[:,0]  = np.array([aa if aa >= 0 else 0 for aa in list(w_bkg[:,0])]) #remove negative weights 


x_ = np.concatenate(( x, x_bkg ))
w_ = np.concatenate(( w, w_bkg ))
v_ = np.concatenate(( v, v_bkg ))

#double check for NaNs:
assert not np.isnan( np.sum( x_ ) ), logging.info("found NaNs in DNN input!")
assert not np.isnan( np.sum( w_ ) ), logging.info("found NaNs in DNN truth values!")
assert not np.isnan( np.sum( v_ ) ), logging.info("found NaNs in LSTM input!")

   

X = np.reshape(x_,(x_[:,0].size, 1, x_[0].size)) # DNN features
V = np.reshape(v_,(v_[:,0,0].size, 1, v_[0,:,0].size, v_[0,0,:].size)) # LSTM features

models=args.model
import onnxruntime as ort
from scipy import optimize 

options = ort.SessionOptions()
options.inter_op_num_threads = 1
options.intra_op_num_threads = 1  
Z = {}


dir_name = args.model
logging.info("loading model %s", dir_name)
ort_sess = ort.InferenceSession(os.path.join(args.predict_directory, str(dir_name)+'.onnx'),  sess_options=options, providers = ['CPUExecutionProvider'])
z = []
LSTM = False

if (len(ort_sess.get_inputs())==2):
    LSTM = True
    for i in range (len(X[:,0])):
        z.append( ort_sess.run(["output1"], {"input1": X[i].astype(np.float32),"input2": V[i].astype(np.float32)})[0][0]  )
if (len(ort_sess.get_inputs())==1):
    for i in range (len(X[:,0])):
        z.append( ort_sess.run(["output1"], {"input1": X[i].astype(np.float32)})[0][0]  )

z = np.array(z)   

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


# Define steps for evaluation 
def eval_train ( var_evaluation, z ):
    zz = z
    total_weight =np.sum(w_[:,0])
    x_eval = np.concatenate((np.array ( xx[bytes(var_evaluation, 'ascii')] ),np.array ( xx_bkg[bytes(var_evaluation, 'ascii')] )))
    nbins = 20 if var_evaluation != "nrecoJet" else 8
    hist_lin,  bins = np.histogram( x_eval, bins=nbins, range=(config.plot_mva_variables[var_evaluation][0][0], config.plot_mva_variables[var_evaluation][0][1]), weights=zz[:,0]*w_[:,0]/total_weight)
    hist_quad, bins = np.histogram( x_eval, bins=nbins, range=(config.plot_mva_variables[var_evaluation][0][0], config.plot_mva_variables[var_evaluation][0][1]), weights=zz[:,1]*w_[:,0]/total_weight)                               
    plots[var_evaluation+'trainlin']  = make_TH1F(hist_lin, bins)
    plots[var_evaluation+'trainquad'] = make_TH1F(hist_quad, bins) 
    plots[var_evaluation+'trainlin'].SetLineColor(ROOT.kRed)
    plots[var_evaluation+'trainquad'].SetLineColor(ROOT.kBlue)

  
def eval_truth ( var_evaluation ):
    total_weight =np.sum(w_[:,0])
    x_eval = np.concatenate((np.array ( xx[bytes(var_evaluation, 'ascii')] ),np.array ( xx_bkg[bytes(var_evaluation, 'ascii')] )))
    nbins = 20 if var_evaluation != "nrecoJet" else 8
    hist_truelin,      bins  = np.histogram( x_eval, bins=nbins, range=(config.plot_mva_variables[var_evaluation][0][0], config.plot_mva_variables[var_evaluation][0][1]), weights= w_[:,1] / total_weight)
    hist_truequad,     bins  = np.histogram( x_eval, bins=nbins, range=(config.plot_mva_variables[var_evaluation][0][0], config.plot_mva_variables[var_evaluation][0][1]), weights= w_[:,2] / total_weight)
         
    i = plotvars.index( var_evaluation )   
    
    plots[var_evaluation+'truelin']  = make_TH1F(hist_truelin, bins)
    plots[var_evaluation+'truequad'] = make_TH1F(hist_truequad, bins)
    plots[var_evaluation+'truelin'].SetLineColor(ROOT.kRed)
    plots[var_evaluation+'truequad'].SetLineColor(ROOT.kBlue)
    plots[var_evaluation+'truelin'].SetLineStyle(7)
    plots[var_evaluation+'truequad'].SetLineStyle(7)
 

 
nbins = 20
index = list(itertools.product(list(range(0, 5)), list(range(0, 8))))
plotvars=list(config.plot_mva_variables.keys())
plots = {}   
logging.info("       plotting truth for %i variables ", len(plotvars))
for i in range (len(plotvars)):
    eval_truth(plotvars[i])
logging.info("       plotting train for %i variables ", len(plotvars))        
for i in range (len(plotvars)):
    eval_train(plotvars[i],z) 

c1 = ROOT.TCanvas()
c1.SetCanvasSize(800, 1000);
#c1.SetWindowSize(4,2);  
ROOT.gStyle.SetOptStat(0) 
c1.Divide(5,8)
for idx, var in enumerate(plotvars):
    c1.cd(idx+1)
    maxim = plots[var+'truequad'].GetMaximum()
    Maxim = plots[var+'truelin'].GetMaximum()
    maxx = np.max((maxim, Maxim))
    minim = plots[var+'truequad'].GetMinimum()
    Minim = plots[var+'truelin'].GetMinimum()
    minn = np.min((minim, Minim))
    plots[var+'truelin'].GetXaxis().SetTitle(config.plot_mva_variables[var][1])
    plots[var+'truelin'].GetYaxis().SetRangeUser(minn*1.2, maxx*1.2)
    #print(plots[var+'truelin'].GetMinimum(),plots[var+'truequad'].GetMaximum())
    plots[var+'truelin'].Draw()
    plots[var+'truequad'].Draw("SAME")
    plots[var+'trainlin'].Draw("SAME")
    plots[var+'trainquad'].Draw("SAME")

SUBDIR = "with_bkg"
c1.Print(os.path.join(args.output_directory, args.sample, SUBDIR, "training_output", EFTCoefficients[args.model]+".png"))
c1.Print(os.path.join(args.output_directory, args.sample, SUBDIR, "training_output", EFTCoefficients[args.model]+".pdf"))
copyIndexPHP(os.path.join(args.output_directory, args.sample, SUBDIR, "training_output") )


logging.info("figure dir link: %s", os.path.join('https://lwild.web.cern.ch/tttt/plots/', os.path.basename(os.path.normpath(args.output_directory)), args.sample, SUBDIR, "training_output" )) 
logging.info("plot link:   %s", os.path.join('https://lwild.web.cern.ch/tttt/plots/', os.path.basename(os.path.normpath(args.output_directory)), args.sample, SUBDIR, "training_output", EFTCoefficients[args.model]+".png")) 
   

Analysis.Tools.syncer.sync()
  