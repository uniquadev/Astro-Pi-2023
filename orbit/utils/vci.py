# vci utils
# --------------------------------------
# IMPORTS
# --------------------------------------

from enum import Enum

# --------------------------------------
# LIB
# --------------------------------------

class VEGETATIONSTATE(Enum):
    NORMAL = 0
    LIGHT_DROUGHT = 1
    DROUGHT = 2
    SEVERE_DROUGHT = 3
    EXTREME_DROUGHT = 4

VCI_RANGES = [
    [40, 100, VEGETATIONSTATE.NORMAL],
    [30, 39, VEGETATIONSTATE.LIGHT_DROUGHT],
    [20, 29, VEGETATIONSTATE.DROUGHT],
    [10, 19, VEGETATIONSTATE.SEVERE_DROUGHT],
    [0, 9, VEGETATIONSTATE.EXTREME_DROUGHT]
]

def vci_classify(vci:int) -> VEGETATIONSTATE:
    assert 0 <= vci <= 100, f"VCI must be between 0 and 100, got {vci}"
    
    for range in VCI_RANGES:
        if vci >= range[0] and vci <= range[1]:
            return range[2]

# The VCI therefore compares the current Vegetation Index (VI) such as NDVI or Enhanced Vegetation Index (EVI) to the values observed
# in the same period in previous years within a specific pixel.
def vci_calculate(vi:int, vi_min:int, vi_max:int):
    return (vi - vi_min) / (vi_max - vi_min) * 100