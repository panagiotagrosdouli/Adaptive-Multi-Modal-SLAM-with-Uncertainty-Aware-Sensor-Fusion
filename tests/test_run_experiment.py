import json
import subprocess
import sys
from pathlib import Path


def test_run_experiment_smoke(tmp_path):
    result = subprocess.run(
        [sys.executable, 'run_experiment.py', '--config', 'configs/example_experiment.yaml'],
        check=True,
        capture_output=True,
        text=True,
    )

    assert 'Experiment completed' in result.stdout

    output_file = Path('results/euroc_degraded_adaptive_fusion_baseline.json')
    assert output_file.exists()

    data = json.loads(output_file.read_text())
    assert 'steps' in data
    assert len(data['steps']) == 20

    plot_dir = Path('results/plots/euroc_degraded_adaptive_fusion_baseline')
    assert (plot_dir / 'failure_probability.png').exists()
    assert (plot_dir / 'reliability.png').exists()
    assert (plot_dir / 'fusion_weights.png').exists()

    manifest_file = Path('results/manifests/euroc_degraded_adaptive_fusion_baseline_manifest.json')
    assert manifest_file.exists()
    manifest = json.loads(manifest_file.read_text())
    assert manifest['experiment_name'] == 'euroc_degraded_adaptive_fusion_baseline'
    assert manifest['config_path'] == 'configs/example_experiment.yaml'
    assert str(output_file) in manifest['outputs']
