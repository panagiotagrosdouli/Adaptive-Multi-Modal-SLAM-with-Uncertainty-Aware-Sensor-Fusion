import argparse
from pathlib import Path

from src.result_aggregation import aggregate_reports, summaries_to_markdown


def parse_args():
    parser = argparse.ArgumentParser(description='Aggregate trajectory evaluation reports into a markdown table.')
    parser.add_argument('reports', nargs='+', help='Evaluation JSON reports to aggregate.')
    parser.add_argument(
        '--output',
        default='results/summary_table.md',
        help='Output markdown table path.',
    )
    return parser.parse_args()


def main():
    args = parse_args()
    summaries = aggregate_reports(args.reports)
    table = summaries_to_markdown(summaries)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(table, encoding='utf-8')

    print(table)
    print(f'Summary table written to: {output_path}')


if __name__ == '__main__':
    main()
