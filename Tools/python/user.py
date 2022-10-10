import os

if os.environ["USER"] in ["maryam.shooshtari"]:
    postprocessing_output_directory = "/scratch-cbe/users/maryam.shooshtari/tttt/nanoTuples"
    postprocessing_tmp_directory    = "/scratch/hephy/cms/maryam.shooshtari/tttt/tmp/"
    plot_directory                  = "/groups/hephy/cms/maryam.shooshtari/www/tttt/plots"
    cache_dir                       = "/groups/hephy/cms/maryam.shooshtari/tttt/caches"
    # Analysis result files
    cern_proxy_certificate          = "/users/maryam.shooshtari/.private/.proxy"
if os.environ["USER"] in ["cristina.giordano"]:
    postprocessing_output_directory = "/scratch-cbe/users/cristina.giordano/tttt/nanoTuples"
    postprocessing_tmp_directory    = "/scratch/hephy/cms/cristina.giordano/tttt/tmp/"
    plot_directory                  = "/groups/hephy/cms/cristina.giordano/www/tttt/plots"
    cache_dir                       = "/groups/hephy/cms/cristina.giordano/tttt/caches"
    # Analysis result files
    cern_proxy_certificate          = "/users/cristina.giordano/.private/.proxy"

