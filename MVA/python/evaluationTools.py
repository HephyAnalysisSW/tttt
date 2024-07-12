'''Functions for misID'''
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
scalerR = RobustScaler()

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


def create_dataframes(file_pattern, branch_names, nFiles):
    '''
    Takes the file_pattern and creates a list of dataFrames where each entry is an events
    A bit convoluted but it is fast
    '''
    trees = []
    files = []
    for i in range(int(nFiles)):
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
    '''
    Takes the list of dataframes and predicts the scores with pretrained model
    '''
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


def filter_candidates(frame, thresholds, fpr_level):
    '''
    Takes dataframe, thresholds from the pkl file and the fpr value and applies the selection to the dataframes
    zB: datafraMes_10 = filter(lambda frame: not filter_candidates(frame, thresholds, 10).empty, frames_scored)
    '''
    scores = frame['scores'].tolist()
    sorted_scores = sorted(scores, reverse=True)
    threshold = thresholds["fpr {}".format(fpr_level)]
    selected_indices = [i for i, score in enumerate(frame['scores'].tolist()) if score > threshold]

    selected_frame = frame.iloc[selected_indices]
    return selected_frame


def count_and_save(dataframeList, filename):
    '''
    Counts the binary truth cases for all the events
    Also saves the first 5 events with FF to a csv
    '''
    TT, FF, FT, TF, noSub = 0, 0, 0, 0, 0
    false_false_frames = []

    for frame in dataframeList:
        max_score_index = frame['scores'].idxmax()
        remaining_scores = frame.drop(max_score_index)

        if not remaining_scores.empty:
            subleading_index = remaining_scores['scores'].idxmax()
            leading_truth = frame.at[max_score_index, 'HadronicTop_TopTruth']
            subleading_truth = frame.at[subleading_index, 'HadronicTop_TopTruth']

            if leading_truth == 1 and subleading_truth == 1:  # 2 true
                TT_count += 1
            elif leading_truth == 0 and subleading_truth == 0:  # 2 false
                FF += 1
                false_false_frames.append(frame)
            elif leading_truth == 0 and subleading_truth == 1:  # l false s true
                FT += 1
            elif leading_truth == 1 and subleading_truth == 0:  # l true s false
                TF += 1
        else:
            noSub += 1  # only leading score

        if len(false_false_frames) >= 5:
            break

    if false_false_frames:
        with open(filename, 'w') as f:
            for i, df in enumerate(false_false_frames[:5]):
                df.to_csv(f, index=False)
                # Add a line separator after each frame except the last one
                if i < len(false_false_frames) - 1:
                    f.write('\n' + '-'*50 + '\n')

    return TT, FF, FT, TF, noSub

# def print_indices(frame, index):
#     print("index0 {} | index1 {} | index2 {} | score {}".format(frame.loc[index, 'HadronicTop_index0'], frame.loc[index, 'HadronicTop_index1'], frame.loc[index, 'HadronicTop_index2'], frame.loc[index, 'scores']))

def get_highest_row(df, column):
    idx = df[column].idxmax()
    return df.loc[idx], idx

def get_indices(row):
    return {row['HadronicTop_index0'], row['HadronicTop_index1'], row['HadronicTop_index2']}



def get_leading_and_subleading(dataframes):
    '''
    Returns: - dataframe of the leading
             - dataframe of subleading scores
             - dictionary of only scores (good for plotting)
             - top right selection of 2D plot events
             - bottom right selection of 2D plot events
    '''
    highest_score_rows, subleading_score_rows = [], []
    scores_dict = {"leading": [], "subleading": []}
    high_scoring_rows, good_events = [], []
    for frame in dataframes:
        if frame.empty:
            continue
        highest_score_row, max_score_index = get_highest_row(frame, 'scores')
        highest_score_rows.append(highest_score_row)
        scores_dict["leading"].append(highest_score_row['scores'])
        highest_indices = get_indices(highest_score_row)

        remaining_frame = frame.drop(max_score_index)
        subleading_score_row = None
        while not remaining_frame.empty:
            second_highest_score_row, second_max_score_index = get_highest_row(remaining_frame, 'scores')
            second_highest_indices = get_indices(second_highest_score_row)
            if highest_indices.isdisjoint(second_highest_indices):
                subleading_score_row = second_highest_score_row
                subleading_score_rows.append(subleading_score_row)
                scores_dict["subleading"].append(subleading_score_row['scores'])
                # append critical zones from 2D plot
                if highest_score_row['scores'] > 0.95:
                    if subleading_score_row['scores'] > 0.8:
                        high_scoring_rows.append((highest_score_row, subleading_score_row))
                    if subleading_score_row['scores'] < 0.2:
                        good_events.append((highest_score_row, subleading_score_row))
                break
            else:
                remaining_frame = remaining_frame.drop(second_max_score_index)

        if subleading_score_row is None:
            scores_dict["subleading"].append(None)
    # cast all to dataframes
    highest_score_df = pd.DataFrame(highest_score_rows)
    good_events_df = pd.DataFrame(good_events, columns=['leading_row', 'subleading_row'])
    subleading_score_df = pd.DataFrame(subleading_score_rows)
    high_scoring_df = pd.DataFrame(high_scoring_rows, columns=['leading_row', 'subleading_row'])


    return highest_score_df, subleading_score_df, scores_dict, high_scoring_df, good_events_df



def classify_indices(indices):
    if indices[0] == indices[1] == indices[2]:
        return 'true'
    elif (indices[0] == indices[2] and indices[0] != indices[1]) or (indices[0] == indices[1] and indices[0] != indices[2]):
        return 'bt1jf'
    elif indices[1] == indices[2] and indices[0] != indices[1]:
        return 'bf2jt'
    elif indices[0] != indices[1] and indices[0] != indices[2] and indices[1] != indices[2]:
        return 'false'


def countMultiTruth(high_scoring_df, prefix="HadronicTop_"):
    results = []

    leading_counts = {'true': 0, 'bt1jf': 0, 'bf2jt': 0, 'false': 0}
    subleading_counts = {'true': 0, 'bt1jf': 0, 'bf2jt': 0, 'false': 0}
    combination_counts = defaultdict(int)

    for idx, row in high_scoring_df.iterrows():
        leading_row = row['leading_row']
        subleading_row = row['subleading_row']

        leading_indices = [leading_row[prefix + 'genMotherIdx0'], leading_row[prefix + 'genMotherIdx1'], leading_row[prefix + 'genMotherIdx2']]
        subleading_indices = [ subleading_row[prefix + 'genMotherIdx0'], subleading_row[prefix + 'genMotherIdx1'], subleading_row[prefix + 'genMotherIdx2']]

        leading_classification = classify_indices(leading_indices)
        subleading_classification = classify_indices(subleading_indices)
        results.append((leading_classification, subleading_classification))
        leading_counts[leading_classification] += 1
        subleading_counts[subleading_classification] += 1
        combination_counts[(leading_classification, subleading_classification)] += 1

    return results, leading_counts, subleading_counts, combination_counts
