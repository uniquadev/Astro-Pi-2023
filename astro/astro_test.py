"""TESTS FOR ASTRO MAIN FILE
"""

# IMPORTS
import cv2
import shutil
import numpy as np
from pathlib import Path

# VARIABLES

WATER_THRESHOLD: int = 43
CLOUD_THRESHOLD: int = 100


# FUNCTIONS TO TEST
def is_useful(path) -> bool:
    """Checks to see if the image is over water/clouds
    so that we can decide to save it in our primary or alternative goal folder.
    The function takes the average light/darkness value of the image and compares
    it to a known threshold to determine if the image is over water/clouds.
    
    Return a boolean value indicating if the image is useful for our primary goal or not.
        
    Original source code at:
    https://github.com/SourishS17/Astro-Pi-2022/blob/db90b7ab1319c276c73f5d70addf7bae4b931a08/main.py#L100
    """
    
    image = cv2.imread(path).astype(np.float64)
    nir_val = np.average(image[:, :, 0]) # Average Near Infrared value

    if CLOUD_THRESHOLD > nir_val > WATER_THRESHOLD:
        return True
    else:
        return False

# ENTRY
if __name__ == "__main__":
    
    # Test for 'is_useful' function
    
    for index in range(1, 251):
        try:
            filename = f"./test_in/cslab3ogel_Files_RawData_raw_image_{index}.jpeg"

            if is_useful(filename):
                shutil.copy(filename, f"./test_out/primary/{index}.jpeg")
            else:
                shutil.copy(filename, f"./test_out/alternative/{index}.jpeg")
        except Exception as e:
            print(e)
            exit(0)
