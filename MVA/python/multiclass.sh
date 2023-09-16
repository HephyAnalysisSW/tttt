#python multiclass.py --input_directory /eos/vbc/group/cms/$USER/tttt/training-ntuples-tttt-v3/MVA-training/ --name tttt_2l --config tttt_2l
#python multiclass.py --input_directory /eos/vbc/group/cms/$USER/tttt/training-ntuples-tttt/MVA-training/ --name tttt_2l --config tttt_2l_v2 #--add_LSTM
#python multiclass_generator.py --input_directory /eos/vbc/group/cms/$USER/tttt/training-ntuples-tttt-v3/MVA-training/ --name tttt_2l_2 --config tttt_2l
#python multiclass_generator.py --input_directory /eos/vbc/group/cms/$USER/tttt/training-ntuples-tttt-v3/MVA-training/ --name tttt_2l_lstm_2 --config tttt_2l --add_LSTM
python multiclass.py --input_directory /eos/vbc/group/cms/$USER/tttt/training-ntuples-ttbb/MVA-training/ --activation sigmoid --name ttbb_eft --config ttbb_eft #--add_LSTM
