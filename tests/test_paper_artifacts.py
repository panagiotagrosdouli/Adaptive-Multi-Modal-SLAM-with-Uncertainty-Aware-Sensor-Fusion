from src.paper_artifacts import write_csv_results_table, write_markdown_results_table
from src.result_aggregation import ExperimentSummary


def test_write_markdown_results_table(tmp_path):
    output = tmp_path / 'table.md'
    summaries = [ExperimentSummary('run_a', 10, 0.1, 0.2)]

    write_markdown_results_table(summaries, output)

    text = output.read_text()
    assert 'Experiment' in text
    assert 'run_a' in text
    assert '0.100000' in text


def test_write_csv_results_table(tmp_path):
    output = tmp_path / 'table.csv'
    summaries = [ExperimentSummary('run_a', 10, 0.1, 0.2)]

    write_csv_results_table(summaries, output)

    text = output.read_text()
    assert 'experiment_name' in text
    assert 'run_a,10,0.100000,0.200000' in text
