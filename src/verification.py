import ast
import traceback
from typing import Any, Dict, List, Optional, Callable
from src.schemas import (
    BenchmarkTask,
    TestCaseDefinition,
    TestCaseResult,
    CandidateVerification,
    AgentOutput
)

# Safe built-in functions allowed for restricted code execution
SAFE_BUILTINS = {
    'abs': abs,
    'all': all,
    'any': any,
    'bool': bool,
    'dict': dict,
    'enumerate': enumerate,
    'filter': filter,
    'float': float,
    'int': int,
    'isinstance': isinstance,
    'len': len,
    'list': list,
    'map': map,
    'max': max,
    'min': min,
    'pow': pow,
    'range': range,
    'reversed': reversed,
    'round': round,
    'set': set,
    'sorted': sorted,
    'str': str,
    'sum': sum,
    'tuple': tuple,
    'zip': zip,
    'None': None,
    'True': True,
    'False': False,
}

class SecurityVisitor(ast.NodeVisitor):
    """AST visitor that checks for unsafe operations in generated code."""
    def __init__(self):
        self.unsafe_errors: List[str] = []

    def visit_Import(self, node):
        # We allow collections (like deque or Counter) but disallow os, sys, subprocess, etc.
        for alias in node.names:
            if alias.name not in ('collections', 'math', 'itertools', 're', 'copy'):
                self.unsafe_errors.append(f"Import of module '{alias.name}' is restricted.")
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module not in ('collections', 'math', 'itertools', 're', 'copy'):
            self.unsafe_errors.append(f"Import from module '{node.module}' is restricted.")
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            if node.func.id in ('eval', 'exec', 'open', 'compile', '__import__', 'globals', 'locals', 'input'):
                self.unsafe_errors.append(f"Call to prohibited function '{node.func.id}' detected.")
        self.generic_visit(node)

    def visit_Attribute(self, node):
        if node.attr.startswith("__") and node.attr.endswith("__"):
            self.unsafe_errors.append(f"Dunder attribute access '{node.attr}' is prohibited.")
        self.generic_visit(node)


class VerificationEngine:
    """
    Independent Verification Engine for deterministic evaluation of agent outputs.
    Guarantees that model evaluation never replaces deterministic verification.
    """

    @classmethod
    def verify_candidate(
        cls,
        task: BenchmarkTask,
        output: AgentOutput,
        candidate_label: str
    ) -> CandidateVerification:
        """
        Independently checks candidate output against all deterministic test cases.
        Supports both structured answers and safe restricted execution of candidate functions.
        """
        # If the agent experienced an upstream API/generation error
        if output.error:
            return cls._create_error_verification(
                candidate_id=output.agent_id,
                candidate_label=candidate_label,
                task=task,
                error_msg=f"Agent failed to produce output: {output.error}"
            )

        # Strategy 1: Check structured answers if provided
        if output.parsed_answers is not None and len(output.parsed_answers) == len(task.test_cases):
            return cls._verify_structured_answers(
                candidate_id=output.agent_id,
                candidate_label=candidate_label,
                task=task,
                answers=output.parsed_answers
            )

        # Strategy 2: If code is provided, execute via restricted sandbox
        if output.parsed_code and output.parsed_code.strip():
            return cls._verify_candidate_code(
                candidate_id=output.agent_id,
                candidate_label=candidate_label,
                task=task,
                code_str=output.parsed_code
            )

        # Strategy 3: Check if answers count is mismatched
        if output.parsed_answers is not None:
            return cls._create_error_verification(
                candidate_id=output.agent_id,
                candidate_label=candidate_label,
                task=task,
                error_msg=f"Output answer count ({len(output.parsed_answers)}) does not match test cases ({len(task.test_cases)})."
            )

        return cls._create_error_verification(
            candidate_id=output.agent_id,
            candidate_label=candidate_label,
            task=task,
            error_msg="No parseable code or structured answer list found in candidate response."
        )

    @classmethod
    def _verify_structured_answers(
        cls,
        candidate_id: str,
        candidate_label: str,
        task: BenchmarkTask,
        answers: List[Any]
    ) -> CandidateVerification:
        test_results = []
        pass_count = 0

        for i, tc in enumerate(task.test_cases):
            actual = answers[i]
            expected = tc.expected_output
            passed = cls._compare_values(actual, expected)
            if passed:
                pass_count += 1

            test_results.append(TestCaseResult(
                test_name=tc.name,
                input_repr=repr(tc.input_args),
                expected_repr=repr(expected),
                actual_repr=repr(actual),
                passed=passed,
                is_edge_case=tc.is_edge_case,
                error_message=None if passed else f"Value mismatch: got {actual!r}, expected {expected!r}"
            ))

        total = len(task.test_cases)
        return CandidateVerification(
            candidate_id=candidate_id,
            candidate_label=candidate_label,
            all_passed=(pass_count == total),
            pass_count=pass_count,
            total_count=total,
            pass_rate=round(pass_count / total, 4) if total > 0 else 0.0,
            test_results=test_results,
            execution_error=None
        )

    @classmethod
    def _verify_candidate_code(
        cls,
        candidate_id: str,
        candidate_label: str,
        task: BenchmarkTask,
        code_str: str
    ) -> CandidateVerification:
        # Step 1: Security AST Audit
        try:
            tree = ast.parse(code_str)
        except SyntaxError as e:
            return cls._create_error_verification(
                candidate_id=candidate_id,
                candidate_label=candidate_label,
                task=task,
                error_msg=f"SyntaxError in candidate code: {str(e)}"
            )

        security_visitor = SecurityVisitor()
        security_visitor.visit(tree)
        if security_visitor.unsafe_errors:
            return cls._create_error_verification(
                candidate_id=candidate_id,
                candidate_label=candidate_label,
                task=task,
                error_msg=f"Security violation: {'; '.join(security_visitor.unsafe_errors)}"
            )

        # Step 2: Compile in safe execution environment
        safe_env: Dict[str, Any] = {'__builtins__': SAFE_BUILTINS}
        import collections, math, itertools, re, copy
        safe_env['collections'] = collections
        safe_env['deque'] = collections.deque
        safe_env['defaultdict'] = collections.defaultdict
        safe_env['Counter'] = collections.Counter
        safe_env['math'] = math
        safe_env['itertools'] = itertools
        safe_env['re'] = re
        safe_env['copy'] = copy

        try:
            compiled = compile(tree, filename="<candidate>", mode="exec")
            exec(compiled, safe_env)
        except Exception as e:
            return cls._create_error_verification(
                candidate_id=candidate_id,
                candidate_label=candidate_label,
                task=task,
                error_msg=f"Execution error compiling function: {type(e).__name__}: {str(e)}"
            )

        # Step 3: Find candidate function
        func_candidates = [
            v for k, v in safe_env.items()
            if callable(v) and k not in SAFE_BUILTINS and k not in ('collections', 'math', 'itertools', 're', 'copy')
        ]

        if not func_candidates:
            return cls._create_error_verification(
                candidate_id=candidate_id,
                candidate_label=candidate_label,
                task=task,
                error_msg="No top-level callable function defined in candidate code."
            )

        # Pick the last defined function
        candidate_func = func_candidates[-1]

        # Step 4: Run each test case
        test_results = []
        pass_count = 0

        for tc in task.test_cases:
            try:
                # Deepcopy input args to prevent mutations between tests
                import copy
                clean_args = copy.deepcopy(tc.input_args)
                actual = candidate_func(**clean_args)
                expected = tc.expected_output
                passed = cls._compare_values(actual, expected)
                if passed:
                    pass_count += 1
                test_results.append(TestCaseResult(
                    test_name=tc.name,
                    input_repr=repr(tc.input_args),
                    expected_repr=repr(expected),
                    actual_repr=repr(actual),
                    passed=passed,
                    is_edge_case=tc.is_edge_case,
                    error_message=None if passed else f"Returned {actual!r}, expected {expected!r}"
                ))
            except Exception as e:
                test_results.append(TestCaseResult(
                    test_name=tc.name,
                    input_repr=repr(tc.input_args),
                    expected_repr=repr(tc.expected_output),
                    actual_repr="EXCEPTION",
                    passed=False,
                    is_edge_case=tc.is_edge_case,
                    error_message=f"{type(e).__name__}: {str(e)}"
                ))

        total = len(task.test_cases)
        return CandidateVerification(
            candidate_id=candidate_id,
            candidate_label=candidate_label,
            all_passed=(pass_count == total),
            pass_count=pass_count,
            total_count=total,
            pass_rate=round(pass_count / total, 4) if total > 0 else 0.0,
            test_results=test_results,
            execution_error=None
        )

    @staticmethod
    def _compare_values(actual: Any, expected: Any) -> bool:
        """Deterministic comparison with float tolerance and deep equality."""
        if actual == expected:
            return True
        if isinstance(actual, float) and isinstance(expected, (int, float)):
            return abs(actual - expected) < 1e-6
        if isinstance(actual, (list, tuple)) and isinstance(expected, (list, tuple)):
            if len(actual) != len(expected):
                return False
            return all(VerificationEngine._compare_values(a, e) for a, e in zip(actual, expected))
        if isinstance(actual, dict) and isinstance(expected, dict):
            if set(actual.keys()) != set(expected.keys()):
                return False
            return all(VerificationEngine._compare_values(actual[k], expected[k]) for k in expected)
        return False

    @classmethod
    def _create_error_verification(
        cls,
        candidate_id: str,
        candidate_label: str,
        task: BenchmarkTask,
        error_msg: str
    ) -> CandidateVerification:
        test_results = [
            TestCaseResult(
                test_name=tc.name,
                input_repr=repr(tc.input_args),
                expected_repr=repr(tc.expected_output),
                actual_repr="ERROR",
                passed=False,
                is_edge_case=tc.is_edge_case,
                error_message=error_msg
            )
            for tc in task.test_cases
        ]
        return CandidateVerification(
            candidate_id=candidate_id,
            candidate_label=candidate_label,
            all_passed=False,
            pass_count=0,
            total_count=len(task.test_cases),
            pass_rate=0.0,
            test_results=test_results,
            execution_error=error_msg
        )
