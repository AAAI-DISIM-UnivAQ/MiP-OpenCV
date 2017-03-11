import mippy
import time
import sys


mip = mippy.MIP('192.168.43.221')

while(True):
    sensing = mip.sense()
    decision = mip.think(sensing[0],sensing[1])
    mip.act(decision)
    


