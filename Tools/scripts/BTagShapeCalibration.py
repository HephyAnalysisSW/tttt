import ROOT
from RootTools.core.standard import *
from tttt.Tools.cutInterpreter import cutInterpreter
import copy
from tttt.samples.color import color


# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--small',      action='store_true', help='Run only on a small subset of the data?')
argParser.add_argument('--era',        action='store',      type=str,     help="Which era?" )
args = argParser.parse_args()

outFile = ROOT.TFile("./BTag_calibration_"+args.era+".root", "RECREATE")

if args.era == "2016":
    from tttt.samples.nano_mc_private_UL20_Summer16_postProcessed_dilep  import * 
elif args.era == "2016_preVFP":
    from tttt.samples.nano_mc_private_UL20_Summer16_preVFP_postProcessed_dilep  import * 
elif args.era == "2017":
    from tttt.samples.nano_mc_private_UL20_Fall17_postProcessed_dilep    import  *
elif args.era == "2018":
    from tttt.samples.nano_mc_private_UL20_Autumn18_postProcessed_dilep  import  *
elif args.era == 'RunII':
    from tttt.samples.nano_private_UL20_RunII_postProcessed_dilep import *

TTLep_bb = copy.deepcopy( TTLep )
TTLep_bb.name = "TTLep_bb"
TTLep_bb.texName = "t#bar{t}b#bar{b}"
TTLep_bb.color   = color.TTbb
TTLep_bb.setSelectionString( "genTtbarId%100>=50" )
TTLep_cc    = copy.deepcopy( TTLep )
TTLep_cc.name = "TTLep_cc"
TTLep_cc.texName = "t#bar{t}c#bar{c}"
TTLep_cc.color   = color.TTcc
TTLep_cc.setSelectionString( "genTtbarId%100>=40&&genTtbarId%100<50" )
TTLep_other = copy.deepcopy( TTLep )
TTLep_other.name = "TTLep_other"
TTLep_other.texName = "t#bar{t} + light j."
TTLep_other.color = color.TTlight
TTLep_other.setSelectionString( "genTtbarId%100<40" )


samples = [ TTbb, TTLep_bb, TTLep_cc, TTLep_other, ST_tch ,ST_twch , TTW, TTH, TTZ, TTTT, DY, DiBoson]

if args.small:
    for sample in samples:
        sample.reduceFiles(to=1)


bTagVariations =[{'name':'BTagSFCentral', 'oldName':'reweightBTagSF_central',},
                  {'name':'BTagSFJesDown', 'oldName':'reweightBTagSF_down_jes',},
                  {'name':'BTagSFJesUp', 'oldName':'reweightBTagSF_up_jes',},
                  {'name':'BTagSFHfDown', 'oldName':'reweightBTagSF_down_hf',},
                  {'name':'BTagSFHfUp', 'oldName':'reweightBTagSF_up_hf',},
                  {'name':'BTagSFLfDown', 'oldName':'reweightBTagSF_down_lf',},
                  {'name':'BTagSFLfUp', 'oldName':'reweightBTagSF_up_lf',},
                  {'name':'BTagSFHfs1Down', 'oldName':'reweightBTagSF_down_hfstats1',},
                  {'name':'BTagSFHfs1Up', 'oldName':'reweightBTagSF_up_hfstats1',},
                  {'name':'BTagSFHfs2Down', 'oldName':'reweightBTagSF_down_hfstats2',},
                  {'name':'BTagSFHfs2Up', 'oldName':'reweightBTagSF_up_hfstats2',},
                  {'name':'BTagSFLfs1Down', 'oldName':'reweightBTagSF_down_lfstats1',},
                  {'name':'BTagSFLfs1Up', 'oldName':'reweightBTagSF_up_lfstats1',},
                  {'name':'BTagSFLfs2Down', 'oldName':'reweightBTagSF_down_lfstats2',},
                  {'name':'BTagSFLfs2Up', 'oldName':'reweightBTagSF_up_lfstats2',},
                  {'name':'BTagSFCfe1Down', 'oldName':'reweightBTagSF_down_cferr1',},
                  {'name':'BTagSFCfe1Up', 'oldName':'reweightBTagSF_up_cferr1',},
                  {'name':'BTagSFCfe2Down', 'oldName':'reweightBTagSF_down_cferr2',},
                  {'name':'BTagSFCfe2Up', 'oldName':'reweightBTagSF_up_cferr2'}]


for sample in samples:
  category = outFile.mkdir(sample.name)
  category.cd()
  for weight in bTagVariations:
    hist = ROOT.TH1F(weight['name'],weight['name'],15,0,15)
    for njet in range(0, 15):
        n = sample.getYieldFromDraw("nJetGood=="+str(njet))
        #print sample.name , n['val'], "CENTRAL"
        rw_n  = sample.getYieldFromDraw("nJetGood=="+str(njet),weight['oldName'])
        if not rw_n['val']==0 : rw_factor = n['val']/rw_n['val']
        else: rw_factor=1
        #print weight, rw_n['val'], rw_factor
        hist.SetBinContent(njet,rw_factor)
    category.cd()
    hist.Write(weight['name'])
    print "done with sample "+sample.name+" and variation "+weight['name']
 
outFile.Close()

