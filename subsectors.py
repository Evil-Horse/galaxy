import utils

def split_generator(text):
    split = text.split(" ")

    if not test_generated(split):
        return None

    return split

def test_generated(split):
    # Synuefe XG-Y d0-3
    # Three parts at least
    if len(split) < 3:
        return False

    # second part should contain '-'
    if not split[-2].__contains__('-'):
        return False

    # should be UPPERCASE
    if not split[-2] == split[-2].upper():
        return False

    # AA-A, 4 characters
    if len(split[-2]) != 4:
        return False

    # 3rd character should be dash
    if split[-2][2] != "-":
        return False

    return True

def sector_name(text):
    split = split_generator(text)

    if split is None:
        return None

    return ' '.join(split[:-2])

class Subsectors:
    def __init__(self, fav):
        self.subsectors = {}
        self.systems = utils.counter_init(fav)
        self.count = utils.counter_init(fav)
        self.fav = fav

    def process(self, system):
        split = split_generator(system["name"])

        if split == None:
            return

        #AA-A b4 -> AA-A b0-4
        if '-' not in split[-1]:
            split[-1] = split[-1][0] + "0-" + split[-1][1:]

        normalized = ' '.join(split)
        normalized_split = normalized.split("-")
        subsector = '-'.join(normalized_split[:-1])
        number = int(normalized_split[-1])

        if not subsector in self.subsectors:
            self.subsectors[subsector] = number
            utils.counter_increment(self.count, system['sector'], self.fav)
        else:
            if number > self.subsectors[subsector]:
                self.subsectors[subsector] = number

        utils.counter_increment(self.systems, system['sector'], self.fav)

    def finalize(self, sector = None):
        if sector is None:
            with open("subsectors", 'w') as f:
                for subsector in self.subsectors:
                    print(f"{subsector}: {self.subsectors[subsector] + 1} systems", file=f)

        if sector is None:
            systems = self.systems['galaxy']
            count = self.count['galaxy']
        else:
            systems = self.systems[sector]
            count = self.count[sector]

        total = 0
        for subsector in self.subsectors:
            if sector is None or sector == sector_name(subsector):
                total += self.subsectors[subsector] + 1

        print(f"Opened {systems:,}/{total:,} systems in {count:,} subsectors")
