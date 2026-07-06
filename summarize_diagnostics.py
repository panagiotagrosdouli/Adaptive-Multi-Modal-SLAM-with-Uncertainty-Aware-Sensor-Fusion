import argparse
import json
from pathlib import Path

from src.diagnostics import load_diagnostic_events, summarize_diagnostics


def parse_args():
    parser = argparse.ArgumentParser(description='Summarize self-healing SLAM diagnostics logs.')
    parser.add_argument('diagnostics_log', help='Path to diagnostics JSONL log.')
    parser.add_argument(
        '--output',
        default='results/diagnostics_summary.json',
        help='Path to output diagnostics summary JSON.',
    )
    return parser.parse_args()


def main():
    args = parse_args()
    events = load_diagnostic_events(args.diagnostics_log)
    summary = summarize_diagnostics(events)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2), encoding='utf-8')

    print(json.dumps(summary, indent=2))
    print(f'Diagnostics summary written to: {output_path}')


if __name__ == '__main__':
    main()
