#!/bin/sh
# python genPostProcessing.py --targetDir v2 --overwrite --addReweights --logLevel INFO --interpolationOrder 2 --delphesEra RunII --sample TTTT_MS #SPLIT493
# python genPostProcessing.py --targetDir v2 --overwrite --addReweights --logLevel INFO --interpolationOrder 2 --delphesEra RunII --sample TTbb_MS #SPLIT497
# python genPostProcessing.py --targetDir v4 --overwrite --addReweights --logLevel INFO --interpolationOrder 2 --delphesEra RunII --sample TTTT_MS #SPLIT493
# python genPostProcessing.py --targetDir v4 --overwrite --addReweights --logLevel INFO --interpolationOrder 2 --delphesEra RunII --sample TTbb_MS #SPLIT497
#python genPostProcessing.py --targetDir v6 --overwrite --addReweights --logLevel INFO --interpolationOrder 2 --delphesEra RunII --sample TTTT_MS --config ttbb_2l --add_training_vars --trainingCoefficients ctt cQQ1 cQQ8 cQt1 cQt8 ctHRe ctHIm #SPLIT493
#python genPostProcessing.py --targetDir v6 --overwrite --addReweights --logLevel INFO --interpolationOrder 2 --delphesEra RunII --sample TTbb_MS --config ttbb_2l --add_training_vars #SPLIT497
# python genPostProcessing.py --targetDir v6 --overwrite --logLevel INFO --interpolationOrder 2 --delphesEra RunII --sample TT_2L --config ttbb_2l --miniAOD --add_training_vars #SPLIT307
python genPostProcessing_weightsum.py --targetDir v6w --overwrite --logLevel INFO --interpolationOrder 2 --delphesEra RunII --sample TT_2L --config ttbb_2l --miniAOD 
python genPostProcessing_weightsum.py --targetDir v6w --overwrite --addReweights --logLevel INFO --interpolationOrder 2 --delphesEra RunII --sample TTTT_MS 
python genPostProcessing_weightsum.py --targetDir v6w --overwrite --addReweights --logLevel INFO --interpolationOrder 2 --delphesEra RunII --sample TTbb_MS 
python genPostProcessing_weightsum.py --targetDir v7w --overwrite --logLevel INFO --interpolationOrder 2 --delphesEra RunII --sample TT_2L --config ttbb_2l --miniAOD #SPLIT307
python genPostProcessing_weightsum.py --targetDir v7w --overwrite --addReweights --logLevel INFO --interpolationOrder 2 --delphesEra RunII --sample TTTT_MS #SPLIT493
python genPostProcessing_weightsum.py --targetDir v7w --overwrite --addReweights --logLevel INFO --interpolationOrder 2 --delphesEra RunII --sample TTbb_MS #SPLIT497
