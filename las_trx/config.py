from datetime import date
from typing import Union

from pydantic import BaseModel, field_validator, FieldValidationInfo
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

from csrspy import enums
from las_trx.utils import date_to_decimal_year, get_utm_zone, is_utm_coord_type


class TransformConfig(BaseModel):
    s_ref_frame: Union[enums.Reference, str]
    t_ref_frame: Union[enums.Reference, str]
    s_epoch: Union[float, date]
    t_epoch: Union[float, date]
    s_vd: Union[enums.VerticalDatum, str]
    t_vd: Union[enums.VerticalDatum, str]
    s_coords: Union[enums.CoordType, str]
    t_coords: Union[enums.CoordType, str]

    @classmethod
    @field_validator("s_epoch", "t_epoch")
    def check_decimal_date(
        cls, v: Union[float, date], info: FieldValidationInfo
    ) -> float:
        if isinstance(v, float):
            return v
        elif isinstance(v, date):
            return date_to_decimal_year(v)
        else:
            raise TypeError(f"Invalid type for {info.field_name}: {type(v)}")

    @property
    def t_crs(self) -> CRS:
        if self.t_ref_frame == enums.Reference.NAD83CSRS:
            geodetic_crs = GeographicCRS.from_epsg(4617)
        elif self.t_ref_frame == enums.Reference.ITRF20:
            geodetic_crs = GeographicCRS.from_epsg(9989)
        elif self.t_ref_frame == enums.Reference.ITRF14:
            geodetic_crs = GeographicCRS.from_epsg(9000)
        elif self.t_ref_frame == enums.Reference.ITRF08:
            geodetic_crs = GeographicCRS.from_epsg(8999)
        elif self.t_ref_frame == enums.Reference.ITRF05:
            geodetic_crs = GeographicCRS.from_epsg(8998)
        elif self.t_ref_frame == enums.Reference.ITRF00:
            geodetic_crs = GeographicCRS.from_epsg(8997)
        elif self.t_ref_frame == enums.Reference.ITRF97:
            geodetic_crs = GeographicCRS.from_epsg(8996)
        elif self.t_ref_frame == enums.Reference.ITRF96:
            geodetic_crs = GeographicCRS.from_epsg(8995)
        elif self.t_ref_frame == enums.Reference.ITRF94:
            geodetic_crs = GeographicCRS.from_epsg(8994)
        elif self.t_ref_frame == enums.Reference.ITRF93:
            geodetic_crs = GeographicCRS.from_epsg(8993)
        elif self.t_ref_frame == enums.Reference.ITRF92:
            geodetic_crs = GeographicCRS.from_epsg(8992)
        elif self.t_ref_frame == enums.Reference.ITRF91:
            geodetic_crs = GeographicCRS.from_epsg(8991)
        elif self.t_ref_frame == enums.Reference.ITRF90:
            geodetic_crs = GeographicCRS.from_epsg(8990)
        elif self.t_ref_frame == enums.Reference.ITRF89:
            geodetic_crs = GeographicCRS.from_epsg(8989)
        elif self.t_ref_frame == enums.Reference.ITRF88:
            geodetic_crs = GeographicCRS.from_epsg(8988)
        elif self.t_ref_frame == enums.Reference.WGS84:
            geodetic_crs = GeographicCRS.from_epsg(4326)
        else:
            raise KeyError(f"No implementation found for {self.t_ref_frame}")

        # See compound CRS docs https://pyproj4.github.io/pyproj/stable/build_crs.html
        if self.t_coords == enums.CoordType.CART:
            xy_crs = GeocentricCRS(name=geodetic_crs.name, datum=geodetic_crs.datum)
        elif self.t_coords == enums.CoordType.GEOG:
            xy_crs = geodetic_crs
        elif is_utm_coord_type(self.t_coords):
            zone = get_utm_zone(self.t_coords)
            xy_crs = ProjectedCRS(
                name=f"{geodetic_crs.name} / UTM zone {zone}N",
                conversion=UTMConversion(str(zone), hemisphere="N"),
                geodetic_crs=geodetic_crs,
                cartesian_cs=Cartesian2DCS(),
            )
        else:
            raise IndexError(f"Could not create horizont CRS for {self.t_coords}")

        if self.t_vd == enums.VerticalDatum.CGG2013A:
            z_crs = VerticalCRS.from_epsg(6647)
        elif self.t_vd == enums.VerticalDatum.CGG2013:
            z_crs = VerticalCRS.from_epsg(
                6647
            )  # ??? Seems to be no distinction between 2013 and 2013a
        elif self.t_vd == enums.VerticalDatum.HT2_2010v70:
            z_crs = VerticalCRS.from_epsg(5713)
        else:
            z_crs = None

        if xy_crs.is_geocentric:
            return xy_crs
        elif z_crs is not None:
            return CompoundCRS(
                name=f"{xy_crs.name} + {z_crs.name}", components=[xy_crs, z_crs]
            )
        elif xy_crs.is_geographic:
            return xy_crs.to_3d()
        else:
            return xy_crs
