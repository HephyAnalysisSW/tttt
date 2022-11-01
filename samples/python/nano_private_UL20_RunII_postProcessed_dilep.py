from RootTools.core.standard import *

from tttt.samples.nano_data_private_UL20_Run2016_postProcessed_dilep import Run2016
from tttt.samples.nano_data_private_UL20_Run2016_preVFP_postProcessed_dilep import Run2016_preVFP
from tttt.samples.nano_data_private_UL20_Run2017_postProcessed_dilep import Run2017
from tttt.samples.nano_data_private_UL20_Run2018_postProcessed_dilep import Run2018

RunII      = Sample.combine( "RunII", [Run2016, Run2016_preVFP, Run2017, Run2018] ) 
RunII.lumi = Run2016.lumi + Run2016_preVFP.lumi + Run2017.lumi + Run2018.lumi

lumi_era  = {'Run2016':Run2016.lumi, 'Run2016_preVFP':Run2016_preVFP.lumi, 'Run2017':Run2017.lumi, 'Run2018':Run2018.lumi}

import tttt.samples.nano_mc_private_UL20_Summer16_preVFP_postProcessed_dilep as Summer16_preVFP
import tttt.samples.nano_mc_private_UL20_Summer16_postProcessed_dilep as Summer16
import tttt.samples.nano_mc_private_UL20_Fall17_postProcessed_dilep as Fall17
import tttt.samples.nano_mc_private_UL20_Autumn18_postProcessed_dilep as Autumn18

TTLep       = Sample.combine( "TTLep", [Summer16_preVFP.TTLep, Summer16.TTLep, Fall17.TTLep, Autumn18.TTLep])
TTTT        = Sample.combine( "TTTT",  [Summer16_preVFP.TTTT, Summer16.TTTT, Fall17.TTTT, Autumn18.TTTT])
TTW         = Sample.combine( "TTW",   [Summer16_preVFP.TTW, Summer16.TTW, Fall17.TTW, Autumn18.TTW])
TTZ         = Sample.combine( "TTZ",   [Summer16_preVFP.TTZ, Summer16.TTZ, Fall17.TTZ, Autumn18.TTZ])
TTH         = Sample.combine( "TTH",   [Summer16_preVFP.TTH, Summer16.TTH, Fall17.TTH, Autumn18.TTH])
