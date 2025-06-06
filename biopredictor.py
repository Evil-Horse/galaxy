import gzip
import json
from RegionMap import findRegion
from distances import Coordinates
import sys
import math
from datetime import date, datetime, UTC

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
    "Ryker's Hope",
    "Odin's Hold",
])

ARM_OUTER = set([
    "Norma Arm",
    "Arcadian Stream",
    "Newton's Vault",
    "The Conduit",
    "Outer Arm",
    "Errant Marches",
    "The Formidine Rift",
    "Xibalba",
    "Kepler's Crest",
])

ARM_PERSEUS = set([
    "Izanami",
    "Outer Orion-Perseus Conflux",
    "Perseus Arm",
    "Vulcan Gate",
    "Elysian Shore",
    "Sanguineous Rim",
    "Achilles's Altar",
    "Lyra's Song",
    "Tenebrae",
])

ARM_SAGITTARIUS_CARINA = set([
    "Inner Orion-Perseus Conflux",
    "Orion-Cygnus Arm",
    "Temple",
    "Inner Orion Spur",
    "Hawking's Gap",
    "Dryman's Point",
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
    "Aquila's Halo",
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

def get_possible_stars(body, stars, threshold = 1.0):
    body_coordinates = body["coordinates"]
    brightnesses = {}
    for star in stars:
        star_type = get_mapped_star_type(star.get("subType", None))
        if star_type is None:
            #print(f'{star["name"]}: type is none')
            continue

        # get distance
        star_coordinates = star["coordinates"]
        dist_au_squared = (star_coordinates[0] - body_coordinates[0]) ** 2 + (star_coordinates[1] - body_coordinates[1]) ** 2 + (star_coordinates[2] - body_coordinates[2]) ** 2
        if dist_au_squared == 0.0:
            #print(f'{star["name"]}: dist is zero')
            continue

        if "solarRadius" not in star:
            #print(f'{star["name"]}: solar radius is unknown')
            continue

        brightness = star["solarRadius"] ** 2 * star["surfaceTemperature"] ** 4 / dist_au_squared
        brightnesses[star["name"]] = {
            "brightness" : brightness,
            "star_type" : star_type,
            "distance" : math.sqrt(dist_au_squared),
        }

    if len(brightnesses) == 0:
        return {}

    brightest = max(brightnesses, key=lambda x: brightnesses[x]["brightness"])

    above_threshold = {k: v for k, v in brightnesses.items() if v["brightness"] >= brightnesses[brightest]["brightness"] * threshold}
    return above_threshold

def get_possible_colors(valid_stars, species, colors, min_dist=None, max_dist=None):
    set_colors = set()

    for k, v in valid_stars.items():
        if min_dist is not None and min_dist > v["distance"]:
            continue

        if max_dist is not None and max_dist < v["distance"]:
            continue

        color = colors[v["star_type"]]
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

def check_region(genus, species, region):
    genus_species = f'{genus} {species}'

    all_regions = [
        "Aleoida Arcus",
        "Aleoida Coronamus",
        "Aleoida Gravis",
        "Bacterium Alcyoneum",
        "Bacterium Aurasus",
        "Bacterium Cerbrus",
        "Cactoida Vermis",
        "Clypeus Lacrimam",
        "Clypeus Margaritus",
        "Clypeus Speculumi",
        "Concha Aureolas",
        "Concha Labiata",
        "Fonticulua Campestris",
        "Fonticulua Digitos",
        "Fonticulua Fluctus",
        "Fonticulua Lapida",
        "Fonticulua Segmentatus",
        "Fonticulua Upupam",
        "Frutexa Collum",
        "Frutexa Metallicum",
        "Frutexa Sponsae",
        "Osseus Discus",
        "Osseus Pumice",
        "Osseus Spiralis",
        "Recepta Umbrux",
        "Stratum Araneamus",
        "Stratum Paleas",
        "Stratum Tectonicas",
        "Tubus Rosarium",
        "Tubus Sororibus",
        "Tussock Capillum",
        "Tussock Stigmasis",
        "Tussock Virgam",
    ]
    if genus_species in all_regions:
        return True

    if genus_species == "Aleoida Laminiae":
        # does not spawn: 15, 33, 34, 35
        if region in ["Outer Orion-Perseus Conflux", "Elysian Shore", "Sanguineous Rim", "Outer Orion Spur"]:
            return False

        # Orion-Cygnus Arm; Sagittarius-Carina Arm including Odin's Hold and Galactic Centre
        if region not in ARM_SAGITTARIUS_CARINA | ARM_ORION_CYGNUS | set(["Odin's Hold", "Galactic Centre"]):
            return False
        return True

    if genus_species == "Aleoida Spica":
        if region == "Outer Orion Spur":
            return True

        # NOT Sagittarius-Carina Arm
        if region in ARM_SAGITTARIUS_CARINA | set(["Inner Scutum-Centaurus Arm", "Izanami"]):
            return False
        return True

    if genus_species == "Cactoida Cortexum":
        # does not spawn: 9, 15, 33, 34
        if region in ["Outer Orion-Perseus Conflux", "Elysian Shore", "Sanguineous Rim", "Inner Scutum-Centaurus Arm"]:
            return False

        # Orion-Cygnus Arm including Odin's Hold and Galactic Centre
        if region not in ARM_ORION_CYGNUS | set(["Odin's Hold", "Galactic Centre"]):
            return False
        return True

    if genus_species == "Cactoida Lapis":
        # does not spawn: 8, 16, 17, 35
        if region in ["Inner Orion-Perseus Conflux", "Orion-Cygnus Arm", "Temple", "Outer Orion Spur"]:
            return False

        # spawns: 9, 24
        if region in ["Inner Scutum-Centaurus Arm", "Formorian Frontier"]:
            return True

        # Sagittarius-Carina Arm including Odin's Hold and Galactic Centre
        if region not in ARM_SAGITTARIUS_CARINA | set(["Odin's Hold", "Galactic Centre"]):
            return False
        return True

    if genus_species == "Cactoida Peperatis":
        # Scutum-Centaurus Arm including Odin's Hold and Galactic Centre
        if region not in ARM_SCUTUM_CENTAURUS | set(["Odin's Hold", "Galactic Centre"]):
            return False
        return True

    if genus_species == "Cactoida Pullulanta":
        # Perseus Arm including Ryker's Hope and Galactic Centre
        if region not in ARM_PERSEUS | set(["Ryker's Hope", "Galactic Centre"]):
            return False
        return True

    if genus_species == "Frutexa Acus":
        # does not spawn: 9, 15, 33, 34
        if region in ["Outer Orion-Perseus Conflux", "Elysian Shore", "Sanguineous Rim", "Inner Scutum-Centaurus Arm"]:
            return False

        # Orion-Cygnus Arm including Odin's Hold and Galactic Centre
        if region not in ARM_ORION_CYGNUS | set(["Odin's Hold", "Galactic Centre"]):
            return False
        return True

    if genus_species == "Frutexa Fera":
        # Outer Arm including Empyrean Straits and Galactic Centre
        if region not in ARM_OUTER | set(["Empyrean Straits", "Galactic Centre"]):
            return False
        return True

    if genus_species == "Frutexa Flabellum":
        # NOT Scutum-Centaurus Arm
        if region in ARM_SCUTUM_CENTAURUS | set(["Odin's Hold", "Galactic Centre"]):
            return False
        return True

    if genus_species == "Frutexa Flammasis":
        # Scutum-Centaurus Arm including Odin's Hold and Galactic Centre
        if region not in ARM_SCUTUM_CENTAURUS | set(["Odin's Hold", "Galactic Centre"]):
            return False
        return True

    if genus_species == "Osseus Cornibus":
        # Perseus Arm including Ryker's Hope and Galactic Centre
        if region not in ARM_PERSEUS | set(["Ryker's Hope", "Galactic Centre"]):
            return False
        return True

    if genus_species == "Osseus Fractus":
        # NOT Perseus Arm but including Odin's Hold and Empyrean Straits
        if region in ARM_PERSEUS | set(["Ryker's Hope", "Galactic Centre"]):
            return False
        return True

    if genus_species == "Osseus Pellebantus":
        # NOT Perseus Arm but including Odin's Hold and Empyrean Straits
        if region in ARM_PERSEUS | set(["Ryker's Hope", "Galactic Centre"]):
            return False
        return True

    if genus_species == "Stratum Cucumisis":
        # does not spawn: 8, 16, 17, 35
        if region in ["Inner Orion-Perseus Conflux", "Orion-Cygnus Arm", "Temple", "Outer Orion Spur"]:
            return False

        # spawns: 9
        if region == "Inner Scutum-Centaurus Arm":
            return True

        # Sagittarius-Carina Arm including Odin's Hold and Galactic Centre
        if region not in ARM_SAGITTARIUS_CARINA | set(["Odin's Hold", "Galactic Centre"]):
            return False
        return True

    if genus_species == "Stratum Excutitus":
        # does not spawn: 9, 15, 33, 34
        if region in ["Inner Scutum-Centaurus Arm", "Outer Orion-Perseus Conflux", "Elysian Shore", "Sanguineous Rim"]:
            return False

        # Orion-Cygnus Arm including Odin's Hold and Galactic Centre
        if region not in ARM_ORION_CYGNUS | set(["Odin's Hold", "Galactic Centre"]):
            return False
        return True

    if genus_species == "Stratum Frigus":
        # Perseus Arm including Ryker's Hope and excluding Galactic Centre
        if region not in (ARM_PERSEUS | set(["Ryker's Hope"])) - set(["Galactic Centre"]):
            return False
        return True

    if genus_species == "Stratum Laminamus":
        # does not spawn: 9, 15, 33, 34
        if region in ["Inner Scutum-Centaurus Arm", "Outer Orion-Perseus Conflux", "Elysian Shore", "Sanguineous Rim"]:
            return False

        # Orion-Cygnus Arm including Odin's Hold and Galactic Centre
        if region not in ARM_ORION_CYGNUS | set(["Odin's Hold", "Galactic Centre"]):
            return False
        return True

    if genus_species == "Stratum Limaxus":
        # Scutum-Centaurus Arm excluding Odin's Hold and Galactic Centre
        if region not in ARM_SCUTUM_CENTAURUS - set(["Odin's Hold", "Galactic Centre"]):
            return False
        return True

    if genus_species == "Tubus Cavas":
        # Scutum-Centaurus Arm including Odin's Hold and Galactic Centre
        if region not in ARM_SCUTUM_CENTAURUS | set(["Odin's Hold", "Galactic Centre"]):
            return False
        return True

    if genus_species == "Tubus Compagibus":
        # does not spawn: 8, 16, 17, 35
        if region in ["Inner Orion-Perseus Conflux", "Orion-Cygnus Arm", "Temple", "Outer Orion Spur"]:
            return False

        # spawns: 9, 24
        if region in ["Inner Scutum-Centaurus Arm", "Formorian Frontier"]:
            return True

        # Sagittarius-Carina Arm including Odin's Hold and Galactic Centre
        if region not in ARM_SAGITTARIUS_CARINA | set(["Odin's Hold", "Galactic Centre"]):
            return False
        return True

    if genus_species == "Tubus Conifer":
        # Perseus Arm including Ryker's Hope and Galactic Centre
        if region not in ARM_PERSEUS | set(["Ryker's Hope", "Galactic Centre"]):
            return False
        return True

    if genus_species == "Tussock Albata":
        # Sagittarius-Carina Arm, Perseus Arm including Ryker's Hope but excluding Galactic Centre
        if region not in (ARM_SAGITTARIUS_CARINA | ARM_PERSEUS | set(["Ryker's Hope"])) - set(["Galactic Centre"]):
            return False
        return True

    if genus_species == "Tussock Caputus":
        # Sagittarius-Carina Arm, Perseus Arm including Ryker's Hope but excluding Galactic Centre
        if region not in (ARM_SAGITTARIUS_CARINA | ARM_PERSEUS | set(["Ryker's Hope"])) - set(["Galactic Centre"]):
            return False
        return True

    if genus_species == "Tussock Catena":
        # Scutum-Centaurus Arm excluding Galactic Central Regions
        if region not in ARM_SCUTUM_CENTAURUS - ARM_CENTRAL:
            return False
        return True

    if genus_species == "Tussock Cultro":
        # does not spawn: 9, 15, 33, 34
        if region in ["Inner Scutum-Centaurus Arm", "Outer Orion-Perseus Conflux", "Elysian Shore", "Sanguineous Rim"]:
            return False

        # Orion-Cygnus Arm including Odin's Hold and Galactic Centre
        if region not in ARM_ORION_CYGNUS | set(["Odin's Hold", "Galactic Centre"]):
            return False
        return True

    if genus_species == "Tussock Divisa":
        # Perseus Arm including Ryker's Hope
        if region not in ARM_PERSEUS | set(["Ryker's Hope"]):
            return False
        return True

    if genus_species == "Tussock Ignis":
        # Sagittarius-Carina Arm and Perseus Arm including Ryker's Hope
        if region not in ARM_SAGITTARIUS_CARINA | ARM_PERSEUS | set(["Ryker's Hope"]):
            return False
        return True

    if genus_species == "Tussock Pennata":
        # Sagittarius-Carina Arm and Perseus Arm including Ryker's Hope
        if region not in ARM_SAGITTARIUS_CARINA | ARM_PERSEUS | set(["Ryker's Hope"]):
            return False
        return True

    if genus_species == "Tussock Pennatis":
        # Outer Arm including Empyrean Straits and Galactic Centre
        if region not in ARM_OUTER | set(["Empyrean Straits", "Galactic Centre"]):
            return False
        return True

    if genus_species == "Tussock Propagito":
        # Scutum-Centaurus Arm including Odin's Hold and Galactic Centre
        if region not in ARM_SCUTUM_CENTAURUS | set(["Odin's Hold", "Galactic Centre"]):
            return False
        return True

    if genus_species == "Tussock Serrati":
        # Sagittarius-Carina Arm and Perseus Arm including Ryker's Hope but excluding Galactic Centre
        if region not in (ARM_SAGITTARIUS_CARINA | ARM_PERSEUS | set(["Ryker's Hope"])) - set(["Galactic Centre"]):
            return False
        return True

    if genus_species == "Tussock Triticum":
        # Sagittarius-Carina Arm and Perseus Arm including Ryker's Hope but excluding Galactic Centre
        if region not in (ARM_SAGITTARIUS_CARINA | ARM_PERSEUS | set(["Ryker's Hope"])) - set(["Galactic Centre"]):
            return False
        return True

    if genus_species == "Tussock Ventusa":
        # Sagittarius-Carina Arm and Perseus Arm including Ryker's Hope but excluding Galactic Centre
        if region not in (ARM_SAGITTARIUS_CARINA | ARM_PERSEUS | set(["Ryker's Hope"])) - set(["Galactic Centre"]):
            return False
        return True

    print(f'Unknown species! {genus_species}')

conditions = {
  "Aleoida" : {
    "colors" : {
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
      "Ae" : None,
      "W" : CANONN_COLOR_GY,
      "D" : CANONN_COLOR_IN,
      "N" : CANONN_COLOR_OC,
      "BH" : None,
      "C" : None,
    },
    "max_gravity" : 0.275313,
    "specs" : {
      "Arcus" : [ { "atm_composition" : { "Carbon dioxide" : lambda x: 97.5 <= x}, "gravity" : 0.275313, "temperature" : lambda x: 175.0 <= x <= 180.0} ],
      "Coronamus" : [ { "atm_composition" : { "Carbon dioxide" : lambda x: 97.5 <= x}, "gravity" : 0.275313, "temperature" : lambda x: 180.0 <= x <= 190.0, "volcanism" : [ "No volcanism" ]} ],
      "Gravis" : [ { "atm_composition" : { "Carbon dioxide" : lambda x: 97.5 <= x}, "gravity" : 0.275313, "temperature" : lambda x: 190.0 <= x <= 197.0, "volcanism" : [ "No volcanism" ]} ],
      "Laminiae" : [ { "atm_composition" : { "Ammonia" : lambda x: 100.0 <= x}, "gravity" : 0.275313, "temperature" : lambda x: 152.0 <= x <= 177.0} ],
      "Spica" : [ { "atm_composition" : { "Ammonia" : lambda x: 100.0 <= x}, "gravity" : 0.275313, "temperature" : lambda x: 170.0 <= x <= 177.0} ],
    },
  },
  "Bacterium" : {
    "colors" : {
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
      "Ae" : CANONN_COLOR_OR,
      "W" : CANONN_COLOR_AM,
      "D" : CANONN_COLOR_OC,
      "N" : CANONN_COLOR_IN,
      "BH" : None,
      "C" : None,
    },
    "max_gravity" : 0.611807,
    "specs" : {
      "Alcyoneum" : [ { "atm_composition" : { "Ammonia" : lambda x: 60.0 <= x}, "gravity" : 0.375253, "temperature" : lambda x: 152.0 <= x <= 177.0} ],
      "Aurasus" : [ { "atm_composition" : { "Carbon dioxide" : lambda x: 50.0 <= x}, "gravity" : 0.611807, "temperature" : lambda x: 145.0 <= x <= 400.0} ],
      "Cerbrus" : [ { "atm_composition" : { "Ammonia" : lambda x: 60.0 <= x}, "gravity" : 0.611807, "temperature" : lambda x: 132.0 <= x <= 500.0} ],
    },
  },
  "Cactoida" : {
    "colors" : {
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
      "Ae" : None,
      "W" : CANONN_COLOR_IN,
      "D" : CANONN_COLOR_TU,
      "N" : CANONN_COLOR_SG,
      "BH" : None,
      "C" : None,
    },
    "max_gravity" : 0.275313,
    "specs" : {
      "Vermis" : [
        { "atm_composition" : { "Water" : lambda x: 100.0 <= x}, "gravity" : 0.275313, "temperature" : lambda x: 390.0 <= x <= 450.0},
        { "atm_composition" : { "Carbon dioxide" : lambda x: 97.5 <= x,('Carbon dioxide', 'Sulphur dioxide') : 100.0}, "gravity" : 0.275313, "temperature" : lambda x: 160.0 <= x <= 207.0}
      ],
      "Cortexum" : [ { "atm_composition" : { "Carbon dioxide" : lambda x: 97.5 <= x}, "gravity" : 0.275313, "temperature" : lambda x: 180.0 <= x <= 196.0, "volcanism" : [ "No volcanism" ]} ],
      "Lapis" : [ { "atm_composition" : { "Ammonia" : lambda x: 99.0 <= x}, "gravity" : 0.275313, "temperature" : lambda x: 160.0 <= x <= 177.0} ],
      "Peperatis" : [ { "atm_composition" : { "Ammonia" : lambda x: 100.0 <= x}, "gravity" : 0.275313, "temperature" : lambda x: 160.0 <= x <= 177.0} ],
      "Pullulanta" : [ { "atm_composition" : { "Carbon dioxide" : lambda x: 97.5 <= x}, "gravity" : 0.275313, "temperature" : lambda x: 180.0 <= x <= 196.0, "volcanism" : [ "No volcanism" ]} ],
    }
  },
  "Clypeus" : {
    "colors" : {
      "O" : None,
      "B" : CANONN_COLOR_MR,
      "A" : CANONN_COLOR_OR,
      "F" : CANONN_COLOR_MV,
      "G" : CANONN_COLOR_AM,
      "K" : CANONN_COLOR_GY,
      "M" : CANONN_COLOR_TU,
      "L" : CANONN_COLOR_TE,
      "T" : None,
      "Y" : CANONN_COLOR_GR,
      "TTS" : None,
      "Ae" : None,
      "W" : None,
      "D" : CANONN_COLOR_LI,
      "N" : CANONN_COLOR_YE,
      "BH" : None,
      "C" : None,
    },
    "max_gravity" : 0.275313,
    "specs" : {
      "Lacrimam" : [
        { "atm_composition" : { "Water" : lambda x: 100.0 <= x}, "max_dist" : 4.0, "gravity" : 0.275313, "temperature" : lambda x: 390.0 <= x <= 452.0, "subtypes" : [ "Rocky body" ]},
        { "atm_composition" : { "Carbon dioxide" : lambda x: 97.5 <= x}, "max_dist" : 4.0, "gravity" : 0.275313, "temperature" : lambda x: 190.0 <= x <= 196.0, "subtypes" : [ "Rocky body" ]}
      ],
      "Margaritus" : [
        { "atm_composition" : { "Water" : lambda x: 100.0 <= x}, "gravity" : 0.275313, "temperature" : lambda x: 390.0 <= x <= 452.0, "subtypes" : [ "High metal content world" ]},
        { "atm_composition" : { "Carbon dioxide" : lambda x: 97.5 <= x}, "gravity" : 0.275313, "temperature" : lambda x: 190.0 <= x <= 196.0, "subtypes" : [ "High metal content world" ]}
      ],
      "Speculumi" : [
        { "atm_composition" : { "Water" : lambda x: 100.0 <= x}, "min_dist" : 4.0, "gravity" : 0.275313, "temperature" : lambda x: 390.0 <= x <= 452.0, "subtypes" : [ "Rocky body" ]},
        { "atm_composition" : { "Carbon dioxide" : lambda x: 97.5 <= x}, "min_dist" : 4.0, "gravity" : 0.275313, "temperature" : lambda x: 190.0 <= x <= 196.0, "subtypes" : [ "Rocky body" ]}
      ],
    }
  },
  "Concha" : {
    "colors" : {
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
      "Ae" : None,
      "W" : CANONN_COLOR_LI,
      "D" : CANONN_COLOR_GR,
      "N" : CANONN_COLOR_EM,
      "BH" : None,
      "C" : None,
    },
    "max_gravity" : 0.275313,
    "specs" : {
      "Aureolas" : [ { "atm_composition" : { "Ammonia" : lambda x: 100.0 <= x}, "gravity" : 0.275313, "temperature" : lambda x: 152.0 <= x <= 176.0, "semimajor_axis" : lambda x: x < 0.04, "subtypes" : [ "High metal content world", "Rocky body" ]} ],
      "Labiata" : [ { "atm_composition" : { "Carbon dioxide" : lambda x: 97.5 <= x}, "gravity" : 0.275313, "temperature" : lambda x: 150.0 <= x <= 199.0, "subtypes" : [ "High metal content world", "Rocky body" ], "volcanism" : [ "No volcanism" ]} ],
    }
  },
  "Fonticulua" : {
    "colors" : {
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
      "Ae" : CANONN_COLOR_MR,
      "W" : CANONN_COLOR_IN,
      "D" : CANONN_COLOR_TU,
      "N" : CANONN_COLOR_SG,
      "BH" : None,
      "C" : None,
    },
    "max_gravity" : 0.275313,
    "specs" : {
      "Campestris" : [ { "atm_composition" : { "Argon" : lambda x: 50.0 <= x}, "gravity" : 0.275313, "temperature" : lambda x: 50.0 <= x <= 150.0, "subtypes" : ['Icy body']} ],
      "Digitos" : [ { "atm_composition" : { "Methane" : lambda x: 100.0 <= x}, "gravity" : 0.064729, "temperature" : lambda x: 83.0 <= x <= 109.0, "subtypes" : ['Icy body']} ],
      "Fluctus" : [ { "atm_composition" : { "Oxygen" : lambda x: 50.0 <= x}, "gravity" : 0.275313, "temperature" : lambda x: 143.0 <= x <= 200.0, "subtypes" : ['Icy body']} ],
      "Lapida" : [ { "atm_composition" :{ "Nitrogen" : lambda x: 99.0 <= x, "Argon" : lambda x: x <= 0.0}, "gravity" : 0.275313, "temperature" : lambda x: 50.0 <= x <= 81.0, "subtypes" : ['Icy body']} ],
      "Segmentatus" : [ { "atm_composition" : { "Neon" : lambda x: 0.1 < x, "Argon" : lambda x: x <= 0.0}, "gravity" : 0.275313, "temperature" : lambda x: 50.0 <= x <= 80.0, "subtypes" : ['Icy body']} ],
      "Upupam" : [ { "atm_composition" :{ "Nitrogen" : lambda x: 50.0 <= x, "Argon" : lambda x: 0.0 < x}, "gravity" : 0.275313, "temperature" : lambda x: 60.0 <= x <= 124.0, "subtypes" : ['Icy body']} ],
    }
  },
  "Frutexa" : {
    "colors" : {
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
      "Ae" : None,
      "W" : CANONN_COLOR_OR,
      "D" : CANONN_COLOR_IN,
      "N" : CANONN_COLOR_RE,
      "BH" : None,
      "C" : None,
    },
    "max_gravity" : 0.275313,
    "specs" : {
      "Acus" : [ { "atm_composition" : { "Carbon dioxide" : lambda x: 97.5 <= x}, "gravity" : 0.275313, "temperature" : lambda x: 146.0 <= x <= 196.0, "subtypes" : ['Rocky body']} ],
      "Collum" : [ { "atm_composition" : { "Sulphur dioxide" : lambda x: 100.0 <= x}, "gravity" : 0.275313, "temperature" : lambda x: 132.0 <= x <= 167.0, "subtypes" : [ 'High metal content world', 'Rocky body' ]} ],
      "Flabellum" : [ { "atm_composition" : { "Ammonia" : lambda x: 99.0 <= x}, "gravity" : 0.275313, "temperature" : lambda x: 152.0 <= x <= 177.0, "subtypes" : ['Rocky body']} ],
      "Flammasis" : [ { "atm_composition" : { "Ammonia" : lambda x: 100.0 <= x}, "gravity" : 0.275313, "temperature" : lambda x: 152.0 <= x <= 177.0, "subtypes" : ['Rocky body']} ],
      "Fera" : [ { "atm_composition" : { "Carbon dioxide" : lambda x: 97.5 <= x}, "gravity" : 0.275313, "temperature" : lambda x: 146.0 <= x <= 196.0, "subtypes" : ['Rocky body']} ],
      "Metallicum" : [
        { "atm_composition" : { "Water" : lambda x: 100.0 <= x}, "gravity" : 0.275313, "temperature" : lambda x: 390.0 <= x <= 400.0, "subtypes" : ['High metal content world'], "volcanism" : [ "No volcanism" ]},
        { "atm_composition" : { "Ammonia" : lambda x: 100.0 <= x}, "gravity" : 0.275313, "temperature" : lambda x: 152.0 <= x <= 176.0, "subtypes" : ['High metal content world'], "volcanism" : [ "No volcanism" ]},
        { "atm_composition" : { "Carbon dioxide" : lambda x: 97.5 <= x}, "gravity" : 0.275313, "temperature" : lambda x: 146.0 <= x <= 196.0, "subtypes" : ['High metal content world'], "volcanism" : [ "No volcanism" ]}
      ],
      "Sponsae" : [ { "atm_composition" : { "Water" : lambda x: 100.0 <= x}, "gravity" : 0.275313, "temperature" : lambda x: 392.0 <= x <= 452.0, "subtypes" : ['Rocky body'], "volcanism" : [ "No volcanism" ]} ],
    }
  },
  "Osseus" : {
    "colors" : {
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
      "Ae" : None,
      "W" : None,
      "D" : None,
      "N" : None,
      "BH" : None,
      "C" : None,
    },
    "max_gravity" : 0.275313,
    "specs" : {
      "Cornibus" : [ { "atm_composition" : { "Carbon dioxide" : lambda x: 97.5 <= x}, "gravity" : 0.275313, "temperature" : lambda x: 180.0 <= x <= 196.0, "volcanism" : [ "No volcanism" ]} ],
      "Fractus" : [ { "atm_composition" : { "Carbon dioxide" : lambda x: 97.5 <= x}, "gravity" : 0.275313, "temperature" : lambda x: 180.0 <= x <= 190.0, "volcanism" : [ "No volcanism" ]} ],
      "Pellebantus" : [ { "atm_composition" : { "Carbon dioxide" : lambda x: 97.5 <= x}, "gravity" : 0.275313, "temperature" : lambda x: 191.0 <= x <= 197.0, "volcanism" : [ "No volcanism" ]} ],
      "Spiralis" : [ { "atm_composition" : { "Ammonia" : lambda x: 99.0 <= x}, "gravity" : 0.275313, "temperature" : lambda x: 160.0 <= x <= 177.0, "subtypes" : [ "High metal content world", 'Rocky body' ]} ],
    }
  },
  "Recepta" : {
    "colors" : {
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
      "Ae" : CANONN_COLOR_GY,
      "W" : None,
      "D" : CANONN_COLOR_YE,
      "N" : CANONN_COLOR_EM,
      "BH" : None,
      "C" : None,
    },
    "max_gravity" : 0.275313,
    "specs" : {
      "Umbrux" : [ { "atm_composition" : { "Sulphur dioxide" : lambda x: 0.0 < x}, "gravity" : 0.275313, "temperature" : lambda x: 132.0 <= x <= 273.0} ],
    }
  },
  "Stratum" : {
    "colors" : {
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
      "Ae" : CANONN_COLOR_TE,
      "W" : CANONN_COLOR_RE,
      "D" : CANONN_COLOR_MV,
      "N" : None,
      "BH" : None,
      "C" : None,
    },
    "max_gravity" : 0.611807,
    "specs" : {
      "Araneamus" : [ { "atm_composition" : { "Sulphur dioxide" : lambda x: 50.0 < x}, "gravity" : 0.550273, "temperature" : lambda x: 165.0 < x} ],
      "Cucumisis" : [
        { "atm_composition" : { "Sulphur dioxide" : lambda x: 0.0 < x}, "gravity" : 0.611807, "temperature" : lambda x: 191.0 < x},
        { "atm_composition" : { "Carbon dioxide" : lambda x: 0.0 < x}, "gravity" : 0.611807, "temperature" : lambda x: 191.0 < x}
      ],
      "Excutitus" : [
        { "atm_composition" : { "Sulphur dioxide" : lambda x: 0.0 < x}, "gravity" : 0.473151, "temperature" : lambda x: 165.0 <= x <= 190.0},
        { "atm_composition" : { "Carbon dioxide" : lambda x: 100.0 <= x}, "gravity" : 0.473151, "temperature" : lambda x: 165.0 <= x <= 190.0}
      ],
      "Laminamus" : [ { "atm_composition" : { "Ammonia" : lambda x: 75.0 <= x}, "gravity" : 0.342592, "temperature" : lambda x: 165.0 <= x <= 177.0} ],
      "Limaxus" : [
        { "atm_composition" : { "Carbon dioxide" : lambda x: 100.0 <= x}, "gravity" : 0.377205, "temperature" : lambda x: 165.0 <= x <= 190.0, "subtypes" : ['Rocky body']},
        { "atm_composition" : { "Sulphur dioxide" : lambda x: 0.0 < x}, "gravity" : 0.377205, "temperature" : lambda x: 165.0 <= x <= 190.0, "subtypes" : ['Rocky body']}
      ],
      "Frigus" : [
        { "atm_composition" : { "Sulphur dioxide" : lambda x: 0.0 < x}, "gravity" : 0.550600, "temperature" : lambda x: 191.0 < x},
        { "atm_composition" : { "Carbon dioxide" : lambda x: 100.0 <= x}, "gravity" : 0.550600, "temperature" : lambda x: 191.0 < x}
      ],
      "Paleas" : [
        { "atm_composition" : { "Carbon dioxide" : lambda x: 0.0 < x, "Sulphur dioxide" : lambda x: x < 50.0}, "gravity" : 0.594972, "temperature" : lambda x: 165.0 <= x, "subtypes" : ['Rocky body']},
        { "atm_composition" : { "Ammonia" : lambda x: 70.0 <= x}, "gravity" : 0.594972, "temperature" : lambda x: 165.0 <= x <= 176.0, "subtypes" : ['Rocky body']},
        { "atm_composition" : { "Water" : lambda x: 100.0 <= x}, "gravity" : 0.594972, "temperature" : lambda x: 390.0 <= x <= 450.0, "subtypes" : ['Rocky body']}
      ],
      "Tectonicas" : [ { "gravity" : 0.611807, "temperature" : lambda x: 165.0 <= x, "subtypes" : ['High metal content world']} ],
    }
  },
  "Tubus" : {
    "colors" : {
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
      "Ae" : None,
      "W" : CANONN_COLOR_LI,
      "D" : CANONN_COLOR_YE,
      "N" : CANONN_COLOR_AM,
      "BH" : None,
      "C" : None,
    },
    "max_gravity" : 0.152952,
    "specs" : {
      "Cavas" : [ { "atm_composition" : { "Carbon dioxide" : lambda x: 97.5 <= x}, "gravity" : 0.152952, "temperature" : lambda x: 160.0 <= x <= 197.0, "subtypes" : ['Rocky body'], "volcanism" : [ "No volcanism" ]} ],
      "Conifer" : [ { "atm_composition" : { "Carbon dioxide" : lambda x: 97.5 <= x}, "gravity" : 0.152952, "temperature" : lambda x: 160.0 <= x <= 196.0, "subtypes" : ['Rocky body'], "volcanism" : [ "No volcanism" ]} ],
      "Sororibus" : [
        { "atm_composition" : { "Carbon dioxide" : lambda x: 98.0 <= x}, "gravity" : 0.152952, "temperature" : lambda x: 160.0 <= x <= 194.0, "subtypes" : ['High metal content world']},
        { "atm_composition" : { "Ammonia" : lambda x: 100.0 <= x}, "gravity" : 0.152952, "temperature" : lambda x: 160.0 <= x <= 194.0, "subtypes" : ['High metal content world']}
      ],
      "Compagibus" : [ { "atm_composition" : { "Carbon dioxide" : lambda x: 97.5 <= x}, "gravity" : 0.152952, "temperature" : lambda x: 160.0 <= x <= 197.0, "subtypes" : ['Rocky body'], "volcanism" : [ "No volcanism" ]} ],
      "Rosarium" : [ { "atm_composition" : { "Ammonia" : lambda x: 100.0 <= x}, "gravity" : 0.152952, "temperature" : lambda x: 160.0 <= x <= 177.0, "subtypes" : ['Rocky body']} ],
    }
  },
  "Tussock" : {
    "colors" : {
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
      "Ae" : None,
      "W" : CANONN_COLOR_OR,
      "D" : CANONN_COLOR_MR,
      "N" : CANONN_COLOR_YE,
      "BH" : None,
      "C" : None,
    },
    "max_gravity" : 0.275313,
    "specs" : {
      "Albata" : [ { "atm_composition" : { "Carbon dioxide" : lambda x: 97.5 <= x}, "gravity" : 0.275313, "temperature" : lambda x: 175.0 <= x <= 180.0, "subtypes" : [ "High metal content world", 'Rocky body' ], "volcanism" : [ "No volcanism" ]} ],
      "Caputus" : [ { "atm_composition" : { "Carbon dioxide" : lambda x: 97.5 <= x}, "gravity" : 0.275313, "temperature" : lambda x: 181.0 <= x <= 190.0, "subtypes" : [ "High metal content world", 'Rocky body' ], "volcanism" : [ "No volcanism" ]} ],
      "Capillum" : [
        { "atm_composition" : { "Argon" : lambda x: 50.0 <= x}, "gravity" : 0.275313, "temperature" : lambda x: 80.0 <= x <= 129.0, "subtypes" : [ "Rocky body", "Rocky Ice world" ]},
        { "atm_composition" : { "Methane" : lambda x: 100.0 <= x}, "gravity" : 0.275313, "temperature" : lambda x: 80.0 <= x <= 129.0, "subtypes" : [ "Rocky body", "Rocky Ice world" ]}
      ],
      "Catena" : [ { "atm_composition" : { "Ammonia" : lambda x: 100.0 <= x}, "gravity" : 0.275313, "temperature" : lambda x: 152.0 <= x <= 177.0, "subtypes" : [ "High metal content world", 'Rocky body' ]} ],
      "Cultro" : [ { "atm_composition" : { "Ammonia" : lambda x: 100.0 <= x}, "gravity" : 0.275313, "temperature" : lambda x: 152.0 <= x <= 177.0, "subtypes" : [ "High metal content world", 'Rocky body' ]} ],
      "Divisa" : [ { "atm_composition" : { "Ammonia" : lambda x: 100.0 <= x}, "gravity" : 0.275313, "temperature" : lambda x: 152.0 <= x <= 177.0, "subtypes" : [ "High metal content world", 'Rocky body' ]} ],
      "Ignis" : [ { "atm_composition" : { "Carbon dioxide" : lambda x: 97.5 <= x}, "gravity" : 0.275313, "temperature" : lambda x: 150.0 <= x <= 170.0, "subtypes" : [ "High metal content world", 'Rocky body' ], "volcanism" : [ "No volcanism" ]} ],
      "Pennata" : [ { "atm_composition" : { "Carbon dioxide" : lambda x: 97.5 <= x}, "gravity" : 0.275313, "temperature" : lambda x: 145.0 <= x <= 154.0, "subtypes" : [ "High metal content world", 'Rocky body' ], "volcanism" : [ "No volcanism" ]} ],
      "Pennatis" : [ { "atm_composition" : { "Carbon dioxide" : lambda x: 97.5 <= x}, "gravity" : 0.275313, "temperature" : lambda x: 146.0 <= x <= 196.0, "subtypes" : [ "High metal content world", 'Rocky body' ], "volcanism" : [ "No volcanism" ]} ],
      "Propagito" : [ { "atm_composition" : { "Carbon dioxide" : lambda x: 97.5 <= x}, "gravity" : 0.275313, "temperature" : lambda x: 145.0 <= x <= 197.0, "subtypes" : [ "High metal content world", 'Rocky body' ], "volcanism" : [ "No volcanism" ]} ],
      "Serrati" : [ { "atm_composition" : { "Carbon dioxide" : lambda x: 97.5 <= x}, "gravity" : 0.275313, "temperature" : lambda x: 171.0 <= x <= 174.0, "subtypes" : [ "High metal content world", 'Rocky body' ], "volcanism" : [ "No volcanism" ]} ],
      "Stigmasis" : [ { "atm_composition" : { "Sulphur dioxide" : lambda x: 100.0 <= x}, "gravity" : 0.275313, "temperature" : lambda x: 132.0 <= x <= 207.0, "subtypes" : [ 'High metal content world', 'Rocky body' ]} ],
      "Triticum" : [ { "atm_composition" : { "Carbon dioxide" : lambda x: 97.5 <= x}, "gravity" : 0.275313, "temperature" : lambda x: 191.0 <= x <= 196.0, "subtypes" : [ 'High metal content world', 'Rocky body' ], "volcanism" : [ "No volcanism" ]} ],
      "Ventusa" : [ { "atm_composition" : { "Carbon dioxide" : lambda x: 97.5 <= x}, "gravity" : 0.275313, "temperature" : lambda x: 155.0 <= x <= 160.0, "subtypes" : [ "High metal content world", 'Rocky body' ]} ],
      "Virgam" : [ { "atm_composition" : { "Water" : lambda x: 100.0 <= x}, "gravity" : 0.275313, "temperature" : lambda x: 390.0 <= x <= 450.0, "subtypes" : [ "High metal content world", 'Rocky body' ]} ],
    }
  }
}

def check_environment(genus, species, body, spec):
    # gravity is too high
    if body["gravity"] > spec.get("gravity", None):
        return False

    # check atmosphere composition
    for gas, gas_req in spec.get("atm_composition", {}).items():

        # special hack for Vermis
        if type(gas) is tuple:
            cond = gas_req
            value = 0.0
            for subgas in gas:
                value += body.get("atmosphereComposition", {}).get(subgas, 0.0)

            if value != cond:
                return False
            continue

        if type(gas) is str:
            value = body.get("atmosphereComposition", {}).get(gas, 0.0)
            if not gas_req(value):
                return False

    if (cond := spec.get("subtypes", [])) != []:
        if body['subType'] not in cond:
            return False

    if (cond := spec.get("volcanism", [])) != []:
        if body.get("volcanism", "No volcanism") not in cond:
            return False

    temp = body["surfaceTemperature"]
    if not spec["temperature"](temp):
        return False

    sma = body.get("semiMajorAxis", None)
    if sma is not None and "semimajor_axis" in spec and not spec["semimajor_axis"](sma):
        #print(f"Skipping {body['name']} - semimajor axis is too big ({body['semiMajorAxis']})")
        return False

    return True

def check(region, body, stars):
    ret = []

    valid_stars = get_possible_stars(body, stars)
    for genus, genus_data in conditions.items():
        if body["gravity"] >= genus_data["max_gravity"]:
            continue

        # check if everything has been scanned
        name = body["name"]
        if name in known_planets and genus in known_planets[name]["by_genus"]:
            if len(known_planets[name]["by_genus"][genus]) > 1:
                print(name, "WTF-2", known_planets[name]["by_genus"][genus], file=sys.stderr)
            for e in known_planets[name]["by_genus"][genus]:
                ret.append((region, name, e, 1))
            continue

        colors = genus_data["colors"]
        for species, species_spec_list in genus_data["specs"].items():
            if not check_region(genus, species, region):
                continue

            for species_spec in species_spec_list:
                if check_environment(genus, species, body, species_spec):
                    #print(body["name"], genus, species, spec)
                    s = f"{genus} {species}"

                    # due to a bug, only Emerald Araneamus exists
                    if s == "Stratum Araneamus":
                        string = f"Stratum Araneamus - {CANONN_COLOR_EM}"
                        region_priority = get_color_priority(region, string)
                        ret.append((region, body["name"], string, region_priority))
                        continue

                    min_dist = species_spec.get("min_dist", None)
                    max_dist = species_spec.get("max_dist", None)
                    set_colors = get_possible_colors(valid_stars, s, colors, min_dist = min_dist, max_dist = max_dist)

                    for color in set_colors:
                        string = f"{s} - {color}"
                        region_priority = get_color_priority(region, string)
                        ret.append((region, body["name"], string, region_priority))
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
        self.predicted = {
            "timestamp": date.today().isoformat(),
            "bio": {}
        }
        self.datetime = datetime.now(tz=UTC).replace(minute=0, second=0, microsecond=0)
        print(f'Predicting biology as of {self.datetime}', file=sys.stderr)

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

                    if genus not in known_planets[body]["by_genus"]:
                        known_planets[body]["by_genus"][genus] = set()

                    known_planets[body]["by_genus"][genus].add(english_name)
                    known_planets[body]["all_bio"].add(english_name)

                    region = regions[entry["region_name"]]
                    global_entries.add(english_name)

                    if region not in regional_entries:
                        regional_entries[region] = set()

                    regional_entries[region].add(english_name)

        with open("invalid-data", "w") as f:
            for planet in known_planets:
                if planet is None:
                    continue

                for genus in known_planets[planet]["by_genus"]:
                    if len(known_planets[planet]["by_genus"][genus]) > 1:
                        print(f'Invalid data for {planet}: {known_planets[planet]["by_genus"][genus]}', file=f)


    def process(self, system):
        stars = []
        planets = []

        x = system["coords"]["x"]
        y = system["coords"]["y"]
        z = system["coords"]["z"]

        region_data = findRegion(x, y, z)
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

        c = Coordinates(system["bodies"], self.datetime)
#        if system["name"] == "Col 359 Sector OT-Q d5-56":
#            c.get_all_coordinates()

        for star in stars:
            star["coordinates"] = c.get_coordinates(star["bodyId"])
            _ = get_mapped_star_type(star.get("subType", None))

        for planet in planets:
            planet["coordinates"] = c.get_coordinates(planet["bodyId"])
            # check for every possible bio
            gravity = planet["gravity"]

            # predicted: list of tuples
            # (region, body name, species name, priority)

            predicted = check(region, planet, stars)

            for entry in predicted:
                region, bodyname, species, priority = entry

                # skip local discoveries
                if priority == 1:
                    continue

                if region not in self.predicted["bio"]:
                    self.predicted["bio"][region] = {}

                if species not in self.predicted["bio"][region]:
                    self.predicted["bio"][region][species] = {
                        "priority" : priority,
                        "locations" : [],
                    }

                self.predicted["bio"][region][species]["locations"].append({
                    "system" : system["name"],
                    "body" : bodyname,
                    "x" : system["coords"]["x"],
                    "y" : system["coords"]["y"],
                    "z" : system["coords"]["z"],
                })

    def finalize(self):
        with open("biopredictor.json", "w") as f:
            json.dump(self.predicted, f)
