import os
import ROOT

plot_path = "/groups/hephy/cms/lena.wild/www/tttt/plots/analysisPlots/"
plot_directory = "new_training_500_noData"
dirname = os.path.join(plot_path, plot_directory,"RunII/all/")
results_dir = os.path.join(plot_path, plot_directory,"RunII/roc/")
njetsel = [
"dilepL-offZ1-njet4p-btag3p-ht500/",
"dilepL-offZ1-njet5p-btag3p-ht500/",
"dilepL-offZ1-njet6p-btag3p-ht500/",
"dilepL-offZ1-njet7p-btag3p-ht500/",
"dilepL-offZ1-njet8p-btag3p-ht500/",
"dilepL-offZ1-njet9p-btag3p-ht500/"
]

data_batch = [
("2l MVA (batch size: 5000)", "MVA_TTTT_model_b-5000_e-500_hs1-70_hs2-40.root",ROOT.kRed+4),
("2l MVA (batch size: 10000)", "MVA_TTTT_model_b-10000_e-500_hs1-70_hs2-40.root",ROOT.kRed+2),
("2l MVA (batch size: 20000)", "MVA_TTTT_model_b-20000_e-500_hs1-70_hs2-40.root",ROOT.kRed-4),
("2l MVA (batch size: 50000)", "MVA_TTTT_model_b-50000_e-500_hs1-70_hs2-40.root",ROOT.kRed-7),
("2l MVA (batch size: 100000)", "MVA_TTTT_model_b-100000_e-500_hs1-70_hs2-40.root",ROOT.kRed-9)
]

data_h1 = [
("2l MVA (size of 1st hidden layer: 35)", "MVA_TTTT_model_b-20000_e-500_hs1-35_hs2-40.root",ROOT.kMagenta+4),
("2l MVA (size of 1st hidden layer: 70)", "MVA_TTTT_model_b-20000_e-500_hs1-70_hs2-40.root",ROOT.kMagenta+2),
("2l MVA (size of 1st hidden layer: 105)", "MVA_TTTT_model_b-20000_e-500_hs1-105_hs2-40.root",ROOT.kMagenta),
("2l MVA (size of 1st hidden layer: 135)", "MVA_TTTT_model_b-20000_e-500_hs1-140_hs2-40.root",ROOT.kMagenta-9),
]

data_h2 = [
("2l MVA (size of 2nd hidden layer: 20)", "MVA_TTTT_model_b-20000_e-500_hs1-70_hs2-20.root",ROOT.kBlue+4),
("2l MVA (size of 2nd hidden layer: 30)", "MVA_TTTT_model_b-20000_e-500_hs1-70_hs2-30.root",ROOT.kBlue+2),
("2l MVA (size of 2nd hidden layer: 35)", "MVA_TTTT_model_b-20000_e-500_hs1-70_hs2-35.root",ROOT.kBlue-4),
("2l MVA (size of 2nd hidden layer: 40)", "MVA_TTTT_model_b-20000_e-500_hs1-70_hs2-40.root",ROOT.kBlue-7),
("2l MVA (size of 2nd hidden layer: 50)", "MVA_TTTT_model_b-20000_e-500_hs1-70_hs2-50.root",ROOT.kBlue-9)
]

data_lstm = [
("2l MVA including 1 LSTM layer", "MVA_TTTT_model_b-20000_e-500_hs1-70_hs2-40_lstm-1_hs-lstm-10.root",ROOT.kGreen+4),
("2l MVA including 2 LSTM layers", "MVA_TTTT_model_b-20000_e-500_hs1-70_hs2-40_lstm-2_hs-lstm-10.root",ROOT.kGreen+3),
("2l MVA including 4 LSTM layers", "MVA_TTTT_model_b-20000_e-500_hs1-70_hs2-40_lstm-4_hs-lstm-10.root", ROOT.kGreen+2),
("2l MVA including 6 LSTM layers", "MVA_TTTT_model_b-20000_e-500_hs1-70_hs2-40_lstm-6_hs-lstm-10.root",ROOT.kGreen+0),
("2l MVA including 8 LSTM layers", "MVA_TTTT_model_b-20000_e-500_hs1-70_hs2-40_lstm-8_hs-lstm-10.root",ROOT.kGreen-9)
]

data_db = [
("2l MVA including 1 LSTM layer and doubleB", "MVA_TTTT_model_b-20000_e-500_hs1-70_hs2-40_lstm-1_hs-lstm-10_DoubleB.root",ROOT.kCyan+4),
("2l MVA including 2 LSTM layers and doubleB", "MVA_TTTT_model_b-20000_e-500_hs1-70_hs2-40_lstm-2_hs-lstm-10_DoubleB.root",ROOT.kCyan+3),
 ("2l MVA including 4 LSTM layers and doubleB", "MVA_TTTT_model_b-20000_e-500_hs1-70_hs2-40_lstm-4_hs-lstm-10_DoubleB.root",ROOT.kCyan+2),
 ("2l MVA including 6 LSTM layers and doubleB", "MVA_TTTT_model_b-20000_e-500_hs1-70_hs2-40_lstm-6_hs-lstm-10_DoubleB.root",ROOT.kCyan+1),
 ("2l MVA including 8 LSTM layers and doubleB", "MVA_TTTT_model_b-20000_e-500_hs1-70_hs2-40_lstm-8_hs-lstm-10_DoubleB.root",ROOT.kCyan+0),
]

data_hs_lstm = [
("2l MVA, 4 LSTM layers, output size of LSTM: 5",  "MVA_TTTT_model_b-20000_e-500_hs1-70_hs2-40_lstm-4_hs-lstm-5.root",ROOT.kOrange+8),
("2l MVA, 4 LSTM layers, output size of LSTM: 10", "MVA_TTTT_model_b-20000_e-500_hs1-70_hs2-40_lstm-4_hs-lstm-10.root",ROOT.kOrange+3),
("2l MVA, 4 LSTM layers, output size of LSTM: 15", "MVA_TTTT_model_b-20000_e-500_hs1-70_hs2-40_lstm-4_hs-lstm-15.root",ROOT.kOrange+2),
("2l MVA, 4 LSTM layers, output size of LSTM: 25", "MVA_TTTT_model_b-20000_e-500_hs1-70_hs2-40_lstm-4_hs-lstm-25.root", ROOT.kOrange+1),
]

data_hs_lstm_db = [
("2l MVA, 4 LSTM layers and DoubleB, output size of LSTM: 5",   "MVA_TTTT_model_b-20000_e-500_hs1-70_hs2-40_lstm-4_hs-lstm-5_DoubleB.root",ROOT.kPink-7),
("2l MVA, 4 LSTM layers and DoubleB, output size of LSTM: 10",  "MVA_TTTT_model_b-20000_e-500_hs1-70_hs2-40_lstm-4_hs-lstm-10_DoubleB.root",ROOT.kPink-6),
("2l MVA, 4 LSTM layers and DoubleB, output size of LSTM: 15",  "MVA_TTTT_model_b-20000_e-500_hs1-70_hs2-40_lstm-4_hs-lstm-15_DoubleB.root", ROOT.kPink-5),
("2l MVA, 4 LSTM layers and DoubleB, output size of LSTM: 25",  "MVA_TTTT_model_b-20000_e-500_hs1-70_hs2-40_lstm-4_hs-lstm-25_DoubleB.root", ROOT.kPink-2),
]                                                               

data_epoch = [
("2l MVA, 4 LSTM layers, output size LSTM: 25, epochs: 500",   "MVA_TTTT_model_b-20000_e-500_hs1-70_hs2-40_lstm-4_hs-lstm-25.root",ROOT.kPink-7),
("2l MVA, 4 LSTM layers, output size LSTM: 25, epochs: 750",   "MVA_TTTT_model_b-20000_e-750_hs1-70_hs2-40_lstm-4_hs-lstm-25.root",ROOT.kPink-2),
("2l MVA, 4 LSTM layers, output size LSTM: 25, epochs: 2000",   "MVA_TTTT_model_b-20000_e-2000_hs1-70_hs2-40_lstm-4_hs-lstm-25.root",ROOT.kPink-7),
]

data_epoch_db = [
("2l MVA, 4 LSTM layers, output size LSTM: 25, epochs: 500 and doubleB",   "MVA_TTTT_model_b-20000_e-500_hs1-70_hs2-40_lstm-4_hs-lstm-25_DoubleB.root",ROOT.kPink-7),
("2l MVA, 4 LSTM layers, output size LSTM: 25, epochs: 750 and doubleB",   "MVA_TTTT_model_b-20000_e-750_hs1-70_hs2-40_lstm-4_hs-lstm-25_DoubleB.root",ROOT.kPink-2),
("2l MVA, 4 LSTM layers, output size LSTM: 25, epochs: 2000 and doubleB",   "MVA_TTTT_model_b-20000_e-2000_hs1-70_hs2-40_lstm-4_hs-lstm-25_DoubleB.root",ROOT.kPink-7),
]

data_compare = [
("2l MVA ", "MVA_TTTT_model_b-20000_e-500_hs1-70_hs2-40.root",ROOT.kRed),
("2l MVA including 4 LSTM layers", "MVA_TTTT_model_b-20000_e-750_hs1-70_hs2-40_lstm-4_hs-lstm-25.root",ROOT.kBlue),
("2l MVA including 4 LSTM layers and doubleB", "MVA_TTTT_model_b-20000_e-750_hs1-70_hs2-40_lstm-4_hs-lstm-25_DoubleB.root",ROOT.kGreen),
]

data_root = [
(data_batch, "Variation of batch size", "roc_batch"),
(data_h1, "Variation of 1st layer hidden size", "roc_h1"),
(data_h2, "Variation of 2nd layer hidden size", "roc_h2"),
(data_lstm, "Variation of number of LSTM layers", "roc_lstm_layers"),
(data_db, "Variation of number of LSTM layers (+DoubleB)", "roc_lstm+db"),
(data_hs_lstm, "Variation of LSTM output size", "roc_lstm_hs"),
(data_hs_lstm_db, "Variation of number of LSTM output size (+DoubleB)", "roc_lstm_hs+db"),
(data_epoch, "Variation of training epochs", "roc_epoch"),
(data_epoch_db, "Variation of training epochs (+DoubleB)", "roc_epoch+db"),
(data_compare, "Comparison of MVAs (w/o LSTM, w/o DoubleB)", "roc_comp")
]
