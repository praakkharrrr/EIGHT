import re
import json
from typing import Dict, Any, Optional, List
from src.schemas import BenchmarkTask, AgentOutput
from src.gemma_client import GemmaClient

class AgentRunner:
    """Orchestrates Baseline, Agent A, and Agent B executions."""

    def __init__(self, client: GemmaClient):
        self.client = client

    def run_baseline(self, task: BenchmarkTask) -> AgentOutput:
        """Runs the single-agent baseline with a direct zero-shot prompt."""
        system_instruction = (
            "You are a single AI coding agent. You must solve programming tasks directly and concisely. "
            "Always wrap your executable Python code inside a ```python ``` markdown code block. "
            "Keep your explanation brief and focused on the solution."
        )
        prompt = (
            f"Solve this task:\n\n"
            f"Task ID: {task.task_id}\n"
            f"Title: {task.title}\n"
            f"Description: {task.description}\n"
            f"Input: {task.input_spec}\n"
            f"Output: {task.output_spec}\n\n"
            "Provide the Python function implementation inside ```python ... ``` and a short explanation."
        )

        if self.client.is_mock_mode:
            raw_text = self._get_mock_baseline(task)
            return self._format_agent_output(
                agent_id="baseline",
                strategy_name="Single-Agent Zero-Shot Baseline",
                prompt_used=prompt,
                raw_response=raw_text,
                latency=0.18,
                tokens=120,
                error=None,
                is_mock=True
            )

        res = self.client.generate(prompt=prompt, system_instruction=system_instruction)
        return self._format_agent_output(
            agent_id="baseline",
            strategy_name="Single-Agent Zero-Shot Baseline",
            prompt_used=prompt,
            raw_response=res["text"],
            latency=res["latency_seconds"],
            tokens=res["tokens_used"],
            error=res["error"],
            is_mock=res["is_mock"]
        )

    def run_agent_a(self, task: BenchmarkTask) -> AgentOutput:
        """Runs Agent A: Analytical / First-Principles Algorithmic Engineer."""
        system_instruction = (
            "You are Agent A, a senior algorithmic engineer. You prioritize optimal time/space complexity, "
            "standard data structures, and idiomatic Python. "
            "Wrap your code in ```python ``` and explain your algorithmic design."
        )
        prompt = (
            f"Solve the following algorithmic task from first principles:\n\n"
            f"Task ID: {task.task_id}\n"
            f"Title: {task.title}\n"
            f"Description: {task.description}\n"
            f"Input: {task.input_spec}\n"
            f"Output: {task.output_spec}\n\n"
            "Implement the Python function inside ```python ... ``` and explain your algorithmic approach."
        )

        if self.client.is_mock_mode:
            raw_text = self._get_mock_agent_a(task)
            return self._format_agent_output(
                agent_id="agent_a",
                strategy_name="Analytical / First-Principles Strategy",
                prompt_used=prompt,
                raw_response=raw_text,
                latency=0.22,
                tokens=140,
                error=None,
                is_mock=True
            )

        res = self.client.generate(prompt=prompt, system_instruction=system_instruction)
        return self._format_agent_output(
            agent_id="agent_a",
            strategy_name="Analytical / First-Principles Strategy",
            prompt_used=prompt,
            raw_response=res["text"],
            latency=res["latency_seconds"],
            tokens=res["tokens_used"],
            error=res["error"],
            is_mock=res["is_mock"]
        )

    def run_agent_b(self, task: BenchmarkTask) -> AgentOutput:
        """Runs Agent B: Adversarial Boundary & Edge-Case Specialist."""
        system_instruction = (
            "You are Agent B, an adversarial verification and edge-case specialist. "
            "You scrutinize potential traps, empty/null inputs, off-by-one errors, and boundary values. "
            "Do not rely on naive implementations. Provide a robust Python function in ```python ``` "
            "and list the specific edge cases your solution guards against."
        )
        prompt = (
            f"Solve the following task with special focus on adversarial edge cases and boundary conditions:\n\n"
            f"Task ID: {task.task_id}\n"
            f"Title: {task.title}\n"
            f"Description: {task.description}\n"
            f"Input: {task.input_spec}\n"
            f"Output: {task.output_spec}\n\n"
            "Provide the Python implementation inside ```python ... ``` and explicitly document guarded edge cases."
        )

        if self.client.is_mock_mode:
            raw_text = self._get_mock_agent_b(task)
            return self._format_agent_output(
                agent_id="agent_b",
                strategy_name="Adversarial Boundary Analysis Strategy",
                prompt_used=prompt,
                raw_response=raw_text,
                latency=0.25,
                tokens=160,
                error=None,
                is_mock=True
            )

        res = self.client.generate(prompt=prompt, system_instruction=system_instruction)
        return self._format_agent_output(
            agent_id="agent_b",
            strategy_name="Adversarial Boundary Analysis Strategy",
            prompt_used=prompt,
            raw_response=res["text"],
            latency=res["latency_seconds"],
            tokens=res["tokens_used"],
            error=res["error"],
            is_mock=res["is_mock"]
        )

    @classmethod
    def extract_code(cls, text: str) -> Optional[str]:
        """Extracts python code block from markdown string."""
        if not text:
            return None
        # Match ```python ... ``` or ``` ... ```
        pattern = r"```(?:python)?\s*\n(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
        if matches:
            return matches[0].strip()
        # If no markdown block, but starts with def
        if "def " in text:
            lines = []
            capture = False
            for line in text.split("\n"):
                if line.strip().startswith("def "):
                    capture = True
                if capture:
                    lines.append(line)
            if lines:
                return "\n".join(lines).strip()
        return None

    @classmethod
    def _format_agent_output(
        cls,
        agent_id: str,
        strategy_name: str,
        prompt_used: str,
        raw_response: str,
        latency: float,
        tokens: int,
        error: Optional[str],
        is_mock: bool
    ) -> AgentOutput:
        parsed_code = cls.extract_code(raw_response) if raw_response else None
        
        # Extract explanation text (text outside of code blocks)
        explanation = ""
        if raw_response:
            non_code = re.sub(r"```.*?```", "", raw_response, flags=re.DOTALL)
            explanation = non_code.strip()

        return AgentOutput(
            agent_id=agent_id,
            strategy_name=strategy_name,
            prompt_used=prompt_used,
            raw_response=raw_response,
            parsed_code=parsed_code,
            parsed_answers=None,
            explanation=explanation,
            latency_seconds=latency,
            tokens_used=tokens,
            error=error,
            is_mock=is_mock
        )

    # -------------------------------------------------------------
    # High-Fidelity Mock Generators for Realistic Benchmark Tests
    # -------------------------------------------------------------
    def _get_mock_baseline(self, task: BenchmarkTask) -> str:
        """Simulates common baseline agent pitfalls."""
        t_id = task.task_id
        if t_id == "TASK-01":
            # Naive set() pitfall: loses order
            return "```python\ndef stable_dedup(items):\n    # Fast set deduplication\n    return list(set(items))\n```\n\nExplanation: Converted the items to a Python set to eliminate duplicates."
        elif t_id == "TASK-02":
            # Naive stack without checking quotes
            return "```python\ndef is_bracket_balanced(s):\n    stack = []\n    matching = {')': '(', ']': '[', '}': '{'}\n    for ch in s:\n        if ch in '([{':\n            stack.append(ch)\n        elif ch in ')]}':\n            if not stack or stack[-1] != matching[ch]:\n                return False\n            stack.pop()\n    return len(stack) == 0\n```\n\nExplanation: Standard stack-based bracket validator."
        elif t_id == "TASK-03":
            # Greedy pitfall
            return "```python\ndef max_profit_cooldown(prices):\n    # Naive greedy without cooldown\n    profit = 0\n    for i in range(1, len(prices)):\n        if prices[i] > prices[i-1]:\n            profit += prices[i] - prices[i-1]\n    return profit\n```\n\nExplanation: Aggregates positive adjacent price deltas."
        elif t_id == "TASK-04":
            # Flattener with truthy check pitfall
            return "```python\ndef flatten_dict(d, parent_key='', sep='.'):\n    items = {}\n    for k, v in d.items():\n        new_key = f\"{parent_key}{sep}{k}\" if parent_key else k\n        if isinstance(v, dict):\n            items.update(flatten_dict(v, new_key, sep=sep))\n        elif v: # BUG: drops None, 0, False\n            items[new_key] = v\n    return items\n```\n\nExplanation: Recursively flattens nested dictionaries."
        elif t_id == "TASK-05":
            # Floating point division pitfall
            return "```python\ndef split_currency(total_cents, num_recipients):\n    part = int(round(total_cents / num_recipients))\n    return [part] * num_recipients\n```\n\nExplanation: Divides total by recipients and rounds."
        elif t_id == "TASK-06":
            # Sliding window with k off-by-one
            return "```python\ndef max_sliding_window(nums, k):\n    if not nums: return []\n    return [max(nums[i:i+k]) for i in range(len(nums) - k + 1)]\n```\n\nExplanation: Simple slice maximum for each window."
        elif t_id == "TASK-07":
            # Roman converter without validation
            return "```python\ndef parse_roman_strict(s):\n    vals = {'I':1,'V':5,'X':10,'L':50,'C':100,'D':500,'M':1000}\n    total = 0\n    prev = 0\n    for ch in reversed(s):\n        curr = vals.get(ch, 0)\n        if curr < prev: total -= curr\n        else: total += curr; prev = curr\n    return total\n```\n\nExplanation: Standard reverse accumulator."
        elif t_id == "TASK-08":
            # Naive RLE: expands single letters to A1
            return "```python\ndef run_length_encode(text):\n    if not text: return ''\n    res = []\n    count = 1\n    for i in range(1, len(text)):\n        if text[i] == text[i-1]:\n            count += 1\n        else:\n            res.append(f\"{text[i-1]}{count}\")\n            count = 1\n    res.append(f\"{text[-1]}{count}\")\n    return ''.join(res)\n```\n\nExplanation: Encodes every run with char followed by count."
        return "```python\ndef solution(*args, **kwargs):\n    return []\n```"

    def _get_mock_agent_a(self, task: BenchmarkTask) -> str:
        """Simulates Agent A: Analytical / First-Principles."""
        t_id = task.task_id
        if t_id == "TASK-01":
            # dict.fromkeys preserves order
            return "```python\ndef stable_dedup(items):\n    # dict keys preserve insertion order in Python 3.7+\n    return list(dict.fromkeys(items))\n```\n\nExplanation: In modern Python, dict keys preserve insertion order while providing O(N) unique deduplication."
        elif t_id == "TASK-02":
            # Misses the quote condition
            return "```python\ndef is_bracket_balanced(s):\n    stack = []\n    table = {')': '(', ']': '[', '}': '{'}\n    for char in s:\n        if char in '([{':\n            stack.append(char)\n        elif char in ')]}':\n            if not stack or stack[-1] != table[char]:\n                return False\n            stack.pop()\n    return not stack\n```\n\nExplanation: Classic stack structure for bracket validation."
        elif t_id == "TASK-03":
            # Correct dynamic programming
            return "```python\ndef max_profit_cooldown(prices):\n    if not prices or len(prices) < 2:\n        return 0\n    hold, sold, rest = -prices[0], 0, 0\n    for p in prices[1:]:\n        prev_hold, prev_sold = hold, sold\n        hold = max(prev_hold, rest - p)\n        sold = prev_hold + p\n        rest = max(rest, prev_sold)\n    return max(sold, rest)\n```\n\nExplanation: Dynamic programming state machine with 3 states (hold, sold, rest)."
        elif t_id == "TASK-04":
            # Correct recursive flattener
            return "```python\ndef flatten_dict(d, parent_key='', sep='.'):\n    items = []\n    for k, v in d.items():\n        new_key = f\"{parent_key}{sep}{k}\" if parent_key else str(k)\n        if isinstance(v, dict) and v:\n            items.extend(flatten_dict(v, new_key, sep=sep).items())\n        else:\n            items.append((new_key, v))\n    return dict(items)\n```\n\nExplanation: Recursively unpacks dictionaries while preserving explicit None and false values."
        elif t_id == "TASK-05":
            # Correct split with divmod
            return "```python\ndef split_currency(total_cents, num_recipients):\n    base, rem = divmod(total_cents, num_recipients)\n    return [base + 1 if i < rem else base for i in range(num_recipients)]\n```\n\nExplanation: Divmod calculates base share and exact remaining cents distributed to earliest recipients."
        elif t_id == "TASK-06":
            # Deque O(N) sliding window
            return "```python\nfrom collections import deque\ndef max_sliding_window(nums, k):\n    if not nums or k <= 0: return []\n    q = deque()\n    res = []\n    for i, n in enumerate(nums):\n        while q and nums[q[-1]] < n: q.pop()\n        q.append(i)\n        if q[0] <= i - k: q.popleft()\n        if i >= k - 1: res.append(nums[q[0]])\n    return res\n```\n\nExplanation: Monotonic deque maintaining maximum element indices in O(N)."
        elif t_id == "TASK-07":
            # Naive parser without strict check
            return "```python\ndef parse_roman_strict(s):\n    mapping = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}\n    total, prev = 0, 0\n    for ch in reversed(s):\n        curr = mapping.get(ch, 0)\n        if curr < prev: total -= curr\n        else: total += curr; prev = curr\n    return total\n```\n\nExplanation: Standard reverse accumulator."
        elif t_id == "TASK-08":
            # Correct single-char guard
            return "```python\ndef run_length_encode(text):\n    if not text: return ''\n    res = []\n    count = 1\n    for i in range(1, len(text)):\n        if text[i] == text[i-1]: count += 1\n        else:\n            res.append(f\"{text[i-1]}{count}\" if count >= 2 else text[i-1])\n            count = 1\n    res.append(f\"{text[-1]}{count}\" if count >= 2 else text[-1])\n    return ''.join(res)\n```\n\nExplanation: Encodes counts only when count >= 2, leaving single letters unmodified."
        return "```python\ndef solution(*args, **kwargs):\n    return []\n```"

    def _get_mock_agent_b(self, task: BenchmarkTask) -> str:
        """Simulates Agent B: Adversarial Boundary Specialist."""
        t_id = task.task_id
        if t_id == "TASK-01":
            # Set lookup + list append (also preserves order)
            return "```python\ndef stable_dedup(items):\n    seen = set()\n    result = []\n    for x in items:\n        if x not in seen:\n            seen.add(x)\n            result.append(x)\n    return result\n```\n\nEdge Cases Handled:\n- Preserves exact insertion order (does not use set() directly).\n- Handles empty lists and all-duplicate lists cleanly."
        elif t_id == "TASK-02":
            # Robust quote handling
            return "```python\ndef is_bracket_balanced(s):\n    stack = []\n    pairs = {')': '(', ']': '[', '}': '{'}\n    in_quote = False\n    for ch in s:\n        if ch == '\"':\n            in_quote = not in_quote\n            continue\n        if in_quote:\n            continue\n        if ch in '([{':\n            stack.append(ch)\n        elif ch in ')]}':\n            if not stack or stack[-1] != pairs[ch]:\n                return False\n            stack.pop()\n    return len(stack) == 0 and not in_quote\n```\n\nEdge Cases Handled:\n- Quoted bracket literals '\"(\"' or '\"]\"' are ignored.\n- Unclosed quotes return False.\n- Empty strings evaluate to True."
        elif t_id == "TASK-03":
            # State machine with edge cases
            return "```python\ndef max_profit_cooldown(prices):\n    if not prices or len(prices) <= 1:\n        return 0\n    hold = -prices[0]\n    sold = 0\n    rest = 0\n    for p in prices[1:]:\n        prev_sold = sold\n        sold = hold + p\n        hold = max(hold, rest - p)\n        rest = max(rest, prev_sold)\n    return max(sold, rest)\n```\n\nEdge Cases Handled:\n- Zero or single-element lists return 0.\n- Strictly decreasing prices return 0.\n- Optimal interleaving of sell cooldowns."
        elif t_id == "TASK-04":
            # Explicit handling of None and falsy
            return "```python\ndef flatten_dict(d, parent_key='', sep='.'):\n    items = []\n    for k, v in d.items():\n        new_key = f\"{parent_key}{sep}{k}\" if parent_key else str(k)\n        if isinstance(v, dict) and v:\n            items.extend(flatten_dict(v, new_key, sep=sep).items())\n        else:\n            items.append((new_key, v))\n    return dict(items)\n```\n\nEdge Cases Handled:\n- None/null values are explicitly retained.\n- Falsy values (False, 0) are preserved."
        elif t_id == "TASK-05":
            # Split with boundary checks
            return "```python\ndef split_currency(total_cents, num_recipients):\n    if num_recipients <= 0: raise ValueError('Invalid recipients')\n    base = total_cents // num_recipients\n    rem = total_cents % num_recipients\n    return [base + 1 if i < rem else base for i in range(num_recipients)]\n```\n\nEdge Cases Handled:\n- 0 total cents returns [0, ..., 0].\n- Remainder distributed cleanly to earliest indices.\n- No floating point penny drift."
        elif t_id == "TASK-06":
            # Over-engineered or alternative
            return "```python\ndef max_sliding_window(nums, k):\n    if not nums or k <= 0: return []\n    if k == 1: return list(nums)\n    from collections import deque\n    q = deque()\n    res = []\n    for i, n in enumerate(nums):\n        while q and nums[q[-1]] < n: q.pop()\n        q.append(i)\n        if q[0] <= i - k: q.popleft()\n        if i >= k - 1: res.append(nums[q[0]])\n    return res\n```\n\nEdge Cases Handled:\n- k = 1 returns input list.\n- k = len(nums) returns single maximum.\n- All-negative values correctly evaluated."
        elif t_id == "TASK-07":
            # Strict Roman validator with canonical re-encoding check!
            return "```python\ndef parse_roman_strict(s):\n    if not s or not isinstance(s, str):\n        return -1\n    mapping = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}\n    for ch in s:\n        if ch not in mapping: return -1\n    \n    def to_roman(num):\n        val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]\n        syb = [\"M\", \"CM\", \"D\", \"CD\", \"C\", \"XC\", \"L\", \"XL\", \"X\", \"IX\", \"V\", \"IV\", \"I\"]\n        res = \"\"\n        for i in range(len(val)):\n            while num >= val[i]: res += syb[i]; num -= val[i]\n        return res\n\n    total, prev = 0, 0\n    for ch in reversed(s):\n        curr = mapping[ch]\n        if curr < prev: total -= curr\n        else: total += curr; prev = curr\n    if total <= 0 or total > 3999: return -1\n    if to_roman(total) != s: return -1\n    return total\n```\n\nEdge Cases Handled:\n- Strictly rejects 'IIII', 'VV', and illegal jumps like 'IC' by round-trip re-encoding canonical Roman notation."
        elif t_id == "TASK-08":
            return "```python\ndef run_length_encode(text):\n    if not text: return ''\n    res = []\n    count = 1\n    for i in range(1, len(text)):\n        if text[i] == text[i-1]: count += 1\n        else:\n            res.append(f\"{text[i-1]}{count}\" if count >= 2 else text[i-1])\n            count = 1\n    res.append(f\"{text[-1]}{count}\" if count >= 2 else text[-1])\n    return ''.join(res)\n```\n\nEdge Cases Handled:\n- Guard against 'A1' expansion on single characters.\n- Handles empty and single-char strings."
        return "```python\ndef solution(*args, **kwargs):\n    return []\n```"
