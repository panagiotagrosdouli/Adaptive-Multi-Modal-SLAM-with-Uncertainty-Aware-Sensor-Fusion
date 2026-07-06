from src.diagnostics import (
    DiagnosticEvent,
    DiagnosticsLogger,
    load_diagnostic_events,
    summarize_diagnostics,
)


def test_diagnostics_logger_roundtrip(tmp_path):
    log_file = tmp_path / 'diagnostics.jsonl'
    logger = DiagnosticsLogger(log_file)
    event = DiagnosticEvent(
        step=1,
        timestamp=1.0,
        state='recovery',
        health_level='critical',
        health_score=0.2,
        recovery_action='emergency_relocalization',
        reason='tracking health is critically degraded',
    )

    logger.write_event(event)
    events = load_diagnostic_events(log_file)

    assert len(events) == 1
    assert events[0].state == 'recovery'
    assert events[0].health_level == 'critical'


def test_summarize_diagnostics_counts_events():
    events = [
        DiagnosticEvent(0, 0.0, 'normal', 'healthy', 0.9, 'continue_normal_operation', 'ok'),
        DiagnosticEvent(1, 1.0, 'adaptive', 'warning', 0.4, 'increase_inertial_weight', 'degraded'),
        DiagnosticEvent(2, 2.0, 'recovery', 'critical', 0.1, 'emergency_relocalization', 'bad'),
    ]

    summary = summarize_diagnostics(events)

    assert summary['num_events'] == 3
    assert summary['num_warnings'] == 1
    assert summary['num_critical'] == 1
    assert summary['num_recovery_actions'] == 1


def test_summarize_diagnostics_handles_empty_input():
    summary = summarize_diagnostics([])
    assert summary['num_events'] == 0
    assert summary['num_recovery_actions'] == 0
