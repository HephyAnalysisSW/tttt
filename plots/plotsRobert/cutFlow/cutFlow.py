import ROOT

from RootTools.core.standard import *

from tttt.Tools.cutInterpreter import cutInterpreter

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',       action='store',      default='INFO', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--selection',      action='store',      default='2lSS', nargs='?', choices=['2lSS', '3l', '4l'], help="which selection?")
argParser.add_argument('--small',                             action='store_true', help='Run only on a small subset of the data?')
#argParser.add_argument('--sorting',                           action='store', default=None, choices=[None, "forDYMB"],  help='Sort histos?', )
args = argParser.parse_args()

# Logger
import TMB.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

# Simulated samples
import tttt.samples.nano_private_UL20_RunII_postProcessed_dilep as allsamples

weight_string = 'weight' #*reweightTopPt*reweightBTag_SF*reweightLeptonSF*reweightDilepTriggerBackup*reweightPU36fb'

# tight selection AN-2021-182 v7 Table 4
def ele_string( pT = 10):
    return "lep_pt>=%3.2f&&abs(lep_pdgId)==11&&abs(lep_eta)<2.5&&abs(lep_dxy)<0.05&&abs(lep_dz)<0.1&&lep_sip3d<8&&lep_miniPFRelIso_all<0.4&&lep_convVeto&&lep_eleIndex>=0&&Electron_tightCharge[lep_eleIndex]>=2&&lep_lostHits<=1&&lep_mvaTOP>0.81"%pT
# tight selection AN-2021-182 v7 Table 4
def mu_string( pT=10 ):
    return "lep_pt>=%3.2f&&abs(lep_pdgId)==13&&abs(lep_eta)<2.4&&abs(lep_dxy)<0.05&&abs(lep_dz)<0.1&&lep_sip3d<8&&lep_miniPFRelIso_all<0.4&&lep_muIndex>=0&&Muon_mediumId[lep_muIndex]&&lep_mvaTOP>0.64"%pT

def same_sign_leptons (pT=10 ):
    return "Sum$(lep_charge*(%s||%s))"%(mu_string(pT),ele_string(pT))+"&&Sum$(%s)+Sum$(%s)==2"%(mu_string(pT),ele_string(pT))
def n2leptons( pT1=25, pT2=20 ):
    return "Sum$(%s)+Sum$(%s)>=1&&Sum$(%s)+Sum$(%s)==2"%(mu_string(pT1),ele_string(pT1), mu_string(pT2),ele_string(pT2))
def n3leptons( pT1=25, pT2=20, pT3=10):
    return "Sum$(%s)+Sum$(%s)>=1&&Sum$(%s)+Sum$(%s)>=2&&Sum$(%s)+Sum$(%s)==3"%(mu_string(pT1),ele_string(pT1), mu_string(pT2),ele_string(pT2),mu_string(pT3),ele_string(pT3))
def n4leptons( pT1=25, pT2=20, pT3=10):
    return "Sum$(%s)+Sum$(%s)>=1&&Sum$(%s)+Sum$(%s)>=2&&Sum$(%s)+Sum$(%s)==4"%(mu_string(pT1),ele_string(pT1), mu_string(pT2),ele_string(pT2),mu_string(pT3),ele_string(pT3))

#remove k-factors after reprocessing!
allsamples.TTTT.scale = 1.3149511150170272 
allsamples.TTLep.scale= 1.0124257194656598
allsamples.TTW.scale  = 1.1502692119432207 
allsamples.TTZ.scale  = 0.9457478005865103

#Define chains for signals and backgrounds
samples = [
  allsamples.TTTT, 
  allsamples.TTLep, 
  allsamples.TTW, 
  allsamples.TTZ,
  allsamples.TTH,
]

if args.small:
    for sample in samples:
        sample.reduceFiles(to=1)

if args.selection == '2lSS':
    # 2l SS
    cuts=[
    #  ("2l SS",             "$2l SS$",                          same_sign_leptons(10)), 
      ("2lSS 25/20",  "2L SS p_{T}(l_1}>25, p_{T}(l_2)>20",     same_sign_leptons(20)+"&&"+n2leptons(25,20)),
      ("min(m(ll))>12",     "min(m(ll))>12",                    "minDLmass>12"),
      ("Nj>=4",             "N_{jet}>=4",                       "nJetGood>=4"),
      ("Nb>=2",             "N_{b-tag}>=2",                     "nBTag>=2"),
      ("Nj>=6 if Nb==2",    "N_{jet}>=6 if N_{b-tag}==2",       "(nBTag>=3||nJetGood>=6)"),
      ("HT>280",            "H_{T}>280",                        "Sum$(JetGood_pt)>280"),
        ]
elif args.selection == '3l':
    # 3l
    cuts=[
      #("3l",                "$3l",                              "Sum$"), 
      ("l1,l2,l3>25/20/10", "p_{T}(l_1}>25, p_{T}(l_2)>20, p_{T}(l_3)>10",     n3leptons(25,20,10)),
      ("min(m(ll))>12",     "min(m(ll))>12",                    "minDLmass>12"),
      ("Z veto (SF)",       "Z veto",                            "(!(abs(Z1_mass-91.2)<15))"),
      ("Nj>=3",             "N_{jet}>=3",                       "nJetGood>=3"),
      ("Nb>=2",             "N_{b-tag}>=2",                     "nBTag>=2"),
      ("HT>200",            "H_{T}>200",                        "Sum$(JetGood_pt)>200"),
        ]
elif args.selection == '4l':
    # 4l
    cuts=[
      ("l1,l2,l3,l4>25/20/10/10", "p_{T}(l_1}>25, p_{T}(l_2)>20, p_{T}(l_{3,4})>10",     n4leptons(25,20,10)),
      ("min(m(ll))>12",     "min(m(ll))>12",                    "minDLmass>12"),
      ("Z veto (SF)",       "Z veto",                            "(!(abs(Z1_mass-91.2)<15))&&(!(abs(Z2_mass-91.2)<15))"),
      ("Nj>=2",             "N_{jet}>=3",                       "nJetGood>=3"),
      ("Nb>=1",             "N_{b-tag}>=2",                     "nBTag>=2"),
      #("HT>200",            "H_{T}>200",                        "Sum$(JetGood_pt)>200"),
        ]

cutFlowFile = "./cutflow_%s.tex"%args.selection
with open(cutFlowFile, "w") as cf:

    cf.write("\\begin{tabular}{r|"+"|l"*len(samples)+"} \n")
    cf.write( 30*" "+"& "+ " & ".join([ "%13s"%s.texName for s in samples ] )+"\\\\\\hline\n" )
    print 30*" "+ "".join([ "%13s"%s.name for s in samples ] )

    for i in range(len(cuts)):
        r=[]
        for sample in samples:
            selection = "&&".join(c[2] for c in cuts[:i+1])
            #selection = "&&".join(c[2] for c in cuts)
            if selection=="":selection="(1)"
            y = sample.getYieldFromDraw(selection, weight_string+("*%f"%sample.scale if hasattr(sample, "scale") else ""))
            n = sample.getYieldFromDraw(selection, '(1)')
            r.append(y)
        cf.write("%30s"%cuts[i][1]+ "& "+" & ".join([ " %12.1f"%r[j]['val'] for j in range(len(r))] )+"\\\\\n")
        print "%30s"%cuts[i][0]+ "".join([ " %12.1f"%r[j]['val'] for j in range(len(r))] )

    cf.write("\\end{tabular} \n")
    cf.write("\\caption{ Cutflow.} \n")
