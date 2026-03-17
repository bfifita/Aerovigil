import streamlit as st
import pandas as pd

def fatigue_risk_score(duty_hours, segments, timezone_changes, rest_hours, circadian_disruption):
    score = 0

    if duty_hours > 10:
        score += (duty_hours - 10) * 5

    score += segments * 3
    score += timezone_changes * 4

    if rest_hours < 10:
        score += (10 - rest_hours) * 6

    if circadian_disruption:
        score += 15

    return min(score, 100)

def risk_level(score):
    if score < 30:
        return "LOW"
    elif score < 60:
        return "MODERATE"
    elif score < 80:
        return "HIGH"
    return "CRITICAL"

st.set_page_config(page_title="AeroVigil", layout="wide")

st.title("AeroVigil")
st.subheader("CSV Crew Fatigue Risk Analyzer")
st.caption("Prototype for airline safety teams and SMS programs")

uploaded_file = st.file_uploader("Upload crew schedule CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
else:
    st.info("No file uploaded yet. Using sample data from crew_data.csv format.")
    df = pd.DataFrame({
        "Pilot": ["John", "Sarah", "Mike", "Lisa"],
        "Duty Hours": [12, 9, 14, 10],
        "Segments": [4, 3, 5, 2],
        "Time Zones": [2, 1, 3, 0],
        "Rest Hours": [8, 12, 7, 11],
        "Circadian Disruption": ["Yes", "No", "Yes", "No"]
    })

def to_bool(value):
    return str(value).strip().lower() in ["yes", "true", "1"]

df["Fatigue Score"] = df.apply(
    lambda row: fatigue_risk_score(
        row["Duty Hours"],
        row["Segments"],
        row["Time Zones"],
        row["Rest Hours"],
        to_bool(row["Circadian Disruption"])
    ),
    axis=1
)

df["Risk"] = df["Fatigue Score"].apply(risk_level)
df = df.sort_values(by="Fatigue Score", ascending=False)

st.markdown("### Crew Fatigue Risk Results")
st.dataframe(df, use_container_width=True)

high_risk = df[df["Fatigue Score"] >= 60]

st.markdown("### Operational Alerts")
if not high_risk.empty:
    st.warning(f"{len(high_risk)} crew member(s) flagged as HIGH or CRITICAL fatigue risk.")
    st.dataframe(high_risk[["Pilot", "Fatigue Score", "Risk"]], use_container_width=True)
else:
    st.success("No crew members currently flagged as HIGH or CRITICAL risk.")

highest = df.iloc[0]
st.markdown("### Highest Risk Crew Member")
st.metric("Pilot", highest["Pilot"])
st.metric("Fatigue Score", highest["Fatigue Score"])
st.metric("Risk Level", highest["Risk"])
