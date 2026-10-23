# EIGHT — AI Crash-Test Lab

> **"Don't trust the answer. Test the intelligence behind it."**

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Gemma 4](https://img.shields.io/badge/Gemma-4%20API-electric--blue)](https://ai.google.dev/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40%2B-FF4B4B.svg)](https://streamlit.io/)
[![pytest](https://img.shields.io/badge/pytest-passing-brightgreen)](https://docs.pytest.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🎯 1. Project Identity & Mission

**EIGHT** is an AI reliability evaluation platform designed to scientifically crash-test AI code generation. It compares a **single-agent baseline** against a **multi-agent collaborative workflow**, independently verifies their candidate solutions using isolated deterministic test suites, detects hallucinations and misjudgments, and quantitatively reports whether multi-agent collaboration actually improves correctness.

### Core Differentiator: Evidence Over Vibes
Most multi-agent demos show agents conversing without establishing whether the final answer is actually correct. **EIGHT** delivers empirical verification:
- **Did collaboration outperform the single-agent baseline?**
- **Which specific edge cases passed or failed independent verification?**
- **Did the Gemma 4 evaluator select an incorrect answer?**
- **What latency, token, and API overhead occurred?**
- **Where did collaboration help, have no effect, or hurt?**

---

## 🏗️ 2. Architectural Pipeline

```
                     ┌───────────────────────┐
                     │   USER BENCHMARK      │
                     └──────────┬────────────┘
                                │
        ┌───────────────────────┴───────────────────────┐
        ▼                                               ▼
┌───────────────────────────────┐     ┌───────────────────────────────────┐
│     SINGLE-AGENT BASELINE     │     │        MULTI-AGENT PIPELINE       │
│  (Direct Zero-Shot Generation)│     │                                   │
└───────────────┬───────────────┘     │  ┌─────────────────────────────┐  │
                │                     │  │ Agent A: First-Principles   │  │
                │                     │  └──────────────┬──────────────┘  │
                │                     │                 │                 │
                │                     │  ┌──────────────┴──────────────┐  │
                │                     │  │ Agent B: Adversarial Bounds │  │
                │                     │  └──────────────┬──────────────┘  │
                │                     │                 │                 │
                │                     │  ┌──────────────▼──────────────┐  │
                │                     │  │      GEMMA 4 EVALUATOR      │  │
                │                     │  │ (Comparative JSON Arbiter)  │  │
                │                     │  └──────────────┬──────────────┘  │
                │                     └─────────────────┼─────────────────┘
                │                                       │
                └───────────────────┬───────────────────┘
                                    │
                                    ▼
                 ┌──────────────────────────────────────┐
                 │    INDEPENDENT VERIFICATION HARNESS   │
                 │ (AST Audited, Deterministic Sandbox) │
                 └──────────────────┬───────────────────┘
                                    │
                                    ▼
                 ┌──────────────────────────────────────┐
                 │       EIGHT RELIABILITY REPORT       │
                 │ (Pass Rates, Disagreements, Latency) │
                 └──────────────────────────────────────┘
```

> **Critical Architectural Note:** Different prompts invoking the same underlying model do not constitute independent models; they represent prompt-divergent strategies testing the model's sensitivity to framing and adversarial boundaries.

---

## 🧪 3. Reproducible Benchmark Tasks

EIGHT includes 8 curated algorithmic tasks spanning diverse failure surfaces:

| Task ID | Title | Category | Difficulty | Architectural Trap Tested |
| :--- | :--- | :--- | :--- | :--- |
| **TASK-01** | Stable Deduplication | List Operations | Easy | `list(set(x))` loses insertion order |
| **TASK-02** | Bracket Matcher with Quotes | String Processing | Medium | Quoted brackets (`"["`) must be ignored |
| **TASK-03** | Max Stock Profit with Cooldown | Numeric / DP | Hard | Greedy trading fails on cooldown transitions |
| **TASK-04** | Deep Key Flattener | Data Structures | Medium | Truthy `if val:` strips `None`, `False`, and `0` |
| **TASK-05** | Exact Currency Splitter | Numeric / Bounds | Medium | Float division induces IEEE-754 penny drift |
| **TASK-06** | Sliding Window Maximum | Boundary Cases | Medium | Off-by-one errors when $k=1$ or $k=N$ |
| **TASK-07** | Strict Roman Numeral Parser | Boundary Cases | Hard | Naive accumulators accept illegal tokens (`IIII`, `IC`) |
| **TASK-08** | Run-Length String Encoder | String Processing | Easy | Appending `1` to singles (`A1`) expands short text |

---

## 🚀 4. Windows Quickstart & Run Instructions

### Step 1: Clone or Navigate to Directory
```powershell
cd C:\Users\shiva\Downloads\eight
```

### Step 2: Install Dependencies
```powershell
python -m pip install -r requirements.txt
```

### Step 3: Run Unit & Verification Tests
```powershell
python -m pytest -v
```
*(All 15 verification, benchmark, metrics, and security tests must pass).*

### Step 4: Configure Credentials (Optional)
If you have a Google Gemini / Gemma API key:
```powershell
copy .env.example .env
# Edit .env with your GEMINI_API_KEY
```
*Note: If no API key is provided, EIGHT automatically starts in **High-Fidelity Simulation Mock Mode** with full transparency. You can also input a key directly in the UI sidebar.*

### Step 5: Launch the Streamlit Dashboard
```powershell
python -m streamlit run app.py
```
Open your browser to `http://localhost:8501`.

---

## 🛡️ 5. Security & Verification Engine

1. **Restricted AST Execution:** Model-generated Python functions are statically parsed using Python's `ast` module before execution.
2. **Prohibited Operations:** Direct imports of `os`, `sys`, `subprocess`, calls to `eval()`, `exec()`, `open()`, and dunder attribute traversals (`__class__`, `__subclasses__`) are blocked.
3. **Safe Execution Sandbox:** Executions run inside an isolated namespace with safe builtins (`range`, `len`, `enumerate`, `reversed`, etc.).
4. **Resilience:** Syntax errors, infinite loops, and exceptions in candidate outputs are caught gracefully and recorded as failed test assertions without crashing the application.

---

## 🎬 6. Live Demo Script for Judges

1. **Launch App:** Open `http://localhost:8501`.
2. **Examine Overview:** Show the dark engineering theme, Gemma 4 configuration, and the architecture diagram.
3. **Run Batch Evaluation:** Click **"Run All 8 Benchmarks"** in the sidebar. Watch the live progress bar evaluate tasks in real-time.
4. **Inspect Agent Arena (TASK-01):**
   - Baseline used `list(set(items))` which collapses duplicates but scrambles order.
   - Agent A and Agent B used order-preserving structures.
   - Evaluator selected Agent B.
5. **Inspect Evaluator Report (TASK-07):**
   - See how Gemma 4 identified that Agent A's Roman parser failed to reject `'IIII'` or `'IC'`, picking Agent B's canonical round-trip validator.
6. **Inspect Verification Center:**
   - Review ground truth test case breakdown showing exact inputs, expected values, actual outputs, and edge case tags.
7. **Examine Reliability Analytics:**
   - Observe the **Pass Rate Delta** (Multi-Agent vs Baseline).
   - Review the trade-off cards: Multi-agent achieves higher accuracy but incurs $3.5\times$ latency and $4\times$ API calls.
8. **Inspect Failure Inspector:**
   - Review forensic audit of tasks where single-agent failed, with AI-generated root-cause hypotheses backed by deterministic evidence.

---

## 📊 7. Reliability Metrics & Trade-offs

- **Pass Rate:** Clear denominator over total benchmark tasks (e.g., $7/8 = 87.5\%$).
- **Collaboration Outcomes:**
  - **Helped:** Multi-Agent Passed, Baseline Failed.
  - **No Effect:** Both Passed or Both Failed.
  - **Hurt:** Baseline Passed, Multi-Agent Failed (over-engineering / evaluator misjudgment).
- **Latency & Tokens:** Explicit tracking per agent role and evaluator call.

---

## 🔒 8. License & Credits

Built for the **Google Gemma Hackathon** (Best Use of Gemma 4).
Released under the MIT License.
