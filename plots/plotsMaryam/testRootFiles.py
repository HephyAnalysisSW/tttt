
import tttt.samples.nano_data_private_UL20_Run2017_postProcessed_dilep as samples 
from Analysis.Tools.helpers import deepCheckRootFile, checkRootFile

for file in samples.Run2017.files:
    if not deepCheckRootFile(file):
        print "PROBLEM in ", file
        break
    else:
        print "OK"
