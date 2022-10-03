# tttt 
cmsrel CMSSW_10_6_0
cd CMSSW_10_6_0/src
cmsenv
git cms-init
git clone https://github.com/HephyAnalysisSW/TMB
git clone https://github.com/HephyAnalysisSW/tWZ
git clone https://github.com/HephyAnalysisSW/Analysis
git clone https://github.com/HephyAnalysisSW/Samples
git clone https://github.com/HephyAnalysisSW/RootTools
git clone https://github.com/HephyAnalysisSW/NanoAODJMARTools.git PhysicsTools/NanoAODJMARTools
cp $CMSSW_BASE/src/PhysicsTools/NanoAODJMARTools/xmlfiles/* $CMSSW_BASE/config/toolbox/$SCRAM_ARCH/tools/selected/
scram setup fastjet
scram setup fastjet-contrib
scram b -j40
