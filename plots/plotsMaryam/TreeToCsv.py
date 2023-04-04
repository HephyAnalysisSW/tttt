import ROOT

# Open the ROOT file and get the TTree
file = ROOT.TFile.Open("/scratch-cbe/users/maryam.shooshtari/tttt/nanoTuples/tttt_v5_v3/UL2018/dilep/TTTT_sync/TTTT_sync_0.root")
tree = file.Get("Events")

# Create a list of events to include
events_to_include = [1598281,1598570,1906159,1906316,13845310,13994079,891544,958217,958608,1018199,1018319,1019000,961251,1093192,896198,896314,896382,927395,282124,283586,283905,283936,548982,682301,712199,712800,712849,770093,771280]
# Open the CSV file for writing
with open("problematicEvents.csv", "w") as csv_file:
  # Write the header line to the CSV file
  csv_file.write("electron/muon, pt, eta, phi, dxy, dz, 3D IP Significance, missing hits (or 0 for muons), miniIso, btagscore closest jet , isFO , pt ratio , TOP lepton mva score v1,TOP lepton mva score v2 \n")

  # Loop over the entries in the TTree
  for i in range(tree.GetEntries()):
    tree.GetEntry(i)
    
    # Get the event number
    event = tree.event
    
    # Check if the event is in the list of events to include
    if event in events_to_include: 
      csv_file.write("{}, nlep = {}\n".format(event,tree.nlep))
      #Get each lepton
      for ilep in range(len(tree.lep_pt)): 
        # Get the values of the x, y, and z branches
        #y = tree.y
        
        if abs(tree.lep_pdgId[ilep])==11:
          pdgId = "electron"
          POGmva = tree.lep_mvaFall17V2noIso_WPL[ilep]
        else:
          pdgId ="muon"
          POGmva = None
        ptRatio = 1/(tree.lep_jetRelIso[ilep]+1)
        pt = tree.lep_pt[ilep]
        eta = tree.lep_eta[ilep]
        phi = tree.lep_phi[ilep]
        dxy = tree.lep_dxy[ilep]
        dz = tree.lep_dz[ilep]
        mvav2 = tree.lep_mvaTOPv2[ilep]
        mvav1 = tree.lep_mvaTOP[ilep]
        Iso = tree.lep_miniPFRelIso_all[ilep]
        jetBTag = tree.lep_jetBTag[ilep]
        sip3d = tree.lep_sip3d[ilep]
        lostHits = tree.lep_lostHits[ilep]
        FO = tree.lep_isFO[ilep]

        # Write the values to the CSV file
        csv_file.write("{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(pdgId, pt, eta, phi, dxy, dz,sip3d,lostHits,Iso,jetBTag,FO,ptRatio,mvav1,mvav2))

print len(events_to_include)
file.Close()
