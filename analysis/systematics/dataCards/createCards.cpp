//
//---------------------------------------------------------------------------------
//this file has to be stored in $CMSSW_BASE$/src/CombineHarvester/CombineTools/bin/
//add the file to BuildFile.xml in the same location
//compile with scram after each change
//saving it here to be easily accesible for everyone
//---------------------------------------------------------------------------------
//
#include <string>
#include <map>
#include <set>
#include <iostream>
#include <iomanip>
#include <utility>
#include <vector>
#include <cstdlib>
#include "CombineHarvester/CombineTools/interface/CombineHarvester.h"
#include "CombineHarvester/CombineTools/interface/Observation.h"
#include "CombineHarvester/CombineTools/interface/Process.h"
#include "CombineHarvester/CombineTools/interface/Utilities.h"
#include "CombineHarvester/CombineTools/interface/Systematics.h"
#include "CombineHarvester/CombineTools/interface/BinByBin.h"

using namespace std;

int main() {
vector<string> regions = {"njet4to5-btag3p","njet6to7-btag3p","njet8p-btag3p","njet4to5-btag2","njet6to7-btag2","njet8p-btag2"};
vector<string> theYounglings = {"nJetGood","2l_4t","2l_4t_coarse"};
vector<string> EXPgroup = {	"LeptonSF","PU","L1Prefire","jesTotal","BTagSFHf","BTagSFLf","BTagSFHfs1","BTagSFLfs1","BTagSFHfs2","BTagSFLfs2","BTagSFCfe1","BTagSFCfe2",
				//"Trigger",
				"noTopPtReweight",
				};

vector<string>  THgroup = {"HDamp","ISR", "FSR","scale"}; 
int nPDFs = 100;
std::vector<std::string> PDFWeights;
for (int i = 1; i <= nPDFs; ++i) { PDFWeights.push_back("PDF_" + std::to_string(i));}
THgroup.insert(THgroup.end(), PDFWeights.begin(), PDFWeights.end());

std::vector<const std::string*> variations;
for (const std::string& THvariation : THgroup) { variations.push_back(&THvariation);}
for (const std::string& EXPvariation : EXPgroup) { variations.push_back(&EXPvariation);}

for (auto selection:regions){
   for (auto theChosenOne:theYounglings){
   	// First define the location of the "auxiliaries" directory where we can source the input files containing the datacard shapes
   	//  string aux_shapes = string(getenv("CMSSW_BASE")) + "/src/auxiliaries/shapes/";
   	string aux_shapes = string(getenv("CMSSW_BASE")) + "/src/CombineHarvester/CombineTools/bin/";
   	// Create an empty CombineHarvester instance that will hold all of the datacard configuration and histograms etc.
   	ch::CombineHarvester cb;
   	// Uncomment this next line to see a *lot* of debug information
   	// cb.SetVerbosity(3);
   	// Here we will just define categories for the analysis. Each entry in the vector below specifies a bin name and corresponding bin_id.
   	ch::Categories cats = {
   	        {1, "tttt__"+theChosenOne}
   	      };
   	// ch::Categories is just a typedef of vector<pair<int, string>>
   	
   	//bkg_procs
   	vector<string> bkg_procs = {"TTLep_bb","TTLep_cc","TTLep_other","ST_tch","ST_twch","TTW","TTZ","TTH","DY","DiBoson"};
   	//signal
   	vector<string>  sig_procs = {"TTTT"}; 
   	
   	cb.AddObservations({"*"}, {"tttt"}, {"13TeV"}, {theChosenOne}, cats);
   	cb.AddProcesses({"*"},  {"tttt"}, {"13TeV"}, {theChosenOne}, bkg_procs, cats, false);
   	cb.AddProcesses({"*"},  {"tttt"}, {"13TeV"}, {theChosenOne}, sig_procs, cats, true);
   	//Some of the code for this is in a nested namespace, so we'll make some using declarations first to simplify things a bit.
   	using ch::syst::SystMap;
   	using ch::syst::era;
   	using ch::syst::bin_id;
   	using ch::syst::process;
   	
   	//cb.cp()
   	//.AddSyst(cb, "lumi_13TeV", "lnN", SystMap<era>::init
   	//({"lumi_13TeV"}, 1.018));
   	
   	// Shape uncertainties
	for (auto syst:variations){
		cb.cp().process( ch::JoinStr({sig_procs, bkg_procs}) )
		.AddSyst(cb, *syst, "shape", SystMap<>::init(1.00));
	}

     	
   	 //Rate uncertainties
   	cb.cp().process({"TTLep_bb","TTLep_cc","TTLep_other"})
   	.AddSyst(cb, "ttbar_rate", "lnN", SystMap<>::init(1.03));
   
   	cb.cp().process({"ST_tch"})
   	.AddSyst(cb, "t_rate", "lnN", SystMap<>::init(1.03));
    
   	cb.cp().process({"ST_twch"})
   	.AddSyst(cb, "tW_rate", "lnN", SystMap<>::init(1.05));
   
    	cb.cp().process({"TTW"})
   	.AddSyst(cb, "ttW_rate", "lnN", SystMap<>::init(1.10));
   
    	cb.cp().process({"TTZ"})
   	.AddSyst(cb, "ttZ_rate", "lnN", SystMap<>::init(1.09));
   
    	cb.cp().process({"TTH"})
   	.AddSyst(cb, "ttH_rate", "lnN", SystMap<>::init(1.08));
    	
	cb.cp().SetGroup("theory", THgroup);
	cb.cp().SetGroup("experimental", EXPgroup);


   	string dir = "../../../../../../../../groups/hephy/cms/maryam.shooshtari/www/tttt/plots/analysisPlots/4t-v10-syst/RunII/all/trg-dilep-OS-minDLmass20-offZ1-lepVeto2-"+selection+"-ht500"; // relative link from this dir
   	string input_filename = dir+"/tttt__systematics.root";
   	
   	cb.cp().backgrounds().ExtractShapes(
   	  aux_shapes + input_filename,
   	  "$BIN/$PROCESS",
   	  "$BIN/$PROCESS__$SYSTEMATIC");
   	cb.cp().signals().ExtractShapes(
   	  aux_shapes + input_filename,
   	  "$BIN/$PROCESS",
   	  "$BIN/$PROCESS__$SYSTEMATIC");
   	
   	// This function modifies every entry to have a standardised bin name of
   	// the form: {analysis}_{channel}_{bin_id}_{era}
   	// hich is commonly used in the htt analyses
   	ch::SetStandardBinNames(cb);
   	
   	// First we generate a set of bin names:
   	set<string> bins = cb.bin_set();
   	// This method will produce a set of unique bin names by considering all Observation, Process and Systematic entries in the CombineHarvester instance.
   	
   	// We create the output root file that will contain all the shapes.
   	TString filename = "tttt_"+theChosenOne+"_"+selection+".input.root";
   	TFile output(filename, "RECREATE");
   	
   	// Finally we iterate through each bin,mass combination and write a datacard
   	for (auto b : bins) {
   	        cout << ">> Writing datacard for bin: " << b << " and mass: " << 125
   	        << "\n";
   		// We need to filter on both the mass and the mass hypothesis,
   		//where we must remember to include the "*" mass entry to get
   		//all the data and backgrounds.
   		cb.cp().bin({b}).mass({125,"*"}).WriteDatacard(b +"_"+selection+ ".txt", output);
   		}
   	}
   
   }
}
