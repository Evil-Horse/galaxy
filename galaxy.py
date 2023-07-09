import gzip
import json
import tqdm

from image import Image
from anomaly import Anomalies
from subsectors import Subsectors, sector_name

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

class Galaxy:
    def __init__(self, name):
        self.json_file = gzip.open(name, 'r')

        self.image = Image()
        self.anomalies = Anomalies(favorite_sectors)
        self.subsectors = Subsectors(favorite_sectors)

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
        pbar = tqdm.tqdm()
        for line in self.json_file:
            line = line[0:-1].decode()

            if line == '[' or line == ']':
                continue

            if line == "":
                break

            if line[-1] == ',':
                line = line[0:-1]
            system = json.loads(line)

            pbar.update(1)
            pbar.set_description(system["name"])

            system["sector"] = sector_name(system["name"])

            self.image.process(system)
            self.anomalies.process(system)
            self.subsectors.process(system)

        pbar.close()
        self.image.finalize()
        self.subsectors.finalize(self.data)
        self.anomalies.finalize(self.data)

        for fav in favorite_sectors:
            self.subsectors.finalize(self.data, fav)
            self.anomalies.finalize(self.data, fav)

        print_data(self.olddata, self.data)
        with open("olddata.json", 'w') as f:
            json.dump(self.data, f)

galaxy = Galaxy("galaxy.json.gz")
galaxy.load()
