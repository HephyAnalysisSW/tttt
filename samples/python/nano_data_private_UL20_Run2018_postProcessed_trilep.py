import copy, os, sys
from RootTools.core.Sample import Sample
import ROOT

# Logging
import logging
logger = logging.getLogger(__name__)

try:
    directory_ = sys.modules['__main__'].directory_
except:
    import tttt.samples.config as config
    directory_ = config.location_data_UL2018_trilep

logger.info("Loading data samples from directory %s", directory_)

def getSample(pd, runName, lumi):
    runs = ["Run2018A","Run2018B","Run2018C","Run2018D"]
    dirlist = [directory_+"/"+pd+"_"+run for run in runs]
    sample      = Sample.fromDirectory(name=(pd + '_' + runName), treeName="Events", texName=(pd + ' (' + runName + ')'), directory=dirlist)
    sample.lumi = lumi
    return sample

allSamples = []

EGamma_Run2018                   = getSample('EGamma',           'Run2018',        ((59.97)*1000))
DoubleMuon_Run2018               = getSample('DoubleMuon',       'Run2018',        ((59.97)*1000))
MuonEG_Run2018                   = getSample('MuonEG',           'Run2018',        ((59.97)*1000))
SingleMuon_Run2018               = getSample('SingleMuon',       'Run2018',        ((59.97)*1000))
allSamples += [MuonEG_Run2018, EGamma_Run2018, DoubleMuon_Run2018, SingleMuon_Run2018]

Run2018 = Sample.combine("Run2018", [MuonEG_Run2018, EGamma_Run2018, DoubleMuon_Run2018, SingleMuon_Run2018], texName = "Run2018")
Run2018.lumi = config.lumi_era["Run2018"]
allSamples.append( Run2018 )

for s in allSamples:
  s.color   = ROOT.kBlack
  s.isData  = True
