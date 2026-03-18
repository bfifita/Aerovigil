import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fatigue_calculator import calculate_fatigue_score

st.set_page_config(page_title="AeroVigil", layout="wide")

# -------------------------------------------------
# Helper functions
# -------------------------------------------------
def classify_risk(score):
    if score < 35:
        return "LOW"
    elif score < 70:
        return "MODERATE"
    return "HIGH"


def get_recommendation(score):
    if score < 35:
        return "Crew appears fit for duty. Continue monitoring."
    elif score < 70:
        return "Moderate fatigue risk detected. Consider added rest or schedule review."
    return "High fatigue risk detected. Recommend immediate mitigation and scheduling review."


def get_alert_message(score):
    if score < 35:
        return "Low operational fatigue risk."
    elif score < 70:
        return "Caution: Moderate fatigue risk may affect performance."
    return "Warning: High fatigue risk may affect crew safety and operational reliability."


def build_trend_data(base_score):
    days = ["Day 1", "Day 2", "Day 3", "Day 4"]
    trend_scores = [
        max(0, min(100, base_score - 12)),
        max(0, min(100, base_score - 5)),
        max(0, min(100, base_score + 4)),
        max(0, min(100, base_score)),
    ]
    return pd.DataFrame({"Day": days, "Fatigue Score": trend_scores})


# -------------------------------------------------
# Title / Header
# -------------------------------------------------
st.title("AeroVigil")
st.subheader("Predictive Fatigue Risk Analytics for Aviation Safety")
st.write(
    "AeroVigil is a prototype aviation safety dashboard designed to estimate "
    "crew fatigue risk using duty time, flight segments, rest, timezone changes, "
    "and circadian disruption."
)

st.divider()

# -------------------------------------------------
# Sidebar Inputs
# -------------------------------------------------
st.sidebar.header("Crew Duty Inputs")

duty_hours = st.sidebar.slider("Duty Hours", 0, 16, 8)
segments = st.sidebar.slider("Flight Segments", 1, 8, 2)
timezone_changes = st.sidebar.slider("Time Zone Changes", 0, 6, 0)
rest_hours = st.sidebar.slider("Rest Hours Before Duty", 0, 16, 10)
circadian_disruption = st.sidebar.slider("Circadian Disruption Level", 0, 10, 3)

# -------------------------------------------------
# Main fatigue score
# -------------------------------------------------
score = calculate_fatigue_score(
    duty_hours,
    segments,
    timezone_changes,
    rest_hours,
    circadian_disruption
)

risk_level = classify_risk(score)
recommendation = get_recommendation(score)
alert_message = get_alert_message(score)

# -------------------------------------------------
# Top Dashboard Metrics
# -------------------------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Fatigue Risk Score", f"{score}/100")

with col2:
    st.metric("Risk Level", risk_level)

with col3:
    st.metric("Operational Recommendation", "Review Status")

st.divider()

# -------------------------------------------------
# Alert Section
# -------------------------------------------------
st.subheader("Operational Alert")

if risk_level == "LOW":
    st.success(alert_message)
elif risk_level == "MODERATE":
    st.warning(alert_message)
else:
    st.error(alert_message)

st.write(f"**Recommendation:** {recommendation}")

# -------------------------------------------------
# Trend Chart
# -------------------------------------------------
st.subheader("Fatigue Risk Trend")
trend_df = build_trend_data(score)

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(trend_df["Day"], trend_df["Fatigue Score"], marker="o")
ax.set_xlabel("Duty Period")
ax.set_ylabel("Fatigue Score")
ax.set_title("4-Day Fatigue Risk Trend")
ax.set_ylim(0, 100)
st.pyplot(fig)

# -------------------------------------------------
# Detailed Driver Breakdown
# -------------------------------------------------
st.subheader("Fatigue Driver Summary")

driver_data = pd.DataFrame(
    {
        "Factor": [
            "Duty Hours",
            "Flight Segments",
            "Timezone Changes",
            "Rest Hours",
            "Circadian Disruption",
        ],
        "Input Value": [
            duty_hours,
            segments,
            timezone_changes,
            rest_hours,
            circadian_disruption,
        ],
    }
)

st.dataframe(driver_data, use_container_width=True)

# -------------------------------------------------
# Scenario Comparison Tool
# -------------------------------------------------
st.divider()
st.subheader("Scenario Comparison Tool")

left_col, right_col = st.columns(2)

with left_col:
    st.markdown("### Scenario A")
    duty_a = st.slider("Duty Hours (A)", 0, 16, 8, key="duty_a")
    segments_a = st.slider("Segments (A)", 1, 8, 2, key="segments_a")
    timezone_a = st.slider("Timezone Changes (A)", 0, 6, 0, key="timezone_a")
    rest_a = st.slider("Rest Hours (A)", 0, 16, 10, key="rest_a")
    circadian_a = st.slider("Circadian Disruption (A)", 0, 10, 3, key="circadian_a")

with right_col:
    st.markdown("### Scenario B")
    duty_b = st.slider("Duty Hours (B)", 0, 16, 10, key="duty_b")
    segments_b = st.slider("Segments (B)", 1, 8, 3, key="segments_b")
    timezone_b = st.slider("Timezone Changes (B)", 0, 6, 1, key="timezone_b")
    rest_b = st.slider("Rest Hours (B)", 0, 16, 8, key="rest_b")
    circadian_b = st.slider("Circadian Disruption (B)", 0, 10, 5, key="circadian_b")

score_a = calculate_fatigue_score(duty_a, segments_a, timezone_a, rest_a, circadian_a)
score_b = calculate_fatigue_score(duty_b, segments_b, timezone_b, rest_b, circadian_b)

risk_a = classify_risk(score_a)
risk_b = classify_risk(score_b)

compare_df = pd.DataFrame(
    {
        "Scenario": ["Scenario A", "Scenario B"],
        "Fatigue Score": [score_a, score_b],
        "Risk Level": [risk_a, risk_b],
    }
)

st.dataframe(compare_df, use_container_width=True)

if score_a < score_b:
    st.info("Scenario A appears safer based on the current fatigue inputs.")
elif score_b < score_a:
    st.info("Scenario B appears safer based on the current fatigue inputs.")
else:
    st.info("Both scenarios currently show the same fatigue risk score.")

# -------------------------------------------------
# Footer / Disclaimer
# -------------------------------------------------
st.divider()
st.caption(
    "Disclaimer: AeroVigil is a prototype decision-support tool for demonstration "
    "purposes only and does not replace approved fatigue risk management systems, "
    "operational control procedures, or regulatory safety assessments."
)
