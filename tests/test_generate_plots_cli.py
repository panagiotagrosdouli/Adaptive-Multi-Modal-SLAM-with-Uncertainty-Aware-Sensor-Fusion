import json
import subprocess
import sys


def test_generate_plots_cli(tmp_path):
    experiment_file = tmp_path / 'experiment.json'
    output_dir = tmp_path / 'plots'

    experiment_file.write_text(
        json.dumps(
            {
                'steps': [
                    {
                        'step': 0,
                        'failure_probability': 0.1,
                        'visual_reliability': 0.8,
                        'inertial_reliability': 0.9,
                        'visual_weight': 0.45,
                        'inertial_weight': 0.55,
                    },
                    {
                        'step': 1,
                        'failure_probability': 0.2,
                        'visual_reliability': 0.7,
                        'inertial_reliability': 0.85,
                        'visual_weight': 0.43,
                        'inertial_weight': 0.57,
                    },
                ]
            }
        )
    )

    result = subprocess.run(
        [
            sys.executable,
            'generate_plots.py',
            str(experiment_file),
            '--output-dir',
            str(output_dir),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert 'Plots written to' in result.stdout
    assert (output_dir / 'failure_probability.png').exists()
    assert (output_dir / 'reliability.png').exists()
    assert (output_dir / 'fusion_weights.png').exists()
