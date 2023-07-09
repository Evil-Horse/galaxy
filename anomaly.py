import utils

def check(system):
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
        return f"is not fully scanned ({len(system['bodies']) - barycenters}/{system['bodyCount']})"

    return None

class Anomalies:
    def __init__(self, fav):
        self.anomaly_file = open("anomaly", 'w')
        self.anomalies = utils.counter_init(fav)
        self.fav = fav

    def process(self, system):
        anomaly_reason = check(system)

        if anomaly_reason is not None:
            print(f"{system['name']}: {anomaly_reason}", file=self.anomaly_file)

            utils.counter_increment(self.anomalies, system['sector'], self.fav)

    def finalize(self, sector = None):
        if sector is None:
            anomalies = self.anomalies['galaxy']
        else:
            anomalies = self.anomalies[sector]
        print(f"Anomalies: {anomalies:,}")
