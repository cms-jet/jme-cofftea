import re
import copy

import coffea.processor as processor
import numpy as np

def regionsForCustomNanoProcessor(triggers):
    """
    Analysis regions for the customNanoProcessor.
    """
    regions = {}

    # Common cuts: Just the lumi mask based on golden JSON.
    common_cuts = ["lumi_mask"]

    # Create numerator and denominator regions for each trigger of interest
    for trigger in triggers:
        regions[f"{trigger}_num"] = common_cuts + [f"{trigger}_HLTPathNotPrescaled", f"{trigger}_HLTPathAccept"]
        regions[f"{trigger}_den"] = common_cuts + [f"{trigger}_HLTPathNotPrescaled"]

    return regions