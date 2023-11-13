//Basic script to create EFT datacards
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
vector<string> regions = {"njet4to5_btag2","njet6to7_btag2","njet8p_btag2","njet4to5_btag1","njet6to7_btag1","njet8p_btag1","njet8p_btag3p","mvaCut0.1m_njet6to7_btag3p","mvaCut0.1p_njet6to7_btag3p","mvaCut0.2m_njet4to5_btag3p","mvaCut0.2p_njet4to5_btag3p"}; //"njet4to5_btag3p","njet6to7_btag3p"
vector<string> theYounglings = {"nJetGood","2l_4t","2l_4t_coarse","nBTag","ht"};
vector<string> EXPgroup = {	"LeptonSF","PU","L1Prefire","jesTotal","BTagSFHf","BTagSFLf","BTagSFHfs1","BTagSFLfs1","BTagSFHfs2","BTagSFLfs2","BTagSFCfe1","BTagSFCfe2",
				//"Trigger",
				"noTopPtReweight",
				};

vector<string>  THgroup = {"HDamp","TTISR","DYISR","TTFSR","DYFSR","TTFactorizationShape","DYFactorizationShape","TTrenormalizationShape","DYrenormalizationShape"}; 
int nPDFs = 100;
std::vector<std::string> PDFWeights;
for (int i = 1; i <= nPDFs; ++i) { PDFWeights.push_back("PDF_" + std::to_string(i));}
THgroup.insert(THgroup.end(), PDFWeights.begin(), PDFWeights.end());

std::vector<const std::string*> variations;
for (const std::string& THvariation : THgroup) { variations.push_back(&THvariation);}
for (const std::string& EXPvariation : EXPgroup) { variations.push_back(&EXPvariation);}

// Define a map to store scale unc. normalization factors
//std::map<std::string, std::map<std::string, double>> scale_factors_Up;
//scale_factors_Up["njet4to5-btag1"]	 = {{"ttbb", 0.72}, {"ttcc", 0.89}, {"ttother", 0.90},{"tttt",0.98},{"DY",1.0}};
//scale_factors_Up["njet4to5-btag2"]	 = {{"ttbb", 0.75}, {"ttcc", 0.90}, {"ttother", 0.91},{"tttt",0.99},{"DY",1.0}};
//scale_factors_Up["njet4to5-btag3p"]	 = {{"ttbb", 0.84}, {"ttcc", 0.90}, {"ttother", 0.90},{"tttt",0.99},{"DY",1.0}};
//scale_factors_Up["njet6to7-btag1"]	 = {{"ttbb", 0.70}, {"ttcc", 0.90}, {"ttother", 0.90},{"tttt",1.02},{"DY",1.0}};
//scale_factors_Up["njet6to7-btag2"]	 = {{"ttbb", 0.72}, {"ttcc", 0.90}, {"ttother", 0.91},{"tttt",0.99},{"DY",1.0}};
//scale_factors_Up["njet6to7-btag3p"]	 = {{"ttbb", 1.0}, {"ttcc", 1.0}, {"ttother", 1.0},{"tttt",1.0},{"DY",1.0}};
//scale_factors_Up["njet8p-btag1"]	 = {{"ttbb", 0.68}, {"ttcc", 0.90}, {"ttother", 0.90},{"tttt",1.03},{"DY",1.0}};
//scale_factors_Up["njet8p-btag2"]	 = {{"ttbb", 0.72}, {"ttcc", 0.90}, {"ttother", 0.90},{"tttt",1.04},{"DY",1.0}};
//scale_factors_Up["njet8p-btag3p"]	 = {{"ttbb", 1.0}, {"ttcc", 1.0}, {"ttother", 1.0},{"tttt",1.0},{"DY",1.0}};

std::map<std::string, std::map<std::string, double>> scale_factors;
scale_factors["njet4to5-btag1"]	 = {{"ttbb", 1.75}, {"ttcc", 1.17}, {"ttother", 1.16},{"tttt",1.04},{"DY",1.02}};
scale_factors["njet4to5-btag2"]	 = {{"ttbb", 1.66}, {"ttcc", 1.14}, {"ttother", 1.13},{"tttt",1.02},{"DY",1.02}};
scale_factors["njet4to5-btag3p"]	 = {{"ttbb", 1.47}, {"ttcc", 1.14}, {"ttother", 1.14},{"tttt",1.03},{"DY",1.02}};
scale_factors["njet6to7-btag1"]	 = {{"ttbb", 1.78}, {"ttcc", 1.16}, {"ttother", 1.14},{"tttt",1.02},{"DY",1.01}};
scale_factors["njet6to7-btag2"]	 = {{"ttbb", 1.75}, {"ttcc", 1.14}, {"ttother", 1.13},{"tttt",1.01},{"DY",1.01}};
scale_factors["njet6to7-btag3p"]	 = {{"ttbb", 1.0}, {"ttcc", 1.0}, {"ttother", 1.0},{"tttt",1.0},{"DY",1.01}};
scale_factors["njet8p-btag1"]	 = {{"ttbb", 1.85}, {"ttcc", 1.17}, {"ttother", 1.16},{"tttt",0.95},{"DY",1.0}};
scale_factors["njet8p-btag2"]	 = {{"ttbb", 1.72}, {"ttcc", 1.14}, {"ttother", 1.14},{"tttt",0.94},{"DY",1.0}};
scale_factors["njet8p-btag3p"]	 = {{"ttbb", 1.0}, {"ttcc", 1.0}, {"ttother", 1.0},{"tttt",1.0},{"DY",1.0}};

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
   	vector<string> bkg_procs = {"TTTT","TTLep_cc","TTLep_other","ST_tch","ST_twch","TTW","TTZ","TTH","DY","DiBoson"};
   	//signal
   	vector<string>  sig_procs = {"sm"}; 
	vector<string>  wcNames = {"cQQ1"};
	for(auto wc: wcNames ){
		sig_procs.push_back("sm_lin_quad_"+wc);
		sig_procs.push_back("quad_"+wc);}
 	
   	cb.AddObservations({"*"}, {"ttbbEFT"}, {"13TeV"}, {theChosenOne}, cats);
   	cb.AddProcesses({"*"},  {"ttbbEFT"}, {"13TeV"}, {theChosenOne}, bkg_procs, cats, false);
   	cb.AddProcesses({"*"},  {"ttbbEFT"}, {"13TeV"}, {theChosenOne}, sig_procs, cats, true);
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
		cb.cp().process( ch::JoinStr({ bkg_procs}) )
		.AddSyst(cb, *syst, "shape", SystMap<>::init(1.00));
	}

     	
   	 //Rate uncertainties
   	cb.cp().process({"sm","TTLep_cc","TTLep_other"})
   	.AddSyst(cb, "ttbar_rate", "lnN", SystMap<>::init(1.03));
   
   	cb.cp().process({"ST_tch"})
   	.AddSyst(cb, "t_rate", "lnN", SystMap<>::init(1.03));
    
   	cb.cp().process({"ST_twch"})
   	.AddSyst(cb, "tW_rate", "lnN", SystMap<>::init(1.30));//1.05
   
    	cb.cp().process({"TTW"})
   	.AddSyst(cb, "ttW_rate", "lnN", SystMap<>::init(1.10));
   
    	cb.cp().process({"TTZ"})
   	.AddSyst(cb, "ttZ_rate", "lnN", SystMap<>::init(1.09));
   
    	cb.cp().process({"TTH"})
   	.AddSyst(cb, "ttH_rate", "lnN", SystMap<>::init(1.08));
    	
	cb.cp().process({"DY"})
   	.AddSyst(cb, "DY_rate", "lnN", SystMap<>::init(5.0));
	
	cb.cp().process({"DiBoson"})
   	.AddSyst(cb, "DiBoson_rate", "lnN", SystMap<>::init(1.30));

	//scale unc. normalization factor	
	std::map<std::string, double>& factor_Down = scale_factors[selection];
	cb.cp().process({"sm"}).AddSyst(cb, "scale_normalization_"+selection, "lnN", SystMap<>::init(factor_Down["ttbb"]));
	cb.cp().process({"TTLep_cc"}).AddSyst(cb, "scale_normalization_"+selection, "lnN", SystMap<>::init(factor_Down["ttcc"]));
	cb.cp().process({"TTLep_other"}).AddSyst(cb, "scale_normalization_"+selection, "lnN", SystMap<>::init(factor_Down["ttother"]));
	cb.cp().process({"TTTT"}).AddSyst(cb, "scale_normalization_"+selection, "lnN", SystMap<>::init(factor_Down["tttt"]));
	cb.cp().process({"DY"}).AddSyst(cb, "scale_normalization_"+selection, "lnN", SystMap<>::init(factor_Down["DY"]));


	//group nuisances
	cb.cp().SetGroup("theory", THgroup);
	cb.cp().SetGroup("experimental", EXPgroup);


   	string dir = "../../../../../../../../groups/hephy/cms/maryam.shooshtari/www/tttt/plots/analysisPlots/4t-v12-syst/RunII/";//all/trg-dilep-OS-minDLmass20-offZ1-lepVeto2-"+selection+"-ht500"; // relative link from this dir
   	string input_filename = dir+"4t-v12-syst_"+selection+".root";
   	
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
   	TString filename = "ttbbEFT_"+theChosenOne+"_"+selection+".input.root";
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
