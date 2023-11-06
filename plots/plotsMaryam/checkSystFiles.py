import os
from tttt.Tools.user    import plot_directory

import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--plot_directory', action='store', default='4t-v11-syst')
argParser.add_argument('--selection',      action='store', default='trg-dilep-OS-minDLmass20-offZ1-lepVeto2-njet4to5-btag3p-ht500')
args = argParser.parse_args()

directory = os.path.join(plot_directory, 'analysisPlots', args.plot_directory, 'RunII', "all", args.selection)

# Possible Syst variations
variations = ['LeptonSFUp', 
              'LeptonSFDown',
	      'PUUp',
	      'PUDown',
              'L1PrefireUp',
	      'L1PrefireDown',
	      #'TriggerUp',
              #'TriggerDown',
              'BTagSFJesUp',
	      'BTagSFJesDown',
	      'BTagSFHfUp',
              'BTagSFHfDown',
              'BTagSFLfUp',
	      'BTagSFLfDown',
              'BTagSFHfs1Up',
	      'BTagSFHfs1Down',
	      'BTagSFLfs1Up',
              'BTagSFLfs1Down',
              'BTagSFHfs2Up',
	      'BTagSFHfs2Down',
              'BTagSFLfs2Up',
	      'BTagSFLfs2Down',
              'BTagSFCfe1Up',
	      'BTagSFCfe1Down',
              'BTagSFCfe2Up',
	      'BTagSFCfe2Down',
              'jesTotalUp',
	      'jesTotalDown',
	      'noTopPtReweight',
	      'HDampUp',
	      'HDampDown',
	      'central'
              ]
nPDFs = 101
PDFWeights = ["PDF_%s"%i for i in range(1,nPDFs)]
scaleWeights = ["ScaleDownDown","ScaleUpUp"]#, "ScaleDownNone", "ScaleNoneDown", "ScaleNoneUp", "ScaleUpNone"
PSWeights = ["ISRUp", "ISRDown", "FSRUp", "FSRDown"]

variations +=  scaleWeights + PSWeights + PDFWeights

# Output .sh file to store the commands
output_sh_file = 'missingSyst.sh'

all_files_exist = True

# Open the .sh file for writing
with open(output_sh_file, 'w') as sh_script:
    # Loop through each root file name
    for root_file in variations:
        file_path = os.path.join(directory, "tttt_"+root_file+".root")
        
        # Check if the file exists
        if not os.path.exists(file_path):
            # If the file doesn't exist, write a command to produce it
	    print file_path, "does not exist" 
	    all_files_exist = False
            # Here, you can customize the command as per your needs
            #command = 'python systematics.py --plot_directory %s --selection --sys %s\n'%args.plot_directory %args.selection %root_file
	    command = 'python systematics.py --plot_directory {} --selection {} --sys {}\n'.format(args.plot_directory, args.selection, root_file)
            sh_script.write(command)
            #print("Command to produce {root_file} has been written to {output_sh_file}")
        #else:
            #print root_file, "already exists in the directory"
if all_files_exist: print "Everything OK here :%s" %args.selection 
# Make the .sh script executable (optional)
os.chmod(output_sh_file, 0o755)

