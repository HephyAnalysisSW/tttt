import os

# Default "latest & greatest"

location_data_UL2016             = "/scratch-cbe/users/maryam.shooshtari/tttt/nanoTuples/tttt_v9/UL2016/dilep-nlepFO2p-ht500/"
location_data_UL2016_preVFP      = "/scratch-cbe/users/maryam.shooshtari/tttt/nanoTuples/tttt_v9/UL2016_preVFP/dilep-nlepFO2p-ht500/"
location_data_UL2017             = "/scratch-cbe/users/maryam.shooshtari/tttt/nanoTuples/tttt_v9/UL2017/dilep-nlepFO2p-ht500/"
location_data_UL2018             = "/scratch-cbe/users/maryam.shooshtari/tttt/nanoTuples/tttt_v9/UL2018/dilep-nlepFO2p-ht500/"

location_mc_UL2016               = "/scratch-cbe/users/maryam.shooshtari/tttt/nanoTuples/tttt_v9/UL2016/dilep-nlepFO2p-ht500/"
location_mc_UL2016_preVFP        = "/scratch-cbe/users/maryam.shooshtari/tttt/nanoTuples/tttt_v9/UL2016_preVFP/dilep-nlepFO2p-ht500/"
location_mc_UL2017               = "/scratch-cbe/users/maryam.shooshtari/tttt/nanoTuples/tttt_v9/UL2017/dilep-nlepFO2p-ht500/"
location_mc_UL2018               = "/scratch-cbe/users/maryam.shooshtari/tttt/nanoTuples/tttt_v9/UL2018/dilep-nlepFO2p-ht500/"

location_data_UL2016_trilep             = "/scratch-cbe/users/cristina.giordano/tttt/nanoTuples/tttt_v7/UL2016/trilep/"
location_data_UL2016_preVFP_trilep      = "/scratch-cbe/users/cristina.giordano/tttt/nanoTuples/tttt_v7/UL2016_preVFP/trilep/"
location_data_UL2017_trilep             = "/scratch-cbe/users/cristina.giordano/tttt/nanoTuples/tttt_v7/UL2017/trilep/"
location_data_UL2018_trilep             = "/scratch-cbe/users/cristina.giordano/tttt/nanoTuples/tttt_v7/UL2018/trilep/"

location_mc_UL2016_trilep               = "/scratch-cbe/users/cristina.giordano/tttt/nanoTuples/tttt_v8/UL2016/trilep/"
location_mc_UL2016_preVFP_trilep        = "/scratch-cbe/users/cristina.giordano/tttt/nanoTuples/tttt_v8/UL2016_preVFP/trilep/"
location_mc_UL2017_trilep               = "/scratch-cbe/users/cristina.giordano/tttt/nanoTuples/tttt_v8/UL2017/trilep/"
location_mc_UL2018_trilep               = "/scratch-cbe/users/cristina.giordano/tttt/nanoTuples/tttt_v8/UL2018/trilep/"

if os.environ["USER"] in ["cristina.giordano", "lena.wild"]:
    location_data_UL2016_trilep             = "/scratch-cbe/users/cristina.giordano/tttt/nanoTuples/tttt_v7/UL2016/trilep/"
    location_data_UL2016_preVFP_trilep      = "/scratch-cbe/users/cristina.giordano/tttt/nanoTuples/tttt_v7/UL2016_preVFP/trilep/"
    location_data_UL2017_trilep             = "/scratch-cbe/users/cristina.giordano/tttt/nanoTuples/tttt_v7/UL2017/trilep/"
    location_data_UL2018_trilep             = "/scratch-cbe/users/cristina.giordano/tttt/nanoTuples/tttt_v7/UL2018/trilep/"

    location_mc_UL2016_trilep               = "/scratch-cbe/users/cristina.giordano/tttt/nanoTuples/tttt_v8/UL2016/trilep/"
    location_mc_UL2016_preVFP_trilep        = "/scratch-cbe/users/cristina.giordano/tttt/nanoTuples/tttt_v8/UL2016_preVFP/trilep/"
    location_mc_UL2017_trilep               = "/scratch-cbe/users/cristina.giordano/tttt/nanoTuples/tttt_v8/UL2017/trilep/"
    location_mc_UL2018_trilep               = "/scratch-cbe/users/cristina.giordano/tttt/nanoTuples/tttt_v8/UL2018/trilep/"

    location_data_UL2016             = "/scratch-cbe/users/robert.schoefbeck/tttt/nanoTuples/tttt_v8/UL2016/dilep-nlepFO2p-ht500/"
    location_data_UL2016_preVFP      = "/scratch-cbe/users/robert.schoefbeck/tttt/nanoTuples/tttt_v8/UL2016_preVFP/dilep-nlepFO2p-ht500/"
    location_data_UL2017             = "/scratch-cbe/users/robert.schoefbeck/tttt/nanoTuples/tttt_v8/UL2017/dilep-nlepFO2p-ht500/"
    location_data_UL2018             = "/scratch-cbe/users/robert.schoefbeck/tttt/nanoTuples/tttt_v8/UL2018/dilep-nlepFO2p-ht500/"

    location_mc_UL2016               = "/scratch-cbe/users/maryam.shooshtari/tttt/nanoTuples/tttt_v8/UL2016/dilep-dilep-nlepFO2p-ht500/"
    location_mc_UL2016_preVFP        = "/scratch-cbe/users/maryam.shooshtari/tttt/nanoTuples/tttt_v8/UL2016_preVFP/dilep/-dilep-nlepFO2p-ht500"
    location_mc_UL2017               = "/scratch-cbe/users/maryam.shooshtari/tttt/nanoTuples/tttt_v8/UL2017/dilep-dilep-nlepFO2p-ht500/"
    location_mc_UL2018               = "/scratch-cbe/users/maryam.shooshtari/tttt/nanoTuples/tttt_v8/UL2018/dilep-dilep-nlepFO2p-ht500/"

elif os.environ["USER"] in ["robert.schoefbeck"]:
    pass

    #location_data_UL2016             = "/scratch-cbe/users/robert.schoefbeck/tttt/nanoTuples/tttt_v8/UL2016/dilep-nlepFO2p-ht500/"
    #location_data_UL2016_preVFP      = "/scratch-cbe/users/robert.schoefbeck/tttt/nanoTuples/tttt_v8/UL2016_preVFP/dilep-nlepFO2p-ht500/"
    #location_data_UL2017             = "/scratch-cbe/users/robert.schoefbeck/tttt/nanoTuples/tttt_v8/UL2017/dilep-nlepFO2p-ht500/"
    #location_data_UL2018             = "/scratch-cbe/users/robert.schoefbeck/tttt/nanoTuples/tttt_v8/UL2018/dilep-nlepFO2p-ht500/"

    #location_mc_UL2016               = "/scratch-cbe/users/maryam.shooshtari/tttt/nanoTuples/tttt_v8/UL2016/dilep-dilep-nlepFO2p-ht500/"
    #location_mc_UL2016_preVFP        = "/scratch-cbe/users/maryam.shooshtari/tttt/nanoTuples/tttt_v8/UL2016_preVFP/dilep-dilep-nlepFO2p-ht500/"
    #location_mc_UL2017               = "/scratch-cbe/users/maryam.shooshtari/tttt/nanoTuples/tttt_v8/UL2017/dilep-dilep-nlepFO2p-ht500/"
    #location_mc_UL2018               = "/scratch-cbe/users/maryam.shooshtari/tttt/nanoTuples/tttt_v8/UL2018/dilep-dilep-nlepFO2p-ht500/"

    #location_data_UL2016_trilep             = "/scratch-cbe/users/robert.schoefbeck/tttt/nanoTuples/tttt_v7-skimmed/UL2016/trilep/"
    #location_data_UL2016_preVFP_trilep      = "/scratch-cbe/users/robert.schoefbeck/tttt/nanoTuples/tttt_v7-skimmed/UL2016_preVFP/trilep/"
    #location_data_UL2017_trilep             = "/scratch-cbe/users/robert.schoefbeck/tttt/nanoTuples/tttt_v7-skimmed/UL2017/trilep/"
    #location_data_UL2018_trilep             = "/scratch-cbe/users/robert.schoefbeck/tttt/nanoTuples/tttt_v7-skimmed/UL2018/trilep/"

    #location_mc_UL2016_trilep               = "/scratch-cbe/users/robert.schoefbeck/tttt/nanoTuples/tttt_v7-skimmed/UL2016/trilep/"
    #location_mc_UL2016_preVFP_trilep        = "/scratch-cbe/users/robert.schoefbeck/tttt/nanoTuples/tttt_v7-skimmed/UL2016_preVFP/trilep/"
    #location_mc_UL2017_trilep               = "/scratch-cbe/users/robert.schoefbeck/tttt/nanoTuples/tttt_v7-skimmed/UL2017/trilep/"
    #location_mc_UL2018_trilep               = "/scratch-cbe/users/robert.schoefbeck/tttt/nanoTuples/tttt_v7-skimmed/UL2018/trilep/"

elif os.environ["USER"] in ["maryam.shooshtari"]:
    location_data_UL2016             = "/scratch-cbe/users/maryam.shooshtari/tttt/nanoTuples/tttt_v9/UL2016/dilep-nlepFO2p-ht500/"
    location_data_UL2016_preVFP      = "/scratch-cbe/users/maryam.shooshtari/tttt/nanoTuples/tttt_v9/UL2016_preVFP/dilep-nlepFO2p-ht500/"
    location_data_UL2017             = "/scratch-cbe/users/maryam.shooshtari/tttt/nanoTuples/tttt_v9/UL2017/dilep-nlepFO2p-ht500/"
    location_data_UL2018             = "/scratch-cbe/users/maryam.shooshtari/tttt/nanoTuples/tttt_v9/UL2018/dilep-nlepFO2p-ht500/"

    location_mc_UL2016               = "/scratch-cbe/users/maryam.shooshtari/tttt/nanoTuples/tttt_v9/UL2016/dilep-nlepFO2p-ht500/"
    location_mc_UL2016_preVFP        = "/scratch-cbe/users/maryam.shooshtari/tttt/nanoTuples/tttt_v9/UL2016_preVFP/dilep-nlepFO2p-ht500/"
    location_mc_UL2017               = "/scratch-cbe/users/maryam.shooshtari/tttt/nanoTuples/tttt_v9/UL2017/dilep-nlepFO2p-ht500/"
    location_mc_UL2018               = "/scratch-cbe/users/maryam.shooshtari/tttt/nanoTuples/tttt_v9/UL2018/dilep-nlepFO2p-ht500/"

    location_data_UL2016_trilep             = "/scratch-cbe/users/cristina.giordano/tttt/nanoTuples/tttt_v7/UL2016/trilep/"
    location_data_UL2016_preVFP_trilep      = "/scratch-cbe/users/cristina.giordano/tttt/nanoTuples/tttt_v7/UL2016_preVFP/trilep/"
    location_data_UL2017_trilep             = "/scratch-cbe/users/cristina.giordano/tttt/nanoTuples/tttt_v7/UL2017/trilep/"
    location_data_UL2018_trilep             = "/scratch-cbe/users/cristina.giordano/tttt/nanoTuples/tttt_v7/UL2018/trilep/"

    location_mc_UL2016_trilep               = "/scratch-cbe/users/cristina.giordano/tttt/nanoTuples/tttt_v7/UL2016/trilep/"
    location_mc_UL2016_preVFP_trilep        = "/scratch-cbe/users/cristina.giordano/tttt/nanoTuples/tttt_v7/UL2016_preVFP/trilep/"
    location_mc_UL2017_trilep               = "/scratch-cbe/users/cristina.giordano/tttt/nanoTuples/tttt_v7/UL2017/trilep/"
    location_mc_UL2018_trilep               = "/scratch-cbe/users/cristina.giordano/tttt/nanoTuples/tttt_v7/UL2018/trilep/"


lumi_era = {"Run2016" : (16.5)*1000, "Run2016_preVFP" : (19.5)*1000, "Run2017" : (41.5)*1000, "Run2018" : (59.97)*1000}
