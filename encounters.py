# system modules
import argparse
import posixpath
from urllib.request import urlopen

# local modules
from parsers import FormParser, TableParser

# CONSTANTS
POKEARTH = "https://www.serebii.net/pokearth"

SUPPORTED_REGIONS = [
    "paldea",
]


def get_encounters(region):
    """Fetches a random encounter for each area in the given Pokearth 'region',
       returned as a dictionary of {'area': 'encounter'}"""
    encounters = {}
    areas = get_areas(region)
    for area, area_page in areas.items():
        pokemon = get_random_encounter(area_page)
        if not pokemon:
            continue
        encounters[area] = pokemon

    return encounters


def get_areas(region):
    """Returns a dictionary of {'area': 'sub_url'} for earh area in 'region'"""
    pass  # TODO FIXME


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


def extract_tables(html, text_only=True):
    """Extracts top-level tables from the given 'html', translating them
       to a multi-dimensional list of lists. If 'text_only' is True (default),
       only returns valid text in each table field, else returns the complete
       contents of each field."""
    


def parse_args():
    """Commandline argument parser"""
    parser = argparse.ArgumentParser(
        help="Generates randomized encounters for each area in a region")
    parser.add_argument(
        "region", choices=SUPPORTED_REGIONS,
        help="Pokearth region to generate encounters for")

    return parser.parse_args()


def run():
    """Commandline handler"""
    args = parse_args()
    encounters = get_encounters(region)
    print_encounters(encounters)


if __name__ == "__main__":
    run()
