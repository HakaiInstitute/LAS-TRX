import enum
import os
from datetime import date

from csrspy.enums import CoordType, Reference, VerticalDatum
from csrspy.utils import date_to_decimal_year
from pydantic import BaseModel
from pyproj.crs import (
    CRS,
    CompoundCRS,
    GeocentricCRS,
    GeographicCRS,
    ProjectedCRS,
    VerticalCRS,
)
from pyproj.crs.coordinate_operation import UTMConversion
from pyproj.crs.coordinate_system import Cartesian2DCS


class CSRSPYConfig(BaseModel):
    s_ref_frame: Reference
    s_epoch: float
    s_vd: VerticalDatum
    s_coords: CoordType
    t_ref_frame: Reference
    t_epoch: float
    t_vd: VerticalDatum
    t_coords: CoordType


class TrxVd(str, enum.Enum):
    WGS84 = "WGS84"
    GRS80 = "GRS80"
    CGG2013A = "CGVD2013/CGG2013a"
    CGG2013 = "CGVD2013/CGG2013"
    HT2_2010v70 = "CGVD28/HT2_2010v70"

    @property
    def vertical_crs(self) -> VerticalCRS | None:
        if self == TrxVd.CGG2013:
            return VerticalCRS.from_epsg(6647)
        elif self == TrxVd.CGG2013A:
            return VerticalCRS.from_dict({
                "$schema": "https://proj.org/schemas/v0.7/projjson.schema.json",
                "type": "VerticalCRS",
                "name": "CGVD2013(CGG2013a) height",
                "datum": {
                    "type": "VerticalReferenceFrame",
                    "name": "Canadian Geodetic Vertical Datum of 2013 (CGG2013a)",
                },
                "coordinate_system": {
                    "subtype": "vertical",
                    "axis": [
                        {
                            "name": "Gravity-related height",
                            "abbreviation": "H",
                            "direction": "up",
                            "unit": "metre",
                        }
                    ],
                },
                "scope": "Geodesy, engineering survey, topographic mapping.",
                "area": (
                    "Canada - onshore and offshore - Alberta; British Columbia; Manitoba; New Brunswick; "
                    "Newfoundland and Labrador; Northwest Territories; Nova Scotia; Nunavut; Ontario; "
                    "Prince Edward Island; Quebec; Saskatchewan; Yukon."
                ),
                "bbox": {
                    "south_latitude": 38.21,
                    "west_longitude": -141.01,
                    "north_latitude": 86.46,
                    "east_longitude": -40.73,
                },
            })
        elif self == TrxVd.HT2_2010v70:
            return VerticalCRS.from_epsg(5713)
        return None

    def to_csrspy(self) -> VerticalDatum:
        return {
            TrxVd.WGS84: VerticalDatum.WGS84,
            TrxVd.GRS80: VerticalDatum.GRS80,
            TrxVd.CGG2013A: VerticalDatum.CGG2013A,
            TrxVd.CGG2013: VerticalDatum.CGG2013,
            TrxVd.HT2_2010v70: VerticalDatum.HT2_2010v70,
        }[self]


class TrxReference(str, enum.Enum):
    NAD83CSRS = "NAD83(CSRS)"
    WGS84 = "WGS84"
    ITRF20 = "ITRF2020"
    ITRF14 = "ITRF2014"
    ITRF08 = "ITRF2008"
    ITRF05 = "ITRF2005"
    ITRF00 = "ITRF2000"
    ITRF97 = "ITRF97"
    ITRF96 = "ITRF96"
    ITRF94 = "ITRF94"
    ITRF93 = "ITRF93"
    ITRF92 = "ITRF92"
    ITRF91 = "ITRF91"
    ITRF90 = "ITRF90"
    ITRF89 = "ITRF89"
    ITRF88 = "ITRF88"

    @property
    def geodetic_crs(self) -> GeographicCRS:
        if self == TrxReference.NAD83CSRS:
            return GeographicCRS.from_epsg(4617)
        elif self == TrxReference.ITRF20:
            return GeographicCRS.from_epsg(9989)
        elif self == TrxReference.ITRF14:
            return GeographicCRS.from_epsg(9000)
        elif self == TrxReference.ITRF08:
            return GeographicCRS.from_epsg(8999)
        elif self == TrxReference.ITRF05:
            return GeographicCRS.from_epsg(8998)
        elif self == TrxReference.ITRF00:
            return GeographicCRS.from_epsg(8997)
        elif self == TrxReference.ITRF97:
            return GeographicCRS.from_epsg(8996)
        elif self == TrxReference.ITRF96:
            return GeographicCRS.from_epsg(8995)
        elif self == TrxReference.ITRF94:
            return GeographicCRS.from_epsg(8994)
        elif self == TrxReference.ITRF93:
            return GeographicCRS.from_epsg(8993)
        elif self == TrxReference.ITRF92:
            return GeographicCRS.from_epsg(8992)
        elif self == TrxReference.ITRF91:
            return GeographicCRS.from_epsg(8991)
        elif self == TrxReference.ITRF90:
            return GeographicCRS.from_epsg(8990)
        elif self == TrxReference.ITRF89:
            return GeographicCRS.from_epsg(8989)
        elif self == TrxReference.ITRF88:
            return GeographicCRS.from_epsg(8988)
        elif self == TrxReference.WGS84:
            return GeographicCRS.from_epsg(4326)
        else:
            raise KeyError(f"No implementation found for {self}")

    def to_csrspy(self) -> Reference:
        return {
            TrxReference.NAD83CSRS: Reference.NAD83CSRS,
            TrxReference.WGS84: Reference.WGS84,
            TrxReference.ITRF20: Reference.ITRF20,
            TrxReference.ITRF14: Reference.ITRF14,
            TrxReference.ITRF08: Reference.ITRF08,
            TrxReference.ITRF05: Reference.ITRF05,
            TrxReference.ITRF00: Reference.ITRF00,
            TrxReference.ITRF97: Reference.ITRF97,
            TrxReference.ITRF96: Reference.ITRF96,
            TrxReference.ITRF94: Reference.ITRF94,
            TrxReference.ITRF93: Reference.ITRF93,
            TrxReference.ITRF92: Reference.ITRF92,
            TrxReference.ITRF91: Reference.ITRF91,
            TrxReference.ITRF90: Reference.ITRF90,
            TrxReference.ITRF89: Reference.ITRF89,
            TrxReference.ITRF88: Reference.ITRF88,
        }[self]


class TrxCoordType(str, enum.Enum):
    CART = "Cartesian"
    GEOG = "Geographic"
    UTM3 = "UTM3"
    UTM4 = "UTM4"
    UTM5 = "UTM5"
    UTM6 = "UTM6"
    UTM7 = "UTM7"
    UTM8 = "UTM8"
    UTM9 = "UTM9"
    UTM10 = "UTM10"
    UTM11 = "UTM11"
    UTM12 = "UTM12"
    UTM13 = "UTM13"
    UTM14 = "UTM14"
    UTM15 = "UTM15"
    UTM16 = "UTM16"
    UTM17 = "UTM17"
    UTM18 = "UTM18"
    UTM19 = "UTM19"
    UTM20 = "UTM20"
    UTM21 = "UTM21"
    UTM22 = "UTM22"
    UTM23 = "UTM23"

    def is_utm(self) -> bool:
        return self.value[:3] == "UTM"

    @property
    def utm_zone(self) -> int:
        if not self.is_utm():
            raise ValueError(f"{self} is not an UTM type")
        return int(self.value[3:])

    @classmethod
    def from_utm_zone(cls, zone: int) -> "TrxCoordType":
        if zone < 3 or zone > 23:
            raise ValueError(f"Unsupported UTM zone {zone}")
        return cls(f"UTM{zone}")

    def to_csrspy(self) -> CoordType:
        return {
            TrxCoordType.CART: CoordType.CART,
            TrxCoordType.GEOG: CoordType.GEOG,
            TrxCoordType.UTM3: CoordType.UTM3,
            TrxCoordType.UTM4: CoordType.UTM4,
            TrxCoordType.UTM5: CoordType.UTM5,
            TrxCoordType.UTM6: CoordType.UTM6,
            TrxCoordType.UTM7: CoordType.UTM7,
            TrxCoordType.UTM8: CoordType.UTM8,
            TrxCoordType.UTM9: CoordType.UTM9,
            TrxCoordType.UTM10: CoordType.UTM10,
            TrxCoordType.UTM11: CoordType.UTM11,
            TrxCoordType.UTM12: CoordType.UTM12,
            TrxCoordType.UTM13: CoordType.UTM13,
            TrxCoordType.UTM14: CoordType.UTM14,
            TrxCoordType.UTM15: CoordType.UTM15,
            TrxCoordType.UTM16: CoordType.UTM16,
            TrxCoordType.UTM17: CoordType.UTM17,
            TrxCoordType.UTM18: CoordType.UTM18,
            TrxCoordType.UTM19: CoordType.UTM19,
            TrxCoordType.UTM20: CoordType.UTM20,
            TrxCoordType.UTM21: CoordType.UTM21,
            TrxCoordType.UTM22: CoordType.UTM22,
            TrxCoordType.UTM23: CoordType.UTM23,
        }[self]


class ReferenceConfig(BaseModel):
    ref_frame: TrxReference
    epoch: date
    vd: TrxVd
    coord_type: TrxCoordType

    @property
    def crs(self) -> CRS:
        geodetic_crs = self.ref_frame.geodetic_crs

        # See compound CRS docs https://pyproj4.github.io/pyproj/stable/build_crs.html
        if self.coord_type == TrxCoordType.CART:
            xy_crs = GeocentricCRS(name=geodetic_crs.name, datum=geodetic_crs.datum)
        elif self.coord_type == TrxCoordType.GEOG:
            xy_crs = geodetic_crs
        elif self.coord_type.is_utm():
            xy_crs = ProjectedCRS(
                name=f"{geodetic_crs.name} / UTM zone {self.coord_type.utm_zone}N",
                conversion=UTMConversion(str(self.coord_type.utm_zone), hemisphere="N"),
                geodetic_crs=geodetic_crs,
                cartesian_cs=Cartesian2DCS(),
            )
        else:
            raise IndexError(f"Could not create horizont CRS for {self.coords}")

        z_crs = self.vd.vertical_crs

        if z_crs is not None and not xy_crs.is_geocentric:
            return CompoundCRS(name=f"{xy_crs.name} + {z_crs.name}", components=[xy_crs, z_crs])
        elif xy_crs.is_geographic:
            return xy_crs.to_3d()

        return xy_crs

    def to_csrspy(self) -> dict:
        return {
            "ref_frame": self.ref_frame.to_csrspy(),
            "epoch": date_to_decimal_year(self.epoch),
            "vd": self.vd.to_csrspy(),
            "coords": self.coord_type.to_csrspy(),
        }


class TransformConfig(BaseModel):
    origin: ReferenceConfig
    destination: ReferenceConfig
    max_workers: int = os.cpu_count()

    def to_csrspy(self) -> CSRSPYConfig:
        s = self.origin.to_csrspy()
        t = self.destination.to_csrspy()

        return CSRSPYConfig(
            s_ref_frame=s["ref_frame"],
            s_coords=s["coords"],
            s_vd=s["vd"],
            s_epoch=s["epoch"],
            t_ref_frame=t["ref_frame"],
            t_coords=t["coords"],
            t_vd=t["vd"],
            t_epoch=t["epoch"],
        )
