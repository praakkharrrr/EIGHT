import json
import os
from typing import List, Dict, Any, Optional
from src.schemas import BenchmarkTask, TestCaseDefinition
from src.config import Config

class BenchmarkManager:
    """Loads, validates, and manages benchmark tasks."""

    def __init__(self, file_path: Optional[str] = None):
        self.file_path = file_path or Config.BENCHMARK_FILE_PATH
        self._tasks: Dict[str, BenchmarkTask] = {}
        self.load_tasks()

    def load_tasks(self) -> List[BenchmarkTask]:
        """Loads tasks from the benchmark JSON file."""
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Benchmark file not found: {self.file_path}")

        with open(self.file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self._tasks.clear()
        for t_dict in data.get("tasks", []):
            task = BenchmarkTask(**t_dict)
            self._tasks[task.task_id] = task

        return list(self._tasks.values())

    def get_task(self, task_id: str) -> Optional[BenchmarkTask]:
        """Returns a single benchmark task by ID."""
        return self._tasks.get(task_id)

    def get_all_tasks(self) -> List[BenchmarkTask]:
        """Returns all loaded benchmark tasks."""
        return list(self._tasks.values())

    @staticmethod
    def reference_implementations() -> Dict[str, Any]:
        """
        Ground-truth reference implementations for deterministic verification
        and test-suite self-checking.
        """
        def stable_dedup(items: list) -> list:
            seen = set()
            result = []
            for item in items:
                if item not in seen:
                    seen.add(item)
                    result.append(item)
            return result

        def is_bracket_balanced(s: str) -> bool:
            stack = []
            matching = {')': '(', ']': '[', '}': '{'}
            in_quote = False
            for ch in s:
                if ch == '"':
                    in_quote = not in_quote
                    continue
                if in_quote:
                    continue
                if ch in "([{":
                    stack.append(ch)
                elif ch in ")]}":
                    if not stack or stack[-1] != matching[ch]:
                        return False
                    stack.pop()
            return len(stack) == 0 and not in_quote

        def max_profit_cooldown(prices: list) -> int:
            if not prices or len(prices) < 2:
                return 0
            n = len(prices)
            # hold: max profit holding stock
            # sold: max profit just sold stock today
            # rest: max profit in cooldown or waiting
            hold = -prices[0]
            sold = 0
            rest = 0
            for i in range(1, n):
                prev_hold = hold
                prev_sold = sold
                prev_rest = rest
                hold = max(prev_hold, prev_rest - prices[i])
                sold = prev_hold + prices[i]
                rest = max(prev_rest, prev_sold)
            return max(sold, rest)

        def flatten_dict(d: dict, parent_key: str = '', sep: str = '.') -> dict:
            items = []
            for k, v in d.items():
                new_key = f"{parent_key}{sep}{k}" if parent_key else str(k)
                if isinstance(v, dict) and v:  # non-empty dict
                    items.extend(flatten_dict(v, new_key, sep=sep).items())
                else:
                    items.append((new_key, v))
            return dict(items)

        def split_currency(total_cents: int, num_recipients: int) -> list:
            if num_recipients <= 0:
                raise ValueError("num_recipients must be > 0")
            base = total_cents // num_recipients
            rem = total_cents % num_recipients
            return [base + 1 if i < rem else base for i in range(num_recipients)]

        def max_sliding_window(nums: list, k: int) -> list:
            if not nums or k <= 0:
                return []
            if k == 1:
                return list(nums)
            from collections import deque
            q = deque()
            res = []
            for i, n in enumerate(nums):
                while q and nums[q[-1]] < n:
                    q.pop()
                q.append(i)
                if q[0] <= i - k:
                    q.popleft()
                if i >= k - 1:
                    res.append(nums[q[0]])
            return res

        def parse_roman_strict(s: str) -> int:
            if not s or not isinstance(s, str):
                return -1
            roman_to_int = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
            for ch in s:
                if ch not in roman_to_int:
                    return -1
            # Reconstruct to verify canonical representation
            def int_to_roman(num: int) -> str:
                val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
                syb = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]
                res = ""
                for i in range(len(val)):
                    while num >= val[i]:
                        res += syb[i]
                        num -= val[i]
                return res

            total = 0
            prev_val = 0
            for ch in reversed(s):
                curr = roman_to_int[ch]
                if curr < prev_val:
                    total -= curr
                else:
                    total += curr
                    prev_val = curr
            if total <= 0 or total > 3999:
                return -1
            if int_to_roman(total) != s:
                return -1
            return total

        def run_length_encode(text: str) -> str:
            if not text:
                return ""
            res = []
            count = 1
            for i in range(1, len(text)):
                if text[i] == text[i - 1]:
                    count += 1
                else:
                    if count >= 2:
                        res.append(f"{text[i-1]}{count}")
                    else:
                        res.append(text[i-1])
                    count = 1
            if count >= 2:
                res.append(f"{text[-1]}{count}")
            else:
                res.append(text[-1])
            return "".join(res)

        return {
            "TASK-01": stable_dedup,
            "TASK-02": is_bracket_balanced,
            "TASK-03": max_profit_cooldown,
            "TASK-04": flatten_dict,
            "TASK-05": split_currency,
            "TASK-06": max_sliding_window,
            "TASK-07": parse_roman_strict,
            "TASK-08": run_length_encode,
        }
