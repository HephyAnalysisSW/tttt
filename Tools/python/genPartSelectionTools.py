# coding=utf-8
import ROOT
import copy
from math import isnan, cos, sin, sinh, sqrt

from Analysis.Tools.helpers         import deltaR


def getGenFirstCopy(genparts):
    copies=[]
    for g in genparts:
        if ((g['statusFlags']&(1<<12))!=0) and g['genPartIdxMother']>=0:
            g['isFirstCopy'] = True
        else: continue
        copies.append(g)
    return copies

def getGenLastCopy(genparts):
    copies=[]
    for g in genparts:
        if ((g['statusFlags']&(1<<13))!=0):#x and g['genPartIdxMother']>=0:
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
              print("top")
              g['isFromTop'] = True
              g['motherPdgId'] = p['pdgId']
              g['motherIdx'] = p['index']
              withparents.append(g)
              break
      return withparents

def getMatching(g, jet, gPart,  dR=0.4):
    # print("g in matching {}".format(g))
    isMatch = False
    outJet = -1
    mother = gPart[g['genPartIdxMother']]
    # print(mother)
    grandmother = gPart[mother['genPartIdxMother']]
    # b comes from top
    if abs(g['pdgId'])== 5 and abs(mother['pdgId']) == 6:
        j, dRmin = closestdR(g, jet)
        if dRmin < dR:
            outJet = j
            isMatch = True
    # u/c from W from top
    elif g['pdgId']%2 == 0 and abs(mother['pdgId']) == 24:
        parentList = filter(lambda p:abs(p['pdgId'])==6, getParents(g, gPart))
        for p in parentList:
            if abs(p['pdgId'])==6 and p['genPartIdxMother']==0:
                j, dRmin = closestdR(p, jet)
                if dRmin < dR:
                    outJet = j
                    isMatch = True
    # d/s from W from top
    elif g['pdgId']%2 != 0 and abs(g['pdgId'])!= [13,11] and abs(mother['pdgId']) == 24:
        parentList = filter(lambda p:abs(p['pdgId'])==6, getParents(g, gPart))
        for p in parentList:
            if abs(p['pdgId'])==6 and p['genPartIdxMother']==0:
                j, dRmin = closestdR(p, jet)
                if dRmin < dR:
                    outJet = j
                    isMatch = True

    return isMatch, outJet


def closestdR(obj, collection, presel=lambda x, y: True):
    ret = None
    drMin = 0.4
    for i, x in enumerate(collection):
        if not presel(obj, x):
            continue
        dr = deltaR(obj, x)
        if dr < drMin:
            ret = i
            drMin = dr
    return (ret, drMin)



def cosW(p1_tlv, p2_tlv):
    newp1, newp2 = ROOT.TLorentzVector(), ROOT.TLorentzVector()
    newp1.SetPtEtaPhiM(p1_tlv.Pt(), p1_tlv.Eta(), p1_tlv.Phi(), p1_tlv.M())
    newp2.SetPtEtaPhiM(p2_tlv.Pt(), p2_tlv.Eta(), p2_tlv.Phi(), p2_tlv.M())
    p12 = newp1.Px()*newp2.Px() + newp1.Py()*newp2.Py() + newp1.Pz()*newp2.Pz()
    p1_magn = sqrt(newp1.Px()*newp1.Px() + newp1.Py()*newp1.Py() + newp1.Pz()*newp1.Pz())
    p2_magn = sqrt(newp2.Px()*newp2.Px() + newp2.Py()*newp2.Py() + newp2.Pz()*newp2.Pz())
    angle = p12/(p1_magn*p2_magn)
    return angle

def CMFrame(v1_p4, v2_p4):
    v1, v2 = ROOT.TLorentzVector(), ROOT.TLorentzVector()
    v1.SetPtEtaPhiM(v1_p4.Pt(), v1_p4.Eta(), v1_p4.Phi(), v1_p4.M())
    v2.SetPtEtaPhiM(v2_p4.Pt(), v2_p4.Eta(), v2_p4.Phi(), v2_p4.M())
    v1.Boost(-v2.BoostVector())
    return v1

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
