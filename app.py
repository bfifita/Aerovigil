import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fatigue_calculator import calculate_fatigue_score

st.set_page_config(page_title="AeroVigil", layout="wide")

st.title("AeroVigil")
st.subheader("Predictive Fatigue Risk Analytics for Aviation Safety")
st.write(
    "A startup prototype for estimating crew fatigue risk using duty time, segments, rest, "
    "timezone changes, and circadian disruption."
)

st.divider()


# -----------------------------
# Helper functions
# -----------------------------
def classify_risk(score):
    if score < 35:
        return "LOW", "Crew member appears fit for duty based on current inputs.", "green"
    elif score < 65:
        return "MODERATE", "Fatigue risk is elevated. Consider monitoring or mitigation strategies.", "orange"
    else:
        return "HIGH", "High fatigue risk detected. Schedule review or fatigue mitigation recommended.", "red"


def build_recommendations(duty_hours, segments, timezone_changes, rest_hours, circadian_disruption):
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

    return recommendations


def build_timeline_data(duty_hours, segments, timezone_changes, rest_hours, circadian_disruption):
    timeline = [
        {
            "Day": "Day 1",
            "Duty Hours": duty_hours,
            "Segments": segments,
            "Time Zones": timezone_changes,
            "Rest Hours": rest_hours,
            "Circadian Disruption": circadian_disruption,
        },
        {
            "Day": "Day 2",
            "Duty Hours": min(duty_hours + 1, 16),
            "Segments": segments,
            "Time Zones": timezone_changes,
            "Rest Hours": max(rest_hours - 1, 0),
            "Circadian Disruption": min(circadian_disruption + 1, 10),
        },
        {
            "Day": "Day 3",
            "Duty Hours": min(duty_hours + 2, 16),
            "Segments": min(segments + 1, 8),
            "Time Zones": min(timezone_changes + 1, 6),
            "Rest Hours": max(rest_hours - 2, 0),
            "Circadian Disruption": min(circadian_disruption + 2, 10),
        },
        {
            "Day": "Day 4",
            "Duty Hours": max(duty_hours - 1, 0),
            "Segments": max(segments - 1, 1),
            "Time Zones": timezone_changes,
            "Rest Hours": min(rest_hours + 2, 16),
            "Circadian Disruption": max(circadian_disruption - 1, 0),
        },
    ]

    for day in timeline:
        score = calculate_fatigue_score(
            day["Duty Hours"],
            day["Segments"],
            day["Time Zones"],
            day["Rest Hours"],
            day["Circadian Disruption"],
        )
        risk_level, _, _ = classify_risk(score)
        day["Fatigue Score"] = score
        day["Risk Level"] = risk_level

    return pd.DataFrame(timeline)


def score_row(row):
    return calculate_fatigue_score(
        row["Duty Hours"],
        row["Flight Segments"],
        row["Time Zone Changes"],
        row["Rest Hours Before Duty"],
        row["Circadian Disruption Level"],
    )


def add_risk_fields(df):
    df = df.copy()
    df["Fatigue Score"] = df.apply(score_row, axis=1)
    df["Risk Level"] = df["Fatigue Score"].apply(lambda x: classify_risk(x)[0])

    def recommended_action(score):
        if score >= 65:
            return "Immediate review"
        elif score >= 35:
            return "Monitor / mitigate"
        return "No immediate action"

    df["Recommended Action"] = df["Fatigue Score"].apply(recommended_action)
    return df


def make_heatmap_dataframe(df):
    heatmap_df = df.copy()
    if "Crew ID" not in heatmap_df.columns:
        heatmap_df["Crew ID"] = [f"Crew {i+1}" for i in range(len(heatmap_df))]

    heatmap_df = heatmap_df[
        [
            "Crew ID",
            "Duty Hours",
            "Flight Segments",
            "Time Zone Changes",
            "Rest Hours Before Duty",
            "Circadian Disruption Level",
            "Fatigue Score",
        ]
    ].set_index("Crew ID")

    return heatmap_df


def plot_heatmap(df):
    fig, ax = plt.subplots(figsize=(10, max(4, len(df) * 0.5)))
    cax = ax.imshow(df.values, aspect="auto")
    ax.set_xticks(range(len(df.columns)))
    ax.set_xticklabels(df.columns, rotation=45, ha="right")
    ax.set_yticks(range(len(df.index)))
    ax.set_yticklabels(df.index)
    ax.set_title("Crew Fatigue Heatmap")
    plt.colorbar(cax, ax=ax)
    st.pyplot(fig)


def run_mitigation_simulation(df):
    simulated = df.copy()

    simulated["Rest Hours Before Duty"] = simulated["Rest Hours Before Duty"].apply(lambda x: min(x + 2, 16))
    simulated["Flight Segments"] = simulated["Flight Segments"].apply(lambda x: max(x - 1, 1))
    simulated["Duty Hours"] = simulated["Duty Hours"].apply(lambda x: max(x - 1, 0))

    simulated = add_risk_fields(simulated)

    return simulated


# -----------------------------
# Sidebar single-crew demo inputs
# -----------------------------
st.sidebar.header("Single Crew Demo Inputs")
duty_hours = st.sidebar.slider("Duty Hours", 0, 16, 8)
segments = st.sidebar.slider("Flight Segments", 1, 8, 2)
timezone_changes = st.sidebar.slider("Time Zone Changes", 0, 6, 0)
rest_hours = st.sidebar.slider("Rest Hours Before Duty", 0, 16, 10)
circadian_disruption = st.sidebar.slider("Circadian Disruption Level", 0, 10, 3)

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


# -----------------------------
# Single crew fatigue analysis
# -----------------------------
if st.button("Calculate Fatigue Risk", use_container_width=True):
    score = calculate_fatigue_score(
        duty_hours,
        segments,
        timezone_changes,
        rest_hours,
        circadian_disruption
    )

    risk_level, status_message, gauge_color = classify_risk(score)

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

    recommendations = build_recommendations(
        duty_hours, segments, timezone_changes, rest_hours, circadian_disruption
    )

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

    st.divider()
    st.subheader("Fatigue Trend Scenario Chart")

    scenario_data = [
        {
            "Scenario": "Current",
            "Score": calculate_fatigue_score(
                duty_hours, segments, timezone_changes, rest_hours, circadian_disruption
            ),
        },
        {
            "Scenario": "+2 Duty Hours",
            "Score": calculate_fatigue_score(
                min(duty_hours + 2, 16), segments, timezone_changes, rest_hours, circadian_disruption
            ),
        },
        {
            "Scenario": "+1 Segment",
            "Score": calculate_fatigue_score(
                duty_hours, min(segments + 1, 8), timezone_changes, rest_hours, circadian_disruption
            ),
        },
        {
            "Scenario": "-2 Rest Hours",
            "Score": calculate_fatigue_score(
                duty_hours, segments, timezone_changes, max(rest_hours - 2, 0), circadian_disruption
            ),
        },
        {
            "Scenario": "+2 Time Zones",
            "Score": calculate_fatigue_score(
                duty_hours, segments, min(timezone_changes + 2, 6), rest_hours, circadian_disruption
            ),
        },
    ]

    scenario_df = pd.DataFrame(scenario_data)
    st.line_chart(scenario_df.set_index("Scenario"))
    st.dataframe(scenario_df, use_container_width=True)

    st.divider()
    st.subheader("4-Day Fatigue Timeline Predictor")

    timeline_df = build_timeline_data(
        duty_hours, segments, timezone_changes, rest_hours, circadian_disruption
    )

    st.line_chart(timeline_df.set_index("Day")["Fatigue Score"])
    st.dataframe(
        timeline_df[
            ["Day", "Duty Hours", "Segments", "Time Zones", "Rest Hours", "Circadian Disruption", "Fatigue Score", "Risk Level"]
        ],
        use_container_width=True
    )

    highest_day = timeline_df.loc[timeline_df["Fatigue Score"].idxmax()]
    st.warning(
        f"Highest projected fatigue day: {highest_day['Day']} "
        f"with score {highest_day['Fatigue Score']}/100 ({highest_day['Risk Level']})."
    )


st.divider()

# -----------------------------
# CSV Upload Section
# -----------------------------
st.header("Crew Schedule Upload")
st.write(
    "Upload a CSV file to analyze multiple crew members at once. "
    "Required columns must match exactly."
)

template_df = pd.DataFrame(
    {
        "Crew ID": ["Crew 101", "Crew 102", "Crew 103"],
        "Duty Hours": [11, 13, 8],
        "Flight Segments": [3, 5, 2],
        "Time Zone Changes": [1, 2, 0],
        "Rest Hours Before Duty": [9, 6, 11],
        "Circadian Disruption Level": [4, 7, 2],
    }
)

st.download_button(
    label="Download CSV Template",
    data=template_df.to_csv(index=False).encode("utf-8"),
    file_name="aerovigil_template.csv",
    mime="text/csv"
)

uploaded_file = st.file_uploader("Upload Crew Schedule CSV", type=["csv"])

required_columns = [
    "Crew ID",
    "Duty Hours",
    "Flight Segments",
    "Time Zone Changes",
    "Rest Hours Before Duty",
    "Circadian Disruption Level",
]

if uploaded_file is not None:
    crew_df = pd.read_csv(uploaded_file)

    missing_cols = [col for col in required_columns if col not in crew_df.columns]

    if missing_cols:
        st.error(f"Missing required columns: {missing_cols}")
    else:
        analyzed_df = add_risk_fields(crew_df)

        st.subheader("Multi-Crew Fatigue Analysis")
        st.dataframe(analyzed_df, use_container_width=True)

        st.divider()

        # Fleet metrics
        high_count = (analyzed_df["Risk Level"] == "HIGH").sum()
        moderate_count = (analyzed_df["Risk Level"] == "MODERATE").sum()
        low_count = (analyzed_df["Risk Level"] == "LOW").sum()
        avg_score = round(analyzed_df["Fatigue Score"].mean(), 1)

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Average Fatigue Score", avg_score)
        with m2:
            st.metric("High Risk Crew", int(high_count))
        with m3:
            st.metric("Moderate Risk Crew", int(moderate_count))
        with m4:
            st.metric("Low Risk Crew", int(low_count))

        st.divider()

        # Multi-crew comparison
        st.subheader("Multi-Crew Risk Comparison")
        comparison_df = analyzed_df[["Crew ID", "Fatigue Score"]].set_index("Crew ID")
        st.bar_chart(comparison_df)

        st.divider()

        # Heatmap dashboard
        st.subheader("Fatigue Heatmap Dashboard")
        heatmap_df = make_heatmap_dataframe(analyzed_df)
        plot_heatmap(heatmap_df)

        st.divider()

        # Ops Control Command Center
        st.subheader("Ops Control Command Center")
        st.write(
            "This startup-style feature highlights the crews that would need immediate operational review."
        )

        alert_df = analyzed_df.sort_values(by="Fatigue Score", ascending=False).reset_index(drop=True)
        critical_df = alert_df[alert_df["Fatigue Score"] >= 65]

        if not critical_df.empty:
            st.error("Critical fatigue exposure detected in uploaded crew set.")
            st.dataframe(
                critical_df[["Crew ID", "Fatigue Score", "Risk Level", "Recommended Action"]],
                use_container_width=True
            )
        else:
            st.success("No critical crews detected in this upload.")

        top5_df = alert_df.head(5)
        st.subheader("Top 5 Highest-Risk Crew")
        st.dataframe(
            top5_df[["Crew ID", "Fatigue Score", "Risk Level", "Recommended Action"]],
            use_container_width=True
        )

        st.divider()

        # Mitigation simulation
        st.subheader("Mitigation Simulation")
        st.write(
            "This simulation shows what happens if operations add 2 hours of rest, remove 1 segment, "
            "and reduce duty by 1 hour across the uploaded group."
        )

        simulated_df = run_mitigation_simulation(crew_df)

        before_after_df = analyzed_df[["Crew ID", "Fatigue Score"]].rename(
            columns={"Fatigue Score": "Before Score"}
        ).merge(
            simulated_df[["Crew ID", "Fatigue Score"]].rename(columns={"Fatigue Score": "After Score"}),
            on="Crew ID"
        )

        before_after_df["Improvement"] = before_after_df["Before Score"] - before_after_df["After Score"]

        st.dataframe(before_after_df, use_container_width=True)

        chart_df = before_after_df.set_index("Crew ID")[["Before Score", "After Score"]]
        st.line_chart(chart_df)

        st.divider()

        # Downloadable report
        st.subheader("Download Analysis Report")
        st.download_button(
            label="Download Results CSV",
            data=analyzed_df.to_csv(index=False).encode("utf-8"),
            file_name="aerovigil_analysis_report.csv",
            mime="text/csv"
        )
else:
    st.info("Upload a CSV to unlock multi-crew comparison, heatmap dashboard, and Ops Control Command Center.")
