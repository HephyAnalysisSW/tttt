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

