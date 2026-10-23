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
from src.styles import BRAND_SVG, MASTERCLASS_CSS
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

# Inject Masterclass UI styles (safe rendering with zero icon breakage)
st.html(MASTERCLASS_CSS)

# Initialize Benchmark Manager
benchmark_manager = BenchmarkManager()
tasks = benchmark_manager.get_all_tasks()
task_map = {t.task_id: t for t in tasks}

# Auto-populate simulation so user lands on a vibrant, populated dashboard
if "evaluation_results" not in st.session_state:
    default_client = GemmaClient(force_mock=True)
    agent_runner = AgentRunner(default_client)
    evaluator_runner = EvaluatorRunner(default_client)
    init_results = {}
    for t in tasks:
        base_out = agent_runner.run_baseline(t)
        a_out = agent_runner.run_agent_a(t)
        b_out = agent_runner.run_agent_b(t)
        eval_dec = evaluator_runner.evaluate_candidates(t, a_out, b_out)
        v_base = VerificationEngine.verify_candidate(t, base_out, "Baseline")
        v_a = VerificationEngine.verify_candidate(t, a_out, "Agent A")
        v_b = VerificationEngine.verify_candidate(t, b_out, "Agent B")
        eval_res = MetricsCalculator.evaluate_task_result(
            task=t,
            baseline_output=base_out,
            agent_a_output=a_out,
            agent_b_output=b_out,
            evaluator_decision=eval_dec,
            baseline_verification=v_base,
            agent_a_verification=v_a,
            agent_b_verification=v_b
        )
        init_results[t.task_id] = eval_res
    st.session_state.evaluation_results = init_results

if "last_connectivity_status" not in st.session_state:
    st.session_state.last_connectivity_status = None

if "available_models" not in st.session_state:
    st.session_state.available_models = list(Config.SUPPORTED_MODELS)

if "selected_model_index" not in st.session_state:
    st.session_state.selected_model_index = 0

# ---------------------------------------------------------
# SIDEBAR: Engine Settings & Fast Batch Runner
# ---------------------------------------------------------
with st.sidebar:
    st.html(f"""<div style="display: flex; align-items: center; gap: 14px; margin-bottom: 20px; padding-bottom: 14px; border-bottom: 1px solid rgba(255,255,255,0.08);">
        {BRAND_SVG}
        <div>
            <div style="font-size: 20px; font-weight: 800; color: #FFFFFF; letter-spacing: -0.02em;">EIGHT</div>
            <div style="font-size: 11px; color: #38BDF8; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase;">AI Crash-Test Lab</div>
        </div>
    </div>""")
    
    st.markdown("##### ⚙️ Engine Settings")
    st.caption("Target model and credentials.")
    
    # Prioritized model list
    model_options = [
        "gemma-4-26b-a4b-it",
        "gemma-4-31b-it",
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
    ]
    # Append any models discovered from the user's key
    for m in st.session_state.available_models:
        if m not in model_options:
            model_options.append(m)

    # Safe index
    curr_idx = min(st.session_state.selected_model_index, len(model_options) - 1)

    selected_model = st.selectbox(
        "Model Identifier",
        options=model_options,
        index=curr_idx,
        help="Target model for Baseline, Agent A, Agent B, and Gemma 4 Evaluator."
    )
    
    runtime_api_key = st.text_input(
        "Gemini / Gemma API Key",
        value=Config.API_KEY or "",
        type="password",
        help="Stored in session memory only. Never logged or committed."
    )
    
    use_mock = st.toggle(
        "Use Offline Simulator",
        value=not Config.is_api_configured(runtime_api_key),
        help="Runs realistic simulations of agent pitfalls and evaluator verdicts without consuming API quotas."
    )
    
    client = GemmaClient(
        api_key=runtime_api_key,
        model_name=selected_model,
        force_mock=use_mock
    )
    
    # Full-width clean buttons to prevent text truncation
    if st.button("📡 Test Connection", use_container_width=True):
        with st.spinner("Connecting..."):
            success, msg = client.test_connectivity()
            st.session_state.last_connectivity_status = (success, msg)
            st.rerun()

    if st.button("🔍 Auto-Detect Models on Key", use_container_width=True):
        with st.spinner("Discovering models on your key..."):
            discovered = client.list_available_models()
            st.session_state.available_models = discovered
            # Auto-select Gemma 4 if found!
            if "gemma-4-26b-a4b-it" in discovered:
                st.session_state.selected_model_index = discovered.index("gemma-4-26b-a4b-it")
            st.session_state.last_connectivity_status = (True, f"Discovered {len(discovered)} models! Auto-selected official Gemma 4.")
            st.rerun()
                
    if st.session_state.last_connectivity_status:
        success, msg = st.session_state.last_connectivity_status
        if success:
            st.success(msg)
        else:
            st.warning(msg)

    st.markdown("---")
    st.markdown("##### 🚀 Fast Batch Evaluation")
    if st.button("▶ Run All 8 Benchmarks", use_container_width=True, type="primary"):
        with st.status("Crash-testing all 8 benchmarks...", expanded=True) as status_box:
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
                
            status_box.update(label="All benchmarks evaluated!", state="complete", expanded=False)
            st.success(f"Evaluated {len(tasks)} benchmark tasks.")
            st.rerun()

    if st.button("🧹 Clear Results", use_container_width=True):
        st.session_state.evaluation_results.clear()
        st.rerun()

    st.html("""<div style="font-size: 11px; opacity: 0.6; margin-top: 24px; text-align: center;">
        EIGHT — AI Crash-Test Lab v1.0<br>
        Hackathon: Best Use of Gemma 4
    </div>""")

# ---------------------------------------------------------
# TOP HERO BANNER
# ---------------------------------------------------------
is_connected_live = (not client.is_mock_mode) and (st.session_state.last_connectivity_status and st.session_state.last_connectivity_status[0])

if client.is_mock_mode:
    mode_pill = '<span class="badge-mock"><span class="pulse-dot-amber"></span>OFFLINE SIMULATOR</span>'
elif is_connected_live:
    mode_pill = f'<span class="badge-real-api"><span class="pulse-dot-green"></span>LIVE: {selected_model}</span>'
else:
    mode_pill = f'<span class="badge-mock"><span class="pulse-dot-amber"></span>API READY: {selected_model}</span>'

st.html(f"""<div class="eight-header">
    {BRAND_SVG}
    <div class="eight-title-group">
        <div class="eight-title-row">
            <h1 class="eight-main-title">EIGHT — AI CRASH-TEST LAB</h1>
            <div>{mode_pill}</div>
        </div>
        <div class="eight-tagline">"Don't trust the answer. Test the intelligence behind it."</div>
        <div class="stats-strip">
            <span class="stat-pill">🎯 <b>8 Curated Benchmarks</b></span>
            <span class="stat-pill">⚔️ <b>1 Baseline vs 2 Specialists</b></span>
            <span class="stat-pill">⚖️ <b>Gemma 4 Evaluator Arbiter</b></span>
            <span class="stat-pill">🛡️ <b>AST Sandboxed Ground Truth</b></span>
        </div>
    </div>
</div>""")

# ---------------------------------------------------------
# NAVIGATION TABS (High Contrast & Perfectly Readable)
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
    st.markdown("""### 💡 The Big Question: Does Multi-Agent Collaboration Actually Help?
Everyone assumes that having multiple AI agents talk to each other automatically produces better code.
**EIGHT** was built to empirically test this assumption with deterministic proof.

We put AI-generated code through an **independent sandbox** to answer:
- **Did multi-agent collaboration actually outperform the single-agent baseline?**
- **Did the AI evaluator pick the wrong answer because of flawed reasoning?**
- **What was the cost in latency, tokens, and extra API calls?**
- **Where did collaboration help, where did it have no effect, and where did it hurt?**
""")

    col_ov1, col_ov2, col_ov3 = st.columns(3)
    with col_ov1:
        st.html("""<div class="eight-card">
            <div class="eight-card-title">🎯 Baseline vs Collaboration</div>
            <p style="font-size: 13.5px; color: #94A3B8; line-height: 1.5; margin: 0;">
                We pit a single-agent zero-shot baseline directly against a collaborative multi-agent pipeline 
                (Analytical Specialist + Edge-Case Specialist + Gemma 4 Judge).
            </p>
        </div>""")
    with col_ov2:
        st.html("""<div class="eight-card">
            <div class="eight-card-title">🛡️ Deterministic Ground Truth</div>
            <p style="font-size: 13.5px; color: #94A3B8; line-height: 1.5; margin: 0;">
                Zero AI self-grading loops. Every candidate function is tested in a sandboxed Python runner against strict boundary assertions.
            </p>
        </div>""")
    with col_ov3:
        st.html("""<div class="eight-card">
            <div class="eight-card-title">🚨 The Cost & Failure Audit</div>
            <p style="font-size: 13.5px; color: #94A3B8; line-height: 1.5; margin: 0;">
                We measure the trade-offs: multi-agent takes ~3.5x longer and 4x the API calls. We track where collaboration helped, did nothing, or backfired.
            </p>
        </div>""")

    st.markdown("#### How the 4-Stage Crash-Test Works")
    c_s1, c_s2 = st.columns(2)
    with c_s1:
        st.html("""<div class="pipeline-step">
            <div class="step-num">1</div>
            <div>
                <div class="step-body-title">Single-Agent Baseline (The Speedrunner)</div>
                <div class="step-body-desc">Generates code in a single prompt. Fast and cheap, but often trips on subtle boundary traps.</div>
            </div>
        </div>
        <div class="pipeline-step">
            <div class="step-num">2</div>
            <div>
                <div class="step-body-title">Dual Specialists: Agent A & Agent B</div>
                <div class="step-body-desc"><b>Agent A</b> designs optimal algorithms, while <b>Agent B</b> hunts for edge cases, nulls, and boundary conditions.</div>
            </div>
        </div>""")
    with c_s2:
        st.html("""<div class="pipeline-step">
            <div class="step-num">3</div>
            <div>
                <div class="step-body-title">Gemma 4 Evaluator (The Reviewer)</div>
                <div class="step-body-desc">Gemma 4 reviews both submissions, highlights disagreements, and issues a structured JSON verdict.</div>
            </div>
        </div>
        <div class="pipeline-step">
            <div class="step-num">4</div>
            <div>
                <div class="step-body-title">Independent Sandboxed Verification</div>
                <div class="step-body-desc">Deterministic test assertions run against all candidates to reveal whether Gemma's choice actually works.</div>
            </div>
        </div>""")

    eval_count = len(st.session_state.evaluation_results)
    st.html(f"""<div class="human-callout">
        <b>💡 Current Status:</b> <code>{eval_count} of {len(tasks)} tasks</code> evaluated in active memory. 
        Head to <b>Evaluation Lab</b> to run single tasks, or <b>Reliability Analytics</b> to view pass-rate charts and trade-offs.
    </div>""")

# ---------------------------------------------------------
# TAB B: EVALUATION LAB
# ---------------------------------------------------------
with tab_lab:
    st.markdown("### 🧪 Evaluation Lab")
    st.markdown("Select a benchmark challenge to inspect its specification, understand the trap, and trigger the crash test.")
    
    task_options = [f"{t.task_id} — {t.title} ({t.category.replace('_', ' ').title()})" for t in tasks]
    selected_option = st.selectbox("Choose Task to Test", options=task_options, index=0)
    current_task_id = selected_option.split(" — ")[0]
    current_task = task_map[current_task_id]
    
    diff_color = {
        "Easy": "#34D399",
        "Medium": "#FBBF24",
        "Hard": "#C084FC"
    }.get(current_task.difficulty, "#38BDF8")
    
    col_t1, col_t2 = st.columns([3, 2])
    with col_t1:
        st.html(f"""<div class="eight-card">
            <div class="eight-card-title">
                <span>📋 {current_task.title}</span>
                <span style="font-size: 11px; padding: 2px 8px; border-radius: 4px; background: rgba(255,255,255,0.06); color: {diff_color}; font-weight: 700;">
                    {current_task.difficulty}
                </span>
            </div>
            <p style="font-size: 14px; color: #E2E8F0; line-height: 1.5; margin: 0 0 12px 0;">{current_task.description}</p>
            <div style="font-size: 12.5px; color: #94A3B8; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.06);">
                <b>Inputs:</b> <code>{current_task.input_spec}</code><br>
                <b>Expected Output:</b> <code>{current_task.output_spec}</code>
            </div>
        </div>""")
    with col_t2:
        st.html(f"""<div class="eight-card">
            <div class="eight-card-title" style="color: #F87171;">⚠️ The Sneaky Trap</div>
            <p style="font-size: 13px; color: #CBD5E1; line-height: 1.5; margin: 0 0 12px 0;">{current_task.expected_trap}</p>
            <div style="font-size: 12px; color: #38BDF8; font-weight: 600; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.06);">
                🛡️ Tested with {len(current_task.test_cases)} strict assertions
            </div>
        </div>""")

    col_btn, col_info = st.columns([1, 2])
    with col_btn:
        run_single = st.button("🚀 Crash-Test This Task", type="primary", use_container_width=True)
    with col_info:
        st.caption("Executes Baseline, Agent A, Agent B, Gemma 4 Evaluator, and deterministic verification.")

    if run_single:
        with st.status(f"Evaluating {current_task.task_id}...", expanded=True) as status:
            agent_runner = AgentRunner(client)
            evaluator_runner = EvaluatorRunner(client)
            
            st.write("1. Running Baseline (Single prompt)...")
            base_out = agent_runner.run_baseline(current_task)
            
            st.write("2. Running Agent A (Algorithmic Specialist)...")
            a_out = agent_runner.run_agent_a(current_task)
            
            st.write("3. Running Agent B (Adversarial Edge-Case Specialist)...")
            b_out = agent_runner.run_agent_b(current_task)
            
            st.write("4. Invoking Gemma 4 Evaluator for comparative review...")
            eval_dec = evaluator_runner.evaluate_candidates(current_task, a_out, b_out)
            
            st.write("5. Executing deterministic test assertions in sandbox...")
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
            status.update(label=f"Done testing {current_task.task_id}!", state="complete", expanded=False)
            st.rerun()

    if current_task_id in st.session_state.evaluation_results:
        res = st.session_state.evaluation_results[current_task_id]
        outcome_color = {
            "Helped": "#10B981",
            "Hurt": "#EF4444",
            "No Effect": "#94A3B8",
            "Indeterminate": "#94A3B8"
        }.get(res.collaboration_outcome, "#94A3B8")
        
        st.html(f"""<div style="background: #111827; border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 14px 18px; margin-top: 15px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
                <b>Verification Result:</b>
                <span style="color: {'#10B981' if res.baseline_verification.all_passed else '#EF4444'}; margin-left: 8px;">
                    Baseline: {'✅ Passed' if res.baseline_verification.all_passed else '❌ Failed'}
                </span>
                <span style="opacity: 0.4; margin: 0 8px;">|</span>
                <span style="color: {'#10B981' if res.multi_agent_verification.all_passed else '#EF4444'};">
                    Multi-Agent Final: {'✅ Passed' if res.multi_agent_verification.all_passed else '❌ Failed'}
                </span>
            </div>
            <div>
                <span style="background: rgba(255,255,255,0.05); color: {outcome_color}; font-weight: 700; padding: 4px 12px; border-radius: 6px; font-size: 13px;">
                    Collaboration: {res.collaboration_outcome}
                </span>
            </div>
        </div>""")

# ---------------------------------------------------------
# TAB C: AGENT ARENA
# ---------------------------------------------------------
with tab_arena:
    st.markdown("### ⚔️ Agent Arena: Candidate Solutions")
    st.markdown("Inspect code from the Baseline, Agent A, and Agent B side-by-side.")
    
    st.html("""<div class="human-callout">
        <b>💡 Why 2 Agents?</b> Prompting the same model differently tests how sensitive it is to framing. 
        Agent A solves for clean code and performance, while Agent B specifically looks for empty inputs, negative values, and traps.
    </div>""")
    
    eval_tasks = list(st.session_state.evaluation_results.keys())
    if not eval_tasks:
        st.info("No evaluations run yet.")
    else:
        selected_arena_id = st.selectbox("Inspect Task", options=eval_tasks, index=0, key="arena_task_select")
        res = st.session_state.evaluation_results[selected_arena_id]
        
        col_arena_b, col_arena_a, col_arena_b_role = st.columns(3)
        
        with col_arena_b:
            st.html("""<div class="agent-header-badge badge-baseline">
                <span style="font-size: 18px;">🟣</span>
                <div>
                    <div style="font-weight: 700; font-size: 14px;">Single-Agent Baseline</div>
                    <div style="font-size: 11px; opacity: 0.8;">The Fast One-Shot Attempt</div>
                </div>
            </div>""")
            st.code(res.baseline_output.parsed_code or res.baseline_output.raw_response or "# No code", language="python")
            with st.expander("Details & Timing"):
                st.caption(f"⏱️ **Latency:** {res.baseline_output.latency_seconds:.2f}s | 🪙 **Tokens:** {res.baseline_output.tokens_used}")
                st.write(res.baseline_output.explanation or "No explanation provided.")

        with col_arena_a:
            st.html("""<div class="agent-header-badge badge-agent-a">
                <span style="font-size: 18px;">🔵</span>
                <div>
                    <div style="font-weight: 700; font-size: 14px;">Agent A (Algorithmic)</div>
                    <div style="font-size: 11px; opacity: 0.8;">First-Principles Design</div>
                </div>
            </div>""")
            st.code(res.agent_a_output.parsed_code or res.agent_a_output.raw_response or "# No code", language="python")
            with st.expander("Details & Timing"):
                st.caption(f"⏱️ **Latency:** {res.agent_a_output.latency_seconds:.2f}s | 🪙 **Tokens:** {res.agent_a_output.tokens_used}")
                st.write(res.agent_a_output.explanation or "No explanation provided.")

        with col_arena_b_role:
            st.html("""<div class="agent-header-badge badge-agent-b">
                <span style="font-size: 18px;">🟢</span>
                <div>
                    <div style="font-weight: 700; font-size: 14px;">Agent B (Adversarial)</div>
                    <div style="font-size: 11px; opacity: 0.8;">Edge-Case Specialist</div>
                </div>
            </div>""")
            st.code(res.agent_b_output.parsed_code or res.agent_b_output.raw_response or "# No code", language="python")
            with st.expander("Guarded Traps & Timing"):
                st.caption(f"⏱️ **Latency:** {res.agent_b_output.latency_seconds:.2f}s | 🪙 **Tokens:** {res.agent_b_output.tokens_used}")
                st.write(res.agent_b_output.explanation or "No explanation provided.")

        st.markdown("#### Did the Agents Agree?")
        if res.agent_disagreement:
            st.warning("⚠️ **Different Approaches:** Agent A and Agent B wrote distinctly different solutions!")
            if res.evaluator_decision.identified_disagreements:
                for dis in res.evaluator_decision.identified_disagreements:
                    st.markdown(f"- 🔸 {dis}")
        else:
            st.info("ℹ️ **Agreement:** Both Agent A and Agent B arrived at equivalent implementations.")

# ---------------------------------------------------------
# TAB D: EVALUATOR REPORT
# ---------------------------------------------------------
with tab_eval:
    st.markdown("### ⚖️ Gemma 4 Evaluator: The AI Judge's Verdict")
    st.markdown("Gemma 4 compares both candidate solutions, detects flaws, and chooses a winner.")
    
    eval_tasks = list(st.session_state.evaluation_results.keys())
    if not eval_tasks:
        st.info("Run an evaluation to view the Evaluator Report.")
    else:
        selected_eval_id = st.selectbox("Inspect Task", options=eval_tasks, index=0, key="eval_task_select")
        res = st.session_state.evaluation_results[selected_eval_id]
        ev = res.evaluator_decision
        
        col_ev_main, col_ev_meta = st.columns([3, 2])
        with col_ev_main:
            st.html(f"""<div class="eight-card">
                <div class="eight-card-title">
                    <span>🏆 Evaluator Pick: <b>{ev.selected_agent}</b></span>
                </div>
                <p style="font-size: 14px; color: #E2E8F0; line-height: 1.6; margin: 0;">
                    {ev.rationale}
                </p>
            </div>""")
            
            st.markdown("##### Potential Edge Cases Flagged by Evaluator")
            if ev.potential_failure_modes:
                for mode in ev.potential_failure_modes:
                    st.markdown(f"- ⚠️ <span style='color: #F87171;'>{mode}</span>", unsafe_allow_html=True)
            else:
                st.caption("No edge-case risks noted.")

        with col_ev_meta:
            st.html(f"""<div class="eight-card">
                <div class="eight-card-title">📊 Evaluator Metadata</div>
                <div style="font-size: 13px; color: #94A3B8; line-height: 1.8;">
                    <b>Confidence:</b> <span style="color: #38BDF8; font-weight: 700;">{ev.confidence_score * 100:.1f}%</span><br>
                    <b>Review Latency:</b> {ev.latency_seconds:.2f}s<br>
                    <b>Tokens Used:</b> {ev.tokens_used}<br>
                    <b>Mode:</b> {'Simulation Simulator' if ev.is_mock else 'Live Gemma 4 API'}<br>
                    <b>Format:</b> Valid Structured JSON
                </div>
            </div>""")
            
            with st.expander("Raw Evaluator JSON Response"):
                st.code(ev.raw_response, language="json")

        st.html("""<div class="human-callout">
            <b>🛡️ Ground Truth Warning:</b> An AI's evaluation is still an AI opinion!
            Head over to the <b>Verification Center</b> to see if this candidate actually passed deterministic test assertions.
        </div>""")

# ---------------------------------------------------------
# TAB E: VERIFICATION CENTER
# ---------------------------------------------------------
with tab_verif:
    st.markdown("### 🛡️ Verification Center: Ground-Truth Proof")
    st.markdown("This is the source of truth. We run real test cases against all generated code in an AST-audited sandbox.")
    
    eval_tasks = list(st.session_state.evaluation_results.keys())
    if not eval_tasks:
        st.info("Run an evaluation to view verification results.")
    else:
        selected_verif_id = st.selectbox("Inspect Task", options=eval_tasks, index=0, key="verif_task_select")
        res = st.session_state.evaluation_results[selected_verif_id]
        
        if res.evaluator_error_flag:
            st.error(
                "🚨 **EVALUATOR MISJUDGMENT!** "
                f"Gemma 4 chose **{res.evaluator_decision.selected_agent}**, "
                "which FAILED the test assertions, even though an alternative candidate passed!"
            )
            
        c_v1, c_v2, c_v3, c_v4 = st.columns(4)
        
        with c_v1:
            vb = res.baseline_verification
            st.html(f"""<div class="kpi-card">
                <div class="kpi-value" style="color: {'#10B981' if vb.all_passed else '#EF4444'};">
                    {vb.pass_count}/{vb.total_count}
                </div>
                <div class="kpi-label">Baseline Score</div>
                <div class="kpi-subtext">{'✅ All passed' if vb.all_passed else '❌ Failed trap'}</div>
            </div>""")
        with c_v2:
            va = res.agent_a_verification
            st.html(f"""<div class="kpi-card">
                <div class="kpi-value" style="color: {'#10B981' if va.all_passed else '#EF4444'};">
                    {va.pass_count}/{va.total_count}
                </div>
                <div class="kpi-label">Agent A Score</div>
                <div class="kpi-subtext">{'✅ All passed' if va.all_passed else '❌ Failed trap'}</div>
            </div>""")
        with c_v3:
            v_b = res.agent_b_verification
            st.html(f"""<div class="kpi-card">
                <div class="kpi-value" style="color: {'#10B981' if v_b.all_passed else '#EF4444'};">
                    {v_b.pass_count}/{v_b.total_count}
                </div>
                <div class="kpi-label">Agent B Score</div>
                <div class="kpi-subtext">{'✅ All passed' if v_b.all_passed else '❌ Failed trap'}</div>
            </div>""")
        with c_v4:
            vm = res.multi_agent_verification
            st.html(f"""<div class="kpi-card">
                <div class="kpi-value" style="color: {'#10B981' if vm.all_passed else '#EF4444'};">
                    {vm.pass_count}/{vm.total_count}
                </div>
                <div class="kpi-label">Multi-Agent Final</div>
                <div class="kpi-subtext">{'✅ All passed' if vm.all_passed else '❌ Failed trap'}</div>
            </div>""")

        st.markdown("#### Test Case Breakdown (Evaluator's Pick)")
        test_rows = []
        for t in res.multi_agent_verification.test_results:
            test_rows.append({
                "Test Name": t.test_name,
                "Type": "🔥 Edge Case" if t.is_edge_case else "Standard",
                "Outcome": "✅ PASS" if t.passed else "❌ FAIL",
                "Input": t.input_repr,
                "Expected": t.expected_repr,
                "Actual Output": t.actual_repr,
                "Diagnostics": t.error_message or "Verified exact match"
            })
            
        df_tests = pd.DataFrame(test_rows)
        st.dataframe(df_tests, use_container_width=True, hide_index=True)

# ---------------------------------------------------------
# TAB F: RELIABILITY ANALYTICS
# ---------------------------------------------------------
with tab_analytics:
    st.markdown("### 📈 Reliability Analytics: The Hard Data")
    st.markdown("Empirical scorecard comparing Single-Agent vs Multi-Agent systems across all benchmarks.")
    
    all_results = list(st.session_state.evaluation_results.values())
    if not all_results:
        st.info("Run evaluations to view analytics.")
    else:
        summary: BenchmarkRunSummary = MetricsCalculator.aggregate_benchmark_runs(all_results)
        
        # KPI Row
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.html(f"""<div class="kpi-card">
                <div class="kpi-value">{summary.baseline_pass_rate * 100:.1f}%</div>
                <div class="kpi-label">Single-Agent Pass Rate</div>
                <div class="kpi-subtext">{summary.baseline_pass_count} of {summary.total_tasks_attempted} tasks verified</div>
            </div>""")
        with c2:
            st.html(f"""<div class="kpi-card">
                <div class="kpi-value" style="color: #10B981;">{summary.multi_agent_pass_rate * 100:.1f}%</div>
                <div class="kpi-label">Multi-Agent Pass Rate</div>
                <div class="kpi-subtext">{summary.multi_agent_pass_count} of {summary.total_tasks_attempted} tasks verified</div>
            </div>""")
        with c3:
            delta_prefix = "+" if summary.pass_rate_delta > 0 else ""
            delta_color = "#10B981" if summary.pass_rate_delta > 0 else ("#EF4444" if summary.pass_rate_delta < 0 else "#64748B")
            st.html(f"""<div class="kpi-card">
                <div class="kpi-value" style="color: {delta_color};">{delta_prefix}{summary.pass_rate_delta * 100:.1f}%</div>
                <div class="kpi-label">Accuracy Gain</div>
                <div class="kpi-subtext">Net gain over baseline</div>
            </div>""")
        with c4:
            st.html(f"""<div class="kpi-card">
                <div class="kpi-value" style="color: #F59E0B;">{summary.evaluator_error_count}</div>
                <div class="kpi-label">Evaluator Misjudgments</div>
                <div class="kpi-subtext">Gemma picked failing code</div>
            </div>""")

        st.markdown("#### Performance Visualizations")
        col_ch1, col_ch2 = st.columns([3, 2])
        with col_ch1:
            st.markdown("##### Task-by-Task Pass Rate (%)")
            chart_tasks = create_task_comparison_chart(all_results)
            st.altair_chart(chart_tasks, use_container_width=True)
            
        with col_ch2:
            st.markdown("##### Did Collaboration Actually Help?")
            chart_donut = create_collaboration_donut(
                helped=summary.collaboration_helped_count,
                no_effect=summary.collaboration_no_effect_count,
                hurt=summary.collaboration_hurt_count
            )
            st.altair_chart(chart_donut, use_container_width=True)

        st.markdown("#### The Trade-Off: Speed & API Cost")
        lat_ratio = (summary.avg_multi_agent_latency / summary.avg_baseline_latency) if summary.avg_baseline_latency > 0 else 1.0
        t1, t2, t3, t4 = st.columns(4)
        with t1:
            st.html(f"""<div class="eight-card">
                <div style="font-size: 11px; color: #94A3B8; text-transform: uppercase; font-weight: 700;">Avg Baseline Speed</div>
                <div style="font-size: 22px; font-weight: 800; color: #F8FAFC; margin-top: 4px;">{summary.avg_baseline_latency:.2f}s</div>
            </div>""")
        with t2:
            st.html(f"""<div class="eight-card">
                <div style="font-size: 11px; color: #94A3B8; text-transform: uppercase; font-weight: 700;">Avg Multi-Agent Speed</div>
                <div style="font-size: 22px; font-weight: 800; color: #38BDF8; margin-top: 4px;">{summary.avg_multi_agent_latency:.2f}s <span style="font-size: 12px; color: #F59E0B;">({lat_ratio:.1f}x slower)</span></div>
            </div>""")
        with t3:
            st.html(f"""<div class="eight-card">
                <div style="font-size: 11px; color: #94A3B8; text-transform: uppercase; font-weight: 700;">Total API Requests</div>
                <div style="font-size: 22px; font-weight: 800; color: #F8FAFC; margin-top: 4px;">{summary.total_api_calls} calls <span style="font-size: 12px; color: #94A3B8;">(4x calls)</span></div>
            </div>""")
        with t4:
            st.html(f"""<div class="eight-card">
                <div style="font-size: 11px; color: #94A3B8; text-transform: uppercase; font-weight: 700;">Total Tokens Used</div>
                <div style="font-size: 22px; font-weight: 800; color: #F8FAFC; margin-top: 4px;">{summary.total_tokens:,} tokens</div>
            </div>""")

# ---------------------------------------------------------
# TAB G: FAILURE INSPECTOR
# ---------------------------------------------------------
with tab_inspector:
    st.markdown("### 🔍 Failure Inspector: Forensic Autopsy")
    st.markdown("Deep dive into bugs, missed edge cases, and why the model tripped.")
    
    all_results = list(st.session_state.evaluation_results.values())
    failed_results = [
        r for r in all_results
        if not r.baseline_verification.all_passed or not r.multi_agent_verification.all_passed or r.evaluator_error_flag
    ]
    
    if not failed_results:
        st.success("🎉 All evaluated tasks passed!")
    else:
        fail_options = [f"{r.task.task_id} — {r.task.title}" for r in failed_results]
        selected_fail = st.selectbox("Select Case to Audit", options=fail_options, index=0)
        fail_id = selected_fail.split(" — ")[0]
        f_res = st.session_state.evaluation_results[fail_id]
        
        st.html(f"""<div class="eight-card" style="border-left: 4px solid #EF4444;">
            <div class="eight-card-title" style="color: #EF4444;">🚨 Incident File: {f_res.task.task_id} — {f_res.task.title}</div>
            <div style="font-size: 13.5px; color: #E2E8F0; line-height: 1.5; margin-bottom: 8px;">
                <b>Problem:</b> {f_res.task.description}
            </div>
            <div style="font-size: 13px; color: #F59E0B;">
                <b>The Trap:</b> {f_res.task.expected_trap}
            </div>
        </div>""")
        
        col_forensic1, col_forensic2 = st.columns(2)
        with col_forensic1:
            st.markdown("##### What Did Gemma 4 Think?")
            st.html(f"""<div class="eight-card">
                <b>Candidate Picked:</b> {f_res.evaluator_decision.selected_agent}<br>
                <b>Confidence:</b> {f_res.evaluator_decision.confidence_score * 100:.1f}%<br><br>
                <div style="font-size: 13px; color: #CBD5E1; line-height: 1.5;">{f_res.evaluator_decision.rationale}</div>
            </div>""")
        with col_forensic2:
            st.markdown("##### What Did Ground-Truth Find?")
            if f_res.multi_agent_verification.all_passed:
                st.html("""<div class="eight-card" style="border-color: rgba(16, 185, 129, 0.4);">
                    <span style="color: #10B981; font-weight: 700;">✅ Multi-Agent Solved It!</span><br>
                    <span style="font-size: 13px; color: #CBD5E1;">The collaborative team successfully avoided the trap that broke the single baseline.</span>
                </div>""")
            else:
                failed_tc = [t for t in f_res.multi_agent_verification.test_results if not t.passed]
                for ft in failed_tc:
                    st.error(f"❌ **{ft.test_name}**: Expected `{ft.expected_repr}`, got `{ft.actual_repr}`")

        st.markdown("##### AI Diagnostic Root-Cause Hypothesis")
        st.html(f"""<div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.25); border-radius: 10px; padding: 14px 18px;">
            <div style="font-size: 11.5px; font-weight: 700; color: #EF4444; text-transform: uppercase;">Diagnostic Breakdown</div>
            <div style="font-size: 13.5px; color: #FCA5A5; margin-top: 6px; line-height: 1.5;">
                {f_res.failure_hypothesis or 'No failure hypothesis generated.'}
            </div>
            <div style="font-size: 11px; color: #94A3B8; margin-top: 8px;">
                *Corroborated by failed assertion traces in the deterministic sandbox.*
            </div>
        </div>""")
