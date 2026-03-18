import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fatigue_calculator import calculate_fatigue_score

st.set_page_config(page_title="AeroVigil", page_icon="✈️", layout="wide")

# ---------- HEADER ----------
st.title("✈️ AeroVigil")
st.subheader("Predictive Fatigue Risk Analytics for Aviation Safety")
st.write(
    "AeroVigil is a prototype decision-support tool designed to estimate aviation crew fatigue risk "
    "using operational inputs such as duty hours, segments, rest, timezone changes, and circadian disruption."
)

st.divider()

# ---------- SIDEBAR ----------
st.sidebar.header("Crew Duty Inputs")

duty_hours = st.sidebar.slider("Duty Hours", 0, 16, 8)
segments = st.sidebar.slider("Flight Segments", 1, 8, 2)
timezone_changes = st.sidebar.slider("Time Zone Changes", 0, 6, 0)
rest_hours = st.sidebar.slider("Rest Hours Before Duty", 0, 16, 10)
circadian_disruption = st.sidebar.slider("Circadian Disruption Level", 0, 10, 3)

# ---------- FATIGUE SCORE ----------
score = calculate_fatigue_score(
    duty_hours,
    segments,
    timezone_changes,
    rest_hours,
    circadian_disruption
)

if score < 35:
    risk_level = "LOW"
    recommendation = "Crew schedule appears acceptable. Continue monitoring fatigue factors."
elif score < 65:
    risk_level = "MODERATE"
    recommendation = "Consider mitigation strategies such as additional monitoring, adjusted rest, or reduced workload."
else:
    risk_level = "HIGH"
    recommendation = "Fatigue risk is elevated. Review duty assignment, rest opportunity, and operational exposure."

# ---------- TOP METRICS ----------
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Fatigue Score", f"{score}/100")

with col2:
    st.metric("Risk Level", risk_level)

with col3:
    st.metric("Rest Hours", f"{rest_hours} hrs")

st.divider()

# ---------- TABS ----------
tab1, tab2, tab3, tab4 = st.tabs([
    "Dashboard",
    "Trend Analysis",
    "Scenario Comparison",
    "Mitigation Advice"
])

# ---------- TAB 1: DASHBOARD ----------
with tab1:
    st.subheader("Current Fatigue Risk Dashboard")

    dashboard_col1, dashboard_col2 = st.columns([2, 1])

    with dashboard_col1:
        st.write("### Input Summary")
        summary_df = pd.DataFrame({
            "Factor": [
                "Duty Hours",
                "Flight Segments",
                "Time Zone Changes",
                "Rest Hours",
                "Circadian Disruption"
            ],
            "Value": [
                duty_hours,
                segments,
                timezone_changes,
                rest_hours,
                circadian_disruption
            ]
        })
        st.dataframe(summary_df, use_container_width=True)

    with dashboard_col2:
        st.write("### Risk Status")
        if risk_level == "LOW":
            st.success(f"Risk Level: {risk_level}")
        elif risk_level == "MODERATE":
            st.warning(f"Risk Level: {risk_level}")
        else:
            st.error(f"Risk Level: {risk_level}")

        st.write("### Recommendation")
        st.info(recommendation)

# ---------- TAB 2: TREND ANALYSIS ----------
with tab2:
    st.subheader("4-Day Fatigue Trend")

    trend_data = pd.DataFrame({
        "Day": ["Day 1", "Day 2", "Day 3", "Day 4"],
        "Fatigue Score": [
            max(0, score - 12),
            max(0, score - 6),
            score,
            min(100, score + 8)
        ]
    })

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(trend_data["Day"], trend_data["Fatigue Score"], marker="o")
    ax.set_title("Projected Fatigue Trend")
    ax.set_ylabel("Fatigue Score")
    ax.set_ylim(0, 100)

    st.pyplot(fig)
    st.dataframe(trend_data, use_container_width=True)

# ---------- TAB 3: SCENARIO COMPARISON ----------
with tab3:
    st.subheader("Scenario Comparison Tool")

    compare_col1, compare_col2 = st.columns(2)

    with compare_col1:
        st.write("### Current Scenario")
        current_score = score
        st.metric("Current Score", f"{current_score}/100")

    with compare_col2:
        st.write("### Improved Scenario")
        improved_rest = min(rest_hours + 2, 16)
        improved_score = calculate_fatigue_score(
            duty_hours,
            segments,
            timezone_changes,
            improved_rest,
            max(circadian_disruption - 1, 0)
        )
        st.metric("Improved Score", f"{improved_score}/100")

    comparison_df = pd.DataFrame({
        "Scenario": ["Current", "Improved"],
        "Fatigue Score": [current_score, improved_score]
    })

    fig2, ax2 = plt.subplots(figsize=(8, 4))
    ax2.bar(comparison_df["Scenario"], comparison_df["Fatigue Score"])
    ax2.set_title("Fatigue Scenario Comparison")
    ax2.set_ylabel("Fatigue Score")
    ax2.set_ylim(0, 100)

    st.pyplot(fig2)
    st.dataframe(comparison_df, use_container_width=True)

# ---------- TAB 4: MITIGATION ----------
with tab4:
    st.subheader("Mitigation Guidance")

    if risk_level == "LOW":
        st.success("Current fatigue exposure is manageable.")
        st.write("- Maintain current rest strategy")
        st.write("- Continue fatigue awareness monitoring")
        st.write("- Reassess if duty length increases")
    elif risk_level == "MODERATE":
        st.warning("Moderate fatigue exposure detected.")
        st.write("- Consider increasing pre-duty rest")
        st.write("- Limit operational complexity where possible")
        st.write("- Monitor cumulative fatigue trends")
    else:
        st.error("High fatigue exposure detected.")
        st.write("- Reevaluate duty assignment")
        st.write("- Increase rest opportunity before next duty period")
        st.write("- Consider schedule redesign or mitigation controls")
        st.write("- Escalate to safety/operations review if needed")

st.divider()
st.caption("Prototype for demonstration purposes only. AeroVigil is not an FAA-approved operational dispatch or medical decision tool.")
