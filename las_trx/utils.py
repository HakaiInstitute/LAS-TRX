import logging
import sys
from datetime import date
from os import path
from typing import TypeVar, overload, List, Mapping, Any, Optional

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
    "WGS84": Reference.WGS84,
    "ITRF2020": Reference.ITRF20,
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


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    base_path = getattr(sys, "_MEIPASS", path.dirname(__file__))
    return path.abspath(path.join(base_path, relative_path))


def _get_available_versions() -> Optional[List[Mapping[str, Any]]]:
    import requests
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    r = requests.get("https://api.github.com/repos/HakaiInstitute/LAS-TRX/releases",
                     headers=headers)
    if r.status_code == requests.codes.ok:
        return list(
            {
                "tag_name": version["tag_name"],
                "html_url": version["html_url"],
                "prerelease": version["prerelease"],
                "draft": version["draft"],
            }
            for version in r.json()
        )
    else:
        return None


def get_upgrade_version(version) -> Optional[Mapping[str, str]]:
    available_versions = _get_available_versions()
    if available_versions is None or len(available_versions) == 0:
        # Error fetching versions, assume no upgrade available
        return None

    # Get all tags that are newer than the current version
    try:
        idx = [v["tag_name"] for v in available_versions].index(version)
    except ValueError:
        # Current version not found in releases, so get latest version of all releases
        idx = len(available_versions)

    # Only recommend stable releases for upgrade
    newer_stable_versions = [v for v in available_versions[:idx] if
                             not v["prerelease"] and not v["draft"]]

    if len(newer_stable_versions) == 0:
        return None

    return newer_stable_versions[0]
