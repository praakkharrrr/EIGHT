import json
import re
from typing import Dict, Any, Optional
from src.schemas import BenchmarkTask, AgentOutput, EvaluatorDecision
from src.gemma_client import GemmaClient

class EvaluatorRunner:
    """Runs the Gemma 4 Evaluator to compare candidate agents and output structured decisions."""

    def __init__(self, client: GemmaClient):
        self.client = client

    def evaluate_candidates(
        self,
        task: BenchmarkTask,
        agent_a: AgentOutput,
        agent_b: AgentOutput
    ) -> EvaluatorDecision:
        """
        Submits candidate outputs to Gemma 4 for comparative analysis and verdict.
        Returns a validated EvaluatorDecision.
        """
        system_instruction = (
            "You are the Gemma 4 Evaluator in EIGHT — AI Crash-Test Lab. "
            "You are an impartial, evidence-driven code reviewer. "
            "Your job is to compare candidate implementations from Agent A and Agent B for a programming task. "
            "Analyze algorithmic correctness, time/space complexity, and critical edge cases (such as empty inputs, boundaries, and subtle traps). "
            "Select the superior candidate ('Agent A' or 'Agent B'), or 'Abstain' if both are critically defective or evidence is insufficient. "
            "You MUST respond ONLY with valid JSON using the following keys:\n"
            "{\n"
            '  "selected_agent": "Agent A" | "Agent B" | "Abstain",\n'
            '  "rationale": "Concise justification for your selection based on code evidence",\n'
            '  "identified_disagreements": ["list of concrete points where A and B disagree"],\n'
            '  "confidence_score": 0.0 to 1.0,\n'
            '  "potential_failure_modes": ["list of remaining risks or subtle edge cases that might fail"]\n'
            "}"
        )

        prompt = (
            f"EVALUATION TASK: {task.task_id} — {task.title}\n"
            f"Description: {task.description}\n"
            f"Input Spec: {task.input_spec}\n"
            f"Output Spec: {task.output_spec}\n\n"
            f"--- AGENT A SUBMISSION ---\n"
            f"Strategy: {agent_a.strategy_name}\n"
            f"Code:\n```python\n{agent_a.parsed_code or 'No code provided'}\n```\n"
            f"Explanation:\n{agent_a.explanation}\n\n"
            f"--- AGENT B SUBMISSION ---\n"
            f"Strategy: {agent_b.strategy_name}\n"
            f"Code:\n```python\n{agent_b.parsed_code or 'No code provided'}\n```\n"
            f"Explanation:\n{agent_b.explanation}\n\n"
            "Compare the two implementations. Deliver your verdict in strict JSON format."
        )

        if self.client.is_mock_mode:
            mock_data = self._get_mock_evaluation(task, agent_a, agent_b)
            return EvaluatorDecision(
                selected_agent=mock_data["selected_agent"],
                rationale=mock_data["rationale"],
                identified_disagreements=mock_data["identified_disagreements"],
                confidence_score=mock_data["confidence_score"],
                potential_failure_modes=mock_data["potential_failure_modes"],
                raw_response=json.dumps(mock_data, indent=2),
                latency_seconds=0.28,
                tokens_used=220,
                error=None,
                is_mock=True
            )

        res = self.client.generate(prompt=prompt, system_instruction=system_instruction)
        raw_text = res["text"]
        latency = res["latency_seconds"]
        tokens = res["tokens_used"]
        err = res["error"]

        if err:
            return EvaluatorDecision(
                selected_agent="Abstain",
                rationale=f"Evaluator API failed: {err}",
                identified_disagreements=[],
                confidence_score=0.0,
                potential_failure_modes=["API error during generation"],
                raw_response=raw_text,
                latency_seconds=latency,
                tokens_used=tokens,
                error=err,
                is_mock=False
            )

        # Parse JSON
        parsed_dict, parse_err = self._parse_json_response(raw_text)
        if parse_err:
            return EvaluatorDecision(
                selected_agent="Abstain",
                rationale=f"Malformed Evaluator response: {parse_err}",
                identified_disagreements=["Failed to parse structured JSON"],
                confidence_score=0.0,
                potential_failure_modes=["Malformed JSON formatting from model"],
                raw_response=raw_text,
                latency_seconds=latency,
                tokens_used=tokens,
                error=parse_err,
                is_mock=False
            )

        selected = parsed_dict.get("selected_agent", "Abstain")
        if selected not in ("Agent A", "Agent B", "Abstain"):
            selected = "Abstain"

        return EvaluatorDecision(
            selected_agent=selected,
            rationale=str(parsed_dict.get("rationale", "No rationale provided.")),
            identified_disagreements=list(parsed_dict.get("identified_disagreements", [])),
            confidence_score=float(parsed_dict.get("confidence_score", 0.5)),
            potential_failure_modes=list(parsed_dict.get("potential_failure_modes", [])),
            raw_response=raw_text,
            latency_seconds=latency,
            tokens_used=tokens,
            error=None,
            is_mock=False
        )

    @staticmethod
    def _parse_json_response(text: str) -> tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Cleans and extracts JSON object from LLM response text."""
        if not text:
            return None, "Empty response text"
        
        # Strip markdown fences
        clean = text.strip()
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", clean, re.DOTALL)
        if match:
            clean = match.group(1)
        else:
            # Try to find outermost { and }
            start = clean.find("{")
            end = clean.rfind("}")
            if start != -1 and end != -1 and end > start:
                clean = clean[start:end+1]

        try:
            data = json.loads(clean)
            return data, None
        except Exception as e:
            return None, f"JSONDecodeError: {str(e)}"

    def _get_mock_evaluation(
        self,
        task: BenchmarkTask,
        agent_a: AgentOutput,
        agent_b: AgentOutput
    ) -> Dict[str, Any]:
        """Realistic mock evaluator decisions reflecting algorithmic nuances."""
        t_id = task.task_id
        if t_id == "TASK-01":
            return {
                "selected_agent": "Agent B",
                "rationale": "Agent B provides a clean, explicit order-preserving lookup using a tracking set and append list. Agent A relies on dict.fromkeys which also works in Python 3.7+, but Agent B's formulation is universally transparent and avoids mutable hash assumptions.",
                "identified_disagreements": [
                    "Agent A relies on dict.fromkeys language-specific order semantics; Agent B uses an explicit seen set with an append array."
                ],
                "confidence_score": 0.94,
                "potential_failure_modes": [
                    "Non-hashable items would require unhashable element serialization."
                ]
            }
        elif t_id == "TASK-02":
            return {
                "selected_agent": "Agent B",
                "rationale": "Agent B correctly recognized the critical constraint that brackets inside double-quoted string literals must be ignored. Agent A utilized a standard stack matcher that erroneously parses quoted brackets as syntactic elements.",
                "identified_disagreements": [
                    "Handling of quote literals: Agent B tracks an in_quote boolean state machine; Agent A treats all characters uniformly."
                ],
                "confidence_score": 0.98,
                "potential_failure_modes": [
                    "Escaped backslash quotes (e.g. \\\" ) would require full lexical tokenizer."
                ]
            }
        elif t_id == "TASK-03":
            return {
                "selected_agent": "Agent A",
                "rationale": "Agent A provides an optimal O(N) dynamic programming state machine (hold, sold, rest). Agent B also implements a state machine, but Agent A's transitions are cleaner and handle boundary values more transparently.",
                "identified_disagreements": [
                    "Minor variable naming and initialization nuances in the 3-state DP recurrence."
                ],
                "confidence_score": 0.90,
                "potential_failure_modes": [
                    "Extremely large price arrays might benefit from memory pre-allocation."
                ]
            }
        elif t_id == "TASK-04":
            return {
                "selected_agent": "Agent B",
                "rationale": "Both Agent A and Agent B preserve None values and falsy values, but Agent B explicitly provides boundary protection for nested dictionaries with empty leaf entries.",
                "identified_disagreements": [
                    "Treatment of empty inner sub-dictionaries."
                ],
                "confidence_score": 0.88,
                "potential_failure_modes": [
                    "Circular dictionary references would cause recursion depth limit."
                ]
            }
        elif t_id == "TASK-05":
            return {
                "selected_agent": "Agent A",
                "rationale": "Agent A leverages python divmod cleanly to split base cents and distribute remainders with zero penny drift. Agent B also achieves this, but Agent A's formulation is more concise and idiomatic.",
                "identified_disagreements": [
                    "Syntax style: divmod tuple unpacking vs manual modulo division."
                ],
                "confidence_score": 0.95,
                "potential_failure_modes": [
                    "Negative input cents require pre-condition assertion."
                ]
            }
        elif t_id == "TASK-06":
            return {
                "selected_agent": "Agent A",
                "rationale": "Agent A implements the optimal O(N) deque sliding window algorithm. Agent B implements a similar deque algorithm, but Agent A's index bounds are strictly minimal.",
                "identified_disagreements": [
                    "Deque eviction order and window initialization."
                ],
                "confidence_score": 0.91,
                "potential_failure_modes": [
                    "k values larger than array length."
                ]
            }
        elif t_id == "TASK-07":
            return {
                "selected_agent": "Agent B",
                "rationale": "Agent B recognized the strict Roman numeral validation requirement and implemented a canonical round-trip reconstruction check (to_roman), correctly rejecting invalid inputs like 'IIII' and 'IC'. Agent A only performed naive additive-subtractive accumulation which erroneously accepts invalid strings.",
                "identified_disagreements": [
                    "Syntax validation: Agent B enforces Roman numeral grammar via canonical re-encoding; Agent A blindly calculates values for invalid strings."
                ],
                "confidence_score": 0.97,
                "potential_failure_modes": [
                    "Case sensitivity on lowercase roman numerals."
                ]
            }
        elif t_id == "TASK-08":
            return {
                "selected_agent": "Agent B",
                "rationale": "Both agents implement the single-character guard constraint to prevent 'A1' inflation, but Agent B explicitly guards against empty string and single-character boundary conditions.",
                "identified_disagreements": [
                    "Boundary condition return checks for empty text."
                ],
                "confidence_score": 0.92,
                "potential_failure_modes": [
                    "Strings containing digits might be ambiguous upon decompression."
                ]
            }
        return {
            "selected_agent": "Agent A",
            "rationale": "Agent A provided a concise, readable implementation.",
            "identified_disagreements": [],
            "confidence_score": 0.70,
            "potential_failure_modes": []
        }
