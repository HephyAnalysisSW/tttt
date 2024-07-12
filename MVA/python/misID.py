import uproot
import ROOT
import pandas as pd
import numpy as np
import os
from keras.models import load_model
from sklearn.model_selection import train_test_split
import pickle as pkl
from sklearn.preprocessing import RobustScaler
import matplotlib.pyplot as plt
from collections import defaultdict
from evaluationTools import *
import matplotlib.colors as mcolors


scalerR = RobustScaler()

pickle_file = "./tresholds_DNN_training2024.pkl"
with open(pickle_file, "rb") as f:
    thresholds = pkl.load(f)

# print("Thresholds for different FPR levels:")
# print("FPR 10%:", thresholds['fpr 10'])
# print("FPR 5%:", thresholds['fpr 5'])
# print("FPR 1%:", thresholds['fpr 1'])
# print("FPR 0.1%:", thresholds['fpr 01'])


import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--plot_directory',     action='store',      default='')
argParser.add_argument('--plotPath', action='store', nargs='?', default="/groups/hephy/cms/cristina.giordano/www/TruthStudies/plots/v12/UL2017", help="where to write the plots" )
argParser.add_argument('--selection', action='store', default='trilep')
argParser.add_argument('--sample', action='store', default='TTTT_MS_EFT')
argParser.add_argument('--nFiles', action='store', default='2')
argParser.add_argument('--plot', action='store', default='2D')
args = argParser.parse_args()

if args.selection == "trilep":
    myModel = load_model('./classifierModel_trilep_v3.h5')
else:
    myModel = load_model('./classifierModel_v3.h5')

file_pattern = "/scratch-cbe/users/cristina.giordano/tttt/nanoTuples/tttt_v12/UL2017/"+args.selection+"/"+args.sample+"/"+args.sample+"_*.root"


nFiles= args.nFiles

final_dataframes = create_dataframes(file_pattern, branch_names, nFiles)
# Add scores as a column
frames_scored = predict_scores(final_dataframes, scalerR, myModel)

print("Number of events: {}".format(len(frames_scored)))
highest, subleading, scores_dict, highestScores, goodEvents = get_leading_and_subleading(frames_scored)
print("Number of good events (s>0.8 ; l>0.95): {}".format(len(highestScores)))
print("Number of wrong events (s<0.2 ; l>0.95): {}".format(len(goodEvents)))
# change it by hand while switching between selections? Not ideal
results, leading_counts, subleading_counts, combos = countMultiTruth(highestScores, "HadronicTop_")
resultsGood, l_good, sub_good, combos_good = countMultiTruth(goodEvents)

#Plotting functions
def plot_subleading_vs_leading(scores_dict):
    filtered_leading_scores = []
    filtered_subleading_scores = []

    for leading, subleading in zip(scores_dict["leading"], scores_dict["subleading"]):
        if subleading is not None:
            filtered_leading_scores.append(leading)
            filtered_subleading_scores.append(subleading)

    plt.hist2d(filtered_leading_scores, filtered_subleading_scores, bins=(50, 50), cmap=plt.cm.jet, norm=mcolors.LogNorm())
    plt.colorbar(label='Counts')

    plt.xlabel("Leading Scores")
    plt.ylabel("Subleading Scores")
    plt.title("Subleading Scores vs Leading Scores")
    plt.savefig("SubLeadingVsLeading_"+args.selection+".eps", format='eps')
    print("Saved with name : SubLeadingVsLeading_"+args.selection+".eps")

def plot_variables_histograms(cats_dict, variable, name):
    plt.figure(figsize=(10, 6))
    for classification, values in cats_dict.items():
        plt.hist(values, bins=100, histtype='step', linewidth=2, label=classification)

    plt.ylabel('Number of Entries')
    plt.title('Histograms of Masses for Different Classifications')
    plt.legend()
    plt.grid(True)
    # plt.show()
    plt.savefig(name+"_"+variable+"_"+args.selection+".png")
    print("Saved with name : "+name+"_"+variable+"_"+args.selection+".png")

def extract_values(highest, variable, prefix="HadronicTop_"):
    cats = {'true': [], 'bt1jf': [], 'bf2jt': [], 'false': []}

    for idx, row in highest.iterrows():
        indices = [row[prefix + 'genMotherIdx0'], row[prefix + 'genMotherIdx1'], row[prefix + 'genMotherIdx2']]
        classification = classify_indices(indices)
        cat = row[prefix + variable]
        cats[classification].append(cat)

    return cats


if args.plot == "2D":
    plot_subleading_vs_leading(scores_dict)

# Call the function

if args.plot == "1D_multi":
    highest_mass_class = extract_values(highest, 'mass')
    subleading_mass_class = extract_values(subleading, 'mass')
    highest_W_class = extract_values(highest, 'diJetMass')
    subleading_W_class = extract_values(subleading, 'diJetMass')
    plot_variables_histograms(highest_mass_class, 'mass', "Leading")
    plot_variables_histograms(subleading_mass_class, 'mass', "Subleading")
    plot_variables_histograms(highest_mass_class, 'diJetMass', "Leading")
    plot_variables_histograms(subleading_mass_class, 'diJetMass', "Subleading")

if args.plot == "1D":
    leading_HadronicTop_mass = highest['HadronicTop_mass']
    leading_HadronicTop_diJetMass = highest['HadronicTop_diJetMass']
    subleading_HadronicTop_mass = subleading['HadronicTop_mass']
    subleading_HadronicTop_diJetMass = subleading['HadronicTop_diJetMass']

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.hist(leading_HadronicTop_mass, bins=100, range=(0, 1000), color='green', alpha=0.7, label='Leading')
    ax.hist(subleading_HadronicTop_mass, bins=100, range=(0, 1000), color='orange', alpha=0.7, label='Subleading')
    ax.set_xlabel('$m_{\mathrm{Top}}$', fontsize=14)
    ax.set_ylabel('Frequency', fontsize=14)
    ax.set_title('', fontsize=16)
    ax.legend()
    plt.grid(True)
    plt.savefig("topMass_comparison_"+args.selection+".png")
    print("Saved with name: topMass_comparison_"+args.selection+".png")
    plt.clf()

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.hist(leading_HadronicTop_diJetMass, bins=100, range=(0, 500), color='green', alpha=0.7, label='Leading')
    ax.hist(subleading_HadronicTop_diJetMass, bins=100, range=(0, 500), color='orange', alpha=0.7, label='Subleading')
    ax.set_xlabel('$m_{\mathrm{W}}$', fontsize=14)
    ax.set_ylabel('Frequency', fontsize=14)
    ax.set_title('', fontsize=16)
    ax.legend()
    plt.grid(True)
    plt.savefig("wMass_comparison_"+args.selection+".png")
    print("Saved with name: wMass_comparison_"+args.selection+".png")
    plt.clf()


# Tables
# for i, (leading_classification, subleading_classification) in enumerate(results):
#     print("Pair {}: Leading = {}, Subleading = {}".format(i+1, leading_classification, subleading_classification))

# for combination, count in combos.items():
#     print("Leading = {}, Subleading = {}: {}".format(combination[0], combination[1], count))

# print("\nTotal counts:")
# print("Leading:")
# print("True: ", leading_counts['true'])
# print("bt1jf: ", leading_counts['bt1jf'])
# print("bf2jt: ", leading_counts['bf2jt'])
# print("False: ", leading_counts['false'])
#
# print("Subleading:")
# print("True: ", subleading_counts['true'])
# print("bt1jf: ", subleading_counts['bt1jf'])
# print("bf2jt: ", subleading_counts['bf2jt'])
# print("False: ", subleading_counts['false'])

# categories = ['true', 'bt1jf', 'bf2jt', 'false']
# data = [[combos[(lead, sub)] for lead in categories] for sub in categories]
# data_array = np.array(data)
# norm = plt.Normalize(data_array.min(), data_array.max())
# colors = plt.cm.viridis(norm(data_array))

# fig, ax = plt.subplots()
# ax.axis('tight')
# ax.axis('off')
# ax.set_title('Subleading(>0.8) vs Leading(>0.95)')
# ax.set_xlabel('Leading')
# ax.set_ylabel('Subleading')
# table = ax.table(cellText=data, rowLabels=categories, colLabels=categories, cellLoc='center', loc='center')
#
# for i in range(len(categories)):
#     for j in range(len(categories)):
#         cell = table[i+1, j]
#         cell.set_facecolor(colors[i, j])
#
#
# plt.savefig('counts_goodEvents_dilep.png')
# plt.clf()
#
# data_good = [[combos_good[(lead, sub)] for lead in categories] for sub in categories]
# data_array_good = np.array(data_good)
# norm = plt.Normalize(data_array_good.min(), data_array.max())
# colors = plt.cm.viridis(norm(data_array_good))
# fig, ax = plt.subplots()
# ax.axis('tight')
# ax.axis('off')
# ax.set_title('Subleading(<0.2) vs Leading(>0.95)')
# ax.set_xlabel('Leading')
# ax.set_ylabel('Subleading')
# table = ax.table(cellText=data, rowLabels=categories, colLabels=categories, cellLoc='center', loc='center')
#
# for i in range(len(categories)):
#     for j in range(len(categories)):
#         cell = table[i+1, j]
#         cell.set_facecolor(colors[i, j])
#
# plt.savefig('counts_tail_dilep.png')

print("Done.")
