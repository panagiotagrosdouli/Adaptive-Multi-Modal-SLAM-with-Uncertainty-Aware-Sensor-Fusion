import json
from pathlib import Path
from typing import List

import matplotlib.pyplot as plt


def load_experiment_steps(path: str | Path) -> List[dict]:
    path = Path(path)
    with path.open('r', encoding='utf-8') as file:
        data = json.load(file)
    return data.get('steps', [])


def _plot_series(steps, keys, title, ylabel, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    x = [step['step'] for step in steps]

    plt.figure(figsize=(7, 4))
    for key in keys:
        y = [step[key] for step in steps]
        plt.plot(x, y, label=key)
    plt.xlabel('Step')
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def plot_failure_probability(steps, output_path='results/plots/failure_probability.png'):
    _plot_series(
        steps,
        ['failure_probability'],
        'Predicted SLAM Failure Probability',
        'Probability',
        output_path,
    )


def plot_reliability(steps, output_path='results/plots/reliability.png'):
    _plot_series(
        steps,
        ['visual_reliability', 'inertial_reliability'],
        'Sensor Reliability Estimates',
        'Reliability',
        output_path,
    )


def plot_fusion_weights(steps, output_path='results/plots/fusion_weights.png'):
    _plot_series(
        steps,
        ['visual_weight', 'inertial_weight'],
        'Adaptive Fusion Weights',
        'Weight',
        output_path,
    )


def generate_all_plots(experiment_json: str | Path, output_dir='results/plots'):
    steps = load_experiment_steps(experiment_json)
    output_dir = Path(output_dir)
    plot_failure_probability(steps, output_dir / 'failure_probability.png')
    plot_reliability(steps, output_dir / 'reliability.png')
    plot_fusion_weights(steps, output_dir / 'fusion_weights.png')
