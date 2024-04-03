#!/bin/bash -x
#SBATCH -D /users/$USER/tttt/CMSSW_10_6_28/src/tttt/analysis/systematics/dataCards/
#SBATCH --job-name=combine
#SBATCH --output=/scratch/$USER/batch_output/combine-%j.log
#SBATCH --time="08:00:00"
#SBATCH --mem=20GB


#How to run Combine commands without going crazy :)
declare -A regions=(
		    ['njet4to5_btag3p']='njet4to5_btag3p'   ['njet4to5_btag2']='njet4to5_btag2' ['njet4to5_btag1']='njet4to5_btag1'
            ['njet6to7_btag3p']='njet6to7_btag3p'   ['njet6to7_btag2']='njet6to7_btag2' ['njet6to7_btag1']='njet6to7_btag1'
            ['njet8p_btag3p']='njet8p_btag3p'       ['njet8p_btag2']='njet8p_btag2'     ['njet8p_btag1']='njet8p_btag1' 
#           ['njet6p_btag3p']='njet6p_btag3p'     ['njet6p_btag2']='njet6p_btag2'     ['njet6p_btag1']='njet6p_btag1'
		    )

declare -A variables=(['ht']='ht' ['mva']='2l_4t' ['nJetGood']='nJetGood' ['nBTag']='nBTag')
declare -A masking=(['nJetGood']='nJetGood' ['nBTag']='nBTag') # ['mva']='2l_4t')

declare -A ht_mask_regions=(
		    ['njet4to5_btag3p']='njet4to5_btag3p'
            ['njet6to7_btag3p']='njet6to7_btag3p'
            ['njet8p_btag3p']='njet8p_btag3p'    
            )
declare -A mva_mask_regions=(
		       ['njet4to5_btag2']='njet4to5_btag2' ['njet4to5_btag1']='njet4to5_btag1'
               ['njet6to7_btag2']='njet6to7_btag2' ['njet6to7_btag1']='njet6to7_btag1'
               ['njet8p_btag2']='njet8p_btag2'     ['njet8p_btag1']='njet8p_btag1' 
                )
for region in "${!ht_mask_regions[@]}";do
    neverendingStory+="mask_ht_$region""=1,"
done
for region in "${!mva_mask_regions[@]}";do
    neverendingStory+="mask_mva_$region""=1,"
done

for mask in "${!masking[@]}";do
  for region in "${!regions[@]}";do
    neverendingStory+="mask_$mask""_$region""=1,"
  done
done
length=${#neverendingStory}
maskingString="${neverendingStory:0:length-1}"
#echo $neverendingStory

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
      theEndlessScroll+="$variable""_$region=ttttEFT_${variables[$variable]}""_1_13TeV_${regions[$region]}"".txt "
    done
  done
  theEndlessScroll+=">& combined.txt"
  eval "$theEndlessScroll"
  echo "* autoMCStats 0 1" >> combined.txt
  wait
  eval "text2workspace.py combined.txt --channel-masks -P HiggsAnalysis.AnalyticAnomalousCoupling.AnomalousCouplingEFTNegative:analiticAnomalousCouplingEFTNegative --X-allow-no-signal --PO eftOperators=cQQ1"
  wait

elif $impact; then
#not updated
  echo "Executing (Second) Impact"
  python combineTool.py -M Impacts -d combined.root -m 125 -t -1 --doInitialFit --robustFit 1 --expectSignal=1  --freezeNuisanceGroups=theory
  python combineTool.py -M Impacts -d combined.root -m 125 -t -1 --doFits --robustFit 1 --expectSignal=1   --freezeNuisanceGroups=theory --parallel 10
  python combineTool.py -M Impacts -d combined.root -m 125 -o impacts_combined.json
  python ../plotImpacts.py -i impacts_combined.json -o impacts_combined

elif $postfit; then
  echo "Executing Postfit."
  diagnosticStory="combine combined.root -t -1 -M FitDiagnostics --plots --saveShapes --saveWithUnc -n .postFit_combined  --cminDefaultMinimizerStrategy=0 --redefineSignalPOIs k_cQQ1 --freezeParameters r --setParameterRanges k_cQQ1=-10,10  --setParameters r=1,"
  diagnosticStory+="${neverendingStory}"
  echo $diagnosticStory
  #python postFitPlotter.py --inputFile dataCards/fitDiagnostics.postFit_combined.root --backgroundOnly

elif $multi; then
  echo "Executing Multi."
  multidimStory="combine combined.root -t -1 -M MultiDimFit --saveWorkspace --algo grid --points 100 -n .combinedFit --redefineSignalPOIs k_cQQ1 --freezeParameters r --setParameterRanges k_cQQ1=-10,10 --setParameters r=1,"
  multidimStory+="${neverendingStory}"
  echo $multidimStory
  #python ../plot1Dscan.py higgsCombine.combinedFit.MultiDimFit.mH120.root  --selection CRs --output -o CRs_combined

else
  echo "I did the thing"
fi
