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

## TTbb_MS_EFTdecay
#TTbb_MS = FWLiteSample.fromDAS("TTbb_MS", "/TTbb_MS_EFTdecay/lwild-TTbb_MS_EFTdecay-c9278d5dad30c5b88f7ba5ad37f5f2d0/USER", "phys03", dbFile = dbFile, overwrite=overwrite, skipCheck=True)
#TTbb_MS.xsec     = 4.728e+00
#TTbb_MS.nEvents  = 9960000
#TTbb_MS.reweight_pkl = "/eos/vbc/group/cms/robert.schoefbeck/gridpacks/4top/TTbb_MS_reweight_card.pkl"

# TTTT_MS_EFTdecay
TTTT_MS = FWLiteSample.fromDAS("TTTT_MS", "/TTTT_MS_EFTdecay/lwild-TTTT_MS_EFTdecay-c9278d5dad30c5b88f7ba5ad37f5f2d0/USER", "phys03", dbFile = dbFile, overwrite=overwrite, skipCheck=True)
TTTT_MS.xsec     = 6.232e-03
TTTT_MS.nEvents  = 9860000
TTTT_MS.reweight_pkl = "/eos/vbc/group/cms/robert.schoefbeck/gridpacks/4top/TTTT_MS_reweight_card.pkl"
