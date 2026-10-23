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

    chart = alt.Chart(df).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
        x=alt.X("Strategy:N", title=None, axis=alt.Axis(labels=False, ticks=False)),
        y=alt.Y("Pass Rate (%):Q", title="Test Pass Rate (%)", scale=alt.Scale(domain=[0, 100]), axis=alt.Axis(gridColor="rgba(15, 23, 42, 0.08)", labelColor="#334155", titleColor="#0F172A")),
        color=alt.Color(
            "Strategy:N",
            scale=alt.Scale(
                domain=["Single-Agent Baseline", "Multi-Agent Pipeline"],
                range=["#8B5CF6", "#0284C7"]
            ),
            legend=alt.Legend(title="Strategy", orient="top", labelColor="#334155", titleColor="#0F172A")
        ),
        column=alt.Column(
            "Task:N",
            title="Benchmark Task ID",
            header=alt.Header(labelColor="#334155", titleColor="#0F172A", labelFont="Plus Jakarta Sans", labelFontSize=12)
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
    """Donut chart illustrating the empirical impact of multi-agent collaboration with center badge and zero clipping."""
    total = helped + no_effect + hurt
    pct_helped = round((helped / total * 100), 1) if total > 0 else 0

    source = pd.DataFrame([
        {"Outcome": "Helped (Multi Won)", "Count": helped, "Color": "#10B981"},
        {"Outcome": "No Effect (Neutral)", "Count": no_effect, "Color": "#94A3B8"},
        {"Outcome": "Hurt (Baseline Won)", "Count": hurt, "Color": "#EF4444"},
    ])

    source = source[source["Count"] > 0]
    if source.empty:
        source = pd.DataFrame([{"Outcome": "No Data", "Count": 1, "Color": "#CBD5E1"}])

    donut = alt.Chart(source).mark_arc(
        innerRadius=52,
        outerRadius=78,
        padAngle=0.04,
        stroke="#FFFFFF",
        strokeWidth=2
    ).encode(
        theta=alt.Theta("Count:Q", stack=True),
        color=alt.Color(
            "Outcome:N",
            scale=alt.Scale(
                domain=source["Outcome"].tolist(),
                range=source["Color"].tolist()
            ),
            legend=alt.Legend(
                orient="bottom",
                labelColor="#334155",
                title=None,
                labelLimit=300,
                labelFontSize=12,
                labelFont="Plus Jakarta Sans",
                symbolType="circle",
                direction="horizontal"
            )
        ),
        tooltip=[
            alt.Tooltip("Outcome:N", title="Outcome"),
            alt.Tooltip("Count:Q", title="Tasks Count")
        ]
    )

    # Clean Center KPI Badge
    center_df = pd.DataFrame([{"val": f"{pct_helped:.0f}%", "label": "Helped"}])
    
    text_val = alt.Chart(center_df).mark_text(
        fontSize=20,
        fontWeight=800,
        color="#0F172A",
        font="Plus Jakarta Sans",
        dy=-5
    ).encode(text="val:N")

    text_label = alt.Chart(center_df).mark_text(
        fontSize=11,
        fontWeight=600,
        color="#64748B",
        font="Plus Jakarta Sans",
        dy=13
    ).encode(text="label:N")

    chart = (donut + text_val + text_label).properties(
        height=260,
        background="transparent",
        padding={"top": 15, "bottom": 15, "left": 10, "right": 10}
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

    chart = alt.Chart(df).mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4).encode(
        y=alt.Y("Task:N", title="Task ID", axis=alt.Axis(labelColor="#334155", titleColor="#0F172A")),
        x=alt.X("Seconds:Q", title="Execution Latency (seconds)", axis=alt.Axis(gridColor="rgba(15, 23, 42, 0.08)", labelColor="#334155", titleColor="#0F172A")),
        color=alt.Color(
            "Strategy:N",
            scale=alt.Scale(domain=["Baseline", "Multi-Agent Pipeline"], range=["#8B5CF6", "#0284C7"]),
            legend=alt.Legend(orient="top", labelColor="#334155", title=None)
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
