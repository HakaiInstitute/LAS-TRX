"""Copied and modified from laspy known vlr module.

Provides easier and corrected writing of geotags

Should switch to the official laspy version if they get this module cleaned up a bit.
"""

import pyproj
from laspy.vlrs.known import (
    GeoAsciiParamsType,
    GeoAsciiParamsVlr,
    GeoKeyDirectoryType,
    GeoKeyDirectoryVlr,
    GeoKeyEntryStruct,
)


class TrxGeoAsciiParamsVlr(GeoAsciiParamsVlr):
    def record_from_crs(self, crs):
        if crs.geodetic_crs is not None:
            self.strings.append(crs.geodetic_crs.name)

        if crs.is_projected:
            geo_name, coord_name = crs.name.split(" / ")
            if crs.is_vertical:
                [coord_name, _] = coord_name.split(" + ")
            self.strings.append(coord_name)

        if crs.is_vertical:
            _, vd_name = crs.name.split(" + ")
            self.strings.append(vd_name)

    @classmethod
    def from_crs(cls: type[GeoAsciiParamsType], crs: pyproj.CRS) -> GeoAsciiParamsType:
        self = cls()
        self.record_from_crs(crs)
        return self


class TrxGeoKeyDirectoryVlr(GeoKeyDirectoryVlr):
    def record_from_crs(self, crs: pyproj.CRS):
        all_keys = {
            "GTModelTypeGeoKey": GeoKeyEntryStruct(id=1024, count=1),
            "GTRasterTypeGeoKey": GeoKeyEntryStruct(id=1025, count=1, value_offset=2),
            "GTCitationGeoKey": GeoKeyEntryStruct(id=1026, count=0, value_offset=0, tiff_tag_location=34737),
            "GeodeticCRSGeoKey": GeoKeyEntryStruct(id=2048, count=1),
            "GeodeticCitationGeoKey": GeoKeyEntryStruct(id=2049, count=0, value_offset=0, tiff_tag_location=34737),
            "ProjectedCRSGeoKey": GeoKeyEntryStruct(id=3072, count=1),
            "GeogAngularUnitsGeoKey": GeoKeyEntryStruct(id=2054, count=1, value_offset=9102),  # assume degrees
            "ProjLinearUnitsGeoKey": GeoKeyEntryStruct(id=3076, count=1, value_offset=9001),  # assume meters
            "VerticalCSTypeGeoKey": GeoKeyEntryStruct(id=4096, count=1),
            "VerticalCitationGeoKey": GeoKeyEntryStruct(id=4097, tiff_tag_location=34737),
            "VerticalUnitsGeoKey": GeoKeyEntryStruct(id=4099, count=1, value_offset=9001),  # assume meters
        }

        added_keys = [
            "GTModelTypeGeoKey",
        ]

        if crs.geodetic_crs is not None:
            geodetic_name = crs.geodetic_crs.name
            all_keys["GeodeticCitationGeoKey"].count = len((geodetic_name + "|").encode("ascii"))
            all_keys["GeodeticCitationGeoKey"].value_offset = 0
            added_keys.append("GeodeticCitationGeoKey")

        if crs.is_projected:
            geo_coord_name = crs.name
            if crs.is_vertical:
                [geo_coord_name, _] = crs.name.split(" + ")
            geo_name, coord_name = geo_coord_name.split(" / ")
            all_keys["GTCitationGeoKey"].count = len((coord_name + "|").encode("ascii"))
            all_keys["GTCitationGeoKey"].value_offset = (
                all_keys["GeodeticCitationGeoKey"].count + all_keys["GeodeticCitationGeoKey"].value_offset
            )
            added_keys.append("GTCitationGeoKey")

        if crs.is_vertical:
            _, vd_name = crs.name.split(" + ")
            all_keys["VerticalCitationGeoKey"].count = len((vd_name + "|").encode("ascii"))
            all_keys["VerticalCitationGeoKey"].value_offset = (
                all_keys["GTCitationGeoKey"].count + all_keys["GTCitationGeoKey"].value_offset
            )

            # all_keys["VerticalCSTypeGeoKey"].value_offset = 2
            # added_keys.append("VerticalCSTypeGeoKey")
            added_keys.append("VerticalCitationGeoKey")
            added_keys.append("VerticalUnitsGeoKey")

        epsg = crs.to_epsg()

        if crs.is_projected:
            all_keys["GTModelTypeGeoKey"].value_offset = 1
            if epsg:
                all_keys["ProjectedCRSGeoKey"].value_offset = epsg
                added_keys.append("ProjectedCRSGeoKey")

            all_keys["ProjLinearUnitsGeoKey"].value_offset = int(crs.axis_info[0].unit_code)
            added_keys.append("ProjLinearUnitsGeoKey")

        elif crs.is_geographic:
            all_keys["GTModelTypeGeoKey"].value_offset = 2
            added_keys.append("GeogAngularUnitsGeoKey")
            if epsg:
                all_keys["GeodeticCRSGeoKey"].value_offset = epsg
                added_keys.append("GeodeticCRSGeoKey")

        elif crs.is_geocentric:
            all_keys["GTModelTypeGeoKey"].value_offset = 3
            if epsg:
                all_keys["GeodeticCRSGeoKey"].value_offset = epsg
                added_keys.append("GeodeticCRSGeoKey")

        self.geo_keys = [all_keys[k] for k in added_keys]
        self.geo_keys_header.number_of_keys = len(self.geo_keys)

    def parse_crs(self):
        for key in self.geo_keys:
            # get ProjectedCRSGeoKey by id
            if key.id == 3072:
                return pyproj.CRS.from_epsg(key.value_offset)
        return None

    @classmethod
    def from_crs(cls: type[GeoKeyDirectoryType], crs: pyproj.CRS) -> GeoKeyDirectoryType:
        self = cls()
        self.record_from_crs(crs)
        return self
