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
