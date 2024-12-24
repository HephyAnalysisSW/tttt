import ROOT
from RootTools.core.standard import *
from Analysis.Tools.GenSearch import GenSearch
import Analysis.Tools.syncer
import os
from tttt.Tools.user                     import plot_directory


# FWLite from CMSSW
tttt_ND_SM_noDec        = FWLiteSample.fromFiles("tttt_ND_SM_noDec",      ["root://eos.grid.vbc.ac.at//eos/vbc/group/cms/robert.schoefbeck/tttt/simulation/tttt_ND_SM_noDec.root"]) 
tttt_ND_noDec           = FWLiteSample.fromFiles("tttt_ND_noDec",         ["root://eos.grid.vbc.ac.at//eos/vbc/group/cms/robert.schoefbeck/tttt/simulation/tttt_ND_noDec.root"]) 
tttt_ND_cQQ1_1p_noDec   = FWLiteSample.fromFiles("tttt_ND_cQQ1_1p_noDec", ["root://eos.grid.vbc.ac.at//eos/vbc/group/cms/robert.schoefbeck/tttt/simulation/tttt_ND_cQQ1_1p_noDec.root"]) 

products = {
    'gp':      {'type':'vector<reco::GenParticle>', 'label':("genParticles")},
    'jets':    {'type':'vector<reco::GenJet>',  'label':("ak4GenJets")},
    'lhe':     {'type':'LHEEventProduct', 'label':("externalLHEProducer")},
    }

r_tttt_ND_SM_noDec = tttt_ND_SM_noDec.fwliteReader( products = products )
r_tttt_ND_SM_noDec.start()

tttt_ND_noDec = tttt_ND_noDec.fwliteReader( products = products )
tttt_ND_noDec.start()

r_tttt_ND_cQQ1_1p_noDec = tttt_ND_cQQ1_1p_noDec.fwliteReader( products = products )
r_tttt_ND_cQQ1_1p_noDec.start()

sm_weight        = 'cQQ8_0p_cQQ1_0p_cQt1_0p_ctt_0p_cQt8_0p_ctHRe_0p_ctHIm_0p'
cQQ1_1p_weight   = 'cQQ8_0p_cQQ1_1p_cQt1_0p_ctt_0p_cQt8_0p_ctHRe_0p_ctHIm_0p'

plots = [ 
    {'sample': "tttt_ND_SM_noDec",      'weight':sm_weight, "color": ROOT.kBlack,       "name": "sim@SM to SM"},
    {'sample': "tttt_ND_SM_noDec",      'weight':cQQ1_1p_weight, "color": ROOT.kRed,    "name": "sim@SM to cQQ1=1"},
    {'sample': "tttt_ND_noDec",         'weight':sm_weight, "color": ROOT.kOrange,      "name": "sim@Ref to SM"},
    {'sample': "tttt_ND_noDec",         'weight':cQQ1_1p_weight, "color": ROOT.kMagenta,"name": "sim@Ref to cQQ1=1"},
    {'sample': "tttt_ND_cQQ1_1p_noDec", 'weight':sm_weight, "color": ROOT.kBlue,        "name": "sim@cQQ1=1 to SM"},
    {'sample': "tttt_ND_cQQ1_1p_noDec", 'weight':cQQ1_1p_weight, "color": ROOT.kGreen,  "name": "sim@cQQ1=1 to cQQ1=1"},
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

maxEvents = -1

for reader in [ r_tttt_ND_SM_noDec, r_tttt_ND_cQQ1_1p_noDec, tttt_ND_noDec]:
    i_event = 0
    print( "Reading sample %s"%reader.sample.name )

    first = True
    while reader.run():
        i_event += 1

        if i_event%1000==0: print("At %i"%i_event)
        gp = reader.event.gp
        genSearch = GenSearch(gp)

        lhe_weights = reader.products['lhe'].weights()

        if first:
            for plot in plots:
                if not plot["sample"]==reader.sample.name: continue
                # construct mapping:
                plot['weight_index'] = None
                for i_w, w in enumerate(lhe_weights):
                    if w.id==plot['weight']:
                        plot['weight_index'] = i_w
                        break
                if plot['weight_index'] is None:
                    raise RuntimeError("Weight %s not found in sample %s"%( plot['weight'], plot['sample']) )
            first = False

        tops = filter( lambda p: abs(p.pdgId())==6 and genSearch.isLast(p), gp )

        for plot in plots:
            if not plot["sample"]==reader.sample.name: continue
            plot["histos"]["leading_top_pt"].Fill( tops[0].pt(), lhe_weights[plot["weight_index"]].wgt )
            plot["histos"]["subleading_top_pt"].Fill( tops[1].pt(), lhe_weights[plot["weight_index"]].wgt )
            plot["histos"]["mttbar"].Fill( (tops[0].p4()+tops[1].p4()).mass(), lhe_weights[plot["weight_index"]].wgt )

        if maxEvents>0 and i_event>=maxEvents: break

for var in variables:
    plotting.draw( 
            Plot.fromHisto(name = var, histos = [[plot["histos"][var]] for plot in plots], texX = plots[0]["histos"][var].texX , texY = "arbitrary" ),  
            plot_directory = os.path.join( plot_directory, 'eft'),
            yRange = 'auto',
            legend = "auto",
            ratio  = None, logY = False, logX = False 
        )

Analysis.Tools.syncer.sync()

#(0, 'dummy', 3.14836e-07)
#(1, 'cQQ8_0p_cQQ1_0p_cQt1_0p_ctt_0p_cQt8_0p_ctHRe_0p_ctHIm_0p', 3.14836e-07)
#(2, 'cQQ8_1p_cQQ1_0p_cQt1_0p_ctt_0p_cQt8_0p_ctHRe_0p_ctHIm_0p', 3.1482765e-07)
#(3, 'cQQ8_0p_cQQ1_1p_cQt1_0p_ctt_0p_cQt8_0p_ctHRe_0p_ctHIm_0p', 3.1488778e-07)
#(4, 'cQQ8_0p_cQQ1_0p_cQt1_1p_ctt_0p_cQt8_0p_ctHRe_0p_ctHIm_0p', 3.2807471e-07)
#(5, 'cQQ8_0p_cQQ1_0p_cQt1_0p_ctt_1p_cQt8_0p_ctHRe_0p_ctHIm_0p', 3.1740239e-07)
#(6, 'cQQ8_0p_cQQ1_0p_cQt1_0p_ctt_0p_cQt8_1p_ctHRe_0p_ctHIm_0p', 3.2625332e-07)
#(7, 'cQQ8_0p_cQQ1_0p_cQt1_0p_ctt_0p_cQt8_0p_ctHRe_1p_ctHIm_0p', 3.1094497e-07)
#(8, 'cQQ8_0p_cQQ1_0p_cQt1_0p_ctt_0p_cQt8_0p_ctHRe_0p_ctHIm_1p', 3.1305507e-07)
#(9, 'cQQ8_2p_cQQ1_0p_cQt1_0p_ctt_0p_cQt8_0p_ctHRe_0p_ctHIm_0p', 3.1484491e-07)
#(10, 'cQQ8_1p_cQQ1_1p_cQt1_0p_ctt_0p_cQt8_0p_ctHRe_0p_ctHIm_0p', 3.1495625e-07)
#(11, 'cQQ8_1p_cQQ1_0p_cQt1_1p_ctt_0p_cQt8_0p_ctHRe_0p_ctHIm_0p', 3.2806093e-07)
#(12, 'cQQ8_1p_cQQ1_0p_cQt1_0p_ctt_1p_cQt8_0p_ctHRe_0p_ctHIm_0p', 3.170678e-07)
#(13, 'cQQ8_1p_cQQ1_0p_cQt1_0p_ctt_0p_cQt8_1p_ctHRe_0p_ctHIm_0p', 3.262387e-07)
#(14, 'cQQ8_1p_cQQ1_0p_cQt1_0p_ctt_0p_cQt8_0p_ctHRe_1p_ctHIm_0p', 3.1094606e-07)
#(15, 'cQQ8_1p_cQQ1_0p_cQt1_0p_ctt_0p_cQt8_0p_ctHRe_0p_ctHIm_1p', 3.1304733e-07)
#(16, 'cQQ8_0p_cQQ1_2p_cQt1_0p_ctt_0p_cQt8_0p_ctHRe_0p_ctHIm_0p', 3.1517002e-07)
#(17, 'cQQ8_0p_cQQ1_1p_cQt1_1p_ctt_0p_cQt8_0p_ctHRe_0p_ctHIm_0p', 3.2811019e-07)
#(18, 'cQQ8_0p_cQQ1_1p_cQt1_0p_ctt_1p_cQt8_0p_ctHRe_0p_ctHIm_0p', 3.1647545e-07)
#(19, 'cQQ8_0p_cQQ1_1p_cQt1_0p_ctt_0p_cQt8_1p_ctHRe_0p_ctHIm_0p', 3.2628628e-07)
#(20, 'cQQ8_0p_cQQ1_1p_cQt1_0p_ctt_0p_cQt8_0p_ctHRe_1p_ctHIm_0p', 3.1102505e-07)
#(21, 'cQQ8_0p_cQQ1_1p_cQt1_0p_ctt_0p_cQt8_0p_ctHRe_0p_ctHIm_1p', 3.1310868e-07)
#(22, 'cQQ8_0p_cQQ1_0p_cQt1_2p_ctt_0p_cQt8_0p_ctHRe_0p_ctHIm_0p', 3.4416399e-07)
#(23, 'cQQ8_0p_cQQ1_0p_cQt1_1p_ctt_1p_cQt8_0p_ctHRe_0p_ctHIm_0p', 3.3061503e-07)
#(24, 'cQQ8_0p_cQQ1_0p_cQt1_1p_ctt_0p_cQt8_1p_ctHRe_0p_ctHIm_0p', 3.4023867e-07)
#(25, 'cQQ8_0p_cQQ1_0p_cQt1_1p_ctt_0p_cQt8_0p_ctHRe_1p_ctHIm_0p', 3.2382777e-07)
#(26, 'cQQ8_0p_cQQ1_0p_cQt1_1p_ctt_0p_cQt8_0p_ctHRe_0p_ctHIm_1p', 3.2628581e-07)
#(27, 'cQQ8_0p_cQQ1_0p_cQt1_0p_ctt_2p_cQt8_0p_ctHRe_0p_ctHIm_0p', 3.2413539e-07)
#(28, 'cQQ8_0p_cQQ1_0p_cQt1_0p_ctt_1p_cQt8_1p_ctHRe_0p_ctHIm_0p', 3.2886026e-07)
#(29, 'cQQ8_0p_cQQ1_0p_cQt1_0p_ctt_1p_cQt8_0p_ctHRe_1p_ctHIm_0p', 3.1340731e-07)
#(30, 'cQQ8_0p_cQQ1_0p_cQt1_0p_ctt_1p_cQt8_0p_ctHRe_0p_ctHIm_1p', 3.156019e-07)
#(31, 'cQQ8_0p_cQQ1_0p_cQt1_0p_ctt_0p_cQt8_2p_ctHRe_0p_ctHIm_0p', 3.3842958e-07)
#(32, 'cQQ8_0p_cQQ1_0p_cQt1_0p_ctt_0p_cQt8_1p_ctHRe_1p_ctHIm_0p', 3.2210891e-07)
#(33, 'cQQ8_0p_cQQ1_0p_cQt1_0p_ctt_0p_cQt8_1p_ctHRe_0p_ctHIm_1p', 3.2447484e-07)
#(34, 'cQQ8_0p_cQQ1_0p_cQt1_0p_ctt_0p_cQt8_0p_ctHRe_2p_ctHIm_0p', 3.0714665e-07)
#(35, 'cQQ8_0p_cQQ1_0p_cQt1_0p_ctt_0p_cQt8_0p_ctHRe_1p_ctHIm_1p', 3.0916304e-07)
#(36, 'cQQ8_0p_cQQ1_0p_cQt1_0p_ctt_0p_cQt8_0p_ctHRe_0p_ctHIm_2p', 3.1132791e-07)
