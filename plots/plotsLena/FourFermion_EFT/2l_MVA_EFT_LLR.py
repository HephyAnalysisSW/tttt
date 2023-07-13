# plot script for multiple WCs
# normalizing to xsec * lumi events 

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
argParser.add_argument('--model_directory',    action='store',      type=str,    default='/groups/hephy/cms/lena.wild/tttt/models/')
argParser.add_argument('--output_directory',   action='store',      type=str,    default='/groups/hephy/cms/lena.wild/www/tttt/plots/signal/new2DLLR/')
argParser.add_argument('--input_directory',    action='store',      type=str,    default='/eos/vbc/group/cms/lena.wild/tttt/training-ntuples-tttt_v6_1/MVA-training/PN_ttbb_2l_dilep2-bjet_delphes-met30-njet4p-btag2p/')
argParser.add_argument('--models',             action='store',      type=str,    nargs='*')
argParser.add_argument('--labels',             action='store',      type=str,    nargs='*', default=None, help="labels for models in plot")
argParser.add_argument('--filename',           action='store',      type=str,    default=None, help="filename")
argParser.add_argument('--theta_range',        action='store',      type=float,    default=10     )
argParser.add_argument('--theta_range_comb',   action='store',      type=float,    default=10, nargs=2     )
argParser.add_argument('--shape_effects_only', action='store_true', default=False, help="Normalize sm *and* bsm weights to sample_weight number of events")
argParser.add_argument('--combine_models',     action='store_true', default=False, help="make a 2D LLR-plot for models?")
argParser.add_argument('--reduce',             action='store',      type=int,    default=None,     help="Reduce training data by factor?"),
argParser.add_argument('--plot_histos',        action='store_true', default=False),
argParser.add_argument('--no14',               action='store_true', default=False),

args = argParser.parse_args()

import ttbb_2l_python3 as config

if args.reduce is not None: reduce = True 
else: reduce = False

allmodels = args.models

logging.basicConfig(filename=None,  format='%(asctime)s %(message)s', level=logging.INFO)
if (args.sample):
    sample           = args.sample
if not (args.sample):
    if (str(args.models).find('TTTT')!=-1): sample = 'TTTT_MS'
    if (str(args.models).find('TTbb')!=-1): sample = 'TTbb_MS'
assert sample != None, "Sample not found"
if args.labels != None:
    assert (len(args.labels)==len(args.models)), "need same number of labels and models"

EFTCoefficients = {}
for model in args.models:
    for coeff in config.WC[sample]:
        if(model.find(coeff)!=-1):
            EFTCoefficients[model] = coeff               
            
            
EFT = list(EFTCoefficients.values())      
assert len(EFTCoefficients) != None, "EFT Coefficient not found"
if (args.combine_models): 
    assert len(EFTCoefficients) == 2, ("Need 2 EFTCoefficients for 2D plot, got {}".format( len(EFTCoefficients), {}) )
    assert  (EFT[0] != EFT[1]), "Got two identical EFTCoefficients"
logging.info("Working on sample {} for EFT Coefficient(s) {}".format( sample, list(EFTCoefficients.values()), {}))

# adding hard coded reweight_pkl because of ML-pytorch
if ( sample == "TTTT_MS" ): reweight_pkl = "/eos/vbc/group/cms/robert.schoefbeck/gridpacks/4top/TTTT_MS_reweight_card.pkl" 
if ( sample == "TTbb_MS" ): reweight_pkl = "/eos/vbc/group/cms/robert.schoefbeck/gridpacks/4top/TTbb_MS_reweight_card.pkl" 


# set hyperparameters
mva_variables    = [ mva_variable[0] for mva_variable in config.mva_variables ]
vector_branches  = ["mva_Jet_%s" % varname for varname in config.lstm_jetVarNames] 
constituents_points = ['mva_Jet_eta', 'mva_Jet_phi']
max_timestep = config.lstm_jets_maxN
   

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
    for name, branch in upfile["Events"].arrays( constituents_points ).items():
        branch = np.array(branch)
        for i in range ( branch.shape[0] ):
            branch[i]=np.pad( branch[i][:max_timestep], (0, max_timestep - len(branch[i][:max_timestep])) )
        vec_br_c[name] = branch    
# put columns side by side and transpose the innermost two axis
v = np.column_stack( [np.stack( vec_br_f[name] ) for name in vec_br_f.keys()] ).reshape( len(x[:,0]), len(vector_branches), max_timestep ).transpose((0,2,1))
c = np.column_stack( [np.stack( vec_br_c[name] ) for name in vec_br_c.keys()] ).reshape( len(x[:,0]), len(constituents_points),  max_timestep  ).transpose((0,2,1))
    
# set weights 
weightInfo = WeightInfo( reweight_pkl ) 
weightInfo.set_order( 2 ) 
index_lin = {}
index_quad = {}

for model in allmodels:
    index_lin[model] = weightInfo.combinations.index( (EFTCoefficients[model],) ) 
    index_quad[model] = weightInfo.combinations.index( (EFTCoefficients[model],EFTCoefficients[model]) )
if (args.combine_models): 
    try: 
        index_mixed = weightInfo.combinations.index( (EFT[0], EFT[1]) ) 
    except:
        index_mixed = weightInfo.combinations.index( (EFT[1], EFT[0]) ) 
weigh = {}

with uproot.open(upfile_name) as upfile:
    for name, branch in upfile["Events"].arrays( "p_C").items(): 
        #weigh = [ (branch[i][0], branch[i][index_lin[args.EFTCoefficients[0]]], branch[i][index_quad[args.EFTCoefficients[0]]],branch[i][index_lin[args.EFTCoefficients[1]]], branch[i][index_quad[args.EFTCoefficients[1]]], branch[i][index_mixed] ) for i in  range (branch.shape[0]) ]
        weigh = [ (branch[i]) for i in  range (branch.shape[0]) ]
        # check number of weights
        assert len( weightInfo.combinations ) == branch[0].shape[0] , "got p_C wrong: found %i weights but need %i" %( branch[0].shape[0], len( weightInfo.combinations ) )
    y = np.asarray( weigh )
    
#double check for NaNs:
assert not np.isnan( np.sum(x) ), logging.info("found NaNs in DNN input!")
assert not np.isnan( np.sum(y) ), logging.info("found NaNs in DNN truth values!")
assert not np.isnan( np.sum(v) ), logging.info("found NaNs in LSTM input!")
assert not np.isnan( np.sum(c) ), logging.info("found NaNs in constituent points!")

if args.reduce is not None: red = int(len(x[:,0])/args.reduce)    
if (reduce):
    x = x[0:red, :]
    v = v[0:red, :, :]
    y = y[0:red, :]
    c = c[0:red, :, :]
    logging.info("using only small dataset of 1/%s of total events -> %s events for signal %s", args.reduce, red, args.sample)

# reshape inputs for models
X_pn = np.reshape(x,(x[:,0].size, 1, x[0].size, 1))# global features
V_pn = np.reshape(v,(v[:,0,0].size, 1, v[0,0,:].size, v[0,:,0].size ))# eflow_features
C_pn = np.reshape(c,(c[:,0,0].size, 1, c[0,0,:].size, c[0,:,0].size ))# constituents_points
M_pn = np.ones((1,1,10))
X = np.reshape(x,(x[:,0].size, 1, x[0].size)) # DNN features
V = np.reshape(v,(v[:,0,0].size, 1, v[0,:,0].size, v[0,0,:].size)) # LSTM features
#V = np.ones(V.shape)

def make_cdf_map( x, y ):
    import scipy.interpolate
    map__ = scipy.interpolate.interp1d(x, y, 'linear', )#fill_value="extrapolate")
    max_x, min_x = max(x), min(x)
    max_y, min_y = max(y), min(y)
    def map_( x_ ):
        x__ = np.array(x_)
        result = np.zeros_like(x__).astype('float64')
        result[x__>max_x] = max_y
        result[x__<min_x] = min_y
        vals = (x__>=min_x) & (x__<=max_x)
        result[vals] = map__(x__[vals]) 
        return result 
    return map_    
    
def make_TH1F( h, ignore_binning = True):
    # remove infs from thresholds
    vals, thrs = h
    if ignore_binning:
        histo = ROOT.TH1F("h","h",len(vals),0,1)
    else:
        histo = ROOT.TH1F("h","h",len(thrs)-1, array('d', thrs))
    for i_v, v in enumerate(vals):
        histo.SetBinContent(i_v+1, v)
    return histo    

lumi = args.lumi    
models=args.models
import onnxruntime as ort
from scipy import optimize 
SUBDIR = "without_bkg"
options = ort.SessionOptions()
options.inter_op_num_threads = 1
options.intra_op_num_threads = 1  
Z = {}

for j in range (len(args.models)):
    dir_name = models[j]
    logging.info("loading model %s", dir_name)
    ort_sess = ort.InferenceSession(os.path.join(args.model_directory, str(dir_name)+'.onnx'),  sess_options=options, providers = ['CPUExecutionProvider'])
    z = []
    LSTM = False
    ParticleNet = False
    DNN = False
    if (len(ort_sess.get_inputs())==2):
        LSTM = True
        for i in range (len(y)):
            z.append( ort_sess.run(["output1"], {"input1": X[i].astype(np.float32),"input2": V[i].astype(np.float32)})[0][0]  )
    if (len(ort_sess.get_inputs())==1 ):
        if str(dir_name).find('PN')==-1:
            DNN = True
            for i in range (len(y)):
                z.append( ort_sess.run([ort_sess.get_outputs()[0].name], {ort_sess.get_inputs()[0].name: X[i].astype(np.float32)})[0][0]  )
        if str(dir_name).find('PN')!=-1:
            DNN_PN = True
            for i in range (len(y)):
                z.append( ort_sess.run([ort_sess.get_outputs()[0].name], {ort_sess.get_inputs()[0].name: X_pn[i].astype(np.float32)})[0][0]  )
    if (len(ort_sess.get_inputs())==4):
        ParticleNet = True
        for i in range (len(y)):
            z.append( ort_sess.run(["output"], {"global_features": X_pn[i].astype(np.float32), "constituents_points": C_pn[i].astype(np.float32), "eflow_features": V_pn[i].astype(np.float32), "eflow_mask": M_pn.astype(np.float32),})[0][0] )
    Z[dir_name] = np.array(z)
    Z[dir_name+"_label"] = args.labels[j] if args.labels != None else ('LSTM' if (LSTM) else ('ParticleNet' if (ParticleNet) else 'DNN') )
    

# read from PN file
logging.info("plotting")

th = args.theta_range
nbins = 30
if (args.combine_models==True):
    th = th * 3.5
else: th = th * 2   
theta_ = np.linspace(-th,th,nbins)
# theta_ = np.array([-2, -1.5, -1.35, -1.2, -1])
import scipy.interpolate
exp_nll_ratios = {}
color = [ROOT.kBlue, ROOT.kRed, ROOT.kOrange, ROOT.kRed, ROOT.kGreen, ROOT.kMagenta+2, ROOT.kBlue-4, ROOT.kOrange-2, ROOT.kPink-9, ROOT.kBlue-2, ROOT.kRed-2, ROOT.kGreen-2, ROOT.kCyan-2, ROOT.kMagenta-2, ROOT.kCyan+3, ROOT.kOrange, ROOT.kRed, ROOT.kGreen, ROOT.kCyan, ROOT.kMagenta]
levels = [0, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1.]
nb = len(levels)-1
if not (args.combine_models):  
    limits = {}
    nbins = nbins+1
    logging.info("plotting 1D LLR")
    for idx, model in enumerate(allmodels):
        k = 0
        j = 0
        for shape in [False, True]:
            exp_nll_ratio = []
            histos = []

            for theta in theta_: 
                w_sm   =   lumi /np.sum(y[:,0]) * config.xsec[sample]* 1000 * y[:,0] 
                stack_weights = y[:,0] + theta * y[:,index_lin[model]]+ theta**2 * y[:,index_quad[model]]
                if shape: w_bsm  =   lumi /np.sum(stack_weights) * config.xsec[sample]* 1000 * stack_weights
                else: 
                    w_bsm  =   lumi /np.sum(y[:,0]) * config.xsec[sample]* 1000 * stack_weights
                
                t_theta = Z[model][:,0]  + theta *  Z[model][:,1] 
                # t_theta = 1+ Z[model][:,0] * theta#+theta * Z[model][:,1] * 0.5 
                
                binning = np.quantile(t_theta, levels)
                np_histo_sm  = np.histogram(t_theta, bins=binning, weights = w_sm  ) 
                np_histo_bsm = np.histogram(t_theta, bins=binning, weights = w_bsm  ) 
                
                if args.plot_histos:
                    if (j%5==0):
                        histo_bsm    = make_TH1F(np_histo_bsm)
                        histo_bsm.legendText = "#theta="+"{:.2f}".format(theta)
                        histo_bsm.style       = styles.lineStyle( color[k%len(color)])
                        histos.append( histo_bsm )
                        #k = k+1
                j = j+1    
                np_histo_sm_ = np_histo_sm
                np_histo_sm  = np_histo_sm[0]
                np_histo_bsm = np_histo_bsm[0]
                if any(np_histo_sm)==0: assert False
                
                exp_nll_ratio_ =2*np.sum(np_histo_sm - np_histo_bsm - np_histo_bsm*np.log(np_histo_sm/np_histo_bsm))
                exp_nll_ratio.append(exp_nll_ratio_)
                
            histo_sm     = make_TH1F(np_histo_sm_)
            k = k+1
            histo_sm.legendText  = "SM"
            histo_sm.style       = styles.lineStyle( ROOT.kBlack, dashed = True)
            histos.append( histo_sm )    
            drawObjects = [ ]
            
     
            if args.plot_histos:
                subdir = "shape_effects_only" if args.shape_effects_only else "full_information"
                plot = Plot.fromHisto( os.path.join(subdir, EFTCoefficients[model]+"_test_stat"), [[h] for h in histos], texX = "t_{#theta}, quantiles", texY = "Entries" )
                plotting.draw( plot,
                        plot_directory = os.path.join(args.output_directory,sample,SUBDIR, "histograms"),
                        #ratio          = {'yRange':(0.6,1.4)} if len(plot.stack)>=2 else None,
                        logX = False, logY = True, sorting = False,
                        yRange = (args.lumi*config.xsec[sample]*1000/nb*0.5, args.lumi*config.xsec[sample]*1000/nb*5) if args.shape_effects_only else (args.lumi*config.xsec[sample]*1000/nb*0.7, args.lumi*config.xsec[sample]*1000/nb*3),
                        legend         = ( (0.2,0.65,0.92,0.9),3),
                        drawObjects    = drawObjects,
                        copyIndexPHP   = True,
                        extensions     = ["png", "pdf"],
                      )
                copyIndexPHP(os.path.join(args.output_directory, sample, SUBDIR, "histograms", subdir) )
            Model = model + "shape" if shape else model + "full"    
            exp_nll_ratios[model] = exp_nll_ratio  
            limits[Model] = ROOT.TGraph(len(exp_nll_ratio), array('d',theta_), array('d',exp_nll_ratio))
            limits[Model+'_4'] = ROOT.TGraph(len(exp_nll_ratio), array('d',theta_), array('d',np.ones(len(exp_nll_ratio))*4))
            limits[Model+'_1'] = ROOT.TGraph(len(exp_nll_ratio), array('d',theta_), array('d',np.ones(len(exp_nll_ratio))))
            limits[Model].SetLineColor(color[idx+k-1])
            limits[Model].SetLineWidth(2)
            limits[Model].SetMarkerStyle(1)
            limits[Model+'_4'].SetLineStyle(7)
            limits[Model+'_1'].SetLineStyle(7)
            interp_fn = scipy.interpolate.interp1d(theta_, exp_nll_ratio, 'linear', fill_value="extrapolate")
            interp_fn4 = lambda x: interp_fn(x)-4
            interp_fn1 = lambda x: interp_fn(x)-1
            
            if not args.no14:
            # auto search for vicinity
                for i in range (len(exp_nll_ratio)-1):
                    if exp_nll_ratio[i] <= 4 and exp_nll_ratio[i+1] >= 4: r4 = theta_[i]
                    if exp_nll_ratio[i] <= 1 and exp_nll_ratio[i+1] >= 1: r1 = theta_[i]
                try: 
                    r4
                except NameError:
                    print("NameError: r4 does not exist. args.range_theta too small?")
                if (r4 < th):   
                    root1, root2 = optimize.newton(interp_fn4, -r4,maxiter=500), optimize.newton(interp_fn4, r4,maxiter=500)
                else: root1, root2 = -th, th
                if (r1 < th):   
                    root3, root4 = optimize.newton(interp_fn1, -r1,maxiter=500), optimize.newton(interp_fn1, r1,maxiter=500)
                else: root3, root4 = -th, th    
        
                limits[Model+'_interp4'] = ROOT.TBox(root1, 5, root2, 0)
                limits[Model+'_interp4'].SetFillColorAlpha(color[0], 0.1)
                limits[Model+'_interp1'] = ROOT.TBox(root3, 5, root4, 0)
                limits[Model+'_interp1'].SetFillColorAlpha(color[1], 0.1)
            exp_nll_ratios[Model+'_label'] = "shape only" if shape else "full information"
        
    c1 = ROOT.TCanvas()
    c1.SetCanvasSize(1000, 1500);
    c1.SetWindowSize(2,3);
    limits[args.models[0]+"shape"].Draw("AC")
    for idx, model in enumerate(allmodels):
        for shape in [True, False]:
            Model = model + "shape" if shape else model + "full"    
            limits[Model].SetMarkerColor(color[idx]);
            limits[Model].SetMarkerSize(1.5);
            limits[Model].SetMarkerStyle(0);
            limits[Model].Draw("SAMEPC")
            limits[Model].SetTitle()
            limits[Model].GetXaxis().SetTitle("#theta")
            limits[Model].GetYaxis().SetTitle(sample.replace('_MS', '') + ', '+EFTCoefficients[model])
            limits[Model].GetXaxis().SetRangeUser(-th,th)
            limits[Model].GetYaxis().SetRangeUser(0,5)
            if not args.no14:
                limits[Model+'_interp1'].Draw("SAME")
                limits[Model+'_interp4'].Draw("SAME")
            limits[Model+'_1'].Draw("SAME")
            limits[Model+'_4'].Draw("SAME")
        
    l = ROOT.TLegend(0.75, 0.18, 0.95, 0.35)
    l.SetFillStyle(0)
    l.SetTextSize(0.03)
    l.SetShadowColor(ROOT.kWhite)
    l.SetBorderSize(0)
    # for model in allmodels:
        # for shape in [True, False]:
            # Model = model + "shape" if shape else model + "full"    
            # l.AddEntry( limits[Model], exp_nll_ratios[Model+'_label'], "l" )
    # l.Draw()    
    c1.RedrawAxis()
    ROOT.gStyle.SetOptStat(0)    
    
else: 
    th = args.theta_range_comb[0]
    TH = args.theta_range_comb[1]

    nbins = 30

    theta_ = np.linspace(-th,th,nbins)
    THETA_ = np.linspace(-TH,TH,nbins)
    logging.info("plotting 2D LLR")
    limits = ROOT.TH2F("", "2D limits", nbins, -th, th, nbins, -TH, TH)  
    k = 0
    for h in range(len(theta_)): 
        for g in range(len(THETA_)): 
            theta_0 = theta_[h]
            theta_1 = THETA_[g]
            theta__ = [theta_0, theta_1]
            
            w_sm   =   lumi /np.sum(y[:,0]) * config.xsec[sample]* 1000 * y[:,0] 
            t_theta = np.ones(y[:,0].shape).astype("float64")
         
            stack_weights = y[:,0] #SM weight
            for idx, model in enumerate(allmodels):
                stack_weights = stack_weights + theta__[idx] * y[:,index_lin[model]] + theta__[idx]**2 * y[:,index_quad[model]]
                t_theta = (t_theta + theta__[idx] * Z[model][:,0]  + theta__[idx]**2 * Z[model][:,1] ).astype("float64")
            
            stack_weights = stack_weights + theta_0*theta_1 * y[:,index_mixed]
            if args.shape_effects_only: w_bsm  =   lumi /np.sum(stack_weights) * config.xsec[sample]* 1000 * stack_weights 
            else: w_bsm  =   lumi /np.sum(y[:,0]) * config.xsec[sample]* 1000 * stack_weights
            
            # t_theta_argsort     = np.argsort(t_theta)
            # t_theta_argsort_inv = np.argsort(t_theta_argsort)
            # cdf_sm = np.cumsum(w_sm[t_theta_argsort])
            # cdf_sm/=cdf_sm[-1]
            
            # cdf_map = make_cdf_map( t_theta[t_theta_argsort], cdf_sm )
           
            # t_theta_cdf = cdf_map( t_theta )
            # nb=10
            # binning = np.linspace(0, 1, nb+1)
            binning = np.quantile(t_theta, levels)
            np_histo_sm  = np.histogram(t_theta, bins=binning, weights = w_sm  ) [0]
            np_histo_bsm = np.histogram(t_theta, bins=binning, weights = w_bsm  ) [0]
                    
            exp_nll_ratio_ =2*np.sum(np_histo_sm - np_histo_bsm - np_histo_bsm*np.log(np_histo_sm/np_histo_bsm))
            limits.SetBinContent(h+1,g+1, exp_nll_ratio_)
            k+=1

    def DrawPaletteLabel():
        textCOLZ = ROOT.TLatex(0.98,0.15,"Observed significance [#sigma]")
        textCOLZ.SetNDC()
        #textCOLZ.SetTextAlign(13)
        textCOLZ.SetTextFont(42)
        textCOLZ.SetTextSize(0.045)
        textCOLZ.SetTextAngle(90)
        textCOLZ.Draw()
        c1.textCOLZ = textCOLZ

    NRGBs = 5
    NCont = 255
    stops = array("d",[0.00, 0.34, 0.61, 0.84, 1.00])
    red= array("d",[0.50, 0.50, 1.00, 1.00, 1.00])
    green = array("d",[ 0.50, 1.00, 1.00, 0.60, 0.50])
    blue = array("d",[1.00, 1.00, 0.50, 0.40, 0.50])
    ROOT.TColor.CreateGradientColorTable(NRGBs, stops, red, green, blue, NCont)
    ROOT.gStyle.SetNumberContours(NCont)


    c1 = ROOT.TCanvas()
    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetOptTitle(0)    
    c1.SetCanvasSize(2380, 2000);
    c1.SetRightMargin(0.19)
    c1.SetTopMargin(0.08)
    c1.SetLeftMargin(0.14)
    c1.SetBottomMargin(0.14)
    c1.SetLogz()
    c1.cd()
    limits.Draw("COLZ")
    ROOT.gPad.Update()
    limits.SetTitle("")
    limits.GetXaxis().SetTitle(EFTCoefficients[allmodels[0]])
    limits.GetYaxis().SetTitle(EFTCoefficients[allmodels[1]])

    limits.GetZaxis().SetRangeUser(0.5*1e-04,1e+03 )

    c1.RedrawAxis()
    c1.RedrawAxis()
    palette = limits.GetListOfFunctions().FindObject("palette")

    palette.SetX1NDC(1.-0.18)
    palette.SetY1NDC(0.14)
    palette.SetX2NDC(1.-0.13)
    palette.SetY2NDC(1.-0.08)
    palette.SetLabelFont(42)
    palette.SetLabelSize(0.035)
    DrawPaletteLabel()

    limits.DrawCopy("COLZ")
    levels = [2.3, 6.18]
    contours = array("d", levels) 
    limits.SetContour(2, contours )
    limits.Draw("CONT3 same")

coeffs = "" 
EFT =  [*set(EFT)] #remove duplicates
for i in range(len(EFT)):
    coeffs = coeffs + "_" + EFT[i]

if (args.combine_models): maindir = "LLR_2D"
if not (args.combine_models): maindir = "LLR_1D"

subdir = "shape_effects_only" if args.shape_effects_only else "full_information"
filename = args.filename+"_"+sample+coeffs+"_LLR" if args.filename is not None else sample+coeffs+"_LLR"
c1.Print(os.path.join(args.output_directory, sample, SUBDIR, maindir, subdir, filename+".png"))
c1.Print(os.path.join(args.output_directory, sample, SUBDIR, maindir, subdir, filename+".pdf"))
copyIndexPHP(os.path.join(args.output_directory, sample, SUBDIR, maindir, subdir) )


if args.plot_histos: logging.info("histos dir link: %s", os.path.join('https://lwild.web.cern.ch/tttt/plots/', os.path.basename(os.path.normpath(args.output_directory)), sample, SUBDIR, "histograms" )) 
logging.info("LLR plot link:   %s", os.path.join('https://lwild.web.cern.ch/tttt/plots/', os.path.basename(os.path.normpath(args.output_directory)), sample, SUBDIR, maindir, subdir, filename+".png")) 
   

Analysis.Tools.syncer.sync()
