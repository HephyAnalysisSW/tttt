import os
import uproot
import numpy as np
import Analysis.Tools.syncer as syncer

import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--selection', action='store', default='dilep')
argParser.add_argument('--sample', action='store', default='TTTT_MS_EFT')
argParser.add_argument('--version', action='store', default='tttt_v12')
argParser.add_argument('--era', action='store', default='UL2017')
args = argParser.parse_args()

directory_ = os.path.join("/scratch-cbe/users/cristina.giordano/tttt/nanoTuples", args.era, args.selection, args.sample)

file_paths = [os.path.join(directory_, args.sample+"_{}.root".format(i)) for i in range(2)]

all_variable_arrays = []

variable_names = ['pt', 'eta', 'phi', 'mass', #'genMass',
                 'bJetCMPt', 'LdgJetCMPt', 'SubldgJetCMPt', 'softDrop_n2',
                 'bJetMass', 'diJetMass', 'LdgJetMass', 'SubldgJetMass',
                 'bJetLdgJetMass', 'bJetSubldgJetMass', 'bJetQGL',
                 'LdgJetQGL', 'SubldgJetQGL', 'DEtaDijetwithBJet', 'diJetPtOverSumPt',
                 'LdgJetDeltaPtOverSumPt', 'SubldgJetDeltaPtOverSumPt',
                 'bJetDeltaPtOverSumPt', 'cosW_Jet1Jet2', 'cosW_Jet1BJet',
                 'cosW_Jet2BJet', 'bJetBdisc', 'LdgJetBdisc', 'SubldgJetBdisc',
                 'bJetCvsL', 'LdgJetCvsL', 'SubldgJetCvsL', 'bJetCvsB',
                 'LdgJetCvsB', #'SubldgJetCvsB', <-- TODO
                 'trijetPtDR', 'dijetPtDR',
                 'TopTruth']

prefix = "HadronicTop_"

for file_path in file_paths:
    try:
        print("Processing file:", file_path)
        tree = uproot.open(file_path)
        ev = tree["Events"]

        variable_arrays = {}

        for var_name in variable_names:
            print("At variable:", var_name)
            variable_array = ev[prefix + var_name].array().flatten()
            variable_arrays[var_name] = variable_array

        all_variable_arrays.append(variable_arrays)

    except IOError as e:
        if "No such file" in str(e):
            print("File {} not found. Skip!".format(file_path))

dtype = [(var_name, float) for var_name in variable_names]
table_list = []
for variable_arrays in all_variable_arrays:
    table = np.zeros((len(variable_arrays[next(iter(variable_arrays))]),), dtype=dtype)
    for var_name, var_array in variable_arrays.items():
        table[var_name] = var_array
    table_list.append(table)

combined_table = np.concatenate(table_list)

filename = os.path.join("/eos/vbc/group/cms/cristina.giordano/tttt", "dataFrame_"+args.sample+"_"+args.selection+".csv")
np.savetxt(filename, combined_table, delimiter=',', fmt='%s', header=','.join(combined_table.dtype.names), comments='')
print("Saved to dataFrame named", filename)
