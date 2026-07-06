import argparse
import json
from pathlib import Path

from src.evaluation import evaluate_trajectory
from src.trajectory import load_euroc_ground_truth


def parse_args():
    parser = argparse.ArgumentParser(description='Evaluate estimated trajectory against EuRoC ground truth.')
    parser.add_argument('--ground-truth', required=True, help='Path to EuRoC ground-truth CSV.')
    parser.add_argument('--estimated', required=True, help='Path to estimated trajectory CSV in EuRoC-style format.')
    parser.add_argument(
        '--output',
        default='results/trajectory_evaluation.json',
        help='Path to output JSON evaluation report.',
    )
    parser.add_argument(
        '--max-time-difference-ns',
        type=int,
        default=10_000_000,
        help='Maximum timestamp difference allowed for matching poses.',
    )
    return parser.parse_args()


def main():
    args = parse_args()
    ground_truth = load_euroc_ground_truth(args.ground_truth)
    estimated = load_euroc_ground_truth(args.estimated)
    evaluation = evaluate_trajectory(
        ground_truth,
        estimated,
        max_time_difference_ns=args.max_time_difference_ns,
    )

    report = {
        'matched_poses': evaluation.matched_poses,
        'absolute_trajectory_error': evaluation.ate,
        'relative_pose_error': evaluation.rpe,
        'ground_truth': args.ground_truth,
        'estimated': args.estimated,
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding='utf-8')

    print(f"Matched poses: {evaluation.matched_poses}")
    print(f"ATE: {evaluation.ate}")
    print(f"RPE: {evaluation.rpe}")
    print(f"Report written to: {output_path}")


if __name__ == '__main__':
    main()
