import argparse
import subprocess
import sys

from src.benchmark_plan import load_benchmark_plan


def parse_args():
    parser = argparse.ArgumentParser(description='Inspect or execute a benchmark plan.')
    parser.add_argument('--plan', default='configs/benchmark_plan.yaml')
    parser.add_argument('--execute', action='store_true', help='Execute enabled safe runs.')
    return parser.parse_args()


def command_for_run(run):
    if run.kind == 'dummy':
        return [sys.executable, 'run_experiment.py', '--config', run.config]
    if run.kind == 'orbslam3':
        return [sys.executable, 'run_orbslam3_experiment.py', '--config', run.config]
    if run.kind == 'degradation':
        return [sys.executable, 'apply_degradation.py', '--help']
    if run.kind == 'self_healing':
        return [sys.executable, '-m', 'pytest', 'tests/test_self_healing_core.py', '-q']
    raise ValueError(f'Unknown benchmark run kind: {run.kind}')


def main():
    args = parse_args()
    plan = load_benchmark_plan(args.plan)

    print(f'Benchmark plan: {plan.name}')
    for run in plan.enabled_runs:
        command = command_for_run(run)
        print(f'- {run.name} [{run.kind}]: ' + ' '.join(command))
        if args.execute:
            subprocess.run(command, check=True)


if __name__ == '__main__':
    main()
