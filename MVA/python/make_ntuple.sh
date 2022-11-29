#3l config
python make_ntuple.py  --output /eos/vbc/group/cms/$USER/tttt/training-ntuples-tttt --sample TTTT         --config tttt_3l
python make_ntuple.py  --output /eos/vbc/group/cms/$USER/tttt/training-ntuples-tttt --sample TTLep_bb     --config tttt_3l
python make_ntuple.py  --output /eos/vbc/group/cms/$USER/tttt/training-ntuples-tttt --sample TTLep_cc     --config tttt_3l
python make_ntuple.py  --output /eos/vbc/group/cms/$USER/tttt/training-ntuples-tttt --sample TTLep_other  --config tttt_3l

#2l config
python make_ntuple.py  --output /eos/vbc/group/cms/$USER/tttt/training-ntuples-tttt --sample TTTT         --config tttt_2l
python make_ntuple.py  --output /eos/vbc/group/cms/$USER/tttt/training-ntuples-tttt --sample TTLep_bb     --config tttt_2l
python make_ntuple.py  --output /eos/vbc/group/cms/$USER/tttt/training-ntuples-tttt --sample TTLep_cc     --config tttt_2l
python make_ntuple.py  --output /eos/vbc/group/cms/$USER/tttt/training-ntuples-tttt --sample TTLep_other  --config tttt_2l
