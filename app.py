import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="AeroVigil", page_icon="✈️", layout="wide")


# -------------------------------
# HELPERS
# -------------------------------
def calculate_fatigue_score(
    duty_hours,
    segments,
    timezone_changes,
    rest_hours,
    circadian_disruption,
    delay_minutes=0,
    reassignment=False,
    extra_segment=False,
    overnight_disruption=False,
    short_notice=False
):
    score = 0
    score += duty_hours * 3
    score += segments * 4
    score += timezone_changes * 5
    score += circadian_disruption * 4
    score -= rest_hours * 2

    # IROPs penalties
    score += delay_minutes / 15
    if reassignment:
        score += 8
    if extra_segment:
        score += 6
    if overnight_disruption:
        score += 10
    if short_notice:
        score += 7

    score = max(0, min(100, round(score)))
    return score


def get_risk_level(score):
    if score < 35:
        return "LOW", "🟢"
    elif score < 65:
        return "MODERATE", "🟡"
    else:
        return "HIGH", "🔴"


def get_action_recommendation(score, duty_hours, rest_hours, segments, reassignment, delay_minutes):
    actions = []

    if score >= 65:
        actions.append("Review crew assignment before release to duty")
    if rest_hours < 8:
        actions.append("Increase rest opportunity if operationally feasible")
    if duty_hours >= 12:
        actions.append("Reduce duty exposure or consider alternate crew")
    if segments >= 5:
        actions.append("Consider reducing segment load")
    if reassignment:
        actions.append("Reassignment increases operational strain; review crew swap carefully")
    if delay_minutes >= 90:
        actions.append("Extended delay exposure may elevate disruption fatigue risk")
    if not actions:
        actions.append("Current schedule appears manageable; continue monitoring")

    return actions


def build_plan_score(
    duty_hours,
    segments,
    timezone_changes,
    rest_hours,
    circadian_disruption,
    delay_minutes,
    reassignment,
    extra_segment,
    overnight_disruption,
    short_notice
):
    return calculate_fatigue_score(
        duty_hours=duty_hours,
        segments=segments,
        timezone_changes=timezone_changes,
        rest_hours=rest_hours,
        circadian_disruption=circadian_disruption,
        delay_minutes=delay_minutes,
        reassignment=reassignment,
        extra_segment=extra_segment,
        overnight_disruption=overnight_disruption,
        short_notice=short_notice
    )


def compare_plans(score_a, score_b):
    if score_a < score_b:
        return "Plan A is the lower-risk operational option."
    elif score_b < score_a:
        return "Plan B is the lower-risk operational option."
    return "Both plans currently show the same fatigue risk score."


def crew_suggested_action(score):
    if score >= 65:
        return "Review / Adjust"
    elif score >= 35:
        return "Monitor"
    return "Acceptable"


# -------------------------------
# HEADER
# -------------------------------
st.title("✈️ AeroVigil")
st.subheader("Operational Fatigue Decision Support for Airline Disruptions")
st.write(
    "AeroVigil is a prototype aviation decision-support dashboard designed to help operations teams "
    "compare legal options, identify elevated fatigue exposure, and make safer operational choices during disruptions."
)

st.divider()


# -------------------------------
# SIDEBAR: BASELINE CREW INPUT
# -------------------------------
st.sidebar.header("Baseline Crew Inputs")
duty_hours = st.sidebar.slider("Duty Hours", 0, 16, 10)
segments = st.sidebar.slider("Flight Segments", 1, 8, 3)
timezone_changes = st.sidebar.slider("Time Zone Changes", 0, 6, 1)
rest_hours = st.sidebar.slider("Rest Hours Before Duty", 0, 16, 9)
circadian_disruption = st.sidebar.slider("Circadian Disruption Level", 0, 10, 4)

st.sidebar.divider()

# -------------------------------
# SIDEBAR: IROPs MODE
# -------------------------------
st.sidebar.header("IROPs / Disruption Inputs")
irops_mode = st.sidebar.toggle("Enable IROPs Mode", value=False)

if irops_mode:
    delay_minutes = st.sidebar.slider("Delay Minutes", 0, 300, 90, step=15)
    reassignment = st.sidebar.checkbox("Crew Reassignment Required", value=True)
    extra_segment = st.sidebar.checkbox("Additional Segment Added", value=False)
    overnight_disruption = st.sidebar.checkbox("Overnight Disruption", value=False)
    short_notice = st.sidebar.checkbox("Short-Notice Reporting", value=False)
else:
    delay_minutes = 0
    reassignment = False
    extra_segment = False
    overnight_disruption = False
    short_notice = False


# -------------------------------
# BASELINE VS DISRUPTED SCORE
# -------------------------------
baseline_score = calculate_fatigue_score(
    duty_hours=duty_hours,
    segments=segments,
    timezone_changes=timezone_changes,
    rest_hours=rest_hours,
    circadian_disruption=circadian_disruption
)

disrupted_score = calculate_fatigue_score(
    duty_hours=duty_hours,
    segments=segments,
    timezone_changes=timezone_changes,
    rest_hours=rest_hours,
    circadian_disruption=circadian_disruption,
    delay_minutes=delay_minutes,
    reassignment=reassignment,
    extra_segment=extra_segment,
    overnight_disruption=overnight_disruption,
    short_notice=short_notice
)

active_score = disrupted_score if irops_mode else baseline_score
risk_level, risk_icon = get_risk_level(active_score)
recommendations = get_action_recommendation(
    active_score, duty_hours, rest_hours, segments, reassignment, delay_minutes
)

# -------------------------------
# ALERT BANNER
# -------------------------------
if risk_level == "HIGH":
    st.error(
        f"🚨 HIGH FATIGUE RISK — Score: {active_score}/100. "
        f"Immediate operational review recommended."
    )
elif risk_level == "MODERATE":
    st.warning(
        f"🟡 MODERATE FATIGUE RISK — Score: {active_score}/100. "
        f"Monitor exposure and evaluate mitigations."
    )
else:
    st.success(
        f"🟢 LOW FATIGUE RISK — Score: {active_score}/100. "
        f"Current exposure appears manageable."
    )

if irops_mode:
    st.info(
        "⚠️ IROPs Mode is active. AeroVigil is applying disruption-related fatigue penalties "
        "to reflect operational strain beyond simple legal compliance."
    )

st.divider()

# -------------------------------
# KPI CARDS
# -------------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Active Fatigue Score", f"{active_score}/100")

with col2:
    st.metric("Risk Level", risk_level)

with col3:
    st.metric("Baseline Score", f"{baseline_score}/100")

with col4:
    delta_value = active_score - baseline_score
    st.metric("Disruption Impact", f"{delta_value:+}" if irops_mode else "0")

st.divider()

# -------------------------------
# TABS
# -------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Executive Dashboard",
    "IROPs Impact",
    "Plan A vs Plan B",
    "Crew Risk Table",
    "Recommendation Engine"
])

# -------------------------------
# TAB 1: EXECUTIVE DASHBOARD
# -------------------------------
with tab1:
    st.subheader("Executive Dashboard")

    left, right = st.columns([1.4, 1])

    with left:
        summary_df = pd.DataFrame({
            "Factor": [
                "Duty Hours",
                "Flight Segments",
                "Time Zone Changes",
                "Rest Hours Before Duty",
                "Circadian Disruption Level",
                "Delay Minutes",
                "Crew Reassignment",
                "Additional Segment",
                "Overnight Disruption",
                "Short-Notice Reporting"
            ],
            "Value": [
                duty_hours,
                segments,
                timezone_changes,
                rest_hours,
                circadian_disruption,
                delay_minutes,
                "Yes" if reassignment else "No",
                "Yes" if extra_segment else "No",
                "Yes" if overnight_disruption else "No",
                "Yes" if short_notice else "No"
            ]
        })
        st.markdown("### Current Operational Inputs")
        st.dataframe(summary_df, use_container_width=True)

    with right:
        st.markdown("### Operational Risk Status")
        if risk_level == "HIGH":
            st.error(f"{risk_icon} {risk_level}")
        elif risk_level == "MODERATE":
            st.warning(f"{risk_icon} {risk_level}")
        else:
            st.success(f"{risk_icon} {risk_level}")

        st.markdown("### Key Insight")
        st.info(
            "The real gap is not fatigue awareness alone — it is actionable decision support "
            "during disruptions when multiple legal options may exist."
        )

# -------------------------------
# TAB 2: IROPs IMPACT
# -------------------------------
with tab2:
    st.subheader("IROPs Impact Analysis")

    i1, i2 = st.columns(2)

    with i1:
        st.markdown("### Baseline Conditions")
        st.metric("Baseline Score", f"{baseline_score}/100")
        base_level, _ = get_risk_level(baseline_score)
        st.write(f"Risk Level: {base_level}")

    with i2:
        st.markdown("### Disruption Conditions")
        st.metric("Disrupted Score", f"{disrupted_score}/100", delta=disrupted_score - baseline_score)
        disrupted_level, _ = get_risk_level(disrupted_score)
        st.write(f"Risk Level: {disrupted_level}")

    impact_df = pd.DataFrame({
        "Scenario": ["Baseline", "IROPs / Disrupted"],
        "Fatigue Score": [baseline_score, disrupted_score]
    })

    fig1, ax1 = plt.subplots(figsize=(8, 4))
    ax1.bar(impact_df["Scenario"], impact_df["Fatigue Score"])
    ax1.set_title("Baseline vs Disruption Fatigue Impact")
    ax1.set_ylabel("Fatigue Score")
    ax1.set_ylim(0, 100)
    st.pyplot(fig1)

    st.markdown("### Why the score changed")
    change_notes = []
    if delay_minutes > 0:
        change_notes.append(f"- Delay exposure added operational strain ({delay_minutes} minutes)")
    if reassignment:
        change_notes.append("- Crew reassignment increased disruption complexity")
    if extra_segment:
        change_notes.append("- Additional segment increased workload exposure")
    if overnight_disruption:
        change_notes.append("- Overnight disruption elevated cumulative fatigue risk")
    if short_notice:
        change_notes.append("- Short-notice reporting reduced predictability and recovery")

    if change_notes:
        for note in change_notes:
            st.write(note)
    else:
        st.write("- No additional disruption penalties are currently active")

# -------------------------------
# TAB 3: PLAN A VS PLAN B
# -------------------------------
with tab3:
    st.subheader("Plan A vs Plan B Scenario Comparison")

    st.markdown("### Plan A")
    a1, a2, a3 = st.columns(3)
    with a1:
        plan_a_duty = st.slider("Plan A Duty Hours", 0, 16, duty_hours, key="a_duty")
        plan_a_segments = st.slider("Plan A Flight Segments", 1, 8, segments, key="a_segments")
    with a2:
        plan_a_rest = st.slider("Plan A Rest Hours", 0, 16, rest_hours, key="a_rest")
        plan_a_tz = st.slider("Plan A Time Zone Changes", 0, 6, timezone_changes, key="a_tz")
    with a3:
        plan_a_circadian = st.slider("Plan A Circadian Disruption", 0, 10, circadian_disruption, key="a_circadian")
        plan_a_delay = st.slider("Plan A Delay Minutes", 0, 300, delay_minutes, step=15, key="a_delay")

    plan_a_reassignment = st.checkbox("Plan A Reassignment", value=reassignment, key="a_reassign")
    plan_a_extra_segment = st.checkbox("Plan A Additional Segment", value=extra_segment, key="a_extra_seg")
    plan_a_overnight = st.checkbox("Plan A Overnight Disruption", value=overnight_disruption, key="a_overnight")
    plan_a_short_notice = st.checkbox("Plan A Short-Notice Reporting", value=short_notice, key="a_short_notice")

    st.markdown("### Plan B")
    b1, b2, b3 = st.columns(3)
    with b1:
        plan_b_duty = st.slider("Plan B Duty Hours", 0, 16, max(0, duty_hours - 1), key="b_duty")
        plan_b_segments = st.slider("Plan B Flight Segments", 1, 8, max(1, segments - 1), key="b_segments")
    with b2:
        plan_b_rest = st.slider("Plan B Rest Hours", 0, 16, min(16, rest_hours + 2), key="b_rest")
        plan_b_tz = st.slider("Plan B Time Zone Changes", 0, 6, timezone_changes, key="b_tz")
    with b3:
        plan_b_circadian = st.slider("Plan B Circadian Disruption", 0, 10, max(0, circadian_disruption - 1), key="b_circadian")
        plan_b_delay = st.slider("Plan B Delay Minutes", 0, 300, max(0, delay_minutes - 30), step=15, key="b_delay")

    plan_b_reassignment = st.checkbox("Plan B Reassignment", value=False, key="b_reassign")
    plan_b_extra_segment = st.checkbox("Plan B Additional Segment", value=False, key="b_extra_seg")
    plan_b_overnight = st.checkbox("Plan B Overnight Disruption", value=False, key="b_overnight")
    plan_b_short_notice = st.checkbox("Plan B Short-Notice Reporting", value=False, key="b_short_notice")

    plan_a_score = build_plan_score(
        plan_a_duty, plan_a_segments, plan_a_tz, plan_a_rest, plan_a_circadian,
        plan_a_delay, plan_a_reassignment, plan_a_extra_segment, plan_a_overnight, plan_a_short_notice
    )

    plan_b_score = build_plan_score(
        plan_b_duty, plan_b_segments, plan_b_tz, plan_b_rest, plan_b_circadian,
        plan_b_delay, plan_b_reassignment, plan_b_extra_segment, plan_b_overnight, plan_b_short_notice
    )

    score_col1, score_col2 = st.columns(2)
    with score_col1:
        level_a, icon_a = get_risk_level(plan_a_score)
        st.metric("Plan A Score", f"{plan_a_score}/100")
        st.write(f"Risk Level: {icon_a} {level_a}")
    with score_col2:
        level_b, icon_b = get_risk_level(plan_b_score)
        st.metric("Plan B Score", f"{plan_b_score}/100")
        st.write(f"Risk Level: {icon_b} {level_b}")

    compare_df = pd.DataFrame({
        "Plan": ["Plan A", "Plan B"],
        "Fatigue Score": [plan_a_score, plan_b_score]
    })

    fig2, ax2 = plt.subplots(figsize=(8, 4))
    ax2.bar(compare_df["Plan"], compare_df["Fatigue Score"])
    ax2.set_title("Plan A vs Plan B Fatigue Comparison")
    ax2.set_ylabel("Fatigue Score")
    ax2.set_ylim(0, 100)
    st.pyplot(fig2)

    st.markdown("### Operational Decision Insight")
    st.info(compare_plans(plan_a_score, plan_b_score))

# -------------------------------
# TAB 4: CREW RISK TABLE
# -------------------------------
with tab4:
    st.subheader("Crew Risk Table")

    try:
        crew_df = pd.read_csv("crew_data.csv")

        crew_df["Fatigue Score"] = crew_df.apply(
            lambda row: calculate_fatigue_score(
                duty_hours=row["Duty Hours"],
                segments=row["Flight Segments"],
                timezone_changes=row["Time Zone Changes"],
                rest_hours=row["Rest Hours Before Duty"],
                circadian_disruption=row["Circadian Disruption Level"],
                delay_minutes=delay_minutes if irops_mode else 0,
                reassignment=reassignment if irops_mode else False,
                extra_segment=extra_segment if irops_mode else False,
                overnight_disruption=overnight_disruption if irops_mode else False,
                short_notice=short_notice if irops_mode else False
            ),
            axis=1
        )

        crew_df["Risk Level"] = crew_df["Fatigue Score"].apply(lambda x: get_risk_level(x)[0])
        crew_df["Status"] = crew_df["Fatigue Score"].apply(lambda x: get_risk_level(x)[1])
        crew_df["Suggested Action"] = crew_df["Fatigue Score"].apply(crew_suggested_action)

        display_df = crew_df[[
            "Crew ID",
            "Duty Hours",
            "Flight Segments",
            "Time Zone Changes",
            "Rest Hours Before Duty",
            "Circadian Disruption Level",
            "Fatigue Score",
            "Risk Level",
            "Status",
            "Suggested Action"
        ]].sort_values(by="Fatigue Score", ascending=False)

        st.dataframe(display_df, use_container_width=True)

        fig3, ax3 = plt.subplots(figsize=(10, 4))
        ax3.bar(display_df["Crew ID"], display_df["Fatigue Score"])
        ax3.set_title("Crew Fatigue Scores")
        ax3.set_ylabel("Fatigue Score")
        ax3.set_ylim(0, 100)
        st.pyplot(fig3)

    except Exception:
        st.warning("crew_data.csv not found or could not be read.")

# -------------------------------
# TAB 5: RECOMMENDATION ENGINE
# -------------------------------
with tab5:
    st.subheader("Recommendation Engine")

    st.markdown("### Suggested Operational Actions")
    for item in recommendations:
        st.write(f"- {item}")

    st.markdown("### Positioning Insight")
    st.info(
        "AeroVigil is solving the gap between legal compliance and operational safety decision-making."
    )

    st.markdown("### Networking / Industry Talking Point")
    st.success(
        "“From what I’ve learned from airline operations personnel, the real gap isn’t fatigue awareness—it’s actionable decision support during disruptions.”"
    )

st.divider()
st.caption(
    "Prototype for educational, research, and demonstration purposes only. "
    "AeroVigil is not an FAA-approved dispatch, scheduling, or operational control system."
)
