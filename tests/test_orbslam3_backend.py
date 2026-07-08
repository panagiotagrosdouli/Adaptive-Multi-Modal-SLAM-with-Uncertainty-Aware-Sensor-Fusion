import pytest

from src.backends.orbslam3_backend import OrbSlam3Backend, OrbSlam3Config


def make_config(tmp_path):
    executable = tmp_path / 'orbslam3_euroc'
    vocabulary = tmp_path / 'ORBvoc.txt'
    settings = tmp_path / 'EuRoC.yaml'
    sequence_path = tmp_path / 'MH_01_easy'
    output_trajectory = tmp_path / 'results' / 'trajectory.csv'

    executable.write_text('#!/bin/sh\n')
    vocabulary.write_text('vocab')
    settings.write_text('settings')
    sequence_path.mkdir()

    return OrbSlam3Config(
        executable=executable,
        vocabulary=vocabulary,
        settings=settings,
        sequence_path=sequence_path,
        output_trajectory=output_trajectory,
    )


def test_orbslam3_command_construction(tmp_path):
    config = make_config(tmp_path)
    backend = OrbSlam3Backend(config)

    command = backend.build_command()

    assert command == [
        str(config.executable),
        str(config.vocabulary),
        str(config.settings),
        str(config.sequence_path),
        str(config.output_trajectory),
    ]


def test_orbslam3_path_validation_accepts_existing_paths(tmp_path):
    config = make_config(tmp_path)
    backend = OrbSlam3Backend(config)
    backend.initialize()


def test_orbslam3_path_validation_rejects_missing_executable(tmp_path):
    config = make_config(tmp_path)
    config.executable = tmp_path / 'missing_orbslam3'
    backend = OrbSlam3Backend(config)

    with pytest.raises(FileNotFoundError):
        backend.initialize()


def test_orbslam3_process_is_not_streaming_backend(tmp_path):
    config = make_config(tmp_path)
    backend = OrbSlam3Backend(config)

    with pytest.raises(NotImplementedError):
        backend.process(None)
