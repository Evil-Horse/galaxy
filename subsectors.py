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
    def __init__(self, fav, connection):
        self.fav = fav
        self.connection = connection

        connection.execute('''
        CREATE TABLE IF NOT EXISTS module_subsectors (
            id64 INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            sector TEXT,
            subsector TEXT,
            number INTEGER
        )
        ''')

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

        self.connection.execute('''
            INSERT OR REPLACE INTO module_subsectors
                (id64, name, sector, subsector, number)
            VALUES
                (?, ?, ?, ?, ?)
        ''', (system["id64"], system["name"], system["sector"], subsector, number))

    def finalize(self, data, sector = None):
        if sector is None:
            with open("subsectors", 'w') as f:
                for fetched in self.connection.execute("SELECT sector, subsector, MAX(number + 1) FROM module_subsectors WHERE subsector IS NOT NULL GROUP BY subsector"):
                    print(f"{fetched[1]}: {fetched[2]} systems", file=f)

        key = 'galaxy' if sector is None else sector

        if key != 'galaxy':
            for fetched in self.connection.execute("SELECT SUM(col1), SUM(col2 + 1) FROM (SELECT COUNT(subsector) AS col1, MAX(number) AS col2 FROM module_subsectors WHERE sector = ? GROUP BY subsector)", (key, )):
                systems = fetched[0]
                total = fetched[1]

            for fetched in self.connection.execute("SELECT COUNT(DISTINCT(subsector)) FROM module_subsectors WHERE sector = ?", (key, )):
                count = fetched[0]
        else:
            for fetched in self.connection.execute("SELECT SUM(col1), SUM(col2 + 1) FROM (SELECT COUNT(subsector) AS col1, MAX(number) AS col2 FROM module_subsectors WHERE sector IS NOT NULL GROUP BY subsector)"):
                systems = fetched[0]
                total = fetched[1]

            for fetched in self.connection.execute("SELECT COUNT(DISTINCT(subsector)) FROM module_subsectors WHERE sector IS NOT NULL"):
                count = fetched[0]

        subdata = data[key]
        subdata["systems"] = systems
        subdata["total"] = total
        subdata["count"] = count
