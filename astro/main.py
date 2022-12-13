"""MAIN FILE

GENERAL DESCRIPTION
    This script will run aboard the ISS taking pictures of the Earth surface depending if there is enough light or free storage.
    The program will also save for each image the ISS location at the time it was taken, and the time itself as metadata.
    The script will automatically stop its execution to not exceed the maximum allowed runtime (3 hours).

EXCEPTION HANDLING
    Requirements:
        - The program runs without errors and does not raise any unhandled exceptions.

    Exceptions are handled by using a try-except statement and logged to the log file.
    The occurence of exceptions during runtime is made obvious by increasing the image counter by a value of 2 instead of 1.
    Also the execution of the program is suspended for 1 second to ensure that the Astro-Pi computer fully recovers from the exception.

TIME MANAGEMENT
    Requirements:
        - The program monitors its running time and stops after 3 hours have elapsed.

    The script will automatically stop before the 3 hours of maximum allowed runtime have passed.
    This is accomplished through the datetime library.
    The maximum allowed runtime is set to 177 minutes, 3 minutes less than 180, to ensure that the requirement is satisfied in case of any delay.

STORAGE MANAGEMENT
    Requirements:
        - The program only saves data in the folder where the main Python file is, as described in the Phase 2 guide 
        (i.e. using the special __file__ variable), and that no absolute path names are used.

        - The program does not use more than 3GB of space to store data.

        - Any files that the program creates have names that only include letters, numbers, dots (.), dashes (-), or underscores (_).
    
    The program only saves data in the folder where the main Python file is by resolving its path name using the special __file__ variable and no absolute path names are used.

    To ensure that the second requirement is satisfied if the maximum storage limit of 3GB is exceeded the program will stop its execution.
    This is accomplished through the 'astro_memory' variable (representing the filled storage) that is initialized with a value of 30e6 (the maximum size of the log file in bytes) and updated every time a photo is taken.

    The files created by the program have names that satisfy the third requirement.

CODE STYLE AND DOCUMENTATION
    Requirements:
        - The program is documented and easy to understand, and that there is no attempt to hide or obfuscate what a piece of code does.

    In order to satisfy this requirement we decided to follow the PEP 8 style guide for Python code.
"""

# --------------------------------------
# IMPORTS
# --------------------------------------

import cv2  # Image processing
import exif  # Embed GPS and time data into any images

import numpy as np  # Array manipulation

from pathlib import Path  # Path utilities
from picamera import PiCamera  # Take images
from skyfield.timelib import Timescale
from skyfield.api import load  # Load timescale data
from time import sleep  # Sleep function to supspend the execution of the program

from datetime import datetime, timedelta  # Time recognition
from logzero import logger, logfile  # Debug purposes
from orbit import ISS, ephemeris  # Import ISS and load the JPL ephemeris DE421 (covers 1900-2050).

# --------------------------------------
# CONSTANTS
# --------------------------------------

# How long to run the program for
RUN_TIME: timedelta = timedelta(minutes=177)

# --------------------------------------
# VARIABLES
# --------------------------------------

# images counters
image_counter: int = 0
# 30 MB used by the log file
astro_memory: float = 30e6

# Defining initial time variables to know when to stop the program
start_time: datetime = datetime.now()
now_time: datetime = datetime.now()

# Resolve absolute path to the current code directory
base_folder: Path = Path(__file__).parent.resolve()


# Define output folder for images
out_folder = base_folder / "out"
out_folder.mkdir(parents=True, exist_ok=True)


# Timescale object for building and converting time
timescale: Timescale = load.timescale()

# Set log file
logfile(base_folder / "astro.log", backupCount=0, maxBytes=30e6)

# Camera settings - max res for more precise indices
camera: PiCamera = PiCamera()
camera.resolution = (4056, 3040)

# --------------------------------------
# FUNCTIONS
# --------------------------------------

def light_level() -> bool:
    """Check if the light level is sufficient for the camera to take a picture.

    Return a boolean value indicating if the light level is sufficient or not.
    """

    curr = timescale.now()

    if ISS.at(curr).is_sunlit(ephemeris):
        return True
    else:
        return False


def convert_cords(angle) -> tuple[bool, str]:
    """Convert a `skyfield` Angle to an EXIF-appropriate
    representation (positive rationals)
    e.g. 98° 34' 58.7 to "98/1,34/1,587/10"

    Return a tuple containing a boolean and the converted angle,
    with the boolean indicating if the angle is negative.
    """

    sign, degrees, minutes, seconds = angle.signed_dms()
    exif_angle = f'{degrees:.0f}/1,{minutes:.0f}/1,{seconds*10:.0f}/10'
    
    return sign < 0, exif_angle


def convert_time(time: datetime) -> str:
    """Convert a `datetime` object to an EXIF-appropriate representation (string)
    e.g. 2022-11-27 14:27:51.098019 to 2022:11:27 14:27:51

    Return a string containing the converted date/time.
    """

    return time.strftime("%Y:%m:%d %H:%M:%S")


def add_metadata(lat: str, latr: str, long: str, longr: str, t: str) -> None:
    """Add the metadata tags to the camera
    so that we know the location and can identify the
    area on a map when we analyse the images on Earth.

    Time will also be saved for further analysis in Phase 4.
    """
    
    global camera
    
    # Location
    camera.exif_tags["GPS.GPSLatitude"] = lat
    camera.exif_tags["GPS.GPSLatitudeRef"] = latr
    camera.exif_tags["GPS.GPSLongitude"] = long
    camera.exif_tags["GPS.GPSLongitudeRef"] = longr

    # Time
    camera.exif_tags["DateTimeOriginal"] = t


def take_image() -> Path:
    """Take a picture, write metadata and return the path to the image

    Return the path to the image taken as a Path object.
    """
  
    global image_counter
    global now_time
  
    # Define output file
    out_file = out_folder / f"img_{image_counter:04d}.jpg"

    # Get location
    location = ISS.coordinates()
    south, exif_lat = convert_cords(location.latitude)
    west, exif_long = convert_cords(location.longitude)
    
    # Get time
    t = convert_time(now_time)

    # Add location and time 
    add_metadata(
      exif_lat,
      "S" if south else "N",
      exif_long,
      "W" if west else "E",
      t
    )

    # Take image
    camera.capture(str(out_file))

    return out_file


# --------------------------------------
# ENTRY
# --------------------------------------

if __name__ == "__main__":

    logger.info("Started")
    
    # Run until the program exceeds the specified RUN_TIME
    while now_time - start_time < RUN_TIME:

        # Update the current time
        now_time: datetime = datetime.now()

        # Check storage limit to not exceed 3 GB
        if astro_memory >= 2.7e9:
            logger.error(f"Storage limit reached with {image_counter} images")
            break

        # Ensure errors don't break anything
        try:
            # Check if the light level is sufficient
            if light_level() == False:
                # Suspend the program execution
                sleep(2)
                continue

            # Take picture
            path: Path = take_image()

            # Increase image counter
            image_counter += 1
            
            # Update the astro_memory variable representing the filled storage
            astro_memory += path.stat().st_size

        except Exception as e:
            # Log the exception/error to the log file
            logger.exception(e)
            
            # Suspend the program execution to recover from the exception/error
            sleep(1)
            
            # Make the occurence of the exception/error obvious
            image_counter += 2

    logger.info(f"execution completed with {image_counter} images (づ ᴗ _ᴗ)づ")

    # Ensure the camera is correctly closed
    camera.close()

    """
     ____  _                ____             
    |  _ \(_)__________ _  |  _ \  _____   __
    | |_) | |_  /_  / _` | | | | |/ _ \ \ / /
    |  __/| |/ / / / (_| | | |_| |  __/\ V / 
    |_|   |_/___/___\__,_| |____/ \___| \_/  

    """
