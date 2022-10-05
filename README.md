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
cp -r /groups/hephy/cms/dennis.schwarz/correctionlib .
cd $CMSSW_BASE

scram b -j40
```
