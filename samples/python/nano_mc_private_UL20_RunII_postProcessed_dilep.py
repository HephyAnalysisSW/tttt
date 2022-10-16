from RootTools.core.standard import *

import tttt.samples.nano_mc_private_UL20_Summer16preVFP_postProcessed_dilep as Summer16preVFP
import tttt.samples.nano_mc_private_UL20_Summer16_postProcessed_dilep as Summer16
import tttt.samples.nano_mc_private_UL20_Fall17_postProcessed_dilep as Fall17
import tttt.samples.nano_mc_private_UL20_Autumn18_postProcessed_dilep as Autumn18

#DYJetsToLL  = Sample.combine( "DYJetsToLL", [Summer16.DYJetsToLL, Fall17.DYJetsToLL, Autumn18.DYJetsToLL])
TTLep       = Sample.combine( "TTLep", [Summer16preVFP.TTLep, Summer16.TTLep, Fall17.TTLep, Autumn18.TTLep])
#TTTT        = Sample.combine( "TTTT", [Summer16preVFP.TTTT, Summer16.TTTT, Fall17.TTTT, Autumn18.TTTT])
