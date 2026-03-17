import streamlit as st
from fatigue_calculator import calculate_fatigue_score

st.set_page_config(page_title="AeroVigil", layout="wide")

st.title("AeroVigil")
st.subheader("Predictive Fatigue Risk Analytics for Aviation Safety")
st.write(
    "A prototype aviation safety tool for estimating crew fatigue risk using duty time, segments, rest, timezone changes, and circadian disruption."
)

st.divider()

# Sidebar inputs
st.sidebar.header("Crew Duty Inputs")
duty_hours = st.sidebar.slider("Duty Hours", 0, 16, 8)
segments = st.sidebar.slider("Flight Segments", 1, 8, 2)
timezone_changes = st.sidebar.slider("Time Zone Changes", 0, 6, 0)
rest_hours = st.sidebar.slider("Rest Hours Before Duty", 0, 16, 10)
circadian_disruption = st.sidebar.slider("Circadian Disruption Level", 0, 10, 3)

# Main panel preview
st.subheader("Current Crew Input Summary")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Duty Hours", duty_hours)
    st.metric("Flight Segments", segments)

with col2:
    st.metric("Timezone Changes", timezone_changes)
    st.metric("Rest Hours", rest_hours)

with col3:
    st.metric("Circadian Disruption", circadian_disruption)

st.divider()

if st.button("Calculate Fatigue Risk", width="stretch"):
    score = calculate_fatigue_score(
        duty_hours,
        segments,
        timezone_changes,
        rest_hours,
        circadian_disruption
    )

    # Risk classification
    if score < 35:
        risk_level = "LOW"
        status_message = "Crew member appears fit for duty based on current inputs."
        gauge_color = "green"
    elif score < 65:
        risk_level = "MODERATE"
        status_message = "Fatigue risk is elevated. Consider monitoring or mitigation strategies."
        gauge_color = "orange"
    else:
        risk_level = "HIGH"
        status_message = "High fatigue risk detected. Schedule review or fatigue mitigation recommended."
        gauge_color = "red"

    st.subheader("Fatigue Risk Results")
    result_col1, result_col2 = st.columns([2, 1])

    with result_col1:
        st.subheader(f"Fatigue Score: {score}/100")
        st.progress(score / 100)

        if risk_level == "LOW":
            st.success(f"Fatigue Risk Level: {risk_level}")
        elif risk_level == "MODERATE":
            st.warning(f"Fatigue Risk Level: {risk_level}")
        else:
            st.error(f"Fatigue Risk Level: {risk_level}")

        st.write(status_message)

    with result_col2:
        st.metric("Operational Status", risk_level)

    st.divider()
    st.subheader("Fatigue Risk Gauge")

    st.markdown(
        f"""
        <div style="background-color:{gauge_color};
                    padding:25px;
                    border-radius:12px;
                    text-align:center;
                    font-size:28px;
                    color:white;
                    font-weight:bold;">
            Fatigue Risk Score: {score}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()
    st.subheader("Mitigation Recommendations")

    recommendations = []

    if duty_hours >= 12:
        recommendations.append("Reduce duty period or split assignments to lower fatigue exposure.")
    if segments >= 4:
        recommendations.append("Reduce the number of flight segments to decrease workload and task saturation.")
    if timezone_changes >= 2:
        recommendations.append("Limit additional timezone transitions or allow more adaptation time.")
    if rest_hours <= 8:
        recommendations.append("Increase pre-duty rest opportunity before assigning the next trip.")
    if circadian_disruption >= 6:
        recommendations.append("Avoid scheduling during peak circadian low periods when possible.")

    if not recommendations:
        recommendations.append("No major fatigue mitigations indicated from the current inputs.")

    for rec in recommendations:
        st.write(f"• {rec}")

    st.divider()
    st.subheader("Operational Summary")

    st.info(
        f"""
AeroVigil assessment complete.

Risk Level: {risk_level}
Fatigue Score: {score}/100

This prototype suggests that current scheduling conditions create a {risk_level.lower()} fatigue risk profile.
Use this result as a decision-support signal for safety review, crew planning, and mitigation action.
        """
    )
