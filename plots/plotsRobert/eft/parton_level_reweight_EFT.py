import ROOT
from RootTools.core.standard import *
from Analysis.Tools.GenSearch import GenSearch
import Analysis.Tools.syncer
import os
from tttt.Tools.user                     import plot_directory
from WeightInfo import WeightInfo
from HyperPoly  import HyperPoly

# The class "WeightInfo" instanziated with a pkl file contains information on the base points where the EFT weights are computed. 
# It corresponds to this reweight_card:
# https://github.com/HephyAnalysisSW/genproductions/blob/master/bin/MadGraph5_aMCatNLO/addons/cards/SMEFTsim_topU3l_MwScheme_UFO/TTTT_MS/TTTT_MS_reweight_card.dat
#TTbb: 'TTbb_MS_reweight_card.pkl'
weightInfo = WeightInfo('TTTT_MS_reweight_card.pkl')
weightInfo.set_order(2) # polynomial order

print "Coefficients: %i (%s), order: %i number of weights: %i" %( len(weightInfo.variables), ",".join(weightInfo.variables), weightInfo.order,  weightInfo.nid )
print "Here are the polynomial coefficients we will compute:"+  ", ".join(map( lambda s: "("+",".join( s )+")",  weightInfo.combinations ))
print "This is the reference point the sample was generated at: ", weightInfo.ref_point_coordinates

# The following gymnastics is ONLY needed because CMSSW decides, uncomprehensibly, to store all weights in lower case. Not always, but sometimes! 
# This is ambigous (cHB vs. cHb!!), so we can't go by the weight.id for determining the sequence of weights
# Fortunately, WeightInfo knows about the sequence of EFT weights  
def interpret_weight(weight_id):
    str_s = weight_id.split('_')
    res={}
    for i in range(len(str_s)/2):
        res[str_s[2*i]] = float(str_s[2*i+1].replace('m','-').replace('p','.'))
    return res

weightInfo_data = list(weightInfo.data.iteritems())
weightInfo_data.sort( key = lambda w: w[1] )
basepoint_coordinates = map( lambda d: [d[v] for v in weightInfo.variables] , map( lambda w: interpret_weight(w[0]), weightInfo_data) )
lowercase_ids = map( lambda s:s.lower(), weightInfo.id )

# We do not use a reference point, so its coordinates will be zero.
ref_point_coordinates = [weightInfo.ref_point_coordinates[var] for var in weightInfo.variables]

# Translating the weights at the base points (obtained from madgraph) to polynomial coefficients involves solving a matrix equation which is done with 'HyperPoly'.
hyperPoly  = HyperPoly( weightInfo.order )
hyperPoly.initialize( basepoint_coordinates, ref_point_coordinates )

sm_weight  = weightInfo.get_weight_func(cQQ8=0, cQQ1=0, cQt1=0, ctt=0, ctHRe=0, ctHIm=0, from_list=True)
eft_weight = weightInfo.get_weight_func(cQQ8=0.5, cQQ1=0.5, cQt1=0.5, ctt=0.5, ctHRe=20, ctHIm=20, from_list=True)

plots = [ 
    {'sample': "TTTT_MS",      'weight':sm_weight, "color": ROOT.kBlack,       "name": "sim@SM to SM"},
    {'sample': "TTTT_MS",      'weight':eft_weight, "color": ROOT.kRed,        "name": "sim@SM to EFT"},
    {'sample': "TTTT_MS_EFT",  'weight':sm_weight, "color": ROOT.kBlue,        "name": "sim@EFT to SM"},
    {'sample': "TTTT_MS_EFT",  'weight':eft_weight, "color": ROOT.kGreen,      "name": "sim@EFT to EFT"},
]

variables = ["leading_top_pt", "subleading_top_pt", "mttbar"]

for plot in plots:
    plot["histos"] = {}

    h = ROOT.TH1F("leading_top_pt", "leading_top_pt", 20,0,1000)
    h.style      = styles.lineStyle( plot['color'], errors=True)
    h.legendText = plot["name"] 
    h.texX       = "leading p_{T}(top)"
    plot["histos"]["leading_top_pt"] = h 

    h = ROOT.TH1F("subleading_top_pt", "subleading_top_pt", 20,0,1000)
    h.style      = styles.lineStyle( plot['color'], errors=True)
    h.legendText = plot["name"] 
    h.texX       = "subleading p_{T}(top)"
    plot["histos"]["subleading_top_pt"] = h 

    h = ROOT.TH1F("mttbar", "mttbar", 20,0,2500)
    h.style      = styles.lineStyle( plot['color'], errors=True)
    h.legendText = plot["name"] 
    h.texX       = "M(t#bar{t})"
    plot["histos"]["mttbar"] = h 


# FWLite from CMSSW
TTTT_MS     = FWLiteSample.fromFiles("TTTT_MS",     [
    #"root://eos.grid.vbc.ac.at//eos/vbc/group/cms/robert.schoefbeck/tttt/simulation/TTTT_MS.root"
    "root://eos.grid.vbc.ac.at//eos/vbc/group/cms/robert.schoefbeck/tttt/GEN/TTTT_MS/TTTT_13TeV_madgraph_pythia8_Run2SIM_UL2018Gen_250112_200340/250112_200415/LHEGEN_1.root",
    "root://eos.grid.vbc.ac.at//eos/vbc/group/cms/robert.schoefbeck/tttt/GEN/TTTT_MS/TTTT_13TeV_madgraph_pythia8_Run2SIM_UL2018Gen_250112_200340/250112_200415/LHEGEN_2.root",
    "root://eos.grid.vbc.ac.at//eos/vbc/group/cms/robert.schoefbeck/tttt/GEN/TTTT_MS/TTTT_13TeV_madgraph_pythia8_Run2SIM_UL2018Gen_250112_200340/250112_200415/LHEGEN_3.root",
    #"root://eos.grid.vbc.ac.at//eos/vbc/group/cms/robert.schoefbeck/tttt/GEN/TTTT_MS/TTTT_13TeV_madgraph_pythia8_Run2SIM_UL2018Gen_250112_200340/250112_200415/LHEGEN_4.root",
    #"root://eos.grid.vbc.ac.at//eos/vbc/group/cms/robert.schoefbeck/tttt/GEN/TTTT_MS/TTTT_13TeV_madgraph_pythia8_Run2SIM_UL2018Gen_250112_200340/250112_200415/LHEGEN_5.root",
    #"root://eos.grid.vbc.ac.at//eos/vbc/group/cms/robert.schoefbeck/tttt/GEN/TTTT_MS/TTTT_13TeV_madgraph_pythia8_Run2SIM_UL2018Gen_250112_200340/250112_200415/LHEGEN_6.root",
    ]) 
#TTTT_MS_EFT = FWLiteSample.fromFiles("TTTT_MS_EFT", ["root://eos.grid.vbc.ac.at//eos/vbc/group/cms/robert.schoefbeck/tttt/simulation/TTTT_MS_EFT.root"]) 
TTTT_MS_EFT = FWLiteSample.fromFiles("TTTT_MS_EFT", [
 "root://eos.grid.vbc.ac.at//eos/vbc/group/cms/robert.schoefbeck/tttt/GEN/TTTT_MS_EFT/TTTT_EFT_13TeV_madgraph_pythia8_Run2SIM_UL2018Gen_250111_204137/250111_223450/LHEGEN_1.root",
# "root://eos.grid.vbc.ac.at//eos/vbc/group/cms/robert.schoefbeck/tttt/GEN/TTTT_MS_EFT/TTTT_EFT_13TeV_madgraph_pythia8_Run2SIM_UL2018Gen_250111_204137/250111_223450/LHEGEN_2.root",
# "root://eos.grid.vbc.ac.at//eos/vbc/group/cms/robert.schoefbeck/tttt/GEN/TTTT_MS_EFT/TTTT_EFT_13TeV_madgraph_pythia8_Run2SIM_UL2018Gen_250111_204137/250111_223450/LHEGEN_3.root",
# "root://eos.grid.vbc.ac.at//eos/vbc/group/cms/robert.schoefbeck/tttt/GEN/TTTT_MS_EFT/TTTT_EFT_13TeV_madgraph_pythia8_Run2SIM_UL2018Gen_250111_204137/250111_223450/LHEGEN_4.root",
# "root://eos.grid.vbc.ac.at//eos/vbc/group/cms/robert.schoefbeck/tttt/GEN/TTTT_MS_EFT/TTTT_EFT_13TeV_madgraph_pythia8_Run2SIM_UL2018Gen_250111_204137/250111_223450/LHEGEN_5.root",
# "root://eos.grid.vbc.ac.at//eos/vbc/group/cms/robert.schoefbeck/tttt/GEN/TTTT_MS_EFT/TTTT_EFT_13TeV_madgraph_pythia8_Run2SIM_UL2018Gen_250111_204137/250111_223450/LHEGEN_6.root",
    ]) 

products = {
    'gp':      {'type':'vector<reco::GenParticle>', 'label':("genParticles")},
    'jets':    {'type':'vector<reco::GenJet>',  'label':("ak4GenJets")},
    'lhe':     {'type':'LHEEventProduct', 'label':("externalLHEProducer")},
    }

r_TTTT_MS = TTTT_MS.fwliteReader( products = products )
r_TTTT_MS.start()

r_TTTT_MS_EFT = TTTT_MS_EFT.fwliteReader( products = products )
r_TTTT_MS_EFT.start()

maxEvents = -1

for reader in [ r_TTTT_MS, r_TTTT_MS_EFT]:
    i_event = 0
    print( "Reading sample %s"%reader.sample.name )

    first = True
    while reader.run():
        i_event += 1

        if i_event%1000==0: print("At %i"%i_event)
        gp = reader.event.gp
        genSearch = GenSearch(gp)

        lhe_weights = reader.products['lhe'].weights()

        base_weights      = []
        for weight in lhe_weights:
            # Store nominal weight (First position!) 
            if weight.id in ['rwgt_1','dummy']: rw_nominal = weight.wgt

            # Some weight.id are lowercase; we decide to keep the weight based on the string but we don't use the string to decide which it is
            if not weight.id.lower() in lowercase_ids: continue
            base_weights.append( weight.wgt )

        # Now we obtain the coefficients. Store this vector of length weightInfo.nid in the flat ntuple.
        coeffs = hyperPoly.get_parametrization( base_weights )

        #assert False, ""

        #if first:
        #    for plot in plots:
        #        if not plot["sample"]==reader.sample.name: continue
        #        # construct mapping:
        #        plot['weight_index'] = None
        #        for i_w, w in enumerate(lhe_weights):
        #            if w.id.lower()==plot['weight'].lower():
        #                plot['weight_index'] = i_w
        #                break
        #        if plot['weight_index'] is None:
        #            raise RuntimeError("Weight %s not found in sample %s"%( plot['weight'], plot['sample']) )
        #    first = False

        tops = filter( lambda p: abs(p.pdgId())==6 and genSearch.isLast(p), gp )


        sample_scale = len(reader.sample.files)
        for plot in plots:
            weight_val = plot["weight"](coeffs)

            if not plot["sample"]==reader.sample.name: continue
            plot["histos"]["leading_top_pt"].Fill( tops[0].pt(),                weight_val/sample_scale )
            plot["histos"]["subleading_top_pt"].Fill( tops[1].pt(),             weight_val/sample_scale )
            plot["histos"]["mttbar"].Fill( (tops[0].p4()+tops[1].p4()).mass(),  weight_val/sample_scale )

        if maxEvents>0 and i_event>=maxEvents: break

for var in variables:
    plotting.draw( 
            Plot.fromHisto(name = var, histos = [[plot["histos"][var]] for plot in plots], texX = plots[0]["histos"][var].texX , texY = "arbitrary" ),  
            plot_directory = os.path.join( plot_directory, 'eft_MS_EFT'),
            yRange = 'auto',
            legend = "auto",
            ratio  = None, logY = False, logX = False 
        )

Analysis.Tools.syncer.sync()

