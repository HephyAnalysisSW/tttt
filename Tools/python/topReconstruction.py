import ROOT
import copy
import numpy as np
import random
from math import isnan, cos, sin, sinh, sqrt

from Analysis.Tools.helpers         import deltaR

from tttt.Tools.genPartSelectionTools import getGenFirstCopy, getGenLastCopy, getParents, getTopMother, getMatching, closestdR, CMFrame, cosW

hadTopVars_       = ['pt/F','phi/F','eta/F','mass/F','TopTruth/I','genMass/F','bJetCMPt/F','LdgJetCMPt/F','SubldgJetCMPt/F',
                    'softDrop_n2/F','bJetMass/F','diJetMass/F','LdgJetMass/F','SubldgJetMass/F','bJetLdgJetMass/F','bJetSubldgJetMass/F',
                    'bJetQGL/F','LdgJetQGL/F','SubldgJetQGL/F','DEtaDijetwithBJet/F','diJetPtOverSumPt/F',
                    'LdgJetDeltaPtOverSumPt/F','SubldgJetDeltaPtOverSumPt/F','bJetDeltaPtOverSumPt/F',
                    'cosW_Jet1Jet2/F','cosW_Jet1BJet/F','cosW_Jet2BJet/F','trijetPtDR/F','dijetPtDR/F',
                    'bJetBdisc/F','LdgJetBdisc/F','SubldgJetBdisc/F','bJetCvsL/F','LdgJetCvsL/F','SubldgJetCvsL/F','bJetCvsB/F','LdgJetCvsB/F','SubldgJetCvsL/F', 'index0/I', 'index1/I', 'index2/I', 'genMotherIdx0/I', 'genMotherIdx1/I', 'genMotherIdx2/I', 'pt1/F', 'pt2/F', 'pt3/F']
hadTopVars_ += ['DNNScore/F']


def isMatching(store_partonFromTop, bHadron_jets, lightParton_jets):
    dRmatch_b, dRmatch_l, index_lJets, index_bJets = [], [], [], []
    for idxg, g in enumerate(store_partonFromTop):
        lst_b, lst_l = [], []
        dR_min = 0.4
        for idxb, b in enumerate(bHadron_jets):
            if idxb in index_bJets:
                continue
            dr = deltaR(g, b)
            if dr < dR_min:
                lst_b.append([dr, g, b])
                index_bJets.append(idxb)
        if len(lst_b) > 0:
            lst_b = np.array(lst_b)
            minIndexB = np.argmin(lst_b[:, 0])
            b_ = lst_b[minIndexB, 2]
            b_['genMotherIdx'] = lst_b[minIndexB, 1]['motherIdx']
            b_['pdgId'] = lst_b[minIndexB, 1]['pdgId']
            b_['genMass'] = lst_b[minIndexB, 1]['mass']
            b_['genEta'] = lst_b[minIndexB, 1]['eta']
            b_['genPhi'] = lst_b[minIndexB, 1]['phi']
            b_['genPt'] = lst_b[minIndexB, 1]['pt']
            b_['isMatched'] = True
            dRmatch_b.append(b_)
        for idxl, l in enumerate(lightParton_jets):
            if idxl in index_lJets:
                continue
            dr = deltaR(g, l)
            if dr < dR_min:
                lst_l.append([dr, g, l])
                index_lJets.append(idxl)
        if len(lst_l) > 0:
            lst_l = np.array(lst_l)
            minIndex = np.argmin(lst_l[:, 0])
            l_ = lst_l[minIndex, 2]
            l_['genMotherIdx'] = lst_l[minIndex, 1]['motherIdx']
            l_['pdgId'] = lst_l[minIndex, 1]['pdgId']
            l_['genMass'] = lst_l[minIndex, 1]['mass']
            l_['genEta'] = lst_l[minIndex, 1]['eta']
            l_['genPhi'] = lst_l[minIndex, 1]['phi']
            l_['genPt'] = lst_l[minIndex, 1]['pt']
            l_['isMatched'] = True
            dRmatch_l.append(l_)
    return dRmatch_b, dRmatch_l



def assignTruthMatched(dRmatch_b, dRmatch_l):
    topTruth_value = -1
    trijet = []

    for i, bmatch in enumerate(dRmatch_b):
        for j, l1match in enumerate(dRmatch_l):
            for k, l2match in enumerate(dRmatch_l):
                if l1match != l2match and j != k and k > j:
                    indices_list = [bmatch['genMotherIdx'], l1match['genMotherIdx'], l2match['genMotherIdx']]
                    index0 = bmatch['index']
                    index1 = l1match['index']
                    index2 = l2match['index']

                    if indices_list[0] == indices_list[1] == indices_list[2]:
                        # print("mother idxs", indices_list)
                        # print("indices from jet", index0, index1, index2)
                        topTruth_value = 1  # All equal
                    else:
                        topTruth_value = 0  # Other cases
                        # print("mother idxs", indices_list)
                        # print("indices from jet", index0, index1, index2)

                    trijet.append([
                    dict({'TopTruth': topTruth_value}.items() + {'index': index0}.items() + {'genMotherIdx': bmatch['genMotherIdx']}.items() + bmatch.items()),
                    dict({'TopTruth': topTruth_value}.items() + {'index': index1}.items() + {'genMotherIdx': l1match['genMotherIdx']}.items() + l1match.items()),
                    dict({'TopTruth': topTruth_value}.items() + {'index': index2}.items() + {'genMotherIdx': l2match['genMotherIdx']}.items() + l2match.items())
                    ])
    return trijet


def topReco(trijet, isSignal=False):
    tlorentz_vectors = []
    W_vectors = []
    for i, triplet in enumerate(trijet):
        if len(triplet)<3 : continue
        dR_lj = deltaR(triplet[1], triplet[2])
        pt_lj1, pt_lj2 = triplet[1]['pt'], triplet[2]['pt']
        lJet, sublJet = None, None
        if pt_lj1 >= pt_lj2:
            lJet = triplet[1]
            sublJet = triplet[2]
            # print(triplet[0]['index'], triplet[0]['pt'], lJet['index'], lJet['pt'], sublJet['index'], sublJet['pt'])
        else:
            lJet = triplet[2]
            sublJet = triplet[1]
            # print(triplet[0]['index'], triplet[0]['pt'], lJet['index'], lJet['pt'], sublJet['index'], sublJet['pt'])

        tlv1, tlv2, tlv3 = ROOT.TLorentzVector(), ROOT.TLorentzVector(), ROOT.TLorentzVector()
        tlv1.SetPtEtaPhiM(triplet[0]['pt'], triplet[0]['eta'], triplet[0]['phi'], triplet[0]['mass'])
        tlv2.SetPtEtaPhiM(lJet['pt'], lJet['eta'], lJet['phi'], lJet['mass'])
        tlv3.SetPtEtaPhiM(sublJet['pt'], sublJet['eta'], sublJet['phi'], sublJet['mass'])

        softDrop_n2 = min(tlv2.Pt(), tlv3.Pt()) / ( (tlv2.Pt() + tlv3.Pt()) * dR_lj * dR_lj)
        if not isSignal==True:
            pass
        else:
            genv1, genv2, genv3 = ROOT.TLorentzVector(), ROOT.TLorentzVector(), ROOT.TLorentzVector()
            genv1.SetPtEtaPhiM(triplet[0]['genPt'], triplet[0]['genEta'], triplet[0]['genPhi'], triplet[0]['genMass'])
            genv2.SetPtEtaPhiM(lJet['genPt'], lJet['genEta'], lJet['genPhi'], lJet['genMass'])
            genv3.SetPtEtaPhiM(sublJet['genPt'], sublJet['genEta'], sublJet['genPhi'], sublJet['genMass'])
            genTotal = genv1 + genv2 + genv3
            genW_tlv = genv2 + genv3
        #Top Hadr
        total_tlv = tlv1 + tlv2 + tlv3
        #W boson
        W_tlv = tlv2 + tlv3
        bjetP4_topCM  = CMFrame(tlv1, total_tlv)
        jet1P4_topCM  = CMFrame(tlv2, total_tlv)
        jet2P4_topCM  = CMFrame(tlv3, total_tlv)
        trijetPtDR = total_tlv.Pt()*sqrt((W_tlv.Phi()-tlv1.Phi())**2 + (W_tlv.Eta()-tlv1.Eta())**2)
        dijetPtDR = total_tlv.Pt()*sqrt((tlv2.Phi()-tlv3.Phi())**2 + (tlv2.Eta()-tlv3.Eta())**2)
        varsTop ={'pt': total_tlv.Pt(), 'eta': total_tlv.Eta(), 'phi': total_tlv.Phi(),
                                 'mass': total_tlv.M(), 'TopTruth': 0, 'genMass': 0.,
                                 'bJetCMPt':bjetP4_topCM.Pt(), 'LdgJetCMPt':jet1P4_topCM.Pt(), 'SubldgJetCMPt':jet2P4_topCM.Pt(),
                                 'softDrop_n2': softDrop_n2, 'bJetMass': tlv1.M(), 'diJetMass': W_tlv.M(),
                                 'LdgJetMass': tlv2.M(), 'SubldgJetMass': tlv3.M(),
                                 'bJetLdgJetMass': (tlv1 + tlv2).M(), 'bJetSubldgJetMass': (tlv1 + tlv3).M(),
                                 'bJetQGL': triplet[0]['qgl'], 'LdgJetQGL': lJet['qgl'], 'SubldgJetQGL':sublJet['qgl'],
                                 'DEtaDijetwithBJet': abs(W_tlv.Eta()-tlv1.Eta()),
                                 'diJetPtOverSumPt': (W_tlv.Pt()/(tlv2.Pt()+tlv3.Pt())),
                                 'LdgJetDeltaPtOverSumPt': abs(tlv2.Pt() - total_tlv.Pt())/(tlv2.Pt() + total_tlv.Pt()),
                                 'SubldgJetDeltaPtOverSumPt': abs(tlv3.Pt() - total_tlv.Pt())/(tlv3.Pt() + total_tlv.Pt()),
                                 'bJetDeltaPtOverSumPt': abs(tlv1.Pt() - total_tlv.Pt())/(tlv1.Pt() + total_tlv.Pt()),
                                 'cosW_Jet1Jet2': cosW(jet1P4_topCM, jet2P4_topCM), 'cosW_Jet1BJet':cosW(jet1P4_topCM, bjetP4_topCM),
                                 'cosW_Jet2BJet': cosW(jet2P4_topCM, bjetP4_topCM),
                                 'bJetBdisc': triplet[0]['btagDeepFlavB'], 'LdgJetBdisc': lJet['btagDeepFlavB'], 'SubldgJetBdisc': sublJet['btagDeepFlavB'],
                                 'bJetCvsL': triplet[0]['btagDeepFlavCvL'], 'LdgJetCvsL': lJet['btagDeepFlavCvL'], 'SubldgJetCvsL': sublJet['btagDeepFlavCvL'],
                                 'bJetCvsB': triplet[0]['btagDeepFlavCvB'], 'LdgJetCvsB': lJet['btagDeepFlavCvB'], 'SubldgJetCvsB': sublJet['btagDeepFlavCvB'],
                                 'trijetPtDR': trijetPtDR, 'dijetPtDR':dijetPtDR, 'pt1': triplet[0]['pt'], 'pt2': lJet['pt'], 'pt3': sublJet['pt']
                                 }
        if isSignal==True:
            varsTop['TopTruth'] = triplet[0]['TopTruth']
            varsTop['index0'] = triplet[0]['index']
            varsTop['genMotherIdx0'] = triplet[0]['genMotherIdx']
            pt_lj1, pt_lj2 = triplet[1]['pt'], triplet[2]['pt']
            lJet, sublJet = None, None
            if pt_lj1 >= pt_lj2:
                lJet = triplet[1]
                sublJet = triplet[2]
                varsTop['index1'] = lJet['index']
                varsTop['index2'] = sublJet['index']
                varsTop['genMotherIdx1'] = lJet['genMotherIdx']
                varsTop['genMotherIdx2'] = sublJet['genMotherIdx']
            else:
                lJet = triplet[2]
                sublJet = triplet[1]
                varsTop['index1'] = lJet['index']
                varsTop['index2'] = sublJet['index']
                varsTop['genMotherIdx2'] = lJet['genMotherIdx']
                varsTop['genMotherIdx1'] = sublJet['genMotherIdx']
            varsTop['genMass'] = genTotal.M()

        tlorentz_vectors.append(varsTop)

    return tlorentz_vectors
