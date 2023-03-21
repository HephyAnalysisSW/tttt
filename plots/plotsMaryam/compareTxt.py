
if __name__ == '__main__':
  File2 = "./EventTags_TTTT_TuneCP5_13TeV-amcatnlo-pythia8_RunIISummer20UL18MiniAODv2_singlelepton_MC_2018_UL.txt"
  File1 = "./Events5_2lSS.txt"

  with open(File1, 'r') as f1, open(File2, 'r') as f2:
    # read the contents of the files into variables
    contents2 = f2.read()

    # use the set difference method to find the lines that are unique to each file
    content_file1 = f1.readlines()
    unique_to_file1 = []

    #for i, event in enumerate(content_file2):
    #  if not event.strip() in contents1: unique_to_file2.append(event)
    
    for i, event in enumerate(content_file1):
      if not event.strip() in contents2: unique_to_file1.append(event)
    
    

    # print out the unique lines
    #change the number for File1 and 2 above
    print "Unique events in my selection:"
    #print "Unique events in Gent selection:"
    print unique_to_file1 
    
