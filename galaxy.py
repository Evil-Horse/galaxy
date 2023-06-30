import gzip
import json
import tqdm

class Galaxy:
    def __init__(self, name):
        self.json_file = gzip.open(name, 'r')

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


galaxy = Galaxy("galaxy.json.gz")
galaxy.load()
