import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fatigue_calculator import calculate_fatigue_score

st.set_page_config(page_title="AeroVigil ", page_icon="✈️", layout="wide")

# ---------- HELPERS ----------
def get_risk_level(score):
    if score < 35:
        return "LOW", "🟢"
    elif score < 65:
        return "MODERATE", "🟡"
    else:
        return "HIGH", "🔴"

def get_recommendation(score):
    if score < 35:
        return "Crew schedule appears acceptable. Continue monitoring fatigue factors."
    elif score < 65:
        return "Consider mitigation such as added rest, reduced workload, or closer fatigue monitoring."
    else:
        return "Immediate review recommended. Reassess duty assignment, rest opportunity, and operational exposure."

def score_row(row, irops_mode=False):
    score = calculate_fatigue_score(
        row["Duty Hours"],
        row["Flight Segments"],
        row["Time Zone Changes"],
        row["Rest Hours Before Duty"],
        row["Circadian Disruption Level"]
    )
    if irops_mode:
        score = min(100, score + 10)
    return score

# ---------- HEADER ----------
st.title("✈️ AeroVigil V3")
st.subheader("Predictive Fatigue Risk Analytics for Airline Operations")
st.write(
    "AeroVigil V3 is a prototype airline fatigue decision-support dashboard designed to help "
    "operations leaders identify elevated crew fatigue exposure, monitor risk trends, and test mitigation scenarios."
)

# ---------- SIDEBAR ----------
st.sidebar.header("Operations Controls")
irops_mode = st.sidebar.toggle("Enable IROPs Mode", value=False)

st.sidebar.markdown("### Single-Crew Input")
duty_hours = st.sidebar.slider("Duty Hours", 0, 16, 8)
segments = st.sidebar.slider("Flight Segments", 1, 8, 2)
timezone_changes = st.sidebar.slider("Time Zone Changes", 0, 6, 0)
rest_hours = st.sidebar.slider("Rest Hours Before Duty", 0, 16, 10)
circadian_disruption = st.sidebar.slider("Circadian Disruption Level", 0, 10, 3)

# ---------- SINGLE CREW SCORE ----------
single_score = calculate_fatigue_score(
    duty_hours,
    segments,
    timezone_changes,
    rest_hours,
    circadian_disruption
)

if irops_mode:
    single_score = min(100, single_score + 10)

risk_level, risk_icon = get_risk_level(single_score)
recommendation = get_recommendation(single_score)

# ---------- TOP ALERT BANNER ----------
if risk_level == "HIGH":
    st.error(f"🚨 HIGH FATIGUE RISK DETECTED — Score: {single_score}/100 | Immediate review recommended.")
elif risk_level == "MODERATE":
    st.warning(f"🟡 MODERATE FATIGUE RISK — Score: {single_score}/100 | Monitor crew exposure and consider mitigations.")
else:
    st.success(f"🟢 LOW FATIGUE RISK — Score: {single_score}/100 | Current fatigue exposure appears manageable.")

if irops_mode:
    st.info("⚠️ IROPs Mode is ON — fatigue exposure is being adjusted upward to reflect disruption conditions.")

st.divider()

# ---------- LOAD CSV ----------
try:
    crew_df = pd.read_csv("crew_data.csv")
    crew_df["Fatigue Score"] = crew_df.apply(lambda row: score_row(row, irops_mode), axis=1)
    crew_df["Risk Level"] = crew_df["Fatigue Score"].apply(lambda x: get_risk_level(x)[0])
    crew_df["Status"] = crew_df["Fatigue Score"].apply(lambda x: get_risk_level(x)[1])

    crews_at_risk = (crew_df["Fatigue Score"] >= 65).sum()
    avg_rest = round(crew_df["Rest Hours Before Duty"].mean(), 1)
    avg_score = round(crew_df["Fatigue Score"].mean(), 1)

except Exception:
    crew_df = None
    crews_at_risk = 0
    avg_rest = rest_hours
    avg_score = single_score

# ---------- KPI CARDS ----------
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric("Fatigue Score", f"{single_score}/100")

with kpi2:
    st.metric("Risk Level", risk_level)

with kpi3:
    st.metric("Crews at High Risk", crews_at_risk)

with kpi4:
    st.metric("Avg Rest Hours", f"{avg_rest} hrs")

st.divider()

# ---------- TABS ----------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Executive Dashboard",
    "Trend Forecast",
    "Scenario Simulator",
    "Crew Risk Table",
    "Mitigation Engine"
])

# ---------- TAB 1 ----------
with tab1:
    st.subheader("Executive Dashboard")

    left, right = st.columns([1.4, 1])

    with left:
        st.markdown("### Current Crew Input Summary")
        summary_df = pd.DataFrame({
            "Factor": [
                "Duty Hours",
                "Flight Segments",
                "Time Zone Changes",
                "Rest Hours Before Duty",
                "Circadian Disruption Level",
                "IROPs Mode"
            ],
            "Value": [
                duty_hours,
                segments,
                timezone_changes,
                rest_hours,
                circadian_disruption,
                "ON" if irops_mode else "OFF"
            ]
        })
        st.dataframe(summary_df, use_container_width=True)

    with right:
        st.markdown("### Current Risk Status")
        if risk_level == "HIGH":
            st.error(f"{risk_icon} {risk_level}")
        elif risk_level == "MODERATE":
            st.warning(f"{risk_icon} {risk_level}")
        else:
            st.success(f"{risk_icon} {risk_level}")

        st.markdown("### Recommendation")
        st.info(recommendation)

# ---------- TAB 2 ----------
with tab2:
    st.subheader("7-Day Fatigue Forecast")

    trend_scores = [
        max(0, single_score - 8),
        max(0, single_score - 5),
        max(0, single_score - 2),
        single_score,
        min(100, single_score + 4),
        min(100, single_score + 7),
        min(100, single_score + 10)
    ]

    trend_df = pd.DataFrame({
        "Day": ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5", "Day 6", "Day 7"],
        "Fatigue Score": trend_scores
    })

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(trend_df["Day"], trend_df["Fatigue Score"], marker="o")
    ax.set_title("Projected 7-Day Fatigue Risk Trend")
    ax.set_ylabel("Fatigue Score")
    ax.set_ylim(0, 100)
    st.pyplot(fig)

    st.dataframe(trend_df, use_container_width=True)

# ---------- TAB 3 ----------
with tab3:
    st.subheader("Scenario Simulator")

    sim1, sim2 = st.columns(2)

    with sim1:
        st.markdown("### Current Schedule")
        st.metric("Current Score", f"{single_score}/100")
        st.write(f"Risk Level: {risk_level}")

    with sim2:
        st.markdown("### Improved Schedule Scenario")
        improved_rest = min(rest_hours + 2, 16)
        improved_segments = max(1, segments - 1)
        improved_circadian = max(0, circadian_disruption - 1)

        improved_score = calculate_fatigue_score(
            duty_hours,
            improved_segments,
            timezone_changes,
            improved_rest,
            improved_circadian
        )

        if irops_mode:
            improved_score = min(100, improved_score + 10)

        improved_level, _ = get_risk_level(improved_score)

        st.metric("Improved Score", f"{improved_score}/100", delta=single_score - improved_score)
        st.write(f"Risk Level: {improved_level}")

    compare_df = pd.DataFrame({
        "Scenario": ["Current", "Improved"],
        "Fatigue Score": [single_score, improved_score]
    })

    fig2, ax2 = plt.subplots(figsize=(8, 4))
    ax2.bar(compare_df["Scenario"], compare_df["Fatigue Score"])
    ax2.set_title("Schedule Scenario Comparison")
    ax2.set_ylabel("Fatigue Score")
    ax2.set_ylim(0, 100)
    st.pyplot(fig2)

    st.markdown("### Applied Mitigation Changes")
    st.write("- Added 2 hours of pre-duty rest")
    st.write("- Reduced flight segments by 1")
    st.write("- Reduced circadian disruption by 1")

# ---------- TAB 4 ----------
with tab4:
    st.subheader("Crew Risk Table")

    if crew_df is not None:
        display_df = crew_df[[
            "Crew ID",
            "Duty Hours",
            "Flight Segments",
            "Time Zone Changes",
            "Rest Hours Before Duty",
            "Circadian Disruption Level",
            "Fatigue Score",
            "Risk Level",
            "Status"
        ]].sort_values(by="Fatigue Score", ascending=False)

        st.dataframe(display_df, use_container_width=True)

        fig3, ax3 = plt.subplots(figsize=(10, 4))
        ax3.bar(display_df["Crew ID"], display_df["Fatigue Score"])
        ax3.set_title("Crew Fatigue Scores")
        ax3.set_ylabel("Fatigue Score")
        ax3.set_ylim(0, 100)
        st.pyplot(fig3)
    else:
        st.warning("crew_data.csv not found. Add your crew file to display the multi-crew operations table.")

# ---------- TAB 5 ----------
with tab5:
    st.subheader("Mitigation Engine")

    st.markdown("### Recommended Actions")
    if single_score < 35:
        st.success("Current fatigue exposure is manageable.")
        st.write("- Maintain current rest strategy")
        st.write("- Continue normal monitoring")
        st.write("- Reassess if duty length increases")
    elif single_score < 65:
        st.warning("Moderate fatigue exposure detected.")
        st.write("- Increase pre-duty rest where possible")
        st.write("- Reduce operational complexity")
        st.write("- Monitor cumulative fatigue trend")
        st.write("- Review additional duty assignments carefully")
    else:
        st.error("High fatigue exposure detected.")
        st.write("- Reevaluate current duty assignment")
        st.write("- Increase rest opportunity before next duty")
        st.write("- Consider reducing segments or delaying reassignment")
        st.write("- Escalate to operations or safety review")
        st.write("- Apply fatigue mitigation before release to duty")

st.divider()
st.caption("Prototype for demonstration purposes only. AeroVigil is not an FAA-approved dispatch, scheduling, or medical decision tool.")
