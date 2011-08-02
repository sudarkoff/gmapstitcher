"""
    Stitch Google Map tiles together to create a larger map.
    $Id: GMapStitcher.py 54 2006-06-21 06:36:54Z george $
    
    THE SCRIPT IS INTENDED FOR EDUCATIONAL PURPOSES ONLY.
    BE ADVISED THAT RUNNING AUTOMATED QUERIES WITHOUT PRIOR EXPRESS 
    PERMISSION FROM GOOGLE VIOLATES THEIR TERMS OF SERVICE AND COULD 
    RESULT IN LOCK OUT AND POSSIBLY FURTHER LEGAL ACTIONS.

    To learn more about Python visit http://www.python.org/
    
    Email to George Sudarkoff <george@sudarkoff.com> if you have any
    questions regarding this script. Or visit http://george.sudarkoff.com
    and search for "stitcher".

    This script takes two parameters:
        (1) encoded index of the center tile of the interested region
        (2) size of the resulting map in tiles
    
    $ python GMapStitcher.py tqtrsrqt 3

"""

import sys
import os
import urllib
import Image
import time
import math
import random

class Tile:
    def __init__(self, index):
        self.index = index
        (self.X, self.Y) = self.decode(index)

    def decode(self, index):
        """Decode the tile's index"""
        self.zoom = power = len(index) - 1
        (x, y) = (0, 0)
        for letter in index[:]:
            if letter == 'r' or letter == 's':
                x += 2**power
            if letter == 't' or letter == 's':
                y += 2**power
            power -= 1
        return (x, y)

    def encode(self, dx, dy):
        """Encode the tile's index"""
        binary = lambda n: n > 0 and [n & 1] + binary(n >> 1) or []
        binX = binary(self.X + dx)
        binY = binary(self.Y + dy)

        digit = lambda d, i: i < len(d) and d[i] or 0
        code = {0:'q', 1:'r', 2:'t', 3:'s'}
        index = ""
        for i in range(self.zoom + 1):
            index = code[digit(binX, i) + (digit(binY, i) << 1)] + index;
        return index
    
    def retrieve(self, dx = 0, dy = 0):
        """Download the tile if needed"""
        index = ""
        if dx == 0 and dy == 0:
            index = self.index
        else:
            index = self.encode(dx, dy)
        url = "http://kh%s.google.com/kh?n=404&v=6&t=%s" % (random.randint(0, 3), index)
        filename = "tile_%s.gif" % index
        # Do not download the tile if we already have it
        if not os._exists(filename):
            urllib.urlretrieve(url, filename)
            time.sleep(1)
        return index

if __name__ == "__main__":
    # center tile
    if len(sys.argv) > 1 and sys.argv[1] != "":
        centerTileIndex = sys.argv[1]
    else:
        centerTileIndex = "tqtrsrqt"
        
    # number of tiles to download
    if len(sys.argv) > 2 and sys.argv[2] != "":
        (width, height) = (int(sys.argv[2]), int(sys.argv[2]))
    else:
        (width, height) = (5, 5)

    # retrieve center tile
    tile = Tile(centerTileIndex)
    tile.retrieve()

    # initialize resulting map image
    (xsize, ysize) = Image.open("tile_%s.gif" % centerTileIndex).size
    (map_xsize, map_ysize) = (xsize * width, ysize * height)
    image = Image.new("RGB", (map_xsize, map_ysize))

    # retrieve the tiles and paste them into the resulting map image
    x_range = range(-(width/2), width/2 + 1)   # range is always odd for the center
    y_range = range(-(height/2), height/2 + 1) # tile to be in the center of the map
    for dx in x_range:
        for dy in y_range:
            tileIndex = tile.retrieve(dx, dy)
            pastePos = (map_xsize / 2 + (dx-1) * xsize + xsize / 2, 
                        map_ysize / 2 + (dy-1) * ysize + ysize / 2)
            image.paste(Image.open("tile_%s.gif" % tileIndex), pastePos)
            
    # save the resulting map image
    image.save("map_%s_%s.gif" % (centerTileIndex, width))
    print "Done."
    