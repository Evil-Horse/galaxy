#!/bin/env python3

from RegionMapData import regions, regionmap

x0 = -49985
y0 = -40985
z0 = -24105

def findRegion(x, y, z):
    px = int((x - x0) * 83 / 4096)
    pz = int((z - z0) * 83 / 4096)
    
    if px < 0 or pz < 0 or pz >= len(regionmap):
        return None
    else:
        row = regionmap[pz]
        rx = 0
        
        for rl, pv in row:
            if px < rx + rl:
                break
            else:
                rx += rl
        else:
            pv = 0

        if pv == 0:
            return None
        else:
            return (pv, regions[pv])

def findRegionForBoxel(id64):
    masscode = id64 & 7
    z = (((id64 >> 3) & (0x3FFF >> masscode)) << masscode) * 10 + z0
    y = (((id64 >> (17 - masscode)) & (0x1FFF >> masscode)) << masscode) * 10 + y0
    x = (((id64 >> (30 - masscode * 2)) & (0x3FFF >> masscode)) << masscode) * 10 + x0

    return {
        'x': x,
        'y': y,
        'z': z,
        'region': findRegion(x, y, z)
    }
