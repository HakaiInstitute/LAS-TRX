"""
Copied and modified from laspy known vlr module.

Provides easier and corrected writing of geo tags

Should switch to the official laspy version if they get this module cleaned up a bit.
"""

import ctypes
from typing import Type, TypeVar

import pyproj
from laspy.vlrs import BaseKnownVLR

NULL_BYTE = b"\0"

GeoKeyDirectoryType = TypeVar("GeoKeyDirectoryType", bound="GeoKeyDirectoryVlr")
GeoAsciiParamsType = TypeVar("GeoAsciiParamsType", bound="GeoAsciiParamsVlr")


class GeoKeyEntryStruct(ctypes.LittleEndianStructure):
    _pack_ = 1
    _fields_ = [
        ("id", ctypes.c_uint16),
        ("tiff_tag_location", ctypes.c_uint16),
        ("count", ctypes.c_uint16),
        ("value_offset", ctypes.c_uint16),
    ]

    def __init__(self, id=0, tiff_tag_location=0, count=0, value_offset=0):
        super().__init__(id=id, tiff_tag_location=tiff_tag_location, count=count, value_offset=value_offset)

    @staticmethod
    def size():
        return ctypes.sizeof(GeoKeysHeaderStructs)

    def __repr__(self):
        return "<GeoKey(Id: {}, Location: {}, count: {}, offset: {})>".format(
            self.id, self.tiff_tag_location, self.count, self.value_offset
        )


class GeoAsciiParamsVlr(BaseKnownVLR):
    def __init__(self):
        super().__init__(description="GeoTIFF GeoAsciiParamsTag")
        self.strings = []

    def parse_record_data(self, record_data):
        st = [s.decode("ascii") for s in record_data.split(NULL_BYTE)]
        if len(st) > 1:
            self.strings = st[0][:-1].split("|")
        else:
            self.strings = []

    def record_data_bytes(self):
        return NULL_BYTE.join([self.ascii_params, b""])

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

    @property
    def ascii_params(self):
        return "".join([s + "|" for s in self.strings]).encode("ascii")

    @classmethod
    def from_crs(cls: Type[GeoAsciiParamsType], crs: pyproj.CRS) -> GeoAsciiParamsType:
        self = cls()
        self.record_from_crs(crs)
        return self

    def __repr__(self):
        return "<GeoAsciiParamsVlr({})>".format(self.strings)

    @staticmethod
    def official_user_id():
        return "LASF_Projection"

    @staticmethod
    def official_record_ids():
        return (34737,)


class GeoKeysHeaderStructs(ctypes.LittleEndianStructure):
    _pack_ = 1
    _fields_ = [
        ("key_directory_version", ctypes.c_uint16),
        ("key_revision", ctypes.c_uint16),
        ("minor_revision", ctypes.c_uint16),
        ("number_of_keys", ctypes.c_uint16),
    ]

    def __init__(self, key_directory_version=1, key_revision=1, minor_revision=0, number_of_keys=0):
        super().__init__(key_directory_version=key_directory_version,
                         key_revision=key_revision,
                         minor_revision=minor_revision,
                         number_of_keys=number_of_keys)

    @staticmethod
    def size():
        return ctypes.sizeof(GeoKeysHeaderStructs)

    def __repr__(self):
        return "<GeoKeysHeader(vers: {}, rev:{}, minor: {}, num_keys: {})>".format(
            self.key_directory_version,
            self.key_revision,
            self.minor_revision,
            self.number_of_keys,
        )


class GeoKeyDirectoryVlr(BaseKnownVLR):
    def __init__(self):
        super().__init__(description="GeoTIFF GeoKeyDirectoryTag")
        self.geo_keys_header = GeoKeysHeaderStructs()
        self.geo_keys = [GeoKeyEntryStruct()]

    def parse_record_data(self, record_data):
        record_data = bytearray(record_data)
        header_data = record_data[: ctypes.sizeof(GeoKeysHeaderStructs)]
        self.geo_keys_header = GeoKeysHeaderStructs.from_buffer(header_data)
        self.geo_keys = []
        keys_data = record_data[GeoKeysHeaderStructs.size():]
        num_keys = (
                len(record_data[GeoKeysHeaderStructs.size():]) // GeoKeyEntryStruct.size()
        )
        if num_keys != self.geo_keys_header.number_of_keys:
            self.geo_keys_header.number_of_keys = num_keys

        for i in range(self.geo_keys_header.number_of_keys):
            data = keys_data[(i * GeoKeyEntryStruct.size()): (i + 1) * GeoKeyEntryStruct.size()]
            self.geo_keys.append(GeoKeyEntryStruct.from_buffer(data))

    def record_data_bytes(self):
        b = bytes(self.geo_keys_header)
        b += b"".join(map(bytes, self.geo_keys))
        return b

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
            all_keys["GTCitationGeoKey"].value_offset = \
                all_keys["GeodeticCitationGeoKey"].count + all_keys["GeodeticCitationGeoKey"].value_offset
            added_keys.append("GTCitationGeoKey")

        if crs.is_vertical:
            _, vd_name = crs.name.split(" + ")
            all_keys["VerticalCitationGeoKey"].count = len((vd_name + "|").encode("ascii"))
            all_keys["VerticalCitationGeoKey"].value_offset = \
                all_keys["GTCitationGeoKey"].count + all_keys["GTCitationGeoKey"].value_offset

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

        self.geo_keys = [all_keys[k] for k in added_keys]
        self.geo_keys_header.number_of_keys = len(self.geo_keys)

    def parse_crs(self):
        for key in self.geo_keys:
            # get ProjectedCRSGeoKey by id
            if key.id == 3072:
                return pyproj.CRS.from_epsg(key.value_offset)
        return None

    @classmethod
    def from_crs(
            cls: Type[GeoKeyDirectoryType], crs: pyproj.CRS
    ) -> GeoKeyDirectoryType:
        self = cls()
        self.record_from_crs(crs)
        return self

    def __repr__(self):
        return "<{}({} geo_keys)>".format(self.__class__.__name__, len(self.geo_keys))

    @staticmethod
    def official_user_id():
        return "LASF_Projection"

    @staticmethod
    def official_record_ids():
        return (34735,)
