import os
import ROOT

plot_path = "/groups/hephy/cms/lena.wild/www/tttt/plots/analysisPlots/"
plot_directory = "training_2p"
dirname = os.path.join(plot_path, plot_directory,"RunII/all/")
results_dir = os.path.join(plot_path, plot_directory,"RunII/roc/")
njetsel = [
"dilepL-offZ1-njet4p-btag2p-ht500/"
]


data_batch_2p = [
("batch size: 5000" , "MVA_TTTT_btag2p_b-5000_e-500_hs1-96_hs2-53.root",ROOT.kRed),
("batch size: 10000", "MVA_TTTT_btag2p_b-10000_e-500_hs1-96_hs2-53.root",ROOT.kRed+4),
("batch size: 20000", "MVA_TTTT_btag2p_b-20000_e-500_hs1-96_hs2-53.root",ROOT.kRed+2),
("batch size: 50000", "MVA_TTTT_btag2p_b-50000_e-500_hs1-96_hs2-53.root",ROOT.kRed-8),
("batch size: 100000", "MVA_TTTT_btag2p_b-100000_e-500_hs1-96_hs2-53.root",ROOT.kRed-4),
]
data_batch_3p = [
("batch size: 5000" , "MVA_TTTT_btag3p_b-5000_e-500_hs1-96_hs2-53.root",ROOT.kRed),
("batch size: 10000", "MVA_TTTT_btag3p_b-10000_e-500_hs1-96_hs2-53.root",ROOT.kRed+4),
("batch size: 20000", "MVA_TTTT_btag3p_b-20000_e-500_hs1-96_hs2-53.root",ROOT.kRed+2),
("batch size: 50000", "MVA_TTTT_btag3p_b-50000_e-500_hs1-96_hs2-53.root",ROOT.kRed-8),
("batch size: 100000","MVA_TTTT_btag3p_b-100000_e-500_hs1-96_hs2-53.root",ROOT.kRed-4),
]

data_h1_2p = [
("1st hidden layer: 48",  "MVA_TTTT_btag2p_b-20000_e-500_hs1-48_hs2-53.root",ROOT.kMagenta+4),
("1st hidden layer: 96",  "MVA_TTTT_btag2p_b-20000_e-500_hs1-96_hs2-53.root",ROOT.kMagenta+2),
("1st hidden layer: 144", "MVA_TTTT_btag2p_b-20000_e-500_hs1-144_hs2-53.root",ROOT.kMagenta),
("1st hidden layer: 192", "MVA_TTTT_btag2p_b-20000_e-500_hs1-192_hs2-53.root",ROOT.kMagenta-9),
]
data_h1_3p = [
("1st hidden layer: 48",  "MVA_TTTT_btag3p_b-20000_e-500_hs1-48_hs2-53.root",ROOT.kMagenta+4),
("1st hidden layer: 96",  "MVA_TTTT_btag3p_b-20000_e-500_hs1-96_hs2-53.root",ROOT.kMagenta+2),
("1st hidden layer: 144", "MVA_TTTT_btag3p_b-20000_e-500_hs1-144_hs2-53.root",ROOT.kMagenta),
("1st hidden layer: 192", "MVA_TTTT_btag3p_b-20000_e-500_hs1-192_hs2-53.root",ROOT.kMagenta-9),
]

data_h2_2p = [
("2nd hidden layer: 33", "MVA_TTTT_btag2p_b-20000_e-500_hs1-96_hs2-33.root",ROOT.kBlue+4),
("2nd hidden layer: 43", "MVA_TTTT_btag2p_b-20000_e-500_hs1-96_hs2-43.root",ROOT.kBlue+2),
("2nd hidden layer: 48", "MVA_TTTT_btag2p_b-20000_e-500_hs1-96_hs2-48.root",ROOT.kBlue-4),
("2nd hidden layer: 53", "MVA_TTTT_btag2p_b-20000_e-500_hs1-96_hs2-53.root",ROOT.kBlue-7),
("2nd hidden layer: 63", "MVA_TTTT_btag2p_b-20000_e-500_hs1-96_hs2-63.root",ROOT.kBlue-8),
]
data_h2_3p = [
("2nd hidden layer: 33", "MVA_TTTT_btag3p_b-20000_e-500_hs1-96_hs2-33.root",ROOT.kBlue+4),
("2nd hidden layer: 43", "MVA_TTTT_btag3p_b-20000_e-500_hs1-96_hs2-43.root",ROOT.kBlue+2),
("2nd hidden layer: 48", "MVA_TTTT_btag3p_b-20000_e-500_hs1-96_hs2-48.root",ROOT.kBlue-4),
("2nd hidden layer: 53", "MVA_TTTT_btag3p_b-20000_e-500_hs1-96_hs2-53.root",ROOT.kBlue-7),
("2nd hidden layer: 63", "MVA_TTTT_btag3p_b-20000_e-500_hs1-96_hs2-63.root",ROOT.kBlue-8),
]

data_lstm_2p = [
("1 LSTM layer",   "MVA_TTTT_btag2p_b-20000_e-500_hs1-96_hs2-53_lstm-1_hs-lstm-10.root",ROOT.kGreen+4),
("2 LSTM layers",  "MVA_TTTT_btag2p_b-20000_e-500_hs1-96_hs2-53_lstm-2_hs-lstm-10.root",ROOT.kGreen+3),
("4 LSTM layers",  "MVA_TTTT_btag2p_b-20000_e-500_hs1-96_hs2-53_lstm-4_hs-lstm-10.root",ROOT.kGreen+2),
("6 LSTM layers",  "MVA_TTTT_btag2p_b-20000_e-500_hs1-96_hs2-53_lstm-6_hs-lstm-10.root",ROOT.kGreen+0),
("8 LSTM layers",  "MVA_TTTT_btag2p_b-20000_e-500_hs1-96_hs2-53_lstm-8_hs-lstm-10.root",ROOT.kGreen-9)
]
data_lstm_3p = [
("1 LSTM layer",   "MVA_TTTT_btag3p_b-20000_e-500_hs1-96_hs2-53_lstm-1_hs-lstm-10.root",ROOT.kGreen+4),
("2 LSTM layers",  "MVA_TTTT_btag3p_b-20000_e-500_hs1-96_hs2-53_lstm-2_hs-lstm-10.root",ROOT.kGreen+3),
("4 LSTM layers",  "MVA_TTTT_btag3p_b-20000_e-500_hs1-96_hs2-53_lstm-4_hs-lstm-10.root",ROOT.kGreen+2),
("6 LSTM layers",  "MVA_TTTT_btag3p_b-20000_e-500_hs1-96_hs2-53_lstm-6_hs-lstm-10.root",ROOT.kGreen+0),
("8 LSTM layers",  "MVA_TTTT_btag3p_b-20000_e-500_hs1-96_hs2-53_lstm-8_hs-lstm-10.root",ROOT.kGreen-9)
]

data_db_2p = [
("1 LSTM layer, doubleB",  "MVA_TTTT_btag2p_b-20000_e-500_hs1-96_hs2-53_lstm-1_hs-lstm-10_DoubleB.root",ROOT.kCyan+4),
("2 LSTM layers, doubleB", "MVA_TTTT_btag2p_b-20000_e-500_hs1-96_hs2-53_lstm-2_hs-lstm-10_DoubleB.root",ROOT.kCyan+3),
#("4 LSTM layers, doubleB", "MVA_TTTT_btag2p_b-20000_e-500_hs1-96_hs2-53_lstm-4_hs-lstm-10_DoubleB.root",ROOT.kCyan+2),
("6 LSTM layers, doubleB", "MVA_TTTT_btag2p_b-20000_e-500_hs1-96_hs2-53_lstm-6_hs-lstm-10_DoubleB.root",ROOT.kCyan+1),
("8 LSTM layers, doubleB", "MVA_TTTT_btag2p_b-20000_e-500_hs1-96_hs2-53_lstm-8_hs-lstm-10_DoubleB.root",ROOT.kCyan+0),
]
data_db_3p = [
("1 LSTM layer, doubleB",  "MVA_TTTT_btag3p_b-20000_e-500_hs1-96_hs2-53_lstm-1_hs-lstm-10_DoubleB.root",ROOT.kCyan+4),
("2 LSTM layers, doubleB", "MVA_TTTT_btag3p_b-20000_e-500_hs1-96_hs2-53_lstm-2_hs-lstm-10_DoubleB.root",ROOT.kCyan+3),
("4 LSTM layers, doubleB", "MVA_TTTT_btag3p_b-20000_e-500_hs1-96_hs2-53_lstm-4_hs-lstm-10_DoubleB.root",ROOT.kCyan+2),
("6 LSTM layers, doubleB", "MVA_TTTT_btag3p_b-20000_e-500_hs1-96_hs2-53_lstm-6_hs-lstm-10_DoubleB.root",ROOT.kCyan+1),
#("8 LSTM layers, doubleB", "MVA_TTTT_btag2p_b-20000_e-500_hs1-96_hs2-53_lstm-8_hs-lstm-10_DoubleB.root",ROOT.kCyan+0),
]

data_hs_lstm_2p = [
("output size of LSTM: 5",  "MVA_TTTT_btag2p_b-20000_e-500_hs1-96_hs2-53_lstm-4_hs-lstm-5.root", ROOT.kOrange+8),
("output size of LSTM: 10", "MVA_TTTT_btag2p_b-20000_e-500_hs1-96_hs2-53_lstm-4_hs-lstm-10.root",ROOT.kOrange+3),
("output size of LSTM: 15", "MVA_TTTT_btag2p_b-20000_e-500_hs1-96_hs2-53_lstm-4_hs-lstm-15.root",ROOT.kOrange+2),
("output size of LSTM: 25", "MVA_TTTT_btag2p_b-20000_e-500_hs1-96_hs2-53_lstm-4_hs-lstm-25.root", ROOT.kOrange+1),
]
data_hs_lstm_3p = [
#("output size of LSTM: 5",  "MVA_TTTT_btag3p_b-20000_e-500_hs1-96_hs2-53_lstm-4_hs-lstm-5.root", ROOT.kOrange+8),
("output size of LSTM: 10", "MVA_TTTT_btag3p_b-20000_e-500_hs1-96_hs2-53_lstm-4_hs-lstm-10.root",ROOT.kOrange+3),
("output size of LSTM: 15", "MVA_TTTT_btag3p_b-20000_e-500_hs1-96_hs2-53_lstm-4_hs-lstm-15.root",ROOT.kOrange+2),
("output size of LSTM: 25", "MVA_TTTT_btag3p_b-20000_e-500_hs1-96_hs2-53_lstm-4_hs-lstm-25.root", ROOT.kOrange+1),
]

data_hs_lstm_db_2p = [
("output size of LSTM: 5,  doubleB",  "MVA_TTTT_btag2p_b-20000_e-500_hs1-96_hs2-53_lstm-4_hs-lstm-5_DoubleB.root",ROOT.kPink-7),
#("output size of LSTM: 10, doubleB",  "MVA_TTTT_btag2p_b-20000_e-500_hs1-96_hs2-53_lstm-4_hs-lstm-10_DoubleB.root",ROOT.kPink-6),
("output size of LSTM: 15, doubleB",  "MVA_TTTT_btag2p_b-20000_e-500_hs1-96_hs2-53_lstm-4_hs-lstm-15_DoubleB.root", ROOT.kPink-5),
("output size of LSTM: 25, doubleB",  "MVA_TTTT_btag2p_b-20000_e-500_hs1-96_hs2-53_lstm-4_hs-lstm-25_DoubleB.root", ROOT.kPink-2),
]  
data_hs_lstm_db_3p = [
("output size of LSTM: 5,  doubleB",  "MVA_TTTT_btag3p_b-20000_e-500_hs1-96_hs2-53_lstm-4_hs-lstm-5_DoubleB.root",ROOT.kPink-7),
#("output size of LSTM: 10, doubleB", "MVA_TTTT_btag3p_b-20000_e-500_hs1-96_hs2-53_lstm-4_hs-lstm-10_DoubleB.root",ROOT.kPink-6),
("output size of LSTM: 15, doubleB",  "MVA_TTTT_btag3p_b-20000_e-500_hs1-96_hs2-53_lstm-4_hs-lstm-15_DoubleB.root", ROOT.kPink-5),
("output size of LSTM: 25, doubleB",  "MVA_TTTT_btag3p_b-20000_e-500_hs1-96_hs2-53_lstm-4_hs-lstm-25_DoubleB.root", ROOT.kPink-2),
]                                                               

data_epoch_2p = [
("epochs: 500",   "MVA_TTTT_btag2p_b-20000_e-500_hs1-96_hs2-53_lstm-4_hs-lstm-25.root",ROOT.kPink-7),
("epochs: 750",   "MVA_TTTT_btag2p_b-20000_e-750_hs1-96_hs2-53_lstm-4_hs-lstm-25.root",ROOT.kPink-2),
]
data_epoch_3p = [
("epochs: 500",   "MVA_TTTT_btag3p_b-20000_e-500_hs1-96_hs2-53_lstm-4_hs-lstm-25.root",ROOT.kPink-7),
("epochs: 750",   "MVA_TTTT_btag3p_b-20000_e-750_hs1-96_hs2-53_lstm-4_hs-lstm-25.root",ROOT.kPink-2),
]

data_epoch_db_2p = [
("epochs: 500, doubleB",   "MVA_TTTT_btag2p_b-20000_e-500_hs1-96_hs2-53_lstm-4_hs-lstm-25_DoubleB.root",ROOT.kPink-7),
("epochs: 750, doubleB",   "MVA_TTTT_btag2p_b-20000_e-750_hs1-96_hs2-53_lstm-4_hs-lstm-25_DoubleB.root",ROOT.kPink-2),
]
data_epoch_db_3p = [
("epochs: 500, doubleB",   "MVA_TTTT_btag3p_b-20000_e-500_hs1-96_hs2-53_lstm-4_hs-lstm-25_DoubleB.root",ROOT.kPink-7),
("epochs: 750, doubleB",   "MVA_TTTT_btag3p_b-20000_e-750_hs1-96_hs2-53_lstm-4_hs-lstm-25_DoubleB.root",ROOT.kPink-2),
]

data_compare_2p = [
("2l MVA ",                 "MVA_TTTT_btag2p_b-20000_e-500_hs1-96_hs2-53.root",ROOT.kRed),
("2l MVA + LSTM",           "MVA_TTTT_btag2p_b-20000_e-750_hs1-96_hs2-53_lstm-4_hs-lstm-25.root",ROOT.kBlue),
("2l MVA + LSTM, doubleB",  "MVA_TTTT_btag2p_b-20000_e-750_hs1-96_hs2-53_lstm-4_hs-lstm-25_DoubleB.root",ROOT.kGreen),
]
data_compare_3p = [
("2l MVA ",                 "MVA_TTTT_btag3p_b-20000_e-500_hs1-96_hs2-53.root",ROOT.kRed),
("2l MVA + LSTM",           "MVA_TTTT_btag3p_b-20000_e-750_hs1-96_hs2-53_lstm-4_hs-lstm-25.root",ROOT.kBlue),
("2l MVA + LSTM, doubleB",  "MVA_TTTT_btag3p_b-20000_e-750_hs1-96_hs2-53_lstm-4_hs-lstm-25_DoubleB.root",ROOT.kGreen),
]


data_root = [
(data_batch_2p, "Variation of batch size", "roc_batch_2p"),
(data_h1_2p, "Variation of 1st layer hidden size", "roc_h1_2p"),
(data_h2_2p, "Variation of 2nd layer hidden size", "roc_h2_2p"),
(data_lstm_2p, "Variation of number of LSTM layers", "roc_lstm_layers_2p"),
(data_db_2p, "Variation of number of LSTM layers (+DoubleB)", "roc_lstm+db_2p"),
(data_hs_lstm_2p, "Variation of LSTM output size", "roc_lstm_hs_2p"),
(data_hs_lstm_db_2p, "Variation of number of LSTM output size (+DoubleB)", "roc_lstm_hs+db_2p"),
(data_epoch_2p, "Variation of training epochs", "roc_epoch_2p"),
(data_epoch_db_2p, "Variation of training epochs (+DoubleB)", "roc_epoch+db_2p"),
(data_compare_2p, "Comparison of MVAs (w/o LSTM, w/o DoubleB)", "roc_comp_2p"),
(data_batch_3p, "Variation of batch size", "roc_batch_3p"),
(data_h1_3p, "Variation of 1st layer hidden size", "roc_h1_3p"),
(data_h2_3p, "Variation of 2nd layer hidden size", "roc_h2_3p"),
(data_lstm_3p, "Variation of number of LSTM layers", "roc_lstm_layers_3p"),
(data_db_3p, "Variation of number of LSTM layers (+DoubleB)", "roc_lstm+db_3p"),
(data_hs_lstm_3p, "Variation of LSTM output size", "roc_lstm_hs_3p"),
(data_hs_lstm_db_3p, "Variation of number of LSTM output size (+DoubleB)", "roc_lstm_hs+db_3p"),
(data_epoch_3p, "Variation of training epochs", "roc_epoch_3p"),
(data_epoch_db_3p, "Variation of training epochs (+DoubleB)", "roc_epoch+db_3p"),
(data_compare_3p, "Comparison of MVAs (w/o LSTM, w/o DoubleB)", "roc_comp_3p"),
]
