import os

if os.environ["USER"] in ["maryam.shooshtari"]:
    postprocessing_output_directory = "/scratch-cbe/users/maryam.shooshtari/tttt/nanoTuples"
    postprocessing_tmp_directory    = "/scratch/hephy/cms/maryam.shooshtari/tttt/tmp/"
    plot_directory                  = "/groups/hephy/cms/maryam.shooshtari/www/tttt/plots"
    cache_dir                       = "/groups/hephy/cms/maryam.shooshtari/tttt/caches"
    #cern_proxy_certificate          = "/users/cristina.giordano/.private/.proxy"
elif os.environ["USER"] in ["cristina.giordano"]:
    postprocessing_output_directory = "/scratch-cbe/users/cristina.giordano/tttt/nanoTuples"
    postprocessing_tmp_directory    = "/scratch/hephy/cms/cristina.giordano/tttt/tmp/"
    plot_directory                  = "/groups/hephy/cms/cristina.giordano/www/tttt/plots"
    cache_dir                       = "/groups/hephy/cms/cristina.giordano/tttt/caches"
    cern_proxy_certificate          = "/users/cristina.giordano/.private/.proxy"
elif os.environ["USER"] in ["robert.schoefbeck"]:
    postprocessing_output_directory = "/scratch-cbe/users/robert.schoefbeck/tttt/nanoTuples"
    postprocessing_tmp_directory    = "/scratch/hephy/cms/robert.schoefbeck/tttt/tmp/"
    plot_directory                  = "/groups/hephy/cms/robert.schoefbeck/www/tttt/plots"
    cache_dir                       = "/groups/hephy/cms/robert.schoefbeck/tttt/caches"
