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


scalerR = RobustScaler()

myModel = load_model('./classifierModel_trilep_v3.h5')

pickle_file = "./tresholds_DNN_training2024.pkl"
with open(pickle_file, "rb") as f:
    thresholds = pkl.load(f)

def filter_candidates(frame, thresholds, fpr_level):
    scores = frame['scores'].tolist()
    sorted_scores = sorted(scores, reverse=True)
    threshold = thresholds["fpr {}".format(fpr_level)]
    selected_indices = [i for i, score in enumerate(frame['scores'].tolist()) if score > threshold]

    selected_frame = frame.iloc[selected_indices]
    return selected_frame

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
args = argParser.parse_args()

file_pattern = "/scratch-cbe/users/cristina.giordano/tttt/nanoTuples/tttt_v12/UL2017/"+args.selection+"/"+args.sample+"/"+args.sample+"_*.root"


branch_names = ['HadronicTop_pt', 'HadronicTop_eta', 'HadronicTop_phi', 'HadronicTop_mass',
                'HadronicTop_bJetCMPt', 'HadronicTop_LdgJetCMPt', 'HadronicTop_SubldgJetCMPt', 'HadronicTop_softDrop_n2',
                'HadronicTop_bJetMass', 'HadronicTop_diJetMass', 'HadronicTop_LdgJetMass', 'HadronicTop_SubldgJetMass',
                'HadronicTop_bJetLdgJetMass', 'HadronicTop_bJetSubldgJetMass', 'HadronicTop_bJetQGL',
                'HadronicTop_LdgJetQGL', 'HadronicTop_SubldgJetQGL', 'HadronicTop_DEtaDijetwithBJet', 'HadronicTop_diJetPtOverSumPt',
                'HadronicTop_LdgJetDeltaPtOverSumPt', 'HadronicTop_SubldgJetDeltaPtOverSumPt',
                'HadronicTop_bJetDeltaPtOverSumPt', 'HadronicTop_cosW_Jet1Jet2', 'HadronicTop_cosW_Jet1BJet',
                'HadronicTop_cosW_Jet2BJet', 'HadronicTop_bJetBdisc', 'HadronicTop_LdgJetBdisc', 'HadronicTop_SubldgJetBdisc',
                'HadronicTop_bJetCvsL', 'HadronicTop_LdgJetCvsL', 'HadronicTop_SubldgJetCvsL', 'HadronicTop_bJetCvsB',
                'HadronicTop_LdgJetCvsB', 'HadronicTop_trijetPtDR', 'HadronicTop_dijetPtDR',
                'HadronicTop_TopTruth', 'HadronicTop_genMotherIdx0', 'HadronicTop_genMotherIdx1', 'HadronicTop_genMotherIdx2',
                'HadronicTop_index0', 'HadronicTop_index1', 'HadronicTop_index2']

jetVars = ['JetGood_pt', 'JetGood_eta', 'JetGood_phi', 'JetGood_genMotherIdx', 'JetGood_pdgId', 'JetGood_jetId', 'JetGood_isMatched']

# utils
def create_dataframes(file_pattern, branch_names):
    trees = []
    files = []
    for i in range(int(args.nFiles)):
        file_name = file_pattern.replace("*", str(i))
        print("Processing file {}".format(file_name))
        if not os.path.exists(file_name):
            print("Skipping file {} as it does not exist.".format(file_name))
            continue
        file = ROOT.TFile.Open(file_name)
        if not file or file.IsZombie():
            print("Skipping file {} as it cannot be opened or is corrupt.".format(file_name))
            continue
        tree = file.Get("Events")
        if not tree:
            print("Skipping file {} as 'Events' tree cannot be found.".format(file_name))
            file.close()
            continue
        trees.append(tree)
        files.append(file)

    dataframes = []
    for tree in trees:
        # print(tree)
        total_events = tree.GetEntries()
        dictionaries = []
        for j in range(total_events):
            # print(j)
            event_data = {}
            tree.GetEntry(j)
            for branch_name in branch_names:
                branch_values = getattr(tree, branch_name)
                branch_values = np.array(branch_values).tolist()
                event_data[branch_name] = branch_values
                event_data["event_index"] = j
            for jet in jetVars:
                jet_attr = getattr(tree, jet)
                hadronic_top_indices = [getattr(tree, "HadronicTop_index"+str(idx)) for idx in range(3)]
                jet_values = []
                for indices in hadronic_top_indices:
                    jet_values_tmp = []
                    for index in indices:
                        if 0 <= index < len(jet_attr):
                            jet_values_tmp.append(jet_attr[index])
                        else:
                            jet_values_tmp.append(None)
                    jet_values.append(jet_values_tmp)

                for i, vals in enumerate(jet_values):
                    event_data['{}[index{}]'.format(jet,i)] = vals
            dictionaries.append(event_data)

        for dictionary in dictionaries:
            df = pd.DataFrame.from_dict(dictionary)
            dataframes.append(df)
    final_dataframes = [df for df in dataframes if not df.empty]
    for file in files:
        file.Close()
    return final_dataframes



def predict_scores(final_dataframes, scaler, model):
    newFrames = []
    to_drop = []
    for var in jetVars:
        for idx in range(3):  # As there are three jets, index 0, 1, 2
            to_drop.append("{}[index{}]".format(var,idx))
    others_to_drop = ['event_index', 'HadronicTop_TopTruth', 'HadronicTop_genMotherIdx0',
                       'HadronicTop_genMotherIdx1', 'HadronicTop_genMotherIdx2',
                       'HadronicTop_index0', 'HadronicTop_index1', 'HadronicTop_index2']
    to_drop += others_to_drop
    for frame in final_dataframes:
        X = frame.drop(to_drop, axis=1)
        X_scaledR = scalerR.fit_transform(X)
        scores = model.predict(X_scaledR)
        frame['scores'] = scores
        newFrames.append(frame)
    return newFrames








final_dataframes = create_dataframes(file_pattern, branch_names)
frames_scored = predict_scores(final_dataframes, scalerR, myModel)
# print(len(final_dataframes))
# if final_dataframes:
#     final_dataframes[0].to_csv('first_dataframe.csv', sep='\t', index=False)

# print(len(frames_scored))


#
newFrames_10 = filter(lambda frame: not filter_candidates(frame, thresholds, 10).empty, frames_scored)
newFrames_5 = filter(lambda frame: not filter_candidates(frame, thresholds, 5).empty, frames_scored)
newFrames_1 = filter(lambda frame: not filter_candidates(frame, thresholds, 1).empty, frames_scored)
# print(len(newFrames_10), len(newFrames_5), len(newFrames_1))
# #
# def count_truth_combinations_old(dataframeList):
#     true_true_count, false_false_count, leading_false_subleading_true_count, leading_true_subleading_false_count, no_subleading_count = 0, 0, 0, 0, 0
#
#     for frame in dataframeList:
#
#         max_score_index = frame['scores'].idxmax()
#         remaining_scores = frame.drop(max_score_index)
#         if not remaining_scores.empty:
#             subleading_index = remaining_scores['scores'].idxmax()
#             leading_truth = frame.at[max_score_index, 'HadronicTop_TopTruth']
#             subleading_truth = frame.at[subleading_index, 'HadronicTop_TopTruth']
#             # Cases
#             if leading_truth == 1 and subleading_truth == 1: # 2 true
#                 true_true_count += 1
#             elif leading_truth == 0 and subleading_truth == 0: # 2 false
#                 false_false_count += 1
#             elif leading_truth == 0 and subleading_truth == 1: # l false s true
#                 leading_false_subleading_true_count += 1
#             elif leading_truth == 1 and subleading_truth == 0: # l true s false
#                 leading_true_subleading_false_count += 1
#         else:
#             no_subleading_count += 1 # only l
#
#     return true_true_count, false_false_count, leading_false_subleading_true_count, leading_true_subleading_false_count, no_subleading_count

# def count_and_save_false_false(dataframeList, filename):
#     true_true_count, false_false_count, leading_false_subleading_true_count, leading_true_subleading_false_count, no_subleading_count = 0, 0, 0, 0, 0
#     false_false_frames = []
#
#     for frame in dataframeList:
#         max_score_index = frame['scores'].idxmax()
#         remaining_scores = frame.drop(max_score_index)
#
#         if not remaining_scores.empty:
#             subleading_index = remaining_scores['scores'].idxmax()
#             leading_truth = frame.at[max_score_index, 'HadronicTop_TopTruth']
#             subleading_truth = frame.at[subleading_index, 'HadronicTop_TopTruth']
#
#             # Cases
#             if leading_truth == 1 and subleading_truth == 1:  # 2 true
#                 true_true_count += 1
#             elif leading_truth == 0 and subleading_truth == 0:  # 2 false
#                 false_false_count += 1
#                 # Save the frame where both leading and subleading scores are fake
#                 false_false_frames.append(frame)
#             elif leading_truth == 0 and subleading_truth == 1:  # l false s true
#                 leading_false_subleading_true_count += 1
#             elif leading_truth == 1 and subleading_truth == 0:  # l true s false
#                 leading_true_subleading_false_count += 1
#         else:
#             no_subleading_count += 1  # only leading score
#
#         # Check if we have already collected 5 false_false_frames
#         if len(false_false_frames) >= 5:
#             break
#
#     # Save the first 5
#     if false_false_frames:
#         with open(filename, 'w') as f:
#             for i, df in enumerate(false_false_frames[:5]):
#                 df.to_csv(f, index=False)
#                 # Add a line separator after each frame except the last one
#                 if i < len(false_false_frames) - 1:
#                     f.write('\n' + '-'*50 + '\n')
#
#     return true_true_count, false_false_count, leading_false_subleading_true_count, leading_true_subleading_false_count, no_subleading_count


# tt_count, ff_count, ft_count, tf_count, no_subleading_count = count_and_save_false_false(frames_scored, "frames.csv")
# tt_count_10, ff_count_10, ft_count_10, tf_count_10, no_subleading_count_10 = count_truth_combinations(newFrames_10)
# tt_count_5, ff_count_5, ft_count_5, tf_count_5, no_subleading_count_5 = count_truth_combinations(newFrames_5)
# tt_count_1, ff_count_1, ft_count_1, tf_count_1, no_subleading_count_1 = count_truth_combinations(newFrames_1)
#
# print("All events (no Threshold)")
# print("Number of times both leading and subleading are true:", tt_count)
# print("Number of times both leading and subleading are false:", ff_count)
# print("Number of times leading is false and subleading is true:", ft_count)
# print("Number of times leading is true and subleading is false:", tf_count)
# print("Number of times there is no subleading score:", no_subleading_count)
# print("10% threshold")
# print("Number of times both leading and subleading are true:", tt_count_10)
# print("Number of times both leading and subleading are false:", ff_count_10)
# print("Number of times leading is false and subleading is true:", ft_count_10)
# print("Number of times leading is true and subleading is false:", tf_count_10)
# print("Number of times there is no subleading score:", no_subleading_count_10)
# print("5% threshold")
# print("Number of times both leading and subleading are true:", tt_count_5)
# print("Number of times both leading and subleading are false:", ff_count_5)
# print("Number of times leading is false and subleading is true:", ft_count_5)
# print("Number of times leading is true and subleading is false:", tf_count_5)
# print("Number of times there is no subleading score:", no_subleading_count_5)
# print("1% threshold")
# print("Number of times both leading and subleading are true:", tt_count_1)
# print("Number of times both leading and subleading are false:", ff_count_1)
# print("Number of times leading is false and subleading is true:", ft_count_1)
# print("Number of times leading is true and subleading is false:", tf_count_1)
# print("Number of times there is no subleading score:", no_subleading_count_1)




# def get_subleading_veto(df, highest_row, column):
#     check = ['HadronicTop_bJetMass', 'HadronicTop_LdgJetMass', 'HadronicTop_SubldgJetMass']
#     remaining_df = df.drop(highest_row.name)
#     for index, row in remaining_df.iterrows():
#         if all(row[col] != highest_row[col] for col in check):
#             return row
#     return remaining_df.loc[remaining_df[column].nlargest(2).index[-1]]


# def get_subleading_veto(df, highest_row, column):
#     check_columns = ['HadronicTop_bJetMass', 'HadronicTop_LdgJetMass', 'HadronicTop_SubldgJetMass']
#     remaining_df = df.drop(highest_row.name)
#     for index, row in remaining_df.iterrows():
#         if not any(row[check_columns].eq(highest_row[check_columns]).all(axis=1)):
#             return row
#     return remaining_df.loc[remaining_df[column].nlargest(2).index[-1]]
#

def print_indices(frame, index):
    print("index0 {} | index1 {} | index2 {} | score {}".format(frame.loc[index, 'HadronicTop_index0'], frame.loc[index, 'HadronicTop_index1'], frame.loc[index, 'HadronicTop_index2'], frame.loc[index, 'scores']))


def get_highest_row(df, column):
    # maxIdx = df.loc[df[column].idxmax()]
    # maxIdxRow = df.loc[maxIdx]
    # return maxIdx, maxIdxRow
    return df.loc[df[column].idxmax()]

def get_highest_and_unique_subleading_score_rows(dataframes):
    highest_score_rows, subleading_score_rows = [], []
    scores_dict = {"leading": [], "subleading": []}
    for frame in dataframes:
        if not frame.empty:
            max_score_index = frame['scores'].idxmax()

            highest_score_row = frame.loc[max_score_index]
            highest_score_rows.append(highest_score_row)
            scores_dict["leading"].append(highest_score_row['scores'])

            highest_indices = {highest_score_row['HadronicTop_index0'], highest_score_row['HadronicTop_index1'], highest_score_row['HadronicTop_index2']}

            remaining_frame = frame.drop(max_score_index)
            subleading_score_row = None

            while not remaining_frame.empty:
                # second_max_score_index = get_highest_row(remaining_frame, 'scores')
                second_max_score_index = remaining_frame['scores'].idxmax()
                second_highest_score_row = remaining_frame.loc[second_max_score_index]
                second_highest_indices = {second_highest_score_row['HadronicTop_index0'], second_highest_score_row['HadronicTop_index1'], second_highest_score_row['HadronicTop_index2']}
                # logLevel.debug("Check")
                # logLevel.debug(print_indices(frame, second_max_score_index))
                if highest_indices.isdisjoint(second_highest_indices):
                    subleading_score_row = second_highest_score_row
                    subleading_score_rows.append(subleading_score_row)
                    # print("Subleading score row indices:")
                    # print_indices(frame, second_max_score_index)
                    scores_dict["subleading"].append(subleading_score_row['scores'])
                    break
                else:
                    remaining_frame = remaining_frame.drop(second_max_score_index)

            if subleading_score_row is None:
                scores_dict["subleading"].append(None)

    highest_score_df = pd.DataFrame(highest_score_rows)
    subleading_score_df = pd.DataFrame(subleading_score_rows)

    return highest_score_df, subleading_score_df, scores_dict

highest, subleading, scores_dict = get_highest_and_unique_subleading_score_rows(frames_scored)

import matplotlib.colors as mcolors

def plot_leading_vs_subleading(scores_dict):
    filtered_leading_scores = []
    filtered_subleading_scores = []

    for leading, subleading in zip(scores_dict["leading"], scores_dict["subleading"]):
        if subleading is not None:
            filtered_leading_scores.append(leading)
            filtered_subleading_scores.append(subleading)

    # Plot the data
    plt.hist2d(filtered_leading_scores, filtered_subleading_scores, bins=(50, 50), cmap=plt.cm.jet, norm=mcolors.LogNorm())
    plt.colorbar(label='Counts')

    # Add labels and title
    plt.xlabel("Leading Scores")
    plt.ylabel("Subleading Scores")
    plt.title("Subleading Scores vs Leading Scores")
    plt.savefig("SubLeadingVsLeading_"+args.selection+".eps", format='eps')


plotNew = plot_leading_vs_subleading(scores_dict)


# def plot_scores_distribution(frames, filename_prefix):
#     # print("Number of frames:", len(frames))
#     true_scores = {'leading': [], 'subleading': []}
#     false_scores = {'leading': [], 'subleading': []}
#     all_scores = {'leading': [], 'subleading': []}
#     leading_4 = {'leading': [], 'subleading': [], '3leading': [], '4leading': []}
#     vars = {'leading': {'mass': [], 'diJetMass': []},
#             'subleading': {'mass': [], 'diJetMass': []}}
#
#     for frame in frames:
#         print(frame[['scores', 'HadronicTop_bJetMass', 'HadronicTop_LdgJetMass', 'HadronicTop_SubldgJetMass']] )
#         # Find the index of the row with the highest score (leading score)
#         max_score_index = frame['scores'].idxmax()
#         # Get the truth value for the leading score
#         leading_truth = frame.at[max_score_index, 'HadronicTop_TopTruth']
#         # Get the leading score
#         leading_score = get_highest_row(frame, 'scores')
#         # leading_masses = frame.loc[max_score_index, ['HadronicTop_bJetMass', 'HadronicTop_LdgJetMass', 'HadronicTop_SubldgJetMass']]
#         subleading_score = get_subleading_veto(frame, leading_score, 'scores')
#         print(leading_score['scores'])
#         print(subleading_score['scores'])
#         # leading_score = frame.at[max_score_index, 'scores']
#         all_scores['leading'].append(leading_score)
#         leading_4['leading'].append(leading_score)
#
#         # Append the scores to the corresponding lists based on the truth value
#         if leading_truth == 1:
#             true_scores['leading'].append(leading_score)
#         else:
#             false_scores['leading'].append(leading_score)
#
#
#         # Get the mass variables for the leading jet
#         leading_masses = frame.loc[max_score_index, ['HadronicTop_bJetMass', 'HadronicTop_LdgJetMass', 'HadronicTop_SubldgJetMass']]
#         leading_vars = frame.loc[max_score_index, ['HadronicTop_mass', 'HadronicTop_diJetMass']]
#         # print(type(leading_vars))
#         vars['leading']['mass'].append(leading_vars[0])
#         vars['leading']['diJetMass'].append(leading_vars[1])
#         # Get the mass variables for the subleading jet
#         subleading_frame = frame.loc[frame.index != max_score_index]
#         if not subleading_frame.empty:
#             subleading_masses = subleading_frame[['HadronicTop_bJetMass', 'HadronicTop_LdgJetMass', 'HadronicTop_SubldgJetMass']]
#
#             if not subleading_masses.equals(leading_masses):
#                 subleading_score = subleading_frame['scores'].max()
#                 leading_4['subleading'].append(subleading_score)
#                 subleading_idx = subleading_frame['scores'].idxmax()
#                 subleading_vars = frame.loc[subleading_idx, ['HadronicTop_mass', 'HadronicTop_diJetMass']]
#                 vars['subleading']['mass'].append(subleading_vars[0])
#                 vars['subleading']['diJetMass'].append(subleading_vars[1])
#                 leading_frame3 = frame.loc[frame.index != subleading_idx]
#                 leading3masses = leading_frame3[['HadronicTop_bJetMass', 'HadronicTop_LdgJetMass', 'HadronicTop_SubldgJetMass']]
                # if not leading3masses.equals(subleading_masses):
                #     leading3score = leading_frame3['scores'].max()
                #     leading_4['3leading'].append(leading3score)
                #     leading_3idx = leading_frame3['scores'].idxmax()
                #     leading4frame = frame.loc[frame.index != leading_3idx]
                #     leading4masses = leading4frame[['HadronicTop_bJetMass', 'HadronicTop_LdgJetMass', 'HadronicTop_SubldgJetMass']]
                #     if not leading4masses.equals(leading3masses):
                #         leading4score = leading_frame3['scores'].max()
                #         leading_4['4leading'].append(leading3score)
                # print("here")
        #         all_scores['subleading'].append(subleading_score)
        #         # Append the subleading score to the corresponding list based on the truth value
        #         if leading_truth == 1:
        #             true_scores['subleading'].append(subleading_score)
        #         else:
        #             false_scores['subleading'].append(subleading_score)
        #
        # # print("Number of leading scores:", len(all_scores['leading']))
        # print("Number of subleading scores:", len(all_scores['subleading']))

    # Plot the distributions for leading scores
    # plt.figure(figsize=(8, 6))
    # plt.hist(all_scores['leading'], bins=30, alpha=0.5, color='green', label='All')
    # plt.hist(true_scores['leading'], bins=30, alpha=0.5, color='blue', linestyle='--', histtype='step', label='True')
    # plt.hist(false_scores['leading'], bins=30, alpha=0.5, color='red', linestyle='--', histtype='step', label='False')
    # plt.axvline(x=thresholds['fpr 10'], color='black', linestyle='--', label='Threshold fpr 10')
    # plt.xlabel('Leading Score')
    # plt.ylabel('Frequency')
    # plt.title('Distribution of Leading Scores')
    # plt.legend()
    # plt.grid(True)
    # plt.savefig(filename_prefix + '_leading_scores_'+args.selection+'.pdf')
    # plt.close()
    # print("Leading scores plot saved.")
    #
    # # Plot the distributions for subleading scores
    # if all_scores['subleading']:
    #     plt.figure(figsize=(8, 6))
    #     plt.hist(all_scores['subleading'], bins=30, alpha=0.5, color='green', label='All')
    #     plt.hist(true_scores['subleading'], bins=30, alpha=0.5, color='blue', linestyle='--', histtype='step', label='True')
    #     plt.hist(false_scores['subleading'], bins=30, alpha=0.5, color='red', linestyle='--', histtype='step', label='False')
    #     plt.axvline(x=thresholds['fpr 10'], color='black', linestyle='--', label='Threshold fpr 10')
    #     plt.xlabel('Subleading Score')
    #     plt.ylabel('Frequency')
    #     plt.title('Distribution of Subleading Scores')
    #     plt.legend()
    #     plt.grid(True)
    #     plt.savefig(filename_prefix + '_subleading_scores_'+args.selection+'.pdf')
    #     plt.close()
    #     print("Subleading scores plot saved.")
    # else:
    #     print("No subleading scores to plot.")
    #
    # lead_data = vars['leading']['mass']
    # sub_data = vars['subleading']['mass']
    #
    # # Compute and normalize the histograms
    # hist_l, bins_l = np.histogram(lead_data, bins=100, range=(0, 1000))
    # # hist_l = hist_l / hist_l.sum()
    # hist_s, bins_s = np.histogram(sub_data, bins=100, range=(0, 1000))
    # # hist_s = hist_s / hist_s.sum()
    #
    # # Plotting the leading mass histogram
    # plt.figure(figsize=(8, 6), dpi=100)
    # bin_centers_l = (bins_l[:-1] + bins_l[1:]) / 2
    # plt.bar(bin_centers_l, hist_l, width=(bins_l[1] - bins_l[0]), alpha=0.5, color='green', label='All')
    #
    # # Uncomment the following line if you need a logarithmic y-axis
    # # plt.yscale('log')
    #
    # # Add labels, title, grid, and legend
    # plt.xlabel('Mass (leading)')
    # plt.xlim(0, 1000)
    # # plt.ylabel('Normalized Events')
    # plt.legend()
    # plt.grid(True)
    #
    # # Save the figure
    # # replace with your actual prefix
    # plt.savefig(filename_prefix + "_massTop_leading_" + args.selection +  ".pdf")
    # plt.close()
    # print("Leading mass plot.")
    #
    # # Plotting the subleading mass histogram
    # plt.figure(figsize=(8, 6), dpi=100)
    # bin_centers_s = (bins_s[:-1] + bins_s[1:]) / 2
    # plt.bar(bin_centers_s, hist_s, width=(bins_s[1] - bins_s[0]), alpha=0.5, color='green', label='All')
    #
    # # Uncomment the following line if you need a logarithmic y-axis
    # # plt.yscale('log')
    #
    # # Add labels, title, grid, and legend
    # plt.xlabel('Mass (subleading)')
    # plt.xlim(0, 1000)
    # # plt.ylabel('Normalized Events')
    # plt.legend()
    # plt.grid(True)
    #
    # # Save the figure
    # plt.savefig(filename_prefix + "_massTop_subleading_" + args.selection + ".pdf")
    # plt.close()
    # print("Subleading mass plot.")
    #
    # plt.figure(figsize=(8, 6))
    #
    # # for score_type in ['leading', 'subleading', '3leading', '4leading']:
    # #     scores = leading_4[score_type
    # # print("1st Leading:", leading_4['leading'])
    # # print("2nd Leading:", leading_4['subleading'])
    # # print("3rd Leading:", leading_4['3leading'])
    # # print("4th Leading:", leading_4['4leading'])
    # plt.hist(leading_4['leading'], label="1st Leading", bins=100, linestyle='-')
    # plt.hist(leading_4['subleading'], label="2nd Leading", bins=100, linestyle='-')
    # plt.hist(leading_4['3leading'], label="3rd Leading", bins=100, linestyle='-')
    # plt.hist(leading_4['4leading'], label="4th Leading", bins=100,linestyle='-')
    # plt.xlabel('Event')
    # plt.xlim(0, 1000)
    # plt.ylabel('Score')
    # plt.title('Leading Scores')
    # plt.legend()
    # plt.grid(True)
    # plt.savefig(filename_prefix + '_leading_4_scores.pdf')
    # plt.close()
    # print("Leading scores plot saved.")
    #
    #
    # # lead_data = vars['leading']['mass']
    # # sub_data = vars['subleading']['mass']
    # # hist_l, bins_l = np.histogram(lead_data, bins=100, range=(0, 1000))
    # # hist_l = hist_l / hist_l.sum()
    # # hist_s, bins_s = np.histogram(sub_data, bins=100, range=(0, 1000))
    # # hist_s = hist_s / hist_s.sum()
    # #
    # #
    # # plt.figure(figsize=(8, 6), dpi=100)
    # # plt.hist(bins_l[:-1], bins_l, weights=hist_l, alpha=0.5, color='green', label='All')
    # # # plt.hist(vars['leading']['mass'], bins=100, alpha=0.5, color='green', label='All')
    # # # plt.hist(true_scores['leading'], bins=30, alpha=0.5, color='blue', linestyle='--', histtype='step', label='True')
    # # # plt.hist(false_scores['leading'], bins=30, alpha=0.5, color='red', linestyle='--', histtype='step', label='False')
    # # # plt.axvline(x=thresholds['fpr 10'], color='black', linestyle='--', label='Threshold fpr 10')
    # # plt.xlabel('Mass(leading)')
    # # plt.xlim(0, 1000)
    # # plt.ylabel('Events')
    # # # plt.title('Distribution of Leading Scores')
    # # plt.legend()
    # # plt.grid(True)
    # # plt.savefig(filename_prefix + '_massTop_leading_'+args.selection+'.pdf')
    # # plt.close()
    # # print("Leading mass plot.")
    # # ########
    # # plt.figure(figsize=(8, 6), dpi=100)
    # # plt.hist(bins_s[:-1], bins_s, weights=hist_s, alpha=0.5, color='green', label='All')
    # # # plt.hist(vars['subleading']['mass'], bins=100, alpha=0.5, color='green', label='All')
    # # # plt.hist(true_scores['leading'], bins=30, alpha=0.5, color='blue', linestyle='--', histtype='step', label='True')
    # # # plt.hist(false_scores['leading'], bins=30, alpha=0.5, color='red', linestyle='--', histtype='step', label='False')
    # # # plt.axvline(x=thresholds['fpr 10'], color='black', linestyle='--', label='Threshold fpr 10')
    # # plt.xlabel('Mass(subleading)')
    # # plt.xlim(0, 1000)
    # # plt.ylabel('Events')
    # # # plt.title('Distribution of Leading Scores')
    # # plt.legend()
    # # plt.grid(True)
    # # plt.savefig(filename_prefix + '_massTop_subleading_'+args.selection+'.pdf')
    # # plt.close()
    # # print("Subleading mass plot.")

# Usage example:
# plot_scores_distribution(frames_scored, 'plot')






# true_labels = []
# predicted_scores = []
# for frame in frames_scored:
#     true_labels.extend(frame['HadronicTop_TopTruth'].tolist())
#     predicted_scores.extend(frame['scores'].tolist())


# from sklearn.metrics import roc_curve, precision_recall_curve, auc
# precision, recall, thresholds_pr = precision_recall_curve(true_labels, predicted_scores)
# pr_auc = auc(recall, precision)
# plt.figure(figsize=(8, 6))
# plt.plot(recall, precision, color='green', label='Precision-Recall curve (AUC = {})'.format(pr_auc))
# plt.xlabel('Recall')
# plt.ylabel('Precision')
# plt.title('Precision-Recall (PR) Curve')
# plt.legend()
# plt.grid(True)
# plt.savefig('pr_curve.pdf')
# print('PR curve saved.')

print("Done.")
