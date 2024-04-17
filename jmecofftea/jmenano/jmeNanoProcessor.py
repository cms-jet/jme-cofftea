import copy
import coffea.processor as processor
import re
import numpy as np
from dynaconf import settings as cfg

from coffea.lumi_tools import LumiMask

from jmecofftea.hlt.definitions import hlt_accumulator, hlt_regions
from jmecofftea.jmenano.definitions import setup_candidates_for_jmenano, regions_for_jmenano

from jmecofftea.helpers import jmecofftea_path, recoil, metnomu, mask_and, mask_or, object_overlap
from jmecofftea.helpers.dataset import extract_year
from jmecofftea.helpers.paths import jmecofftea_path

class jmeNanoProcessor(processor.ProcessorABC):
    def __init__(self):
        self._accumulator = hlt_accumulator()
    
    @property
    def accumulator(self):
        return self._accumulator

    def _configure(self, df=None):
        cfg.DYNACONF_WORKS="merge_configs"
        cfg.MERGE_ENABLED_FOR_DYNACONF = True
        cfg.SETTINGS_FILE_FOR_DYNACONF = jmecofftea_path("config/hlt.yaml")

        if df:
            dataset = df['dataset']
            # Try to determine dataset year from dataset name.
            # If we can't, assign a -1. 
            try:
                self._year = extract_year(dataset)
            except RuntimeError:
                self._year = -1
            df["year"] = self._year
            
            # Use the default config for now
            cfg.ENV_FOR_DYNACONF = "default"
        else:
            cfg.ENV_FOR_DYNACONF = "default"
        
        cfg.reload()

    def process(self, df):
        if not df.size:
            return self.accumulator.identity()
        dataset = df['dataset']

        self._configure(df)

        ak4, muons = setup_candidates_for_jmenano(df, cfg)
    
        # Implement selections
        selection = processor.PackedSelection()
        pass_all = np.ones(df.size)==1
        selection.add('inclusive', pass_all)

        # Create mask for events with good lumis (using the golden JSON)
        # If no golden JSON is ready yet, do not apply any filtering
        if df["year"] in cfg.LUMI_MASKS:
            # Pick the correct golden JSON for this year
            json_path = jmecofftea_path(cfg.LUMI_MASKS[df["year"]])
            lumi_mask = LumiMask(json_path)(df["run"], df["luminosityBlock"])
        
        # Apply no lumi mask filtering
        else:
            lumi_mask = pass_all

        selection.add('lumi_mask', lumi_mask)

        # Dimuon pair for Z->mumu
        dimuons = muons[:,:2].distincts()

        # Two muons with opposite electrical charge
        opp_sign = dimuons.i0.pdgId * dimuons.i1.pdgId < 0
        selection.add("opp_sign", opp_sign.any())

        # At least two muons
        selection.add("two_muons", dimuons.counts>0)

        # Both muons within tracker
        central_muons = (dimuons.i0.abseta < 2.3) & (dimuons.i1.abseta < 2.3)
        selection.add("central_muons", central_muons.any())

        # Minimum pt cut on muons
        muon_pt_cut = (dimuons.i0.pt > 20) & (dimuons.i1.pt > 20)
        selection.add("muon_pt", muon_pt_cut.any())

        # Dimuon mass cut
        dimu_mass_cut = (dimuons.mass > 70) & (dimuons.mass < 110)
        selection.add("dimuon_mass", dimu_mass_cut.any())

        # Dimuon (Z) pt cut
        selection.add("dimuon_pt", (dimuons.pt > 15).any())

        # Leading jet in barrel, back-to-back with the Z boson
        leadak4_index = ak4.pt.argmax()
        ak4_in_barrel = ak4[leadak4_index].abseta < 1.3
        selection.add("lead_ak4_in_barrel", ak4_in_barrel.any())

        # Trigger cuts
        triggers = [
            "HLT_PFJet60",
            "HLT_PFJet140",
            "HLT_PFJet320",
            "HLT_PFJetFwd60",
            "HLT_PFJetFwd140",
            "HLT_PFJetFwd320",
        ]

        for trigger in triggers:
            selection.add(f"{trigger}_accepted", df[f"{trigger}_HLTPathAccept"])
            selection.add(f"{trigger}_wasrun",  ~df[f"{trigger}_HLTPathPrescaled"])

        # Reference IsoMu27 trigger
        selection.add("HLT_IsoMu27", df["HLT_IsoMu27_HLTPathAccept"])
        selection.add("HLT_IsoMu27_wasrun", ~df["HLT_IsoMu27_HLTPathPrescaled"])

        # Fill histograms for each region
        output = self.accumulator.identity()

        regions = regions_for_jmenano()

        for region, cuts in regions.items():
            mask = selection.all(*cuts)

            def ezfill(name, **kwargs):
                """Helper function to make filling easier."""
                output[name].fill(
                    region=region, 
                    dataset=dataset, 
                    **kwargs
                )

            # Kinematics of the leading jet
            ezfill("ak4_pt0",     jetpt=ak4[leadak4_index].pt[mask].flatten())
            ezfill("ak4_eta0",    jeteta=ak4[leadak4_index].eta[mask].flatten())
            ezfill("ak4_phi0",    jetphi=ak4[leadak4_index].phi[mask].flatten())

            # Z boson pt
            ezfill("z_pt",        pt=dimuons.pt[mask].flatten())

        return output

    def postprocess(self, accumulator):
        return accumulator