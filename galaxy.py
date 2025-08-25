import gzip
import json
import tqdm
import sqlite3
from datetime import datetime

from image import Image
from anomaly import Anomalies
from subsectors import Subsectors, sector_name
from biopredictor import Predictor

favorite_sectors = ('Boepp',)

def compare(old_data, data, key, subkey):
    value = data[key][subkey]
    old_value = old_data[key][subkey]

    if value == old_value:
        return f'{value:,}'

    diff = value - old_value
    return f'{value:,} ({diff:+,})'

def print_data(old, data):
    print("=======")
    for key in data.keys():
        if key == 'galaxy':
            print("Milky Way Galaxy:")
        else:
            print(f'\n{key} Sector:')

        systems = compare(old, data, key, "systems")
        total = compare(old, data, key, "total")
        count = compare(old, data, key, "count")
        print(f"Opened {systems}/{total} systems in {count} subsectors")

        anomalies = compare(old, data, key, "anomalies")
        print(f"Anomalies: {anomalies}")

# checks if lesser can be achieved by removing key-value pairs from bigger without any modification
def compare_dicts(lesser, bigger):
    for k, v in lesser.items():

        # skip if key does not exist in original
        if k not in bigger:
            continue

        if isinstance(lesser[k], dict):
            if not compare_dicts(lesser[k], bigger[k]):
                return False

        elif isinstance(lesser[k], list):
            for iteml in lesser[k]:
                if not any([compare_dicts(iteml, itemr) for itemr in bigger[k]]):
                    return False

            for itemr in bigger[k]:
                if not any([compare_dicts(iteml, itemr) for iteml in lesser[k]]):
                    return False

        elif lesser[k] != bigger[k]:
            return False

    return True

class Galaxy:
    def __init__(self, name):
        self.con = sqlite3.connect("galaxy.sqlite")
        self.con.execute('''
        CREATE TABLE IF NOT EXISTS data_systems (
            id64 INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            bodyCount INT,
            coord_x FLOAT NOT NULL,
            coord_y FLOAT NOT NULL,
            coord_z FLOAT NOT NULL,
            last_updated DATETIME NOT NULL,
            sector TEXT
        )
        ''')
        self.con.execute('''
        CREATE TABLE IF NOT EXISTS data_bodies (
            id64 INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            system_id64 INTEGER,
            type TEXT NOT NULL,
            body_id INTEGER NOT NULL,
            updateTime DATETIME NOT NULL,
            ascendingNode FLOAT NOT NULL,
            axialTilt FLOAT NOT NULL,
            orbitalEccentricity FLOAT NOT NULL,
            orbitalInclination FLOAT NOT NULL,
            meanAnomaly FLOAT NOT NULL,
            orbitalPeriod FLOAT NOT NULL,
            argOfPeriapsis FLOAT NOT NULL,
            semiMajorAxis FLOAT NOT NULL
        )
        ''')
        self.con.execute('''
        CREATE TABLE IF NOT EXISTS data_stars (
            id64 INTEGER PRIMARY KEY,
            surfaceTemperature FLOAT,
            absoluteMagnitude FLOAT,
            solarMasses FLOAT,
            subtype TEXT,
            solarRadius FLOAT
        )
        ''')
        self.con.execute('''
        CREATE TABLE IF NOT EXISTS data_planets (
            id64 INTEGER PRIMARY KEY,
            earthMasses FLOAT,
            subtype TEXT,
            atmosphereType TEXT,
            gravity FLOAT,
            isLandable BOOLEAN NOT NULL,
            surfaceTemperature FLOAT,
            volcanism TEXT NOT NULL
        )
        ''')
        self.con.execute('''
        CREATE TABLE IF NOT EXISTS data_signals (
            id64 INTEGER NOT NULL,
            signalType TEXT NOT NULL,
            signalCount INTEGER NOT NULL,
            PRIMARY KEY (id64, signalType)
        )
        ''')
        self.con.execute('''
        CREATE TABLE IF NOT EXISTS data_parents (
            system_id64 INTEGER NOT NULL,
            bodyId INTEGER NOT NULL,
            parent_bodyID INTEGER NOT NULL,
            parent_type TEXT NOT NULL,
            PRIMARY KEY (system_id64, bodyId)
        )
        ''')
        self.con.execute('''
        CREATE TABLE IF NOT EXISTS data_atmcomposition (
            id64 INTEGER NOT NULL,
            gas TEXT NOT NULL,
            percentage FLOAT NOT NULL,
            PRIMARY KEY (id64, gas)
        )
        ''')
        self.con.execute("CREATE INDEX IF NOT EXISTS idx_id64_s ON data_systems(id64)")
        self.con.execute("CREATE INDEX IF NOT EXISTS idx_id64_b ON data_bodies(system_id64)")
        self.con.execute("CREATE INDEX IF NOT EXISTS idx_id64_st ON data_stars(id64)")
        self.con.execute("CREATE INDEX IF NOT EXISTS idx_id64_p ON data_planets(id64)")
        self.con.execute("CREATE INDEX IF NOT EXISTS idx_id64_si ON data_signals(id64)")

        self.json_file = gzip.open(name, 'r')

        self.image = Image(self.con)
        self.anomalies = Anomalies(favorite_sectors, self.con)
        self.subsectors = Subsectors(favorite_sectors, self.con)
        self.predictor = Predictor(self.con)

        self.data = {
            "galaxy": {}
        }
        for key in favorite_sectors:
            self.data[key] = {}

        with open("olddata.json", 'r') as f:
            self.olddata = json.load(f)

    def __del__(self):
        self.json_file.close()

    def get_parent_chain(self, parents, bodyid):
        chain = []

        head = parents.get(bodyid, None)
        if head is None:
            return chain

        head_dict = {head[0] : head[1]}
        tail = []
        if bodyid != head[1]:
            tail = self.get_parent_chain(parents, head[1])
        chain = [head_dict] + tail
        return chain

    def build_system_json(self, id64):
        sys_json = {}
        for fetched_system in self.con.execute("SELECT name, coord_x, coord_y, coord_z, sector, bodyCount FROM data_systems WHERE id64 = ?", (id64, )):
            sys_json = {
                "id64" : id64,
                "name" : fetched_system[0],
                "coords" : {
                    "x" : fetched_system[1],
                    "y" : fetched_system[2],
                    "z" : fetched_system[3]
                },
                "sector" : fetched_system[4],
                "bodyCount" : fetched_system[5]
            }
            break
        else:
            return sys_json

        parents = {}
        for fetched_parent in self.con.execute("SELECT bodyId, parent_bodyID, parent_type FROM data_parents WHERE system_id64 = ?", (id64, )):
            parents[fetched_parent[0]] = (fetched_parent[2], fetched_parent[1])

        bodies = []
        for fetched_body in self.con.execute("SELECT id64, name, type, body_id, updateTime, ascendingNode, axialTilt, orbitalEccentricity, orbitalInclination, meanAnomaly, orbitalPeriod, argOfPeriapsis, semiMajorAxis FROM data_bodies WHERE system_id64 = ?", (id64, )):
            body = {
                "id64" : fetched_body[0],
                "name" : fetched_body[1],
                "type" : fetched_body[2],
                "bodyId" : fetched_body[3],
                "updateTime" : fetched_body[4],
                "ascendingNode" : fetched_body[5],
                "axialTilt" : fetched_body[6],
                "orbitalEccentricity" : fetched_body[7],
                "orbitalInclination" : fetched_body[8],
                "meanAnomaly" : fetched_body[9],
                "orbitalPeriod" : fetched_body[10],
                "argOfPeriapsis" : fetched_body[11],
                "semiMajorAxis" : fetched_body[12],
            }

            body["parents"] = self.get_parent_chain(parents, body["bodyId"])

            if body["type"] == "Star":
                for fetched_star in self.con.execute("SELECT surfaceTemperature, absoluteMagnitude, solarMasses, subType, solarRadius FROM data_stars WHERE id64 = ?", (fetched_body[0], )):
                    body["surfaceTemperature"] = fetched_star[0]
                    body["absoluteMagnitude"] = fetched_star[1]
                    body["solarMasses"] = fetched_star[2]
                    body["subType"] = fetched_star[3]
                    body["solarRadius"] = fetched_star[4]
                    break

            if body["type"] == "Planet":
                for fetched_planet in self.con.execute("SELECT earthMasses, subType, atmosphereType, gravity, isLandable, surfaceTemperature, volcanism FROM data_planets WHERE id64 = ?", (fetched_body[0], )):
                    body["earthMasses"] = fetched_planet[0]
                    body["subType"] = fetched_planet[1]
                    body["atmosphereType"] = fetched_planet[2]
                    body["gravity"] = fetched_planet[3]
                    body["isLandable"] = fetched_planet[4]
                    body["surfaceTemperature"] = fetched_planet[5]
                    body["volcanism"] = fetched_planet[6]

                    signals = {}
                    for fetched_signal in self.con.execute("SELECT signalType, signalCount FROM data_signals WHERE id64 = ?", (fetched_body[0], )):
                        signals[fetched_signal[0]] = fetched_signal[1]

                    body["signals"] = {"signals" : signals}

                    atmosphereComposition = {}
                    for fetched_atmcomposition in self.con.execute("SELECT gas, percentage FROM data_atmcomposition WHERE id64 = ?", (fetched_body[0], )):
                        atmosphereComposition[fetched_atmcomposition[0]] = fetched_atmcomposition[1]

                    body["atmosphereComposition"] = atmosphereComposition

                    break

            bodies.append(body)

        sys_json["bodies"] = bodies
        return sys_json


    def import_json(self):
        i = 0
        updated_systems = 0
        step = 10000
        pbar = tqdm.tqdm(total=self.olddata['galaxy']['systems'])
        for line in self.json_file:
            line = line[0:-1].decode()

            if line == '[' or line == ']':
                continue

            if line == "":
                break

            if line[-1] == ',':
                line = line[0:-1]
            system = json.loads(line)
            system["sector"] = sector_name(system["name"])

            i += 1
            if i % step == 0:
                pbar.update(step)
                pbar.set_description(f'Updating data ({updated_systems} systems updated): {system["name"]}')
                self.con.commit()

            updated = True
            cur_id64 = system["id64"]

            db_json = self.build_system_json(cur_id64)
            if db_json != {} and compare_dicts(db_json, system) == True:
                updated = False

            if not updated:
                continue

            bodyCount = system.get("bodyCount", None)
            self.con.execute('''
                INSERT OR REPLACE INTO data_systems
                (id64, name, bodyCount, coord_x, coord_y, coord_z, last_updated, sector)
                    VALUES
                (?, ?, ?, ?, ?, ?, ?, ?)''',
            (system["id64"], system["name"], bodyCount, system["coords"]["x"], system["coords"]["y"], system["coords"]["z"], system["date"], system["sector"]))

            test_parents = {}
            for body in system["bodies"]:
                parents = body.get("parents", [])

                current_body = body["bodyId"]
                for parent_dict in parents:
                    for k, v in parent_dict.items():
                        if current_body not in test_parents:
                            test_parents[current_body] = v
                            self.con.execute('''
                                INSERT OR REPLACE INTO data_parents
                                (system_id64, bodyId, parent_type, parent_bodyID)
                                    VALUES
                                (?, ?, ?, ?)''',
                            (system["id64"], current_body, k, v))
                        elif test_parents[current_body] != v:
                            with open("invalid-parents.txt", "a") as f:
                                print(f'System {system["name"]} - {system["id64"]}: trying to change parent of {current_body}: {body["name"]} from {test_parents[current_body]} to {v}', file=f)

                        current_body = v

                self.con.execute('''
                    INSERT OR REPLACE INTO data_bodies
                    (id64, name, system_id64, type, body_id, updateTime, ascendingNode, axialTilt, orbitalEccentricity, orbitalInclination, meanAnomaly, orbitalPeriod, argOfPeriapsis, semiMajorAxis)
                        VALUES
                    (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (body["id64"],
                 body["name"],
                 system["id64"],
                 body["type"],
                 body["bodyId"],
                 body["updateTime"],
                 body.get("ascendingNode", 0.0),
                 body.get("axialTilt", 0.0),
                 body.get("orbitalEccentricity", 0.0),
                 body.get("orbitalInclination", 0.0),
                 body.get("meanAnomaly", 0.0),
                 body.get("orbitalPeriod", 0.0),
                 body.get("argOfPeriapsis", 0.0),
                 body.get("semiMajorAxis", 0.0)))

                if body["type"] == "Star":
                    surfaceTemperature = body.get("surfaceTemperature", None)
                    absoluteMagnitude = body.get("absoluteMagnitude", None)
                    solarMasses = body.get("solarMasses", None)
                    subType = body.get("subType", None)
                    solarRadius = body.get("solarRadius", None)

                    self.con.execute('''
                        INSERT OR REPLACE INTO data_stars
                        (id64, surfaceTemperature, absoluteMagnitude, solarMasses, subType, solarRadius)
                            VALUES
                        (?, ?, ?, ?, ?, ?)''',
                    (body["id64"], surfaceTemperature, absoluteMagnitude, solarMasses, subType, solarRadius))

                if body["type"] == "Planet":
                    earthMasses = body.get("earthMasses", None)
                    subType = body.get("subType", None)
                    atmosphereType = body.get("atmosphereType", None)
                    gravity = body.get("gravity", None)
                    isLandable = body.get("isLandable", False)
                    surfaceTemperature = body.get("surfaceTemperature", None)
                    volcanism = body.get("volcanism", "No volcanism")

                    self.con.execute('''
                        INSERT OR REPLACE INTO data_planets
                        (id64, earthMasses, subType, atmosphereType, gravity, isLandable, surfaceTemperature, volcanism)
                            VALUES
                        (?, ?, ?, ?, ?, ?, ?, ?)''',
                    (body["id64"], earthMasses, subType, atmosphereType, gravity, isLandable, surfaceTemperature, volcanism))

                    if "atmosphereComposition" in body:
                        for k, v in body["atmosphereComposition"].items():
                            self.con.execute('''
                                INSERT OR REPLACE INTO data_atmcomposition
                                (id64, gas, percentage)
                                    VALUES
                                (?, ?, ?)''',
                            (body["id64"], k, v))

                    #signals
                    if "signals" in body:
                        for signal in body["signals"]["signals"].items():
                            self.con.execute('''
                                INSERT OR REPLACE INTO data_signals
                                (id64, signalType, signalCount)
                                    VALUES
                                (?, ?, ?)''',
                            (body["id64"], signal[0], signal[1]))

            updated_systems += 1

        pbar.close()
        self.con.commit()
        print(f'Updated {updated_systems} systems')


    def process_db(self):
        i = 0
        step = 10000

        total = None
        for fetched in self.con.execute("SELECT COUNT(id64) FROM data_systems"):
            total = fetched[0]

        pbar = tqdm.tqdm(total=total)

        for fetched in self.con.execute("SELECT id64, name FROM data_systems"):
            i += 1
            if i % step == 0:
                pbar.update(step)
                pbar.set_description(f'Processing data: {fetched[1]}')

            system = self.build_system_json(fetched[0])

            self.image.process(system)
            self.anomalies.process(system)
            self.subsectors.process(system)
            self.predictor.process(system)

        pbar.close()
        self.con.commit()
        print(f'Processed {i} systems')


    def finalize(self):
        print(f"{datetime.now()} Finalizing image")
        self.image.finalize()
        print(f"{datetime.now()} Finalizing anomalies")
        self.anomalies.finalize(self.data)
        print(f"{datetime.now()} Finalizing subsectors")
        self.subsectors.finalize(self.data)
        print(f"{datetime.now()} Finalizing predictor")
        self.predictor.finalize()

        for fav in favorite_sectors:
            print(f"{datetime.now()} Finalizing anomalies for sector {fav}")
            self.anomalies.finalize(self.data, fav)
            print(f"{datetime.now()} Finalizing subsectors for sector {fav}")
            self.subsectors.finalize(self.data, fav)

        print(f"{datetime.now()} Finalizing done")


    def load(self):
        self.import_json()
        self.process_db()
        self.finalize()

        self.con.commit()
        print_data(self.olddata, self.data)
        with open("olddata.json", 'w') as f:
            json.dump(self.data, f)

galaxy = Galaxy("galaxy.json.gz")
galaxy.load()
