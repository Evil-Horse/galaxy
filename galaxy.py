import gzip
import json
import tqdm

from image import Image
from anomaly import Anomalies
from subsectors import Subsectors, sector_name

favorite_sectors = ('Boepp',)

def print_data(data):
    print("=======")
    for key in data.keys():
        if key == 'galaxy':
            print("Milky Way Galaxy:")
        else:
            print(f'\n{key} Sector:')

        systems = data[key]["systems"]
        total   = data[key]["total"]
        count   = data[key]["count"]
        print(f"Opened {systems:,}/{total:,} systems in {count:,} subsectors")

        anomalies = data[key]["anomalies"]
        print(f"Anomalies: {anomalies:,}")

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

        print_data(self.data)

galaxy = Galaxy("galaxy.json.gz")
galaxy.load()
