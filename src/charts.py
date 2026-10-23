"""
Altair-based interactive charts for EIGHT — AI Crash-Test Lab.
Adapts dynamically to both Dark and Light dashboard themes.
"""

import altair as alt
import pandas as pd
from typing import List
from src.schemas import TaskEvaluationResult

def _get_chart_colors(theme: str):
    is_dark = (theme.lower() == "dark")
    return {
        "label": "#94A3B8" if is_dark else "#475569",
        "title": "#CBD5E1" if is_dark else "#1E293B",
        "grid": "rgba(255, 255, 255, 0.06)" if is_dark else "rgba(15, 23, 42, 0.08)",
        "baseline_bar": "#A855F7" if is_dark else "#9333EA",
        "multi_bar": "#38BDF8" if is_dark else "#0284C7",
    }

def create_task_comparison_chart(task_results: List[TaskEvaluationResult], theme: str = "dark") -> alt.Chart:
    """Grouped bar chart comparing Single-Agent Baseline vs Multi-Agent pass rates."""
    c = _get_chart_colors(theme)
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
        y=alt.Y("Pass Rate (%):Q", title="Test Pass Rate (%)", scale=alt.Scale(domain=[0, 100]), axis=alt.Axis(gridColor=c["grid"], labelColor=c["label"], titleColor=c["title"])),
        color=alt.Color(
            "Strategy:N",
            scale=alt.Scale(
                domain=["Single-Agent Baseline", "Multi-Agent Pipeline"],
                range=[c["baseline_bar"], c["multi_bar"]]
            ),
            legend=alt.Legend(title="System Strategy", orient="top", labelColor=c["title"], titleColor=c["label"])
        ),
        column=alt.Column(
            "Task:N",
            title="Benchmark Task ID",
            header=alt.Header(labelColor=c["title"], titleColor=c["label"], labelFont="Plus Jakarta Sans", labelFontSize=12)
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

def create_collaboration_donut(helped: int, no_effect: int, hurt: int, theme: str = "dark") -> alt.Chart:
    """Donut chart illustrating the empirical impact of multi-agent collaboration."""
    c = _get_chart_colors(theme)
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
        color=alt.Color("Outcome:N", scale=alt.Scale(domain=source["Outcome"].tolist(), range=source["Color"].tolist()), legend=alt.Legend(orient="bottom", labelColor=c["title"], title=None, labelLimit=250)),
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

def create_latency_comparison_chart(task_results: List[TaskEvaluationResult], theme: str = "dark") -> alt.Chart:
    """Horizontal bar chart illustrating the latency trade-off."""
    c = _get_chart_colors(theme)
    data = []
    for r in task_results:
        data.append({"Task": r.task.task_id, "Strategy": "Baseline", "Seconds": r.baseline_output.latency_seconds})
        multi_lat = round(r.agent_a_output.latency_seconds + r.agent_b_output.latency_seconds + r.evaluator_decision.latency_seconds, 2)
        data.append({"Task": r.task.task_id, "Strategy": "Multi-Agent Pipeline", "Seconds": multi_lat})

    df = pd.DataFrame(data)

    chart = alt.Chart(df).mark_bar(cornerRadiusTopRight=3, cornerRadiusBottomRight=3).encode(
        y=alt.Y("Task:N", title="Task ID", axis=alt.Axis(labelColor=c["title"], titleColor=c["label"])),
        x=alt.X("Seconds:Q", title="Execution Latency (seconds)", axis=alt.Axis(gridColor=c["grid"], labelColor=c["label"], titleColor=c["title"])),
        color=alt.Color(
            "Strategy:N",
            scale=alt.Scale(domain=["Baseline", "Multi-Agent Pipeline"], range=[c["baseline_bar"], c["multi_bar"]]),
            legend=alt.Legend(orient="top", labelColor=c["title"], title=None)
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
