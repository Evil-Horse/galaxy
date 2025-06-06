import utils

def enum_to_string(name, reason):
    string_list = []
    if reason & 0x01:
        string_list.append("Star mass is unknown")
    if reason & 0x02:
        string_list.append("Planet mass is unknown")
    if reason & 0x04:
        string_list.append("Body count unknown")
    if reason & 0x08:
        string_list.append("Is not fully scanned")

    # build reason string
    separator = "\n" + " " * (2 + len(name)) #TODO make alignment
    string_joined = separator.join(string_list)

    return string_joined

def check(system):
    reasons = 0

    barycenters = 0
    for body in system["bodies"]:
        if body["type"] == "Barycentre":
            barycenters += 1

        # stars first
        if not "solarMasses" in body:
            # star mass unknown, skip system
            if body["type"] == "Star":
                reasons |= 0x01
        if not "earthMasses" in body:
            if body["type"] == "Planet":
                reasons |= 0x02

    if not "bodyCount" in system:
        reasons |= 0x04
    elif system["bodyCount"] + barycenters != len(system["bodies"]):
        reasons |= 0x08

    return reasons

class Anomalies:
    def __init__(self, fav, cursor):
        self.fav = fav
        self.cursor = cursor

    def process(self, system):
        anomaly_reason = check(system)

        if anomaly_reason is not None:
            self.cursor.execute('''
                UPDATE systems SET anomalies = ? WHERE name = ?
            ''', (anomaly_reason, system["name"]))

    def finalize(self, data, sector = None):
        if sector is None:
            with open("anomaly", 'w') as f:
                self.cursor.execute('''
                    SELECT name, anomalies FROM systems WHERE anomalies != 0
                ''')
                while fetched := self.cursor.fetchone():
                    anomaly_reason = enum_to_string(fetched[0], fetched[1])
                    print(f"{fetched[0]}: {anomaly_reason}", file=f)

        key = 'galaxy' if sector is None else sector

        if key != 'galaxy':
            self.cursor.execute('''
                SELECT COUNT(anomalies) FROM systems WHERE sector = ?
            ''', (key, ))
            fetched = self.cursor.fetchone()
            anomalies = fetched[0]
        else:
            self.cursor.execute('''
                SELECT COUNT(anomalies) FROM systems WHERE sector IS NOT NULL
            ''')
            fetched = self.cursor.fetchone()
            anomalies = fetched[0]

        subdata = data[key]
        subdata["anomalies"] = anomalies
