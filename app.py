import math
from datetime import datetime

import pandas as pd
import streamlit as st


# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="AeroVigil Operations Risk Console",
    page_icon="✈️",
    layout="wide"
)


# ---------------------------------------------------
# HELPERS (UNCHANGED LOGIC)
# ---------------------------------------------------
def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(value, high))


def calculate_fatigue_score( 
    duty_hours: float,
    segments: int,
    timezone_changes: int,
    rest_hours: float,
    circadian_disruption: bool,
    delay_hours: float,
    delay_type: str
) -> tuple[float, str]:
    """
    Returns fatigue score (0-100) and risk level.
    """
    score = 0.0

    # Base fatigue components
    score += duty_hours * 3.5
    score += segments * 5.0
    score += timezone_changes * 4.0
    score += max(0, 10 - rest_hours) * 4.5

    if circadian_disruption:
        score += 15

    # Delay effect
    score += delay_hours * 5.0

    # Delay type effect
    delay_type_weights = {
        "Mechanical": 8,
        "Weather": 6,
        "ATC": 5,
        "Crew": 7,
        "Security": 4,
        "Other": 3
    }
    score += delay_type_weights.get(delay_type, 3)

    score = clamp(score, 0, 100)

    if score < 35:
        risk = "LOW"
    elif score < 70:
        risk = "MODERATE"
    else:
        risk = "HIGH"

    return round(score, 1), risk


def calculate_legality(
    duty_hours: float,
    rest_hours: float,
    segments: int,
    delay_hours: float
) -> tuple[bool, list[str]]:
    """
    Simplified legality check for operational demonstration.
    """
    reasons = []
    projected_duty = duty_hours + delay_hours

    if projected_duty > 14:
        reasons.append("Projected duty exceeds 14 hours")

    if rest_hours < 10:
        reasons.append("Rest below 10 hours")

    if segments > 6:
        reasons.append("High segment count may increase operational strain")

    legal = len([r for r in reasons if "exceeds 14 hours" in r or "Rest below 10 hours" in r]) == 0
    return legal, reasons


def generate_recommendation(
    fatigue_score: float,
    risk_level: str,
    legal_ok: bool,
    delay_type: str,
    delay_hours: float,
    reserve_available: bool,
    maintenance_hold: bool
) -> str:
    """
    Recommendation engine.
    """
    if maintenance_hold and delay_type == "Mechanical":
        return "HOLD AIRCRAFT / COORDINATE WITH MAINTENANCE before crew reassignment."

    if not legal_ok:
        if reserve_available:
            return "SWAP CREW - current crew projected illegal."
        return "DELAY OR CANCEL - current crew projected illegal and no reserve available."

    if risk_level == "HIGH":
        if reserve_available:
            return "CONSIDER CREW SWAP - crew legal but fatigue risk is HIGH."
        return "DELAY WITH MITIGATION - crew legal but fatigue risk HIGH; no reserve available."

    if risk_level == "MODERATE":
        if delay_hours >= 3:
            return "MONITOR CLOSELY - moderate fatigue risk with extended disruption."
        return "PROCEED WITH CAUTION - moderate fatigue risk."

    return "PROCEED - crew legal and fatigue risk acceptable."


def disruption_priority(
    fatigue_score: float,
    legal_ok: bool,
    delay_hours: float,
    reserve_available: bool
) -> str:
    if not legal_ok and not reserve_available:
        return "CRITICAL"
    if not legal_ok:
        return "HIGH"
    if fatigue_score >= 70:
        return "HIGH"
    if fatigue_score >= 35 or delay_hours >= 2:
        return "MEDIUM"
    return "LOW"


def build_case_row(
    flight_id: str,
    delay_type: str,
    delay_hours: float,
    duty_hours: float,
    segments: int,
    timezone_changes: int,
    rest_hours: float,
    circadian_disruption: bool,
    reserve_available: bool,
    maintenance_hold: bool
) -> dict:
    fatigue_score, risk_level = calculate_fatigue_score(
        duty_hours=duty_hours,
        segments=segments,
        timezone_changes=timezone_changes,
        rest_hours=rest_hours,
        circadian_disruption=circadian_disruption,
        delay_hours=delay_hours,
        delay_type=delay_type
    )

    legal_ok, reasons = calculate_legality(
        duty_hours=duty_hours,
        rest_hours=rest_hours,
        segments=segments,
        delay_hours=delay_hours
    )

    recommendation = generate_recommendation(
        fatigue_score=fatigue_score,
        risk_level=risk_level,
        legal_ok=legal_ok,
        delay_type=delay_type,
        delay_hours=delay_hours,
        reserve_available=reserve_available,
        maintenance_hold=maintenance_hold
    )

    priority = disruption_priority(
        fatigue_score=fatigue_score,
        legal_ok=legal_ok,
        delay_hours=delay_hours,
        reserve_available=reserve_available
    )

    return {
        "Flight": flight_id,
        "Delay Type": delay_type,
        "Delay Hrs": delay_hours,
        "Duty Hrs": duty_hours,
        "Segments": segments,
        "TZ Changes": timezone_changes,
        "Rest Hrs": rest_hours,
        "Circadian": "Yes" if circadian_disruption else "No",
        "Reserve": "Yes" if reserve_available else "No",
        "Legal": "Yes" if legal_ok else "No",
        "Fatigue Score": fatigue_score,
        "Risk": risk_level,
        "Priority": priority,
        "Recommendation": recommendation,
        "Reason Notes": "; ".join(reasons) if reasons else "No major legal flags"
    }


def make_sample_irrops_data() -> pd.DataFrame:
    rows = [
        build_case_row("DL104", "Mechanical", 3.5, 10.0, 4, 1, 11.0, True, True, True),
        build_case_row("AA221", "Weather", 2.0, 9.0, 5, 0, 10.5, False, False, False),
        build_case_row("UA515", "ATC", 1.5, 11.0, 3, 2, 9.5, True, True, False),
        build_case_row("WN880", "Crew", 4.0, 12.0, 6, 0, 8.5, False, False, False),
        build_case_row("JB390", "Security", 1.0, 7.5, 2, 0, 12.0, False, True, False),
    ]
    return pd.DataFrame(rows)


# ---------------------------------------------------
# STYLES (simple CSS for dashboard feel)
# ---------------------------------------------------
st.markdown(
    """
    <style>
    /* Top header styling */
    .header-title { font-size: 22px; font-weight:600; }
    .kpi { background-color: #0f172a; color: white; padding: 12px; border-radius:8px; }
    .risk-pill { padding:6px 10px; border-radius:999px; color:white; font-weight:600; }
    .risk-low { background:#16a34a; }
    .risk-moderate { background:#f59e0b; color:#111827; }
    .risk-high { background:#ef4444; }
    .left-panel { background-color:#0b1220; color:white; padding:10px; border-radius:8px; }
    .small-muted { color: #94a3b8; font-size:12px; }
    .card { padding:12px; border-radius:8px; background: #ffffff; }
    </style>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------------------
# SIDEBAR / GLOBAL CONTROLS
# ---------------------------------------------------
st.sidebar.header("AeroVigil Control Panel")
show_demo_data = st.sidebar.toggle("Load sample IROPs cases", value=True)
show_methodology = st.sidebar.toggle("Show scoring methodology", value=False)
current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
st.sidebar.write(f"**System Time:** {current_time}")
st.sidebar.markdown("---")
st.sidebar.caption("Theme: Enterprise OCC | Layout: 3-Column Operational Console")


# ---------------------------------------------------
# MAIN LAYOUT - Tabs preserved; Tab1 becomes OCC Dashboard
# ---------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "Operations Risk Console",
    "Scenario Comparison",
    "Multi-Flight Console",
    "Executive Snapshot"
])


# ---------------------------------------------------
# TAB 1 - OPERATIONS RISK CONSOLE (new dashboard layout)
# ---------------------------------------------------
with tab1:
    # Top header with KPIs
    header_col1, header_col2 = st.columns([3, 1])
    with header_col1:
        st.markdown('<div class="header-title">✈️ AeroVigil — Operations Risk Console</div>', unsafe_allow_html=True)
        st.caption("Real-time fatigue-aware decision support for OCC teams during IROPs")
    with header_col2:
        st.markdown(f"**{current_time}**")

    # Determine dataset for alerts / queue
    if show_demo_data:
        base_df = make_sample_irrops_data()
    else:
        base_df = pd.DataFrame(columns=[
            "Flight", "Delay Type", "Delay Hrs", "Duty Hrs", "Segments", "TZ Changes",
            "Rest Hrs", "Circadian", "Reserve", "Legal", "Fatigue Score", "Risk",
            "Priority", "Recommendation", "Reason Notes"
        ])

    # KPIs row
    k1, k2, k3, k4 = st.columns(4)
    active_alerts = len(base_df)
    high_risk_cases = int((base_df["Risk"] == "HIGH").sum()) if not base_df.empty else 0
    avg_fatigue = round(base_df["Fatigue Score"].mean(), 1) if not base_df.empty else 0.0
    # Simple network disruption level: proportion of HIGH/CRITICAL
    nd_level = 0
    if not base_df.empty:
        nd_level = round(((base_df["Priority"].isin(["CRITICAL", "HIGH"])).sum() / max(1, len(base_df))) * 100, 0)

    k1.metric("Active Alerts", active_alerts)
    k2.metric("High Risk Cases", high_risk_cases)
    k3.metric("Avg Fatigue Score", avg_fatigue)
    k4.metric("Network Disruption Level (%)", f"{nd_level}%")

    st.markdown("---")

    # Main three-column dashboard: Left=Alert Queue, Center=Case Detail, Right=Action Engine
    left_col, center_col, right_col = st.columns([1.4, 2.4, 1.2], gap="large")

    # LEFT PANEL: Alert Queue (selectable)
    with left_col:
        st.markdown("### Alert Queue")
        st.caption("Click a flight to open the Case Detail")
        if base_df.empty:
            st.info("No active alerts. Toggle sample data to load demo cases.")
            selected_flight = None
        else:
            # Build a compact list with colored risk pills and status
            # Create a selectable list
            list_items = []
            for _, row in base_df.iterrows():
                flight = row["Flight"]
                risk = row["Risk"]
                duty = row["Duty Hrs"]
                legal = row["Legal"]
                priority = row["Priority"]
                list_items.append({
                    "label": flight,
                    "risk": risk,
                    "duty": duty,
                    "legal": legal,
                    "priority": priority
                })

            # Use selectbox for simplicity and keyboard accessibility
            options = [f"{it['label']} | {it['risk']} | Duty:{it['duty']}h | {it['legal']}" for it in list_items]
            selected_option = st.selectbox("Select Flight", options, index=0)
            # parse selected
            selected_flight = selected_option.split("|")[0].strip()

            # Compact visual list below
            st.markdown("#### Queue Snapshot")
            for it in list_items:
                # color class
                cls = "risk-low"
                if it["risk"] == "MODERATE":
                    cls = "risk-moderate"
                elif it["risk"] == "HIGH":
                    cls = "risk-high"
                st.markdown(
                    f"<div style='display:flex; justify-content:space-between; align-items:center; padding:6px 0;'>"
                    f"<div><b>{it['label']}</b><div class='small-muted'>Priority: {it['priority']}</div></div>"
                    f"<div class='risk-pill {cls}'>{it['risk']}</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )

    # CENTER PANEL: Case Detail View
    with center_col:
        st.markdown("### Case Detail")
        if selected_flight is None:
            st.info("Select a flight from the Alert Queue to view details.")
        else:
            # Find case in base_df
            case_row = base_df[base_df["Flight"] == selected_flight]
            if case_row.empty:
                st.error("Selected flight not found in dataset.")
            else:
                case = case_row.iloc[0].to_dict()

                # Top summary cards
                sc1, sc2, sc3, sc4 = st.columns([1.2, 1.0, 1.0, 1.0])
                sc1.metric("Flight", case["Flight"])
                sc2.metric("Fatigue Score", case["Fatigue Score"])
                sc3.metric("Risk", case["Risk"])
                sc4.metric("Legal", case["Legal"])

                st.markdown("#### Crew Duty & Sleep")
                cols = st.columns(3)
                cols[0].metric("Duty Hours", case["Duty Hrs"])
                cols[1].metric("Rest Hours", case["Rest Hrs"])
                cols[2].metric("Segments", case["Segments"])

                st.markdown("#### Circadian & Time Zones")
                tz_col, circ_col = st.columns([2, 1])
                tz_col.metric("Time Zones Crossed", case["TZ Changes"])
                circ_col.metric("Circadian Disruption", case["Circadian"])

                st.markdown("#### Fatigue Gauge")
                # Visual progress bar for fatigue score
                fatigue_pct = min(100, max(0, float(case["Fatigue Score"])))
                bar_color = "#16a34a"
                if case["Risk"] == "MODERATE":
                    bar_color = "#f59e0b"
                elif case["Risk"] == "HIGH":
                    bar_color = "#ef4444"
                st.progress(int(fatigue_pct))
                st.caption(f"Fatigue Score: {fatigue_pct} / 100")

                st.markdown("#### Reasoning & Legal Notes")
                st.write(case["Reason Notes"])

                st.markdown("#### Full Case Data")
                detail_df = pd.DataFrame([case]).T.rename(columns={0: "Value"})
                st.table(detail_df)

    # RIGHT PANEL: Action / Recommendation Engine
    with right_col:
        st.markdown("### Action Engine")
        st.caption("Recommended operational actions with rationale")
        if selected_flight is None:
            st.info("Select an alert to surface recommendations.")
        else:
            case_row = base_df[base_df["Flight"] == selected_flight]
            if case_row.empty:
                st.error("Selected flight case missing.")
            else:
                case = case_row.iloc[0].to_dict()

                # Show available quick actions (without changing logic)
                st.markdown("#### Recommended Action")
                st.markdown(f"**{case['Recommendation']}**")

                st.markdown("#### Action Options")
                # Keep these as non-destructive buttons that simulate OCC actions
                if st.button("Acknowledge Case"):
                    st.success(f"{case['Flight']} acknowledged.")
                if st.button("Flag for Crew Swap"):
                    st.info(f"{case['Flight']} flagged for crew swap review.")
                if st.button("Assign Reserve"):
                    st.info(f"Reserve requested for {case['Flight']}.")
                if st.button("Escalate to CCO"):
                    st.warning(f"{case['Flight']} escalated to CCO.")

                st.markdown("---")
                st.markdown("#### Rationale")
                st.write(case["Reason Notes"])

    st.markdown("---")

    # Optional methodology info (unchanged content)
    if show_methodology:
        st.info(
            """
**Scoring logic summary**
- Higher duty hours increase fatigue risk
- More segments increase workload burden
- Time zone changes increase circadian strain
- Lower rest increases fatigue risk
- Circadian disruption adds penalty
- Longer disruptions increase fatigue pressure
- Mechanical / crew-related disruptions add operational stress weighting
"""
        )


# ---------------------------------------------------
# TAB 2 - SCENARIO COMPARISON (preserve functionality, UI improved slightly)
# ---------------------------------------------------
with tab2:
    st.subheader("Scenario Comparison Engine")
    st.write("Compare two recovery options side by side.")

    left, right = st.columns(2)

    with left:
        st.markdown("#### Scenario A")
        a_delay_type = st.selectbox("A - Delay Type", ["Mechanical", "Weather", "ATC", "Crew", "Security", "Other"], key="a_dt")
        a_delay_hours = st.slider("A - Delay Hours", 0.0, 8.0, 2.0, 0.5, key="a_dh")
        a_duty_hours = st.slider("A - Duty Hours", 0.0, 16.0, 10.0, 0.5, key="a_du")
        a_segments = st.slider("A - Segments", 1, 8, 4, key="a_seg")
        a_tz = st.slider("A - Time Zone Changes", 0, 6, 1, key="a_tz")
        a_rest = st.slider("A - Rest Hours", 6.0, 16.0, 10.5, 0.5, key="a_re")
        a_circadian = st.checkbox("A - Circadian Disruption", value=True, key="a_cd")
        a_reserve = st.checkbox("A - Reserve Available", value=True, key="a_ra")
        a_maint = st.checkbox("A - Maintenance Hold", value=False, key="a_mh")

    with right:
        st.markdown("#### Scenario B")
        b_delay_type = st.selectbox("B - Delay Type", ["Mechanical", "Weather", "ATC", "Crew", "Security", "Other"], key="b_dt")
        b_delay_hours = st.slider("B - Delay Hours", 0.0, 8.0, 4.0, 0.5, key="b_dh")
        b_duty_hours = st.slider("B - Duty Hours", 0.0, 16.0, 12.0, 0.5, key="b_du")
        b_segments = st.slider("B - Segments", 1, 8, 5, key="b_seg")
        b_tz = st.slider("B - Time Zone Changes", 0, 6, 2, key="b_tz")
        b_rest = st.slider("B - Rest Hours", 6.0, 16.0, 8.5, 0.5, key="b_re")
        b_circadian = st.checkbox("B - Circadian Disruption", value=True, key="b_cd")
        b_reserve = st.checkbox("B - Reserve Available", value=False, key="b_ra")
        b_maint = st.checkbox("B - Maintenance Hold", value=True, key="b_mh")

    scenario_a = build_case_row(
        flight_id="Scenario A",
        delay_type=a_delay_type,
        delay_hours=a_delay_hours,
        duty_hours=a_duty_hours,
        segments=a_segments,
        timezone_changes=a_tz,
        rest_hours=a_rest,
        circadian_disruption=a_circadian,
        reserve_available=a_reserve,
        maintenance_hold=a_maint
    )

    scenario_b = build_case_row(
        flight_id="Scenario B",
        delay_type=b_delay_type,
        delay_hours=b_delay_hours,
        duty_hours=b_duty_hours,
        segments=b_segments,
        timezone_changes=b_tz,
        rest_hours=b_rest,
        circadian_disruption=b_circadian,
        reserve_available=b_reserve,
        maintenance_hold=b_maint
    )

    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### Scenario A Result")
        st.metric("Fatigue Score", scenario_a["Fatigue Score"])
        st.metric("Risk", scenario_a["Risk"])
        st.metric("Legal", scenario_a["Legal"])
        st.write(f"**Recommendation:** {scenario_a['Recommendation']}")

    with c2:
        st.markdown("### Scenario B Result")
        st.metric("Fatigue Score", scenario_b["Fatigue Score"])
        st.metric("Risk", scenario_b["Risk"])
        st.metric("Legal", scenario_b["Legal"])
        st.write(f"**Recommendation:** {scenario_b['Recommendation']}")

    compare_df = pd.DataFrame([
        scenario_a,
        scenario_b
    ])[["Flight", "Delay Type", "Delay Hrs", "Duty Hrs", "Rest Hrs", "Fatigue Score", "Risk", "Legal", "Priority", "Recommendation"]]

    st.dataframe(compare_df, use_container_width=True, hide_index=True)

    # Suggested better option
    def scenario_rank(case_dict: dict) -> float:
        penalty = 0
        if case_dict["Legal"] == "No":
            penalty += 100
        if case_dict["Priority"] == "CRITICAL":
            penalty += 50
        elif case_dict["Priority"] == "HIGH":
            penalty += 25
        return case_dict["Fatigue Score"] + penalty

    a_rank = scenario_rank(scenario_a)
    b_rank = scenario_rank(scenario_b)

    better = "Scenario A" if a_rank < b_rank else "Scenario B"
