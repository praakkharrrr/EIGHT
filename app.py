import streamlit as st
import pandas as pd
import json
import time
from typing import List, Optional

from src.config import Config
from src.schemas import BenchmarkTask, TaskEvaluationResult, BenchmarkRunSummary
from src.benchmark import BenchmarkManager
from src.gemma_client import GemmaClient
from src.agents import AgentRunner
from src.evaluator import EvaluatorRunner
from src.verification import VerificationEngine
from src.metrics import MetricsCalculator
from src.styles import CUSTOM_CSS, BRAND_SVG

# Configure Streamlit page
st.set_page_config(
    page_title="EIGHT — AI Crash-Test Lab",
    page_icon="♾️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply custom dark engineering theme
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Initialize session state for persistent evaluation results
if "evaluation_results" not in st.session_state:
    st.session_state.evaluation_results = {}  # task_id -> TaskEvaluationResult
if "current_task_id" not in st.session_state:
    st.session_state.current_task_id = "TASK-01"
if "last_connectivity_status" not in st.session_state:
    st.session_state.last_connectivity_status = None

# Initialize Benchmark Manager
benchmark_manager = BenchmarkManager()
tasks = benchmark_manager.get_all_tasks()
task_map = {t.task_id: t for t in tasks}

# ---------------------------------------------------------
# SIDEBAR: Configuration, Credentials, and Connectivity
# ---------------------------------------------------------
with st.sidebar:
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 20px;">
            {BRAND_SVG}
            <div>
                <div style="font-size: 20px; font-weight: 800; color: #FFFFFF; letter-spacing: 0.05em;">EIGHT</div>
                <div style="font-size: 11px; color: #38BDF8; font-weight: 600;">AI CRASH-TEST LAB</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("### ⚙️ Engine Settings")
    
    selected_model = st.selectbox(
        "Gemma Model Identifier",
        options=Config.SUPPORTED_MODELS,
        index=0,
        help="Target model for Baseline, Agent A, Agent B, and Evaluator."
    )
    
    runtime_api_key = st.text_input(
        "Gemini / Gemma API Key",
        value=Config.API_KEY or "",
        type="password",
        help="Stored only in session memory. Never exposed in logs or commits."
    )
    
    use_mock = st.toggle(
        "Simulated Mock Mode",
        value=not Config.is_api_configured(runtime_api_key),
        help="Run deterministic, high-fidelity simulations of agent failure modes and evaluator decisions without API calls."
    )
    
    # Initialize client with current configurations
    client = GemmaClient(
        api_key=runtime_api_key,
        model_name=selected_model,
        force_mock=use_mock
    )
    
    # Connectivity Check Button
    col_conn1, col_conn2 = st.columns([1, 1])
    with col_conn1:
        if st.button("Ping Model", use_container_width=True):
            with st.spinner("Testing connectivity..."):
                success, msg = client.test_connectivity()
                st.session_state.last_connectivity_status = (success, msg)
                
    if st.session_state.last_connectivity_status:
        success, msg = st.session_state.last_connectivity_status
        if success:
            st.success(msg)
        else:
            st.info(msg)

    st.markdown("---")
    st.markdown("### 🚀 Batch Benchmark")
    if st.button("Run All 8 Benchmarks", use_container_width=True, type="primary"):
        progress_bar = st.progress(0, text="Starting full benchmark evaluation...")
        agent_runner = AgentRunner(client)
        evaluator_runner = EvaluatorRunner(client)
        
        for idx, task in enumerate(tasks):
            progress_bar.progress((idx + 1) / len(tasks), text=f"Evaluating {task.task_id}: {task.title}...")
            # Pipeline execution
            base_out = agent_runner.run_baseline(task)
            a_out = agent_runner.run_agent_a(task)
            b_out = agent_runner.run_agent_b(task)
            eval_dec = evaluator_runner.evaluate_candidates(task, a_out, b_out)
            
            # Independent verification
            v_base = VerificationEngine.verify_candidate(task, base_out, "Baseline")
            v_a = VerificationEngine.verify_candidate(task, a_out, "Agent A")
            v_b = VerificationEngine.verify_candidate(task, b_out, "Agent B")
            
            eval_res = MetricsCalculator.evaluate_task_result(
                task=task,
                baseline_output=base_out,
                agent_a_output=a_out,
                agent_b_output=b_out,
                evaluator_decision=eval_dec,
                baseline_verification=v_base,
                agent_a_verification=v_a,
                agent_b_verification=v_b
            )
            st.session_state.evaluation_results[task.task_id] = eval_res
        
        progress_bar.empty()
        st.success(f"Evaluated all {len(tasks)} benchmark tasks!")
        st.rerun()

    if st.session_state.evaluation_results:
        if st.button("Clear Results", use_container_width=True):
            st.session_state.evaluation_results.clear()
            st.rerun()

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
mode_badge = (
    '<span class="badge-mock">⚠️ SIMULATION MOCK MODE</span>'
    if client.is_mock_mode
    else f'<span class="badge-real-api">⚡ REAL API: {selected_model}</span>'
)

st.markdown(
    f"""
    <div class="eight-header">
        {BRAND_SVG}
        <div style="flex-grow: 1;">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <h1 class="eight-title">EIGHT — AI CRASH-TEST LAB</h1>
                <div>{mode_badge}</div>
            </div>
            <div class="eight-tagline">"Don't trust the answer. Test the intelligence behind it."</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# NAVIGATION TABS
# ---------------------------------------------------------
tab_overview, tab_lab, tab_arena, tab_eval, tab_verif, tab_analytics, tab_inspector = st.tabs([
    "📊 Overview",
    "🧪 Evaluation Lab",
    "⚔️ Agent Arena",
    "⚖️ Evaluator Report",
    "🛡️ Verification Center",
    "📈 Reliability Analytics",
    "🔍 Failure Inspector",
])

# ---------------------------------------------------------
# TAB A: OVERVIEW
# ---------------------------------------------------------
with tab_overview:
    st.markdown(
        """
        ### The AI Reliability Challenge
        Multi-agent architectures are frequently hyped as universally superior to single-agent prompts.
        **EIGHT** provides empirical, deterministic evidence rather than vibes or conversational illusions.
        """
    )
    
    col_ov1, col_ov2, col_ov3 = st.columns(3)
    with col_ov1:
        st.markdown(
            """
            <div class="eight-card">
                <div class="eight-card-title">🎯 Baseline vs Collaboration</div>
                <p style="color: #94A3B8; font-size: 13px;">
                    We pit a single-agent zero-shot baseline directly against a collaborative multi-agent pipeline 
                    (Analytical Specialist + Adversarial Boundary Specialist + Gemma 4 Evaluator) on identical tasks.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col_ov2:
        st.markdown(
            """
            <div class="eight-card">
                <div class="eight-card-title">🛡️ Deterministic Ground Truth</div>
                <p style="color: #94A3B8; font-size: 13px;">
                    No LLM self-grading or circular trust loops. Candidate outputs are passed through an isolated,
                    deterministic test harness checking boundary values, data integrity, and strict algorithmic assertions.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col_ov3:
        st.markdown(
            """
            <div class="eight-card">
                <div class="eight-card-title">🚨 Failure & Trade-off Auditing</div>
                <p style="color: #94A3B8; font-size: 13px;">
                    EIGHT tracks where collaboration helped, where it made no difference, and where the evaluator picked
                    an incorrect answer — exposing latency and token overhead trade-offs.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("#### Evaluation Pipeline Architecture")
    st.code(
        """
[ USER TASK ] ───────────► 1. SINGLE-AGENT BASELINE (Zero-Shot Direct)
       │
       ├────────────────► 2. AGENT A (First-Principles / Complexity Specialist)
       │                        ▲
       ├────────────────► 3. AGENT B (Adversarial Boundary & Edge-Case Specialist)
       │                        ▼
       └────────────────► 4. GEMMA 4 EVALUATOR (Comparative Analysis & Selection)
                                │
                                ▼
                         5. INDEPENDENT VERIFICATION ENGINE (Deterministic Sandboxed Tests)
                                │
                                ▼
                         6. RELIABILITY REPORT (Pass-Rates, Latency, & Failure Inspector)
        """,
        language="text"
    )

    eval_count = len(st.session_state.evaluation_results)
    st.markdown(f"**Current Evaluation Status:** `{eval_count} of {len(tasks)} benchmark tasks evaluated.`")
    if eval_count == 0:
        st.info("💡 To start, head to **Evaluation Lab** to run an individual task, or click **Run All 8 Benchmarks** in the sidebar.")
    else:
        st.success(f"Active evaluation results stored in memory for {eval_count} tasks. Explore the tabs above to inspect agents, verdicts, and analytics.")

# ---------------------------------------------------------
# TAB B: EVALUATION LAB
# ---------------------------------------------------------
with tab_lab:
    st.markdown("### 🧪 Evaluation Lab")
    st.markdown("Select a reproducible benchmark task and execute the evaluation pipeline.")
    
    task_options = [f"{t.task_id} — {t.title} ({t.category}, {t.difficulty})" for t in tasks]
    selected_option = st.selectbox(
        "Select Benchmark Task",
        options=task_options,
        index=0
    )
    current_task_id = selected_option.split(" — ")[0]
    current_task = task_map[current_task_id]
    
    col_task_info1, col_task_info2 = st.columns([2, 1])
    with col_task_info1:
        st.markdown(
            f"""
            <div class="eight-card">
                <div class="eight-card-title">📋 Task Specification: {current_task.title}</div>
                <p style="font-size: 14px; color: #E2E8F0;">{current_task.description}</p>
                <div style="font-size: 13px; color: #94A3B8; margin-top: 10px;">
                    <b>Input:</b> <code>{current_task.input_spec}</code><br>
                    <b>Output:</b> <code>{current_task.output_spec}</code>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col_task_info2:
        st.markdown(
            f"""
            <div class="eight-card">
                <div class="eight-card-title">⚠️ Common Trap & Verification Criteria</div>
                <p style="font-size: 13px; color: #F87171;">{current_task.expected_trap}</p>
                <div style="margin-top: 8px; font-size: 12px; color: #38BDF8;">
                    <b>Deterministic Test Cases:</b> {len(current_task.test_cases)} assertions
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Execution Action
    col_run_btn, col_run_status = st.columns([1, 3])
    with col_run_btn:
        run_single = st.button("🚀 Run Evaluation on This Task", type="primary", use_container_width=True)
        
    if run_single:
        with st.status(f"Executing evaluation pipeline for {current_task.task_id}...", expanded=True) as status:
            agent_runner = AgentRunner(client)
            evaluator_runner = EvaluatorRunner(client)
            
            st.write("1. Running Single-Agent Baseline...")
            base_out = agent_runner.run_baseline(current_task)
            
            st.write("2. Running Agent A (First-Principles Strategy)...")
            a_out = agent_runner.run_agent_a(current_task)
            
            st.write("3. Running Agent B (Adversarial Boundary Strategy)...")
            b_out = agent_runner.run_agent_b(current_task)
            
            st.write("4. Invoking Gemma 4 Evaluator for comparative arbitration...")
            eval_dec = evaluator_runner.evaluate_candidates(current_task, a_out, b_out)
            
            st.write("5. Executing deterministic verification harness...")
            v_base = VerificationEngine.verify_candidate(current_task, base_out, "Baseline")
            v_a = VerificationEngine.verify_candidate(current_task, a_out, "Agent A")
            v_b = VerificationEngine.verify_candidate(current_task, b_out, "Agent B")
            
            eval_res = MetricsCalculator.evaluate_task_result(
                task=current_task,
                baseline_output=base_out,
                agent_a_output=a_out,
                agent_b_output=b_out,
                evaluator_decision=eval_dec,
                baseline_verification=v_base,
                agent_a_verification=v_a,
                agent_b_verification=v_b
            )
            st.session_state.evaluation_results[current_task.task_id] = eval_res
            status.update(label=f"Completed {current_task.task_id} evaluation!", state="complete", expanded=False)
            st.rerun()

    # If this task has an active evaluation result, display quick status summary
    if current_task_id in st.session_state.evaluation_results:
        res = st.session_state.evaluation_results[current_task_id]
        outcome_color = {
            "Helped": "badge-helped",
            "Hurt": "badge-hurt",
            "No Effect": "badge-no-effect",
            "Indeterminate": "badge-no-effect"
        }.get(res.collaboration_outcome, "badge-no-effect")
        
        st.markdown(
            f"""
            <div style="background: #1E293B; border: 1px solid rgba(56,189,248,0.2); border-radius: 8px; padding: 12px 18px; margin-top: 15px; display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <b>Result for {res.task.task_id}:</b> 
                    Baseline: {'✅ Passed' if res.baseline_verification.all_passed else '❌ Failed'} | 
                    Multi-Agent: {'✅ Passed' if res.multi_agent_verification.all_passed else '❌ Failed'}
                </div>
                <div>
                    <span class="{outcome_color}">Collaboration: {res.collaboration_outcome}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

# ---------------------------------------------------------
# TAB C: AGENT ARENA
# ---------------------------------------------------------
with tab_arena:
    st.markdown("### ⚔️ Agent Arena")
    st.markdown(
        """
        *Inspection of candidate strategies.* 
        > **Critical Architectural Note:** Different prompts using the same model do not constitute independent models; 
        > they represent prompt-divergent strategies testing the model's sensitivity to framing and adversarial instructions.
        """
    )
    
    eval_tasks = list(st.session_state.evaluation_results.keys())
    if not eval_tasks:
        st.info("No evaluations run yet. Run a task in the **Evaluation Lab** or click **Run All 8 Benchmarks** in the sidebar.")
    else:
        selected_arena_id = st.selectbox("Inspect Task", options=eval_tasks, index=0, key="arena_task_select")
        res = st.session_state.evaluation_results[selected_arena_id]
        
        col_arena_b, col_arena_a, col_arena_b_role = st.columns(3)
        
        with col_arena_b:
            st.markdown(
                f"""
                <div class="eight-card">
                    <div class="eight-card-title">🤖 Single-Agent Baseline</div>
                    <div style="font-size: 12px; color: #94A3B8; margin-bottom: 8px;">
                        <b>Strategy:</b> {res.baseline_output.strategy_name}<br>
                        <b>Latency:</b> {res.baseline_output.latency_seconds:.2f}s | <b>Tokens:</b> {res.baseline_output.tokens_used}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.code(res.baseline_output.parsed_code or res.baseline_output.raw_response or "No code", language="python")
            with st.expander("Explanation & Prompt"):
                st.caption(res.baseline_output.explanation)

        with col_arena_a:
            st.markdown(
                f"""
                <div class="eight-card">
                    <div class="eight-card-title">💡 Agent A (Analytical)</div>
                    <div style="font-size: 12px; color: #94A3B8; margin-bottom: 8px;">
                        <b>Strategy:</b> {res.agent_a_output.strategy_name}<br>
                        <b>Latency:</b> {res.agent_a_output.latency_seconds:.2f}s | <b>Tokens:</b> {res.agent_a_output.tokens_used}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.code(res.agent_a_output.parsed_code or res.agent_a_output.raw_response or "No code", language="python")
            with st.expander("Explanation & Strategy"):
                st.caption(res.agent_a_output.explanation)

        with col_arena_b_role:
            st.markdown(
                f"""
                <div class="eight-card">
                    <div class="eight-card-title">🛡️ Agent B (Adversarial)</div>
                    <div style="font-size: 12px; color: #94A3B8; margin-bottom: 8px;">
                        <b>Strategy:</b> {res.agent_b_output.strategy_name}<br>
                        <b>Latency:</b> {res.agent_b_output.latency_seconds:.2f}s | <b>Tokens:</b> {res.agent_b_output.tokens_used}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.code(res.agent_b_output.parsed_code or res.agent_b_output.raw_response or "No code", language="python")
            with st.expander("Explanation & Edge Cases"):
                st.caption(res.agent_b_output.explanation)

        st.markdown("#### Agent Disagreement Analysis")
        if res.agent_disagreement:
            st.warning(f"⚠️ **Disagreement Detected:** Agent A and Agent B produced distinct algorithmic implementations.")
            if res.evaluator_decision.identified_disagreements:
                for dis in res.evaluator_decision.identified_disagreements:
                    st.markdown(f"- {dis}")
        else:
            st.info("ℹ️ **Agreement:** Agent A and Agent B produced convergent implementations.")

# ---------------------------------------------------------
# TAB D: EVALUATOR REPORT
# ---------------------------------------------------------
with tab_eval:
    st.markdown("### ⚖️ Gemma 4 Evaluator Report")
    st.markdown("Structured arbitration output comparing Agent A and Agent B.")
    
    eval_tasks = list(st.session_state.evaluation_results.keys())
    if not eval_tasks:
        st.info("Run an evaluation to inspect the Evaluator Report.")
    else:
        selected_eval_id = st.selectbox("Inspect Evaluator Report for Task", options=eval_tasks, index=0, key="eval_task_select")
        res = st.session_state.evaluation_results[selected_eval_id]
        ev = res.evaluator_decision
        
        col_ev_left, col_ev_right = st.columns([2, 1])
        with col_ev_left:
            st.markdown(
                f"""
                <div class="eight-card">
                    <div class="eight-card-title">🏆 Evaluator Decision: {ev.selected_agent}</div>
                    <p style="font-size: 14px; color: #E2E8F0; line-height: 1.5;">{ev.rationale}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            st.markdown("#### Potential Failure Modes Flagged by Evaluator")
            if ev.potential_failure_modes:
                for mode in ev.potential_failure_modes:
                    st.markdown(f"- ⚠️ {mode}")
            else:
                st.caption("None reported.")
                
        with col_ev_right:
            st.markdown(
                f"""
                <div class="eight-card">
                    <div class="eight-card-title">📊 Decision Metadata</div>
                    <div style="font-size: 13px; color: #94A3B8;">
                        <b>Confidence Score:</b> <span style="color: #38BDF8; font-weight: 700;">{ev.confidence_score * 100:.1f}%</span><br>
                        <b>Latency:</b> {ev.latency_seconds:.2f}s<br>
                        <b>Tokens:</b> {ev.tokens_used}<br>
                        <b>Mode:</b> {'Simulated Mock' if ev.is_mock else 'Real API Call'}<br>
                        <b>Status:</b> {'Error' if ev.error else 'Valid JSON Schema'}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            with st.expander("Raw Evaluator JSON Response"):
                st.code(ev.raw_response, language="json")

        st.info(
            "🛡️ **Verification Safeguard:** The evaluator's selection is merely an AI hypothesis. "
            "Proceed to the **Verification Center** to see if this candidate passed deterministic ground-truth tests."
        )

# ---------------------------------------------------------
# TAB E: VERIFICATION CENTER
# ---------------------------------------------------------
with tab_verif:
    st.markdown("### 🛡️ Verification Center")
    st.markdown("Independent, deterministic ground truth checking. Model verdicts never replace verification.")
    
    eval_tasks = list(st.session_state.evaluation_results.keys())
    if not eval_tasks:
        st.info("Run an evaluation to view deterministic verification results.")
    else:
        selected_verif_id = st.selectbox("Inspect Verification for Task", options=eval_tasks, index=0, key="verif_task_select")
        res = st.session_state.evaluation_results[selected_verif_id]
        
        # Check for Evaluator Error
        if res.evaluator_error_flag:
            st.error(
                "🚨 **EVALUATOR MISJUDGMENT DETECTED!** "
                f"The Gemma 4 Evaluator selected **{res.evaluator_decision.selected_agent}**, "
                "which FAILED independent verification despite alternative passing candidate availability."
            )
            
        col_v1, col_v2, col_v3, col_v4 = st.columns(4)
        
        with col_v1:
            vb = res.baseline_verification
            status_emoji = "✅ PASS" if vb.all_passed else "❌ FAIL"
            st.markdown(
                f"""
                <div class="metric-box">
                    <div class="metric-value" style="color: {'#10B981' if vb.all_passed else '#EF4444'};">{status_emoji}</div>
                    <div class="metric-label">Baseline ({vb.pass_count}/{vb.total_count})</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col_v2:
            va = res.agent_a_verification
            status_emoji = "✅ PASS" if va.all_passed else "❌ FAIL"
            st.markdown(
                f"""
                <div class="metric-box">
                    <div class="metric-value" style="color: {'#10B981' if va.all_passed else '#EF4444'};">{status_emoji}</div>
                    <div class="metric-label">Agent A ({va.pass_count}/{va.total_count})</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col_v3:
            vb_agent = res.agent_b_verification
            status_emoji = "✅ PASS" if vb_agent.all_passed else "❌ FAIL"
            st.markdown(
                f"""
                <div class="metric-box">
                    <div class="metric-value" style="color: {'#10B981' if vb_agent.all_passed else '#EF4444'};">{status_emoji}</div>
                    <div class="metric-label">Agent B ({vb_agent.pass_count}/{vb_agent.total_count})</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col_v4:
            vm = res.multi_agent_verification
            status_emoji = "✅ PASS" if vm.all_passed else "❌ FAIL"
            st.markdown(
                f"""
                <div class="metric-box">
                    <div class="metric-value" style="color: {'#10B981' if vm.all_passed else '#EF4444'};">{status_emoji}</div>
                    <div class="metric-label">Multi-Agent Final ({vm.pass_count}/{vm.total_count})</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("#### Test Case Breakdown (Evaluator's Selected Candidate)")
        candidate_to_show = res.multi_agent_verification
        
        test_rows = []
        for t in candidate_to_show.test_results:
            test_rows.append({
                "Test Name": t.test_name,
                "Edge Case?": "🔥 Yes" if t.is_edge_case else "No",
                "Status": "✅ Passed" if t.passed else "❌ Failed",
                "Input": t.input_repr,
                "Expected": t.expected_repr,
                "Actual": t.actual_repr,
                "Error": t.error_message or "-"
            })
            
        df_tests = pd.DataFrame(test_rows)
        st.dataframe(df_tests, use_container_width=True)

# ---------------------------------------------------------
# TAB F: RELIABILITY ANALYTICS
# ---------------------------------------------------------
with tab_analytics:
    st.markdown("### 📈 Reliability Analytics")
    st.markdown("Comprehensive comparative performance of Single-Agent vs Multi-Agent systems.")
    
    all_results = list(st.session_state.evaluation_results.values())
    if not all_results:
        st.info("Run evaluations to view reliability metrics.")
    else:
        summary: BenchmarkRunSummary = MetricsCalculator.aggregate_benchmark_runs(all_results)
        
        # Metric Cards Row 1
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(
                f"""
                <div class="metric-box">
                    <div class="metric-value">{summary.baseline_pass_rate * 100:.1f}%</div>
                    <div class="metric-label">Single-Agent Pass Rate ({summary.baseline_pass_count}/{summary.total_tasks_attempted})</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with c2:
            st.markdown(
                f"""
                <div class="metric-box">
                    <div class="metric-value" style="color: #34D399;">{summary.multi_agent_pass_rate * 100:.1f}%</div>
                    <div class="metric-label">Multi-Agent Pass Rate ({summary.multi_agent_pass_count}/{summary.total_tasks_attempted})</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with c3:
            delta_prefix = "+" if summary.pass_rate_delta > 0 else ""
            delta_color = "#34D399" if summary.pass_rate_delta > 0 else ("#EF4444" if summary.pass_rate_delta < 0 else "#94A3B8")
            st.markdown(
                f"""
                <div class="metric-box">
                    <div class="metric-value" style="color: {delta_color};">{delta_prefix}{summary.pass_rate_delta * 100:.1f}%</div>
                    <div class="metric-label">Accuracy Delta</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with c4:
            st.markdown(
                f"""
                <div class="metric-box">
                    <div class="metric-value" style="color: #FBBF24;">{summary.evaluator_error_count}</div>
                    <div class="metric-label">Evaluator Misjudgments</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Metric Cards Row 2: Trade-offs
        st.markdown("#### Performance Trade-Offs (Latency & Cost)")
        col_t1, col_t2, col_t3, col_t4 = st.columns(4)
        with col_t1:
            st.markdown(
                f"""
                <div class="eight-card">
                    <div style="font-size: 13px; color: #94A3B8;">Baseline Latency</div>
                    <div style="font-size: 20px; font-weight: 700; color: #F8FAFC;">{summary.avg_baseline_latency:.2f}s</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col_t2:
            latency_mult = (summary.avg_multi_agent_latency / summary.avg_baseline_latency) if summary.avg_baseline_latency > 0 else 1.0
            st.markdown(
                f"""
                <div class="eight-card">
                    <div style="font-size: 13px; color: #94A3B8;">Multi-Agent Latency</div>
                    <div style="font-size: 20px; font-weight: 700; color: #38BDF8;">{summary.avg_multi_agent_latency:.2f}s ({latency_mult:.1f}x)</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col_t3:
            st.markdown(
                f"""
                <div class="eight-card">
                    <div style="font-size: 13px; color: #94A3B8;">Total API Calls</div>
                    <div style="font-size: 20px; font-weight: 700; color: #F8FAFC;">{summary.total_api_calls} calls</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col_t4:
            st.markdown(
                f"""
                <div class="eight-card">
                    <div style="font-size: 13px; color: #94A3B8;">Total Token Usage</div>
                    <div style="font-size: 20px; font-weight: 700; color: #F8FAFC;">{summary.total_tokens:,} tokens</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Collaboration Outcome Distribution
        st.markdown("#### Collaboration Impact Distribution")
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            st.markdown(
                f"""
                <div class="metric-box">
                    <div class="metric-value" style="color: #10B981;">{summary.collaboration_helped_count}</div>
                    <div class="metric-label">Helped (Multi passed, Baseline failed)</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col_c2:
            st.markdown(
                f"""
                <div class="metric-box">
                    <div class="metric-value" style="color: #94A3B8;">{summary.collaboration_no_effect_count}</div>
                    <div class="metric-label">No Effect (Equal outcomes)</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col_c3:
            st.markdown(
                f"""
                <div class="metric-box">
                    <div class="metric-value" style="color: #EF4444;">{summary.collaboration_hurt_count}</div>
                    <div class="metric-label">Hurt (Baseline passed, Multi failed)</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Comparative Visualization
        st.markdown("#### Pass Rate Comparison")
        chart_data = pd.DataFrame({
            "Strategy": ["Single-Agent Baseline", "Multi-Agent Workflow"],
            "Verified Pass Rate (%)": [summary.baseline_pass_rate * 100, summary.multi_agent_pass_rate * 100]
        })
        st.bar_chart(chart_data.set_index("Strategy"), use_container_width=True)

# ---------------------------------------------------------
# TAB G: FAILURE INSPECTOR
# ---------------------------------------------------------
with tab_inspector:
    st.markdown("### 🔍 Failure Inspector")
    st.markdown("In-depth forensic audit of task failures, evaluator oversights, and AI failure hypotheses.")
    
    all_results = list(st.session_state.evaluation_results.values())
    failed_results = [
        r for r in all_results
        if not r.baseline_verification.all_passed or not r.multi_agent_verification.all_passed or r.evaluator_error_flag
    ]
    
    if not failed_results:
        st.success("🎉 No failure cases found among currently evaluated tasks! (Or no evaluations run yet).")
    else:
        fail_options = [f"{r.task.task_id} — {r.task.title}" for r in failed_results]
        selected_fail = st.selectbox("Select Failed Task to Inspect", options=fail_options, index=0)
        fail_id = selected_fail.split(" — ")[0]
        f_res = st.session_state.evaluation_results[fail_id]
        
        st.markdown(
            f"""
            <div class="eight-card" style="border-left: 4px solid #EF4444;">
                <div class="eight-card-title" style="color: #EF4444;">🚨 Failure Audit: {f_res.task.task_id} — {f_res.task.title}</div>
                <div style="font-size: 13px; color: #E2E8F0; margin-bottom: 8px;">
                    <b>Task Description:</b> {f_res.task.description}
                </div>
                <div style="font-size: 13px; color: #FBBF24;">
                    <b>Known Architectural Trap:</b> {f_res.task.expected_trap}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown("#### Forensic Breakdown")
        col_forensic1, col_forensic2 = st.columns(2)
        with col_forensic1:
            st.markdown("**Evaluator Decision & Rationale:**")
            st.info(f"**Selected:** {f_res.evaluator_decision.selected_agent}\n\n**Rationale:** {f_res.evaluator_decision.rationale}")
        with col_forensic2:
            st.markdown("**Deterministic Verification Evidence:**")
            if f_res.multi_agent_verification.all_passed:
                st.success("Multi-Agent candidate passed all deterministic assertions.")
            else:
                failed_tc = [t for t in f_res.multi_agent_verification.test_results if not t.passed]
                for ft in failed_tc:
                    st.error(f"❌ **{ft.test_name}**: Expected `{ft.expected_repr}`, got `{ft.actual_repr}`")

        st.markdown("#### AI Root-Cause Failure Hypothesis")
        st.markdown(
            f"""
            <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 8px; padding: 14px 18px;">
                <div style="font-size: 12px; font-weight: 700; color: #F87171; text-transform: uppercase;">AI-Generated Diagnostic Hypothesis</div>
                <div style="font-size: 14px; color: #FCA5A5; margin-top: 6px;">
                    {f_res.failure_hypothesis or 'No failure hypothesis generated.'}
                </div>
                <div style="font-size: 11px; color: #94A3B8; margin-top: 8px;">
                    *Note: This explanation is a model-derived diagnostic hypothesis, independently corroborated by failed test cases.*
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
