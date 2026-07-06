import subprocess
import sys

import cv2
import numpy as np


def test_apply_degradation_cli(tmp_path):
    input_dir = tmp_path / 'input'
    output_dir = tmp_path / 'output'
    input_dir.mkdir()

    image = np.full((8, 8, 3), 100, dtype=np.uint8)
    cv2.imwrite(str(input_dir / '000001.png'), image)

    result = subprocess.run(
        [
            sys.executable,
            'apply_degradation.py',
            '--input-dir',
            str(input_dir),
            '--output-dir',
            str(output_dir),
            '--brightness-scale',
            '0.5',
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert 'Processed images' in result.stdout
    output_image = cv2.imread(str(output_dir / '000001.png'), cv2.IMREAD_UNCHANGED)
    assert output_image is not None
    assert output_image.mean() == 50
