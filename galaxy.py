import gzip
import json
import tqdm

from image import Image
from anomaly import Anomalies
from subsectors import Subsectors, sector_name

favorite_sectors = ('Boepp',)

class Galaxy:
    def __init__(self, name):
        self.json_file = gzip.open(name, 'r')

        self.image = Image()
        self.anomalies = Anomalies(favorite_sectors)
        self.subsectors = Subsectors(favorite_sectors)

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
        print("=======")
        print("Milky Way Galaxy:")
        self.image.finalize()
        self.subsectors.finalize()
        self.anomalies.finalize()

        for fav in favorite_sectors:
            print(f"\n{fav} Sector:")
            self.subsectors.finalize(fav)
            self.anomalies.finalize(fav)

galaxy = Galaxy("galaxy.json.gz")
galaxy.load()
