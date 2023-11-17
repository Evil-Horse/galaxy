import utils

def check(system):
    string_list = []

    barycenters = 0
    for body in system["bodies"]:
        if body["type"] == "Barycentre":
            barycenters += 1

        # stars first
        if not "solarMasses" in body:
            # star mass unknown, skip system
            if body["type"] == "Star":
                string_list.append("Star mass is unknown")

        if not "earthMasses" in body:
            if body["type"] == "Planet":
                string_list.append("Planet mass is unknown")

    if not "bodyCount" in system:
        string_list.append("Body count unknown")
    elif system["bodyCount"] + barycenters != len(system["bodies"]):
        string_list.append(f"is not fully scanned ({len(system['bodies']) - barycenters}/{system['bodyCount']})")

    # build reason string
    separator = "\n" + " " * (2 + len(system["name"])) #TODO make alignment
    string_joined = separator.join(string_list)
    if string_joined == "":
        return None

    return string_joined

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

    def finalize(self, data, sector = None):
        key = 'galaxy' if sector is None else sector

        anomalies = self.anomalies[key]

        subdata = data[key]
        subdata["anomalies"] = anomalies
