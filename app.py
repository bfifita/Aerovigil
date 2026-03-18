import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="AeroVigil | Operations Risk Console",
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


def legal_status(duty_hours: float, rest_hours: float):
    """
    Simplified demo logic only.
    Not FAA-approved logic.
    """
    legal_duty_limit = 14
    minimum_rest = 10

    is_legal = (duty_hours <= legal_duty_limit) and (rest_hours >= minimum_rest)

    if is_legal:
        return True, "YES"
    return False, "NO"


def generate_recommendation(score: int, legal_ok: bool, delay_hours: float, reserve_available: bool) -> str:
    if not legal_ok:
        if reserve_available:
            return "Pairing exceeds simplified legality threshold. Assign reserve crew or re-route coverage."
        return "Pairing exceeds simplified legality threshold. Escalate to crew scheduling immediately."

    if score >= 80:
        if reserve_available:
            return "High operational fatigue exposure. Strongly consider reserve replacement before departure."
        return "High operational fatigue exposure. Escalate for scheduler and safety review."
    elif score >= 65:
        if delay_hours >= 2:
            return "Legal but elevated fatigue risk after disruption. Evaluate mitigation before release."
        return "Moderate-to-high fatigue exposure. Continue monitoring and review pairing stability."
    elif score >= 35:
        return "Moderate risk profile. Monitor for further disruption or extension."
    else:
        return "Risk appears manageable. Continue standard monitoring."


def risk_badge(level: str) -> str:
    if level == "HIGH":
        return "CRITICAL"
    elif level == "MODERATE":
        return "WATCH"
    return "NORMAL"


def build_trend_data(base_duty, base_segments, base_tz, base_rest, base_circadian):
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


def build_sample_alerts():
    data = [
        {
            "Flight": "DL2217",
            "Route": "ATL-MIA",
            "Crew_ID": "CR102",
            "Duty_Hours": 10.5,
            "Segments": 3,
            "TZ_Changes": 1,
            "Rest_Hours": 10.0,
            "Circadian": "Moderate",
            "Delay_Hours": 1.5,
            "Reserve_Available": "Yes"
        },
        {
            "Flight": "AA884",
            "Route": "LAX-JFK",
            "Crew_ID": "CR208",
            "Duty_Hours": 12.5,
            "Segments": 2,
            "TZ_Changes": 3,
            "Rest_Hours": 9.0,
            "Circadian": "High",
            "Delay_Hours": 2.5,
            "Reserve_Available": "No"
        },
        {
            "Flight": "UA1902",
            "Route": "ORD-CLT",
            "Crew_ID": "CR311",
            "Duty_Hours": 9.0,
            "Segments": 4,
            "TZ_Changes": 1,
            "Rest_Hours": 11.0,
            "Circadian": "Moderate",
            "Delay_Hours": 0.5,
            "Reserve_Available": "Yes"
        },
        {
            "Flight": "WN517",
            "Route": "DEN-PHX",
            "Crew_ID": "CR417",
            "Duty_Hours": 8.0,
            "Segments": 2,
            "TZ_Changes": 0,
            "Rest_Hours": 12.0,
            "Circadian": "Low",
            "Delay_Hours": 0.0,
            "Reserve_Available": "Yes"
        },
        {
            "Flight": "B6721",
            "Route": "BOS-FLL",
            "Crew_ID": "CR522",
            "Duty_Hours": 13.0,
            "Segments": 3,
            "TZ_Changes": 1,
            "Rest_Hours": 8.5,
            "Circadian": "High",
            "Delay_Hours": 3.0,
            "Reserve_Available": "No"
        }
    ]

    df = pd.DataFrame(data)

    scores = []
    categories = []
    legal_list = []
    severity = []
    recommendations = []

    for _, row in df.iterrows():
        score = calculate_fatigue_score(
            duty_hours=row["Duty_Hours"],
            segments=row["Segments"],
            timezone_changes=row["TZ_Changes"],
            rest_hours=row["Rest_Hours"],
            circadian_disruption=row["Circadian"]
        )
        legal_ok, legal_text = legal_status(row["Duty_Hours"], row["Rest_Hours"])
        category = fatigue_category(score)
        reserve_available = row["Reserve_Available"] == "Yes"

        scores.append(score)
        categories.append(category)
        legal_list.append(legal_text)
        severity.append(risk_badge(category))
        recommendations.append(
            generate_recommendation(score, legal_ok, row["Delay_Hours"], reserve_available)
        )

    df["Fatigue_Score"] = scores
    df["Risk"] = categories
    df["Legal"] = legal_list
    df["Severity"] = severity
    df["Recommendation"] = recommendations

    return df


# ---------------------------------------------------
# HEADER
# ---------------------------------------------------
st.title("AeroVigil")
st.subheader("Operations Risk Console")
st.caption("Disruption-aware crew risk decision support for OCC, Crew Scheduling, and Safety teams")

st.markdown("---")

# ---------------------------------------------------
# TOP FILTER / CONTROL BAR
# ---------------------------------------------------
top1, top2, top3, top4 = st.columns([1.2, 1.2, 1.2, 2])

with top1:
    airline = st.selectbox("Airline", ["Demo Airline", "Regional Carrier", "Cargo Operator"])
with top2:
    hub = st.selectbox("Hub / Base", ["ATL", "DFW", "ORD", "LAX", "JFK"])
with top3:
    view = st.selectbox("View", ["OCC View", "Crew Scheduling View", "Safety View", "Executive Summary"])
with top4:
    st.markdown("**Last Updated:** 08:42 Local Ops Time")

# ---------------------------------------------------
# DATA
# ---------------------------------------------------
alerts_df = build_sample_alerts()

# ---------------------------------------------------
# KPI ROW
# ---------------------------------------------------
active_flights = len(alerts_df)
high_risk_crews = len(alerts_df[alerts_df["Risk"] == "HIGH"])
legal_but_high = len(alerts_df[(alerts_df["Risk"] == "HIGH") & (alerts_df["Legal"] == "YES")])
reserves_available = len(alerts_df[alerts_df["Reserve_Available"] == "Yes"])
disruption_alerts = len(alerts_df[alerts_df["Delay_Hours"] >= 2])

k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.metric("Active Flights Monitored", active_flights)
with k2:
    st.metric("Crews at Elevated Risk", high_risk_crews)
with k3:
    st.metric("Legal but High Risk", legal_but_high)
with k4:
    st.metric("Disruption Alerts", disruption_alerts)
with k5:
    st.metric("Reserve Coverage Available", reserves_available)

st.markdown("---")

# ---------------------------------------------------
# MAIN LAYOUT
# ---------------------------------------------------
left_col, center_col, right_col = st.columns([1.5, 1.3, 1.2])

# ---------------------------------------------------
# LEFT: ALERT QUEUE
# ---------------------------------------------------
with left_col:
    st.markdown("### Alert Queue")

    queue_df = alerts_df[[
        "Flight", "Route", "Crew_ID", "Legal", "Fatigue_Score", "Risk", "Severity"
    ]].copy()

    st.dataframe(queue_df, use_container_width=True, hide_index=True)

    selected_flight = st.selectbox("Select Flight Case", alerts_df["Flight"].tolist())
    selected_row = alerts_df[alerts_df["Flight"] == selected_flight].iloc[0]

# ---------------------------------------------------
# CENTER: CASE DETAIL
# ---------------------------------------------------
with center_col:
    st.markdown("### Case Detail")

    st.markdown(f"**Flight:** {selected_row['Flight']}")
    st.markdown(f"**Route:** {selected_row['Route']}")
    st.markdown(f"**Crew ID:** {selected_row['Crew_ID']}")
    st.markdown(f"**Severity:** {selected_row['Severity']}")

    st.info(
        f"""
**Operational Snapshot**
- Legal to Operate: {selected_row['Legal']}
- Fatigue Score: {selected_row['Fatigue_Score']}
- Risk Category: {selected_row['Risk']}
- Duty Hours: {selected_row['Duty_Hours']}
- Segments: {selected_row['Segments']}
- Time Zone Changes: {selected_row['TZ_Changes']}
- Rest Hours: {selected_row['Rest_Hours']}
- Circadian Disruption: {selected_row['Circadian']}
- Delay Exposure: {selected_row['Delay_Hours']} hrs
- Reserve Available: {selected_row['Reserve_Available']}
"""
    )

    st.markdown("**System Recommendation**")
    if selected_row["Risk"] == "HIGH" or selected_row["Legal"] == "NO":
        st.error(selected_row["Recommendation"])
    elif selected_row["Risk"] == "MODERATE":
        st.warning(selected_row["Recommendation"])
    else:
        st.success(selected_row["Recommendation"])

    st.markdown("**Why this case is flagged**")
    reasons = []
    if selected_row["Duty_Hours"] >= 12:
        reasons.append("- Extended duty window increases fatigue exposure.")
    if selected_row["Rest_Hours"] < 10:
        reasons.append("- Reduced rest margin creates recovery concern.")
    if selected_row["TZ_Changes"] >= 2:
        reasons.append("- Multiple time-zone changes increase circadian strain.")
    if selected_row["Segments"] >= 4:
        reasons.append("- High segment count may increase cumulative workload.")
    if selected_row["Delay_Hours"] >= 2:
        reasons.append("- Disruption delay increases pairing instability.")
    if selected_row["Circadian"] == "High":
        reasons.append("- High circadian disruption raises operational risk.")

    if reasons:
        for reason in reasons:
            st.write(reason)
    else:
        st.write("- No major risk drivers beyond baseline inputs.")

# ---------------------------------------------------
# RIGHT: ACTION ENGINE
# ---------------------------------------------------
with right_col:
    st.markdown("### Action Engine")

    action = st.radio(
        "Recommended Workflow",
        [
            "Monitor",
            "Use Reserve Crew",
            "Reassign Pairing",
            "Delay Departure",
            "Escalate to Safety",
            "Mark Resolved"
        ]
    )

    st.markdown("**Action Guidance**")
    if action == "Monitor":
        st.write("Continue tracking current pairing for additional delay, reassignment, or rest deterioration.")
    elif action == "Use Reserve Crew":
        st.write("Deploy reserve coverage where available to reduce fatigue exposure before departure.")
    elif action == "Reassign Pairing":
        st.write("Review legality, downstream connections, and reserve options before finalizing a crew swap.")
    elif action == "Delay Departure":
        st.write("Use only when staffing alternatives are limited and downstream disruption is acceptable.")
    elif action == "Escalate to Safety":
        st.write("Send case for joint operational and safety review when risk remains elevated despite legality.")
    elif action == "Mark Resolved":
        st.write("Close alert only after mitigation action has been completed and risk is reduced.")

    st.markdown("**Case Notes**")
    st.text_area(
        "Scheduler / Safety Notes",
        value="Crew remains legal under simplified thresholds; review mitigation options before release.",
        height=180
    )

st.markdown("---")

# ---------------------------------------------------
# SCENARIO SIMULATOR
# ---------------------------------------------------
st.markdown("### Scenario Simulator")

sim1, sim2, sim3, sim4 = st.columns(4)

with sim1:
    sim_delay = st.slider("Add Delay (Hours)", 0.0, 6.0, float(selected_row["Delay_Hours"]), 0.5)
with sim2:
    sim_extra_segments = st.slider("Add Segments", 0, 3, 0)
with sim3:
    sim_extra_tz = st.slider("Add Time Zone Changes", 0, 3, 0)
with sim4:
    sim_rest_reduction = st.slider("Reduce Rest (Hours)", 0.0, 4.0, 0.0, 0.5)

base_score = int(selected_row["Fatigue_Score"])
base_legal_text = selected_row["Legal"]
base_risk = selected_row["Risk"]

scenario_duty = float(selected_row["Duty_Hours"]) + sim_delay
scenario_segments = int(selected_row["Segments"]) + sim_extra_segments
scenario_tz = int(selected_row["TZ_Changes"]) + sim_extra_tz
scenario_rest = max(0.0, float(selected_row["Rest_Hours"]) - sim_rest_reduction)

scenario_score = calculate_fatigue_score(
    duty_hours=scenario_duty,
    segments=scenario_segments,
    timezone_changes=scenario_tz,
    rest_hours=scenario_rest,
    circadian_disruption=selected_row["Circadian"]
)

scenario_risk = fatigue_category(scenario_score)
scenario_legal_ok, scenario_legal_text = legal_status(scenario_duty, scenario_rest)
scenario_recommendation = generate_recommendation(
    scenario_score,
    scenario_legal_ok,
    sim_delay,
    selected_row["Reserve_Available"] == "Yes"
)

s1, s2 = st.columns(2)

with s1:
    st.markdown("#### Current Plan")
    st.info(
        f"""
- Legal to Operate: {base_legal_text}
- Fatigue Score: {base_score}
- Risk Category: {base_risk}
- Duty Hours: {selected_row['Duty_Hours']}
- Rest Hours: {selected_row['Rest_Hours']}
- Segments: {selected_row['Segments']}
- Time Zone Changes: {selected_row['TZ_Changes']}
"""
    )

with s2:
    st.markdown("#### Simulated Plan")
    st.info(
        f"""
- Legal to Operate: {scenario_legal_text}
- Fatigue Score: {scenario_score}
- Risk Category: {scenario_risk}
- Duty Hours: {scenario_duty}
- Rest Hours: {scenario_rest}
- Segments: {scenario_segments}
- Time Zone Changes: {scenario_tz}
"""
    )

    if scenario_legal_text == "NO" or scenario_risk == "HIGH":
        st.error(f"Recommendation: {scenario_recommendation}")
    elif scenario_risk == "MODERATE":
        st.warning(f"Recommendation: {scenario_recommendation}")
    else:
        st.success(f"Recommendation: {scenario_recommendation}")

# ---------------------------------------------------
# BOTTOM PANELS
# ---------------------------------------------------
tab1, tab2, tab3 = st.tabs(["Trend View", "Scenario Comparison", "Executive Snapshot"])

with tab1:
    trend_df = build_trend_data(
        base_duty=float(selected_row["Duty_Hours"]),
        base_segments=int(selected_row["Segments"]),
        base_tz=int(selected_row["TZ_Changes"]),
        base_rest=float(selected_row["Rest_Hours"]),
        base_circadian=selected_row["Circadian"]
    )

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(trend_df["Day"], trend_df["Fatigue Score"], marker="o")
    ax.set_title("4-Day Crew Fatigue Trend")
    ax.set_ylabel("Fatigue Score")
    ax.set_xlabel("Duty Period")
    ax.set_ylim(0, 100)
    ax.grid(True)

    st.pyplot(fig)

with tab2:
    comparison_df = pd.DataFrame({
        "Metric": [
            "Legal to Operate",
            "Fatigue Score",
            "Risk Category",
            "Duty Hours",
            "Rest Hours",
            "Segments",
            "Time Zone Changes"
        ],
        "Current Plan": [
            base_legal_text,
            base_score,
            base_risk,
            selected_row["Duty_Hours"],
            selected_row["Rest_Hours"],
            selected_row["Segments"],
            selected_row["TZ_Changes"]
        ],
        "Simulated Plan": [
            scenario_legal_text,
            scenario_score,
            scenario_risk,
            scenario_duty,
            scenario_rest,
            scenario_segments,
            scenario_tz
        ]
    })

    st.dataframe(comparison_df, use_container_width=True, hide_index=True)

with tab3:
    st.markdown("#### Executive Snapshot")
    st.write(f"- **Airline:** {airline}")
    st.write(f"- **Hub/Base:** {hub}")
    st.write(f"- **Operational View:** {view}")
    st.write(f"- **Highest-Risk Case:** {alerts_df.sort_values('Fatigue_Score', ascending=False).iloc[0]['Flight']}")
    st.write(f"- **Total Critical/High-Risk Cases:** {high_risk_crews}")
    st.write(f"- **Legal but High-Risk Cases:** {legal_but_high}")
    st.write("- **Positioning:** AeroVigil supports earlier identification of legal-but-elevated-risk pairings during disruption events.")

# ---------------------------------------------------
# FOOTER
# ---------------------------------------------------
st.markdown("---")
st.caption(
    "Disclaimer: AeroVigil is a prototype decision-support tool for demonstration purposes only. "
    "It does not replace FAA regulations, company policy, dispatch authority, crew scheduling processes, "
    "or formal fatigue risk management systems."
)
