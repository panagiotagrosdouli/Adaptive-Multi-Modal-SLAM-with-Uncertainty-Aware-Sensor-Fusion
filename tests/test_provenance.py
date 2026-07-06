from src.provenance import ExperimentManifest, create_manifest, load_manifest, save_manifest


def test_create_manifest_contains_required_fields():
    manifest = create_manifest(
        experiment_name='test_experiment',
        config_path='configs/test.yaml',
        outputs=['results/test.json'],
    )

    assert manifest.experiment_name == 'test_experiment'
    assert manifest.config_path == 'configs/test.yaml'
    assert manifest.outputs == ['results/test.json']
    assert manifest.created_utc


def test_manifest_roundtrip(tmp_path):
    manifest = ExperimentManifest(
        experiment_name='roundtrip',
        config_path='configs/test.yaml',
        created_utc='2026-01-01T00:00:00+00:00',
        git_commit='abc123',
        outputs=['results/a.json'],
        metadata={'dataset': 'EuRoC'},
    )
    output = tmp_path / 'manifest.json'

    save_manifest(manifest, output)
    loaded = load_manifest(output)

    assert loaded.experiment_name == 'roundtrip'
    assert loaded.git_commit == 'abc123'
    assert loaded.metadata['dataset'] == 'EuRoC'
