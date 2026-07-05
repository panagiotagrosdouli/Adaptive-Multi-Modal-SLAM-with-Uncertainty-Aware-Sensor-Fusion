from src.dataset_loader import EurocDataset


def test_euroc_image_frame_parsing(tmp_path):
    image_dir = tmp_path / 'mav0' / 'cam0' / 'data'
    image_dir.mkdir(parents=True)
    image_path = image_dir / '1403636579763555584.png'
    image_path.write_bytes(b'')

    dataset = EurocDataset(tmp_path)
    frames = dataset.image_frames()

    assert len(frames) == 1
    assert frames[0].timestamp_ns == 1403636579763555584
    assert frames[0].path == image_path
    assert frames[0].timestamp_s > 0.0


def test_euroc_imu_parsing(tmp_path):
    imu_dir = tmp_path / 'mav0' / 'imu0'
    imu_dir.mkdir(parents=True)
    imu_csv = imu_dir / 'data.csv'
    imu_csv.write_text(
        '#timestamp [ns],w_RS_S_x [rad s^-1],w_RS_S_y [rad s^-1],w_RS_S_z [rad s^-1],a_RS_S_x [m s^-2],a_RS_S_y [m s^-2],a_RS_S_z [m s^-2]\n'
        '1403636579758555392,0.1,0.2,0.3,9.7,0.1,-0.2\n'
    )

    dataset = EurocDataset(tmp_path)
    measurements = dataset.imu_measurements()

    assert len(measurements) == 1
    assert measurements[0].timestamp_ns == 1403636579758555392
    assert measurements[0].gyro_x == 0.1
    assert measurements[0].accel_x == 9.7


def test_euroc_summary(tmp_path):
    image_dir = tmp_path / 'mav0' / 'cam0' / 'data'
    image_dir.mkdir(parents=True)
    (image_dir / '1403636579763555584.png').write_bytes(b'')

    dataset = EurocDataset(tmp_path)
    summary = dataset.summary()

    assert summary['num_cam0_images'] == 1
    assert summary['num_imu_measurements'] == 0
