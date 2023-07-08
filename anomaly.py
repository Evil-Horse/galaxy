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
    def __init__(self):
        self.anomaly_file = open("anomaly", 'w')
        self.anomalies = 0

    def process(self, system):
        anomaly_reason = check(system)

        if anomaly_reason is not None:
            print(f"{system['name']}: {anomaly_reason}", file=self.anomaly_file)
            self.anomalies += 1

    def finalize(self):
        print(f"Anomalies: {self.anomalies:,}")
