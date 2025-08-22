from datetime import date

from las_trx.config import (
    ReferenceConfig,
    TransformConfig,
    TrxCoordType,
    TrxReference,
    TrxVd,
)

ORIGIN_REFERENCE = ReferenceConfig(
    ref_frame=TrxReference.NAD83CSRS,
    vd=TrxVd.GRS80,
    coord_type=TrxCoordType.UTM10,
    epoch=date(2010, 1, 1),
)


def test_t_crs_nad83_geog_grs80():
    config = TransformConfig(
        origin=ORIGIN_REFERENCE,
        destination=ReferenceConfig(
            ref_frame=TrxReference.NAD83CSRS,
            vd=TrxVd.GRS80,
            coord_type=TrxCoordType.GEOG,
            epoch=date(2010, 1, 1),
        ),
    )
    assert config.destination.crs.to_epsg() == 4955


def test_t_crs_nad83_geog_cgvd2013():
    config = TransformConfig(
        origin=ORIGIN_REFERENCE,
        destination=ReferenceConfig(
            ref_frame=TrxReference.NAD83CSRS,
            vd=TrxVd.CGG2013,
            coord_type=TrxCoordType.GEOG,
            epoch=date(2010, 1, 1),
        ),
    )
    assert config.destination.crs.to_epsg() == 6649


def test_t_crs_nad83_geog_cgvd28():
    config = TransformConfig(
        origin=ORIGIN_REFERENCE,
        destination=ReferenceConfig(
            ref_frame=TrxReference.NAD83CSRS,
            vd=TrxVd.HT2_2010v70,
            coord_type=TrxCoordType.GEOG,
            epoch=date(2010, 1, 1),
        ),
    )
    assert config.destination.crs.is_compound
    assert config.destination.crs.name == "NAD83(CSRS) + CGVD28 height"
    assert config.destination.crs.to_epsg() is None


def test_t_crs_nad83_utm9_grs80():
    config = TransformConfig(
        origin=ORIGIN_REFERENCE,
        destination=ReferenceConfig(
            ref_frame=TrxReference.NAD83CSRS,
            vd=TrxVd.GRS80,
            coord_type=TrxCoordType.UTM9,
            epoch=date(2010, 1, 1),
        ),
    )
    assert config.destination.crs.is_projected
    assert config.destination.crs.name == "NAD83(CSRS) / UTM zone 9N"
    assert config.destination.crs.ellipsoid.name == "GRS 1980"


def test_t_crs_nad83_utm9_cgvd2013():
    config = TransformConfig(
        origin=ORIGIN_REFERENCE,
        destination=ReferenceConfig(
            ref_frame=TrxReference.NAD83CSRS,
            vd=TrxVd.CGG2013,
            coord_type=TrxCoordType.UTM9,
            epoch=date(2010, 1, 1),
        ),
    )
    assert config.destination.crs.to_epsg() == 6652


def test_t_crs_nad83_utm9_cgvd28():
    config = TransformConfig(
        origin=ORIGIN_REFERENCE,
        destination=ReferenceConfig(
            ref_frame=TrxReference.NAD83CSRS,
            vd=TrxVd.HT2_2010v70,
            coord_type=TrxCoordType.UTM9,
            epoch=date(2010, 1, 1),
        ),
    )
    assert config.destination.crs.is_compound
    assert config.destination.crs.name == "NAD83(CSRS) / UTM zone 9N + CGVD28 height"


def test_t_crs_nad83_utm10_grs80():
    config = TransformConfig(
        origin=ORIGIN_REFERENCE,
        destination=ReferenceConfig(
            ref_frame=TrxReference.NAD83CSRS,
            vd=TrxVd.GRS80,
            coord_type=TrxCoordType.UTM10,
            epoch=date(2010, 1, 1),
        ),
    )
    assert config.destination.crs.is_projected
    assert config.destination.crs.name == "NAD83(CSRS) / UTM zone 10N"
    assert config.destination.crs.ellipsoid.name == "GRS 1980"


def test_t_crs_nad83_utm10_cgvd2013():
    config = TransformConfig(
        origin=ORIGIN_REFERENCE,
        destination=ReferenceConfig(
            ref_frame=TrxReference.NAD83CSRS,
            vd=TrxVd.CGG2013,
            coord_type=TrxCoordType.UTM10,
            epoch=date(2010, 1, 1),
        ),
    )
    assert config.destination.crs.to_epsg() == 6653


def test_t_crs_nad83_utm10_cgvd28():
    config = TransformConfig(
        origin=ORIGIN_REFERENCE,
        destination=ReferenceConfig(
            ref_frame=TrxReference.NAD83CSRS,
            vd=TrxVd.HT2_2010v70,
            coord_type=TrxCoordType.UTM10,
            epoch=date(2010, 1, 1),
        ),
    )
    assert config.destination.crs.is_compound
    assert config.destination.crs.name == "NAD83(CSRS) / UTM zone 10N + CGVD28 height"


def test_t_crs_nad83_utm11_grs80():
    config = TransformConfig(
        origin=ORIGIN_REFERENCE,
        destination=ReferenceConfig(
            ref_frame=TrxReference.NAD83CSRS,
            vd=TrxVd.GRS80,
            coord_type=TrxCoordType.UTM11,
            epoch=date(2010, 1, 1),
        ),
    )
    assert config.destination.crs.is_projected
    assert config.destination.crs.name == "NAD83(CSRS) / UTM zone 11N"
    assert config.destination.crs.ellipsoid.name == "GRS 1980"


def test_t_crs_nad83_utm11_cgvd2013():
    config = TransformConfig(
        origin=ORIGIN_REFERENCE,
        destination=ReferenceConfig(
            ref_frame=TrxReference.NAD83CSRS,
            vd=TrxVd.CGG2013,
            coord_type=TrxCoordType.UTM11,
            epoch=date(2010, 1, 1),
        ),
    )
    assert config.destination.crs.to_epsg() == 6654


def test_t_crs_nad83_utm11_cgvd28():
    config = TransformConfig(
        origin=ORIGIN_REFERENCE,
        destination=ReferenceConfig(
            ref_frame=TrxReference.NAD83CSRS,
            vd=TrxVd.HT2_2010v70,
            coord_type=TrxCoordType.UTM11,
            epoch=date(2010, 1, 1),
        ),
    )
    assert config.destination.crs.is_compound
    assert config.destination.crs.name == "NAD83(CSRS) / UTM zone 11N + CGVD28 height"


def test_t_crs_nad83_cart_grs80():
    config = TransformConfig(
        origin=ORIGIN_REFERENCE,
        destination=ReferenceConfig(
            ref_frame=TrxReference.NAD83CSRS,
            vd=TrxVd.GRS80,
            coord_type=TrxCoordType.CART,
            epoch=date(2010, 1, 1),
        ),
    )
    assert config.destination.crs.is_geocentric
    assert config.destination.crs.name == "NAD83(CSRS)"
    assert config.destination.crs.to_epsg() == 4954


def test_t_crs_nad83_cart_cgvd2013():
    config = TransformConfig(
        origin=ORIGIN_REFERENCE,
        destination=ReferenceConfig(
            ref_frame=TrxReference.NAD83CSRS,
            vd=TrxVd.CGG2013A,
            coord_type=TrxCoordType.CART,
            epoch=date(2010, 1, 1),
        ),
    )
    assert config.destination.crs.is_geocentric
    assert config.destination.crs.name == "NAD83(CSRS)"
    assert config.destination.crs.to_epsg() == 4954


def test_t_crs_nad83_cart_cgvd28():
    config = TransformConfig(
        origin=ORIGIN_REFERENCE,
        destination=ReferenceConfig(
            ref_frame=TrxReference.NAD83CSRS,
            vd=TrxVd.HT2_2010v70,
            coord_type=TrxCoordType.CART,
            epoch=date(2010, 1, 1),
        ),
    )
    assert config.destination.crs.is_geocentric
    assert config.destination.crs.name == "NAD83(CSRS)"
    assert config.destination.crs.to_epsg() == 4954


def test_t_crs_itrf14_geog_grs80():
    config = TransformConfig(
        origin=ORIGIN_REFERENCE,
        destination=ReferenceConfig(
            ref_frame=TrxReference.ITRF14,
            vd=TrxVd.GRS80,
            coord_type=TrxCoordType.GEOG,
            epoch=date(2010, 1, 1),
        ),
    )
    assert config.destination.crs.is_geographic
    assert config.destination.crs.name == "ITRF2014"
    assert config.destination.crs.to_epsg() == 7912


def test_t_crs_itrf14_geog_cgvd2013():
    config = TransformConfig(
        origin=ORIGIN_REFERENCE,
        destination=ReferenceConfig(
            ref_frame=TrxReference.ITRF14,
            vd=TrxVd.CGG2013A,
            coord_type=TrxCoordType.GEOG,
            epoch=date(2010, 1, 1),
        ),
    )
    assert config.destination.crs.is_geographic
    assert config.destination.crs.name == "ITRF2014 + CGVD2013(CGG2013a) height"
    assert config.destination.crs.to_epsg() is None


def test_t_crs_itrf14_geog_cgvd28():
    config = TransformConfig(
        origin=ORIGIN_REFERENCE,
        destination=ReferenceConfig(
            ref_frame=TrxReference.ITRF14,
            vd=TrxVd.HT2_2010v70,
            coord_type=TrxCoordType.GEOG,
            epoch=date(2010, 1, 1),
        ),
    )
    assert config.destination.crs.is_geographic
    assert config.destination.crs.name == "ITRF2014 + CGVD28 height"
    assert config.destination.crs.to_epsg() is None


def test_t_crs_itrf_utm9_grs80():
    config = TransformConfig(
        origin=ORIGIN_REFERENCE,
        destination=ReferenceConfig(
            ref_frame=TrxReference.ITRF14,
            vd=TrxVd.GRS80,
            coord_type=TrxCoordType.UTM9,
            epoch=date(2010, 1, 1),
        ),
    )
    assert config.destination.crs.is_projected
    assert config.destination.crs.name == "ITRF2014 / UTM zone 9N"
    assert config.destination.crs.ellipsoid.name == "GRS 1980"


def test_t_crs_itrf_utm9_cgvd2013():
    config = TransformConfig(
        origin=ORIGIN_REFERENCE,
        destination=ReferenceConfig(
            ref_frame=TrxReference.ITRF14,
            vd=TrxVd.CGG2013A,
            coord_type=TrxCoordType.UTM9,
            epoch=date(2010, 1, 1),
        ),
    )
    assert config.destination.crs.is_compound
    assert config.destination.crs.name == "ITRF2014 / UTM zone 9N + CGVD2013(CGG2013a) height"


def test_t_crs_itrf_utm9_cgvd28():
    config = TransformConfig(
        origin=ORIGIN_REFERENCE,
        destination=ReferenceConfig(
            ref_frame=TrxReference.ITRF14,
            vd=TrxVd.HT2_2010v70,
            coord_type=TrxCoordType.UTM9,
            epoch=date(2010, 1, 1),
        ),
    )
    assert config.destination.crs.is_compound
    assert config.destination.crs.name == "ITRF2014 / UTM zone 9N + CGVD28 height"


def test_t_crs_itrf_utm10_grs80():
    config = TransformConfig(
        origin=ORIGIN_REFERENCE,
        destination=ReferenceConfig(
            ref_frame=TrxReference.ITRF14,
            vd=TrxVd.GRS80,
            coord_type=TrxCoordType.UTM10,
            epoch=date(2010, 1, 1),
        ),
    )
    assert config.destination.crs.is_projected
    assert config.destination.crs.name == "ITRF2014 / UTM zone 10N"
    assert config.destination.crs.ellipsoid.name == "GRS 1980"


def test_t_crs_itrf_utm10_cgvd2013():
    config = TransformConfig(
        origin=ORIGIN_REFERENCE,
        destination=ReferenceConfig(
            ref_frame=TrxReference.ITRF14,
            vd=TrxVd.CGG2013A,
            coord_type=TrxCoordType.UTM10,
            epoch=date(2010, 1, 1),
        ),
    )
    assert config.destination.crs.is_compound
    assert config.destination.crs.name == "ITRF2014 / UTM zone 10N + CGVD2013(CGG2013a) height"


def test_t_crs_itrf_utm10_cgvd28():
    config = TransformConfig(
        origin=ORIGIN_REFERENCE,
        destination=ReferenceConfig(
            ref_frame=TrxReference.ITRF14,
            vd=TrxVd.HT2_2010v70,
            coord_type=TrxCoordType.UTM10,
            epoch=date(2010, 1, 1),
        ),
    )
    assert config.destination.crs.is_compound
    assert config.destination.crs.name == "ITRF2014 / UTM zone 10N + CGVD28 height"


def test_t_crs_itrf_utm11_grs80():
    config = TransformConfig(
        origin=ORIGIN_REFERENCE,
        destination=ReferenceConfig(
            ref_frame=TrxReference.ITRF14,
            vd=TrxVd.GRS80,
            coord_type=TrxCoordType.UTM11,
            epoch=date(2010, 1, 1),
        ),
    )
    assert config.destination.crs.is_projected
    assert config.destination.crs.name == "ITRF2014 / UTM zone 11N"
    assert config.destination.crs.ellipsoid.name == "GRS 1980"


def test_t_crs_itrf_utm11_cgvd2013():
    config = TransformConfig(
        origin=ORIGIN_REFERENCE,
        destination=ReferenceConfig(
            ref_frame=TrxReference.ITRF14,
            vd=TrxVd.CGG2013A,
            coord_type=TrxCoordType.UTM11,
            epoch=date(2010, 1, 1),
        ),
    )
    assert config.destination.crs.is_compound
    assert config.destination.crs.name == "ITRF2014 / UTM zone 11N + CGVD2013(CGG2013a) height"


def test_t_crs_itrf_utm11_cgvd28():
    config = TransformConfig(
        origin=ORIGIN_REFERENCE,
        destination=ReferenceConfig(
            ref_frame=TrxReference.ITRF14,
            vd=TrxVd.HT2_2010v70,
            coord_type=TrxCoordType.UTM11,
            epoch=date(2010, 1, 1),
        ),
    )
    assert config.destination.crs.is_compound
    assert config.destination.crs.name == "ITRF2014 / UTM zone 11N + CGVD28 height"


def test_t_crs_itrf_cart_grs80():
    config = TransformConfig(
        origin=ORIGIN_REFERENCE,
        destination=ReferenceConfig(
            ref_frame=TrxReference.ITRF14,
            vd=TrxVd.GRS80,
            coord_type=TrxCoordType.CART,
            epoch=date(2010, 1, 1),
        ),
    )
    assert config.destination.crs.is_geocentric
    assert config.destination.crs.name == "ITRF2014"
    assert config.destination.crs.ellipsoid.name == "GRS 1980"


def test_t_crs_itrf_cart_cgvd2013():
    config = TransformConfig(
        origin=ORIGIN_REFERENCE,
        destination=ReferenceConfig(
            ref_frame=TrxReference.ITRF14,
            vd=TrxVd.CGG2013A,
            coord_type=TrxCoordType.CART,
            epoch=date(2010, 1, 1),
        ),
    )
    assert config.destination.crs.is_geocentric
    # assert config.destination.crs.name == "ITRF2014 + CGVD2013(CGG2013) height"


def test_t_crs_itrf_cart_cgvd28():
    config = TransformConfig(
        origin=ORIGIN_REFERENCE,
        destination=ReferenceConfig(
            ref_frame=TrxReference.ITRF14,
            vd=TrxVd.HT2_2010v70,
            coord_type=TrxCoordType.CART,
            epoch=date(2010, 1, 1),
        ),
    )
    assert config.destination.crs.is_geocentric
    # assert config.destination.crs.name == "ITRF2014 + CGVD28 height"
