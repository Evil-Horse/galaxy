import gzip
import json
import tqdm
import sqlite3

from image import Image
from anomaly import Anomalies
from subsectors import Subsectors, sector_name
from biopredictor import Predictor

favorite_sectors = ('Boepp',)

# predictor is slow
predictor_enabled = False

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
            type TEXT NOT NULL
        )
        ''')
        self.con.execute('''
        CREATE TABLE IF NOT EXISTS data_stars (
            id64 INTEGER PRIMARY KEY,
            surfaceTemperature FLOAT,
            absoluteMagnitude FLOAT,
            solarMasses FLOAT
        )
        ''')
        self.con.execute('''
        CREATE TABLE IF NOT EXISTS data_planets (
            id64 INTEGER PRIMARY KEY,
            earthMasses FLOAT
        )
        ''')
        self.con.execute("CREATE INDEX IF NOT EXISTS idx_id64_s ON data_systems(id64)")
        self.con.execute("CREATE INDEX IF NOT EXISTS idx_id64_b ON data_bodies(system_id64)")
        self.con.execute("CREATE INDEX IF NOT EXISTS idx_id64_st ON data_stars(id64)")
        self.con.execute("CREATE INDEX IF NOT EXISTS idx_id64_p ON data_planets(id64)")

        self.json_file = gzip.open(name, 'r')

        self.image = Image(self.con)
        self.anomalies = Anomalies(favorite_sectors, self.con)
        self.subsectors = Subsectors(favorite_sectors, self.con)
        if predictor_enabled:
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

    def build_system_json(self, id64):
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

        bodies = []
        for fetched_body in self.con.execute("SELECT id64, name, type FROM data_bodies WHERE system_id64 = ?", (id64, )):
            body = {
                "id64" : fetched_body[0],
                "name" : fetched_body[1],
                "type" : fetched_body[2],
            }

            if body["type"] == "Star":
                for fetched_star in self.con.execute("SELECT surfaceTemperature, absoluteMagnitude, solarMasses FROM data_stars WHERE id64 = ?", (fetched_body[0], )):
                    body["surfaceTemperature"] = fetched_star[0]
                    body["absoluteMagnitude"] = fetched_star[1]
                    body["solarMasses"] = fetched_star[2]
                    break

            if body["type"] == "Planet":
                for fetched_planet in self.con.execute("SELECT earthMasses FROM data_planets WHERE id64 = ?", (fetched_body[0], )):
                    body["earthMasses"] = fetched_planet[0]
                    break

            bodies.append(body)

        sys_json["bodies"] = bodies
        return sys_json


    def load(self):
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

            i += 1
            if i % step == 0:
                pbar.update(step)
                pbar.set_description(f'Updating data: {system["name"]}')
                self.con.commit()

            updated = True
            for fetched in self.con.execute("SELECT last_updated, id64 FROM data_systems WHERE id64 = ?", (system["id64"], )):
                if fetched[0] == system["date"]:
                    updated = False

            if not updated:
                continue

            self.con.execute('''
                INSERT OR REPLACE INTO data_systems
                (id64, name, bodyCount, coord_x, coord_y, coord_z, last_updated, sector)
                    VALUES
                (?, ?, ?, ?, ?, ?, ?, ?)''',
            (system["id64"], system["name"], system.get("bodyCount", None), system["coords"]["x"], system["coords"]["y"], system["coords"]["z"], system["date"], sector_name(system["name"])))

            for body in system["bodies"]:
                self.con.execute('''
                    INSERT OR REPLACE INTO data_bodies
                    (id64, name, system_id64, type)
                        VALUES
                    (?, ?, ?, ?)''',
                (body["id64"], body["name"], system["id64"], body["type"]))

                if body["type"] == "Star":
                    surfaceTemperature = body.get("surfaceTemperature", None)
                    absoluteMagnitude = body.get("absoluteMagnitude", None)
                    solarMasses = body.get("solarMasses", None)

                    self.con.execute('''
                        INSERT OR REPLACE INTO data_stars
                        (id64, surfaceTemperature, absoluteMagnitude, solarMasses)
                            VALUES
                        (?, ?, ?, ?)''',
                    (body["id64"], surfaceTemperature, absoluteMagnitude, solarMasses))

                if body["type"] == "Planet":
                    earthMasses = body.get("earthMasses", None)

                    self.con.execute('''
                        INSERT OR REPLACE INTO data_planets
                        (id64, earthMasses)
                            VALUES
                        (?, ?)''',
                    (body["id64"], earthMasses))

            updated_systems += 1

        pbar.close()
        print(f'Processing done, updated {updated_systems} systems')

        total = None
        for fetched in self.con.execute("SELECT COUNT(id64) FROM data_systems"):
            total = fetched[0]

        pbar = tqdm.tqdm(total=total)
        i = 0
        for fetched in self.con.execute("SELECT id64, name FROM data_systems"):
            system = self.build_system_json(fetched[0])

            self.image.process(system)
            self.anomalies.process(system)
            self.subsectors.process(system)
#            if predictor_enabled:
#                self.predictor.process(system)

            i += 1
            if i % step == 0:
                pbar.update(step)
                pbar.set_description(f'Processing data: {system["name"]}')

        pbar.close()

        self.image.finalize()
        self.anomalies.finalize(self.data)
        self.subsectors.finalize(self.data)
#        if predictor_enabled:
#            self.predictor.finalize()

        for fav in favorite_sectors:
            self.anomalies.finalize(self.data, fav)
            self.subsectors.finalize(self.data, fav)

        self.con.commit()
        print_data(self.olddata, self.data)
        #with open("olddata.json", 'w') as f:
        #    json.dump(self.data, f)

galaxy = Galaxy("galaxy.json.gz")
galaxy.load()
