#!/bin/bash -x
#SBATCH -D /users/$USER/tttt/CMSSW_10_6_28/src/tttt/analysis/systematics/dataCards/
#SBATCH --job-name=combine
#SBATCH --output=/scratch/$USER/batch_output/combine-%j.log
#SBATCH --time="08:00:00"
#SBATCH --mem=20GB


#How to run Combine commands without going crazy :)
declare -A regions=(['njet4to5_btag3p']='njet4to5-btag3p' ['njet4to5_btag2']='njet4to5-btag2' ['njet4to5_btag1']='njet4to5-btag1'
                    ['njet6to7_btag2']='njet6to7-btag2' ['njet6to7_btag1']='njet6to7-btag1'
                    ['njet8p_btag2']='njet8p-btag2' ['njet8p_btag1']='njet8p-btag1'
                    )
declare -A variables=(['mva']='2l_4t' ['nJetGood']='nJetGood' ['nBTag']='nBTag' ['ht']='ht')
declare -A masking=(['nJetGood']='nJetGood' ['nBTag']='nBTag' ['ht']='ht')

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
      theEndlessScroll+="$variable""_$region=tttt_${variables[$variable]}""_1_13TeV_${regions[$region]}"".txt "
    done
  done
  theEndlessScroll+=">& CRs_combined.txt"
  # * autoMCStats 0 at the end of the file
  eval "$theEndlessScroll"
  echo "* autoMCStats 0" >> CRs_combined.txt
  wait
  submit "text2workspace.py CRs_combined.txt --channel-masks"
  wait
elif $impact; then
  echo "Executing (Second) Impact"
  # python ../combineTool.py -M Impacts -d CRs_combined.root -m 125 -t -1 --doInitialFit --robustFit 1 --expectSignal=0  --freezeNuisanceGroups=theory # --time=00-48:00:00
  # python ../combineTool.py -M Impacts -d CRs_combined.root -m 125 -t -1 --doFits --robustFit 1 --expectSignal=0   --freezeNuisanceGroups=theory --parallel 10
  # python ../combineTool.py -M Impacts -d CRs_combined.root -m 125 -o impacts_CRs_combined.json
  # python ../../plotImpacts.py -i impacts_CRs_combined.json -o impacts_CRs_combined
  # --selection and --plot_directory as for plotting script
elif $postfit; then
  echo "Executing Postfit."
  neverendingStory="combine CRs_combined.root -M FitDiagnostics --saveShapes --saveWithUnc -n .postFit_combined --setParameterRange r=-19,20 --expectSignal=1 --plots --ignoreCovWarning --setParameters "
  for mask in "${!masking[@]}";do
    for region in "${!regions[@]}";do
      neverendingStory+="mask_$mask""_$region""=1,"
    done
  done
  length=${#neverendingStory}
  lastHurra="${neverendingStory:0:length-1}"
  lastHurra+=" -t -1"
  $lastHurra
  wait
  eval "python ../postFitPlotter.py --inputFile fitDiagnostics.postFit_combined.root --backgroundOnly"

elif $multi; then
  echo "Executing Multi."
  # neverendingStory="combine CRs_combined.root -M MultiDimFit --saveWorkspace --algo grid --points 100 --setParameterRange r=-19,20 -n .combinedFit --expectSignal=0"
  # for mask in "${!masking[@]}";do
  #   for region in "${!regions[@]}";do
  #     neverendingStory+="mask_$mask""_$region""=1,"
  #   done
  # done
  # length=${#neverendingStory}
  # lastHurra="${neverendingStory:0:length-1}"
  # # lastHurra+=" -t -1"
  # $lastHurra
  # # plot directory and selection sab
  # python ../plot1Dscan.py higgsCombine.combinedFit.MultiDimFit.mH120.root  --selection CRs --output -o CRs_combined
else
  echo "Any other business"
fi
