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
        
        # Cuts both in num and denom to ensure that the path was not prescaled by either L1 algo or HLT.
        prescale_cuts = [f"{trigger}_HLTPathNotPrescaled", f"{trigger}_L1TSeedNotPrescaled"]

        l1_cuts = [f"{trigger}_L1TSeedAccept"]

        regions[f"{trigger}_num"] = common_cuts + prescale_cuts + l1_cuts + [f"{trigger}_HLTPathAccept"]
        regions[f"{trigger}_den"] = common_cuts + prescale_cuts + l1_cuts 

    return regions