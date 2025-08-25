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
        if body["type"] == "Star" and body["solarMasses"] is None:
            # star mass unknown, skip system
            reasons |= 0x01
        if body["type"] == "Planet" and body["earthMasses"] is None:
            reasons |= 0x02

    if system["bodyCount"] is None:
        reasons |= 0x04
    elif system["bodyCount"] + barycenters != len(system["bodies"]):
        reasons |= 0x08

    return reasons

class Anomalies:
    def __init__(self, fav, connection):
        self.fav = fav
        self.connection = connection

        connection.execute('''
        CREATE TABLE IF NOT EXISTS module_anomaly (
            id64 INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            sector TEXT,
            anomalies INTEGER NOT NULL DEFAULT 0
        )
        ''')

    def process(self, system):
        anomaly_reason = check(system)

        if anomaly_reason is not None:
            self.connection.execute('''
                INSERT OR REPLACE INTO module_anomaly
                    (id64, name, sector, anomalies)
                VALUES
                    (?, ?, ?, ?)
            ''', (system["id64"], system["name"], system["sector"], anomaly_reason))

    def finalize(self, data, sector = None):
        if sector is None:
            with open("anomaly", 'w') as f:
                for fetched in self.connection.execute("SELECT name, anomalies FROM module_anomaly WHERE anomalies != 0"):
                    anomaly_reason = enum_to_string(fetched[0], fetched[1])
                    print(f"{fetched[0]}: {anomaly_reason}", file=f)

        key = 'galaxy' if sector is None else sector

        if key != 'galaxy':
            for fetched in self.connection.execute("SELECT COUNT(anomalies) FROM module_anomaly WHERE anomalies != 0 AND sector = ?", (key, )):
                anomalies = fetched[0]
        else:
            for fetched in self.connection.execute("SELECT COUNT(anomalies) FROM module_anomaly WHERE anomalies != 0"):
                anomalies = fetched[0]

        subdata = data[key]
        subdata["anomalies"] = anomalies
