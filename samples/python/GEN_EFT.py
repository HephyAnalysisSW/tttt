''' GEN samples for TMB'''

# standard imports
import os

# RootTools
from RootTools.core.standard import *

# TMB
from tttt.Tools.user import cache_dir, gridpack_directory 

# sqlite3 sample cache file
dbFile = os.path.join( cache_dir, 'sample_cache', 'GEN_EFT.db')
overwrite = False

# Logging
if __name__ == "__main__":
    import TMB.Tools.logger as logger
    logger = logger.get_logger('DEBUG')
    import RootTools.core.logger as logger_rt
    logger_rt = logger_rt.get_logger('DEBUG')

# for debug
test = FWLiteSample.fromDirectory( "test", ["/groups/hephy/cms/robert.schoefbeck/TMB/nlo_for_debug/"] )
test.xsec         = 1 
test.reweight_pkl = "/eos/vbc/group/cms/robert.schoefbeck/gridpacks/VH_nlo/WH_LeptonicW_NLO/WH_LeptonicW_NLO_reweight_card.pkl" 
test.nEvents      = 50000 

## TTbb_MS_EFT
#TTbb_MS = FWLiteSample.fromDAS("TTbb_MS", "/TTbb_MS_EFT/lwild-TTbb_MS_EFT-c9278d5dad30c5b88f7ba5ad37f5f2d0/USER", "phys03", dbFile = dbFile, overwrite=overwrite, skipCheck=True)
#TTbb_MS.xsec     = 5.253e-01
#TTbb_MS.nEvents  = 9940000
#TTbb_MS.reweight_pkl = "/eos/vbc/group/cms/robert.schoefbeck/gridpacks/4top/TTbb_MS_reweight_card.pkl"
#
## TTTT_MS_EFTdecay
#TTTT_MS = FWLiteSample.fromDAS("TTTT_MS", "/TTTT_MS_EFTdecay/lwild-TTTT_MS_EFTdecay-c9278d5dad30c5b88f7ba5ad37f5f2d0/USER", "phys03", dbFile = dbFile, overwrite=overwrite, skipCheck=True)
#TTTT_MS.xsec     = 6.232e-03
#TTTT_MS.nEvents  = 9860000
#TTTT_MS.reweight_pkl = "/eos/vbc/group/cms/robert.schoefbeck/gridpacks/4top/TTTT_MS_reweight_card.pkl"
#
##TT ttbar powheg 2l MINIAODSIM
#TT_2L   = FWLiteSample.fromDAS("TT_2L", "/TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8/RunIISummer20UL18MiniAODv2-106X_upgrade2018_realistic_v16_L1v1-v1/MINIAODSIM", dbFile = dbFile, overwrite=overwrite, skipCheck=True)
#TT_2L.xsec     = 831.762*((3*0.108)**2)
#TT_2L.nEvents  = 146058000

#EFT TTbb test sample
TTbb_MS = FWLiteSample.fromDirectory( "GEN_LO_0j_102X", ["/eos/vbc/group/cms/robert.schoefbeck/tttt/GEN/TTbb_MS/"] )
TTbb_MS.xsec = 1
TTbb_MS.reweight_pkl = "/eos/vbc/group/cms/robert.schoefbeck/gridpacks/4top/TTbb_MS_reweight_card.pkl"
TTbb_MS.nEvents = 1000 

TTbbRef = FWLiteSample.fromDirectory( "GEN_LO_0j_102X", ["/eos/vbc/group/cms/robert.schoefbeck/tttt/GEN/TTbbRef/"] )
TTbbRef.xsec = 1
TTbbRef.reweight_pkl = "/eos/vbc/group/cms/robert.schoefbeck/gridpacks/4top/TTbbRef_reweight_card.pkl"
TTbbRef.nEvents = 10000

TTbbRefHelIgn = FWLiteSample.fromDirectory( "GEN_LO_0j_102X", ["/eos/vbc/group/cms/robert.schoefbeck/tttt/GEN/TTbbRefHelIgn/"] )
TTbbRefHelIgn.xsec = 1
TTbbRefHelIgn.reweight_pkl = "/eos/vbc/group/cms/robert.schoefbeck/gridpacks/4top/TTbbRefHelIgn_reweight_card.pkl"
TTbbRefHelIgn.nEvents = 10000 

TTbbRefNoDec = FWLiteSample.fromDirectory( "GEN_LO_0j_102X", ["/eos/vbc/group/cms/robert.schoefbeck/tttt/GEN/TTbbRefNoDec/"] )
TTbbRefNoDec.xsec = 1
TTbbRefNoDec.reweight_pkl = "/eos/vbc/group/cms/robert.schoefbeck/gridpacks/4top/TTbbRefNoDec_reweight_card.pkl"
TTbbRefNoDec.nEvents = 10000

TTbbRefNoDecHelIgn = FWLiteSample.fromDirectory( "GEN_LO_0j_102X", ["/eos/vbc/group/cms/robert.schoefbeck/tttt/GEN/TTbbRefNoDecHelIgn/"] )
TTbbRefNoDecHelIgn.xsec = 1
TTbbRefNoDecHelIgn.reweight_pkl = "/eos/vbc/group/cms/robert.schoefbeck/gridpacks/4top/TTbbRefNoDecHelIgn_reweight_card.pkl"
TTbbRefNoDecHelIgn.nEvents = 10000

TTbbRef3NoDecHelIgn = FWLiteSample.fromDirectory( "GEN_LO_0j_102X", ["/eos/vbc/group/cms/robert.schoefbeck/tttt/GEN/TTbbRef3NoDecHelIgn/"] )
TTbbRef3NoDecHelIgn.xsec = 1
TTbbRef3NoDecHelIgn.reweight_pkl = "/eos/vbc/group/cms/robert.schoefbeck/gridpacks/4top/TTbbRef3NoDecHelIgn_reweight_card.pkl"
TTbbRef3NoDecHelIgn.nEvents = 10000

TTbbRef5 = FWLiteSample.fromDirectory( "GEN_LO_0j_102X", ["/eos/vbc/group/cms/robert.schoefbeck/tttt/GEN/TTbbRef5/"] )
TTbbRef5.xsec = 1
TTbbRef5.reweight_pkl = "/eos/vbc/group/cms/robert.schoefbeck/gridpacks/4top/TTbbRef5_reweight_card.pkl"
TTbbRef5.nEvents = 10000


