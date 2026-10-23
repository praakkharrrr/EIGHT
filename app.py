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
from src.charts import (
    create_task_comparison_chart,
    create_collaboration_donut,
    create_latency_comparison_chart
)

# Configure Streamlit page
st.set_page_config(
    page_title="EIGHT — AI Crash-Test Lab",
    page_icon="♾️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject modern styling & typography
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Initialize Benchmark Manager
benchmark_manager = BenchmarkManager()
tasks = benchmark_manager.get_all_tasks()
task_map = {t.task_id: t for t in tasks}

# Helper to run full evaluation suite
def evaluate_all_tasks(client_inst: GemmaClient) -> dict:
    results = {}
    agent_runner = AgentRunner(client_inst)
    evaluator_runner = EvaluatorRunner(client_inst)
    for task in tasks:
        base_out = agent_runner.run_baseline(task)
        a_out = agent_runner.run_agent_a(task)
        b_out = agent_runner.run_agent_b(task)
        eval_dec = evaluator_runner.evaluate_candidates(task, a_out, b_out)
        
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
        results[task.task_id] = eval_res
    return results

# Initialize session state
if "evaluation_results" not in st.session_state:
    # Auto-load initial simulation so the dashboard is immediately populated and settled
    default_client = GemmaClient(force_mock=True)
    st.session_state.evaluation_results = evaluate_all_tasks(default_client)

if "last_connectivity_status" not in st.session_state:
    st.session_state.last_connectivity_status = None

# ---------------------------------------------------------
# SIDEBAR: Engine Settings & Controls
# ---------------------------------------------------------
with st.sidebar:
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid rgba(255,255,255,0.08);">
            {BRAND_SVG}
            <div>
                <div style="font-size: 20px; font-weight: 800; color: #FFFFFF; letter-spacing: -0.02em;">EIGHT</div>
                <div style="font-size: 11px; color: #38BDF8; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase;">AI Crash-Test Lab</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("#### ⚙️ Engine Configuration")
    
    selected_model = st.selectbox(
        "Gemma Model Identifier",
        options=Config.SUPPORTED_MODELS,
        index=0,
        help="Selected model configuration for Baseline, Agent A, Agent B, and Evaluator."
    )
    
    runtime_api_key = st.text_input(
        "Gemini / Gemma API Key",
        value=Config.API_KEY or "",
        type="password",
        help="API Key is stored only in session RAM. Never logged or committed."
    )
    
    use_mock = st.toggle(
        "Simulation Mock Mode",
        value=not Config.is_api_configured(runtime_api_key),
        help="Runs realistic, deterministic simulations of agent failure modes and evaluator decisions without consuming API quotas."
    )
    
    client = GemmaClient(
        api_key=runtime_api_key,
        model_name=selected_model,
        force_mock=use_mock
    )
    
    col_ping, col_reset = st.columns([1, 1])
    with col_ping:
        if st.button("📡 Ping Model", use_container_width=True):
            with st.spinner("Connecting..."):
                success, msg = client.test_connectivity()
                st.session_state.last_connectivity_status = (success, msg)
    with col_reset:
        if st.button("🧹 Reset Data", use_container_width=True):
            st.session_state.evaluation_results.clear()
            st.rerun()
                
    if st.session_state.last_connectivity_status:
        success, msg = st.session_state.last_connectivity_status
        if success:
            st.success(msg)
        else:
            st.info(msg)

    st.markdown("---")
    st.markdown("#### ⚡ Batch Evaluation")
    if st.button("🚀 Re-Run All 8 Benchmarks", use_container_width=True, type="primary"):
        with st.status("Executing full benchmark crash-test suite...", expanded=True) as status_box:
            progress_bar = st.progress(0)
            agent_runner = AgentRunner(client)
            evaluator_runner = EvaluatorRunner(client)
            
            for idx, task in enumerate(tasks):
                status_box.write(f"Testing **{task.task_id}**: {task.title}...")
                progress_bar.progress((idx + 1) / len(tasks))
                
                base_out = agent_runner.run_baseline(task)
                a_out = agent_runner.run_agent_a(task)
                b_out = agent_runner.run_agent_b(task)
                eval_dec = evaluator_runner.evaluate_candidates(task, a_out, b_out)
                
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
                
            status_box.update(label="All 8 benchmarks successfully evaluated!", state="complete", expanded=False)
            st.success(f"Updated evaluations for {len(tasks)} tasks.")
            st.rerun()

    st.markdown(
        """
        <div style="font-size: 11.5px; color: #64748B; margin-top: 30px; text-align: center;">
            EIGHT v1.0.0 • Hackathon Edition<br>
            Category: Best Use of Gemma 4
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------------------------------------------------------
# TOP HERO HEADER
# ---------------------------------------------------------
mode_pill = (
    '<span class="badge-mock"><span class="pulse-dot-amber"></span>SIMULATION MOCK MODE</span>'
    if client.is_mock_mode
    else f'<span class="badge-real-api"><span class="pulse-dot-green"></span>LIVE API: {selected_model}</span>'
)

st.markdown(
    f"""
    <div class="eight-header">
        {BRAND_SVG}
        <div class="eight-title-group">
            <div class="eight-title-row">
                <h1 class="eight-main-title">EIGHT — AI CRASH-TEST LAB</h1>
                <div>{mode_pill}</div>
            </div>
            <div class="eight-tagline">"Don't trust the answer. Test the intelligence behind it."</div>
            <div class="stats-strip">
                <span class="stat-pill">🎯 <b>8 Curated Benchmarks</b></span>
                <span class="stat-pill">⚔️ <b>Single Baseline vs Multi-Agent</b></span>
                <span class="stat-pill">⚖️ <b>Gemma 4 Evaluator Arbiter</b></span>
                <span class="stat-pill">🛡️ <b>AST-Audited Deterministic Verification</b></span>
            </div>
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
        In modern AI engineering, **multi-agent architectures** are frequently assumed to be strictly superior to single-agent prompts.
        However, conversational agent loops often introduce token bloat, latency spikes, and collective hallucination without guaranteeing ground-truth correctness.

        **EIGHT** provides empirical, deterministic proof:
        We pit a **single-agent baseline** against a **collaborative multi-agent pipeline**, independently verify their candidate solutions in a secure AST-audited sandbox, and measure the real trade-offs between correctness, latency, and API costs.
        """
    )
    
    col_ov1, col_ov2, col_ov3 = st.columns(3)
    with col_ov1:
        st.markdown(
            """
            <div class="eight-card">
                <div class="eight-card-title">🎯 Baseline vs Collaboration</div>
                <p style="color: #94A3B8; font-size: 13.5px; line-height: 1.5; margin: 0;">
                    Does pitting an Analytical Engineer against an Adversarial Edge-Case Specialist and arbitrating with 
                    Gemma 4 actually yield higher code reliability than a direct zero-shot prompt?
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col_ov2:
        st.markdown(
            """
            <div class="eight-card">
                <div class="eight-card-title">🛡️ Deterministic Verification</div>
                <p style="color: #94A3B8; font-size: 13.5px; line-height: 1.5; margin: 0;">
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
                <p style="color: #94A3B8; font-size: 13.5px; line-height: 1.5; margin: 0;">
                    EIGHT flags evaluator misjudgments (cases where Gemma 4 chose an incorrect candidate), reports pass-rate deltas,
                    and quantifies the latency multiplier incurred by multi-agent orchestration.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("#### The 4-Stage Crash-Test Pipeline")
    
    c_s1, c_s2 = st.columns(2)
    with c_s1:
        st.markdown(
            """
            <div class="pipeline-step">
                <div class="step-num">1</div>
                <div>
                    <div class="step-body-title">Single-Agent Baseline</div>
                    <div class="step-body-desc">Direct zero-shot prompt given the task description. Fast and inexpensive, but prone to boundary edge-case traps.</div>
                </div>
            </div>
            <div class="pipeline-step">
                <div class="step-num">2</div>
                <div>
                    <div class="step-body-title">Dual Specialist Generation</div>
                    <div class="step-body-desc"><b>Agent A</b> (First-principles algorithmic focus) and <b>Agent B</b> (Adversarial boundary & edge-case focus) generate isolated candidate solutions.</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with c_s2:
        st.markdown(
            """
            <div class="pipeline-step">
                <div class="step-num">3</div>
                <div>
                    <div class="step-body-title">Gemma 4 Evaluator Arbitration</div>
                    <div class="step-body-desc">Gemma 4 performs comparative code review, pinpoints disagreements, identifies potential failure modes, and outputs a structured JSON verdict.</div>
                </div>
            </div>
            <div class="pipeline-step">
                <div class="step-num">4</div>
                <div>
                    <div class="step-body-title">Independent Sandboxed Verification</div>
                    <div class="step-body-desc">Every candidate and the evaluator choice are tested against deterministic assertions in an AST-audited sandbox. Ground truth is established.</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    eval_count = len(st.session_state.evaluation_results)
    st.markdown(
        f"""
        <div class="human-callout">
            💡 <b>Live Benchmark State:</b> <code>{eval_count} of {len(tasks)} tasks</code> evaluated in active session memory. 
            Navigate to <b>Evaluation Lab</b> to run single tasks, or <b>Reliability Analytics</b> to inspect pass rates and latency trade-offs.
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------------------------------------------------------
# TAB B: EVALUATION LAB
# ---------------------------------------------------------
with tab_lab:
    st.markdown("### 🧪 Evaluation Lab")
    st.markdown("Select an algorithmic benchmark task to inspect its specification and trigger the evaluation pipeline.")
    
    task_options = [f"{t.task_id} — {t.title} ({t.category.replace('_', ' ').title()})" for t in tasks]
    selected_option = st.selectbox(
        "Select Benchmark Task",
        options=task_options,
        index=0,
        help="Choose one of the 8 reproducible benchmark tasks."
    )
    current_task_id = selected_option.split(" — ")[0]
    current_task = task_map[current_task_id]
    
    diff_color = {
        "Easy": "#34D399",
        "Medium": "#FBBF24",
        "Hard": "#C084FC"
    }.get(current_task.difficulty, "#38BDF8")
    
    col_task_info1, col_task_info2 = st.columns([3, 2])
    with col_task_info1:
        st.markdown(
            f"""
            <div class="eight-card">
                <div class="eight-card-title">
                    <span>📋 {current_task.title}</span>
                    <span style="font-size: 11px; padding: 2px 8px; border-radius: 4px; background: rgba(255,255,255,0.06); color: {diff_color}; font-weight: 700;">
                        {current_task.difficulty}
                    </span>
                </div>
                <p style="font-size: 14px; color: #E2E8F0; line-height: 1.5;">{current_task.description}</p>
                <div style="font-size: 12.5px; color: #94A3B8; margin-top: 14px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.06);">
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
                <div class="eight-card-title" style="color: #F87171;">⚠️ Architectural Trap Tested</div>
                <p style="font-size: 13px; color: #CBD5E1; line-height: 1.5;">{current_task.expected_trap}</p>
                <div style="margin-top: 14px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.06); font-size: 12px; color: #38BDF8; font-weight: 600;">
                    🛡️ {len(current_task.test_cases)} Deterministic Test Assertions
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Action Row
    col_run_btn, col_run_note = st.columns([1, 2])
    with col_run_btn:
        run_single = st.button("🚀 Crash-Test This Task", type="primary", use_container_width=True)
    with col_run_note:
        st.caption("Executes Baseline, Agent A, Agent B, Gemma 4 Evaluator, and deterministic verification.")
        
    if run_single:
        with st.status(f"Evaluating {current_task.task_id}...", expanded=True) as status:
            agent_runner = AgentRunner(client)
            evaluator_runner = EvaluatorRunner(client)
            
            st.write("1. Running Single-Agent Zero-Shot Baseline...")
            base_out = agent_runner.run_baseline(current_task)
            
            st.write("2. Invoking Agent A (Algorithmic / First-Principles)...")
            a_out = agent_runner.run_agent_a(current_task)
            
            st.write("3. Invoking Agent B (Adversarial Boundary Specialist)...")
            b_out = agent_runner.run_agent_b(current_task)
            
            st.write("4. Arbitrating candidate code via Gemma 4 Evaluator...")
            eval_dec = evaluator_runner.evaluate_candidates(current_task, a_out, b_out)
            
            st.write("5. Executing deterministic test harness in AST sandbox...")
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

    # Quick Status Card if task evaluated
    if current_task_id in st.session_state.evaluation_results:
        res = st.session_state.evaluation_results[current_task_id]
        outcome_badge = {
            "Helped": '<span class="badge-helped">✅ Collaboration Helped</span>',
            "Hurt": '<span class="badge-hurt">❌ Collaboration Hurt</span>',
            "No Effect": '<span class="badge-no-effect">⚖️ No Effect (Equal)</span>',
            "Indeterminate": '<span class="badge-no-effect">❓ Indeterminate</span>'
        }.get(res.collaboration_outcome, '<span class="badge-no-effect">Equal</span>')
        
        st.markdown(
            f"""
            <div style="background: #111827; border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 14px 20px; margin-top: 15px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
                <div>
                    <span style="font-size: 13.5px; font-weight: 600; color: #F8FAFC;">Verification Outcome:</span> 
                    <span style="font-size: 13px; color: {'#34D399' if res.baseline_verification.all_passed else '#F87171'}; margin-left: 8px;">
                        Baseline: {'✅ Passed' if res.baseline_verification.all_passed else '❌ Failed'}
                    </span>
                    <span style="color: #64748B; margin: 0 8px;">|</span>
                    <span style="font-size: 13px; color: {'#34D399' if res.multi_agent_verification.all_passed else '#F87171'};">
                        Multi-Agent: {'✅ Passed' if res.multi_agent_verification.all_passed else '❌ Failed'}
                    </span>
                </div>
                <div>{outcome_badge}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

# ---------------------------------------------------------
# TAB C: AGENT ARENA
# ---------------------------------------------------------
with tab_arena:
    st.markdown("### ⚔️ Agent Arena")
    st.markdown("Side-by-side inspection of candidate strategies and prompt-divergence behaviors.")
    
    st.markdown(
        """
        <div class="human-callout">
            ⚠️ <b>Critical Architectural Note:</b> Different prompts using the same model do not constitute independent models; 
            they represent prompt-divergent strategies designed to probe the model's sensitivity to framing and adversarial boundaries.
        </div>
        """,
        unsafe_allow_html=True
    )
    
    eval_tasks = list(st.session_state.evaluation_results.keys())
    if not eval_tasks:
        st.info("No evaluations run yet.")
    else:
        selected_arena_id = st.selectbox("Inspect Task", options=eval_tasks, index=0, key="arena_task_select")
        res = st.session_state.evaluation_results[selected_arena_id]
        
        col_arena_b, col_arena_a, col_arena_b_role = st.columns(3)
        
        with col_arena_b:
            st.markdown(
                f"""
                <div class="agent-header-badge badge-baseline">
                    <span style="font-size: 18px;">🟣</span>
                    <div>
                        <div style="font-weight: 700; font-size: 14px;">Single-Agent Baseline</div>
                        <div style="font-size: 11.5px; opacity: 0.85;">Direct Zero-Shot Prompt</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.code(res.baseline_output.parsed_code or res.baseline_output.raw_response or "# No code generated", language="python")
            with st.expander("Strategy & Explanation"):
                st.caption(f"**Latency:** {res.baseline_output.latency_seconds:.2f}s | **Tokens:** {res.baseline_output.tokens_used}")
                st.write(res.baseline_output.explanation or "No explanation provided.")

        with col_arena_a:
            st.markdown(
                f"""
                <div class="agent-header-badge badge-agent-a">
                    <span style="font-size: 18px;">🔵</span>
                    <div>
                        <div style="font-weight: 700; font-size: 14px;">Agent A (Analytical)</div>
                        <div style="font-size: 11.5px; opacity: 0.85;">First-Principles & Complexity</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.code(res.agent_a_output.parsed_code or res.agent_a_output.raw_response or "# No code generated", language="python")
            with st.expander("Strategy & Explanation"):
                st.caption(f"**Latency:** {res.agent_a_output.latency_seconds:.2f}s | **Tokens:** {res.agent_a_output.tokens_used}")
                st.write(res.agent_a_output.explanation or "No explanation provided.")

        with col_arena_b_role:
            st.markdown(
                f"""
                <div class="agent-header-badge badge-agent-b">
                    <span style="font-size: 18px;">🟢</span>
                    <div>
                        <div style="font-weight: 700; font-size: 14px;">Agent B (Adversarial)</div>
                        <div style="font-size: 11.5px; opacity: 0.85;">Boundary & Edge-Case Specialist</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.code(res.agent_b_output.parsed_code or res.agent_b_output.raw_response or "# No code generated", language="python")
            with st.expander("Guarded Edge Cases & Explanation"):
                st.caption(f"**Latency:** {res.agent_b_output.latency_seconds:.2f}s | **Tokens:** {res.agent_b_output.tokens_used}")
                st.write(res.agent_b_output.explanation or "No explanation provided.")

        st.markdown("#### Disagreement & Strategy Analysis")
        if res.agent_disagreement:
            st.warning("⚠️ **Divergent Implementations:** Agent A and Agent B produced distinct algorithmic logic.")
            if res.evaluator_decision.identified_disagreements:
                for dis in res.evaluator_decision.identified_disagreements:
                    st.markdown(f"- 🔸 {dis}")
        else:
            st.info("ℹ️ **Convergent Implementations:** Agent A and Agent B arrived at equivalent code logic.")

# ---------------------------------------------------------
# TAB D: EVALUATOR REPORT
# ---------------------------------------------------------
with tab_eval:
    st.markdown("### ⚖️ Gemma 4 Evaluator Report")
    st.markdown("Structured code-review arbitration comparing Agent A and Agent B.")
    
    eval_tasks = list(st.session_state.evaluation_results.keys())
    if not eval_tasks:
        st.info("Run an evaluation to view the Evaluator Report.")
    else:
        selected_eval_id = st.selectbox("Inspect Task", options=eval_tasks, index=0, key="eval_task_select")
        res = st.session_state.evaluation_results[selected_eval_id]
        ev = res.evaluator_decision
        
        col_ev_main, col_ev_meta = st.columns([3, 2])
        with col_ev_main:
            st.markdown(
                f"""
                <div class="eight-card">
                    <div class="eight-card-title">
                        <span>🏆 Selected Candidate: <b>{ev.selected_agent}</b></span>
                    </div>
                    <p style="font-size: 14px; color: #E2E8F0; line-height: 1.6; margin: 0;">
                        {ev.rationale}
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            st.markdown("#### Flagged Failure Modes & Risks")
            if ev.potential_failure_modes:
                for mode in ev.potential_failure_modes:
                    st.markdown(f"- ⚠️ <span style='color: #FCA5A5;'>{mode}</span>", unsafe_allow_html=True)
            else:
                st.caption("No residual risks noted by evaluator.")

        with col_ev_meta:
            st.markdown(
                f"""
                <div class="eight-card">
                    <div class="eight-card-title">📊 Evaluator Metadata</div>
                    <div style="font-size: 13px; color: #94A3B8; line-height: 1.8;">
                        <b>Confidence Level:</b> <span style="color: #38BDF8; font-weight: 700;">{ev.confidence_score * 100:.1f}%</span><br>
                        <b>Arbitration Latency:</b> {ev.latency_seconds:.2f}s<br>
                        <b>Tokens Consumed:</b> {ev.tokens_used}<br>
                        <b>Execution Mode:</b> {'Simulated Mock' if ev.is_mock else 'Live Gemma 4 API'}<br>
                        <b>Schema Validation:</b> {'Error' if ev.error else 'Valid JSON Object'}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            with st.expander("Raw Evaluator JSON Response"):
                st.code(ev.raw_response, language="json")

        st.markdown(
            """
            <div class="human-callout">
                🛡️ <b>Verification Checkpoint:</b> Evaluator decisions reflect the model's judgment, which can still be flawed. 
                Proceed to the <b>Verification Center</b> to inspect how this candidate performed against deterministic assertions.
            </div>
            """,
            unsafe_allow_html=True
        )

# ---------------------------------------------------------
# TAB E: VERIFICATION CENTER
# ---------------------------------------------------------
with tab_verif:
    st.markdown("### 🛡️ Verification Center")
    st.markdown("Deterministic, sandboxed assertions establishing ground-truth correctness.")
    
    eval_tasks = list(st.session_state.evaluation_results.keys())
    if not eval_tasks:
        st.info("Run an evaluation to inspect verification outcomes.")
    else:
        selected_verif_id = st.selectbox("Inspect Task", options=eval_tasks, index=0, key="verif_task_select")
        res = st.session_state.evaluation_results[selected_verif_id]
        
        if res.evaluator_error_flag:
            st.error(
                "🚨 **EVALUATOR MISJUDGMENT DETECTED:** "
                f"The Gemma 4 Evaluator selected **{res.evaluator_decision.selected_agent}**, "
                "which FAILED deterministic verification despite alternative passing candidate availability."
            )
            
        c_v1, c_v2, c_v3, c_v4 = st.columns(4)
        
        with c_v1:
            vb = res.baseline_verification
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-value" style="color: {'#34D399' if vb.all_passed else '#F87171'};">
                        {vb.pass_count}/{vb.total_count}
                    </div>
                    <div class="kpi-label">Baseline Pass Count</div>
                    <div class="kpi-subtext">{'✅ 100% Passed' if vb.all_passed else '❌ Boundary Failure'}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with c_v2:
            va = res.agent_a_verification
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-value" style="color: {'#34D399' if va.all_passed else '#F87171'};">
                        {va.pass_count}/{va.total_count}
                    </div>
                    <div class="kpi-label">Agent A (Analytical)</div>
                    <div class="kpi-subtext">{'✅ 100% Passed' if va.all_passed else '❌ Boundary Failure'}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with c_v3:
            v_b = res.agent_b_verification
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-value" style="color: {'#34D399' if v_b.all_passed else '#F87171'};">
                        {v_b.pass_count}/{v_b.total_count}
                    </div>
                    <div class="kpi-label">Agent B (Adversarial)</div>
                    <div class="kpi-subtext">{'✅ 100% Passed' if v_b.all_passed else '❌ Boundary Failure'}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with c_v4:
            vm = res.multi_agent_verification
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-value" style="color: {'#34D399' if vm.all_passed else '#F87171'};">
                        {vm.pass_count}/{vm.total_count}
                    </div>
                    <div class="kpi-label">Multi-Agent Final</div>
                    <div class="kpi-subtext">{'✅ 100% Passed' if vm.all_passed else '❌ Boundary Failure'}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("#### Test Assertions Matrix (Evaluator Selection)")
        candidate_to_show = res.multi_agent_verification
        
        test_rows = []
        for t in candidate_to_show.test_results:
            test_rows.append({
                "Test Name": t.test_name,
                "Type": "🔥 Edge Case" if t.is_edge_case else "Standard",
                "Outcome": "✅ PASS" if t.passed else "❌ FAIL",
                "Input Arguments": t.input_repr,
                "Expected Output": t.expected_repr,
                "Candidate Output": t.actual_repr,
                "Diagnostics": t.error_message or "Verified exact match"
            })
            
        df_tests = pd.DataFrame(test_rows)
        st.dataframe(df_tests, use_container_width=True, hide_index=True)

# ---------------------------------------------------------
# TAB F: RELIABILITY ANALYTICS
# ---------------------------------------------------------
with tab_analytics:
    st.markdown("### 📈 Reliability Analytics")
    st.markdown("Aggregated empirical performance across all benchmark tasks.")
    
    all_results = list(st.session_state.evaluation_results.values())
    if not all_results:
        st.info("Run evaluations to view analytics.")
    else:
        summary: BenchmarkRunSummary = MetricsCalculator.aggregate_benchmark_runs(all_results)
        
        # Row 1: Key Performance Indicators
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-value">{summary.baseline_pass_rate * 100:.1f}%</div>
                    <div class="kpi-label">Single-Agent Pass Rate</div>
                    <div class="kpi-subtext">{summary.baseline_pass_count} of {summary.total_tasks_attempted} tasks verified</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with c2:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-value" style="color: #34D399;">{summary.multi_agent_pass_rate * 100:.1f}%</div>
                    <div class="kpi-label">Multi-Agent Pass Rate</div>
                    <div class="kpi-subtext">{summary.multi_agent_pass_count} of {summary.total_tasks_attempted} tasks verified</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with c3:
            delta_prefix = "+" if summary.pass_rate_delta > 0 else ""
            delta_color = "#34D399" if summary.pass_rate_delta > 0 else ("#F43F5E" if summary.pass_rate_delta < 0 else "#94A3B8")
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-value" style="color: {delta_color};">{delta_prefix}{summary.pass_rate_delta * 100:.1f}%</div>
                    <div class="kpi-label">Accuracy Delta</div>
                    <div class="kpi-subtext">Multi-Agent vs Baseline Net Gain</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with c4:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-value" style="color: #FBBF24;">{summary.evaluator_error_count}</div>
                    <div class="kpi-label">Evaluator Misjudgments</div>
                    <div class="kpi-subtext">Gemma 4 selected failing code</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("#### System Trade-offs: Latency, Cost, & Impact")
        
        # Row 2: Charts
        col_ch1, col_ch2 = st.columns([3, 2])
        with col_ch1:
            st.markdown("##### Task-by-Task Pass Rate Comparison")
            chart_tasks = create_task_comparison_chart(all_results)
            st.altair_chart(chart_tasks, use_container_width=True)
            
        with col_ch2:
            st.markdown("##### Collaboration Outcome Distribution")
            chart_donut = create_collaboration_donut(
                helped=summary.collaboration_helped_count,
                no_effect=summary.collaboration_no_effect_count,
                hurt=summary.collaboration_hurt_count
            )
            st.altair_chart(chart_donut, use_container_width=True)

        # Row 3: Trade-off Cards
        lat_ratio = (summary.avg_multi_agent_latency / summary.avg_baseline_latency) if summary.avg_baseline_latency > 0 else 1.0
        t1, t2, t3, t4 = st.columns(4)
        with t1:
            st.markdown(
                f"""
                <div class="eight-card">
                    <div style="font-size: 12px; color: #94A3B8; text-transform: uppercase; font-weight: 600;">Avg Baseline Latency</div>
                    <div style="font-size: 22px; font-weight: 800; color: #F8FAFC; margin-top: 4px;">{summary.avg_baseline_latency:.2f}s</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with t2:
            st.markdown(
                f"""
                <div class="eight-card">
                    <div style="font-size: 12px; color: #94A3B8; text-transform: uppercase; font-weight: 600;">Avg Multi-Agent Latency</div>
                    <div style="font-size: 22px; font-weight: 800; color: #38BDF8; margin-top: 4px;">{summary.avg_multi_agent_latency:.2f}s <span style="font-size: 13px; color: #FBBF24;">({lat_ratio:.1f}x slower)</span></div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with t3:
            st.markdown(
                f"""
                <div class="eight-card">
                    <div style="font-size: 12px; color: #94A3B8; text-transform: uppercase; font-weight: 600;">Total API Requests</div>
                    <div style="font-size: 22px; font-weight: 800; color: #F8FAFC; margin-top: 4px;">{summary.total_api_calls} calls <span style="font-size: 13px; color: #94A3B8;">(4x overhead)</span></div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with t4:
            st.markdown(
                f"""
                <div class="eight-card">
                    <div style="font-size: 12px; color: #94A3B8; text-transform: uppercase; font-weight: 600;">Total Tokens Processed</div>
                    <div style="font-size: 22px; font-weight: 800; color: #F8FAFC; margin-top: 4px;">{summary.total_tokens:,} tokens</div>
                </div>
                """,
                unsafe_allow_html=True
            )

# ---------------------------------------------------------
# TAB G: FAILURE INSPECTOR
# ---------------------------------------------------------
with tab_inspector:
    st.markdown("### 🔍 Failure Inspector")
    st.markdown("Forensic incident audit of edge-case bugs, evaluator oversights, and AI diagnostic hypotheses.")
    
    all_results = list(st.session_state.evaluation_results.values())
    failed_results = [
        r for r in all_results
        if not r.baseline_verification.all_passed or not r.multi_agent_verification.all_passed or r.evaluator_error_flag
    ]
    
    if not failed_results:
        st.success("🎉 No failure cases found among currently evaluated tasks!")
    else:
        fail_options = [f"{r.task.task_id} — {r.task.title}" for r in failed_results]
        selected_fail = st.selectbox("Select Incident to Audit", options=fail_options, index=0)
        fail_id = selected_fail.split(" — ")[0]
        f_res = st.session_state.evaluation_results[fail_id]
        
        st.markdown(
            f"""
            <div class="eight-card" style="border-left: 4px solid #F43F5E;">
                <div class="eight-card-title" style="color: #FB7185;">🚨 Incident Case File: {f_res.task.task_id} — {f_res.task.title}</div>
                <div style="font-size: 13.5px; color: #E2E8F0; line-height: 1.5; margin-bottom: 8px;">
                    <b>Task:</b> {f_res.task.description}
                </div>
                <div style="font-size: 13px; color: #FBBF24;">
                    <b>Root-Cause Trap:</b> {f_res.task.expected_trap}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        col_forensic1, col_forensic2 = st.columns(2)
        with col_forensic1:
            st.markdown("##### Evaluator Decision & Argument")
            st.markdown(
                f"""
                <div class="eight-card">
                    <b>Candidate Chosen:</b> {f_res.evaluator_decision.selected_agent}<br>
                    <b>Confidence:</b> {f_res.evaluator_decision.confidence_score * 100:.1f}%<br><br>
                    <div style="color: #CBD5E1; font-size: 13px; line-height: 1.5;">{f_res.evaluator_decision.rationale}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col_forensic2:
            st.markdown("##### Ground-Truth Deterministic Findings")
            if f_res.multi_agent_verification.all_passed:
                st.markdown(
                    """
                    <div class="eight-card" style="border-color: rgba(16, 185, 129, 0.3);">
                        <span style="color: #34D399; font-weight: 700;">✅ Multi-Agent Passed All Assertions</span><br>
                        <span style="font-size: 13px; color: #CBD5E1;">The collaborative pipeline correctly avoided the architectural trap that broke the baseline.</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                failed_tc = [t for t in f_res.multi_agent_verification.test_results if not t.passed]
                for ft in failed_tc:
                    st.error(f"❌ **{ft.test_name}**: Expected `{ft.expected_repr}`, but got `{ft.actual_repr}`")

        st.markdown("##### AI Root-Cause Diagnostic Hypothesis")
        st.markdown(
            f"""
            <div style="background: rgba(244, 63, 94, 0.08); border: 1px solid rgba(244, 63, 94, 0.25); border-radius: 10px; padding: 16px 20px;">
                <div style="font-size: 12px; font-weight: 700; color: #FB7185; text-transform: uppercase; letter-spacing: 0.05em;">AI Diagnostic Explanation</div>
                <div style="font-size: 13.5px; color: #FCA5A5; margin-top: 8px; line-height: 1.5;">
                    {f_res.failure_hypothesis or 'No failure hypothesis generated.'}
                </div>
                <div style="font-size: 11px; color: #94A3B8; margin-top: 10px; border-top: 1px solid rgba(244, 63, 94, 0.15); padding-top: 6px;">
                    *Independently validated against failed assertion traces in the deterministic sandbox.*
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
