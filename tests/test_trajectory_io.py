from src.trajectory import TrajectoryPose, load_euroc_ground_truth, save_tum_trajectory


def test_load_euroc_ground_truth(tmp_path):
    trajectory_file = tmp_path / 'gt.csv'
    trajectory_file.write_text(
        '#timestamp,p_RS_R_x,p_RS_R_y,p_RS_R_z,q_RS_w,q_RS_x,q_RS_y,q_RS_z\n'
        '100,1.0,2.0,3.0,1.0,0.0,0.0,0.0\n'
    )

    poses = load_euroc_ground_truth(trajectory_file)

    assert len(poses) == 1
    assert poses[0].timestamp_ns == 100
    assert poses[0].tx == 1.0
    assert poses[0].qw == 1.0


def test_save_tum_trajectory(tmp_path):
    output_file = tmp_path / 'trajectory.txt'
    poses = [
        TrajectoryPose(
            timestamp_ns=1_000_000_000,
            tx=1.0,
            ty=2.0,
            tz=3.0,
            qx=0.0,
            qy=0.0,
            qz=0.0,
            qw=1.0,
        )
    ]

    save_tum_trajectory(poses, output_file)

    text = output_file.read_text().strip()
    assert text == '1.000000000 1.000000000 2.000000000 3.000000000 0.000000000 0.000000000 0.000000000 1.000000000'
