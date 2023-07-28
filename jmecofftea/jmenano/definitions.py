import re
import copy

import coffea.processor as processor
import numpy as np

from coffea.analysis_objects import JaggedCandidateArray

def setup_candidates_for_jmenano(df, cfg):
    """
    Set up physics candidates as JaggedCandidateArray data structures, 
    from the given dataframe.
    """
    ak4 = JaggedCandidateArray.candidatesfromcounts(
        df["offlineAK4PFPuppiJetsCorrected_multiplicity"],
        pt=df["offlineAK4PFPuppiJetsCorrected_pt"],
        eta=df["offlineAK4PFPuppiJetsCorrected_eta"],
        abseta=np.abs(df["offlineAK4PFPuppiJetsCorrected_eta"]),
        phi=df["offlineAK4PFPuppiJetsCorrected_phi"],
        mass=df["offlineAK4PFPuppiJetsCorrected_mass"],
    )

    muons = JaggedCandidateArray.candidatesfromcounts(
        df["offlineMuons_multiplicity"],
        pt=df["offlineMuons_pt"],
        eta=df["offlineMuons_eta"],
        abseta=np.abs(df["offlineMuons_eta"]),
        phi=df["offlineMuons_phi"],
        mass=df["offlineMuons_pt"] * 0.,
        pdgId=df["offlineMuons_pdgId"],
        dxy=df["offlineMuons_dxyPV"],
        dz=df["offlineMuons_dzPV"],
    )

    return ak4, muons


def regions_for_jmenano():
    regions_and_cuts = {}

    # Common cuts for numerator and denominator regions
    # These implement the Z(mu mu) + jet selection
    common_cuts = [
        "HLT_IsoMu27", 
        "HLT_IsoMu27_wasrun", 
        "opp_sign",
        "two_muons",
        "central_muons",
        "muon_pt",
        "dimuon_mass",
        "lead_ak4_in_barrel",
    ]

    # Triggers of interest
    triggers = [
        "HLT_PFJet60",
        "HLT_PFJet140",
        "HLT_PFJet320",
        "HLT_PFJetFwd60",
        "HLT_PFJetFwd140",
        "HLT_PFJetFwd320",
    ]

    for trigger in triggers:
        regions_and_cuts[f"{trigger}_num"] = common_cuts + [f"{trigger}_wasrun", f"{trigger}_accepted"]
        regions_and_cuts[f"{trigger}_den"] = common_cuts + [f"{trigger}_wasrun"]

    return regions_and_cuts