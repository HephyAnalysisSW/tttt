#!/bin/bash
#How to run Combine commands without going crazy :)
# substitute "echo" with "submit" OR "eval" once the files are there!

declare -A regions=(['njet4to5_btag3p']='njet4to5-btag3p' ['njet4to5_btag2']='njet4to5-btag2' ['njet4to5_btag1']='njet4to5-btag1'
                    ['njet6to7_btag2']='njet6to7-btag2' ['njet6to7_btag1']='njet6to7-btag1'
                    ['njet8p_btag2']='njet8p-btag2' ['njet8p_btag1']='njet8p-btag1')
declare -A variables=(['mva']='2l_4t' ['nJetGood']='nJetGood' ['nBTag']='nBTag' ['ht']='ht')
declare -A masking=(['nJetGood']='nJetGood' ['nBTag']='nBTag' ['ht']='ht')

merge=false
asimov=false
postfit=false
impact=false

while getopts "mapi" opt; do
  case $opt in
    m)
      merge=true
      ;;
    a)
      asimov=true
      ;;
    p)
      postfit=true
      ;;
    i)
      impact=true
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
  esac
done

if $merge;then
  echo "Executing Merging."
  theEndlessScroll="combineCards.py "
  for variable in "${!variables[@]}";do
    for region in "${!regions[@]}";do
      theEndlessScroll+="$variable""_$region=tttt_${variables[$variable]}""_1_13TeV_${regions[$region]}"".txt "
    done
  done
  theEndlessScroll+=">& CRs_combined.txt"
  echo "$theEndlessScroll"
  wait
  echo "text2workspace.py CRs_combined.txt --channel-masks"
  wait
elif $asimov; then
  echo "Executing Asimov."
  echo "python combineTool.py -M Impacts -d CRs_combined.root -m 125 -t -1 --doInitialFit --robustFit 1 --expectSignal=1  --freezeNuisanceGroups=theory"
  wait
  echo "python combineTool.py -M Impacts -d CRs_combined.root -m 125 -t -1 --doFits --robustFit 1 --expectSignal=1   --freezeNuisanceGroups=theory --parallel 10"
  wait
  echo "python combineTool.py -M Impacts -d CRs_combined.root -m 125 -o impacts_CRs_combined.json"
  wait
  echo "python ../plotImpacts.py -i impacts_CRs_combined.json -o impacts_CRs_combined"
elif $postfit; then
  echo "Executing Postfit."
  neverendingStory="combine CRs_combined.root -M FitDiagnostics --saveShapes --saveWithUnc  -1 -n .postFit_combined --setParameterRange r=-19,20 --expectSignal=1 --plots --freezeNuisanceGroups=theory --ignoreCovWarning --setParameters "
  for mask in "${!masking[@]}";do
    for region in "${!regions[@]}";do
      neverendingStory+="mask_$mask""_$region""=1,"
    done
  done
  length=${#neverendingStory}
  lastHurra="${neverendingStory:0:length-1}"
  lastHurra+=" -t -1"
  echo "$lastHurra"
  wait
  echo "python postFitPlotter.py --inputFile dataCards/fitDiagnostics.postFit_combined.root --backgroundOnly"

elif $impact; then
  echo "Executing (Second) Impact."
  neverendingStory="combine CRs_combined.root -M MultiDimFit --saveWorkspace  -t -1 --algo grid --points 100 --setParameterRange r=-19,20 -n .combinedFit --expectSignal=1 --freezeNuisanceGroups=theory"
  for mask in "${!masking[@]}";do
    for region in "${!regions[@]}";do
      neverendingStory+="mask_$mask""_$region""=1,"
    done
  done
  length=${#neverendingStory}
  lastHurra="${neverendingStory:0:length-1}"
  lastHurra+=" -t -1"
  echo "$lastHurra"
  wait
  echo "python ../plot1Dscan.py higgsCombine.combinedFit.MultiDimFit.mH120.root  --selection CRs --output -o CRs_combined"
else
  echo "Any other business"
fi
