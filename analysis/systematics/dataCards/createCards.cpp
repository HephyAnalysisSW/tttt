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
vector<string> regions = {"njet4to5-btag3p","njet6to7-btag3p","njet8p-btag3p","njet4to5-btag2","njet6to7-btag2","njet8p-btag2","njet4to5-btag1","njet6to7-btag1","njet8p-btag1"};//, "njet4p-btag2p","njet6p-btag2p"};
vector<string> theYounglings = {"nJetGood","2l_4t","2l_4t_coarse","nBTag","ht"};
vector<string> EXPgroup = {	"LeptonSF","PU","L1Prefire","jesTotal","BTagSFHf","BTagSFLf","BTagSFHfs1","BTagSFLfs1","BTagSFHfs2","BTagSFLfs2","BTagSFCfe1","BTagSFCfe2",
				//"Trigger",
				"noTopPtReweight",
				};

vector<string>  THgroup = {"HDamp","ISR", "FSR","scaleShape"}; 
int nPDFs = 100;
std::vector<std::string> PDFWeights;
for (int i = 1; i <= nPDFs; ++i) { PDFWeights.push_back("PDF_" + std::to_string(i));}
THgroup.insert(THgroup.end(), PDFWeights.begin(), PDFWeights.end());

std::vector<const std::string*> variations;
for (const std::string& THvariation : THgroup) { variations.push_back(&THvariation);}
for (const std::string& EXPvariation : EXPgroup) { variations.push_back(&EXPvariation);}

// Define a map to store scale unc. normalization factors
std::map<std::string, std::map<std::string, double>> scale_factors;
scale_factors["njet4to5-btag1"]	 = {{"ttbb", 1.75}, {"ttcc", 1.17}, {"ttother", 1.16},{"tttt",1.04},{"DY_inclusive",1.0}};
scale_factors["njet4to5-btag2"]	 = {{"ttbb", 1.66}, {"ttcc", 1.14}, {"ttother", 1.13},{"tttt",1.02},{"DY_inclusive",1.0}};
scale_factors["njet4to5-btag3p"]	 = {{"ttbb", 1.47}, {"ttcc", 1.14}, {"ttother", 1.14},{"tttt",1.03},{"DY_inclusive",1.0}};
scale_factors["njet6to7-btag1"]	 = {{"ttbb", 1.78}, {"ttcc", 1.16}, {"ttother", 1.14},{"tttt",1.02},{"DY_inclusive",1.0}};
scale_factors["njet6to7-btag2"]	 = {{"ttbb", 1.75}, {"ttcc", 1.14}, {"ttother", 1.13},{"tttt",1.01},{"DY_inclusive",1.0}};
scale_factors["njet6to7-btag3p"]	 = {{"ttbb", 1.0}, {"ttcc", 1.0}, {"ttother", 1.0},{"tttt",1.0},{"DY_inclusive",1.0}};
scale_factors["njet8p-btag1"]	 = {{"ttbb", 1.85}, {"ttcc", 1.17}, {"ttother", 1.16},{"tttt",0.95},{"DY_inclusive",1.0}};
scale_factors["njet8p-btag2"]	 = {{"ttbb", 1.72}, {"ttcc", 1.14}, {"ttother", 1.14},{"tttt",0.94},{"DY_inclusive",1.0}};
scale_factors["njet8p-btag3p"]	 = {{"ttbb", 1.0}, {"ttcc", 1.0}, {"ttother", 1.0},{"tttt",1.0},{"DY_inclusive",1.0}};

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
   	vector<string> bkg_procs = {"TTLep_bb","TTLep_cc","TTLep_other","ST_tch","ST_twch","TTW","TTZ","TTH","DY_inclusive","DiBoson"};
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

	//scale unc. normalization factor
    	
	std::map<std::string, double>& factor_Down = scale_factors[selection];
	cb.cp().process({"TTLep_bb"}).AddSyst(cb, "scale_normalization_Down_"+selection, "lnN", SystMap<>::init(factor_Down["ttbb"]));
	cb.cp().process({"TTLep_cc"}).AddSyst(cb, "scale_normalization_Down_"+selection, "lnN", SystMap<>::init(factor_Down["ttcc"]));
	cb.cp().process({"TTLep_other"}).AddSyst(cb, "scale_normalization_Down_"+selection, "lnN", SystMap<>::init(factor_Down["ttother"]));
	cb.cp().process({"TTTT"}).AddSyst(cb, "scale_normalization_Down_"+selection, "lnN", SystMap<>::init(factor_Down["tttt"]));
	cb.cp().process({"DY_inclusive"}).AddSyst(cb, "scale_normalization_Down_"+selection, "lnN", SystMap<>::init(factor_Down["DY_inclusive"]));


	//group nuisances
	cb.cp().SetGroup("theory", THgroup);
	cb.cp().SetGroup("experimental", EXPgroup);


   	string dir = "../../../../../../../../groups/hephy/cms/maryam.shooshtari/www/tttt/plots/analysisPlots/4t-v10.3-syst/RunII/all/trg-dilep-OS-minDLmass20-offZ1-lepVeto2-"+selection+"-ht500"; // relative link from this dir
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
