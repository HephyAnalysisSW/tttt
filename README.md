# tttt 
```
cmsrel CMSSW_10_6_28
cd CMSSW_10_6_28/src
cmsenv
git cms-init
curl -sLO https://gist.githubusercontent.com/dietrichliko/8aaeec87556d6dd2f60d8d1ad91b4762/raw/a34563dfa03e4db62bb9d7bf8e5bf0c1729595e3/install_correctionlib.sh
chmod +x install_correctionlib.sh
./install_correctionlib.sh
cmsenv
git clone https://github.com/cms-nanoAOD/nanoAOD-tools.git PhysicsTools/NanoAODTools
git clone https://github.com/HephyAnalysisSW/tttt
git clone https://github.com/HephyAnalysisSW/TMB
git clone https://github.com/HephyAnalysisSW/tWZ --branch UL
git clone https://github.com/HephyAnalysisSW/Analysis
git clone https://github.com/HephyAnalysisSW/Samples
git clone https://github.com/HephyAnalysisSW/RootTools
cd $CMSSW_BASE
scram b -j40

```
