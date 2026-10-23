import pytest
from src.schemas import (
    BenchmarkTask,
    TestCaseDefinition,
    AgentOutput,
    EvaluatorDecision,
    CandidateVerification,
    TestCaseResult
)
from src.metrics import MetricsCalculator

@pytest.fixture
def mock_task():
    return BenchmarkTask(
        task_id="TASK-MOCK",
        title="Mock Task",
        category="mock",
        difficulty="Easy",
        description="Task for metric tests",
        input_spec="x",
        output_spec="x",
        expected_trap="None",
        test_cases=[
            TestCaseDefinition(name="tc1", input_args={"x": 1}, expected_output=1),
            TestCaseDefinition(name="tc2", input_args={"x": 2}, expected_output=2),
        ]
    )

def make_verification(all_passed: bool, candidate_id: str = "test"):
    count = 2 if all_passed else 1
    return CandidateVerification(
        candidate_id=candidate_id,
        candidate_label=candidate_id,
        all_passed=all_passed,
        pass_count=count,
        total_count=2,
        pass_rate=count / 2,
        test_results=[
            TestCaseResult(test_name="tc1", input_repr="{}", expected_repr="1", actual_repr="1", passed=True),
            TestCaseResult(test_name="tc2", input_repr="{}", expected_repr="2", actual_repr="2" if all_passed else "0", passed=all_passed)
        ]
    )

def test_collaboration_helped(mock_task):
    baseline_output = AgentOutput(agent_id="baseline", strategy_name="Direct", prompt_used="", raw_response="")
    agent_a_output = AgentOutput(agent_id="agent_a", strategy_name="A", prompt_used="", raw_response="")
    agent_b_output = AgentOutput(agent_id="agent_b", strategy_name="B", prompt_used="", raw_response="")
    evaluator_decision = EvaluatorDecision(
        selected_agent="Agent B",
        rationale="Agent B handled edge cases",
        identified_disagreements=["order"],
        confidence_score=0.9
    )

    baseline_verif = make_verification(all_passed=False, candidate_id="baseline")
    agent_a_verif = make_verification(all_passed=False, candidate_id="agent_a")
    agent_b_verif = make_verification(all_passed=True, candidate_id="agent_b")

    result = MetricsCalculator.evaluate_task_result(
        task=mock_task,
        baseline_output=baseline_output,
        agent_a_output=agent_a_output,
        agent_b_output=agent_b_output,
        evaluator_decision=evaluator_decision,
        baseline_verification=baseline_verif,
        agent_a_verification=agent_a_verif,
        agent_b_verification=agent_b_verif
    )

    assert result.collaboration_outcome == "Helped"
    assert result.evaluator_error_flag is False
    assert result.multi_agent_verification.all_passed is True

def test_collaboration_hurt(mock_task):
    baseline_output = AgentOutput(agent_id="baseline", strategy_name="Direct", prompt_used="", raw_response="")
    agent_a_output = AgentOutput(agent_id="agent_a", strategy_name="A", prompt_used="", raw_response="")
    agent_b_output = AgentOutput(agent_id="agent_b", strategy_name="B", prompt_used="", raw_response="")
    evaluator_decision = EvaluatorDecision(
        selected_agent="Agent A",
        rationale="Agent A seemed simpler",
        identified_disagreements=[],
        confidence_score=0.7
    )

    baseline_verif = make_verification(all_passed=True, candidate_id="baseline")
    agent_a_verif = make_verification(all_passed=False, candidate_id="agent_a")
    agent_b_verif = make_verification(all_passed=True, candidate_id="agent_b")

    result = MetricsCalculator.evaluate_task_result(
        task=mock_task,
        baseline_output=baseline_output,
        agent_a_output=agent_a_output,
        agent_b_output=agent_b_output,
        evaluator_decision=evaluator_decision,
        baseline_verification=baseline_verif,
        agent_a_verification=agent_a_verif,
        agent_b_verification=agent_b_verif
    )

    assert result.collaboration_outcome == "Hurt"
    # Evaluator picked Agent A (which failed) when Agent B passed!
    assert result.evaluator_error_flag is True
    assert result.multi_agent_verification.all_passed is False

def test_aggregate_benchmark_runs(mock_task):
    # Create two results: one where collaboration helped, one where both passed (no effect)
    dummy_out = AgentOutput(agent_id="test", strategy_name="test", prompt_used="", raw_response="", latency_seconds=0.1, tokens_used=50)
    eval_dec = EvaluatorDecision(selected_agent="Agent A", rationale="ok", confidence_score=0.9, latency_seconds=0.1, tokens_used=50)

    # Result 1: Helped
    r1 = MetricsCalculator.evaluate_task_result(
        task=mock_task,
        baseline_output=dummy_out,
        agent_a_output=dummy_out,
        agent_b_output=dummy_out,
        evaluator_decision=eval_dec,
        baseline_verification=make_verification(False),
        agent_a_verification=make_verification(True),
        agent_b_verification=make_verification(False)
    )

    # Result 2: No effect (both passed)
    r2 = MetricsCalculator.evaluate_task_result(
        task=mock_task,
        baseline_output=dummy_out,
        agent_a_output=dummy_out,
        agent_b_output=dummy_out,
        evaluator_decision=eval_dec,
        baseline_verification=make_verification(True),
        agent_a_verification=make_verification(True),
        agent_b_verification=make_verification(True)
    )

    summary = MetricsCalculator.aggregate_benchmark_runs([r1, r2])
    assert summary.total_tasks_attempted == 2
    assert summary.baseline_pass_count == 1
    assert summary.multi_agent_pass_count == 2
    assert summary.baseline_pass_rate == 0.5
    assert summary.multi_agent_pass_rate == 1.0
    assert summary.pass_rate_delta == 0.5
    assert summary.collaboration_helped_count == 1
    assert summary.collaboration_no_effect_count == 1
    assert summary.collaboration_hurt_count == 0
