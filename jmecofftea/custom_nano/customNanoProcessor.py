import copy
import coffea.processor as processor
import re
import numpy as np
from dynaconf import settings as cfg

from coffea.lumi_tools import LumiMask

from jmecofftea.hlt.definitions import hlt_accumulator
from jmecofftea.helpers import jmecofftea_path, recoil, metnomu, mask_and, mask_or, object_overlap
from jmecofftea.helpers.dataset import extract_year
from jmecofftea.helpers.paths import jmecofftea_path

from jmecofftea.custom_nano.definitions import regionsForCustomNanoProcessor

class customNanoProcessor(processor.ProcessorABC):
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
            self._year = extract_year(dataset)
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

        # Implement selections
        selection = processor.PackedSelection()

        pass_all = np.ones(df.size)==1

        # Create mask for events with good lumis (using the golden JSON)
        # If no golden JSON is ready yet (i.e. early 2023 data, do not apply any filtering)
        if df["year"] in cfg.LUMI_MASKS:
            # Pick the correct golden JSON for this year
            json = jmecofftea_path(cfg.LUMI_MASKS[df["year"]])
            lumi_mask = LumiMask(json)(df["run"], df["luminosityBlock"])
        
        # If no golden JSON available, apply no filtering
        else:
            lumi_mask = pass_all

        selection.add("lumi_mask", lumi_mask)

        # Triggers of interest
        triggers = [
            # Single jet paths
            "HLT_PFJet60",
            "HLT_PFJet80",
            "HLT_PFJet140",
            "HLT_PFJet320",
            "HLT_PFJet500",
            # Forward single jet paths
            "HLT_PFJetFwd60",
            "HLT_PFJetFwd80",
            "HLT_PFJetFwd140",
            "HLT_PFJetFwd320",
            # HT paths
            "HLT_PFHT180",
            "HLT_PFHT350",
            "HLT_PFHT510",
            "HLT_PFHT780",
            "HLT_PFHT1050",
        ]

        for trigger in triggers:
            # The given path has been accepted by HLT
            selection.add(f"{trigger}_HLTPathAccept", df[f"{trigger}_HLTPathAccept"])

            # The given path was run (not prescaled)
            selection.add(f"{trigger}_HLTPathNotPrescaled", ~df[f"{trigger}_HLTPathPrescaled"])

            # The underlying L1 seed was run (not prescaled)
            selection.add(f"{trigger}_L1TSeedNotPrescaled", ~df[f"{trigger}_L1TSeedPrescaledOrMasked"])

            # The L1 seed passed
            selection.add(f"{trigger}_L1TSeedAccept", df[f"{trigger}_L1TSeedAccept"])

        output = self.accumulator.identity()

        # Loop over regions for each trigger and fill histograms
        regions = regionsForCustomNanoProcessor(triggers)

        for region, cuts in regions.items():
            # Get the selection mask for this region
            mask = selection.all(*cuts)

            def ezfill(name, **kwargs):
                """Helper function to make filling easier."""
                output[name].fill(
                    region=region, 
                    dataset=dataset, 
                    **kwargs
                    )

            # Fill the histograms
            ezfill("ak4_pt0",  jetpt=df["leadingJet_pt"][mask])
            ezfill("ht",       ht=df["ht"][mask])
            ezfill("met",      met=df["met"][mask])

        return output

    def postprocess(self, accumulator):
        return accumulator