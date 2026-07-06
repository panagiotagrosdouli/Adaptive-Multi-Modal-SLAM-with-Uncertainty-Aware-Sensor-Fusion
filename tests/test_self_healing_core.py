from src.health_monitor import SlamHealthMonitor, SlamHealthSignals, SlamHealthStatus
from src.recovery_manager import RecoveryManager
from src.recovery_policy import RecoveryAction
from src.self_healing_state_machine import SelfHealingStateMachine


def make_signals(**overrides):
    values = {
        'tracking_ok': True,
        'tracked_features': 180,
        'mean_reprojection_error': 1.0,
        'visual_reliability': 0.9,
        'inertial_reliability': 0.9,
        'failure_probability': 0.05,
    }
    values.update(overrides)
    return SlamHealthSignals(**values)


def test_health_monitor_reports_healthy_for_good_tracking():
    monitor = SlamHealthMonitor()
    status = monitor.evaluate(make_signals())
    assert status.level == 'healthy'
    assert status.score > 0.55


def test_health_monitor_reports_critical_for_bad_tracking():
    monitor = SlamHealthMonitor()
    status = monitor.evaluate(
        make_signals(
            tracking_ok=False,
            tracked_features=5,
            mean_reprojection_error=10.0,
            visual_reliability=0.1,
            inertial_reliability=0.1,
            failure_probability=0.95,
        )
    )
    assert status.level == 'critical'


def test_state_machine_enters_recovery_on_critical_health():
    machine = SelfHealingStateMachine()
    transition = machine.update('critical', 'adaptive_sensor_reweighting')
    assert transition.previous_state == 'normal'
    assert transition.next_state == 'recovery'


def test_state_machine_enters_adaptive_on_warning_health():
    machine = SelfHealingStateMachine()
    transition = machine.update('warning', 'adaptive_sensor_reweighting')
    assert transition.next_state == 'adaptive'


def test_recovery_manager_overrides_policy_when_critical():
    manager = RecoveryManager()
    decision = manager.decide(
        SlamHealthStatus(score=0.1, level='critical', reason='bad tracking'),
        RecoveryAction(name='increase_inertial_weight', reason='vision unreliable'),
    )
    assert decision.action == 'emergency_relocalization'
    assert decision.priority == 3


def test_recovery_manager_uses_policy_when_warning():
    manager = RecoveryManager()
    decision = manager.decide(
        SlamHealthStatus(score=0.4, level='warning', reason='degraded tracking'),
        RecoveryAction(name='increase_inertial_weight', reason='vision unreliable'),
    )
    assert decision.action == 'increase_inertial_weight'
    assert decision.priority == 2
