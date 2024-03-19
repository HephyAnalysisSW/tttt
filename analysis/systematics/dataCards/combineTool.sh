#!/bin/bash -x
#SBATCH -D /users/$USER/tttt/CMSSW_10_6_28/src/tttt/analysis/systematics/dataCards/
#SBATCH --job-name=combine
#SBATCH --output=/scratch/$USER/batch_output/combine-%j.log
#SBATCH --time="08:00:00"
#SBATCH --mem=20GB


#How to run Combine commands without going crazy :)
declare -A regions=(
		   ['njet4to5_btag3p']='njet4to5_btag3p' ['njet4to5_btag2']='njet4to5_btag2' ['njet4to5_btag1']='njet4to5_btag1'
           ['njet6p_btag3p']='njet6p_btag3p'     ['njet6p_btag2']='njet6p_btag2'     ['njet6p_btag1']='njet6p_btag1'
#            ['njet6to7_btag2']='njet6to7_btag2' ['njet6to7_btag1']='njet6to7_btag1'
#            ['njet8p_btag2']='njet8p_btag2' ['njet8p_btag1']='njet8p_btag1'
#		    ['njet8p_btag3p']='njet8p_btag3p' 
#		    ['mvaCut1p_njet6to7_btag3p']='mvaCut0.1p_njet6to7_btag3p'
#		    ['mvaCut1m_njet6to7_btag3p']='mvaCut0.1m_njet6to7_btag3p'
#		    ['mvaCut2p_njet4to5_btag3p']='mvaCut0.2p_njet4to5_btag3p' 
#		    ['mvaCut2m_njet4to5_btag3p']='mvaCut0.2m_njet4to5_btag3p' 
		    )

declare -A variables=(['ht']='ht') #(['mva']='2l_4t' ['nJetGood']='nJetGood' ['nBTag']='nBTag' ['ht']='ht')
declare -A masking=(['nJetGood']='nJetGood' ['nBTag']='nBTag' ['mva']='2l_4t')

for mask in "${!masking[@]}";do
  for region in "${!regions[@]}";do
    neverendingStory+=" mask_$mask""_$region""=1,"
  done
done
length=${#neverendingStory}
maskingString="${neverendingStory:0:length-1}"
# echo $maskingString

unite=false
impact=false
postfit=false
multi=false

while getopts "uipm" opt; do
  case $opt in
    u)
      unite=true
      ;;
    i)
      impact=true
      ;;
    p)
      postfit=true
      ;;
    m)
      multi=true
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
  esac
done

# customizing of parser in single command
if $unite;then
  echo "Executing Unite."
  # Command is bash ../combineTool.sh -u
  theEndlessScroll="combineCards.py "
  for variable in "${!variables[@]}";do
    for region in "${!regions[@]}";do
      theEndlessScroll+="$variable""_$region=ttbbEFT_${variables[$variable]}""_1_13TeV_${regions[$region]}"".txt "
    done
  done
  echo $theEndlessScroll
  theEndlessScroll+=">& combined.txt"
  eval "$theEndlessScroll"
  echo "* autoMCStats 0 1" >> combined.txt
  wait
  echo "text2workspace.py combined.txt --channel-masks"
  wait
elif $impact; then
  echo "Executing (Second) Impact"
  python combineTool.py -M Impacts -d combined.root -m 125 -t -1 --doInitialFit --robustFit 1 --expectSignal=1  --freezeNuisanceGroups=theory
  python combineTool.py -M Impacts -d combined.root -m 125 -t -1 --doFits --robustFit 1 --expectSignal=1   --freezeNuisanceGroups=theory --parallel 10
  python combineTool.py -M Impacts -d combined.root -m 125 -o impacts_combined.json
  python ../plotImpacts.py -i impacts_combined.json -o impacts_combined
elif $postfit; then
  echo "Executing Postfit."
  neverendingStory="combine combined.root -M FitDiagnostics --saveShapes --saveWithUnc  -n .postFit_combined --setParameterRange r=-19,20 --expectSignal=0 --plots  --ignoreCovWarning --setParameters "
  for mask in "${!masking[@]}";do
    for region in "${!regions[@]}";do
      neverendingStory+="mask_$mask""_$region""=1,"
    done
  done
  length=${#neverendingStory}
  lastHurra="${neverendingStory:0:length-1}"
  #lastHurra+=" -t -1"
  echo $lastHurra
  #python postFitPlotter.py --inputFile dataCards/fitDiagnostics.postFit_combined.root --backgroundOnly

elif $multi; then
  echo "Executing Multi."
  neverendingStory="combine combined.root -M MultiDimFit --saveWorkspace  -t -1 --algo grid --points 100 --setParameterRange r=-5,5 -n .combinedFit --expectSignal=1 --setParameters "
  for mask in "${!masking[@]}";do
    for region in "${!regions[@]}";do
      neverendingStory+="mask_$mask""_$region""=1,"
    done
  done
  length=${#neverendingStory}
  lastHurra="${neverendingStory:0:length-1}"
  #lastHurra+=" -t -1"
  echo $lastHurra
  #python ../plot1Dscan.py higgsCombine.combinedFit.MultiDimFit.mH120.root  --selection CRs --output -o CRs_combined
else
  echo "Any other business"
fi
