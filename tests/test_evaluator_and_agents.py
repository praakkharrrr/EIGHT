import pytest
from src.gemma_client import GemmaClient
from src.agents import AgentRunner
from src.evaluator import EvaluatorRunner
from src.benchmark import BenchmarkManager
from src.verification import VerificationEngine
from src.metrics import MetricsCalculator

def test_mock_mode_execution_pipeline():
    """Verify end-to-end execution of baseline, agents, evaluator, verification in mock mode."""
    client = GemmaClient(force_mock=True)
    assert client.is_mock_mode is True

    manager = BenchmarkManager()
    task = manager.get_task("TASK-01")
    assert task is not None

    runner = AgentRunner(client)
    baseline_out = runner.run_baseline(task)
    agent_a_out = runner.run_agent_a(task)
    agent_b_out = runner.run_agent_b(task)

    assert baseline_out.is_mock is True
    assert baseline_out.parsed_code is not None
    assert agent_a_out.parsed_code is not None
    assert agent_b_out.parsed_code is not None

    evaluator = EvaluatorRunner(client)
    eval_decision = evaluator.evaluate_candidates(task, agent_a_out, agent_b_out)

    assert eval_decision.is_mock is True
    assert eval_decision.selected_agent in ("Agent A", "Agent B", "Abstain")
    assert len(eval_decision.rationale) > 0

    # Run independent verifications
    v_base = VerificationEngine.verify_candidate(task, baseline_out, "Baseline")
    v_a = VerificationEngine.verify_candidate(task, agent_a_out, "Agent A")
    v_b = VerificationEngine.verify_candidate(task, agent_b_out, "Agent B")

    # In TASK-01 mock: baseline used set() which loses order -> should fail test 1
    assert v_base.all_passed is False
    # Agent A used dict.fromkeys or Agent B used set+list -> both preserve order
    assert v_a.all_passed is True
    assert v_b.all_passed is True

    # Check metrics calculation
    res = MetricsCalculator.evaluate_task_result(
        task=task,
        baseline_output=baseline_out,
        agent_a_output=agent_a_out,
        agent_b_output=agent_b_out,
        evaluator_decision=eval_decision,
        baseline_verification=v_base,
        agent_a_verification=v_a,
        agent_b_verification=v_b
    )

    assert res.collaboration_outcome == "Helped"
    assert res.is_mock is True

def test_evaluator_malformed_json_resilience():
    client = GemmaClient(force_mock=True)
    evaluator = EvaluatorRunner(client)

    # Test JSON parser with messy markdown or text
    valid_with_markdown = "Here is my evaluation:\n```json\n{\"selected_agent\": \"Agent A\", \"rationale\": \"Good\", \"confidence_score\": 0.8}\n```"
    data, err = evaluator._parse_json_response(valid_with_markdown)
    assert err is None
    assert data["selected_agent"] == "Agent A"

    # Malformed text
    bad_text = "This is not valid json at all {"
    data2, err2 = evaluator._parse_json_response(bad_text)
    assert err2 is not None
    assert data2 is None
