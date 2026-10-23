from typing import List, Dict, Any, Optional
from src.schemas import (
    BenchmarkTask,
    TaskEvaluationResult,
    CandidateVerification,
    BenchmarkRunSummary,
    AgentOutput,
    EvaluatorDecision
)

class MetricsCalculator:
    """Computes, aggregates, and analyzes reliability metrics across tasks."""

    @classmethod
    def evaluate_task_result(
        cls,
        task: BenchmarkTask,
        baseline_output: AgentOutput,
        agent_a_output: AgentOutput,
        agent_b_output: AgentOutput,
        evaluator_decision: EvaluatorDecision,
        baseline_verification: CandidateVerification,
        agent_a_verification: CandidateVerification,
        agent_b_verification: CandidateVerification
    ) -> TaskEvaluationResult:
        """
        Combines model outputs and independent verifications into a comprehensive TaskEvaluationResult.
        Determines collaboration outcome, evaluator error flags, and failure hypotheses.
        """
        # Determine Multi-Agent Verification outcome based on Evaluator selection
        selected = evaluator_decision.selected_agent
        if selected == "Agent A":
            multi_agent_verification = agent_a_verification
        elif selected == "Agent B":
            multi_agent_verification = agent_b_verification
        else:
            # Abstain or error
            multi_agent_verification = CandidateVerification(
                candidate_id="multi_agent_abstain",
                candidate_label="Multi-Agent (Abstained)",
                all_passed=False,
                pass_count=0,
                total_count=len(task.test_cases),
                pass_rate=0.0,
                test_results=[],
                execution_error=f"Evaluator abstained or failed: {evaluator_decision.rationale}"
            )

        # Collaboration outcome determination
        b_passed = baseline_verification.all_passed
        m_passed = multi_agent_verification.all_passed

        if m_passed and not b_passed:
            collaboration_outcome = "Helped"
        elif not m_passed and b_passed:
            collaboration_outcome = "Hurt"
        elif b_passed == m_passed:
            collaboration_outcome = "No Effect"
        else:
            collaboration_outcome = "Indeterminate"

        # Evaluator error detection:
        # Flag if:
        # 1. Evaluator chose a candidate that FAILED, but the other candidate PASSED.
        # 2. Evaluator chose a candidate that FAILED.
        evaluator_error_flag = False
        if selected == "Agent A" and not agent_a_verification.all_passed and agent_b_verification.all_passed:
            evaluator_error_flag = True
        elif selected == "Agent B" and not agent_b_verification.all_passed and agent_a_verification.all_passed:
            evaluator_error_flag = True
        elif not multi_agent_verification.all_passed and (agent_a_verification.all_passed or agent_b_verification.all_passed):
            evaluator_error_flag = True

        # Check for agent disagreement
        agent_disagreement = False
        if agent_a_output.parsed_code and agent_b_output.parsed_code:
            # Normalize whitespace
            code_a = "".join(agent_a_output.parsed_code.split())
            code_b = "".join(agent_b_output.parsed_code.split())
            agent_disagreement = (code_a != code_b)
        else:
            agent_disagreement = bool(evaluator_decision.identified_disagreements)

        # Totals
        total_latency = round(
            baseline_output.latency_seconds +
            agent_a_output.latency_seconds +
            agent_b_output.latency_seconds +
            evaluator_decision.latency_seconds,
            3
        )
        api_calls = 4  # Baseline + Agent A + Agent B + Evaluator
        total_tokens = (
            baseline_output.tokens_used +
            agent_a_output.tokens_used +
            agent_b_output.tokens_used +
            evaluator_decision.tokens_used
        )
        is_mock = any([
            baseline_output.is_mock,
            agent_a_output.is_mock,
            agent_b_output.is_mock,
            evaluator_decision.is_mock
        ])

        # Failure hypothesis generation if failure occurred
        failure_hypothesis = cls._derive_failure_hypothesis(
            task=task,
            baseline_verification=baseline_verification,
            agent_a_verification=agent_a_verification,
            agent_b_verification=agent_b_verification,
            multi_agent_verification=multi_agent_verification,
            evaluator_decision=evaluator_decision
        )

        return TaskEvaluationResult(
            task=task,
            baseline_output=baseline_output,
            agent_a_output=agent_a_output,
            agent_b_output=agent_b_output,
            evaluator_decision=evaluator_decision,
            baseline_verification=baseline_verification,
            agent_a_verification=agent_a_verification,
            agent_b_verification=agent_b_verification,
            multi_agent_verification=multi_agent_verification,
            collaboration_outcome=collaboration_outcome,
            evaluator_error_flag=evaluator_error_flag,
            agent_disagreement=agent_disagreement,
            total_latency_seconds=total_latency,
            api_calls_count=api_calls,
            total_tokens_used=total_tokens,
            is_mock=is_mock,
            failure_hypothesis=failure_hypothesis
        )

    @staticmethod
    def _derive_failure_hypothesis(
        task: BenchmarkTask,
        baseline_verification: CandidateVerification,
        agent_a_verification: CandidateVerification,
        agent_b_verification: CandidateVerification,
        multi_agent_verification: CandidateVerification,
        evaluator_decision: EvaluatorDecision
    ) -> Optional[str]:
        """Derives a root-cause explanation for failures grounded in verification evidence."""
        reasons = []

        # Baseline failures
        if not baseline_verification.all_passed:
            failed_tests = [t.test_name for t in baseline_verification.test_results if not t.passed]
            reasons.append(
                f"Baseline failed {len(failed_tests)} test case(s) ({', '.join(failed_tests[:2])}). "
                f"Known trap: {task.expected_trap}"
            )

        # Multi-agent / Evaluator selection failures
        if not multi_agent_verification.all_passed:
            if evaluator_decision.selected_agent == "Abstain":
                reasons.append(f"Multi-agent system abstained from choosing a candidate: {evaluator_decision.rationale}")
            else:
                failed_tests = [t.test_name for t in multi_agent_verification.test_results if not t.passed]
                reasons.append(
                    f"Selected candidate ({evaluator_decision.selected_agent}) failed {len(failed_tests)} test(s). "
                    f"Evaluator rationale was: '{evaluator_decision.rationale}'. "
                    f"Independent check proved this candidate breached test constraints."
                )

        if not reasons:
            return None

        return " | ".join(reasons)

    @classmethod
    def aggregate_benchmark_runs(
        cls,
        task_results: List[TaskEvaluationResult]
    ) -> BenchmarkRunSummary:
        """Aggregates an array of TaskEvaluationResults into summary statistics."""
        total = len(task_results)
        if total == 0:
            return BenchmarkRunSummary()

        completed = sum(1 for r in task_results if not r.baseline_output.error and not r.multi_agent_verification.execution_error)
        b_passes = sum(1 for r in task_results if r.baseline_verification.all_passed)
        m_passes = sum(1 for r in task_results if r.multi_agent_verification.all_passed)

        b_pass_rate = round(b_passes / total, 4)
        m_pass_rate = round(m_passes / total, 4)
        pass_delta = round(m_pass_rate - b_pass_rate, 4)

        helped = sum(1 for r in task_results if r.collaboration_outcome == "Helped")
        no_effect = sum(1 for r in task_results if r.collaboration_outcome == "No Effect")
        hurt = sum(1 for r in task_results if r.collaboration_outcome == "Hurt")
        eval_errors = sum(1 for r in task_results if r.evaluator_error_flag)
        disagreements = sum(1 for r in task_results if r.agent_disagreement)

        avg_b_latency = round(sum(r.baseline_output.latency_seconds for r in task_results) / total, 3)
        avg_m_latency = round(
            sum(
                (r.agent_a_output.latency_seconds + r.agent_b_output.latency_seconds + r.evaluator_decision.latency_seconds)
                for r in task_results
            ) / total,
            3
        )

        total_api_calls = sum(r.api_calls_count for r in task_results)
        total_tokens = sum(r.total_tokens_used for r in task_results)

        return BenchmarkRunSummary(
            total_tasks_attempted=total,
            total_tasks_completed=completed,
            baseline_pass_count=b_passes,
            multi_agent_pass_count=m_passes,
            baseline_pass_rate=b_pass_rate,
            multi_agent_pass_rate=m_pass_rate,
            pass_rate_delta=pass_delta,
            collaboration_helped_count=helped,
            collaboration_no_effect_count=no_effect,
            collaboration_hurt_count=hurt,
            evaluator_error_count=eval_errors,
            agent_disagreement_count=disagreements,
            avg_baseline_latency=avg_b_latency,
            avg_multi_agent_latency=avg_m_latency,
            total_api_calls=total_api_calls,
            total_tokens=total_tokens,
            task_results=task_results
        )
