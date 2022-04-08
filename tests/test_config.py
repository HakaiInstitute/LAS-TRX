from csrspy.enums import CoordType, Reference, VerticalDatum

from las_trx.config import TransformConfig

DEFAULT_S_PARAMS = {
    's_ref_frame': Reference.NAD83CSRS,
    's_vd': VerticalDatum.GRS80,
    's_coords': CoordType.UTM10,
    's_epoch': 2010,
}


def test_t_crs_nad83_geog_grs80():
    config = TransformConfig(
        **DEFAULT_S_PARAMS,
        t_ref_frame=Reference.NAD83CSRS,
        t_vd=VerticalDatum.GRS80,
        t_coords=CoordType.GEOG,
        t_epoch=2010,
    )
    assert config.t_crs.to_epsg() == 4955


def test_t_crs_nad83_geog_cgvd2013():
    config = TransformConfig(
        **DEFAULT_S_PARAMS,
        t_ref_frame=Reference.NAD83CSRS,
        t_vd=VerticalDatum.CGG2013A,
        t_coords=CoordType.GEOG,
        t_epoch=2010,
    )
    assert config.t_crs.to_epsg() == 6649


def test_t_crs_nad83_geog_cgvd28():
    config = TransformConfig(
        **DEFAULT_S_PARAMS,
        t_ref_frame=Reference.NAD83CSRS,
        t_vd=VerticalDatum.HT2_2010v70,
        t_coords=CoordType.GEOG,
        t_epoch=2010,
    )
    assert config.t_crs.is_compound
    assert config.t_crs.name == "NAD83(CSRS) + CGVD28 height"
    assert config.t_crs.to_epsg() is None


def test_t_crs_nad83_utm9_grs80():
    config = TransformConfig(
        **DEFAULT_S_PARAMS,
        t_ref_frame=Reference.NAD83CSRS,
        t_vd=VerticalDatum.GRS80,
        t_coords=CoordType.UTM9,
        t_epoch=2010,
    )
    assert config.t_crs.is_projected
    assert config.t_crs.name == "NAD83(CSRS) / UTM zone 9N"
    assert config.t_crs.ellipsoid.name == "GRS 1980"


def test_t_crs_nad83_utm9_cgvd2013():
    config = TransformConfig(
        **DEFAULT_S_PARAMS,
        t_ref_frame=Reference.NAD83CSRS,
        t_vd=VerticalDatum.CGG2013A,
        t_coords=CoordType.UTM9,
        t_epoch=2010,
    )
    assert config.t_crs.to_epsg() == 6652


def test_t_crs_nad83_utm9_cgvd28():
    config = TransformConfig(
        **DEFAULT_S_PARAMS,
        t_ref_frame=Reference.NAD83CSRS,
        t_vd=VerticalDatum.HT2_2010v70,
        t_coords=CoordType.UTM9,
        t_epoch=2010,
    )
    assert config.t_crs.is_compound
    assert config.t_crs.name == "NAD83(CSRS) / UTM zone 9N + CGVD28 height"


def test_t_crs_nad83_utm10_grs80():
    config = TransformConfig(
        **DEFAULT_S_PARAMS,
        t_ref_frame=Reference.NAD83CSRS,
        t_vd=VerticalDatum.GRS80,
        t_coords=CoordType.UTM10,
        t_epoch=2010,
    )
    assert config.t_crs.is_projected
    assert config.t_crs.name == "NAD83(CSRS) / UTM zone 10N"
    assert config.t_crs.ellipsoid.name == "GRS 1980"


def test_t_crs_nad83_utm10_cgvd2013():
    config = TransformConfig(
        **DEFAULT_S_PARAMS,
        t_ref_frame=Reference.NAD83CSRS,
        t_vd=VerticalDatum.CGG2013A,
        t_coords=CoordType.UTM10,
        t_epoch=2010,
    )
    assert config.t_crs.to_epsg() == 6653


def test_t_crs_nad83_utm10_cgvd28():
    config = TransformConfig(
        **DEFAULT_S_PARAMS,
        t_ref_frame=Reference.NAD83CSRS,
        t_vd=VerticalDatum.HT2_2010v70,
        t_coords=CoordType.UTM10,
        t_epoch=2010,
    )
    assert config.t_crs.is_compound
    assert config.t_crs.name == "NAD83(CSRS) / UTM zone 10N + CGVD28 height"


def test_t_crs_nad83_utm11_grs80():
    config = TransformConfig(
        **DEFAULT_S_PARAMS,
        t_ref_frame=Reference.NAD83CSRS,
        t_vd=VerticalDatum.GRS80,
        t_coords=CoordType.UTM11,
        t_epoch=2010,
    )
    assert config.t_crs.is_projected
    assert config.t_crs.name == "NAD83(CSRS) / UTM zone 11N"
    assert config.t_crs.ellipsoid.name == "GRS 1980"


def test_t_crs_nad83_utm11_cgvd2013():
    config = TransformConfig(
        **DEFAULT_S_PARAMS,
        t_ref_frame=Reference.NAD83CSRS,
        t_vd=VerticalDatum.CGG2013A,
        t_coords=CoordType.UTM11,
        t_epoch=2010,
    )
    assert config.t_crs.to_epsg() == 6654


def test_t_crs_nad83_utm11_cgvd28():
    config = TransformConfig(
        **DEFAULT_S_PARAMS,
        t_ref_frame=Reference.NAD83CSRS,
        t_vd=VerticalDatum.HT2_2010v70,
        t_coords=CoordType.UTM11,
        t_epoch=2010,
    )
    assert config.t_crs.is_compound
    assert config.t_crs.name == "NAD83(CSRS) / UTM zone 11N + CGVD28 height"


def test_t_crs_nad83_cart_grs80():
    config = TransformConfig(
        **DEFAULT_S_PARAMS,
        t_ref_frame=Reference.NAD83CSRS,
        t_vd=VerticalDatum.GRS80,
        t_coords=CoordType.CART,
        t_epoch=2010,
    )
    assert config.t_crs.is_geocentric
    assert config.t_crs.name == "NAD83(CSRS)"
    assert config.t_crs.to_epsg() == 4954


def test_t_crs_nad83_cart_cgvd2013():
    config = TransformConfig(
        **DEFAULT_S_PARAMS,
        t_ref_frame=Reference.NAD83CSRS,
        t_vd=VerticalDatum.CGG2013A,
        t_coords=CoordType.CART,
        t_epoch=2010,
    )
    assert config.t_crs.is_geocentric
    assert config.t_crs.name == "NAD83(CSRS)"
    assert config.t_crs.to_epsg() == 4954


def test_t_crs_nad83_cart_cgvd28():
    config = TransformConfig(
        **DEFAULT_S_PARAMS,
        t_ref_frame=Reference.NAD83CSRS,
        t_vd=VerticalDatum.HT2_2010v70,
        t_coords=CoordType.CART,
        t_epoch=2010,
    )
    assert config.t_crs.is_geocentric
    assert config.t_crs.name == "NAD83(CSRS)"
    assert config.t_crs.to_epsg() == 4954


def test_t_crs_itrf14_geog_grs80():
    config = TransformConfig(
        **DEFAULT_S_PARAMS,
        t_ref_frame=Reference.ITRF14,
        t_vd=VerticalDatum.GRS80,
        t_coords=CoordType.GEOG,
        t_epoch=2010,
    )
    assert config.t_crs.is_geographic
    assert config.t_crs.name == "ITRF2014"
    assert config.t_crs.to_epsg() == 7912


def test_t_crs_itrf14_geog_cgvd2013():
    config = TransformConfig(
        **DEFAULT_S_PARAMS,
        t_ref_frame=Reference.ITRF14,
        t_vd=VerticalDatum.CGG2013A,
        t_coords=CoordType.GEOG,
        t_epoch=2010,
    )
    assert config.t_crs.is_geographic
    assert config.t_crs.name == "ITRF2014 + CGVD2013(CGG2013) height"
    assert config.t_crs.to_epsg() is None


def test_t_crs_itrf14_geog_cgvd28():
    config = TransformConfig(
        **DEFAULT_S_PARAMS,
        t_ref_frame=Reference.ITRF14,
        t_vd=VerticalDatum.HT2_2010v70,
        t_coords=CoordType.GEOG,
        t_epoch=2010,
    )
    assert config.t_crs.is_geographic
    assert config.t_crs.name == "ITRF2014 + CGVD28 height"
    assert config.t_crs.to_epsg() is None




def test_t_crs_itrf_utm9_grs80():
    config = TransformConfig(
        **DEFAULT_S_PARAMS,
        t_ref_frame=Reference.ITRF14,
        t_vd=VerticalDatum.GRS80,
        t_coords=CoordType.UTM9,
        t_epoch=2010,
    )
    assert config.t_crs.is_projected
    assert config.t_crs.name == "ITRF2014 / UTM zone 9N"
    assert config.t_crs.ellipsoid.name == "GRS 1980"


def test_t_crs_itrf_utm9_cgvd2013():
    config = TransformConfig(
        **DEFAULT_S_PARAMS,
        t_ref_frame=Reference.ITRF14,
        t_vd=VerticalDatum.CGG2013A,
        t_coords=CoordType.UTM9,
        t_epoch=2010,
    )
    assert config.t_crs.is_compound
    assert config.t_crs.name == "ITRF2014 / UTM zone 9N + CGVD2013(CGG2013) height"


def test_t_crs_itrf_utm9_cgvd28():
    config = TransformConfig(
        **DEFAULT_S_PARAMS,
        t_ref_frame=Reference.ITRF14,
        t_vd=VerticalDatum.HT2_2010v70,
        t_coords=CoordType.UTM9,
        t_epoch=2010,
    )
    assert config.t_crs.is_compound
    assert config.t_crs.name == "ITRF2014 / UTM zone 9N + CGVD28 height"


def test_t_crs_itrf_utm10_grs80():
    config = TransformConfig(
        **DEFAULT_S_PARAMS,
        t_ref_frame=Reference.ITRF14,
        t_vd=VerticalDatum.GRS80,
        t_coords=CoordType.UTM10,
        t_epoch=2010,
    )
    assert config.t_crs.is_projected
    assert config.t_crs.name == "ITRF2014 / UTM zone 10N"
    assert config.t_crs.ellipsoid.name == "GRS 1980"


def test_t_crs_itrf_utm10_cgvd2013():
    config = TransformConfig(
        **DEFAULT_S_PARAMS,
        t_ref_frame=Reference.ITRF14,
        t_vd=VerticalDatum.CGG2013A,
        t_coords=CoordType.UTM10,
        t_epoch=2010,
    )
    assert config.t_crs.is_compound
    assert config.t_crs.name == "ITRF2014 / UTM zone 10N + CGVD2013(CGG2013) height"


def test_t_crs_itrf_utm10_cgvd28():
    config = TransformConfig(
        **DEFAULT_S_PARAMS,
        t_ref_frame=Reference.ITRF14,
        t_vd=VerticalDatum.HT2_2010v70,
        t_coords=CoordType.UTM10,
        t_epoch=2010,
    )
    assert config.t_crs.is_compound
    assert config.t_crs.name == "ITRF2014 / UTM zone 10N + CGVD28 height"


def test_t_crs_itrf_utm11_grs80():
    config = TransformConfig(
        **DEFAULT_S_PARAMS,
        t_ref_frame=Reference.ITRF14,
        t_vd=VerticalDatum.GRS80,
        t_coords=CoordType.UTM11,
        t_epoch=2010,
    )
    assert config.t_crs.is_projected
    assert config.t_crs.name == "ITRF2014 / UTM zone 11N"
    assert config.t_crs.ellipsoid.name == "GRS 1980"


def test_t_crs_itrf_utm11_cgvd2013():
    config = TransformConfig(
        **DEFAULT_S_PARAMS,
        t_ref_frame=Reference.ITRF14,
        t_vd=VerticalDatum.CGG2013A,
        t_coords=CoordType.UTM11,
        t_epoch=2010,
    )
    assert config.t_crs.is_compound
    assert config.t_crs.name == "ITRF2014 / UTM zone 11N + CGVD2013(CGG2013) height"


def test_t_crs_itrf_utm11_cgvd28():
    config = TransformConfig(
        **DEFAULT_S_PARAMS,
        t_ref_frame=Reference.ITRF14,
        t_vd=VerticalDatum.HT2_2010v70,
        t_coords=CoordType.UTM11,
        t_epoch=2010,
    )
    assert config.t_crs.is_compound
    assert config.t_crs.name == "ITRF2014 / UTM zone 11N + CGVD28 height"


def test_t_crs_itrf_cart_grs80():
    config = TransformConfig(
        **DEFAULT_S_PARAMS,
        t_ref_frame=Reference.ITRF14,
        t_vd=VerticalDatum.GRS80,
        t_coords=CoordType.CART,
        t_epoch=2010,
    )
    assert config.t_crs.is_geocentric
    assert config.t_crs.name == "ITRF2014"
    assert config.t_crs.ellipsoid.name == "GRS 1980"


def test_t_crs_itrf_cart_cgvd2013():
    config = TransformConfig(
        **DEFAULT_S_PARAMS,
        t_ref_frame=Reference.ITRF14,
        t_vd=VerticalDatum.CGG2013A,
        t_coords=CoordType.CART,
        t_epoch=2010,
    )
    assert config.t_crs.is_compound
    assert config.t_crs.name == "ITRF2014 + CGVD2013(CGG2013) height"


def test_t_crs_itrf_cart_cgvd28():
    config = TransformConfig(
        **DEFAULT_S_PARAMS,
        t_ref_frame=Reference.ITRF14,
        t_vd=VerticalDatum.HT2_2010v70,
        t_coords=CoordType.CART,
        t_epoch=2010,
    )
    assert config.t_crs.is_compound
    assert config.t_crs.name == "ITRF2014 + CGVD28 height"