import sys
from os import path
from exif import Image

def decimal_coords(coords, ref):
    decimal_degrees = coords[0] + coords[1] / 60 + coords[2] / 3600
    if ref == "S" or ref == "W":
        decimal_degrees = -decimal_degrees
    return decimal_degrees

def main(argc : int, argv : list[str]):
    # check arguments
    if argc != 2:
        print("Usage: python3 extract.py <path/to/image>")
        return
    
    # check if the file exists
    if(not path.exists(argv[1])):
        print("File does not exist")
        return
    
    # extract exif data
    with open(argv[1], 'rb') as src:
        img = Image(src)

    print(f'Latitude: {decimal_coords(img.gps_latitude, img.gps_latitude_ref)}')
    print(f'Longitude: {decimal_coords(img.gps_longitude, img.gps_longitude_ref)}')


if __name__ == '__main__':
    main(len(sys.argv), sys.argv)