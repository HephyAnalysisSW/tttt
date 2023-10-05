import ROOT
import os

class isrJetCorrector:
    def __init__(self, era = None, MC = "HTbinned"):
        ''' apply constant SF to leading lepton, if SF is larger than uncertainty inflate uncertainty accordingly
        '''

        if not MC in ["HTbinned", "inclusive"]:
            raise RuntimeError("Don't know which DY MC you'll be using")
        if era is not None:
            raise NotImplementedError("We might have eras ... but not now.")

        # FIXME load histograms here
        self.r_4To5 = None
        self.r_6p   = None

    def getSF(self, nJetGood, isrJetPt):

        if nJetGood>=4 and nJetGood<=5:
            h = self.r_4To5 
        elif nJetGood>=6:
            h = self.r_6p 

        return h.GetBinContent(h.FindBin(isrJetPt))

