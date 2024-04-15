import os
import ROOT

# Define the directory containing the ROOT files
root_directory = "/eos/vbc/group/cms/robert.schoefbeck/tttt/nanoAOD/TTTT_MS_EFT-22-05-12/"

# Create a TChain to concatenate the TTrees from multiple ROOT files
chain = ROOT.TChain("Events")

# Add all ROOT files in the directory to the TChain
for root_file in os.listdir(root_directory):
    if root_file.endswith(".root"):
      if not root_file=="NANOAODSIMoutput_1041.root":
        file_path = os.path.join(root_directory, root_file)
        chain.Add(file_path)

# Define the variable name you want to compare ("event" in this case)
variable_name = "event"

# Define the list of target values
target_values = [1882425, 2393412]  # Add your desired target values to this list

# Loop over entries in the TChain and check each target value
for target_value in target_values:
    for entry in chain:
        if entry.GetBranchStatus(variable_name) == 1:
            value = entry.GetLeaf(variable_name).GetValue()
            if value == target_value:
                print "Match found in file: "+chain.GetCurrentFile().GetName()+" for target value: {}".format(target_value)

# Cleanup ROOT resources
chain.Reset()
ROOT.gROOT.GetListOfFiles().Clear()

