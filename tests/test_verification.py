import pytest
from src.schemas import BenchmarkTask, TestCaseDefinition, AgentOutput
from src.verification import VerificationEngine

@pytest.fixture
def sample_task():
    return BenchmarkTask(
        task_id="TEST-01",
        title="Add Two Numbers",
        category="numeric",
        difficulty="Easy",
        description="Write a function add(a, b) that returns the sum of a and b.",
        input_spec="Two numbers a and b.",
        output_spec="Sum of a and b.",
        expected_trap="Overlooking float precision or negative numbers.",
        test_cases=[
            TestCaseDefinition(name="positive", input_args={"a": 2, "b": 3}, expected_output=5),
            TestCaseDefinition(name="negative", input_args={"a": -1, "b": -4}, expected_output=-5, is_edge_case=True),
            TestCaseDefinition(name="zero", input_args={"a": 0, "b": 7}, expected_output=7),
        ]
    )

def test_verification_valid_code(sample_task):
    code = "def add(a, b):\n    return a + b\n"
    output = AgentOutput(
        agent_id="test_agent",
        strategy_name="Direct",
        prompt_used="",
        raw_response=code,
        parsed_code=code
    )
    result = VerificationEngine.verify_candidate(sample_task, output, "Test Agent")
    assert result.all_passed is True
    assert result.pass_count == 3
    assert result.total_count == 3
    assert result.pass_rate == 1.0
    assert result.execution_error is None

def test_verification_failing_code(sample_task):
    # Buggy implementation that fails on negative numbers
    code = "def add(a, b):\n    return a * b if a < 0 else a + b\n"
    output = AgentOutput(
        agent_id="buggy_agent",
        strategy_name="Faulty",
        prompt_used="",
        raw_response=code,
        parsed_code=code
    )
    result = VerificationEngine.verify_candidate(sample_task, output, "Buggy Agent")
    assert result.all_passed is False
    assert result.pass_count == 2
    assert result.total_count == 3
    assert round(result.pass_rate, 2) == 0.67
    assert result.test_results[1].passed is False

def test_verification_syntax_error(sample_task):
    code = "def add(a, b)\n    return a + b\n" # Missing colon
    output = AgentOutput(
        agent_id="syntax_agent",
        strategy_name="Broken",
        prompt_used="",
        raw_response=code,
        parsed_code=code
    )
    result = VerificationEngine.verify_candidate(sample_task, output, "Broken Agent")
    assert result.all_passed is False
    assert result.pass_count == 0
    assert "SyntaxError" in (result.execution_error or "")

def test_verification_security_block(sample_task):
    # Prohibited import: os
    code = "import os\ndef add(a, b):\n    return a + b\n"
    output = AgentOutput(
        agent_id="malicious_agent",
        strategy_name="Attack",
        prompt_used="",
        raw_response=code,
        parsed_code=code
    )
    result = VerificationEngine.verify_candidate(sample_task, output, "Malicious Agent")
    assert result.all_passed is False
    assert result.pass_count == 0
    assert "Security violation" in (result.execution_error or "")

def test_verification_prohibited_call(sample_task):
    code = "def add(a, b):\n    eval('2+2')\n    return a + b\n"
    output = AgentOutput(
        agent_id="eval_agent",
        strategy_name="Prohibited Call",
        prompt_used="",
        raw_response=code,
        parsed_code=code
    )
    result = VerificationEngine.verify_candidate(sample_task, output, "Eval Agent")
    assert result.all_passed is False
    assert result.pass_count == 0
    assert "Security violation" in (result.execution_error or "")

def test_verification_structured_answers(sample_task):
    output = AgentOutput(
        agent_id="structured_agent",
        strategy_name="Structured Answers",
        prompt_used="",
        raw_response="",
        parsed_answers=[5, -5, 7]
    )
    result = VerificationEngine.verify_candidate(sample_task, output, "Structured Agent")
    assert result.all_passed is True
    assert result.pass_count == 3
    assert result.pass_rate == 1.0

def test_verification_runtime_exception(sample_task):
    code = "def add(a, b):\n    raise RuntimeError('Crashing!')\n"
    output = AgentOutput(
        agent_id="crashing_agent",
        strategy_name="Crashing",
        prompt_used="",
        raw_response=code,
        parsed_code=code
    )
    result = VerificationEngine.verify_candidate(sample_task, output, "Crashing Agent")
    assert result.all_passed is False
    assert result.pass_count == 0
    assert result.test_results[0].passed is False
    assert "RuntimeError" in (result.test_results[0].error_message or "")
