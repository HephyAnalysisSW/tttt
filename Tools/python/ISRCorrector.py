import ROOT
import os
from Analysis.Tools.helpers import getObjFromFile

import logging
logger = logging.getLogger(__name__)

directory = os.path.expandvars("$CMSSW_BASE/src/tttt/Tools/data/isrJetReweighting/")

f_4to5 = "trg-dilep-OS-minDLmass20-onZ1-lepVeto2-njet4to5-btag1to2-ht500_ISRJet_pt40.root"
f_6p   = "trg-dilep-OS-minDLmass20-onZ1-lepVeto2-njet6p-btag1to2-ht500_ISRJet_pt40.root"

class ISRCorrector:
    def __init__(self, era = None, MC = "HTbinned"):
        ''' apply constant SF to leading lepton, if SF is larger than uncertainty inflate uncertainty accordingly
        '''

        if not MC in ["HTbinned", "inclusive"]:
            raise RuntimeError("Don't know which DY MC you'll be using")
        if era is not None:
            raise NotImplementedError("We might have eras ... but not now.")

        # FIXME load histograms here

        self.h_reweight = {}
        self.stuff = []
        if MC == "HTbinned":
            for name, file in [ ( "4to5", f_4to5), ("6p", f_6p) ]:
                gDir = ROOT.gDirectory.GetName()
                f = ROOT.TFile(os.path.join(directory, file))
                assert not f.IsZombie()
                f.cd()
                c_ = f.Get(f.GetListOfKeys().At(0).GetName()) 
                canvas = c_.Clone()
                self.stuff.append( canvas ) 
                ROOT.gDirectory.cd('PyROOT:/')
                f.Close()
                DYMC = canvas.GetListOfPrimitives().At(0).GetListOfPrimitives().At(1) 
                bkgMC   = canvas.GetListOfPrimitives().At(0).GetListOfPrimitives().At(2) 
                data    = canvas.GetListOfPrimitives().At(0).GetListOfPrimitives().At(11)

                # subtract background from data and MC
                bkgMC.Scale(-1)
                DYMC.Add(bkgMC) #the histogram is the SUM of all MCs, so subtract N-1 terms 
                data.Add(bkgMC)
                DYMC.Scale(1./DYMC.Integral())
                data.Scale(1./data.Integral())

                self.h_reweight[name] = data 
                self.h_reweight[name].Divide(DYMC)

        self.max_isrJetPt = self.h_reweight['4to5'].GetXaxis().GetXmax()

    def getSF(self, nJetGood, isrJetPt):

        if isrJetPt<0: isrJetPt=0
        if isrJetPt>=self.max_isrJetPt: isrJetPt = self.max_isrJetPt-.1

        if nJetGood>=4 and nJetGood<=5:
            h = self.h_reweight["4to5"] 
        elif nJetGood>=6:
            h = self.h_reweight["6p"]
        else:
            logger.warning("No ISR jet correction for nJet",nJetGood)
            return 1 

        return h.GetBinContent(h.FindBin(isrJetPt))

if __name__=="__main__":
    corr = ISRJetCorrector()

    import tttt.Tools.user as user
    from RootTools.core.standard import *
    import Analysis.Tools.syncer 

    c1 = ROOT.TCanvas()
    corr.h_reweight["4to5"].legendText = "4to5"
    corr.h_reweight["6p"].legendText = "6p"
    corr.h_reweight["4to5"].style = styles.lineStyle(ROOT.kBlue)
    corr.h_reweight["6p"].style = styles.lineStyle(ROOT.kRed)
    plot = Plot.fromHisto( "isrJetReweight", [[corr.h_reweight["4to5"]], [corr.h_reweight["6p"]]], texX="ISR Jet pt 40", texY="reweight")
    plotting.draw(plot, plot_directory = os.path.join( user.plot_directory, "isrJetReweighting", ), copyIndexPHP=True, logY=False, yRange=(0,1.5))

#OBJ: TList  TList   Doubly linked list : 0
# TFrame  X1= 0.000000 Y1=-0.045757 X2=2000.000000 Y2=6.433272
# OBJ: TH1F  ISRJet_pt40_DY_282c7357_3cbe_4563_9470_968370c4ef6f ISRJet_pt40_DY : 1 at: 0x4e15320
# OBJ: TH1F  ISRJet_pt40_TTLep_other_a2027934_457f_45cd_a0e8_7637870c2405    ISRJet_pt40_TTLep_other : 1 at: 0x4e15a70
# OBJ: TH1F  ISRJet_pt40_DiBoson_61351db3_986e_4ca5_91fd_c5c3e76d8feb    ISRJet_pt40_DiBoson : 1 at: 0x4e19fa0
# OBJ: TH1F  ISRJet_pt40_TTZ_65677b82_e4d3_4f1c_a49f_5f3092886811    ISRJet_pt40_TTZ : 1 at: 0x4e1a770
# OBJ: TH1F  ISRJet_pt40_TTLep_cc_ab2f7a9e_7dab_4757_a9d2_63d1bc19063f   ISRJet_pt40_TTLep_cc : 1 at: 0x4e1eb70
# OBJ: TH1F  ISRJet_pt40_TTLep_bb_721be393_833a_4edc_acfd_09e406d0815b   ISRJet_pt40_TTLep_bb : 1 at: 0x4e61020
# OBJ: TH1F  ISRJet_pt40_ST_87d57eaa_cb50_4fef_9590_23cc88fd3f0c ISRJet_pt40_ST : 1 at: 0x4e617f0
# OBJ: TH1F  ISRJet_pt40_TTH_0a45ffa2_9654_47f0_9356_9971a2edbb1c    ISRJet_pt40_TTH : 1 at: 0x4e58100
# OBJ: TH1F  ISRJet_pt40_TTW_7d647785_2518_4db0_969e_dff96a0e8bd0    ISRJet_pt40_TTW : 1 at: 0x4e58830
# OBJ: TH1F  ISRJet_pt40_TTTT_c4c6f409_ba7e_45dd_adc0_71ec676e3573   ISRJet_pt40_TTTT : 1 at: 0x4e29fc0
# OBJ: TH1F  ISRJet_pt40_data_389748c1_7838_47f2_8525_e006a571187b   ISRJet_pt40_data : 1 at: 0x4e2a740
# OBJ: TH1F  ISRJet_pt40_DY_282c7357_3cbe_4563_9470_968370c4ef6f_copy    ISRJet_pt40_DY : 1 at: 0x4e16890
# OBJ: TLegend   TPave   X1= 74.999992 Y1=3.785926 X2=1874.999999 Y2=6.084937
# Text  X=0.150000 Y=0.950000 Text=CMS Simulation
# Text  X=0.450000 Y=0.950000 Text=L=137.5 fb{}^{-1} (13 TeV)
#
