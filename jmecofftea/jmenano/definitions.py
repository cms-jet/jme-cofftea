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
