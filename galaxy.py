import gzip
import json
import tqdm

from image import Image
import anomaly
from subsectors import Subsectors

class Galaxy:
    def __init__(self, name):
        self.json_file = gzip.open(name, 'r')

        self.image = Image()
        self.anomaly_file = open("anomaly", 'w')
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
            anomaly_reason = anomaly.process(system)
            if anomaly_reason is not None:
                print("%s: %s" % (system["name"], anomaly_reason), file=self.anomaly_file)
            self.subsectors.process(system)

        self.image.finalize()
        self.subsectors.finalize()


galaxy = Galaxy("galaxy.json.gz")
galaxy.load()
