import math
from datetime import datetime

import pandas as pd
import streamlit as st


# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="AeroVigil V5 - IROPs Mode",
    page_icon="✈️",
    layout="wide"
)


# ---------------------------------------------------
# HELPERS
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
# HEADER
# ---------------------------------------------------
st.title("✈️ AeroVigil V5 - IROPs Decision Support")
st.caption("Predictive fatigue-aware operational support for airline disruptions.")

st.markdown(
    """
AeroVigil V5 focuses on the **operational impact of disruptions** — not fixing the disruption itself,
but helping teams make better crew and flight decisions during **IROPs, delays, and irregular operations**.
"""
)


# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------
st.sidebar.header("AeroVigil Control Panel")
show_demo_data = st.sidebar.toggle("Load sample IROPs cases", value=True)
show_methodology = st.sidebar.toggle("Show scoring methodology", value=False)
current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
st.sidebar.write(f"**System Time:** {current_time}")


# ---------------------------------------------------
# TABS
# ---------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "IROPs Mode",
    "Scenario Comparison",
    "Multi-Flight Console",
    "Executive Snapshot"
])


# ---------------------------------------------------
# TAB 1 - IROPS MODE
# ---------------------------------------------------
with tab1:
    st.subheader("IROPs Case Analyzer")

    col1, col2, col3 = st.columns(3)

    with col1:
        flight_id = st.text_input("Flight ID", value="DL104")
        delay_type = st.selectbox(
            "Delay Type",
            ["Mechanical", "Weather", "ATC", "Crew", "Security", "Other"]
        )
        delay_hours = st.slider("Delay Duration (hours)", 0.0, 8.0, 2.5, 0.5)
        maintenance_hold = st.checkbox("Maintenance hold active", value=(delay_type == "Mechanical"))

    with col2:
        duty_hours = st.slider("Current Duty Hours", 0.0, 16.0, 9.5, 0.5)
        segments = st.slider("Flight Segments Today", 1, 8, 4)
        timezone_changes = st.slider("Time Zone Changes", 0, 6, 1)

    with col3:
        rest_hours = st.slider("Rest Hours Before Duty", 6.0, 16.0, 10.0, 0.5)
        circadian_disruption = st.checkbox("Circadian Disruption", value=True)
        reserve_available = st.checkbox("Reserve Crew Available", value=True)

    case = build_case_row(
        flight_id=flight_id,
        delay_type=delay_type,
        delay_hours=delay_hours,
        duty_hours=duty_hours,
        segments=segments,
        timezone_changes=timezone_changes,
        rest_hours=rest_hours,
        circadian_disruption=circadian_disruption,
        reserve_available=reserve_available,
        maintenance_hold=maintenance_hold
    )

    st.divider()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Fatigue Score", case["Fatigue Score"])
    m2.metric("Risk Level", case["Risk"])
    m3.metric("Legal Status", case["Legal"])
    m4.metric("Priority", case["Priority"])

    alert_box = st.container(border=True)
    with alert_box:
        st.markdown(f"### Recommendation")
        st.write(case["Recommendation"])
        st.markdown(f"**Reason Notes:** {case['Reason Notes']}")

    st.markdown("### Case Detail")
    detail_df = pd.DataFrame([case]).drop(columns=["Recommendation", "Reason Notes"])
    st.dataframe(detail_df, use_container_width=True, hide_index=True)

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
# TAB 2 - SCENARIO COMPARISON
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
    st.success(f"Suggested lower-risk operational option: **{better}**")


# ---------------------------------------------------
# TAB 3 - MULTI-FLIGHT CONSOLE
# ---------------------------------------------------
with tab3:
    st.subheader("Multi-Flight Disruption Console")

    if show_demo_data:
        df_cases = make_sample_irrops_data()
    else:
        df_cases = pd.DataFrame(columns=[
            "Flight", "Delay Type", "Delay Hrs", "Duty Hrs", "Segments", "TZ Changes",
            "Rest Hrs", "Circadian", "Reserve", "Legal", "Fatigue Score", "Risk",
            "Priority", "Recommendation", "Reason Notes"
        ])

    st.write("This console helps prioritize disruption cases across multiple flights.")

    editor_df = st.data_editor(
        df_cases,
        use_container_width=True,
        num_rows="dynamic",
        hide_index=True
    )

    # If edited data no longer has calculated fields, attempt safe rebuild only if raw columns exist
    raw_columns = {"Flight", "Delay Type", "Delay Hrs", "Duty Hrs", "Segments", "TZ Changes", "Rest Hrs", "Circadian", "Reserve"}
    if raw_columns.issubset(set(editor_df.columns)):
        rebuilt_rows = []
        for _, row in editor_df.iterrows():
            rebuilt_rows.append(
                build_case_row(
                    flight_id=str(row["Flight"]),
                    delay_type=str(row["Delay Type"]),
                    delay_hours=float(row["Delay Hrs"]),
                    duty_hours=float(row["Duty Hrs"]),
                    segments=int(row["Segments"]),
                    timezone_changes=int(row["TZ Changes"]),
                    rest_hours=float(row["Rest Hrs"]),
                    circadian_disruption=str(row["Circadian"]).lower() in ["yes", "true", "1"],
                    reserve_available=str(row["Reserve"]).lower() in ["yes", "true", "1"],
                    maintenance_hold=str(row["Delay Type"]) == "Mechanical"
                )
            )
        results_df = pd.DataFrame(rebuilt_rows)
    else:
        results_df = df_cases.copy()

    st.divider()

    st.markdown("### Prioritized Queue")
    priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    if not results_df.empty and "Priority" in results_df.columns:
        results_df["Priority Rank"] = results_df["Priority"].map(priority_order)
        results_df = results_df.sort_values(
            by=["Priority Rank", "Fatigue Score", "Delay Hrs"],
            ascending=[True, False, False]
        ).drop(columns=["Priority Rank"])

    st.dataframe(results_df, use_container_width=True, hide_index=True)

    if not results_df.empty:
        st.markdown("### Alert Queue")
        critical_df = results_df[results_df["Priority"].isin(["CRITICAL", "HIGH"])]

        if critical_df.empty:
            st.success("No HIGH or CRITICAL cases in current queue.")
        else:
            for _, row in critical_df.iterrows():
                with st.container(border=True):
                    st.markdown(
                        f"**{row['Flight']}** | {row['Delay Type']} delay | "
                        f"Fatigue Score: **{row['Fatigue Score']}** | "
                        f"Legal: **{row['Legal']}** | Priority: **{row['Priority']}**"
                    )
                    st.write(row["Recommendation"])
                    st.caption(row["Reason Notes"])


# ---------------------------------------------------
# TAB 4 - EXECUTIVE SNAPSHOT
# ---------------------------------------------------
with tab4:
    st.subheader("Executive Snapshot")

    exec_df = make_sample_irrops_data() if show_demo_data else pd.DataFrame()

    if exec_df.empty:
        st.info("No data available. Turn on sample cases from the sidebar.")
    else:
        total_cases = len(exec_df)
        avg_score = round(exec_df["Fatigue Score"].mean(), 1)
        high_cases = int((exec_df["Priority"].isin(["HIGH", "CRITICAL"])).sum())
        illegal_cases = int((exec_df["Legal"] == "No").sum())

        e1, e2, e3, e4 = st.columns(4)
        e1.metric("Open Disruption Cases", total_cases)
        e2.metric("Average Fatigue Score", avg_score)
        e3.metric("High / Critical Cases", high_cases)
        e4.metric("Projected Illegal Cases", illegal_cases)

        st.divider()

        st.markdown("### Risk Distribution")
        risk_counts = exec_df["Risk"].value_counts().reset_index()
        risk_counts.columns = ["Risk", "Count"]
        st.bar_chart(risk_counts.set_index("Risk"))

        st.markdown("### Delay Type Distribution")
        delay_counts = exec_df["Delay Type"].value_counts().reset_index()
        delay_counts.columns = ["Delay Type", "Count"]
        st.bar_chart(delay_counts.set_index("Delay Type"))

        st.markdown("### Executive Interpretation")
        st.write(
            """
This snapshot is designed for operational leaders, OCC teams, crew scheduling, and safety stakeholders.
It shows where disruption pressure is accumulating and where fatigue-aware decision support may improve
recovery planning.
"""
        )

        st.dataframe(
            exec_df[["Flight", "Delay Type", "Delay Hrs", "Fatigue Score", "Risk", "Legal", "Priority", "Recommendation"]],
            use_container_width=True,
            hide_index=True
        )


# ---------------------------------------------------
# FOOTER
# ---------------------------------------------------
st.divider()
st.caption(
    "AeroVigil is a prototype decision-support tool for operational analysis and human-factors-informed disruption response. "
    "It does not replace regulatory, dispatch, maintenance, or crew scheduling systems."
)