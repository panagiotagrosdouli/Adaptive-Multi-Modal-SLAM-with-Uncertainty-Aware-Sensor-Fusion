import json

from src.visualization import generate_all_plots, load_experiment_steps


def test_load_experiment_steps(tmp_path):
    experiment_file = tmp_path / "experiment.json"
    experiment_file.write_text(json.dumps({"steps": [{"step": 0}]}))
    steps = load_experiment_steps(experiment_file)
    assert steps == [{"step": 0}]


def test_generate_all_plots(tmp_path):
    experiment_file = tmp_path / "experiment.json"
    experiment_file.write_text(
        json.dumps(
            {
                "steps": [
                    {
                        "step": 0,
                        "failure_probability": 0.1,
                        "visual_reliability": 0.8,
                        "inertial_reliability": 0.9,
                        "visual_weight": 0.45,
                        "inertial_weight": 0.55,
                    },
                    {
                        "step": 1,
                        "failure_probability": 0.2,
                        "visual_reliability": 0.7,
                        "inertial_reliability": 0.85,
                        "visual_weight": 0.43,
                        "inertial_weight": 0.57,
                    },
                ]
            }
        )
    )

    output_dir = tmp_path / "plots"
    generate_all_plots(experiment_file, output_dir)

    assert (output_dir / "failure_probability.png").exists()
    assert (output_dir / "reliability.png").exists()
    assert (output_dir / "fusion_weights.png").exists()
