from datetime import date
from typing import Literal, Union

from csrspy import enums
from pydantic import BaseModel, validator

from las_trx.utils import date_to_decimal_year

VALID_OUTPUT_STRINGS = tuple(["geog", "cart"] + [f"utm{z}" for z in range(7, 23)])


class TransformConfig(BaseModel):
    s_ref_frame: Union[enums.Ref, str] = enums.Ref.ITRF14
    s_crs: Union[int, str]
    s_epoch: Union[float, date]
    t_epoch: Union[float, date] = None
    t_vd: Union[enums.Geoid, str] = None
    # noinspection PyTypeHints
    out: Literal[VALID_OUTPUT_STRINGS] = "geog"

    # validators
    _normalize_s_epoch = validator('s_epoch', allow_reuse=True)(date_to_decimal_year)
    _normalize_t_epoch = validator('t_epoch', allow_reuse=True)(date_to_decimal_year)
