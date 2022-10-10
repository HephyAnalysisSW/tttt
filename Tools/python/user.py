import os

if os.environ["USER"] in ["dennis.schwarz"]:
    postprocessing_output_directory = "/scratch-cbe/users/dennis.schwarz/tttt/nanoTuples"
    postprocessing_tmp_directory    = "/scratch/hephy/cms/dennis.schwarz/tttt/tmp/"
    plot_directory                  = "/groups/hephy/cms/dennis.schwarz/www/tttt/plots"
    cache_dir                       = "/groups/hephy/cms/dennis.schwarz/tWZ/caches"
    # Analysis result files
    cern_proxy_certificate          = "/users/dennis.schwarz/.private/.proxy"
if os.environ["USER"] in ["cristina.giordano"]:
    postprocessing_output_directory = "/scratch-cbe/users/cristina.giordano/tttt/nanoTuples"
    postprocessing_tmp_directory    = "/scratch/hephy/cms/cristina.giordano/tttt/tmp/"
    plot_directory                  = "/groups/hephy/cms/cristina.giordano/www/tttt/plots"
    cache_dir                       = "/groups/hephy/cms/cristina.giordano/tttt/caches"
    # Analysis result files
    cern_proxy_certificate          = "/users/cristina.giordano/.private/.proxy"

