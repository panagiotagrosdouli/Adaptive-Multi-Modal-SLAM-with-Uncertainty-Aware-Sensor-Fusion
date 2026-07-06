import argparse
import json
from pathlib import Path

from src.analysis import compare_experiments
from src.result_aggregation import load_evaluation_report


def parse_args():
    parser = argparse.ArgumentParser(description='Compare two trajectory evaluation reports.')
    parser.add_argument('--baseline', required=True, help='Baseline evaluation JSON report.')
    parser.add_argument('--candidate', required=True, help='Candidate evaluation JSON report.')
    parser.add_argument(
        '--output',
        default='results/improvement_report.json',
        help='Path to output improvement report.',
    )
    return parser.parse_args()


def main():
    args = parse_args()
    baseline = load_evaluation_report(args.baseline)
    candidate = load_evaluation_report(args.candidate)
    comparison = compare_experiments(baseline, candidate)

    report = {
        'baseline_name': comparison.baseline_name,
        'candidate_name': comparison.candidate_name,
        'ate_improvement_percent': comparison.ate_improvement_percent,
        'rpe_improvement_percent': comparison.rpe_improvement_percent,
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding='utf-8')

    print(json.dumps(report, indent=2))
    print(f'Improvement report written to: {output_path}')


if __name__ == '__main__':
    main()
