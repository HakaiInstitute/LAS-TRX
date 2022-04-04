import os
from datetime import date
from typing import TypeVar, overload

import pyproj.sync
from csrspy import enums

T = TypeVar('T')


@overload
def date_to_decimal_year(d: date) -> float:
    ...


def date_to_decimal_year(d: T) -> T:
    if not isinstance(d, date):
        return d
    year_part = d - date(d.year, 1, 1)
    year_length = date(d.year + 1, 1, 1) - date(d.year, 1, 1)
    return d.year + year_part / year_length


GEOID_LOOKUP = {
    "CGG2013a": enums.Geoid.CGG2013A,
    "CGG2013": enums.Geoid.CGG2013,
    "HT2_2010v70": enums.Geoid.HT2_2010v70
}
REFERENCE_LOOKUP = {
    "NAD83(CSRS)": enums.Ref.NAD83CSRS,
    "ITRF2014": enums.Ref.ITRF14,
    "ITRF2008": enums.Ref.ITRF08,
    "ITRF2005": enums.Ref.ITRF05,
    "ITRF2000": enums.Ref.ITRF00,
    "ITRF97": enums.Ref.ITRF97,
    "ITRF96": enums.Ref.ITRF96,
    "ITRF94": enums.Ref.ITRF94,
    "ITRF93": enums.Ref.ITRF93,
    "ITRF92": enums.Ref.ITRF92,
    "ITRF91": enums.Ref.ITRF91,
    "ITRF90": enums.Ref.ITRF90,
    "ITRF89": enums.Ref.ITRF89,
    "ITRF88": enums.Ref.ITRF88
}


def sync_missing_grid_files():
    target_directory = pyproj.sync.get_data_dir().split(os.path.sep)[0]
    endpoint = pyproj.sync.get_proj_endpoint()
    grids = pyproj.sync.get_transform_grid_list(area_of_use="Canada")

    for grid in grids:
        filename = grid["properties"]["name"]
        pyproj.sync._download_resource_file(
            file_url=f"{endpoint}/{filename}",
            short_name=filename,
            directory=target_directory,
            sha256=grid["properties"]["sha256sum"],
        )
