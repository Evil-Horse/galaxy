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

    # Skip override sectors (e.g. Col 285 Sector)
    if "Sector" in split:
        return False

    # XXX Dark Region
    if "Region" in split:
        return False

    # ICZ
    if "ICZ" in split:
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
    def __init__(self, fav, cursor):
        self.fav = fav
        self.cursor = cursor

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

        self.cursor.execute('''
        UPDATE systems SET (sector, subsector, number) = (?, ?, ?) WHERE name = ?
        ''', (system['sector'], subsector, number, system["name"]))

    def finalize(self, data, sector = None):
        if sector is None:
            with open("subsectors", 'w') as f:
                self.cursor.execute('''
                    SELECT sector, subsector, MAX(number + 1) FROM systems WHERE subsector IS NOT NULL GROUP BY subsector
                ''')
                while fetched := self.cursor.fetchone():
                    print(f"{fetched[1]}: {fetched[2]} systems", file=f)

        key = 'galaxy' if sector is None else sector

        if key != 'galaxy':
            self.cursor.execute('''
                SELECT COUNT(subsector), SUM(number + 1) FROM systems WHERE sector = ?
            ''', (key, ))
            fetched = self.cursor.fetchone()
            systems = fetched[0]
            total = fetched[1]

            self.cursor.execute('''
                SELECT COUNT(subsector) FROM systems WHERE sector = ?
            ''', (key, ))
            fetched = self.cursor.fetchone()
            count = fetched[0]
        else:
            self.cursor.execute('''
                SELECT COUNT(subsector), SUM(number + 1) FROM systems WHERE sector IS NOT NULL
            ''')
            fetched = self.cursor.fetchone()
            systems = fetched[0]
            total = fetched[1]

            self.cursor.execute('''
                SELECT COUNT(subsector) FROM systems WHERE sector IS NOT NULL
            ''')
            fetched = self.cursor.fetchone()
            print(fetched)
            count = fetched[0]

        subdata = data[key]
        subdata["systems"] = systems
        subdata["total"] = total
        subdata["count"] = count
