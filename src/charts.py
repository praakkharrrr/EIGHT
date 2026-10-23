"""
Interactive Altair charts for EIGHT — AI Crash-Test Lab.
Tuned for the masterclass dark engineering dashboard theme.
"""

import altair as alt
import pandas as pd
from typing import List
from src.schemas import TaskEvaluationResult

def create_task_comparison_chart(task_results: List[TaskEvaluationResult]) -> alt.Chart:
    """Grouped bar chart comparing Single-Agent Baseline vs Multi-Agent pass rates."""
    rows = []
    for r in task_results:
        rows.append({
            "Task": r.task.task_id,
            "Title": r.task.title,
            "Strategy": "Single-Agent Baseline",
            "Pass Rate (%)": r.baseline_verification.pass_rate * 100,
            "Passed Cases": f"{r.baseline_verification.pass_count}/{r.baseline_verification.total_count}",
            "Latency (s)": r.baseline_output.latency_seconds,
        })
        rows.append({
            "Task": r.task.task_id,
            "Title": r.task.title,
            "Strategy": "Multi-Agent Pipeline",
            "Pass Rate (%)": r.multi_agent_verification.pass_rate * 100,
            "Passed Cases": f"{r.multi_agent_verification.pass_count}/{r.multi_agent_verification.total_count}",
            "Latency (s)": round(r.agent_a_output.latency_seconds + r.agent_b_output.latency_seconds + r.evaluator_decision.latency_seconds, 2),
        })

    df = pd.DataFrame(rows)

    chart = alt.Chart(df).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
        x=alt.X("Strategy:N", title=None, axis=alt.Axis(labels=False, ticks=False)),
        y=alt.Y("Pass Rate (%):Q", title="Test Pass Rate (%)", scale=alt.Scale(domain=[0, 100]), axis=alt.Axis(gridColor="rgba(255, 255, 255, 0.08)", labelColor="#CBD5E1", titleColor="#F8FAFC")),
        color=alt.Color(
            "Strategy:N",
            scale=alt.Scale(
                domain=["Single-Agent Baseline", "Multi-Agent Pipeline"],
                range=["#A855F7", "#38BDF8"]
            ),
            legend=alt.Legend(title="Strategy", orient="top", labelColor="#CBD5E1", titleColor="#F8FAFC")
        ),
        column=alt.Column(
            "Task:N",
            title="Benchmark Task ID",
            header=alt.Header(labelColor="#CBD5E1", titleColor="#F8FAFC", labelFont="Inter", labelFontSize=12)
        ),
        tooltip=[
            alt.Tooltip("Task:N", title="Task ID"),
            alt.Tooltip("Title:N", title="Task Title"),
            alt.Tooltip("Strategy:N", title="Strategy"),
            alt.Tooltip("Pass Rate (%):Q", format=".1f", title="Pass Rate"),
            alt.Tooltip("Passed Cases:N", title="Assertions Passed"),
            alt.Tooltip("Latency (s):Q", format=".2f", title="Latency (sec)")
        ]
    ).properties(
        height=260,
        background="transparent"
    ).configure_view(
        strokeWidth=0
    )

    return chart

def create_collaboration_donut(helped: int, no_effect: int, hurt: int) -> alt.Chart:
    """Donut chart illustrating the empirical impact of multi-agent collaboration."""
    source = pd.DataFrame([
        {"Outcome": "Helped (Multi passed, Baseline failed)", "Count": helped, "Color": "#10B981"},
        {"Outcome": "No Effect (Equal pass/fail)", "Count": no_effect, "Color": "#64748B"},
        {"Outcome": "Hurt (Baseline passed, Multi failed)", "Count": hurt, "Color": "#F43F5E"},
    ])

    source = source[source["Count"] > 0]
    if source.empty:
        source = pd.DataFrame([{"Outcome": "No Data", "Count": 1, "Color": "#334155"}])

    chart = alt.Chart(source).mark_arc(innerRadius=60, outerRadius=95, cornerRadius=4).encode(
        theta=alt.Theta("Count:Q", stack=True),
        color=alt.Color("Outcome:N", scale=alt.Scale(domain=source["Outcome"].tolist(), range=source["Color"].tolist()), legend=alt.Legend(orient="bottom", labelColor="#CBD5E1", title=None, labelLimit=250)),
        tooltip=[
            alt.Tooltip("Outcome:N", title="Outcome"),
            alt.Tooltip("Count:Q", title="Tasks Count")
        ]
    ).properties(
        height=240,
        background="transparent"
    ).configure_view(
        strokeWidth=0
    )

    return chart

def create_latency_comparison_chart(task_results: List[TaskEvaluationResult]) -> alt.Chart:
    """Horizontal bar chart illustrating the latency trade-off."""
    data = []
    for r in task_results:
        data.append({"Task": r.task.task_id, "Strategy": "Baseline", "Seconds": r.baseline_output.latency_seconds})
        multi_lat = round(r.agent_a_output.latency_seconds + r.agent_b_output.latency_seconds + r.evaluator_decision.latency_seconds, 2)
        data.append({"Task": r.task.task_id, "Strategy": "Multi-Agent Pipeline", "Seconds": multi_lat})

    df = pd.DataFrame(data)

    chart = alt.Chart(df).mark_bar(cornerRadiusTopRight=3, cornerRadiusBottomRight=3).encode(
        y=alt.Y("Task:N", title="Task ID", axis=alt.Axis(labelColor="#CBD5E1", titleColor="#F8FAFC")),
        x=alt.X("Seconds:Q", title="Execution Latency (seconds)", axis=alt.Axis(gridColor="rgba(255, 255, 255, 0.08)", labelColor="#CBD5E1", titleColor="#F8FAFC")),
        color=alt.Color(
            "Strategy:N",
            scale=alt.Scale(domain=["Baseline", "Multi-Agent Pipeline"], range=["#A855F7", "#38BDF8"]),
            legend=alt.Legend(orient="top", labelColor="#CBD5E1", title=None)
        ),
        tooltip=[
            alt.Tooltip("Task:N"),
            alt.Tooltip("Strategy:N"),
            alt.Tooltip("Seconds:Q", format=".2f", title="Latency (s)")
        ]
    ).properties(
        height=260,
        background="transparent"
    ).configure_view(
        strokeWidth=0
    )

    return chart
