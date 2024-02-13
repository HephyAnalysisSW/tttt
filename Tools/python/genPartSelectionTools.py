import ROOT
import copy
from math import isnan

from Analysis.Tools.helpers         import deltaR


def getGenFirstCopy(genparts):
    copies=[]
    for g in genparts:
        if ((g['statusFlags']&(1<<12))!=0) and g['genPartIdxMother']>0:
            g['isFirstCopy'] = True
        else: continue
        copies.append(g)
    return copies

def getGenLastCopy(genparts):
    copies=[]
    for g in genparts:
        if ((g['statusFlags']&(1<<13))!=0) and g['genPartIdxMother']>0:
            g['isLastCopy'] = True
        else: continue
        copies.append(g)
    return copies

# Run through parents in genparticles, and return list
def getParents(g, genParticles ):
  parents = []
  if g['genPartIdxMother'] >= 0:
    try:
        mother1  = [ genParticle for genParticle in genParticles if genParticle["index"] == g['genPartIdxMother'] ][0]
        parents      += [ mother1 ] + getParents( mother1, genParticles )
    except:
        return parents
  return parents

def getTopMother(g, gPart):
      withparents = []
      parentsList = getParents(g, gPart)
      parentsList.pop()
      for i, p in enumerate(parentsList):
          if abs(p['pdgId'])==6:
              g['isFromTop'] = True
              g['motherPdgId'] = p['pdgId']
              g['motherIdx'] = p['index']
          elif abs(p['pdgId'])==6 and abs(g['pdgId'])==5:
              g['isFromTop'] = True
              g['motherPdgId'] = p['pdgId']
              g['motherIdx'] = p['index']
              break
          withparents.append(g)
      return withparents

# THIS below is the funct that gives the correct peak plot (for reference)
# def getTopMother(partons, gPart):
#     withparents = []
#     for index, g in enumerate(partons):
#         if g['genPartIdxMother'] < 0: continue
#         mother = gPart[g['genPartIdxMother']]
#         grandmother = gPart[mother['genPartIdxMother']]
#         if g['pdgId']!= mother['pdgId']:
#             if abs(mother['pdgId']) in [6, 24]:
#                 if abs(mother['pdgId'])==6:
#                     #check for Ws!!!
#                     g['isFromTop'] = True
#                     g['motherPdgId'] = mother['pdgId']
#                     g['motherIdx'] = mother['genPartIdxMother']
#                 elif abs(mother['pdgId'])==24 and abs(grandmother['pdgId'])==6:
#                     g['isFromTop'] = True
#                     g['motherPdgId'] = grandmother['pdgId']
#                     g['motherIdx'] = grandmother['genPartIdxMother']
#                 else: continue
#             else: continue
#         withparents.append(g)
#     return withparents
