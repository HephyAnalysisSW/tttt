''' Class to interpret string based cuts
'''
from objectSelection          import lepString
import logging
logger = logging.getLogger(__name__)

jetSelection    = "nJetGood"
bJetSelectionM  = "nBTag"

mIsoWP = { "VT":5, "T":4, "M":3 , "L":2 , "VL":1, 0:"None" }


mu_string  = lepString('mu','M')
ele_string = lepString('ele','T')

special_cuts = {

    "example":         "l1_pt>50",
    
    "singlelep":       "l1_pt>20",
    "singlelepVL":     "l1_pt>20",
    "singlelepL":      "l1_pt>20&&l1_mvaTOPWP>=2",
    "singlelepM":      "l1_pt>20&&l1_mvaTOPWP>=3",
    "singlelepT":      "l1_pt>20&&l1_mvaTOPWP>=4",
    
    "dilep":           "Sum$({mu_string})+Sum$({ele_string})==2&&l1_pt>40&&l2_pt>20".format(mu_string=mu_string,ele_string=ele_string),
    "dilepVL":         "(Sum$(lep_pt>15)==2)&&l1_pt>40&&l2_pt>20",
    "dilepL" :         "(Sum$(lep_pt>15)==2)&&l1_pt>40&&l2_pt>20&&l1_mvaTOPWP>=2&&l2_mvaTOPWP>=2",
    "dilepM" :         "(Sum$(lep_pt>15)==2)&&l1_pt>40&&l2_pt>20&&l1_mvaTOPWP>=3&&l2_mvaTOPWP>=3",
    "dilepT" :         "(Sum$(lep_pt>15)==2)&&l1_pt>40&&l2_pt>20&&l1_mvaTOPWP>=4&&l2_mvaTOPWP>=4",
    
    "trilep":          "Sum$({mu_string})+Sum$({ele_string})==3&&l1_pt>25&&l2_pt>20&&l3_pt>10".format(mu_string=mu_string,ele_string=ele_string),
    "trilepVL":        "(Sum$(lep_pt>=10)==3)&&l1_pt>40&&l2_pt>20&&l3_pt>10",
    "trilepL":         "(Sum$(lep_pt>=10)==3)&&l1_pt>40&&l2_pt>20&&l3_pt>10&&l1_mvaTOPWP>=2&&l2_mvaTOPWP>=2&&l3_mvaTOPWP>=2",
    "trilepM":         "(Sum$(lep_pt>15)==3)&&l1_pt>40&&l2_pt>20&&l3_pt>10&&l1_mvaTOPWP>=3&&l2_mvaTOPWP>=3&&l3_mvaTOPWP>=3",
    "trilepT":         "(Sum$(lep_pt>15)==3)&&l1_pt>40&&l2_pt>20&&l3_pt>10&&l1_mvaTOPWP>=4&&l2_mvaTOPWP>=4&&l3_mvaTOPWP>=4",
    
    "quadlep":         "(Sum$(lep_pt>15)==4)&&l1_pt>40&&l2_pt>20&&l3_pt>10&&l4_pt>10",
    "quadlepVL":       "(Sum$(lep_pt>15)==4)&&l1_pt>40&&l2_pt>20&&l3_pt>10&&l4_pt>10&&l1_mvaTOPWP>=2&&l2_mvaTOPWP>=2&&l3_mvaTOPWP>=2&&l4_mvaTOPWP>=2",
    "quadlepM":        "(Sum$(lep_pt>15)==4)&&l1_pt>40&&l2_pt>20&&l3_pt>10&&l4_pt>10&&l1_mvaTOPWP>=3&&l2_mvaTOPWP>=3&&l3_mvaTOPWP>=3&&l4_mvaTOPWP>=3",
    "quadlepM":        "(Sum$(lep_pt>15)==4)&&l1_pt>40&&l2_pt>20&&l3_pt>10&&l4_pt>10&&l1_mvaTOPWP>=4&&l2_mvaTOPWP>=4&&l3_mvaTOPWP>=4&&l4_mvaTOPWP>=4",
    
    "OS":              "(Sum$(lep_isFO)==2&&Sum$(lep_isTight)==2&&(l1_pdgId/abs(l1_pdgId))*(abs(l2_pdgId)/l2_pdgId)<0)",
    "SS":              "(Sum$(lep_isFO)==2&&Sum$(lep_isTight)==2&&(l1_pdgId/abs(l1_pdgId))*(abs(l2_pdgId)/l2_pdgId)>0)",
 
    "trg":             "triggerDecision",
    
    "leptonveto":      "(Sum$(lep_isFO))==3&&(Sum$(lep_isTight))==3",
    
    "onZ1"   :         "abs(Z1_mass-91.2)<10",
    "offZ1"  :         "(!(abs(Z1_mass-91.2)<15))",
    "offZ2"  :         "(!(abs(Z2_mass-91.2)<15))",
  }



continous_variables = [ ('ht','Sum$(JetGood_pt*(JetGood_pt>25&&abs(JetGood_eta)<2.4))'), ("met", "met_pt"), ("Z2mass", "Z2_mass"), ("Z1pt", "Z1_pt"), ("Z2pt", "Z2_pt"), ("Z1mass", "Z1_mass"), ("minDLmass", "minDLmass"), ("mT", "mT"), ("ptG", "photon_pt")]
discrete_variables  = [ ("njet", "nJetGood"), ("btag", "nBTag"), ("nlep", "nlep")]

class cutInterpreter:
    ''' Translate var100to200-var2p etc.
    '''

    @staticmethod
    def translate_cut_to_string( string ):

        if string.startswith("multiIso"):
            str_ = mIsoWP[ string.replace('multiIso','') ]
            return "l1_mIsoWP>%i&&l2_mIsoWP>%i" % (str_, str_)
        elif string.startswith("relIso"):
           iso = float( string.replace('relIso','') )
           raise ValueError("We do not want to use relIso for our analysis anymore!")
           return "l1_relIso03<%3.2f&&l2_relIso03<%3.2f"%( iso, iso )
        elif string.startswith("miniIso"):
           iso = float( string.replace('miniIso','') )
           return "l1_miniRelIso<%3.2f&&l2_miniRelIso<%3.2f"%( iso, iso )
        # special cuts
        if string in special_cuts.keys(): return special_cuts[string]

        # continous Variables and discrete variables with "To"
        for var, tree_var in continous_variables + discrete_variables:
            isDiscrete = (var, tree_var) in discrete_variables
            if string.startswith( var ):
                num_str = string[len( var ):].replace("to","To").split("To")
                # don't do discrete variables without "To"
                if isDiscrete and len(num_str)<=1:
                    continue
                upper = None
                lower = None
                if len(num_str)==2:
                    lower, upper = num_str
                elif len(num_str)==1:
                    lower = num_str[0]
                else:
                    raise ValueError( "Can't interpret string %s" % string )
                res_string = []
                if lower: res_string.append( tree_var+">="+lower )
                leq = "<=" if isDiscrete else "<"
                if upper: res_string.append( tree_var+leq+upper )
                return "&&".join( res_string )

        # discrete Variables
        for var, tree_var in discrete_variables:
            logger.debug("Reading discrete cut %s as %s"%(var, tree_var))
            if string.startswith( var ):
                # Omit discrete variables, done above
                if string[len( var ):].replace("to","To").count("To"):
                    continue
                    #raise NotImplementedError( "Can't interpret string with 'to' for discrete variable: %s. You just volunteered." % string )

                num_str = string[len( var ):]
                # logger.debug("Num string is %s"%(num_str))
                # var1p -> tree_var >= 1
                if num_str[-1] == 'p' and len(num_str)==2:
                    # logger.debug("Using cut string %s"%(tree_var+">="+num_str[0]))
                    return tree_var+">="+num_str[0]
                # var123->tree_var==1||tree_var==2||tree_var==3
                else:
                    vls = [ tree_var+"=="+c for c in num_str ]
                    if len(vls)==1:
                      # logger.debug("Using cut string %s"%vls[0])
                      return vls[0]
                    else:
                      # logger.debug("Using cut string %s"%'('+'||'.join(vls)+')')
                      return '('+'||'.join(vls)+')'
        raise ValueError( "Can't interpret string %s. All cuts %s" % (string,  ", ".join( [ c[0] for c in continous_variables + discrete_variables] +  special_cuts.keys() ) ) )

    @staticmethod
    def cutString( cut, select = [""], ignore = []):
        ''' Cutstring syntax: cut1-cut2-cut3
        '''
        if cut is None or cut=="":
            return "(1)"
        cuts = cut.split('-')
        # require selected
        cuts = filter( lambda c: any( sel in c for sel in select ), cuts )
        # ignore
        cuts = filter( lambda c: not any( ign in c for ign in ignore ), cuts )

        cutString = "&&".join( map( cutInterpreter.translate_cut_to_string, cuts ) )

        return cutString

    @staticmethod
    def cutList ( cut, select = [""], ignore = []):
        ''' Cutstring syntax: cut1-cut2-cut3
        '''
        cuts = cut.split('-')
        # require selected
        cuts = filter( lambda c: any( sel in c for sel in select ), cuts )
        # ignore
        cuts = filter( lambda c: not any( ign in c for ign in ignore ), cuts )
        return [ cutInterpreter.translate_cut_to_string(cut) for cut in cuts ]
        #return  "&&".join( map( cutInterpreter.translate_cut_to_string, cuts ) )

if __name__ == "__main__":
    print cutInterpreter.cutString("njet2-btag0p-multiIsoVT-relIso0.12-looseLeptonVeto-mll20-onZ-met80-metSig5-dPhiJet0-dPhiJet1-mt2ll100")
    print
    print cutInterpreter.cutList("njet2-btag0p-multiIsoVT-relIso0.12-looseLeptonVeto-mll20-onZ-met80-metSig5-dPhiJet0-dPhiJet1-mt2ll100")
