# AeroVigil

**Predictive Fatigue Risk Analytics for Aviation Safety**

AeroVigil is a prototype aviation safety tool designed to estimate **crew fatigue risk** using key operational factors such as duty hours, flight segments, time zone changes, rest periods, and circadian disruption.

This project was built as an early proof-of-concept for a larger vision: helping airlines and aviation safety teams identify fatigue risk **before flights operate**.

---

## 1. Live Demo

👉 **AeroVigil App:**  
https://aerovigil-demo.streamlit.app

---

## 2. Overview

Fatigue remains one of the most critical human factors issues in aviation safety. AeroVigil explores how operational inputs from crew scheduling and duty periods can be converted into a clear **fatigue risk score**.

This prototype allows users to experiment with different operational scenarios and instantly see how fatigue risk changes.

---

## 3. Features

- Calculates a **fatigue risk score** from 0–100
- Uses operational inputs such as:
  - Duty hours
  - Flight segments
  - Time zone changes
  - Rest hours before duty
  - Circadian disruption
- Displays a fatigue **classification level**
  - LOW
  - MODERATE
  - HIGH
- Provides a **mitigation recommendation**
- Includes a **scenario comparison chart**
- Includes a **4-day fatigue trend / timeline predictor**
- Built with an interactive **Streamlit dashboard**

---

## 4. How It Works

The fatigue calculator assigns weighted values to operational risk factors:

- Longer duty periods increase fatigue risk
- More flight segments increase workload
- Crossing time zones increases disruption
- Greater circadian disruption increases fatigue likelihood
- More rest before duty lowers fatigue risk

The total is converted into a capped score from **0 to 100**, making it easier to understand risk severity.

---

## 5. Example Use Cases

AeroVigil can be used as a prototype concept for:

- Comparing duty schedules
- Demonstrating fatigue risk visually
- Exploring human factors research ideas
- Presenting an aviation safety analytics concept
- Building future predictive safety tools for airline operations

---

## 6. Future Development Roadmap

Planned future improvements may include:

- Real airline schedule data integration
- Predictive crew fatigue dashboards
- AI-based fatigue forecasting
- Risk alerts for schedulers and safety departments
- FRMS compliance reporting tools
- Multi-crew schedule analysis
- Exportable fatigue risk reports
- Airline operational scenario modeling

---

## 7. Tech Stack

- **Python**
- **Streamlit**
- **Pandas**
- **Matplotlib**

---

## 8. Project Structure

```bash
AeroVigil/
│
├── app.py
├── fatigue_calculator.py
├── requirements.txt
└── README.md
