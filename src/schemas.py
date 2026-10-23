from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field

class TestCaseDefinition(BaseModel):
    """Definition of a single deterministic test case."""
    __test__ = False
    name: str
    input_args: Dict[str, Any] = Field(default_factory=dict)
    expected_output: Any
    is_edge_case: bool = False
    description: str = ""

class BenchmarkTask(BaseModel):
    """Specification of a benchmark task in EIGHT."""
    task_id: str
    title: str
    category: str
    difficulty: Literal["Easy", "Medium", "Hard"]
    description: str
    input_spec: str
    output_spec: str
    expected_trap: str
    test_cases: List[TestCaseDefinition]

class AgentOutput(BaseModel):
    """Output from an agent attempt (Baseline, Agent A, or Agent B)."""
    agent_id: str
    strategy_name: str
    prompt_used: str
    raw_response: str
    parsed_code: Optional[str] = None
    parsed_answers: Optional[List[Any]] = None
    explanation: str = ""
    latency_seconds: float = 0.0
    tokens_used: int = 0
    error: Optional[str] = None
    is_mock: bool = False

class EvaluatorDecision(BaseModel):
    """Structured decision returned by the Gemma 4 Evaluator."""
    selected_agent: Literal["Agent A", "Agent B", "Abstain"]
    rationale: str
    identified_disagreements: List[str] = Field(default_factory=list)
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    potential_failure_modes: List[str] = Field(default_factory=list)
    raw_response: str = ""
    latency_seconds: float = 0.0
    tokens_used: int = 0
    error: Optional[str] = None
    is_mock: bool = False

class TestCaseResult(BaseModel):
    """Outcome of running one test case against a candidate."""
    __test__ = False
    test_name: str
    input_repr: str
    expected_repr: str
    actual_repr: str
    passed: bool
    is_edge_case: bool = False
    error_message: Optional[str] = None

class CandidateVerification(BaseModel):
    """Independent verification outcomes for one candidate."""
    candidate_id: str
    candidate_label: str
    all_passed: bool
    pass_count: int
    total_count: int
    pass_rate: float
    test_results: List[TestCaseResult] = Field(default_factory=list)
    execution_error: Optional[str] = None

class TaskEvaluationResult(BaseModel):
    """Comprehensive evaluation record combining baseline, agents, evaluator, and verification."""
    task: BenchmarkTask
    baseline_output: AgentOutput
    agent_a_output: AgentOutput
    agent_b_output: AgentOutput
    evaluator_decision: EvaluatorDecision
    
    # Independent verification
    baseline_verification: CandidateVerification
    agent_a_verification: CandidateVerification
    agent_b_verification: CandidateVerification
    multi_agent_verification: CandidateVerification  # Verification of evaluator's chosen output
    
    # Meta analytics
    collaboration_outcome: Literal["Helped", "No Effect", "Hurt", "Indeterminate"]
    evaluator_error_flag: bool = False  # Evaluator picked a failing candidate or failed while a pass existed
    agent_disagreement: bool = False
    total_latency_seconds: float = 0.0
    api_calls_count: int = 0
    total_tokens_used: int = 0
    is_mock: bool = False
    failure_hypothesis: Optional[str] = None

class BenchmarkRunSummary(BaseModel):
    """Summary of metrics across multiple evaluated tasks."""
    total_tasks_attempted: int = 0
    total_tasks_completed: int = 0
    baseline_pass_count: int = 0
    multi_agent_pass_count: int = 0
    baseline_pass_rate: float = 0.0
    multi_agent_pass_rate: float = 0.0
    pass_rate_delta: float = 0.0
    collaboration_helped_count: int = 0
    collaboration_no_effect_count: int = 0
    collaboration_hurt_count: int = 0
    evaluator_error_count: int = 0
    agent_disagreement_count: int = 0
    avg_baseline_latency: float = 0.0
    avg_multi_agent_latency: float = 0.0
    total_api_calls: int = 0
    total_tokens: int = 0
    task_results: List[TaskEvaluationResult] = Field(default_factory=list)
