def process(system):
    if not "bodyCount" in system:
        return "Body count unknown"

    barycenters = 0
    for body in system["bodies"]:
        if body["type"] == "Barycentre":
            barycenters += 1

        # stars first
        if not "solarMasses" in body:
            # star mass unknown, skip system
            if body["type"] == "Star":
                return "Star mass in unknown"

        if not "earthMasses" in body:
            if body["type"] == "Planet":
                return "Planet mass in unknown"

    if system["bodyCount"] + barycenters != len(system["bodies"]):
        return "is not fully scanned (%s/%s)" % (len(system["bodies"]) - barycenters, system["bodyCount"])

    return None
