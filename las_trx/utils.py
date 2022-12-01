import logging
from datetime import date
from typing import TypeVar, overload

import pyproj.sync

from csrspy.enums import CoordType, Reference, VerticalDatum

T = TypeVar("T")

logger = logging.getLogger(__name__)


@overload
def date_to_decimal_year(d: date) -> float:
    ...


def date_to_decimal_year(d: T) -> T:
    if not isinstance(d, date):
        return d
    year_part = d - date(d.year, 1, 1)
    year_length = date(d.year + 1, 1, 1) - date(d.year, 1, 1)
    return d.year + year_part / year_length


VD_LOOKUP = {
    "WGS84": VerticalDatum.WGS84,
    "GRS80": VerticalDatum.GRS80,
    "CGVD2013/CGG2013a": VerticalDatum.CGG2013A,
    "CGVD2013/CGG2013": VerticalDatum.CGG2013,
    "CGVD28/HT2_2010v70": VerticalDatum.HT2_2010v70,
}
REFERENCE_LOOKUP = {
    "NAD83(CSRS)": Reference.NAD83CSRS,
    "ITRF2014": Reference.ITRF14,
    "ITRF2008": Reference.ITRF08,
    "ITRF2005": Reference.ITRF05,
    "ITRF2000": Reference.ITRF00,
    "ITRF97": Reference.ITRF97,
    "ITRF96": Reference.ITRF96,
    "ITRF94": Reference.ITRF94,
    "ITRF93": Reference.ITRF93,
    "ITRF92": Reference.ITRF92,
    "ITRF91": Reference.ITRF91,
    "ITRF90": Reference.ITRF90,
    "ITRF89": Reference.ITRF89,
    "ITRF88": Reference.ITRF88,
}


def sync_missing_grid_files():
    target_directory = pyproj.sync.get_user_data_dir(True)
    endpoint = pyproj.sync.get_proj_endpoint()
    grids = pyproj.sync.get_transform_grid_list(area_of_use="Canada")

    if len(grids):
        logger.info("Syncing PROJ grid files.")

    for grid in grids:
        filename = grid["properties"]["name"]
        pyproj.sync._download_resource_file(
            file_url=f"{endpoint}/{filename}",
            short_name=filename,
            directory=target_directory,
            sha256=grid["properties"]["sha256sum"],
        )


def is_utm_coord_type(coords: CoordType) -> bool:
    # TODO: This is awful, fix it
    return coords in [
        CoordType.UTM3,
        CoordType.UTM4,
        CoordType.UTM5,
        CoordType.UTM6,
        CoordType.UTM7,
        CoordType.UTM8,
        CoordType.UTM9,
        CoordType.UTM10,
        CoordType.UTM11,
        CoordType.UTM12,
        CoordType.UTM13,
        CoordType.UTM14,
        CoordType.UTM15,
        CoordType.UTM16,
        CoordType.UTM17,
        CoordType.UTM18,
        CoordType.UTM19,
        CoordType.UTM20,
        CoordType.UTM21,
        CoordType.UTM22,
        CoordType.UTM23,
    ]


def utm_zone_to_coord_type(zone: int) -> CoordType:
    # TODO: This is awful, fix it
    utm_types = (
        CoordType.UTM3,
        CoordType.UTM4,
        CoordType.UTM5,
        CoordType.UTM6,
        CoordType.UTM7,
        CoordType.UTM8,
        CoordType.UTM9,
        CoordType.UTM10,
        CoordType.UTM11,
        CoordType.UTM12,
        CoordType.UTM13,
        CoordType.UTM14,
        CoordType.UTM15,
        CoordType.UTM16,
        CoordType.UTM17,
        CoordType.UTM18,
        CoordType.UTM19,
        CoordType.UTM20,
        CoordType.UTM21,
        CoordType.UTM22,
        CoordType.UTM23,
    )
    return utm_types[zone - 3]


def get_utm_zone(coord_type: CoordType) -> int:
    return int(coord_type.value[3:])
