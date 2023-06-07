#!/bin/bash
declare -a sys=('LeptonSFDown' 'LeptonSFUp' 'PUDown' 'PUUp'
                'L1PrefireDown' 'L1PrefireUp' 'BTagSFJesDown' 'BTagSFJesUp'
                'BTagSFHfDown' 'BTagSFHfUp' 'BTagSFLfDown' 'BTagSFLfUp'
                'BTagSFHfs1Down' 'BTagSFHfs1Up' 'BTagSFLfs1Down' 'BTagSFLfs1Up',
                'BTagSFHfs2Down' 'BTagSFHfs2Up' 'BTagSFLfs2Down' 'BTagSFLfs2Up',
                'BTagSFCfe1Down' 'BTagSFCfe1Up' 'BTagSFCfe2Down' 'BTagSFCfe2Up',
         	      'noTopPtReweight' 'HDampUp' 'HDampDown' 'jesTotalUp'
                'jesTotalDown' 'ScaleDownDown' 'ScaleDownNone' 'ScaleNoneDown'
                'ScaleNoneUp' 'ScaleUpNone' 'ScaleUpUp' 'ISRUp'
                'ISRDown' 'FSRUp' 'FSRDown')
for i in {1..100};do
  pdf="PDF_${i}"
  pdfs+=("$pdf")
done
declare -a cuts=('trg-dilepL-OS-minDLmass20-offZ1-lepVeto2-njet4to5-btag2-ht500' 'trg-dilepL-OS-minDLmass20-offZ1-lepVeto2-njet6to7-btag3-ht500' '')
for e in "RunII" "2016" "2016_preVFP" "2017" "2018";do
  for s in ${sys[@]};do
    echo submit "python systematics.py --plot_directory 4t-v10-syst --selection "${cuts[0]}" --era $e --sys $s"
    submit "python systematics.py --plot_directory 4t-v10-syst --selection "${cuts[0]}" --era $e --sys $s"
    echo submit "python systematics.py --plot_directory 4t-v10-syst --selection "${cuts[1]}" --era $e --sys $s"
    submit "python systematics.py --plot_directory 4t-v10-syst --selection "${cuts[1]}" --era $e --sys $s"
  done
  for pdf in "${pdfs[@]}";do
    echo submit "python systematics.py --plot_directory 4t-v10-syst --selection "${cuts[0]}" --era $e --sys $pdf"
    submit "python systematics.py --plot_directory 4t-v10-syst --selection "${cuts[0]}" --era $e --sys $pdf"
    echo submit "python systematics.py --plot_directory 4t-v10-syst --selection "${cuts[1]}" --era $e --sys $pdf"
    submit "python systematics.py --plot_directory 4t-v10-syst --selection "${cuts[1]}" --era $e --sys $pdf"
  done
done
