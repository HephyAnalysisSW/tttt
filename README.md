# tttt 
```
cmsrel CMSSW_10_6_28
cd CMSSW_10_6_28/src
cmsenv
git cms-init
git clone https://github.com/HephyAnalysisSW/tttt
git clone https://github.com/HephyAnalysisSW/TMB
git clone https://github.com/HephyAnalysisSW/tWZ
cd tWZ
git checkout UL
cd ..
git clone https://github.com/HephyAnalysisSW/Analysis
git clone https://github.com/HephyAnalysisSW/Samples
git clone https://github.com/HephyAnalysisSW/RootTools
cd Analysis/Tools/python
git clone --recursive git@github.com:cms-nanoAOD/correctionlib.git
cd correctionlib
make PYTHON=python
make install

scram b -j40
```
