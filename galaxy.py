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
        self.cur = self.con.cursor()
        self.cur.execute('''
        CREATE TABLE IF NOT EXISTS data_systems (
            id64 INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            last_updated DATETIME NOT NULL,
            sector TEXT,
            subsector TEXT,
            number INTEGER
        )
        ''')
        self.cur.execute('''
            CREATE INDEX IF NOT EXISTS idx_id64 ON data_systems(id64)
        ''')

        self.json_file = gzip.open(name, 'r')

        self.image = Image(self.cur)
        self.anomalies = Anomalies(favorite_sectors, self.cur)
        self.subsectors = Subsectors(favorite_sectors, self.cur)
        if predictor_enabled:
            self.predictor = Predictor(self.cur)

        self.data = {
            "galaxy": {}
        }
        for key in favorite_sectors:
            self.data[key] = {}

        with open("olddata.json", 'r') as f:
            self.olddata = json.load(f)

    def __del__(self):
        self.json_file.close()

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
                pbar.set_description(system["name"])
                self.con.commit()

            system["sector"] = sector_name(system["name"])

            # check if system has been updates
            self.cur.execute('''
                SELECT last_updated, id64 FROM data_systems WHERE id64 = ?
            ''', (system["id64"], ))

            updated = True
            while fetched := self.cur.fetchone():
                if fetched[0] == system["date"]:
                    updated = False

            if not updated:
                continue

            updated_systems += 1
            #print(f'Updated system {system["name"]}')

            self.image.process(system)
            self.anomalies.process(system)
#            self.subsectors.process(system)
#            if predictor_enabled:
#                self.predictor.process(system)

            self.cur.execute('''
                INSERT OR REPLACE INTO data_systems
                (id64, name, last_updated)
                    VALUES
                (?, ?, ?)''',
            (system["id64"], system["name"], system["date"]))

        pbar.close()
        print(f'Processing done, updated {updated_systems} systems')

        self.image.finalize()
        self.anomalies.finalize(self.data)
#        self.subsectors.finalize(self.data)
#        if predictor_enabled:
#            self.predictor.finalize()

        for fav in favorite_sectors:
            self.anomalies.finalize(self.data, fav)
#            self.subsectors.finalize(self.data, fav)

        self.con.commit()
        #print_data(self.olddata, self.data)
        #with open("olddata.json", 'w') as f:
        #    json.dump(self.data, f)

galaxy = Galaxy("galaxy.json.gz")
galaxy.load()
