"""Selects a random encounter from Pokearth for each valid area in a Nuzlocke
   of the given region"""

# system modules
import argparse
import logging
import os
import posixpath
import random
from urllib.request import urlopen

# local modules
from parsers import FormParser, TableParser

# CONSTANTS
SEREBII = "https://www.serebii.net"
POKEARTH = posixpath.join(SEREBII, "pokearth")

SUPPORTED_REGIONS = [
    "paldea",
]

# GLOBALS
LOGGER = logging.getLogger("encounters")


def get_encounters(region):
    """Fetches a random encounter for each area in the given Pokearth 'region',
       returned as a dictionary of {'area': 'encounter'}"""
    encounters = {}
    areas = get_areas(region)
    LOGGER.debug("Found %d areas in %s", len(areas), region)
    for area, area_page in areas.items():
        LOGGER.info("Looking up random encounters for %s...", area)
        pokemon = get_random_encounter(area_page, region)
        if not pokemon:
            LOGGER.info("No possible encounter from: %s", area)
            continue
        LOGGER.debug("Selected %s from %s", pokemon, area)
        encounters[area] = pokemon

    return encounters


def get_random_encounter(area_page, region):
    """Selects a random encounter from the encounter table for 'region''s
       'area_page'"""
    possible_encounters = get_possible_encounters(area_page, region)
    LOGGER.debug("Possible encounters: %s", str(possible_encounters))
    if not possible_encounters:
        return None

    return random.choice(possible_encounters)

# pylint: disable=unused-argument
def get_possible_encounters(area_page, region):
    """Parses any encounter tables from 'region''s 'area_page' and returns a list of
       possible encounters"""
    while area_page.startswith("/"):
        area_page = area_page[1:]

    area_url = posixpath.join(SEREBII, area_page)
    LOGGER.debug("Looking up possible encounters on:\n%s", area_url)
    html = get_url(area_url)
    parser = TableParser()
    parser.feed(html)
    for table in parser.tables:
        if len(table) < 3:
            continue
        if tuple(table[0])[0] != "Filters":
            continue
        if tuple(table[1])[0] != "Standard":
            continue
        if "Standard Spawns" in table[2]:
            continue
        if "Fixed Encounters" in table[2]:
            continue
        LOGGER.debug("Found encounter table")
        return flatten(table[2:])

    # Did not find a valid table. No encounters in this area.
    LOGGER.debug("No encounter table found")
    return []
# pylint: enable=unused-argument


def get_areas(region):
    """Returns a dictionary of {'area': 'sub_url'} for earh area in 'region'"""
    region_url = posixpath.join(POKEARTH, region)
    html = get_url(region_url)
    parser = FormParser()
    parser.feed(html)
    areas_form = parser.forms[3]
    # Finally, remove any page that just points to an index. There should only
    # be one (title) item that matches this criterion.
    keys_to_remove = []
    for key, value in areas_form.items():
        filename, _ = os.path.splitext(os.path.basename(value))
        if filename == "index":
            keys_to_remove.append(key)

    for key in keys_to_remove:
        LOGGER.debug("Removing invalid area: '%s'", key)
        del areas_form[key]

    LOGGER.debug("Found areas: %s", str(list(areas_form.keys())))
    return areas_form


def print_encounters(encounters):
    """Prints each area + encounter combination"""
    for area, pokemon in encounters.items():
        print(f"{area}: {pokemon}")


# helper methods
def get_url(url, binary=False):
    """Fetches the html source for 'url' and returns it as binary data if
       'binary' is True else as a utf-8 encoded string (default)."""
    data = None
    with urlopen(url) as handle:
        data = handle.read()

    assert data is not None
    if binary:
        return data

    return data.decode("utf-8", errors="ignore")


def flatten(multidimensional_list):
    """Flattens the given 'multidimensional_list' into a depth-1 list"""
    ret = []
    for item in multidimensional_list:
        if isinstance(item, list):
            ret.extend(flatten(item))
            continue
        ret.append(item)

    return ret


def parse_args():
    """Commandline argument parser"""
    parser = argparse.ArgumentParser(
        description="Generates randomized encounters for each area in a "
                    "region")
    parser.add_argument(
        "region", choices=SUPPORTED_REGIONS,
        help="Pokearth region to generate encounters for")
    parser.add_argument(
        "-v", "--verbose", action="count", default=0,
        help="Increase logging verbosity. May be added multiple times.")

    return parser.parse_args()


def run():
    """Commandline handler"""
    args = parse_args()
    if args.verbose >= 2:
        LOGGER.setLevel(logging.DEBUG)
    elif args.verbose == 1:
        LOGGER.setLevel(logging.INFO)
    else:
        LOGGER.setLevel(logging.WARNING)

    encounters = get_encounters(args.region)
    print_encounters(encounters)


if __name__ == "__main__":
    logging.basicConfig()
    run()
