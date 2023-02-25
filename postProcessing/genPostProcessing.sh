#!/bin/sh
# python genPostProcessing.py --targetDir v2 --overwrite --addReweights --logLevel INFO --interpolationOrder 2 --delphesEra RunII --sample TTTT_MS #SPLIT493
# python genPostProcessing.py --targetDir v2 --overwrite --addReweights --logLevel INFO --interpolationOrder 2 --delphesEra RunII --sample TTbb_MS #SPLIT497
# python genPostProcessing.py --targetDir v4 --overwrite --addReweights --logLevel INFO --interpolationOrder 2 --delphesEra RunII --sample TTTT_MS #SPLIT493
# python genPostProcessing.py --targetDir v4 --overwrite --addReweights --logLevel INFO --interpolationOrder 2 --delphesEra RunII --sample TTbb_MS #SPLIT497
python genPostProcessing.py --targetDir v6 --overwrite --addReweights --logLevel INFO --interpolationOrder 2 --delphesEra RunII --sample TTTT_MS --config ttbb_2l --add_training_vars --trainingCoefficients ctt cQQ1 cQQ8 cQt1 cQt8 ctHRe ctHIm #SPLIT493
# python genPostProcessing.py --targetDir v6 --overwrite --addReweights --logLevel INFO --interpolationOrder 2 --delphesEra RunII --sample TTbb_MS --config ttbb_2l --add_training_vars #SPLIT497
