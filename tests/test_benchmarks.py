import pytest
from src.benchmark import BenchmarkManager
from src.schemas import BenchmarkTask

def test_load_all_benchmark_tasks():
    manager = BenchmarkManager()
    tasks = manager.get_all_tasks()
    assert len(tasks) >= 8, f"Expected at least 8 benchmark tasks, found {len(tasks)}"
    
    for task in tasks:
        assert isinstance(task, BenchmarkTask)
        assert task.task_id.startswith("TASK-")
        assert len(task.title) > 0
        assert task.difficulty in ("Easy", "Medium", "Hard")
        assert len(task.test_cases) >= 3, f"Task {task.task_id} has fewer than 3 test cases"
        assert len(task.expected_trap) > 0

def test_task_retrieval_by_id():
    manager = BenchmarkManager()
    task = manager.get_task("TASK-01")
    assert task is not None
    assert task.title == "Stable Deduplication"
    assert task.category == "list_operations"

    non_existent = manager.get_task("TASK-999")
    assert non_existent is None

def test_reference_implementations_pass_all_benchmarks():
    """Verify that every reference implementation passes 100% of its own test cases."""
    manager = BenchmarkManager()
    tasks = manager.get_all_tasks()
    refs = manager.reference_implementations()

    for task in tasks:
        ref_func = refs.get(task.task_id)
        assert ref_func is not None, f"Missing reference implementation for {task.task_id}"

        for tc in task.test_cases:
            actual = ref_func(**tc.input_args)
            assert actual == tc.expected_output, (
                f"Task {task.task_id} failed on '{tc.name}': "
                f"expected {tc.expected_output!r}, got {actual!r}"
            )
