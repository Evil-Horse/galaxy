from edtslib import pgnames

def get_sector_name(id64, coords):
    masscode = id64 & 0x07
    id64 >>= 3

    id64 >>= 7 - masscode
    sector_z = id64 & 0x7f
    id64 >>= 7

    id64 >>= 7 - masscode
    sector_y = id64 & 0x3f
    id64 >>= 6

    id64 >>= 7 - masscode
    sector_x = id64 & 0x7f
    id64 >>= 7

    offset = (sector_z << 14) + (sector_y << 7) + sector_x
    return pgnames.get_sector_name(offset)
