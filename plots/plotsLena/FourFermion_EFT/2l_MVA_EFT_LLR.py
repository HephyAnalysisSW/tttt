
import  uproot  
import  numpy                   as np
from    matplotlib              import pyplot as plt
import  os
import  argparse
from    WeightInfo              import WeightInfo #have it in my local folder
import  itertools
import  logging


argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',                   default='INFO', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--sample',             action='store',      type=str      )
argParser.add_argument('--output_directory',   action='store',      type=str,    default='/groups/hephy/cms/lena.wild/tttt/models/')
argParser.add_argument('--input_directory',    action='store',      type=str,    default='/eos/vbc/group/cms/lena.wild/tttt/training-ntuples-tttt_v4/MVA-training/ttbb_2l_dilep-met30-njet4p-btag2p/')
argParser.add_argument('--EFTCoefficients',    action='store',      help="Training vectors for particle net")
argParser.add_argument('--models',             action='store',      type=str,    nargs='*')
args = argParser.parse_args()


logging.basicConfig(filename=None,  format='%(asctime)s %(message)s', level=logging.INFO)
if (args.sample):
    sample           = args.sample
if not (args.sample):
    if (str(args.models).find('TTTT')!=-1): sample = 'TTTT_MS'
    if (str(args.models).find('TTbb')!=-1): sample = 'TTbb_MS'
assert sample != None, "Sample not found"
assert args.EFTCoefficients != None, "EFT Coefficient not found"

logging.info("Working on sample %s for EFT Coefficient %s", sample, args.EFTCoefficients)
# adding hard coded reweight_pkl because of ML-pytorch
if ( sample == "TTTT_MS" ): reweight_pkl = "/eos/vbc/group/cms/robert.schoefbeck/gridpacks/4top/TTTT_MS_reweight_card.pkl" 
if ( sample == "TTbb_MS" ): reweight_pkl = "/eos/vbc/group/cms/robert.schoefbeck/gridpacks/4top/TTbb_MS_reweight_card.pkl" 


import ttbb_2l_python3 as config

# set hyperparameters
mva_variables    = [ mva_variable[0] for mva_variable in config.mva_variables ]
vector_branches = ["mva_Jet_%s" % varname for varname in config.lstm_jetVarNames] 
max_timestep = config.lstm_jets_maxN
   
# set weights 
weightInfo = WeightInfo( reweight_pkl ) 
weightInfo.set_order( 2 ) 
index_lin  = weightInfo.combinations.index( (args.EFTCoefficients,) ) 
index_quad = weightInfo.combinations.index( (args.EFTCoefficients,args.EFTCoefficients) )

# import training data
upfile_name = os.path.join( args.input_directory, sample, sample+".root" )
xx     = uproot.open( upfile_name ) 
xx     = xx["Events"].arrays( mva_variables )
x      = np.array( [ xx[branch] for branch in list(xx.keys()) ] ).transpose() 

weigh = {}
with uproot.open(upfile_name) as upfile:
    for name, branch in upfile["Events"].arrays( "p_C").items(): 
        weigh = [ (branch[i][0], branch[i][index_lin], branch[i][index_quad]) for i in  range (branch.shape[0]) ]
        # check number of weights
        assert len( weightInfo.combinations ) == branch[0].shape[0] , "got p_C wrong: found %i weights but need %i" %( branch[0].shape[0], len( weightInfo.combinations ) )
    y = np.asarray( weigh )
    


# add lstm if needed
vec_br_f  = {}
upfile_name = os.path.join( args.input_directory, sample, sample+".root" )
with uproot.open( upfile_name ) as upfile:
    for name, branch in upfile["Events"].arrays( vector_branches ).items():
        branch = np.array(branch)
        for i in range ( branch.shape[0] ):
            branch[i]=np.pad( branch[i][:max_timestep], (0, max_timestep - len(branch[i][:max_timestep])) )
        vec_br_f[name] = branch
# put columns side by side and transpose the innermost two axis
v = np.column_stack( [np.stack( vec_br_f[name] ) for name in vec_br_f.keys()] ).reshape( len(y), len(vector_branches), max_timestep ).transpose((0,2,1))
    

#double check for NaNs:
assert not np.isnan( np.sum(x) ), logging.info("found NaNs in DNN input!")
assert not np.isnan( np.sum(y) ), logging.info("found NaNs in DNN truth values!")
assert not np.isnan( np.sum(v) ), logging.info("found NaNs in LSTM input!")

models=args.models
import onnxruntime as ort
X = np.reshape(x,(x[:,0].size, 1, x[0].size))
V = np.reshape(v,(v[:,0,0].size, 1, v[0,:,0].size, v[0,0,:].size))
options = ort.SessionOptions()
options.inter_op_num_threads = 1


def make_cdf_map( x, y ):
    import scipy.interpolate
    map__ = scipy.interpolate.interp1d(x, y, kind='linear')
    max_x, min_x = max(x), min(x)
    max_y, min_y = max(y), min(y)
    def map_( x_ ):
        x__ = np.array(x_)
        result = np.zeros_like(x__).astype('float')
        result[x__>max_x] = max_y
        result[x__<min_x] = min_y
        vals = (x__>=min_x) & (x__<=max_x)
        result[vals] = map__(x__[vals]) 
        return result 
    return map_    

exp_nll_ratios = {}
for i in range (len(args.models)):
    dir_name = models[i]
    logging.info("loading model %s", dir_name)
    ort_sess = ort.InferenceSession(os.path.join(args.output_directory, str(dir_name)+'.onnx'), providers = ['CPUExecutionProvider'],sess_options=options)
    z = []
    LSTM = False
    if (str(dir_name).find('lstm')!=-1): LSTM = True
    if (LSTM):
        for i in range (len(y)):
            z.append( ort_sess.run(["output1"], {"input1": X[i].astype(np.float32),"input2": V[i].astype(np.float32)})[0][0]  )
    else: 
        for i in range (len(y)):
            z.append( ort_sess.run(["output1"], {"input1": X[i].astype(np.float32)})[0][0] )
    z = np.array(z)
    logging.info("plotting")
    exp_nll_ratio = []
    
    if (sample == "TTTT_MS"): theta_ = np.linspace(-5,5,20)
    if (sample == "TTbb_MS"): theta_ = np.linspace(-40,40,20)
    #theta_ = np.linspace(-40,40,20)
    scale_weight = 10**5
    fig, ax = plt.subplots(dpi = 300)
    for theta in theta_: 
        w_sm   =   y[:,0] 
        w_bsm  =   y[:,0] + theta * y[:,1] + theta**2 * y[:,2] 
        
        # t_theta = 1 + theta * z[:,0] + theta**2 * z[:,1] *0.5
        t_theta =  z[:,0] + theta * z[:,1] * 0.5
        t_theta_argsort     = np.argsort(t_theta)
        t_theta_argsort_inv = np.argsort(t_theta_argsort)
        cdf_sm = np.cumsum(w_sm[t_theta_argsort])
        cdf_sm/=cdf_sm[-1]
        
        cdf_map = make_cdf_map( t_theta[t_theta_argsort], cdf_sm )
        t_theta_cdf = cdf_map( t_theta )
        nbins=10
        binning = np.linspace(0, 1, nbins+1)

        np_histo_sm  = np.histogram(t_theta_cdf, bins=binning, weights = w_sm ) [0]
        np_histo_bsm = np.histogram(t_theta_cdf, bins=binning, weights = w_bsm ) [0]
        #print(np.sum(np_histo_bsm), np.sum(np_histo_sm))
        ax.hist(t_theta_cdf, bins=binning, weights = w_bsm / np.sum(w_bsm)*np.sum(w_sm), histtype='step', label = 'bsm, '+'%.2f' %theta)
        if (theta == theta_[len(theta_)-1]): ax.hist(t_theta_cdf, bins=binning, weights = w_sm, histtype='step', label = 'sm '+'%.2f' %theta, color = 'black')
        
        exp_nll_ratio_ =2*np.sum(np_histo_sm - np_histo_bsm - np_histo_bsm*np.log(np_histo_sm/np_histo_bsm))
        exp_nll_ratio.append(exp_nll_ratio_)
    exp_nll_ratios[dir_name] = exp_nll_ratio       
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05), ncol=3, fancybox=True, shadow=True, prop={'size': 6})
    plt.savefig(dir_name+'_hist.png')  
    
    
fig, az = plt.subplots(figsize = (5,8))    
az.set_ylim((0,5))
az.set_xlabel(r' $\theta $')
az.set_title(sample + ', '+args.EFTCoefficients)
for i in range (len(args.models)):
    az.plot(theta_, exp_nll_ratios[models[i]], label = 'LSTM' if (str(models[i]).find('lstm')!=-1) else 'no LSTM')
plt.legend()    
plt.savefig(sample+'_'+args.EFTCoefficients+"_LLR.png")