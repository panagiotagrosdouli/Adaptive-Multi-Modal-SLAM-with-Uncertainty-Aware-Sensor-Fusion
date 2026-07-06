import argparse
from pathlib import Path

from src.paper_artifacts import write_csv_results_table, write_markdown_results_table
from src.result_aggregation import aggregate_reports


def parse_args():
    parser = argparse.ArgumentParser(description='Generate paper-ready artifacts from evaluation reports.')
    parser.add_argument('reports', nargs='+', help='Evaluation JSON reports.')
    parser.add_argument('--output-dir', default='paper/generated')
    return parser.parse_args()


def main():
    args = parse_args()
    summaries = aggregate_reports(args.reports)
    output_dir = Path(args.output_dir)
    write_markdown_results_table(summaries, output_dir / 'results_table.md')
    write_csv_results_table(summaries, output_dir / 'results_table.csv')
    print(f'Paper artifacts written to: {output_dir}')


if __name__ == '__main__':
    main()
