import os
import uproot
import numpy as np

directory_ = "/scratch-cbe/users/cristina.giordano/tttt/nanoTuples/tttt_v11/UL2017/dilep/TTTT_MS_EFT/"
# change the range!!!
file_paths = [os.path.join(directory_, "TTTT_MS_EFT_{}.root".format(i)) for i in range(20)]

all_variable_arrays = []

variable_names = ['pt', 'eta', 'phi', 'mass', 'genMass',
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


filename = "dataFrame20.csv" #change the name when adding files
np.savetxt(filename, combined_table, delimiter=',', fmt='%s', header=','.join(combined_table.dtype.names), comments='')
print("Saved to dataFrame named", filename)
