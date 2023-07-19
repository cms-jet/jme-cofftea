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
        df["hltAK4PFJetsCorrected_pt"].counts,
        pt=df["hltAK4PFJetsCorrected_pt"].flatten(),
        eta=df["hltAK4PFJetsCorrected_eta"].flatten(),
        abseta=np.abs(df["hltAK4PFJetsCorrected_eta"].flatten()),
        phi=df["hltAK4PFJetsCorrected_phi"].flatten(),
        mass=df["hltAK4PFJetsCorrected_mass"].flatten(),
    )

    muons = JaggedCandidateArray.candidatesfromcounts(
        df["offlineMuons_pt"].counts,
        pt=df["offlineMuons_pt"].flatten(),
        eta=df["offlineMuons_eta"].flatten(),
        abseta=np.abs(df["offlineMuons_eta"].flatten()),
        phi=df["offlineMuons_phi"].flatten(),
        mass=df["offlineMuons_mass"].flatten(),
        pdgId=df["offlineMuons_pdgId"].flatten(),
        vx=df["offlineMuons_vx"].flatten(),
        vy=df["offlineMuons_vy"].flatten(),
        vz=df["offlineMuons_vz"].flatten(),
    )

    return ak4, muons


def regions_for_jmenano():
    regions_and_cuts = {}

    # Common cuts for numerator and denominator regions
    # These implement the Z(mu mu) + jet selection
    common_cuts = [
        "HLT_IsoMu27", 
        "opp_sign",
        "two_muons",
        "central_muons",
        "muon_pt",
        "dimuon_mass",
        "lead_ak4_in_barrel",
    ]

    regions_and_cuts["HLT_PFJet60_num"] = common_cuts + ["HLT_PFJet60_wasrun", "HLT_PFJet60"]
    regions_and_cuts["HLT_PFJet60_den"] = common_cuts + ["HLT_PFJet60_wasrun"]

    return regions_and_cuts