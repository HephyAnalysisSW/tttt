#!/bin/bash
declare -a sys=('LeptonSFDown' 'LeptonSFUp' 'PUDown' 'PUUp'
                'L1PrefireDown' 'L1PrefireUp' 'BTagSFJesDown' 'BTagSFJesUp'
                'BTagSFHfDown' 'BTagSFHfUp' 'BTagSFLfDown' 'BTagSFLfUp'
                'BTagSFHfs1Down' 'BTagSFHfs1Up' 'BTagSFLfs1Down' 'BTagSFLfs1Up'
                'BTagSFHfs2Down' 'BTagSFHfs2Up' 'BTagSFLfs2Down' 'BTagSFLfs2Up'
                'BTagSFCfe1Down' 'BTagSFCfe1Up' 'BTagSFCfe2Down' 'BTagSFCfe2Up'
                'noTopPtReweight' 'HDampUp' 'HDampDown' 'jesTotalUp'
                'jesTotalDown' 'ScaleDownDown' 'ScaleDownNone' 'ScaleNoneDown'
                'ScaleNoneUp' 'ScaleUpNone' 'ScaleUpUp' 'ISRUp'
                'ISRDown' 'FSRUp' 'FSRDown' 'central')
for i in {1..100};do
  pdf="PDF_${i}"
  pdfs+=("$pdf")
done
declare -a cuts=('trg-dilep-OS-minDLmass20-offZ1-lepVeto2-njet8p-btag1-ht500'
                'trg-dilep-OS-minDLmass20-offZ1-lepVeto2-njet4to5-btag1-ht500'
                'trg-dilep-OS-minDLmass20-offZ1-lepVeto2-njet4to5-btag2-ht500'
                'trg-dilep-OS-minDLmass20-offZ1-lepVeto2-njet4to5-btag3p-ht500'
                'trg-dilep-OS-minDLmass20-offZ1-lepVeto2-njet6to7-btag1-ht500'
                'trg-dilep-OS-minDLmass20-offZ1-lepVeto2-njet6to7-btag2-ht500'
                'trg-dilep-OS-minDLmass20-offZ1-lepVeto2-njet6to7-btag3p-ht500'
                'trg-dilep-OS-minDLmass20-offZ1-lepVeto2-njet8p-btag3p-ht500'
                'trg-dilep-OS-minDLmass20-offZ1-lepVeto2-njet8p-btag2-ht500')
# All systematics files
for e in "2018" "2017" "2016" "2016_preVFP", "RunII";do
  for c in ${cuts[@]};do
    for s in ${sys[@]};do
      echo submit "python systematics.py --plot_directory 4t-v13-syst --selection $c --era $e --sys $s"
      submit "python systematics.py --plot_directory 4t-v13-syst --selection $c --era $e --sys $s"
    done
    for pdf in "${pdfs[@]}";do
      echo submit "python systematics.py --plot_directory 4t-v13-syst --selection $c --era $e --sys $pdf"
      submit "python systematics.py --plot_directory 4t-v13-syst --selection $c --era $e --sys $pdf"
    done
  done
done

# EFT files
declare -a WC=("cQQ1")
for c in ${cuts[@]};do
  for coeff in ${WC[@]};do
    echo submit "python systematics.py --plot_directory 4t-v13-syst --selection $c --era 2018 --wc $coeff"
    submit "python systematics.py --plot_directory 4t-v13-syst --selection $c --era 2018 --wc $coeff"
  done
done
