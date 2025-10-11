from src.utils.workers import compute_worker_count


def test_compute_worker_count_zero_tasks():
    assert compute_worker_count(0, configured_limit=4, cpu_count=8) == 0


def test_compute_worker_count_respects_limits():
    assert compute_worker_count(5, configured_limit=2, cpu_count=8) == 2
    assert compute_worker_count(1, configured_limit=0, cpu_count=8) == 1
    assert compute_worker_count(10, configured_limit=None, cpu_count=3) == 3


def test_compute_worker_count_handles_negative_limit():
    assert compute_worker_count(3, configured_limit=-5, cpu_count=4) == 1
