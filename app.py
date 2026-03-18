import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="AeroVigil | Airline Dashboard Mode",
    layout="wide"
)

# ---------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------
def calculate_fatigue_score(
    duty_hours: float,
    segments: int,
    timezone_changes: int,
    rest_hours: float,
    circadian_disruption: str
) -> int:
    """
    Calculates a fatigue risk score from 0 to 100.
    Higher score = higher fatigue risk.
    """
    score = 0

    # Duty hours
    if duty_hours <= 8:
        score += 10
    elif duty_hours <= 10:
        score += 20
    elif duty_hours <= 12:
        score += 30
    else:
        score += 40

    # Flight segments
    if segments <= 2:
        score += 5
    elif segments <= 4:
        score += 15
    else:
        score += 25

    # Time zone changes
    if timezone_changes == 0:
        score += 0
    elif timezone_changes <= 2:
        score += 10
    else:
        score += 20

    # Rest hours
    if rest_hours >= 12:
        score += 0
    elif rest_hours >= 10:
        score += 10
    elif rest_hours >= 8:
        score += 20
    else:
        score += 30

    # Circadian disruption
    circadian_map = {
        "Low": 5,
        "Moderate": 15,
        "High": 25
    }
    score += circadian_map.get(circadian_disruption, 0)

    return max(0, min(100, score))


def fatigue_category(score: int) -> str:
    if score < 35:
        return "LOW"
    elif score < 70:
        return "MODERATE"
    else:
        return "HIGH"


def fatigue_recommendation(score: int, legal_ok: bool) -> str:
    if not legal_ok:
        return "Not legal to operate. Reassign or remove this crew pairing immediately."
    if score < 35:
        return "Fatigue risk appears manageable. Continue monitoring."
    elif score < 70:
        return "Moderate fatigue risk. Consider mitigation such as schedule adjustment, extended rest, or crew support."
    else:
        return "High fatigue risk. Consider crew swap, reassignment, or delaying operation if alternatives are limited."


def legal_status(duty_hours: float, rest_hours: float) -> tuple:
    """
    Simplified operational legality check.
    This is NOT FAA-certified logic — demo only.
    """
    legal_duty_limit = 14
    minimum_rest = 10

    is_legal = (duty_hours <= legal_duty_limit) and (rest_hours >= minimum_rest)

    if is_legal:
        return True, "YES"
    return False, "NO"


def build_trend_data(base_duty, base_segments, base_tz, base_rest, base_circadian):
    """
    Creates a simple 4-day fatigue trend based on user inputs.
    """
    days = ["Day 1", "Day 2", "Day 3", "Day 4"]
    adjustments = [
        (0.0, 0, 0, 0.0),
        (1.0, 1, 0, -1.0),
        (2.0, 1, 1, -2.0),
        (0.5, 0, 0, 1.0),
    ]

    trend_scores = []
    for duty_adj, seg_adj, tz_adj, rest_adj in adjustments:
        score = calculate_fatigue_score(
            duty_hours=max(0, base_duty + duty_adj),
            segments=max(1, base_segments + seg_adj),
            timezone_changes=max(0, base_tz + tz_adj),
            rest_hours=max(0, base_rest + rest_adj),
            circadian_disruption=base_circadian,
        )
        trend_scores.append(score)

    return pd.DataFrame({
        "Day": days,
        "Fatigue Score": trend_scores
    })


# ---------------------------------------------------
# HEADER
# ---------------------------------------------------
st.title("✈️ AeroVigil")
st.subheader("Airline Dashboard Mode")
st.caption("Predictive fatigue analytics for airline safety teams and operational decision support")

st.markdown("---")

# ---------------------------------------------------
# SIDEBAR INPUTS
# ---------------------------------------------------
st.sidebar.header("Flight / Crew Inputs")

duty_hours = st.sidebar.slider("Duty Hours", 4.0, 18.0, 10.0, 0.5)
segments = st.sidebar.slider("Flight Segments", 1, 6, 3)
timezone_changes = st.sidebar.slider("Time Zone Changes", 0, 6, 1)
rest_hours = st.sidebar.slider("Rest Hours Before Duty", 6.0, 16.0, 10.0, 0.5)
circadian_disruption = st.sidebar.selectbox(
    "Circadian Disruption",
    ["Low", "Moderate", "High"]
)

st.sidebar.markdown("---")
st.sidebar.header("IROPs Simulator")

delay_hours = st.sidebar.slider("Operational Delay (Hours)", 0.0, 6.0, 2.0, 0.5)
extra_segments = st.sidebar.slider("Additional Segments Due to Reassignment", 0, 3, 1)
extra_timezone = st.sidebar.slider("Additional Time Zone Changes", 0, 3, 0)
rest_reduction = st.sidebar.slider("Reduced Rest Impact (Hours)", 0.0, 4.0, 1.0, 0.5)

# ---------------------------------------------------
# BASE SCENARIO
# ---------------------------------------------------
base_score = calculate_fatigue_score(
    duty_hours=duty_hours,
    segments=segments,
    timezone_changes=timezone_changes,
    rest_hours=rest_hours,
    circadian_disruption=circadian_disruption
)
base_category = fatigue_category(base_score)
base_legal_ok, base_legal_text = legal_status(duty_hours, rest_hours)
base_recommendation = fatigue_recommendation(base_score, base_legal_ok)

# ---------------------------------------------------
# IROPS SCENARIO
# ---------------------------------------------------
irrops_duty = duty_hours + delay_hours
irrops_segments = segments + extra_segments
irrops_timezone = timezone_changes + extra_timezone
irrops_rest = max(0.0, rest_hours - rest_reduction)

irrops_score = calculate_fatigue_score(
    duty_hours=irrops_duty,
    segments=irrops_segments,
    timezone_changes=irrops_timezone,
    rest_hours=irrops_rest,
    circadian_disruption=circadian_disruption
)
irrops_category = fatigue_category(irrops_score)
irrops_legal_ok, irrops_legal_text = legal_status(irrops_duty, irrops_rest)
irrops_recommendation = fatigue_recommendation(irrops_score, irrops_legal_ok)

# ---------------------------------------------------
# TOP KPI ROW
# ---------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Base Fatigue Score", base_score)

with col2:
    st.metric("Base Risk Category", base_category)

with col3:
    st.metric("Legal to Operate", base_legal_text)

with col4:
    score_delta = irrops_score - base_score
    st.metric("IROPs Scenario Score", irrops_score, delta=score_delta)

st.markdown("---")

# ---------------------------------------------------
# LEGAL VS RISK DECISION PANELS
# ---------------------------------------------------
left, right = st.columns(2)

with left:
    st.markdown("## Base Operation")
    st.info(
        f"""
**Decision Panel**
- **Legal to Operate:** {base_legal_text}
- **Fatigue Risk:** {base_category}
- **Duty Hours:** {duty_hours}
- **Rest Hours:** {rest_hours}
- **Segments:** {segments}
- **Time Zone Changes:** {timezone_changes}
- **Circadian Disruption:** {circadian_disruption}
"""
    )
    st.success(f"**Recommendation:** {base_recommendation}") if base_legal_ok and base_score < 70 else st.warning(
        f"**Recommendation:** {base_recommendation}"
    )

with right:
    st.markdown("## IROPs / Disruption Scenario")
    st.info(
        f"""
**Decision Panel**
- **Legal to Operate:** {irrops_legal_text}
- **Fatigue Risk:** {irrops_category}
- **Duty Hours:** {irrops_duty}
- **Rest Hours:** {irrops_rest}
- **Segments:** {irrops_segments}
- **Time Zone Changes:** {irrops_timezone}
- **Operational Delay:** {delay_hours} hrs
"""
    )
    if not irrops_legal_ok or irrops_score >= 70:
        st.error(f"**Recommendation:** {irrops_recommendation}")
    else:
        st.warning(f"**Recommendation:** {irrops_recommendation}")

st.markdown("---")

# ---------------------------------------------------
# SCENARIO COMPARISON TABLE
# ---------------------------------------------------
st.markdown("## Scenario Comparison")

comparison_df = pd.DataFrame({
    "Scenario": ["Original Plan", "IROPs Adjusted Plan"],
    "Duty Hours": [duty_hours, irrops_duty],
    "Segments": [segments, irrops_segments],
    "Time Zone Changes": [timezone_changes, irrops_timezone],
    "Rest Hours": [rest_hours, irrops_rest],
    "Legal to Operate": [base_legal_text, irrops_legal_text],
    "Fatigue Score": [base_score, irrops_score],
    "Risk Category": [base_category, irrops_category]
})

st.dataframe(comparison_df, use_container_width=True)

# ---------------------------------------------------
# TREND CHART
# ---------------------------------------------------
st.markdown("## 4-Day Fatigue Trend")

trend_df = build_trend_data(
    base_duty=duty_hours,
    base_segments=segments,
    base_tz=timezone_changes,
    base_rest=rest_hours,
    base_circadian=circadian_disruption
)

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(trend_df["Day"], trend_df["Fatigue Score"], marker="o")
ax.set_title("Projected Fatigue Trend")
ax.set_ylabel("Fatigue Score")
ax.set_xlabel("Duty Period")
ax.set_ylim(0, 100)
ax.grid(True)

st.pyplot(fig)

# ---------------------------------------------------
# AIRLINE OPS NOTES
# ---------------------------------------------------
st.markdown("---")
st.markdown("## Operations Notes")

if irrops_score > base_score:
    st.write(
        f"- The IROPs scenario increases fatigue exposure by **{irrops_score - base_score} points**."
    )
else:
    st.write("- The disruption scenario did not increase fatigue exposure.")

if base_legal_ok and irrops_legal_ok and irrops_score >= 70:
    st.write("- Crew may remain legal under basic duty/rest thresholds, but fatigue risk is still elevated.")
if not irrops_legal_ok:
    st.write("- Disruption scenario crosses simplified legality limits and should trigger reassignment review.")
if timezone_changes >= 2 or irrops_timezone >= 2:
    st.write("- Multiple time-zone transitions may increase circadian fatigue burden.")
if segments >= 4 or irrops_segments >= 4:
    st.write("- Higher segment count may increase workload and cumulative fatigue risk.")

# ---------------------------------------------------
# BOTTOM DISCLAIMER
# ---------------------------------------------------
st.markdown("---")
st.caption(
    "Disclaimer: AeroVigil is a prototype decision-support tool for demonstration purposes only. "
    "It does not replace FAA regulations, company policy, dispatch authority, crew scheduling processes, "
    "or formal fatigue risk management systems."
)
