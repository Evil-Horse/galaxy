import gzip
import json
import tqdm

from image import Image
from anomaly import Anomalies
from subsectors import Subsectors

class Galaxy:
    def __init__(self, name):
        self.json_file = gzip.open(name, 'r')

        self.image = Image()
        self.anomalies = Anomalies()
        self.subsectors = Subsectors()

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

            self.image.process(system)
            self.anomalies.process(system)
            self.subsectors.process(system)

        pbar.close()
        print("=======")
        self.image.finalize()
        self.anomalies.finalize()
        self.subsectors.finalize()


galaxy = Galaxy("galaxy.json.gz")
galaxy.load()
