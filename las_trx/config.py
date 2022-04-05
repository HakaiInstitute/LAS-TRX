from datetime import date
from typing import Union

from csrspy import enums
from pydantic import BaseModel, validator

from las_trx.utils import date_to_decimal_year


class TransformConfig(BaseModel):
    s_ref_frame: Union[enums.Reference, str]
    t_ref_frame: Union[enums.Reference, str]
    s_epoch: Union[float, date]
    t_epoch: Union[float, date]
    s_vd: Union[enums.VerticalDatum, str]
    t_vd: Union[enums.VerticalDatum, str]
    s_coords: Union[enums.CoordType, str]
    t_coords: Union[enums.CoordType, str]

    # validators
    _normalize_s_epoch = validator('s_epoch', allow_reuse=True)(date_to_decimal_year)
    _normalize_t_epoch = validator('t_epoch', allow_reuse=True)(date_to_decimal_year)
