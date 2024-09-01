import gzip
import json
from RegionMap import findRegionForBoxel
from distances import Coordinates
import sys
import math

regions = {
    "$Codex_RegionName_1;" : 'Galactic Centre',
    "$Codex_RegionName_2;" : 'Empyrean Straits',
    "$Codex_RegionName_3;" : "Ryker's Hope",
    "$Codex_RegionName_4;" : "Odin's Hold",
    "$Codex_RegionName_5;" : 'Norma Arm',
    "$Codex_RegionName_6;" : 'Arcadian Stream',
    "$Codex_RegionName_7;" : 'Izanami',
    "$Codex_RegionName_8;" : 'Inner Orion-Perseus Conflux',
    "$Codex_RegionName_9;" : 'Inner Scutum-Centaurus Arm',
    "$Codex_RegionName_10;" : 'Norma Expanse',
    "$Codex_RegionName_11;" : 'Trojan Belt',
    "$Codex_RegionName_12;" : 'The Veils',
    "$Codex_RegionName_13;" : "Newton's Vault",
    "$Codex_RegionName_14;" : 'The Conduit',
    "$Codex_RegionName_15;" : 'Outer Orion-Perseus Conflux',
    "$Codex_RegionName_16;" : 'Orion-Cygnus Arm',
    "$Codex_RegionName_17;" : 'Temple',
    "$Codex_RegionName_18;" : 'Inner Orion Spur',
    "$Codex_RegionName_19;" : "Hawking's Gap",
    "$Codex_RegionName_20;" : "Dryman's Point",
    "$Codex_RegionName_21;" : 'Sagittarius-Carina Arm',
    "$Codex_RegionName_22;" : 'Mare Somnia',
    "$Codex_RegionName_23;" : 'Acheron',
    "$Codex_RegionName_24;" : 'Formorian Frontier',
    "$Codex_RegionName_25;" : 'Hieronymus Delta',
    "$Codex_RegionName_26;" : 'Outer Scutum-Centaurus Arm',
    "$Codex_RegionName_27;" : 'Outer Arm',
    "$Codex_RegionName_28;" : "Aquila's Halo",
    "$Codex_RegionName_29;" : 'Errant Marches',
    "$Codex_RegionName_30;" : 'Perseus Arm',
    "$Codex_RegionName_31;" : 'Formidine Rift',
    "$Codex_RegionName_32;" : 'Vulcan Gate',
    "$Codex_RegionName_33;" : 'Elysian Shore',
    "$Codex_RegionName_34;" : 'Sanguineous Rim',
    "$Codex_RegionName_35;" : 'Outer Orion Spur',
    "$Codex_RegionName_36;" : "Achilles's Altar",
    "$Codex_RegionName_37;" : 'Xibalba',
    "$Codex_RegionName_38;" : "Lyra's Song",
    "$Codex_RegionName_39;" : 'Tenebrae',
    "$Codex_RegionName_40;" : 'The Abyss',
    "$Codex_RegionName_41;" : "Kepler's Crest",
    "$Codex_RegionName_42;" : 'The Void',
}


star_types_map = {
    # Main Sequence
    "O (Blue-White) Star" : "O",
    "B (Blue-White super giant) Star" : "B",
    "B (Blue-White) Star" : "B",
    "A (Blue-White super giant) Star" : "A",
    "A (Blue-White) Star" : "A",
    "F (White super giant) Star" : "F",
    "F (White) Star" : "F",
    "G (White-Yellow super giant) Star" : "G",
    "G (White-Yellow) Star" : "G" ,
    "K (Yellow-Orange giant) Star" : "K",
    "K (Yellow-Orange) Star" : "K",
    "M (Red super giant) Star" : "M",
    "M (Red giant) Star" : "M",
    "M (Red dwarf) Star" : "M",

    # Brown Dwarfs
    "L (Brown dwarf) Star" : "L",
    "T (Brown dwarf) Star" : "T",
    "Y (Brown dwarf) Star" : "Y",

    # Proto Stars
    "T Tauri Star" : "TTS",
    "Herbig Ae/Be Star": "Ae",

    # Wolf-Rayet
    "Wolf-Rayet Star" : "W",
    "Wolf-Rayet C Star" : "W",
    "Wolf-Rayet N Star" : "W",
    "Wolf-Rayet NC Star" : "W",
    "Wolf-Rayet O Star" : "W",

    # White Dwarfs
    "White Dwarf (D) Star" : "D",
    "White Dwarf (DA) Star" : "D",
    "White Dwarf (DAB) Star" : "D",
    "White Dwarf (DAV) Star" : "D",
    "White Dwarf (DAZ) Star" : "D",
    "White Dwarf (DB) Star" : "D",
    "White Dwarf (DBV) Star" : "D",
    "White Dwarf (DBZ) Star" : "D",
    "White Dwarf (DC) Star" : "D",
    "White Dwarf (DCV) Star" : "D",
    "White Dwarf (DQ) Star" : "D",

    # Neutron Star
    "Neutron Star" : "N",

    # Carbon Star - biology does not spawn
    "C Star" : "C",
    "CJ Star" : "C",
    "CN Star" : "C",
    "MS-type Star" : "C",
    "S-type Star" : "C",

    # Black Hole - biology does not spawn
    "Black Hole" : "BH",
    # Sagittarius A*
    "Supermassive Black Hole" : "BH",
}

# pre-defined colors
CANONN_COLOR_AM = "Amethyst"
CANONN_COLOR_EM = "Emerald"
CANONN_COLOR_GR = "Green"
CANONN_COLOR_GY = "Grey"
CANONN_COLOR_IN = "Indigo"
CANONN_COLOR_LI = "Lime"
CANONN_COLOR_MR = "Maroon"
CANONN_COLOR_MV = "Mauve"
CANONN_COLOR_OC = "Ocher"
CANONN_COLOR_OR = "Orange"
CANONN_COLOR_RE = "Red"
CANONN_COLOR_SG = "Sage"
CANONN_COLOR_TE = "Teal"
CANONN_COLOR_TU = "Turquoise"
CANONN_COLOR_WH = "White"
CANONN_COLOR_YE = "Yellow"

# galactic arms
ARM_CENTRAL = set([
    "Galactic Centre",
    "Empyrean Straits",
    "Ryker’s Hope",
    "Odin’s Hold",
])

ARM_OUTER = set([
    "Norma Arm",
    "Arcadian Stream",
    "Newton’s Vault",
    "The Conduit",
    "Outer Arm",
    "Errant Marches",
    "The Formidine Rift",
    "Xibalba",
    "Kepler’s Crest",
])

ARM_PERSEUS = set([
    "Izanami",
    "Outer Orion-Perseus Conflux",
    "Perseus Arm",
    "Vulcan Gate",
    "Elysian Shore",
    "Sanguineous Rim",
    "Achilles’s Altar",
    "Lyra’s Song",
    "Tenebrae",
])

ARM_SAGITTARIUS_CARINA = set([
    "Inner Orion-Perseus Conflux",
    "Orion-Cygnus Arm",
    "Temple",
    "Inner Orion Spur",
    "Hawking’s Gap",
    "Dryman’s Point",
    "Sagittarius-Carina Arm",
    "Mare Somnia",
    "Acheron",
    "Outer Orion Spur",
    "The Abyss",
])

ARM_SCUTUM_CENTAURUS = set([
    "Inner Scutum-Centaurus Arm",
    "Norma Expanse",
    "Trojan Belt",
    "The Veils",
    "Formorian Frontier",
    "Hieronymus Delta",
    "Outer Scutum-Centaurus Arm",
    "Aquila’s Halo",
    "The Void",
])

ARM_ORION_CYGNUS = set([
    "Izanami",
    "Inner Orion-Perseus Conflux",
    "Inner Scutum-Centaurus Arm",
    "Outer Orion-Perseus Conflux",
    "Orion-Cygnus Arm",
    "Temple",
    "Inner Orion Spur",
    "Elysian Shore",
    "Sanguineous Rim",
    "Outer Orion Spur",
])

def get_mapped_star_type(star_type):
    if star_type is None:
        return None

    return star_types_map[star_type]

def get_possible_colors(species, body, stars, colors, min_dist=None, max_dist=None):
    set_colors = set()

    body_coordinates = body["coordinates"]

    brightnesses = {}

    stars_filtered = []
    shadow_colors = set()
    for star in stars:
        star_type = get_mapped_star_type(star.get("subType", None))
        if star_type is None:
            continue

        # get distance
        star_coordinates = star["coordinates"]
        dist_au_squared = (star_coordinates[0] - body_coordinates[0]) ** 2 + (star_coordinates[1] - body_coordinates[1]) ** 2 + (star_coordinates[2] - body_coordinates[2]) ** 2
        if dist_au_squared == 0.0:
            continue

        if "solarRadius" not in star:
            continue

        color = colors[star_type]
        if color is not None:
            # we return this if no brightnesses known
            shadow_colors.add(color)

        stars_filtered.append(star)

        brightness = star["solarRadius"] ** 2 * star["surfaceTemperature"] ** 4 / dist_au_squared
        brightnesses[star["name"]] = brightness

    if len(brightnesses) == 0:
        # return every possible color based on star types in system
        return shadow_colors

    brightest = [key for key in brightnesses if all(brightnesses[key] >= brightnesses[x] for x in brightnesses)]
    if len(brightest) > 0:
        max_brightness = brightnesses[brightest[0]]

    for star in stars_filtered:
        star_type = get_mapped_star_type(star.get("subType", None))
        if star_type is None:
            continue

        if brightnesses.get(star["name"], 0.0) < max_brightness * 0.1:
            continue

        star_coordinates = star["coordinates"]
        dist_au_squared = (star_coordinates[0] - body_coordinates[0]) ** 2 + (star_coordinates[1] - body_coordinates[1]) ** 2 + (star_coordinates[2] - body_coordinates[2]) ** 2

        # Clypeus constraints:
        if min_dist is not None and min_dist ** 2 > dist_au_squared:
            #print(f'Speculumi: star {star["name"]} is too close ({min_dist} > {math.sqrt(dist_au_squared)})')
            continue

        if max_dist is not None and max_dist ** 2 < dist_au_squared:
            #print(f'Lacrimam: star {star["name"]} is too far ({max_dist} < {math.sqrt(dist_au_squared)})')
            continue


        color = colors[star_type]
        if color is not None:
            set_colors.add(color)

    return set_colors

def get_color_priority(region, variant):
    # galaxy-wide discovery
    if variant not in global_entries:
        return 3

    # region discovery
    if variant not in regional_entries[region]:
        return 2

    return 1

# Carbon Dioxide >= 97.5%
# 175-180K
def aleoida_arcus(genus, species, region, body, stars, colors):
    ret = []
    co2 = body.get("atmosphereComposition", {}).get('Carbon dioxide', 0.0)
    if co2 < 97.5:
        return ret

    temperature = body["surfaceTemperature"]

    if not 175.0 <= temperature <= 180.0:
        return ret

    volcanism = body.get("volcanism", "No volcanism")

    if volcanism != "No volcanism":
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"

        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

# Carbon Dioxide >= 97.5%
# 180-190K
def aleoida_coronamus(genus, species, region, body, stars, colors):
    ret = []
    co2 = body.get("atmosphereComposition", {}).get('Carbon dioxide', 0.0)
    if co2 < 97.5:
        return ret

    temperature = body["surfaceTemperature"]

    if not 180.0 <= temperature <= 190.0:
        return ret

    volcanism = body.get("volcanism", "No volcanism")

    if volcanism != "No volcanism":
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

# Carbon Dioxide >= 97.5%
# 190-197K
def aleoida_gravis(genus, species, region, body, stars, colors):
    ret = []
    co2 = body.get("atmosphereComposition", {}).get('Carbon dioxide', 0.0)
    if co2 < 97.5:
        return ret

    temperature = body["surfaceTemperature"]

    if not 190.0 <= temperature <= 197.0:
        return ret

    volcanism = body.get("volcanism", "No volcanism")

    if volcanism != "No volcanism":
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

# Ammonia 100%
# 152-177K
def aleoida_laminiae(genus, species, region, body, stars, colors):
    ret = []

    # Orion-Cygnus Arm; Sagittarius-Carina Arm including Odin’s Hold and Galactic Centre
    if region not in ARM_SAGITTARIUS_CARINA | ARM_ORION_CYGNUS | set(["Odin’s Hold", "Galactic Centre"]):
        return ret

    ammonia = body.get("atmosphereComposition", {}).get('Ammonia', 0.0)
    if ammonia < 100.0:
        return ret

    temperature = body["surfaceTemperature"]

    if not 152.0 <= temperature <= 177.0:
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

# Ammonia 100%
# 170-177K
def aleoida_spica(genus, species, region, body, stars, colors):
    ret = []

    # NOT Sagittarius-Carina Arm
    if region in ARM_SAGITTARIUS_CARINA:
        return ret

    ammonia = body.get("atmosphereComposition", {}).get('Ammonia', 0.0)
    if ammonia < 100.0:
        return ret

    temperature = body["surfaceTemperature"]

    if not 170.0 <= temperature <= 177.0:
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

def check_aleoida(region, body, stars):
    ret = []

    colors = {
        "O" : None,
        "B" : CANONN_COLOR_YE,
        "A" : CANONN_COLOR_GR,
        "F" : CANONN_COLOR_TE,
        "G" : None,
        "K" : CANONN_COLOR_TU,
        "M" : CANONN_COLOR_EM,
        "L" : CANONN_COLOR_LI,
        "T" : CANONN_COLOR_SG,
        "Y" : CANONN_COLOR_AM,
        "TTS" : CANONN_COLOR_MV,
        "Ae": None,
        "W" : CANONN_COLOR_GY,
        "D" : CANONN_COLOR_IN,
        "N" : CANONN_COLOR_OC,
        "BH" : None,
        "C" : None,
    }

    genus = "Aleoida"
    name = body["name"]
    if name in known_planets and genus in known_planets[name]:
        if len(known_planets[name]["by_genus"][genus]) > 2:
            print(name, "WTF", known_planets[name]["by_genus"][genus], file=sys.stderr)
        for e in known_planets[name]["by_genus"][genus]:
            ret.append((region, name, e, 1))
        return ret

    ret += aleoida_arcus     (genus, "Arcus"    , region, body, stars, colors)
    ret += aleoida_coronamus (genus, "Coronamus", region, body, stars, colors)
    ret += aleoida_gravis    (genus, "Gravis"   , region, body, stars, colors)
    ret += aleoida_laminiae  (genus, "Laminiae" , region, body, stars, colors)
    ret += aleoida_spica     (genus, "Spica"    , region, body, stars, colors)
    return ret

# Ammonia >= 60%
# 152-177 K
def bacterium_alcyoneum(genus, species, region, body, stars, colors):
    ret = []

    # 3.68 m/s^2 - unlikely
    gravity = body["gravity"]
    if gravity > 0.375253:
        return ret

    ammonia = body.get("atmosphereComposition", {}).get('Ammonia', 0.0)
    if ammonia < 60.0:
        return ret

    temperature = body["surfaceTemperature"]

    if not 152.0 <= temperature <= 177.0:
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

# Carbon dioxide > 50% (one planet with 39%)
# 145-400K
def bacterium_aurasus(genus, species, region, body, stars, colors):
    ret = []
    co2 = body.get("atmosphereComposition", {}).get('Carbon dioxide', 0.0)
    if co2 < 50.0:
        return ret

    temperature = body["surfaceTemperature"]

    if not 145.0 <= temperature <= 400.0:
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

# 132-500K
def bacterium_cerbrus(genus, species, region, body, stars, colors):
    ret = []
    ammonia = body.get("atmosphereComposition", {}).get('Ammonia', 0.0)
    if ammonia < 60.0:
        return ret

    temperature = body["surfaceTemperature"]

    if not 132.0 <= temperature <= 500.0:
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

def check_bacterium(region, body, stars):
    ret = []

    colors = {
        "O" : CANONN_COLOR_TU,
        "B" : CANONN_COLOR_GY,
        "A" : CANONN_COLOR_YE,
        "F" : CANONN_COLOR_LI,
        "G" : CANONN_COLOR_EM,
        "K" : CANONN_COLOR_GR,
        "M" : CANONN_COLOR_TE,
        "L" : CANONN_COLOR_SG,
        "T" : CANONN_COLOR_RE,
        "Y" : CANONN_COLOR_MV,
        "TTS" : CANONN_COLOR_MR,
        "Ae": CANONN_COLOR_OR,
        "W" : CANONN_COLOR_AM,
        "D" : CANONN_COLOR_OC,
        "N" : CANONN_COLOR_IN,
        "BH" : None,
        "C" : None,
    }

    genus = "Bacterium"
    name = body["name"]
    if name in known_planets and genus in known_planets[name]:
        if len(known_planets[name]["by_genus"][genus]) > 2:
            print(name, "WTF", known_planets[name]["by_genus"][genus], file=sys.stderr)
        for e in known_planets[name]["by_genus"][genus]:
            ret.append((region, name, e, 1))
        return ret

    ret += bacterium_alcyoneum (genus, "Alcyoneum", region, body, stars, colors)
    ret += bacterium_aurasus   (genus, "Aurasus"  , region, body, stars, colors)
    ret += bacterium_cerbrus   (genus, "Cerbrus"  , region, body, stars, colors)
    return ret

# Carbon dioxide > 97.5%
# 180-196K
def cactoida_cortexum(genus, species, region, body, stars, colors):
    ret = []

    # Orion-Cygnus Arm including Odin’s Hold and Galactic Centre
    if region not in ARM_ORION_CYGNUS | set(["Odin’s Hold", "Galactic Centre"]):
        return ret

    co2 = body.get("atmosphereComposition", {}).get('Carbon dioxide', 0.0)
    if co2 < 97.5:
        return ret

    temperature = body["surfaceTemperature"]

    if not 180.0 <= temperature <= 196.0:
        return ret

    volcanism = body.get("volcanism", "No volcanism")

    if volcanism != "No volcanism":
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

# Ammonia > 99%
# 160-177K
def cactoida_lapis(genus, species, region, body, stars, colors):
    ret = []

    # Sagittarius-Carina Arm including Odin’s Hold and Galactic Centre
    if region not in ARM_SAGITTARIUS_CARINA | set(["Odin’s Hold", "Galactic Centre"]):
        return ret

    ammonia = body.get("atmosphereComposition", {}).get('Ammonia', 0.0)
    if ammonia < 99.0:
        return ret

    temperature = body["surfaceTemperature"]

    if not 160.0 <= temperature <= 177.0:
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

# Ammonia 100%
# 160-177K
def cactoida_peperatis(genus, species, region, body, stars, colors):
    ret = []

    # Scutum-Centaurus Arm including Odin’s Hold and Galactic Centre
    if region not in ARM_SCUTUM_CENTAURUS | set(["Odin’s Hold", "Galactic Centre"]):
        return ret

    ammonia = body.get("atmosphereComposition", {}).get('Ammonia', 0.0)
    if ammonia < 100.0:
        return ret

    temperature = body["surfaceTemperature"]

    if not 160.0 <= temperature <= 177.0:
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

# Carbon dioxide > 97.5%
# 180-196K
def cactoida_pullulanta(genus, species, region, body, stars, colors):
    ret = []

    # Perseus Arm including Ryker’s Hope and Galactic Centre
    if region not in ARM_PERSEUS | set(["Ryker’s Hope", "Galactic Centre"]):
        return ret

    co2 = body.get("atmosphereComposition", {}).get('Carbon dioxide', 0.0)
    if co2 < 97.5:
        return ret

    temperature = body["surfaceTemperature"]

    if not 180.0 <= temperature <= 196.0:
        return ret

    volcanism = body.get("volcanism", "No volcanism")

    if volcanism != "No volcanism":
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

# Water 100%, 390-450K
# CO2 97.5+%, SO2 only 160-207K
def cactoida_vermis(genus, species, region, body, stars, colors):
    ret = []

    temperature = body["surfaceTemperature"]

    valid = False

    water = body.get("atmosphereComposition", {}).get('Water', 0.0)
    if water == 100.0 and 390.0 <= temperature <= 450.0:
        valid = True

    co2 = body.get("atmosphereComposition", {}).get('Carbon dioxide', 0.0)
    so2 = body.get("atmosphereComposition", {}).get('Sulphur dioxide', 0.0)
    if co2 >= 97.5 and co2 + so2 == 100.0 and 160.0 <= temperature <= 207.0:
        valid = True

    if not valid:
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

def check_cactoida(region, body, stars):
    ret = []

    colors = {
        "O" : CANONN_COLOR_GY,
        "B" : None,
        "A" : CANONN_COLOR_GR,
        "F" : CANONN_COLOR_YE,
        "G" : CANONN_COLOR_TE,
        "K" : None,
        "M" : CANONN_COLOR_AM,
        "L" : CANONN_COLOR_MV,
        "T" : CANONN_COLOR_OR,
        "Y" : CANONN_COLOR_OC,
        "TTS" : CANONN_COLOR_RE,
        "Ae": None,
        "W" : CANONN_COLOR_IN,
        "D" : CANONN_COLOR_TU,
        "N" : CANONN_COLOR_SG,
        "BH" : None,
        "C" : None,
    }

    genus = "Cactoida"
    name = body["name"]
    if name in known_planets and genus in known_planets[name]:
        if len(known_planets[name]["by_genus"][genus]) > 2:
            print(name, "WTF", known_planets[name]["by_genus"][genus], file=sys.stderr)
        for e in known_planets[name]["by_genus"][genus]:
            ret.append((region, name, e, 1))
        return ret

    ret += cactoida_cortexum   (genus, "Cortexum"  , region, body, stars, colors)
    ret += cactoida_lapis      (genus, "Lapis"     , region, body, stars, colors)
    ret += cactoida_peperatis  (genus, "Peperatis" , region, body, stars, colors)
    ret += cactoida_pullulanta (genus, "Pullulanta", region, body, stars, colors)
    ret += cactoida_vermis     (genus, "Vermis"    , region, body, stars, colors)
    return ret

# Water 100%, 390-452K
# CO2 >= 97.5%, 190-196K
# rocky body
# < 5 AU
def clypeus_lacrimam(genus, species, region, body, stars, colors):
    ret = []

    temperature = body["surfaceTemperature"]

    valid = False

    water = body.get("atmosphereComposition", {}).get('Water', 0.0)
    if water == 100.0 and 390.0 <= temperature <= 452.0:
        valid = True

    co2 = body.get("atmosphereComposition", {}).get('Carbon dioxide', 0.0)
    if co2 >= 97.5 and 190.0 <= temperature <= 196.0:
        valid = True

    if not valid:
        return ret

    subtype = body['subType']

    if subtype != "Rocky body":
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors, max_dist = 4.0)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

# Water 100%, 390-452K
# CO2 >= 97.5%, 190-196K
def clypeus_margaritus(genus, species, region, body, stars, colors):
    ret = []

    temperature = body["surfaceTemperature"]

    valid = False

    water = body.get("atmosphereComposition", {}).get('Water', 0.0)
    if water == 100.0 and 390.0 <= temperature <= 452.0:
        valid = True

    co2 = body.get("atmosphereComposition", {}).get('Carbon dioxide', 0.0)
    if co2 >= 97.5 and 190.0 <= temperature <= 196.0:
        valid = True

    if not valid:
        return ret

    subtype = body['subType']

    if subtype != "High metal content world":
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

# Water 100%, 390-452K
# CO2 >= 97.5%, 190-196K
# rocky body
# > 5 AU
def clypeus_speculumi(genus, species, region, body, stars, colors):
    ret = []

    temperature = body["surfaceTemperature"]

    valid = False

    water = body.get("atmosphereComposition", {}).get('Water', 0.0)
    if water == 100.0 and 390.0 <= temperature <= 452.0:
        valid = True

    co2 = body.get("atmosphereComposition", {}).get('Carbon dioxide', 0.0)
    if co2 >= 97.5 and 190.0 <= temperature <= 196.0:
        valid = True

    if not valid:
        return ret

    subtype = body['subType']

    if subtype != "Rocky body":
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors, min_dist = 4.0)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

def check_clypeus(region, body, stars):
    ret = []

    colors = {
        "O" : None,
        "B" : CANONN_COLOR_MR,
        "A" : CANONN_COLOR_OR,
        "F" : CANONN_COLOR_MV,
        "G" : CANONN_COLOR_AM,
        "K" : CANONN_COLOR_GY,
        "M" : CANONN_COLOR_TU,
        "L" : CANONN_COLOR_TE,
        "T" : CANONN_COLOR_GR,
        "Y" : None,
        "TTS" : None,
        "Ae": None,
        "W" : None,
        "D" : CANONN_COLOR_LI,
        "N" : CANONN_COLOR_YE,
        "BH" : None,
        "C" : None,
    }

    genus = "Clypeus"
    name = body["name"]
    if name in known_planets and genus in known_planets[name]:
        if len(known_planets[name]["by_genus"][genus]) > 2:
            print(name, "WTF", known_planets[name]["by_genus"][genus], file=sys.stderr)
        for e in known_planets[name]["by_genus"][genus]:
            ret.append((region, name, e, 1))
        return ret

    ret += clypeus_lacrimam   (genus, "Lacrimam"  , region, body, stars, colors)
    ret += clypeus_margaritus (genus, "Margaritus", region, body, stars, colors)
    ret += clypeus_speculumi  (genus, "Speculumi" , region, body, stars, colors)
    return ret

# Ammonia 100%
# 152-176K
# HMC, Rocky
def concha_aureolas(genus, species, region, body, stars, colors):
    ret = []
    ammonia = body.get("atmosphereComposition", {}).get('Ammonia', 0.0)
    if ammonia < 100.0:
        return ret

    temperature = body["surfaceTemperature"]

    if not 152.0 <= temperature <= 176.0:
        return ret

    subtype = body['subType']

    if subtype not in ["High metal content world", "Rocky body"]:
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

# CO2 > 97.5%
# 150-199K
# HMC, Rocky
# No volcanism
def concha_labiata(genus, species, region, body, stars, colors):
    ret = []
    co2 = body.get("atmosphereComposition", {}).get('Carbon dioxide', 0.0)
    if co2 < 97.5:
        return ret

    temperature = body["surfaceTemperature"]

    if not 150.0 <= temperature <= 199.0:
        return ret

    subtype = body['subType']

    if subtype not in ["High metal content world", "Rocky body"]:
        return ret

    volcanism = body.get("volcanism", "No volcanism")

    if volcanism != "No volcanism":
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

def check_concha(region, body, stars):
    ret = []

    colors = {
        "O" : None,
        "B" : CANONN_COLOR_IN,
        "A" : CANONN_COLOR_GY,
        "F" : CANONN_COLOR_TE,
        "G" : CANONN_COLOR_TU,
        "K" : CANONN_COLOR_RE,
        "M" : None,
        "L" : CANONN_COLOR_OR,
        "T" : None,
        "Y" : CANONN_COLOR_YE,
        "TTS" : None,
        "Ae": None,
        "W" : CANONN_COLOR_LI,
        "D" : CANONN_COLOR_GR,
        "N" : CANONN_COLOR_EM,
        "BH" : None,
        "C" : None,
    }

    genus = "Concha"
    name = body["name"]
    if name in known_planets and genus in known_planets[name]:
        if len(known_planets[name]["by_genus"][genus]) > 2:
            print(name, "WTF", known_planets[name]["by_genus"][genus], file=sys.stderr)
        for e in known_planets[name]["by_genus"][genus]:
            ret.append((region, name, e, 1))
        return ret

    ret += concha_aureolas (genus, "Aureolas", region, body, stars, colors)
    ret += concha_labiata  (genus, "Labiata" , region, body, stars, colors)
    return ret

# argon atmosphere
# icy body
# 50-150K
def fonticulua_campestris(genus, species, region, body, stars, colors):
    ret = []
    argon = body.get("atmosphereComposition", {}).get('Argon', 0.0)
    if argon < 50.0:
        return ret

    temperature = body["surfaceTemperature"]

    if not 50.0 <= temperature <= 150.0:
        return ret

    subtype = body['subType']

    if subtype != "Icy body":
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

# 100% methane
# icy body
# temperature:
# found: 83.51 - 108.59
# signal: 67.00 - 108.76
def fonticulua_digitos(genus, species, region, body, stars, colors):
    ret = []

    # 0.634 m/s^2 - unlikely
    # planets exist up to 0.13g
    gravity = body["gravity"]
    if gravity > 0.064729:
        return ret

    methane = body.get("atmosphereComposition", {}).get('Methane', 0.0)
    if methane < 100.0:
        return ret

    temperature = body["surfaceTemperature"]

    if not 83.0 <= temperature <= 109.0:
        return ret

    subtype = body['subType']

    if subtype != "Icy body":
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

# Oxygen
# icy body
# temperature:
# found: 143.80 - 199.29
def fonticulua_fluctus(genus, species, region, body, stars, colors):
    ret = []
    oxygen = body.get("atmosphereComposition", {}).get('Oxygen', 0.0)
    if oxygen < 50.0:
        return ret

    temperature = body["surfaceTemperature"]

    if not 143.0 <= temperature <= 200.0:
        return ret

    subtype = body['subType']

    if subtype != "Icy body":
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

# Nitrogen > 99%, argon presence -> Upupam
# icy body
# temperature:
# found: 50 - 80.77
def fonticulua_lapida(genus, species, region, body, stars, colors):
    ret = []
    nitrogen = body.get("atmosphereComposition", {}).get('Nitrogen', 0.0)
    argon = body.get("atmosphereComposition", {}).get('Argon', 0.0)
    if nitrogen < 99.0 or argon > 0.0:
        return ret

    temperature = body["surfaceTemperature"]

    if not 50.0 <= temperature <= 81.0:
        return ret

    subtype = body['subType']

    if subtype != "Icy body":
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

# Nitrogen > 50%, argon present
# icy body
# temperature:
# found: 60.76 - 123.13
def fonticulua_upupam(genus, species, region, body, stars, colors):
    ret = []
    nitrogen = body.get("atmosphereComposition", {}).get('Nitrogen', 0.0)
    argon = body.get("atmosphereComposition", {}).get('Argon', 0.0)
    if nitrogen < 50.0 or argon == 0.0:
        return ret

    temperature = body["surfaceTemperature"]

    if not 60.0 <= temperature <= 124.0:
        return ret

    subtype = body['subType']

    if subtype != "Icy body":
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

# Neon present, Argon absent
# icy body
# temperature: 50-80K
def fonticulua_segmentatus(genus, species, region, body, stars, colors):
    ret = []
    neon = body.get("atmosphereComposition", {}).get('Neon', 0.0)
    argon = body.get("atmosphereComposition", {}).get('Argon', 0.0)
    if neon < 0.1 or argon > 0.0:
        return ret

    temperature = body["surfaceTemperature"]

    if not 50.0 <= temperature <= 80.0:
        return ret

    subtype = body['subType']

    if subtype != "Icy body":
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

def check_fonticulua(region, body, stars):
    ret = []

    colors = {
        "O" : CANONN_COLOR_GY,
        "B" : CANONN_COLOR_LI,
        "A" : CANONN_COLOR_GR,
        "F" : CANONN_COLOR_YE,
        "G" : CANONN_COLOR_TE,
        "K" : CANONN_COLOR_EM,
        "M" : CANONN_COLOR_AM,
        "L" : CANONN_COLOR_MV,
        "T" : CANONN_COLOR_OR,
        "Y" : CANONN_COLOR_OC,
        "TTS" : CANONN_COLOR_RE,
        "Ae": CANONN_COLOR_MR,
        "W" : CANONN_COLOR_IN,
        "D" : CANONN_COLOR_TU,
        "N" : CANONN_COLOR_SG,
        "BH" : None,
        "C" : None,
    }

    genus = "Fonticulua"
    name = body["name"]
    if name in known_planets and genus in known_planets[name]:
        if len(known_planets[name]["by_genus"][genus]) > 2:
            print(name, "WTF", known_planets[name]["by_genus"][genus], file=sys.stderr)
        for e in known_planets[name]["by_genus"][genus]:
            ret.append((region, name, e, 1))
        return ret

    ret += fonticulua_campestris  (genus, "Campestris" , region, body, stars, colors)
    ret += fonticulua_digitos     (genus, "Digitos"    , region, body, stars, colors)
    ret += fonticulua_fluctus     (genus, "Fluctus"    , region, body, stars, colors)
    ret += fonticulua_lapida      (genus, "Lapida"     , region, body, stars, colors)
    ret += fonticulua_segmentatus (genus, "Segmentatus", region, body, stars, colors)
    ret += fonticulua_upupam      (genus, "Upupam"     , region, body, stars, colors)
    return ret

# CO2 >= 97.5%
# 146-196K
# Rocky
def frutexa_acus(genus, species, region, body, stars, colors):
    ret = []

    # Orion-Cygnus Arm including Odin’s Hold and Galactic Centre
    if region not in ARM_ORION_CYGNUS | set(["Odin’s Hold", "Galactic Centre"]):
        return ret

    co2 = body.get("atmosphereComposition", {}).get('Carbon dioxide', 0.0)
    if co2 < 97.5:
        return ret

    temperature = body["surfaceTemperature"]

    if not 146.0 <= temperature <= 196.0:
        return ret

    subtype = body['subType']

    if subtype != "Rocky body":
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret


# SO2 100%
# 132-167K
# HMC, Rocky
def frutexa_collum(genus, species, region, body, stars, colors):
    ret = []

    so2 = body.get("atmosphereComposition", {}).get('Sulphur dioxide', 0.0)
    if so2 < 100.0:
        return ret

    temperature = body["surfaceTemperature"]

    if not 132.0 <= temperature <= 167.0: # one planet with 210K
        return ret

    subtype = body['subType']

    if subtype not in ["High metal content world", "Rocky body"]:
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

# CO2 >= 97.5%
# 146-196K
def frutexa_fera(genus, species, region, body, stars, colors):
    ret = []

    # Outer Arm including Empyrean Straits and Galactic Centre
    if region not in ARM_OUTER | set(["Empyrean Straits", "Galactic Centre"]):
        return ret

    co2 = body.get("atmosphereComposition", {}).get('Carbon dioxide', 0.0)
    if co2 < 97.5:
        return ret

    temperature = body["surfaceTemperature"]

    if not 146.0 <= temperature <= 196.0: # one planet with 210K
        return ret

    subtype = body['subType']

    if subtype != "Rocky body":
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

# Ammonia >= 99%
# 152-177K
# Rocky
def frutexa_flabellum(genus, species, region, body, stars, colors):
    ret = []

    # NOT Scutum-Centaurus Arm
    if region in ARM_SCUTUM_CENTAURUS | set(["Odin’s Hold", "Galactic Centre"]):
        return ret

    ammonia = body.get("atmosphereComposition", {}).get('Ammonia', 0.0)
    if ammonia < 99.0:
        return ret

    temperature = body["surfaceTemperature"]

    if not 152.0 <= temperature <= 177.0:
        return ret

    subtype = body['subType']

    if subtype != "Rocky body":
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

# Ammonia 100%
# 152-177K
# Rocky
def frutexa_flammasis(genus, species, region, body, stars, colors):
    ret = []

    # Scutum-Centaurus Arm including Odin’s Hold and Galactic Centre
    if region not in ARM_SCUTUM_CENTAURUS | set(["Odin’s Hold", "Galactic Centre"]):
        return ret

    ammonia = body.get("atmosphereComposition", {}).get('Ammonia', 0.0)
    if ammonia < 100.0:
        return ret

    temperature = body["surfaceTemperature"]

    if not 152.0 <= temperature <= 177.0:
        return ret

    subtype = body['subType']

    if subtype != "Rocky body":
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

# Ammonia 100%, 152-176K
# CO2 > 97.5%, 146-195K
# Water 100%, 390-400K
# No volcanism
def frutexa_metallicum(genus, species, region, body, stars, colors):
    ret = []

    valid = False

    temperature = body["surfaceTemperature"]
    water = body.get("atmosphereComposition", {}).get('Water', 0.0)
    if water == 100.0 and 390.0 <= temperature <= 400.0:
        valid = True

    ammonia = body.get("atmosphereComposition", {}).get('Ammonia', 0.0)
    if ammonia == 100.0 and 152.0 <= temperature <= 176.0:
        valid = True

    co2 = body.get("atmosphereComposition", {}).get('Carbon dioxide', 0.0)
    if co2 >= 97.5 and 146.0 <= temperature <= 195.0:
        valid = True

    if not valid:
        return ret

    subtype = body['subType']

    if subtype != "High metal content world":
        return ret

    volcanism = body.get("volcanism", "No volcanism")

    if volcanism != "No volcanism":
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

# Water 100%
# 392-452K
# Rocky
# No volcanism
def frutexa_sponsae(genus, species, region, body, stars, colors):
    ret = []

    water = body.get("atmosphereComposition", {}).get('Water', 0.0)
    if water < 100.0:
        return ret

    temperature = body["surfaceTemperature"]

    if not 392.0 <= temperature <= 452.0:
        return ret

    subtype = body['subType']

    if subtype != "Rocky body":
        return ret

    volcanism = body.get("volcanism", "No volcanism")

    if volcanism != "No volcanism":
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

def check_frutexa(region, body, stars):
    ret = []

    colors = {
        "O" : CANONN_COLOR_YE,
        "B" : CANONN_COLOR_LI,
        "A" : None,
        "F" : CANONN_COLOR_GR,
        "G" : CANONN_COLOR_EM,
        "K" : None,
        "M" : CANONN_COLOR_GY,
        "L" : CANONN_COLOR_TE,
        "T" : None,
        "Y" : None,
        "TTS" : CANONN_COLOR_MV,
        "Ae": None,
        "W" : CANONN_COLOR_OR,
        "D" : CANONN_COLOR_IN,
        "N" : CANONN_COLOR_RE,
        "BH" : None,
        "C" : None,
    }

    genus = "Frutexa"
    name = body["name"]
    if name in known_planets and genus in known_planets[name]:
        if len(known_planets[name]["by_genus"][genus]) > 2:
            print(name, "WTF", known_planets[name]["by_genus"][genus], file=sys.stderr)
        for e in known_planets[name]["by_genus"][genus]:
            ret.append((region, name, e, 1))
        return ret

    ret += frutexa_acus       (genus, "Acus"      , region, body, stars, colors)
    ret += frutexa_collum     (genus, "Collum"    , region, body, stars, colors)
    ret += frutexa_fera       (genus, "Fera"      , region, body, stars, colors)
    ret += frutexa_flabellum  (genus, "Flabellum" , region, body, stars, colors)
    ret += frutexa_flammasis  (genus, "Flammasis" , region, body, stars, colors)
    ret += frutexa_metallicum (genus, "Metallicum", region, body, stars, colors)
    ret += frutexa_sponsae    (genus, "Sponsae"   , region, body, stars, colors)
    return ret

# CO2 >= 97.5%
# 180-196K
def osseus_cornibus(genus, species, region, body, stars, colors):
    ret = []
    # Perseus Arm including Ryker’s Hope and Galactic Centre
    if region not in ARM_PERSEUS | set(["Ryker’s Hope", "Galactic Centre"]):
        return ret

    co2 = body.get("atmosphereComposition", {}).get('Carbon dioxide', 0.0)
    if co2 < 97.5:
        return ret

    temperature = body["surfaceTemperature"]

    if not 180.0 <= temperature <= 196.0:
        return ret

    volcanism = body.get("volcanism", "No volcanism")

    if volcanism != "No volcanism":
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

# CO2 >= 97.5%
# 180-190K
def osseus_fractus(genus, species, region, body, stars, colors):
    ret = []
    # NOT Perseus Arm but including Odin’s Hold and Empyrean Straits
    if region in ARM_PERSEUS | set(["Ryker’s Hope", "Galactic Centre"]):
        return ret

    co2 = body.get("atmosphereComposition", {}).get('Carbon dioxide', 0.0)
    if co2 < 97.5:
        return ret

    temperature = body["surfaceTemperature"]

    if not 180.0 <= temperature <= 190.0:
        return ret

    volcanism = body.get("volcanism", "No volcanism")

    if volcanism != "No volcanism":
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

# CO2 >= 97.5%
# 191-197K
def osseus_pellebantus(genus, species, region, body, stars, colors):
    ret = []
    # NOT Perseus Arm but including Odin’s Hold and Empyrean Straits
    if region in ARM_PERSEUS | set(["Ryker’s Hope", "Galactic Centre"]):
        return ret

    co2 = body.get("atmosphereComposition", {}).get('Carbon dioxide', 0.0)
    if co2 < 97.5:
        return ret

    temperature = body["surfaceTemperature"]

    if not 191.0 <= temperature <= 197.0:
        return ret

    volcanism = body.get("volcanism", "No volcanism")

    if volcanism != "No volcanism":
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

# Ammonia > 99%
# 160-177K
# Rocky, HMC
def osseus_spiralis(genus, species, region, body, stars, colors):
    ret = []
    ammonia = body.get("atmosphereComposition", {}).get('Ammonia', 0.0)
    if ammonia < 99.0:
        return ret

    temperature = body["surfaceTemperature"]

    if not 160.0 <= temperature <= 177.0:
        return ret

    subtype = body['subType']

    if subtype not in ["High metal content world", "Rocky body"]:
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

def check_osseus(region, body, stars):
    ret = []

    colors = {
        "O" : CANONN_COLOR_YE,
        "B" : None,
        "A" : CANONN_COLOR_LI,
        "F" : CANONN_COLOR_TU,
        "G" : CANONN_COLOR_GY,
        "K" : CANONN_COLOR_IN,
        "M" : None,
        "L" : None,
        "T" : CANONN_COLOR_EM,
        "Y" : CANONN_COLOR_MR,
        "TTS" : CANONN_COLOR_GR,
        "Ae": None,
        "W" : None,
        "D" : None,
        "N" : None,
        "BH" : None,
        "C" : None,
    }

    genus = "Osseus"
    name = body["name"]
    if name in known_planets and genus in known_planets[name]:
        if len(known_planets[name]["by_genus"][genus]) > 2:
            print(name, "WTF", known_planets[name]["by_genus"][genus], file=sys.stderr)
        for e in known_planets[name]["by_genus"][genus]:
            ret.append((region, name, e, 1))
        return ret

    ret += osseus_cornibus    (genus, "Cornibus"   , region, body, stars, colors)
    ret += osseus_fractus     (genus, "Fractus"    , region, body, stars, colors)
    ret += osseus_pellebantus (genus, "Pellebantus", region, body, stars, colors)
    ret += osseus_spiralis    (genus, "Spiralis"   , region, body, stars, colors)
    return ret

# SO2
# 132-273K
def recepta_umbrux(genus, species, region, body, stars, colors):
    ret = []

    so2 = body.get("atmosphereComposition", {}).get('Sulphur dioxide', 0.0)
    if so2 == 0.0:
        return ret

    temperature = body["surfaceTemperature"]

    if not 132.0 <= temperature <= 273.0:
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

def check_recepta(region, body, stars):
    ret = []

    colors = {
        "O" : None,
        "B" : CANONN_COLOR_TU,
        "A" : CANONN_COLOR_AM,
        "F" : CANONN_COLOR_MV,
        "G" : CANONN_COLOR_OR,
        "K" : CANONN_COLOR_RE,
        "M" : CANONN_COLOR_MR,
        "L" : CANONN_COLOR_OC,
        "T" : CANONN_COLOR_TE,
        "Y" : CANONN_COLOR_LI,
        "TTS" : CANONN_COLOR_SG,
        "Ae": CANONN_COLOR_GY,
        "W" : None,
        "D" : CANONN_COLOR_YE,
        "N" : CANONN_COLOR_EM,
        "BH" : None,
        "C" : None,
    }

    genus = "Recepta"
    name = body["name"]
    if name in known_planets and genus in known_planets[name]:
        if len(known_planets[name]["by_genus"][genus]) > 2:
            print(name, "WTF", known_planets[name]["by_genus"][genus], file=sys.stderr)
        for e in known_planets[name]["by_genus"][genus]:
            ret.append((region, name, e, 1))
        return ret

    ret += recepta_umbrux(genus, "Umbrux", region, body, stars, colors)
    return ret

# SO2 > 50%
def stratum_araneamus(genus, species, region, body, stars, colors):
    ret = []

    # 0.550627 = 5.4 m/s^2
    gravity = body["gravity"]
    if gravity > 0.550273:
        return ret

    so2 = body.get("atmosphereComposition", {}).get('Sulphur dioxide', 0.0)
    if so2 <= 50.0:
        return ret

    temperature = body["surfaceTemperature"]

    if temperature <= 165.0:
        return ret

    # only Emerald variant spawns
    string = f"Stratum Araneamus - {CANONN_COLOR_EM}"
    region_priority = get_color_priority(region, string)
    ret.append((region, body["name"], string, region_priority))

    return ret

# SO2 or CO2 in atmosphere
# 191+K
def stratum_cucumisis(genus, species, region, body, stars, colors):
    ret = []

    # Sagittarius-Carina Arm including Odin’s Hold and Galactic Centre
    if region not in ARM_SAGITTARIUS_CARINA | set(["Odin’s Hold", "Galactic Centre"]):
        return ret

    so2 = body.get("atmosphereComposition", {}).get('Sulphur dioxide', 0.0)
    co2 = body.get("atmosphereComposition", {}).get('Carbon dioxide', 0.0)
    if so2 == 0.0 and co2 == 0.0:
        return ret

    temperature = body["surfaceTemperature"]

    if temperature <= 191.0:
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

# SO2 any rate or CO2 100%
# 165-190K
def stratum_excutitus(genus, species, region, body, stars, colors):
    ret = []

    # 4.64 m/s^2 - unlikely
    gravity = body["gravity"]
    if gravity > 0.473151:
        return ret

    # Orion-Cygnus Arm including Odin’s Hold and Galactic Centre
    if region not in ARM_ORION_CYGNUS | set(["Odin’s Hold", "Galactic Centre"]):
        return ret

    so2 = body.get("atmosphereComposition", {}).get('Sulphur dioxide', 0.0)
    co2 = body.get("atmosphereComposition", {}).get('Carbon dioxide', 0.0)
    if so2 == 0.0 and co2 < 100.0:
        return ret

    temperature = body["surfaceTemperature"]

    if not 165.0 <= temperature <= 190.0:
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

# SO2 any rate or CO2 100%
def stratum_frigus(genus, species, region, body, stars, colors):
    ret = []

    # 0.550627 = 5.4 m/s^2
    gravity = body["gravity"]
    if gravity > 0.550600:
        return ret

    # Perseus Arm including Ryker’s Hope and excluding Galactic Centre
    if region not in (ARM_PERSEUS | set(["Ryker’s Hope"])) - set(["Galactic Centre"]):
        return ret

    so2 = body.get("atmosphereComposition", {}).get('Sulphur dioxide', 0.0)
    co2 = body.get("atmosphereComposition", {}).get('Carbon dioxide', 0.0)
    if so2 == 0.0 and co2 < 100.0:
        return ret

    temperature = body["surfaceTemperature"]

    if temperature <= 191.0:
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

# Ammonia >= 75%
# rocky body
def stratum_laminamus(genus, species, region, body, stars, colors):
    ret = []

    # 0.342612 = 3.36 m/s^2
    gravity = body["gravity"]
    if gravity > 0.342592:
        return ret

    # Orion-Cygnus Arm including Odin’s Hold and Galactic Centre
    if region not in ARM_ORION_CYGNUS | set(["Odin’s Hold", "Galactic Centre"]):
        return ret

    ammonia = body.get("atmosphereComposition", {}).get('Ammonia', 0.0)
    if ammonia < 75.0:
        return ret

    temperature = body["surfaceTemperature"]

    if not 165.0 <= temperature <= 177.0:
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

# SO2 any rate or CO2 100%
# 165-190K
def stratum_limaxus(genus, species, region, body, stars, colors):
    ret = []

    # 0.377281 = 3.7 m/s^2
    gravity = body["gravity"]
    if gravity > 0.377205:
        return ret

    # Scutum-Centaurus Arm excluding Odin’s Hold and Galactic Centre
    if region not in ARM_SCUTUM_CENTAURUS - set(["Odin’s Hold", "Galactic Centre"]):
        return ret

    so2 = body.get("atmosphereComposition", {}).get('Sulphur dioxide', 0.0)
    co2 = body.get("atmosphereComposition", {}).get('Carbon dioxide', 0.0)
    if so2 == 0.0 and co2 < 100.0:
        return ret

    temperature = body["surfaceTemperature"]

    if not 165.0 <= temperature <= 190.0:
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

# CO2 in atmosphere, SO2 < 50%, 165+K
# Water 100%, 390-450K
# Ammonia 70+%, 165-176K
# Rocky
def stratum_paleas(genus, species, region, body, stars, colors):
    ret = []

    # 5.835 m/s^2 - unlikely
    gravity = body["gravity"]
    if gravity > 0.594972:
        return ret

    valid = False

    temperature = body["surfaceTemperature"]
    water = body.get("atmosphereComposition", {}).get('Water', 0.0)
    if water == 100.0 and 390.0 <= temperature <= 450.0:
        valid = True

    so2 = body.get("atmosphereComposition", {}).get('Sulphur dioxide', 0.0)
    co2 = body.get("atmosphereComposition", {}).get('Carbon dioxide', 0.0)
    if co2 > 0.0 and so2 < 50.0 and temperature >= 165.0:
        valid = True

    ammonia = body.get("atmosphereComposition", {}).get('Ammonia', 0.0)
    if ammonia >= 70.0 and 165.0 <= temperature <= 176.0:
        valid = True

    if not valid:
        return ret

    subtype = body['subType']

    if subtype != "Rocky body":
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

# Temp >= 165 K
# HMC
def stratum_tectonicas(genus, species, region, body, stars, colors):
    ret = []

    temperature = body["surfaceTemperature"]

    if temperature < 165.0:
        return ret

    subtype = body['subType']

    if subtype != "High metal content world":
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

def check_stratum(region, body, stars):
    ret = []

    colors = {
        "O" : None,
        "B" : None,
        "A" : None,
        "F" : CANONN_COLOR_EM,
        "G" : None,
        "K" : CANONN_COLOR_LI,
        "M" : CANONN_COLOR_GR,
        "L" : CANONN_COLOR_TU,
        "T" : CANONN_COLOR_GY,
        "Y" : CANONN_COLOR_IN,
        "TTS" : CANONN_COLOR_AM,
        "Ae": CANONN_COLOR_TE,
        "W" : CANONN_COLOR_RE,
        "D" : CANONN_COLOR_MV,
        "N" : None,
        "BH" : None,
        "C" : None,
    }

    genus = "Stratum"
    name = body["name"]
    if name in known_planets and genus in known_planets[name]:
        if len(known_planets[name]["by_genus"][genus]) > 2:
            print(name, "WTF", known_planets[name]["by_genus"][genus], file=sys.stderr)
        for e in known_planets[name]["by_genus"][genus]:
            ret.append((region, name, e, 1))
        return ret

    ret += stratum_araneamus  (genus, "Araneamus" , region, body, stars, colors)
    ret += stratum_cucumisis  (genus, "Cucumisis" , region, body, stars, colors)
    ret += stratum_excutitus  (genus, "Excutitus" , region, body, stars, colors)
    ret += stratum_frigus     (genus, "Frigus"    , region, body, stars, colors)
    ret += stratum_laminamus  (genus, "Laminamus" , region, body, stars, colors)
    ret += stratum_limaxus    (genus, "Limaxus"   , region, body, stars, colors)
    ret += stratum_paleas     (genus, "Paleas"    , region, body, stars, colors)
    ret += stratum_tectonicas (genus, "Tectonicas", region, body, stars, colors)
    return ret

# CO2 > 97.5%
# 160-197K
# Rocky
def tubus_cavas(genus, species, region, body, stars, colors):
    ret = []

    # Scutum-Centaurus Arm including Odin’s Hold and Galactic Centre
    if region not in ARM_SCUTUM_CENTAURUS | set(["Odin’s Hold", "Galactic Centre"]):
        return ret

    co2 = body.get("atmosphereComposition", {}).get('Carbon dioxide', 0.0)
    if co2 <= 97.5:
        return ret

    temperature = body["surfaceTemperature"]

    if not 160.0 <= temperature <= 197.0:
        return ret

    subtype = body['subType']

    if subtype != "Rocky body":
        return ret

    volcanism = body.get("volcanism", "No volcanism")

    if volcanism != "No volcanism":
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

# CO2 > 97.5%
# 160-197K
# Rocky
def tubus_compagibus(genus, species, region, body, stars, colors):
    ret = []

    # Sagittarius-Carina Arm including Odin’s Hold and Galactic Centre
    if region not in ARM_SAGITTARIUS_CARINA | set(["Odin’s Hold", "Galactic Centre"]):
        return ret

    co2 = body.get("atmosphereComposition", {}).get('Carbon dioxide', 0.0)
    if co2 <= 97.5:
        return ret

    temperature = body["surfaceTemperature"]

    if not 160.0 <= temperature <= 197.0:
        return ret

    subtype = body['subType']

    if subtype != "Rocky body":
        return ret

    volcanism = body.get("volcanism", "No volcanism")

    if volcanism != "No volcanism":
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

# CO2 > 97.5%
# 160-196K
# Rocky
def tubus_conifer(genus, species, region, body, stars, colors):
    ret = []

    # Perseus Arm including Ryker’s Hope and Galactic Centre
    if region not in ARM_PERSEUS | set(["Ryker’s Hope", "Galactic Centre"]):
        return ret

    co2 = body.get("atmosphereComposition", {}).get('Carbon dioxide', 0.0)
    if co2 <= 97.5:
        return ret

    temperature = body["surfaceTemperature"]

    if not 160.0 <= temperature <= 196.0:
        return ret

    subtype = body['subType']

    if subtype != "Rocky body":
        return ret

    volcanism = body.get("volcanism", "No volcanism")

    if volcanism != "No volcanism":
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

# 100% ammonia
# 160-177K
def tubus_rosarium(genus, species, region, body, stars, colors):
    ret = []

    co2 = body.get("atmosphereComposition", {}).get('Carbon dioxide', 0.0)
    if co2 <= 97.5:
        return ret

    temperature = body["surfaceTemperature"]

    if not 160.0 <= temperature <= 177.0:
        return ret

    subtype = body['subType']

    if subtype != "Rocky body":
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

# HMC
# 160-194K
# Carbon Dioxide >= 98% or Ammonia 100%
def tubus_sororibus(genus, species, region, body, stars, colors):
    ret = []

    ammonia = body.get("atmosphereComposition", {}).get('Ammonia', 0.0)
    co2 = body.get("atmosphereComposition", {}).get('Carbon dioxide', 0.0)
    if ammonia < 100.0 and co2 <= 98.0:
        return ret

    temperature = body["surfaceTemperature"]

    if not 160.0 <= temperature <= 194.0:
        return ret

    subtype = body['subType']

    if subtype != "High metal content world":
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

def check_tubus(region, body, stars):
    ret = []
    colors = {
        "O" : CANONN_COLOR_GR,
        "B" : CANONN_COLOR_EM,
        "A" : CANONN_COLOR_IN,
        "F" : CANONN_COLOR_GY,
        "G" : CANONN_COLOR_RE,
        "K" : CANONN_COLOR_MR,
        "M" : CANONN_COLOR_TE,
        "L" : CANONN_COLOR_TU,
        "T" : CANONN_COLOR_MV,
        "Y" : None,
        "TTS" : CANONN_COLOR_OC,
        "Ae": None,
        "W" : CANONN_COLOR_LI,
        "D" : CANONN_COLOR_YE,
        "N" : CANONN_COLOR_AM,
        "BH" : None,
        "C" : None,
    }

    genus = "Tubus"
    name = body["name"]
    if name in known_planets and genus in known_planets[name]:
        if len(known_planets[name]["by_genus"][genus]) > 2:
            print(name, "WTF", known_planets[name]["by_genus"][genus], file=sys.stderr)
        for e in known_planets[name]["by_genus"][genus]:
            ret.append((region, name, e, 1))
        return ret

    ret += tubus_cavas      (genus, "Cavas"     , region, body, stars, colors)
    ret += tubus_compagibus (genus, "Compagibus", region, body, stars, colors)
    ret += tubus_conifer    (genus, "Conifer"   , region, body, stars, colors)
    ret += tubus_rosarium   (genus, "Rosarium"  , region, body, stars, colors)
    ret += tubus_sororibus  (genus, "Sororibus" , region, body, stars, colors)
    return ret

# CO2 >= 97.5%
# 175-180K
def tussock_albata(genus, species, region, body, stars, colors):
    ret = []

    # Sagittarius-Carina Arm, Perseus Arm including Ryker’s Hope but excluding Galactic Centre
    if region not in (ARM_SAGITTARIUS_CARINA | ARM_PERSEUS | set(["Ryker’s Hope"])) - set(["Galactic Centre"]):
        return ret

    co2 = body.get("atmosphereComposition", {}).get('Carbon dioxide', 0.0)
    if co2 < 97.5:
        return ret

    temperature = body["surfaceTemperature"]

    if not 175.0 <= temperature <= 180.0:
        return ret

    subtype = body['subType']

    if subtype not in ["High metal content world", "Rocky body"]:
        return ret

    volcanism = body.get("volcanism", "No volcanism")

    if volcanism != "No volcanism":
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

# Argon > 50%
# Methane 100%
# 80-129K
def tussock_capillum(genus, species, region, body, stars, colors):
    ret = []

    argon = body.get("atmosphereComposition", {}).get('Argon', 0.0)
    methane = body.get("atmosphereComposition", {}).get('Methane', 0.0)
    if 0.0 < methane < 100.0 or argon < 50.0:
        return ret

    temperature = body["surfaceTemperature"]

    if not 80.0 <= temperature <= 129.0:
        return ret

    subtype = body['subType']

    if subtype not in ["Rocky body", "Rocky Ice world"]:
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

# CO2 >= 97.5%
# 181-190K
def tussock_caputus(genus, species, region, body, stars, colors):
    ret = []

    # Sagittarius-Carina Arm, Perseus Arm including Ryker’s Hope but excluding Galactic Centre
    if region not in (ARM_SAGITTARIUS_CARINA | ARM_PERSEUS | set(["Ryker’s Hope"])) - set(["Galactic Centre"]):
        return ret

    co2 = body.get("atmosphereComposition", {}).get('Carbon dioxide', 0.0)
    if co2 < 97.5:
        return ret

    temperature = body["surfaceTemperature"]

    if not 181.0 <= temperature <= 190.0:
        return ret

    subtype = body['subType']

    if subtype not in ["High metal content world", "Rocky body"]:
        return ret

    volcanism = body.get("volcanism", "No volcanism")

    if volcanism != "No volcanism":
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

# 100% ammonia
# 152-177K
def tussock_catena(genus, species, region, body, stars, colors):
    ret = []

    # Scutum-Centaurus Arm excluding Galactic Central Regions
    if region not in ARM_SCUTUM_CENTAURUS - ARM_CENTRAL:
        return ret

    ammonia = body.get("atmosphereComposition", {}).get('Ammonia', 0.0)
    if ammonia < 100.0:
        return ret

    temperature = body["surfaceTemperature"]

    if not 152.0 <= temperature <= 177.0:
        return ret

    subtype = body['subType']

    if subtype not in ["High metal content world", "Rocky body"]:
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

# 100% Ammonia
# 152-177K
def tussock_cultro(genus, species, region, body, stars, colors):
    ret = []

    # Orion-Cygnus Arm including Odin’s Hold, Empyrean Straits and Galactic Centre
    if region not in ARM_ORION_CYGNUS | set(["Odin’s Hold", "Empyrean Straits", "Galactic Centre"]):
        return ret

    ammonia = body.get("atmosphereComposition", {}).get('Ammonia', 0.0)
    if ammonia < 100.0:
        return ret

    temperature = body["surfaceTemperature"]

    if not 152.0 <= temperature <= 177.0:
        return ret

    subtype = body['subType']

    if subtype not in ["High metal content world", "Rocky body"]:
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

# 100% ammonia
# 152-177K
def tussock_divisa(genus, species, region, body, stars, colors):
    ret = []

    # Perseus Arm including Ryker’s Hope
    if region not in ARM_PERSEUS | set(["Ryker’s Hope"]):
        return ret

    ammonia = body.get("atmosphereComposition", {}).get('Ammonia', 0.0)
    if ammonia < 100.0:
        return ret

    temperature = body["surfaceTemperature"]

    if not 152.0 <= temperature <= 177.0:
        return ret

    subtype = body['subType']

    if subtype not in ["High metal content world", "Rocky body"]:
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

# CO2 > 97.5%
# 150-170K
def tussock_ignis(genus, species, region, body, stars, colors):
    ret = []

    # Sagittarius-Carina Arm and Perseus Arm including Ryker’s Hope
    if region not in ARM_SAGITTARIUS_CARINA | ARM_PERSEUS | set(["Ryker’s Hope"]):
        return ret

    co2 = body.get("atmosphereComposition", {}).get('Carbon dioxide', 0.0)
    if co2 < 97.5:
        return ret

    temperature = body["surfaceTemperature"]

    if not 150.0 <= temperature <= 170.0:
        return ret

    subtype = body['subType']

    if subtype not in ["High metal content world", "Rocky body"]:
        return ret

    volcanism = body.get("volcanism", "No volcanism")

    if volcanism != "No volcanism":
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

# CO2 > 97.5%
# 145-154K
def tussock_pennata(genus, species, region, body, stars, colors):
    ret = []

    # Sagittarius-Carina Arm and Perseus Arm including Ryker’s Hope
    if region not in ARM_SAGITTARIUS_CARINA | ARM_PERSEUS | set(["Ryker’s Hope"]):
        return ret

    co2 = body.get("atmosphereComposition", {}).get('Carbon dioxide', 0.0)
    if co2 < 97.5:
        return ret

    temperature = body["surfaceTemperature"]

    if not 145.0 <= temperature <= 154.0:
        return ret

    subtype = body['subType']

    if subtype not in ["High metal content world", "Rocky body"]:
        return ret

    volcanism = body.get("volcanism", "No volcanism")

    if volcanism != "No volcanism":
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

# CO2 > 97.5%
# 146-196K
def tussock_pennatis(genus, species, region, body, stars, colors):
    ret = []

    # Outer Arm including Empyrean Straits and Galactic Centre
    if region not in ARM_OUTER | set(["Empyrean Straits", "Galactic Centre"]):
        return ret

    co2 = body.get("atmosphereComposition", {}).get('Carbon dioxide', 0.0)
    if co2 < 97.5:
        return ret

    temperature = body["surfaceTemperature"]

    if not 146.0 <= temperature <= 196.0:
        return ret

    subtype = body['subType']

    if subtype not in ["High metal content world", "Rocky body"]:
        return ret

    volcanism = body.get("volcanism", "No volcanism")

    if volcanism != "No volcanism":
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

# CO2 > 97.5%
# 145-197K
def tussock_propagito(genus, species, region, body, stars, colors):
    ret = []

    # Scutum-Centaurus Arm including Odin’s Hold and Galactic Centre
    if region not in ARM_SCUTUM_CENTAURUS | set(["Odin’s Hold", "Galactic Centre"]):
        return ret

    co2 = body.get("atmosphereComposition", {}).get('Carbon dioxide', 0.0)
    if co2 < 97.5:
        return ret

    temperature = body["surfaceTemperature"]

    if not 145.0 <= temperature <= 197.0:
        return ret

    subtype = body['subType']

    if subtype not in ["High metal content world", "Rocky body"]:
        return ret

    volcanism = body.get("volcanism", "No volcanism")

    if volcanism != "No volcanism":
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

# CO2 > 97.5%
# 171-174K
def tussock_serrati(genus, species, region, body, stars, colors):
    ret = []

    # Sagittarius-Carina Arm and Perseus Arm including Ryker’s Hope but excluding Galactic Centre
    if region not in (ARM_SAGITTARIUS_CARINA | ARM_PERSEUS | set(["Ryker’s Hope"])) - set(["Galactic Centre"]):
        return ret

    co2 = body.get("atmosphereComposition", {}).get('Carbon dioxide', 0.0)
    if co2 < 97.5:
        return ret

    temperature = body["surfaceTemperature"]

    if not 171.0 <= temperature <= 174.0:
        return ret

    subtype = body['subType']

    if subtype not in ["High metal content world", "Rocky body"]:
        return ret

    volcanism = body.get("volcanism", "No volcanism")

    if volcanism != "No volcanism":
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

# SO2 100%
# 132-207K
def tussock_stigmasis(genus, species, region, body, stars, colors):
    ret = []

    so2 = body.get("atmosphereComposition", {}).get('Sulphur dioxide', 0.0)
    if so2 < 100.0:
        return ret

    temperature = body["surfaceTemperature"]

    if not 132.0 <= temperature <= 207.0:
        return ret

    subtype = body['subType']

    if subtype not in ["High metal content world", "Rocky body"]:
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

# CO2 > 97.5%
# 191-196K
def tussock_triticum(genus, species, region, body, stars, colors):
    ret = []

    # Sagittarius-Carina Arm and Perseus Arm including Ryker’s Hope but excluding Galactic Centre
    if region not in (ARM_SAGITTARIUS_CARINA | ARM_PERSEUS | set(["Ryker’s Hope"])) - set(["Galactic Centre"]):
        return ret

    co2 = body.get("atmosphereComposition", {}).get('Carbon dioxide', 0.0)
    if co2 < 97.5:
        return ret

    temperature = body["surfaceTemperature"]

    if not 191.0 <= temperature <= 196.0:
        return ret

    subtype = body['subType']

    if subtype not in ["High metal content world", "Rocky body"]:
        return ret

    volcanism = body.get("volcanism", "No volcanism")

    if volcanism != "No volcanism":
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

# CO2 > 97.5%
# 155-160K
def tussock_ventusa(genus, species, region, body, stars, colors):
    ret = []

    # Sagittarius-Carina Arm and Perseus Arm including Ryker’s Hope but excluding Galactic Centre
    if region not in (ARM_SAGITTARIUS_CARINA | ARM_PERSEUS | set(["Ryker’s Hope"])) - set(["Galactic Centre"]):
        return ret

    co2 = body.get("atmosphereComposition", {}).get('Carbon dioxide', 0.0)
    if co2 < 97.5:
        return ret

    temperature = body["surfaceTemperature"]

    if not 155.0 <= temperature <= 160.0:
        return ret

    subtype = body['subType']

    if subtype not in ["High metal content world", "Rocky body"]:
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

# Water 100%
# 390-450K
def tussock_virgam(genus, species, region, body, stars, colors):
    ret = []

    water = body.get("atmosphereComposition", {}).get('Water', 0.0)
    if water < 100.0:
        return ret

    temperature = body["surfaceTemperature"]

    if not 390.0 <= temperature <= 450.0:
        return ret

    subtype = body['subType']

    if subtype not in ["High metal content world", "Rocky body"]:
        return ret

    spec = f"{genus} {species}"
    set_colors = get_possible_colors(spec, body, stars, colors)

    for color in set_colors:
        string = f"{spec} - {color}"
        region_priority = get_color_priority(region, string)
        ret.append((region, body["name"], string, region_priority))

    return ret

def check_tussock(region, body, stars):
    ret = []

    # Special Case:
    # Yellow spawns also near N
    # but it looks like something else
    colors = {
        "O" : None,
        "B" : None,
        "A" : None,
        "F" : CANONN_COLOR_YE,
        "G" : CANONN_COLOR_LI,
        "K" : CANONN_COLOR_GR,
        "M" : CANONN_COLOR_EM,
        "L" : CANONN_COLOR_SG,
        "T" : CANONN_COLOR_TE,
        "Y" : CANONN_COLOR_RE,
        "TTS" : None,
        "Ae": None,
        "W" : CANONN_COLOR_OR,
        "D" : CANONN_COLOR_MR,
        "N" : CANONN_COLOR_YE,
        "BH" : None,
        "C" : None,
    }

    genus = "Tussock"
    name = body["name"]
    if name in known_planets and genus in known_planets[name]:
        if len(known_planets[name]["by_genus"][genus]) > 2:
            print(name, "WTF", known_planets[name]["by_genus"][genus], file=sys.stderr)
        for e in known_planets[name]["by_genus"][genus]:
            ret.append((region, name, e, 1))
        return ret

    ret += tussock_albata    (genus, "Albata"   , region, body, stars, colors)
    ret += tussock_capillum  (genus, "Capillum" , region, body, stars, colors)
    ret += tussock_caputus   (genus, "Caputus"  , region, body, stars, colors)
    ret += tussock_catena    (genus, "Catena"   , region, body, stars, colors)
    ret += tussock_cultro    (genus, "Cultro"   , region, body, stars, colors)
    ret += tussock_divisa    (genus, "Divisa"   , region, body, stars, colors)
    ret += tussock_ignis     (genus, "Ignis"    , region, body, stars, colors)
    ret += tussock_pennata   (genus, "Pennata"  , region, body, stars, colors)
    ret += tussock_pennatis  (genus, "Pennatis" , region, body, stars, colors)
    ret += tussock_propagito (genus, "Propagito", region, body, stars, colors)
    ret += tussock_serrati   (genus, "Serrati"  , region, body, stars, colors)
    ret += tussock_stigmasis (genus, "Stigmasis", region, body, stars, colors)
    ret += tussock_triticum  (genus, "Triticum" , region, body, stars, colors)
    ret += tussock_ventusa   (genus, "Ventusa"  , region, body, stars, colors)
    ret += tussock_virgam    (genus, "Virgam"   , region, body, stars, colors)
    return ret

global_entries = set()
regional_entries = {}

known_planets = {}

def get_odyssey_genus(name):
    if name.startswith("$Codex_Ent_Bacterial"):
        return "Bacterium"
    if name.startswith("$Codex_Ent_Tussocks"):
        return "Tussock"
    if name.startswith("$Codex_Ent_Stratum"):
        return "Stratum"
    if name.startswith("$Codex_Ent_Conchas"):
        return "Concha"
    if name.startswith("$Codex_Ent_Shrubs"):
        return "Frutexa"
    if name.startswith("$Codex_Ent_Aleoids"):
        return "Aleoida"
    if name.startswith("$Codex_Ent_Fungoids"):
        return "Fungoids"
    if name.startswith("$Codex_Ent_Tubus"):
        return "Tubus"
    if name.startswith("$Codex_Ent_Fonticulus"):
        return "Fonticulua"
    if name.startswith("$Codex_Ent_Fumerolas"):
        return "Fumerola"
    if name.startswith("$Codex_Ent_Electricae"):
        return "Electricae"
    if name.startswith("$Codex_Ent_Osseus"):
        return "Osseus"
    if name.startswith("$Codex_Ent_Cactoid"):
        return "Cactoida"
    if name.startswith("$Codex_Ent_Clypeus"):
        return "Clypeus"
    if name.startswith("$Codex_Ent_Recepta"):
        return "Recepta"
    return None

class Predictor:
    def __init__(self):
        # list of tuples: (region, system_name, species, priority)
        self.predicted = {}

        with gzip.open("codex.json.gz", "r") as codex:
            entries = json.load(codex)
            for entry in entries:
                if entry["hud_category"] == "Biology":
                    english_name = entry["english_name"]
                    name = entry["name"]
                    genus = get_odyssey_genus(name)
                    if genus is None:
                        continue

                    body = entry["body"]
                    if body not in known_planets:
                        known_planets[body] = {
                            "all_bio" : set(),
                            "by_genus" : {},
                        }

                    if genus not in known_planets[body]:
                        known_planets[body]["by_genus"][genus] = set()

                    known_planets[body]["by_genus"][genus].add(english_name)
                    known_planets[body]["all_bio"].add(english_name)

                    region = regions[entry["region_name"]]
                    global_entries.add(english_name)

                    if region not in regional_entries:
                        regional_entries[region] = set()

                    regional_entries[region].add(english_name)


    def process(self, system):
        stars = []
        planets = []

        region_data = findRegionForBoxel(system["id64"])["region"]
        if region_data is not None:
            region = region_data[1]
        else:
            region = "Out of bounds"

        bodies = {}

        for body in system["bodies"]:
            bodies[body["bodyId"]] = body

        for body in system["bodies"]:
            if "parents" in body:
                for parent in body["parents"]:
                    for key in parent:
                        id = parent[key]
                        if key == "Star" and (id not in bodies or "subType" not in bodies[id]):
                            #print(f'looks like star {id} is missing in system {system["name"]}, adding dummy M')
                            M_star = {
                                "name" : f"{system["name"]} dummy {id}",
                                "type" : "Star",
                                "bodyId" : id,
                                "subType" : "M (Red dwarf) Star",
                                "surfaceTemperature" : 2000,
                                "solarRadius" : 0.30,
                                "updateTime" : "1970-01-01",
                            }

                            system["bodies"].append(M_star)
                            bodies[id] = M_star


        for body in system["bodies"]:
            if body["type"] == "Star":
                stars.append(body)
                continue

            if body["type"] == "Planet":
                if body.get("subType", None) in ["Icy body", "Rocky Ice world", "Rocky body", "High metal content world", "Metal-rich body"]:
                    atmosphere_type = body.get("atmosphereType", "No atmosphere")

                    if "signals" in body and "$SAA_SignalType_Biological;" in body["signals"]["signals"] and body["name"] in known_planets:
                        signals_found = len(known_planets[body["name"]]["all_bio"])
                        signals_on_planet = body["signals"]["signals"]["$SAA_SignalType_Biological;"]
                        if signals_found > signals_on_planet:
                            print(f'WTF: {body["name"]} has {signals_on_planet} signals, found {signals_found}', file=sys.stderr)

                        if signals_found == signals_on_planet:
                            #print(f'Skipping {body["name"]}: all {signals_found} signals found', file=sys.stderr)
                            # all signals has been already found, skip the planet
                            continue

                    if atmosphere_type is not None and atmosphere_type.startswith("Thin"):
                        if body["updateTime"] >= "2021-05-19" and body["isLandable"] == False:
                            #print(f'Skipping non-landable in Odyssey body {body["name"]}, last updated {body["updateTime"]}')
                            continue

                        planets.append(body)

        # no valuable planets, skip the system
        if planets == []:
            return

        c = Coordinates(system["bodies"])
#        if system["name"] == "Col 359 Sector OT-Q d5-56":
#            c.get_all_coordinates()

        for star in stars:
            star["coordinates"] = c.get_coordinates(star["bodyId"])
            _ = get_mapped_star_type(star.get("subType", None))

        for planet in planets:
            planet["coordinates"] = c.get_coordinates(planet["bodyId"])
            # check for every possible bio
            gravity = planet["gravity"]

            predicted = []

            # maximum known 0.610985
            # 0.611807 = 6 m/s^2
            if gravity < 0.611807:
                predicted += check_bacterium(region, planet, stars)
                predicted += check_stratum(region, planet, stars)

            # 0.275313 = 2.7 m/s^2
            if gravity < 0.275313:
                predicted += check_aleoida(region, planet, stars)
                predicted += check_cactoida(region, planet, stars)
                predicted += check_clypeus(region, planet, stars)
                predicted += check_concha(region, planet, stars)
                predicted += check_fonticulua(region, planet, stars)
                predicted += check_frutexa(region, planet, stars)
                predicted += check_osseus(region, planet, stars)
                predicted += check_recepta(region, planet, stars)
                predicted += check_tussock(region, planet, stars)

            # 0.152952 = 1.5 m/s^2
            if gravity < 0.152952:
                predicted += check_tubus(region, planet, stars)

            # predicted: list of tuples
            # (region, body name, species name, priority)

            for entry in predicted:
                region, bodyname, species, priority = entry

                if region not in self.predicted:
                    self.predicted[region] = {}

                if species not in self.predicted[region]:
                    self.predicted[region][species] = {
                        "priority" : priority,
                        "locations" : [],
                    }

                self.predicted[region][species]["locations"].append({
                    "system" : system["name"],
                    "body" : bodyname,
                    "x" : system["coords"]["x"],
                    "y" : system["coords"]["y"],
                    "z" : system["coords"]["z"],
                })

    def finalize(self):
        with open("biopredictor.json", "w") as f:
            json.dump(self.predicted, f)
