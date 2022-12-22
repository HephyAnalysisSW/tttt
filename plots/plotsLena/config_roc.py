import os
import ROOT

dirname = "/groups/hephy/cms/lena.wild/www/tttt/plots/analysisPlots/tttt_small/RunII/all/dilepL-offZ1-njet4p-btag2p-ht500/"

data_batch = [
("2l MVA (batch size: 5000)", os.path.join(dirname, "lenas_MVA_TTTT_model1.root"),ROOT.kRed+4),
("2l MVA (batch size: 10000)", os.path.join(dirname, "lenas_MVA_TTTT_model2.root"),ROOT.kRed+2),
("2l MVA (batch size: 20000)", os.path.join(dirname, "lenas_MVA_TTTT_model3.root"),ROOT.kRed-4),
("2l MVA (batch size: 50000)", os.path.join(dirname, "lenas_MVA_TTTT_model4.root"),ROOT.kRed-7),
("2l MVA (batch size: 100000)", os.path.join(dirname, "lenas_MVA_TTTT_model5.root"),ROOT.kRed-9)
]

data_h1 = [
("2l MVA (size of 1st hidden layer: 70)", os.path.join(dirname, "lenas_MVA_TTTT_model3.root"),ROOT.kMagenta+4),
("2l MVA (size of 1st hidden layer: 105)", os.path.join(dirname, "lenas_MVA_TTTT_model6.root"),ROOT.kMagenta+2),
("2l MVA (size of 1st hidden layer: 140)", os.path.join(dirname, "lenas_MVA_TTTT_model7.root"),ROOT.kMagenta),
("2l MVA (size of 1st hidden layer: 175)", os.path.join(dirname, "lenas_MVA_TTTT_model8.root"),ROOT.kMagenta-9)
]

data_h2 = [
("2l MVA (size of 2nd hidden layer: 40)", os.path.join(dirname, "lenas_MVA_TTTT_model3.root"),ROOT.kBlue+4),
("2l MVA (size of 2nd hidden layer: 45)", os.path.join(dirname, "lenas_MVA_TTTT_model9.root"),ROOT.kBlue+2),
("2l MVA (size of 2nd hidden layer: 50)", os.path.join(dirname, "lenas_MVA_TTTT_model10.root"),ROOT.kBlue-4),
("2l MVA (size of 2nd hidden layer: 65)", os.path.join(dirname, "lenas_MVA_TTTT_model11.root"),ROOT.kBlue-9)
]

data_lstm = [
("2l MVA including 1 LSTM layer", os.path.join(dirname, "lenas_MVA_TTTT_model1_lstm.root"),ROOT.kGreen+4),
("2l MVA including 2 LSTM layers", os.path.join(dirname, "lenas_MVA_TTTT_model2_lstm.root"),ROOT.kGreen+3),
("2l MVA including 4 LSTM layers", os.path.join(dirname, "lenas_MVA_TTTT_model4_lstm.root"), ROOT.kGreen+2),
("2l MVA including 6 LSTM layers", os.path.join(dirname, "lenas_MVA_TTTT_model6_lstm.root"),ROOT.kGreen+0),
("2l MVA including 8 LSTM layers", os.path.join(dirname, "lenas_MVA_TTTT_model8_lstm.root"),ROOT.kGreen-9)
]

data_db = [
("2l MVA including 1 LSTM layer and doubleB", os.path.join(dirname, "lenas_MVA_TTTT_model1_db_lstm.root"),ROOT.kCyan+4),
("2l MVA including 2 LSTM layers and doubleB", os.path.join(dirname, "lenas_MVA_TTTT_model2_db_lstm.root"),ROOT.kCyan+3),
("2l MVA including 4 LSTM layers and doubleB", os.path.join(dirname, "lenas_MVA_TTTT_model4_db_lstm.root"),ROOT.kCyan+2),
("2l MVA including 6 LSTM layers and doubleB", os.path.join(dirname, "lenas_MVA_TTTT_model6_db_lstm.root"),ROOT.kCyan+1),
("2l MVA including 8 LSTM layers and doubleB", os.path.join(dirname, "lenas_MVA_TTTT_model8_db_lstm.root"),ROOT.kCyan+0)
]

data_compare = [
("2l MVA ", os.path.join(dirname, "lenas_MVA_TTTT_model3.root"),ROOT.kRed),
("2l MVA including 4 LSTM layers", os.path.join(dirname, "lenas_MVA_TTTT_model4_lstm.root"),ROOT.kBlue),
("2l MVA including 4 LSTM layers and doubleB", os.path.join(dirname, "lenas_MVA_TTTT_model4_db_lstm.root"),ROOT.kGreen),
]

data_root = [
(data_batch, "Variation of batch size", "roc_batch"),
(data_h1, "Variation of 1st layer hidden size", "roc_h1"),
(data_h2, "Variation of 2nd layer hidden size", "roc_h2"),
(data_lstm, "Variation of number of LSTM layers", "roc_lstm"),
(data_db, "Variation of number of LSTM layers (+DoubleB)", "roc_lstm+db"),
(data_compare, "Comparison of MVAs (w/o LSTM, w/o DoubleB)", "roc_comp")
]
