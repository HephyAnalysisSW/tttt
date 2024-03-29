# Recipe for <= CMSSW_12 (python 2) 
```
cmsrel CMSSW_10_6_28
cd CMSSW_10_6_28/src
cmsenv
git cms-init
curl -sLO https://gist.githubusercontent.com/dietrichliko/8aaeec87556d6dd2f60d8d1ad91b4762/raw/a34563dfa03e4db62bb9d7bf8e5bf0c1729595e3/install_correctionlib.sh
. ./install_correctionlib.sh
cmsenv
git clone https://github.com/cms-nanoAOD/nanoAOD-tools.git PhysicsTools/NanoAODTools
git clone git@github.com:HephyAnalysisSW/tttt.git
git clone git@github.com:HephyAnalysisSW/TMB
git clone git@github.com:HephyAnalysisSW/Analysis
git clone git@github.com:HephyAnalysisSW/Samples
git clone git@github.com:HephyAnalysisSW/RootTools
cd $CMSSW_BASE
scram b -j40

```

# Recipe for CMSSW_12 (python 3) 

```
cmsrel CMSSW_12_0_0
cd CMSSW_12_0_0/src
cmsenv
git cms-init
cmsenv
git clone git@github.com:cms-nanoAOD/nanoAOD-tools.git PhysicsTools/NanoAODTools
git clone git@github.com:HephyAnalysisSW/tttt --branch python3
git clone git@github.com:HephyAnalysisSW/Analysis  --branch python3
git clone git@github.com:HephyAnalysisSW/Samples  --branch python3
git clone git@github.com:HephyAnalysisSW/RootTools  --branch python3
cd $CMSSW_BASE
scram b -j40

```


## Delphes

```
cd $CMSSW_BASE/..
git clone https://github.com/TTXPheno/delphes.git
#patch $CMSSW_BASE/../delphes/cards/delphes_card_CMS.tcl < $CMSSW_BASE/src/TTXPheno/patches/slim_delphes.diff # Reduce Delphes output
cd delphes
./configure
sed -i -e 's/c++0x/c++17/g' Makefile
make -j 4 
```

## Recipe for gen production

```
cmsrel CMSSW_10_6_27
cd CMSSW_10_6_27/src
cmsenv
git cms-init
git clone git@github.com:HephyAnalysisSW/tttt.git
cp $CMSSW_BASE/src/tttt/sparse-checkout $CMSSW_BASE/src/.git/info/.
git remote add hephy git@github.com:HephyAnalysisSW/cmssw.git
git pull hephy private-UL-10_6_27
git read-tree -mu HEAD
git clone git@github.com:HephyAnalysisSW/Samples
git clone git@github.com:HephyAnalysisSW/RootTools
cd $CMSSW_BASE
scram b -j40

source /cvmfs/cms.cern.ch/crab3/crab.sh
```
