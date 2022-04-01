import math
import os
from datetime import date

import laspy
import numpy as np
from csrspy import CSRSTransformer, enums
from tqdm.auto import tqdm

from las_trx.config import TransformConfig


def convert(input_file: str, output_file: str, config: TransformConfig):
    transformer = CSRSTransformer(**config.dict(exclude_none=True))

    with laspy.open(input_file) as in_las, \
            laspy.open(output_file, mode='w', header=in_las.header) as out_las:

        out_las.header.offsets = None  # Adjusted later using first batch
        if config.out == "geog":
            out_las.header.scales = np.array([1e-6, 1e-6, 0.001])
        else:
            out_las.header.scales = np.array([0.01, 0.01, 0.01])

        chunk_size = 1_000
        for points in tqdm(in_las.chunk_iterator(chunk_size), total=math.ceil(in_las.header.point_count / chunk_size)):
            # Convert the coordinates
            data = np.stack((points.x.scaled_array(), points.y.scaled_array(), points.z.scaled_array())).T
            data = np.array(list(transformer.forward(data)))

            # Update header offsets
            if out_las.header.offsets is None:
                out_las.header.offsets = np.min(data, axis=0)

            # Create new point records
            points.change_scaling(offsets=out_las.header.offsets)
            points.x = data[:, 0]
            points.y = data[:, 1]
            points.z = data[:, 2]
            out_las.write_points(points)

        # TODO: Update VLR data?


if __name__ == '__main__':
    if os.getenv('DEBUG', False):
        input_path = '../testfiles/408000_5635000_5m_stp_grnd_denoised.laz'
        output_path = 'testfiles/converted.laz'

        trans_config = TransformConfig(
            s_ref_frame=enums.Ref.ITRF14,
            s_crs="EPSG:32610",
            s_epoch=date(2022, 6, 22),
            t_epoch=1997.0,
            t_vd=enums.Geoid.CGG2013A,
            out='utm10')

        convert(input_path, output_path, config=trans_config)

    # TODO Add CLI config
