import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fatigue_calculator import calculate_fatigue_score

st.set_page_config(page_title="AeroVigil", layout="wide")

# -------------------------------------------------
# Custom UI styling
# -------------------------------------------------
st.markdown(
    """
    <style>
        .main {
            padding-top: 1rem;
        }
        .hero-box {
            background: linear-gradient(135deg, #0f172a, #1e293b);
            padding: 28px;
            border-radius: 18px;
            margin-bottom: 18px;
            color: white;
            border: 1px solid #334155;
        }
        .hero-title {
            font-size: 2.2rem;
            font-weight: 700;
            margin-bottom: 0.3rem;
        }
        .hero-subtitle {
            font-size: 1.05rem;
            color: #cbd5e1;
            margin-bottom: 0.7rem;
        }
        .hero-tag {
            display: inline-block;
            padding: 6px 12px;
            border-radius: 999px;
            background-color: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.15);
            font-size: 0.85rem;
            margin-top: 6px;
        }
        .section-card {
            background: #111827;
            border: 1px solid #1f2937;
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 16px;
        }
        .section-title {
            font-size: 1.15rem;
            font-weight: 700;
            margin-bottom: 0.6rem;
            color: #f9fafb;
        }
        .mini-note {
            font-size: 0.9rem;
            color: #9ca3af;
            margin-bottom: 0.4rem;
        }
        .score-box {
            background: #0b1220;
            border: 1px solid #233044;
            border-radius: 16px;
            padding: 18px;
            text-align: center;
            min-height: 130px;
        }
        .score-label {
            font-size: 0.9rem;
            color: #94a3b8;
            margin-bottom: 8px;
        }
        .score-value {
            font-size: 2rem;
            font-weight: 800;
            color: #f8fafc;
        }
        .score-sub {
            font-size: 0.95rem;
            color: #cbd5e1;
            margin-top: 8px;
        }
        .alert-low {
            background: rgba(34, 197, 94, 0.10);
            border: 1px solid rgba(34, 197, 94, 0.35);
            color: #dcfce7;
            padding: 14px;
            border-radius: 14px;
            margin-top: 8px;
        }
        .alert-moderate {
            background: rgba(245, 158, 11, 0.10);
            border: 1px solid rgba(245, 158, 11, 0.35);
            color: #fef3c7;
            padding: 14px;
            border-radius: 14px;
            margin-top: 8px;
        }
        .alert-high {
            background: rgba(239, 68, 68, 0.10);
            border: 1px solid rgba(239, 68, 68, 0.35);
            color: #fee2e2;
            padding: 14px;
            border-radius: 14px;
            margin-top: 8px;
        }
        .footer-box {
            font-size: 0.85rem;
            color: #9ca3af;
            padding-top: 6px;
            padding-bottom: 20px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

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
        return "Crew appears fit for duty. Continue standard monitoring."
    elif score < 70:
        return "Moderate fatigue risk detected. Consider added rest or schedule adjustment."
    return "High fatigue risk detected. Recommend immediate mitigation and scheduling review."


def get_alert_message(score):
    if score < 35:
        return "Low operational fatigue risk."
    elif score < 70:
        return "Caution: Moderate fatigue risk may affect crew performance."
    return "Warning: High fatigue risk may affect crew safety and operational reliability."


def build_trend_data(base_score):
    periods = ["Day 1", "Day 2", "Day 3", "Day 4"]
    trend_scores = [
        max(0, min(100, base_score - 12)),
        max(0, min(100, base_score - 5)),
        max(0, min(100, base_score + 3)),
        max(0, min(100, base_score)),
    ]
    return pd.DataFrame({"Duty Period": periods, "Fatigue Score": trend_scores})


def build_driver_table(duty_hours, segments, timezone_changes, rest_hours, circadian_disruption):
    return pd.DataFrame(
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
            "Operational Effect": [
                "Longer duty periods increase fatigue exposure.",
                "More segments can raise workload and cognitive load.",
                "Timezone shifts increase circadian disruption.",
                "More rest lowers fatigue risk.",
                "Higher circadian disruption raises fatigue risk.",
            ],
        }
    )


# -------------------------------------------------
# Sidebar
# -------------------------------------------------
st.sidebar.header("Crew Duty Inputs")
st.sidebar.write("Adjust the scheduling variables below to estimate fatigue risk.")

duty_hours = st.sidebar.slider("Duty Hours", 0, 16, 8)
segments = st.sidebar.slider("Flight Segments", 1, 8, 2)
timezone_changes = st.sidebar.slider("Time Zone Changes", 0, 6, 0)
rest_hours = st.sidebar.slider("Rest Hours Before Duty", 0, 16, 10)
circadian_disruption = st.sidebar.slider("Circadian Disruption Level", 0, 10, 3)

# -------------------------------------------------
# Core calculation
# -------------------------------------------------
score = calculate_fatigue_score(
    duty_hours,
    segments,
    timezone_changes,
    rest_hours,
    circadian_disruption,
)

risk_level = classify_risk(score)
recommendation = get_recommendation(score)
alert_message = get_alert_message(score)
trend_df = build_trend_data(score)
driver_df = build_driver_table(
    duty_hours, segments, timezone_changes, rest_hours, circadian_disruption
)

# -------------------------------------------------
# Header / Hero
# -------------------------------------------------
st.markdown(
    f"""
    <div class="hero-box">
        <div class="hero-title">AeroVigil</div>
        <div class="hero-subtitle">
            Predictive Fatigue Risk Analytics for Aviation Safety
        </div>
        <div>
            AeroVigil is a prototype decision-support dashboard designed to help aviation
            leaders evaluate fatigue exposure using duty time, workload, rest opportunity,
            timezone changes, and circadian disruption.
        </div>
        <div class="hero-tag">Live Risk Status: {risk_level}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------
# Top score cards
# -------------------------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        f"""
        <div class="score-box">
            <div class="score-label">Fatigue Risk Score</div>
            <div class="score-value">{score}/100</div>
            <div class="score-sub">Current estimated risk level</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
        <div class="score-box">
            <div class="score-label">Risk Classification</div>
            <div class="score-value">{risk_level}</div>
            <div class="score-sub">Based on current duty inputs</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    short_action = "Continue Monitoring"
    if risk_level == "MODERATE":
        short_action = "Review Schedule"
    elif risk_level == "HIGH":
        short_action = "Mitigate Immediately"

    st.markdown(
        f"""
        <div class="score-box">
            <div class="score-label">Recommended Action</div>
            <div class="score-value" style="font-size:1.4rem;">{short_action}</div>
            <div class="score-sub">Operational decision support</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")

# -------------------------------------------------
# Alert + recommendation section
# -------------------------------------------------
left_alert, right_alert = st.columns([1.3, 1])

with left_alert:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Operational Alert Panel</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="mini-note">Current fatigue status based on the entered duty scenario.</div>',
        unsafe_allow_html=True,
    )

    if risk_level == "LOW":
        st.markdown(
            f'<div class="alert-low"><strong>{risk_level} RISK:</strong> {alert_message}</div>',
            unsafe_allow_html=True,
        )
    elif risk_level == "MODERATE":
        st.markdown(
            f'<div class="alert-moderate"><strong>{risk_level} RISK:</strong> {alert_message}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="alert-high"><strong>{risk_level} RISK:</strong> {alert_message}</div>',
            unsafe_allow_html=True,
        )

    st.write("")
    st.write(f"**Recommendation:** {recommendation}")

    if duty_hours >= 12:
        st.write("- Extended duty time is materially increasing fatigue exposure.")
    if timezone_changes >= 2:
        st.write("- Timezone transitions are contributing to fatigue risk.")
    if rest_hours <= 8:
        st.write("- Reduced rest opportunity is elevating the score.")
    if circadian_disruption >= 6:
        st.write("- Circadian disruption is a major fatigue driver in this scenario.")
    if segments >= 5:
        st.write("- High segment count may increase workload and operational strain.")

    st.markdown("</div>", unsafe_allow_html=True)

with right_alert:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Quick Risk Snapshot</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="mini-note">A simplified executive view for demo purposes.</div>',
        unsafe_allow_html=True,
    )

    st.metric("Duty Hours", duty_hours)
    st.metric("Rest Hours", rest_hours)
    st.metric("Timezone Changes", timezone_changes)
    st.metric("Circadian Disruption", circadian_disruption)
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------
# Trend chart
# -------------------------------------------------
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Fatigue Risk Trend</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="mini-note">Illustrative short-term fatigue trend based on the current score.</div>',
    unsafe_allow_html=True,
)

fig, ax = plt.subplots(figsize=(9, 4.2))
ax.plot(trend_df["Duty Period"], trend_df["Fatigue Score"], marker="o", linewidth=2)
ax.set_xlabel("Duty Period")
ax.set_ylabel("Fatigue Score")
ax.set_title("4-Day Fatigue Risk Trend")
ax.set_ylim(0, 100)
ax.grid(True, alpha=0.25)
st.pyplot(fig)
st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------
# Driver table
# -------------------------------------------------
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Fatigue Driver Summary</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="mini-note">Key fatigue inputs and their operational relevance.</div>',
    unsafe_allow_html=True,
)
st.dataframe(driver_df, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------
# Scenario comparison
# -------------------------------------------------
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Scenario Comparison Tool</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="mini-note">Compare two scheduling scenarios to see which one produces lower fatigue risk.</div>',
    unsafe_allow_html=True,
)

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
    duty_b = st.slider("Duty Hours (B)", 0, 16, 11, key="duty_b")
    segments_b = st.slider("Segments (B)", 1, 8, 4, key="segments_b")
    timezone_b = st.slider("Timezone Changes (B)", 0, 6, 1, key="timezone_b")
    rest_b = st.slider("Rest Hours (B)", 0, 16, 8, key="rest_b")
    circadian_b = st.slider("Circadian Disruption (B)", 0, 10, 5, key="circadian_b")

score_a = calculate_fatigue_score(duty_a, segments_a, timezone_a, rest_a, circadian_a)
score_b = calculate_fatigue_score(duty_b, segments_b, timezone_b, rest_b, circadian_b)

risk_a = classify_risk(score_a)
risk_b = classify_risk(score_b)

comparison_df = pd.DataFrame(
    {
        "Scenario": ["Scenario A", "Scenario B"],
        "Fatigue Score": [score_a, score_b],
        "Risk Level": [risk_a, risk_b],
    }
)

st.dataframe(comparison_df, use_container_width=True)

if score_a < score_b:
    st.info("Scenario A appears safer based on the current fatigue inputs.")
elif score_b < score_a:
    st.info("Scenario B appears safer based on the current fatigue inputs.")
else:
    st.info("Both scenarios currently show the same estimated fatigue risk.")

st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------
# Footer
# -------------------------------------------------
st.markdown(
    """
    <div class="footer-box">
        Disclaimer: AeroVigil is a prototype demonstration tool for fatigue risk awareness and
        decision support. It does not replace approved fatigue risk management systems, regulatory
        requirements, dispatch authority, or formal safety assessments.
    </div>
    """,
    unsafe_allow_html=True,
)
