import json
import subprocess
import sys


def write_trajectory(path, offset=0.0):
    path.write_text(
        '#timestamp,p_RS_R_x,p_RS_R_y,p_RS_R_z,q_RS_w,q_RS_x,q_RS_y,q_RS_z\n'
        f'100,0.0,0.0,0.0,1.0,0.0,0.0,0.0\n'
        f'200,{1.0 + offset},0.0,0.0,1.0,0.0,0.0,0.0\n'
    )


def test_evaluate_trajectory_cli(tmp_path):
    gt = tmp_path / 'ground_truth.csv'
    est = tmp_path / 'estimated.csv'
    output = tmp_path / 'report.json'
    write_trajectory(gt, offset=0.0)
    write_trajectory(est, offset=0.1)

    result = subprocess.run(
        [
            sys.executable,
            'evaluate_trajectory.py',
            '--ground-truth',
            str(gt),
            '--estimated',
            str(est),
            '--output',
            str(output),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert 'Matched poses' in result.stdout
    report = json.loads(output.read_text())
    assert report['matched_poses'] == 2
    assert report['absolute_trajectory_error'] > 0.0
