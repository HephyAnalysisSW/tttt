import logging
logger = logging.getLogger(__name__)

class triggerSelector:
    # ttH multilepton AN Run II
    # http://cms.cern.ch/iCMS/jsp/openfile.jsp?tp=draft&files=AN2019_111_v6.pdf

    @staticmethod
    def getTriggerList( sample ):
        return [t.GetName() for t in sample.chain.GetListOfBranches() if t.GetName().startswith("HLT_")]

    def __init__(self, year, isTrilep = True):
        self.isTrilep = isTrilep

        if year == 2016:

            #PURE MULTILEPTON CHANNELS:
            #Muons
            self.mmm    =    ["HLT_TripleMu_12_10_5"]
            #This is kept for counting purposes, check if correct

            self.mm     =    ["HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL",       #data runs B-G & MC
                            "HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL",       #data runs B-G & MC
                            "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ",      #data only run H
                            "HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ",    #data only run H
                            "HLT_IsoMu24",                             #data & MC
                            "HLT_IsoTkMu24"                             #data & MC
                            ]#Done

            #Electrons
            self.eee    =    ["HLT_Ele16_Ele12_Ele8_CaloIdL_TrackIdL"]
            #This is kept for counting purposes, check if correct

            self.ee     =   ["HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ",       #data & MC
                            "HLT_DoubleEle33_CaloIdL_MW",                       #data & MC
                            "HLT_DoubleEle33_CaloIdL_GsfTrkIdVL",               #data & MC
                            "HLT_Ele27_WPTight_Gsf"                             #data & MC
                            ]#Done

            #MIXED MULTILEPTON CHANNELS:
            self.em     =   ["HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL",      #data runs B-G & MC
                            "HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL",      #data runs B-G & MC
                            "HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ",    #data only run H
                            "HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ",   #data only run H
                            "HLT_Ele27_WPTight_Gsf",                                #data & MC
                            #"HLT_IsoMu24",                                          #data & MC
                            "HLT_IsoTkMu24"                                         #data & MC
                            ]#Done

            self.emm    =   ["HLT_DiMu9_Ele9_CaloIdL_TrackIdL"]
            self.eem    =   ["HLT_Mu8_DiEle12_CaloIdL_TrackIdL"]
            #Note -> "eem" & "emm" inherited from the trilep selection, chech if correct
            #This is kept for counting purposes, check if correct

            #SINGLE LEPTON CHANNELS:
            #These are standard triggers for single lepton selection in ttbar
            #Might want to go lower in lepton pT
            #Check http://cms.cern.ch/iCMS/jsp/openfile.jsp?tp=draft&files=AN2020_020_v13.pdf
            self.e    = ["HLT_Ele27_WPTight_Gsf"]
            self.m     = ["HLT_IsoMu24"]

        elif year == 2017:

            #PURE MULTILEPTON CHANNELS:
            #Muons
            self.mmm    =   ["HLT_TripleMu_10_5_5_DZ","HLT_TripleMu_12_10_5"]
            #This is kept for counting purposes, check if correct

            self.mm     =   ["HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ",                 #data runs B-G & MC
                            "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8",            #data runs C-F & MC
                            "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8",          #data runs C-F & MC
                            "HLT_IsoMu27"                                           #data & MC
                            ]#Done
            #Electrons
            self.eee    =   ["HLT_Ele16_Ele12_Ele8_CaloIdL_TrackIdL"]
            #This is kept for counting purposes, check if correct

            self.ee     =   ["HLT_Ele23_Ele12_caloIdL_TrackIdL_IsoVL",              #data & MC
                            "HLT_DoubleEle33_CaloIdL_MW",                           #data & MC
                            "HLT_Ele35_WPTight_Gsf"                                 #data & MC
                            ]#Done

            #MIXED MULTILEPTON CHANNELS:
            self.em     =   ["HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ",    #data & MC
                            "HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL",      #data & MC
                            "HLT_Ele35_WPTight_Gsf",                                #data & MC
                            "HLT_IsoMu27"
                            ]#Done

            self.eem    = ["HLT_Mu8_DiEle12_CaloIdL_TrackIdL", "HLT_Mu8_DiEle12_CaloIdL_TrackIdL_DZ"]
            self.emm    = ["HLT_DiMu9_Ele9_CaloIdL_TrackIdL", "HLT_DiMu9_Ele9_CaloIdL_TrackIdL_DZ"]
            #Note -> "eem" & "emm" inherited from the trilep selection, chech if correct
            #This is kept for counting purposes, check if correct

            #SINGLE LEPTON CHANNELS:
            #These are standard triggers for single lepton selection in ttbar
            #Might want to go lower in lepton pT
            #Check http://cms.cern.ch/iCMS/jsp/openfile.jsp?tp=draft&files=AN2020_020_v13.pdf
            self.e    = ["HLT_Ele27_WPTight_Gsf"]
            self.m     = ["HLT_IsoMu27"]


        elif year == 2018:


            #PURE MULTILEPTON CHANNELS:
            #Muons
            self.mmm    =   ["HLT_TripleMu_12_10_5"]
            #This is kept for counting purposes, check if correct

            self.mm     =   ["HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8",        #data & MC
                            "HLT_IsoMu24"                                           #data & MC
                            ]#Done
            #Electrons
            self.eee    =   ["HLT_Ele16_Ele12_Ele8_CaloIdL_TrackIdL"]
            #This is kept for counting purposes, check if correct

            self.ee     =   [ "HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL",             #data & MC
                            "HLT_DoubleEle25_CaloIdL_MW",                           #data & MC
                            "HLT_Ele32_WPTight_Gsf"                                 #data & MC
                            ]#Done

            #MIXED MULTILEPTON CHANNELS:
            self.em     =   ["HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ",   #data & MC
                            "HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL",      #data & MC
                            "HLT_IsoMu24",                                          #data & MC
                            "HLT_Ele32_WPTight_Gsf"                                 #data & MC
                            ]#Done

            self.eem    = [ "HLT_Mu8_DiEle12_CaloIdL_TrackIdL"] # HLT_Mu8_DiEle12_CaloIdL_TrackIdL_DZ
            self.emm    = [ "HLT_DiMu9_Ele9_CaloIdL_TrackIdL_DZ" ] # HLT_DiMu9_Ele9_CaloIdL_TrackId
            #Note -> "eem" & "emm" inherited from the trilep selection, chech if correct
            #This is kept for counting purposes, check if correct

            #SINGLE LEPTON CHANNELS:
            #These are standard triggers for single lepton selection in ttbar
            #Might want to go lower in lepton pT
            #Check http://cms.cern.ch/iCMS/jsp/openfile.jsp?tp=draft&files=AN2020_020_v13.pdf
            self.m      = ["HLT_IsoMu24"]
            self.e      = ["HLT_Ele32_WPTight_Gsf"] # higher threshold not needed of Ele32 was unprescaled in 17+18

        else:
            raise NotImplementedError("Trigger selection %r not implemented"%year)

        #Define arbitrary hierarchy
        if year == 2016 or year == 2017:
            self.PDHierarchy = [ "DoubleMuon", "DoubleEG", "MuonEG", "SingleMuon", "SingleElectron" ]
        else:
            # DoubleEG and SingleElectron PDs are merged into EGamma. No change necessary for MC
            self.PDHierarchy = [ "DoubleMuon", "EGamma", "MuonEG", "SingleMuon" ]

    def __getVeto(self, cutString):
        return "!%s"%cutString

    def getSelection(self, PD, triggerList = None):

        # reduce the set of triggers in case
        for lst in [ "mm", "m", "ee", "e", "em"] if not self.isTrilep else ["mmm", "mm", "m", "eee", "ee", "e", "em", "eem", "emm" ]:
            print("Which list are you taking"+ str(lst))
            res = []
            for trig in getattr(self, lst):
                print("My list of triggers"+trig)
                if type(triggerList)==type([]) and not trig in triggerList:
                    logger.warning( "Removing trigger %s", trig )
                else:
                    res.append(trig)
            setattr( self, 'red_'+lst, res )

        # define which triggers should be used for which dataset
        self.DoubleMuon     = "(%s)"%"||".join(self.red_mm if not self.isTrilep else self.red_mmm + self.red_mm)
        self.DoubleEG       = "(%s)"%"||".join(self.red_ee if not self.isTrilep else self.red_eee + self.red_ee)
        self.MuonEG         = "(%s)"%"||".join(self.red_em if not self.isTrilep else self.red_em + self.red_eem + self.red_emm)
        self.SingleMuon     = "(%s)"%"||".join(self.red_m)
        self.SingleElectron = "(%s)"%"||".join(self.red_e)
        self.EGamma         = "(%s)"%"||".join(self.red_ee+self.red_e)

        found = False
        cutString = ""
        if PD == "MC":
            return "(%s)"%"||".join([self.DoubleMuon, self.DoubleEG, self.MuonEG, self.SingleMuon, self.SingleElectron])
        else:
            for x in reversed(self.PDHierarchy):
                if found:
                    cutString += "&&%s"%self.__getVeto(getattr(self,x))
                if x in PD:# == getattr(self, PD):
                    found = True
                    cutString = getattr(self, x)

            return "(%s)"%cutString
