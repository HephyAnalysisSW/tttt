import ROOT,os
from tttt.Tools.Plotter import Plotter
from tttt.samples.color import color
from tttt.Tools.user    import plot_directory
import Analysis.Tools.syncer

import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',       action='store',      default='INFO', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--noData',         action='store_true', help='Do not plot data.')
argParser.add_argument('--plot_directory', action='store', default='4t-syst')
argParser.add_argument('--input_directory', action='store', default='4t-syst')
argParser.add_argument('--selection',      action='store', default='trg-dilepL-minDLmass20-offZ1-njet4p-btag2p-ht500')
argParser.add_argument('--small',         action='store_true', default=False,      help='Run only on a small subset of the data?')
argParser.add_argument('--level',       action='store',     default='SM',       help='Plot at SM or EFT point')
args = argParser.parse_args()

import tttt.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)


hist_dir = os.path.join(plot_directory, 'analysisPlots', args.input_directory, 'RunII', "all", args.selection)
if args.small: 
  #hist_dir += "_small"
  args.input_directory += "_small"
if args.level == "EFT":
  args.input_directory += "_EFTpoint"

nominalSample = ROOT.TFile.Open(os.path.join(hist_dir, "tttt_central.root"))
#EFTSample = ROOT.TFile.Open(os.path.join(hist_dir, "tttt_EFTs.root"))

systematics = [ 
        {"name" : "LeptonSF", "color" : ROOT.kTeal-9, "type":"experimental",
                "up" :  ROOT.TFile.Open(os.path.join(hist_dir, "tttt_LeptonSFUp.root")),
                "down": ROOT.TFile.Open(os.path.join(hist_dir, "tttt_LeptonSFDown.root"))},
		{"name" : "PU", "color" : ROOT.kAzure+2, "type":"experimental",
                "up" :  ROOT.TFile.Open(os.path.join(hist_dir, "tttt_PUUp.root")),
                "down": ROOT.TFile.Open(os.path.join(hist_dir, "tttt_PUDown.root"))},
		{"name" : "L1Prefire", "color" : ROOT.kBlue+2, "type":"experimental",
                "up" :  ROOT.TFile.Open(os.path.join(hist_dir, "tttt_L1PrefireUp.root")),
                "down": ROOT.TFile.Open(os.path.join(hist_dir, "tttt_L1PrefireDown.root"))},
#                {"name" : "BTagSFJes", "color" : ROOT.kBlue, "type":"experimental",
#                "up" :  ROOT.TFile.Open(os.path.join(hist_dir, "tttt_BTagSFJesUp.root")),
#                "down": ROOT.TFile.Open(os.path.join(hist_dir, "tttt_BTagSFJesDown.root"))},
		{"name" : "BTagSFHf", "color" : ROOT.kPink+2, "type":"experimental",
                "up" :  ROOT.TFile.Open(os.path.join(hist_dir, "tttt_BTagSFHfUp.root")),
                "down": ROOT.TFile.Open(os.path.join(hist_dir, "tttt_BTagSFHfDown.root"))},
		{"name" : "BTagSFHfs1", "color" : ROOT.kPink-8, "type":"experimental",
                "up" :  ROOT.TFile.Open(os.path.join(hist_dir, "tttt_BTagSFHfs1Up.root")),
                "down": ROOT.TFile.Open(os.path.join(hist_dir, "tttt_BTagSFHfs1Down.root"))},
		{"name" : "BTagSFHfs2", "color" : ROOT.kPink-7, "type":"experimental",
                "up" :  ROOT.TFile.Open(os.path.join(hist_dir, "tttt_BTagSFHfs2Up.root")),
                "down": ROOT.TFile.Open(os.path.join(hist_dir, "tttt_BTagSFHfs2Down.root"))},
		{"name" : "BTagSFLf",  "color" : ROOT.kBlue-2, "type":"experimental",
                "up" :  ROOT.TFile.Open(os.path.join(hist_dir, "tttt_BTagSFLfUp.root")),
                "down": ROOT.TFile.Open(os.path.join(hist_dir, "tttt_BTagSFLfDown.root"))},
		{"name" : "BTagSFLfs1",  "color" : ROOT.kPink+7, "type":"experimental",
                "up" :  ROOT.TFile.Open(os.path.join(hist_dir, "tttt_BTagSFLfs1Up.root")),
                "down": ROOT.TFile.Open(os.path.join(hist_dir, "tttt_BTagSFLfs1Down.root"))},
		{"name" : "BTagSFLfs2", "color" : ROOT.kCyan+2, "type":"experimental",
                "up" :  ROOT.TFile.Open(os.path.join(hist_dir, "tttt_BTagSFLfs2Up.root")),
                "down": ROOT.TFile.Open(os.path.join(hist_dir, "tttt_BTagSFLfs2Down.root"))},
		{"name" : "BTagSFCfe1", "color" : ROOT.kBlue-4, "type":"experimental",
                "up" :  ROOT.TFile.Open(os.path.join(hist_dir, "tttt_BTagSFCfe1Up.root")),
                "down": ROOT.TFile.Open(os.path.join(hist_dir, "tttt_BTagSFCfe1Down.root"))},
		{"name" : "BTagSFCfe2", "color" : ROOT.kBlue+4, "type":"experimental",
                "up" :  ROOT.TFile.Open(os.path.join(hist_dir, "tttt_BTagSFCfe2Up.root")),
                "down": ROOT.TFile.Open(os.path.join(hist_dir, "tttt_BTagSFCfe2Down.root"))}, 
		{"name" : "jesTotal", "color" : ROOT.kCyan, "type":"experimental",
                "up" :  ROOT.TFile.Open(os.path.join(hist_dir, "tttt_jesTotalUp.root")),
                "down": ROOT.TFile.Open(os.path.join(hist_dir, "tttt_jesTotalDown.root"))},
		{"name" : "DYISR", "color" : ROOT.kMagenta-1,  "type":"theoretical",
				"up" :  ROOT.TFile.Open(os.path.join(hist_dir, "tttt_DYISRUp.root")),
				"down": ROOT.TFile.Open(os.path.join(hist_dir, "tttt_DYISRDown.root"))},
#		{"name" : "DYFSR", "color" : ROOT.kMagenta-5,  "type":"theoretical",
#				"up" :  ROOT.TFile.Open(os.path.join(hist_dir, "tttt_DYFSRUp.root")),
#				"down": ROOT.TFile.Open(os.path.join(hist_dir, "tttt_DYFSRDown.root"))}, 
		{"name" : "TTTTISR", "color" : ROOT.kMagenta,  "type":"theoretical",
				"up" :  ROOT.TFile.Open(os.path.join(hist_dir, "tttt_TTTTISRUp.root")),
				"down": ROOT.TFile.Open(os.path.join(hist_dir, "tttt_TTTTISRDown.root"))},
		{"name" : "TTbbISR", "color" : ROOT.kMagenta,  "type":"theoretical",
				"up" :  ROOT.TFile.Open(os.path.join(hist_dir, "tttt_TTbbISRUp.root")),
				"down": ROOT.TFile.Open(os.path.join(hist_dir, "tttt_TTbbISRDown.root"))},
		{"name" : "TTccISR", "color" : ROOT.kMagenta,  "type":"theoretical",
				"up" :  ROOT.TFile.Open(os.path.join(hist_dir, "tttt_TTccISRUp.root")),
				"down": ROOT.TFile.Open(os.path.join(hist_dir, "tttt_TTccISRDown.root"))},
		{"name" : "TTlightISR", "color" : ROOT.kMagenta,  "type":"theoretical",
				"up" :  ROOT.TFile.Open(os.path.join(hist_dir, "tttt_TTlightISRUp.root")),
				"down": ROOT.TFile.Open(os.path.join(hist_dir, "tttt_TTlightISRDown.root"))},
		{"name" : "FSR", "color" : ROOT.kMagenta+2,  "type":"theoretical",
				"up" :  ROOT.TFile.Open(os.path.join(hist_dir, "tttt_FSRUp.root")),
				"down": ROOT.TFile.Open(os.path.join(hist_dir, "tttt_FSRDown.root"))}, 
		{"name" : "noTopPtReweight", "color" : ROOT.kBlue-9,  "type":"experimental",
				"up" :  ROOT.TFile.Open(os.path.join(hist_dir, "tttt_noTopPtReweight.root")),
				"down": ROOT.TFile.Open(os.path.join(hist_dir, "tttt_central.root"))},
#		{"name" : "DYrenormalization", "color" : ROOT.kAzure+1,  "type":"theoretical",
#				"up" :  ROOT.TFile.Open(os.path.join(hist_dir, "tttt_DYrenormalizationShapeUp.root")),
#				"down": ROOT.TFile.Open(os.path.join(hist_dir, "tttt_DYrenormalizationShapeDown.root"))},
#		{"name" : "DYFactorization", "color" : ROOT.kCyan,  "type":"theoretical",
#				"up" :  ROOT.TFile.Open(os.path.join(hist_dir, "tttt_DYFactorizationShapeUp.root")),
#				"down": ROOT.TFile.Open(os.path.join(hist_dir, "tttt_DYFactorizationShapeDown.root"))},
#		{"name" : "TTrenormalization", "color" : ROOT.kGreen+3,  "type":"theoretical",
#				"up" :  ROOT.TFile.Open(os.path.join(hist_dir, "tttt_TTrenormalizationShapeUp.root")),
#				"down": ROOT.TFile.Open(os.path.join(hist_dir, "tttt_TTrenormalizationShapeDown.root"))},
#		{"name" : "TTFactorization", "color" : ROOT.kGreen-7,  "type":"theoretical",
#				"up" :  ROOT.TFile.Open(os.path.join(hist_dir, "tttt_TTFactorizationShapeUp.root")),
#				"down": ROOT.TFile.Open(os.path.join(hist_dir, "tttt_TTFactorizationShapeDown.root"))},
#		{"name" : "TTbbrenormalization", "color" : ROOT.kRed,  "type":"theoretical",
#				"up" :  ROOT.TFile.Open(os.path.join(hist_dir, "tttt_TTbbrenormalizationShapeUp.root")),
#				"down": ROOT.TFile.Open(os.path.join(hist_dir, "tttt_TTbbrenormalizationShapeDown.root"))},
#		{"name" : "TTbbFactorization", "color" : ROOT.kPink-9,  "type":"theoretical",
#				"up" :  ROOT.TFile.Open(os.path.join(hist_dir, "tttt_TTbbFactorizationShapeUp.root")),
#				"down": ROOT.TFile.Open(os.path.join(hist_dir, "tttt_TTbbFactorizationShapeDown.root"))},
#		{"name" : "TTccrenormalization", "color" : ROOT.kViolet,  "type":"theoretical",
#				"up" :  ROOT.TFile.Open(os.path.join(hist_dir, "tttt_TTccrenormalizationShapeUp.root")),
#				"down": ROOT.TFile.Open(os.path.join(hist_dir, "tttt_TTccrenormalizationShapeDown.root"))},
#		{"name" : "TTccFactorization", "color" : ROOT.kViolet-6,  "type":"theoretical",
#				"up" :  ROOT.TFile.Open(os.path.join(hist_dir, "tttt_TTccFactorizationShapeUp.root")),
#				"down": ROOT.TFile.Open(os.path.join(hist_dir, "tttt_TTccFactorizationShapeDown.root"))},
#		{"name" : "TTlightrenormalization", "color" : ROOT.kOrange,  "type":"theoretical",
#				"up" :  ROOT.TFile.Open(os.path.join(hist_dir, "tttt_TTlightrenormalizationShapeUp.root")),
#				"down": ROOT.TFile.Open(os.path.join(hist_dir, "tttt_TTlightrenormalizationShapeDown.root"))},
#		{"name" : "TTlightFactorization", "color" : ROOT.kOrange-3,  "type":"theoretical",
#				"up" :  ROOT.TFile.Open(os.path.join(hist_dir, "tttt_TTlightFactorizationShapeUp.root")),
#				"down": ROOT.TFile.Open(os.path.join(hist_dir, "tttt_TTlightFactorizationShapeDown.root"))},
#		{"name" : "TTTTrenormalization", "color" : ROOT.kBlue+2,  "type":"theoretical",
#				"up" :  ROOT.TFile.Open(os.path.join(hist_dir, "tttt_TTTTrenormalizationShapeUp.root")),
#				"down": ROOT.TFile.Open(os.path.join(hist_dir, "tttt_TTTTrenormalizationShapeDown.root"))},
#		{"name" : "TTTTFactorization", "color" : ROOT.kBlue,  "type":"theoretical",
#				"up" :  ROOT.TFile.Open(os.path.join(hist_dir, "tttt_TTTTFactorizationShapeUp.root")),
#				"down": ROOT.TFile.Open(os.path.join(hist_dir, "tttt_TTTTFactorizationShapeDown.root"))},
		{"name" : "HDamp", "color" : ROOT.kCyan+3,  "type":"theoretical",
				"up" :  ROOT.TFile.Open(os.path.join(hist_dir, "tttt_HDampUp.root")),
				"down": ROOT.TFile.Open(os.path.join(hist_dir, "tttt_HDampDown.root"))},
		{"name" : "scale", "color" : ROOT.kGreen-1,  "type":"theoretical",
				"up" :  ROOT.TFile.Open(os.path.join(hist_dir, "tttt_ScaleUpUp.root")),
				"down": ROOT.TFile.Open(os.path.join(hist_dir, "tttt_ScaleDownDown.root"))},
              ]

PDFs = []
for i in range(1,100):
	PDFs += [{"name" : "PDF_%s"%i,
	"up": ROOT.TFile.Open(os.path.join(hist_dir, "tttt_PDF_%s.root"%i))}]


mc = [  {"name": "TTLep_bb", "legendText" : "t#bar{t}b#bar{b}", "color" : color.TTbb},
	    {"name": "TTLep_cc", "legendText" : "t#bar{t}c#bar{c}", "color" : color.TTcc},
	    {"name": "TTLep_other", "legendText" : "t#bar{t} + light j.", "color" : color.TTlight},
		#       {"name": "ST", "legendText" : "t/tW"},
		{"name": "ST_tch", "legendText" : "t", "color" : color.T},
		{"name": "ST_twch", "legendText" : "tW", "color" : color.tW},
		{"name": "TTW", "legendText" : "t#bar{t}W", "color" : color.TTW},
		{"name": "TTH", "legendText" : "t#bar{t}H", "color" : color.TTH},
		{"name": "TTZ", "legendText" : "t#bar{t}Z", "color" : color.TTZ},
		{"name": "TTTT", "legendText" : "t#bar{t}t#bar{t}", "color" : color.TTTT}, 
		{"name": "DY", "legendText" : "DY", "color" : color.DY},
		{"name": "DiBoson", "legendText" : "DiBoson", "color" : color.DiBoson},

	]

#if args.level == "SM":
#  mc+= {"name": "TTLep_bb", "legendText" : "t#bar{t}b#bar{b}"}
#elif args.level == "EFT":
#  mc+= {"name": "sm_lin_quad", "legendText" : "t#bar{t}b#bar{b} at c_{#alpha}=1"}

plots = [{"name" : "nJetGood" ,     "texX": "N_{Jet}", "texY" : 'Number of Events'},
         {"name" : "nBTag",         "texX": "N_{BJet}", "texY" : 'Number of Events'},
#         {"name" : "mu0_pt",        "texX" : "p_{t}", "texY" : 'Number of Events'},
         {"name" : 'yield',         "texX" : "", "texY" : 'Number of Events'},
#         {"name" : 'nVtxs',         "texX" : 'vertex multiplicity', "texY" : 'Number of Events'},
         {"name" : 'l1_pt',         "texX" : 'p_{T}(l_{1}) (GeV)', "texY" : 'Number of Events'},
         {"name" : 'l1_eta',        "texX" : '#eta(l_{1})', "texY" : 'Number of Events'},
         {"name" : 'l1_mvaTOP',     "texX" : 'MVA_{TOP}(l_{1})', "texY" : 'Number of Events'},
         {"name" : 'l1_mvaTOPWP',   "texX" : 'MVA_{TOP}(l_{1}) WP', "texY" : 'Number of Events'},
         {"name" : 'l2_pt',         "texX" : 'p_{T}(l_{2}) (GeV)', "texY" : 'Number of Events'},
         {"name" : 'l2_eta',        "texX" : '#eta(l_{2})', "texY" : 'Number of Events'},
         {"name" : 'l2_mvaTOP',     "texX" : 'MVA_{TOP}(l_{2})', "texY" : 'Number of Events'},
         {"name" : 'l2_mvaTOPWP',   "texX" : 'MVA_{TOP}(l_{1}) WP', "texY" : 'Number of Events'},
         {"name" : "met_pt",        "texX" : 'E_{T}^{miss} (GeV)', "texY" : 'Number of Events / 20 GeV'},
         {"name" : "met_phi",       "texX" : '#phi(E_{T}^{miss})', "texY" :  'Number of Events / 20 GeV'},
#         {"name" : "Z1_pt",         "texX" : 'p_{T}(Z_{1}) (GeV)', "texY" : 'Number of Events / 20 GeV'},
#         {"name" : 'Z1_pt_coarse',  "texX" : 'p_{T}(Z_{1}) (GeV)', "texY" : 'Number of Events / 50 GeV'},
#         {"name" : 'Z1_pt_superCoarse', "texX" : 'p_{T}(Z_{1}) (GeV)', "texY" : 'Number of Events'},
#         {"name" : 'lep1_pt',       "texX" : 'p_{T}(leading l) (GeV)', "texY" : 'Number of Events / 20 GeV'},
#         {"name" : 'lep2_pt',       "texX" : 'p_{T}(subleading l) (GeV)', "texY" : 'Number of Events / 10 GeV'},
#         {"name" : 'lep3_pt',       "texX" : 'p_{T}(trailing l) (GeV)', "texY" : 'Number of Events / 10 GeV'},
#         {"name" : "Z1_mass",       "texX" : 'M(ll) (GeV)', "texY" : 'Number of Events / 20 GeV'},
#         {"name" : "Z1_mass_wide",  "texX" : 'M(ll) (GeV)', "texY" : 'Number of Events / 2 GeV'},
#         {"name" : "Z1_cosThetaStar", "texX" : 'cos#theta(l-)', "texY" : 'Number of Events / 0.2'},
#         {"name" : "Z2_mass_wide",  "texX" : 'M(ll) of 2nd OSDL pair', "texY" : 'Number of Events / 2 GeV'},
         {"name" : "minDLmass",     "texX" : 'min mass of all DL pairs', "texY" : 'Number of Events / 2 GeV'},
#         {"name" : "Z1_lldPhi",     "texX" : '#Delta#phi(Z_{1}(ll))', "texY" : 'Number of Events'},
#         {"name" : "Z1_lldR",       "texX" : '#Delta R(Z_{1}(ll))', "texY" : 'Number of Events'},
         {"name" : "ht",            "texX" : 'H_{T} (GeV)', "texY" : 'Number of Events'},
    	 {"name" : "htb",            "texX" : 'H_{T}b (GeV)', "texY" : 'Number of Events'},
         {"name" : 'jet0_pt',       "texX" : 'p_{T}(leading jet) (GeV)', "texY" : 'Number of Events / 30 GeV'},
         {"name" : 'jet1_pt',       "texX" : 'p_{T}(subleading jet) (GeV)', "texY" : 'Number of Events / 30 GeV'},
#         {"name" : 'jet2_pt',       "texX" : 'p_{T}(jet2) (GeV)', "texY" : 'Number of Events / 30 GeV'},
#         {"name" : 'jet3_pt',       "texX" : 'p_{T}(jet3) (GeV)', "texY" : 'Number of Events / 30 GeV'},
#         {"name" : 'jet4_pt',       "texX" : 'p_{T}(jet4) (GeV)', "texY" : 'Number of Events / 30 GeV'},
#         {"name" : 'jet5_pt',       "texX" : 'p_{T}(jet5) (GeV)', "texY" : 'Number of Events / 30 GeV'},
#         {"name" : 'jet6_pt',       "texX" : 'p_{T}(jet6) (GeV)', "texY" : 'Number of Events / 30 GeV'},
#         {"name" : 'jet7_pt',       "texX" : 'p_{T}(jet7) (GeV)', "texY" : 'Number of Events / 30 GeV'},
#         {"name" : 'jet0_eta',       "texX" : '#eta(leading jet) (GeV)', "texY" : 'Number of Events / 30 GeV'},
#         {"name" : 'jet1_eta',       "texX" : '#eta(subleading jet) (GeV)', "texY" : 'Number of Events / 30 GeV'},
#         {"name" : 'jet0_phi',       "texX" : '#phi(leading jet) (GeV)', "texY" : 'Number of Events / 30 GeV'},
#         {"name" : 'jet1_phi',       "texX" : '#phi(subleading jet) (GeV)', "texY" : 'Number of Events / 30 GeV'},
#         {"name" : 'Btagging_discriminator_value_Jet0',       "texX" : 'DeepB J0', "texY" : 'Number of Events'},
#         {"name" : 'Btagging_discriminator_value_Jet1',       "texX" : 'DeepB J1', "texY" : 'Number of Events'},	
	 {"name" : "2l_4t",	    "texX" : "2l_4t", "texY" : "Number of Events"},
	 {"name" : "2l_ttbb",	    "texX" : "2l_ttbb", "texY" : "Number of Events"},
	 {"name" : "2l_ttcc",  	    "texX" : "2l_ttcc", "texY" : "Number of Events"},
	 {"name" : "2l_ttlight",    "texX" : "2l_ttlight", "texY" : "Number of Events"},
#	 {"name" : "nJetGood_pt30" ,     "texX": "N_{Jet}", "texY" : 'Number of Events'},
#	 {"name" : "nJetGood_pt40" ,     "texX": "N_{Jet}", "texY" : 'Number of Events'},
#	 {"name" : "nJetGood_pt50" ,     "texX": "N_{Jet}", "texY" : 'Number of Events'},
#	 {"name" : "nJetGood_pt80" ,     "texX": "N_{Jet}", "texY" : 'Number of Events'},
#	 {"name" : "nJetGood_pt100" ,     "texX": "N_{Jet}", "texY" : 'Number of Events'},
#	 {"name" : "nJetGood_pt150" ,     "texX": "N_{Jet}", "texY" : 'Number of Events'},
#	 {"name" : "nJetGood_pt200" ,     "texX": "N_{Jet}", "texY" : 'Number of Events'},
#	 {"name" : "ISRJet_pt40",         "texX" : " p_{T}(ISR j)>40 ", "texY" : "Number of Events"},
#	 {"name" : "ISRJet_pt50",         "texX" : " p_{T}(ISR j)>50 ", "texY" : "Number of Events"},
#	 {"name" : "ISRJet_pt60",         "texX" : " p_{T}(ISR j)>60 ", "texY" : "Number of Events"},
#	 {"name" : "ISRJet_pt80",         "texX" : " p_{T}(ISR j)>80 ", "texY" : "Number of Events"},
#	 {"name" : "htPt40",		"texX" : " H_{T} from p_{T}(j)>40 ", "texY" : "Number of Events"},
#	 {"name" : "htPt50",		"texX" : " H_{T} from p_{T}(j)>50 ", "texY" : "Number of Events"},
#	 {"name" : "htPt80",		"texX" : " H_{T} from p_{T}(j)>80 ", "texY" : "Number of Events"},
#	 {"name" : "2l_4t_course", 	    "texX" : "tttt_2l_TTTT", "texY" : "Number of Events"},
#	 {"name" : "2l_ttbb_course",	    "texX" : "tttt_2l_TTLep_bb", "texY" : "Number of Events"},
#	 {"name" : "2l_ttcc_course",  	    "texX" : "tttt_2l_TTLep_cc", "texY" : "Number of Events"},
#	 {"name" : "2l_ttlight_course",     "texX" : "tttt_2l_TTLep_other", "texY" : "Number of Events"},


        ]

#for index in range(2):
#    for i, lep_name in enumerate(["mu", "ele"]):
#        plots.append({"name" : lep_name+'%i_pt'%index,  "texX" : 'p_{T}(%s_{%i}) (GeV)'%(lep_name, index), "texY" : 'Number of Events' })
#        plots.append({"name" : lep_name+'%i_eta'%index, "texX" : '#eta(%s_{%i})'%(lep_name, index), "texY" : 'Number of Events' })
#        plots.append({"name" : lep_name+'%i_phi'%index, "texX" : '#phi(%s_{%i})'%(lep_name, index), "texY" : 'Number of Events' })
#        plots.append({"name" : lep_name+'%i_dxy'%index, "texX" : 'dxy(%s_{%i})'%(lep_name, index), "texY" : 'Number of Events' })
#        plots.append({"name" : lep_name+'%i_dz'%index,  "texX" : 'dz(%s_{%i})'%(lep_name, index), "texY" : 'Number of Events' })

EFT_file = ROOT.TFile.Open(os.path.join(hist_dir, "tttt_EFTs.root"))

def getQuadratic(hist_sm, hist_plus, hist_minus):
    #create quad term for EFT
# Since the quadratic term does not change sign, we can get it from the
# histograms where c = +1, c = 0, and c = -1
# (1) c = +1 is SM + LIN + QUAD
# (2) c = -1 is SM - LIN + QUAD
# (3) c =  0 is SM
# Thus, we can get the quad from
# (1)+(2) = SM + SM + QUAD + QUAD | -2*(3)
# (1)+(2)-(3) = QUAD + QUAD       | /2
# 0.5*[(1)+(2)-(3)] = QUAD
   hist_quad = hist_plus.Clone(hist_plus.GetName()+"_quad")
   hist_quad.Add(hist_minus)
   hist_quad.Add(hist_sm, -2)
   hist_quad.Scale(0.5)
   return hist_quad

def getLinear(hist_plus, hist_minus):
    linHist = hist_plus.Clone("line")
    linHist.Add(hist_minus, -1)
    linHist.Scale(0.5)

def getC2(sm,cp1,cm1):
    lin = getLinear(cp1,cm1)
    quad = getQuadratic(sm,cp1,cm1)
    c2Hist = sm.Clone("c2hist")
    c2Hist.Add(lin,2)
    c2Hist.Add(quad,4)
    return c2Hist
  

for j, plot in enumerate(plots):
    plotter = Plotter(plot["name"])
    for sample in mc:
	hist = nominalSample.Get(plot["name"]+"__"+sample["name"])
        plotter.addSample(sample["name"], hist, sample["legendText"], color=sample["color"])

        for i, syst in enumerate(systematics):

            Uphist = syst["up"].Get(plot["name"]+"__"+sample["name"])
            Downhist = syst["down"].Get(plot["name"]+"__"+sample["name"])
            plotter.addSystematic(sample["name"] , syst["name"], Uphist, Downhist, syst["color"], syst["type"])
	
	for j,pdf in enumerate(PDFs):

	    pdfHist = pdf["up"].Get(plot["name"]+"__"+sample["name"])
	    plotter.addPDF(sample["name"] , pdf["name"] , pdfHist)

    if not args.noData:
        datahist = nominalSample.Get(plot["name"]+"__data")
        plotter.addData(datahist)

    SMhist = EFT_file.Get(plot["name"]+"__TTTT_EFT_central")
    Plushist = EFT_file.Get(plot["name"]+"__TTTT_EFT_ctt_+1.000")
    Minushist = EFT_file.Get(plot["name"]+"__TTTT_EFT_ctt_-1.000")
#    print SMhist.GetMaximum()
#    print Plushist.GetMaximum()
#    print Minushist.GetMaximum() 
    C2hist = getC2(SMhist,Plushist,Minushist)
    C2hist_ratio = C2hist.Clone()
    C2hist_ratio.Divide(SMhist)
    Plushist_ratio = Plushist.Clone()
    Plushist_ratio.Divide(SMhist)

    plotter.addLine("ctt1",Plushist,"ctt=1",color=ROOT.kBlue, ratio = Plushist_ratio)
    plotter.addLine("ctt2",C2hist,"ctt=2",color=ROOT.kOrange-3, ratio = C2hist_ratio)

    for log in [True, False]:
        plot_directory_ = os.path.join(plot_directory, 'analysisPlots', args.plot_directory, 'RunII', "all" + ("_log" if log else ""), args.selection)
        plotter.draw(plot_directory_, log, texX = plot["texX"], texY = plot["texY"] , ratio = True, comparisonPlots = False )


EFT_file.Close()
