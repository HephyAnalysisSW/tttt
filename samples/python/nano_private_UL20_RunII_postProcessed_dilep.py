from RootTools.core.standard import *

from tttt.samples.nano_data_private_UL20_Run2016_postProcessed_dilep import Run2016
from tttt.samples.nano_data_private_UL20_Run2016_preVFP_postProcessed_dilep import Run2016_preVFP
from tttt.samples.nano_data_private_UL20_Run2017_postProcessed_dilep import Run2017
from tttt.samples.nano_data_private_UL20_Run2018_postProcessed_dilep import Run2018

RunII      = Sample.combine( "RunII", [Run2016, Run2016_preVFP, Run2017, Run2018], texName = "Data (Run II)")
RunII.lumi = Run2016.lumi + Run2016_preVFP.lumi + Run2017.lumi + Run2018.lumi

lumi_era  = {'Run2016':Run2016.lumi, 'Run2016_preVFP':Run2016_preVFP.lumi, 'Run2017':Run2017.lumi, 'Run2018':Run2018.lumi}

import tttt.samples.nano_mc_private_UL20_Summer16_preVFP_postProcessed_dilep as Summer16_preVFP
import tttt.samples.nano_mc_private_UL20_Summer16_postProcessed_dilep as Summer16
import tttt.samples.nano_mc_private_UL20_Fall17_postProcessed_dilep as Fall17
import tttt.samples.nano_mc_private_UL20_Autumn18_postProcessed_dilep as Autumn18

TTLep       = Sample.combine( "TTLep", [Summer16_preVFP.TTLep, Summer16.TTLep, Fall17.TTLep, Autumn18.TTLep], texName = "t#bar{t}")
TTLepbb       = Sample.combine( "TTLepbb", [Summer16_preVFP.TTLepbb, Summer16.TTLepbb, Fall17.TTLepbb, Autumn18.TTLepbb], texName = "t#bar{t}")
TTbb        = Sample.combine( "TTbb", [Summer16_preVFP.TTbb, Summer16.TTbb, Fall17.TTbb, Autumn18.TTbb], texName = "t#bar{t}b#bar{b}")
ST          = Sample.combine( "ST",    [Summer16_preVFP.ST, Summer16.ST, Fall17.ST, Autumn18.ST],             texName = "t/tW")
ST_tch      = Sample.combine( "ST_tch",     [Summer16_preVFP.ST_tch, Summer16.ST_tch, Fall17.ST_tch, Autumn18.ST_tch],             texName = "t")
ST_twch     = Sample.combine( "ST_twch",    [Summer16_preVFP.ST_twch, Summer16.ST_twch, Fall17.ST_twch, Autumn18.ST_twch],             texName = "tW")
TTTT        = Sample.combine( "TTTT",  [Summer16_preVFP.TTTT, Summer16.TTTT, Fall17.TTTT, Autumn18.TTTT],     texName = "t#bar{t}t#bar{t}")
TTW         = Sample.combine( "TTW",   [Summer16_preVFP.TTW, Summer16.TTW, Fall17.TTW, Autumn18.TTW],         texName = "t#bar{t}W" )
TTZ         = Sample.combine( "TTZ",   [Summer16_preVFP.TTZ, Summer16.TTZ, Fall17.TTZ, Autumn18.TTZ],         texName = "t#bar{t}Z")
TTH         = Sample.combine( "TTH",   [Summer16_preVFP.TTH, Summer16.TTH, Fall17.TTH, Autumn18.TTH],         texName = "t#bar{t}H")
DY          = Sample.combine( "DY",    [Summer16_preVFP.DY, Summer16.DY, Fall17.DY, Autumn18.DY],             texName = "DY")
DiBoson     = Sample.combine( "DiBoson", [Summer16_preVFP.DiBoson, Summer16.DiBoson, Fall17.DiBoson, Autumn18.DiBoson], texName = "DiBoson")
