import json

from src.result_aggregation import aggregate_reports, load_evaluation_report, summaries_to_markdown


def test_load_evaluation_report(tmp_path):
    report = tmp_path / 'report.json'
    report.write_text(
        json.dumps(
            {
                'experiment_name': 'baseline_clean',
                'matched_poses': 100,
                'absolute_trajectory_error': 0.12,
                'relative_pose_error': 0.03,
            }
        )
    )

    summary = load_evaluation_report(report)

    assert summary.experiment_name == 'baseline_clean'
    assert summary.matched_poses == 100
    assert summary.absolute_trajectory_error == 0.12
    assert summary.relative_pose_error == 0.03


def test_aggregate_reports(tmp_path):
    first = tmp_path / 'first.json'
    second = tmp_path / 'second.json'
    first.write_text(json.dumps({'experiment_name': 'a', 'matched_poses': 1, 'absolute_trajectory_error': 0.1, 'relative_pose_error': 0.2}))
    second.write_text(json.dumps({'experiment_name': 'b', 'matched_poses': 2, 'absolute_trajectory_error': 0.3, 'relative_pose_error': 0.4}))

    summaries = aggregate_reports([first, second])

    assert len(summaries) == 2
    assert summaries[0].experiment_name == 'a'
    assert summaries[1].experiment_name == 'b'


def test_summaries_to_markdown(tmp_path):
    report = tmp_path / 'report.json'
    report.write_text(json.dumps({'experiment_name': 'baseline_clean', 'matched_poses': 100, 'absolute_trajectory_error': 0.12, 'relative_pose_error': 0.03}))
    summaries = aggregate_reports([report])

    table = summaries_to_markdown(summaries)

    assert '| Experiment | Matched Poses | ATE | RPE |' in table
    assert '| baseline_clean | 100 | 0.120000 | 0.030000 |' in table
