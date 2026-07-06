from run_benchmark_plan import command_for_run
from src.benchmark_plan import BenchmarkRun


def test_command_for_dummy_run():
    run = BenchmarkRun(name='dummy', kind='dummy', config='configs/example.yaml')
    command = command_for_run(run)
    assert command[1:] == ['run_experiment.py', '--config', 'configs/example.yaml']


def test_command_for_self_healing_run():
    run = BenchmarkRun(name='self_healing', kind='self_healing', config='configs/self_healing.yaml')
    command = command_for_run(run)
    assert 'pytest' in command
    assert 'tests/test_self_healing_core.py' in command
