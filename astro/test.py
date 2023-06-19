"""
    TESTS FOR ASTRO MAIN FILE
    TO RUN ON RASPBERRY PI
"""

# IMPORTS
from pathlib import Path  # Path utilities
from picamera import PiCamera  # Take images
from main import is_usefull, camera


def start_stream():
    camera.resolution = (150, 150)
    camera.start_preview()
    camera.start_recording('video.h264')

# ENTRY
if __name__ == "__main__":
    pass