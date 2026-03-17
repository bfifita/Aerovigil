import streamlit as st
from fatigue_calculator import calculate_fatigue_score

st.set_page_config(page_title="AeroVigil", layout="wide")

st.title("AeroVigil")
st.subheader("Predictive Fatigue Risk Analytics for Aviation Safety")

st.write(
    "Enter crew scheduling inputs below to estimate fatigue risk based on duty time, flight segments, circadian disruption, and rest."
)

st.divider()

# Crew scheduling inputs
duty_hours = st.slider("Duty Hours", 0, 16, 8)
segments = st.slider("Flight Segments", 1, 8, 2)
timezone_changes = st.slider("Time Zone Changes", 0, 6, 0)
rest_hours = st.slider("Rest Hours Before Duty", 0, 16, 10)
circadian_disruption = st.slider("Circadian Disruption Level", 0, 10, 3)

# Calculate fatigue score
if st.button("Calculate Fatigue Risk", width="stretch"):

    score = calculate_fatigue_score(
        duty_hours,
        segments,
        timezone_changes,
        rest_hours,
        circadian_disruption
    )

    st.divider()

    st.subheader(f"Fatigue Score: {score}/100")
    st.progress(score / 100)

    # Risk classification
    if score < 35:
        risk_level = "LOW"
        st.success(f"Fatigue Risk Level: {risk_level}")
        st.write("Crew member appears fit for duty based on current inputs.")

    elif score < 65:
        risk_level = "MODERATE"
        st.warning(f"Fatigue Risk Level: {risk_level}")
        st.write("Fatigue risk is elevated. Consider monitoring or mitigation strategies.")

    else:
        risk_level = "HIGH"
        st.error(f"Fatigue Risk Level: {risk_level}")
        st.write("High fatigue risk detected. Schedule review or fatigue mitigation recommended.")

    st.metric("Operational Status", risk_level)

    st.divider()
    st.subheader("Fatigue Risk Gauge")

    # Gauge color logic
    gauge_color = "green"
    if score >= 65:
        gauge_color = "red"
    elif score >= 35:
        gauge_color = "orange"

    # Gauge display
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
