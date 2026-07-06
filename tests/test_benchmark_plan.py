from src.benchmark_plan import load_benchmark_plan


def test_load_benchmark_plan(tmp_path):
    plan_file = tmp_path / 'plan.yaml'
    plan_file.write_text(
        'name: test_plan\n'
        'runs:\n'
        '  - name: first\n'
        '    kind: dummy\n'
        '    config: configs/example.yaml\n'
        '    enabled: true\n'
        '  - name: second\n'
        '    kind: orbslam3\n'
        '    config: configs/orbslam3.yaml\n'
        '    enabled: false\n'
    )

    plan = load_benchmark_plan(plan_file)

    assert plan.name == 'test_plan'
    assert len(plan.runs) == 2
    assert len(plan.enabled_runs) == 1
    assert plan.enabled_runs[0].name == 'first'
