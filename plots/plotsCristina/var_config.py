#class Variable:
#
#    def __init__(self, name, type, read=True, write=True, inData=False, inPlot=False, isSyst=False ):
#
#        self.name   = self
#        self.type   = type
#        self.read   = read
#        self.write  = write
#        self.inData = inData
#        self.inPlot = inPlot
#        self.isSyst = isSyst

#class NanoVariables:

#    def __init__(self, year):

#        if year not in [2016, 2017, 2018]:
#            raise Exception("This variable was not implemented in the %s"%year )

#        self.usedParticlesList = ["Electron", "Muon", "Lepton", "Jet", "BJet", "MET", "GenJet"]


def fetch_variables_jets():

    #in analysis-2l it is called jetVars
    variables_jets =    ['pt/F',
                         'eta/F',
                         'phi/F',
                         'btagDeepB/F']

    #in analysis-2l it is called jetVars
    #variables_

    return variables_jets
